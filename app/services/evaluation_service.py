from app.evaluators.ragas import RagasEval
from app.schemas.eval_metric import EvalMetric
from app.services.db_service import DatabaseService
from app.config.config import get_settings
from app.services.notifier_service import NotifierService
from app.schemas.evaluation_request import EvaluationRequest
from app.utils.logger import get_logger
from app.evaluators.llm_as_judge import LLMAsJudge


import yaml


settings = get_settings()
class EvaluationService:
    """
    EvaluationService handles RAG (Retrieval-Augmented Generation) evaluation operations.
    This service orchestrates the evaluation pipeline including:
    - LLM and embedding model initialization via factory patterns
    - RAG evaluation execution using the RAGAS framework
    - Persistence of evaluation metrics to a database
    - Alert notification based on evaluation results
    Attributes:
        logger: Logger instance for service operations
        event_id: Unique identifier for the evaluation event
        ragas_eval: RagasEval instance for executing RAG evaluations
        db_service: DatabaseService instance for metrics persistence
        notifier_service: NotifierService instance for alert notifications
    """

    def __init__(self,event_id:str = None,eval_type:str= None):
        """
        Initialize the EvaluationService.
        Args:
            event_id: The unique identifier for the evaluation event.
        Initializes the following components:
            - Logger: Sets up logging for the service.
            - AsyncOpenAI Client: Configures Ollama-based LLM client pointing to local instance.
            - LLM: Creates a language model instance using gemma3:1b model via OpenAI provider.
            - Embedding LLM: Creates an embedding model instance using embeddinggemma:latest.
            - RagasEval: Initializes the evaluation engine with configured LLM and embedding models.
            - DatabaseService: Sets up database connection using settings.database_url.
            - NotifierService: Initializes the notification service for event updates.
        Raises:
            Exception: If connection to Ollama instance fails or if database initialization fails.
        """

        self.logger = get_logger(__name__)
        self.event_id = event_id
        self.eval_type = eval_type

        if self.eval_type == "Ragas":
            self.ragas_eval = RagasEval()
        elif self.eval_type == "LLM-As-Judge":
            self.llm_as_judge = LLMAsJudge()
        
        self.db_service = DatabaseService(db_path=settings.database_url)
        self.notifier_service = NotifierService()
        self.logger.info(f"Initialised EvaluationService with event_id : {event_id}")


    async def run_evaluation(self,event_id:str, eval_request:EvaluationRequest):
        """
        Run evaluation for a given event based on eval_type and save results.
        Args:
            event_id (str): The unique identifier for the evaluation event.
            eval_request (EvaluationRequest): The evaluation request containing parameters and project details.
        Returns:
            None
        Raises:
            None (logs warning if evaluation returns empty results)
        Side Effects:
            - Saves evaluation metrics to database if evaluation is successful
            - Checks and notifies alerts based on evaluation results
            - Updates event status to "COMPLETED" in database
            - Logs evaluation progress and completion status
        """

        self.logger.info(f"running evaluaiton on event_id : {event_id} using eval_type : {eval_request.eval_type}")

        if self.eval_type == "Ragas": 
            eval_result = await self.ragas_eval.eval(eval_request=eval_request)
        elif self.eval_type == "LLM-As-Judge":
            eval_result = await self.llm_as_judge.eval(eval_request=eval_request)

        if eval_result:
            self.db_service.save_metrics(event_id, eval_result,eval_request)

            self.notifier_service.check_alerts(eval_request.project_id, eval_result)

            self.db_service.update_event(event_id, "COMPLETED")

            self.logger.info(f"evaluation completed using {eval_request.eval_type} and saved for event_id : {event_id}")
        else:
            self.logger.warning("eval_result is empty")


    def get_metrics(self, app_name:str):
        """
        Retrieve evaluation metrics for a specified application name from the database.
        Args:
            app_name (str): The name of the application for which to retrieve evaluation metrics.
        Returns:
            List[EvalMetric]: A list of evaluation metrics associated with the specified application name.
        """
        self.logger.info(f"retrieving metrics for app_name : {app_name}")
        metrics_rows = self.db_service.get_metrics(app_name)

        metrics = [
                EvalMetric(
                    project_id=row["project_id"],
                    environment=row["environment"],
                    question=row["question"],
                    answer=row["answer"],
                    metric_name=row["metric_name"],
                    metric_value=row["metric_value"]
                )
                for row in metrics_rows
            ]
        
        with open(file = settings.project_alert_config_path) as f:
            thresholds = yaml.safe_load(f)
        
        self.logger.info(f"threshold for project_id {app_name} = {thresholds}")

        metrics_thresholds = thresholds.get(app_name, {})
        return metrics, metrics_thresholds


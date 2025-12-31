from app.evaluators.ragas_eval import RagasEval
from app.services.db_service import DatabaseService
from app.config.config import get_settings
from app.services.notifier_service import NotifierService
from app.schemas.evaluation_request import EvaluationRequest
from app.utils.logger import get_logger
from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.embeddings.base import embedding_factory


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

    def __init__(self,event_id):
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

        client = AsyncOpenAI(
        api_key="ollama",  # Ollama doesn't require a real key
        base_url="http://localhost:11434/v1"
        )
        llm = llm_factory(model="gemma3:1b",provider="openai",client=client)
        
        embed_llm = embedding_factory(provider="openai", model="embeddinggemma:latest", client=client)

        self.ragas_eval = RagasEval(llm=llm,embed_llm=embed_llm)
        
        self.db_service = DatabaseService(db_path=settings.database_url)
        self.notifier_service = NotifierService()
        self.logger.info(f"Initialised EvaluationService with event_id : {event_id}")



    async def run_evaluation(self,event_id:str, eval_request:EvaluationRequest):
        """
        Run evaluation for a given event and save results.
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

        self.logger.info(f"running evaluaiton on event_id : {event_id}")

        eval_result = await self.ragas_eval.eval(eval_request=eval_request)
        if eval_result:
            self.db_service.save_metrics(event_id, eval_result)

            self.notifier_service.check_alerts(eval_request.project_id, eval_result)

            self.db_service.update_event(event_id, "COMPLETED")
            
            self.logger.info(f"evaluation completed and saved for event_id : {event_id}")
        else:
            self.logger.warning("scores is empty")


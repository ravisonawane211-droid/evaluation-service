from app.evaluators.ragas_eval import RagasEval
from app.services.db_service import DatabaseService
from app.config.config import get_settings
from app.services.notifier_servie import NotifierService
from app.schemas.evaluation_request import EvaluationRequest
from app.utils.logger import get_logger
from langchain_community.llms.ollama import Ollama
from langchain_community.embeddings.ollama import OllamaEmbeddings
from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.embeddings.base import embedding_factory


settings = get_settings()
class EvaluationService:
    def __init__(self,event_id):
        self.logger = get_logger(__name__)
        self.event_id = event_id

        client = AsyncOpenAI(
        api_key="ollama",  # Ollama doesn't require a real key
        base_url="http://localhost:11434/v1"
        )
        #llm=Ollama(model="gemma3:1b", base_url="http://localhost:11434",format="json")

        llm = llm_factory(model="gemma3:1b",provider="openai",client=client)
        

        #embed_llm=OllamaEmbeddings(base_url="http://localhost:11434", model="embeddinggemma:latest")

        embed_llm = embedding_factory(provider="openai", model="embeddinggemma:latest", client=client)

        self.ragas_eval = RagasEval(llm=llm,embed_llm=embed_llm)
        
        self.db_service = DatabaseService(db_path=settings.database_url)
        self.notifier_service = NotifierService()
        self.logger.info(f"Initialised EvaluationService with event_id : {event_id}")



    async def run_evaluation(self,event_id:str, eval_request:EvaluationRequest):
        self.logger.info(f"running evaluaiton on event_id : {event_id}")

        eval_result = await self.ragas_eval.eval(eval_request=eval_request)
        if eval_result:
            self.db_service.save_metrics(event_id, eval_result)

            self.notifier_service.check_alerts(eval_request.project_id, eval_result)

            self.db_service.update_event(event_id, "COMPLETED")
            
            self.logger.info(f"evaluation completed and saved for event_id : {event_id}")
        else:
            self.logger.warning("scores is empty")


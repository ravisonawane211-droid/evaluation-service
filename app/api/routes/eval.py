from fastapi import APIRouter, BackgroundTasks
from app.schemas.evaluation_request import EvaluationRequest
from app.services.evaluation_service import EvaluationService
from app.services.db_service import DatabaseService
from app.config.config import get_settings
from app.utils.logger import get_logger

router = APIRouter(prefix="/evaluate",tags=["eval"])
settings = get_settings()
logger = get_logger(__name__)

@router.post("",
             description="evaluates users query and stores metrics in db")
async def evaluate(eval_request: EvaluationRequest, background_tasks: BackgroundTasks):
    logger.info(f"evaluating eval_request : {eval_request}")
    try:
        database_service = DatabaseService(db_path=settings.database_url)
        event_id = database_service.create_event(eval_request)

        evaluation_service = EvaluationService(event_id)
        background_tasks.add_task(evaluation_service.run_evaluation,event_id,eval_request)
    except Exception as e:
        logger.error("error occurred while evaluate")
        raise e
    
    logger.info("evaluation started in background")
    return {"message":"evaluation request accepted.", "status": "accepted", "event_id": event_id}
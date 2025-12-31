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
    """
    Asynchronously processes an evaluation request and runs the evaluation in the background.
    This function accepts an evaluation request, stores it in the database, and schedules
    the actual evaluation to run as a background task. It returns immediately with an
    event ID that can be used to track the evaluation progress.
    Args:
        eval_request (EvaluationRequest): The evaluation request object containing the
            parameters and configuration for the evaluation to be performed.
        background_tasks (BackgroundTasks): FastAPI's BackgroundTasks object for
            scheduling the evaluation to run asynchronously without blocking the response.
    Returns:
        dict: A response dictionary containing:
            - message (str): A confirmation message indicating the request was accepted.
            - status (str): The status of the request ("accepted").
            - event_id (int): A unique identifier for the evaluation event that can be
                used to retrieve the evaluation results later.
    Raises:
        Exception: Re-raises any exception that occurs during database operations or
            background task scheduling, with error logging.
    Note:
        The actual evaluation is executed asynchronously in the background via
        EvaluationService.run_evaluation(). The client receives an immediate response
        with an event_id to check the status later.
    """

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
import uuid

from fastapi import APIRouter, BackgroundTasks
from app.schemas.evaluation_request import EvaluationRequest
from app.services.evaluation_service import EvaluationService
from app.schemas.eval_metrics_response import EvalMetricsResponse
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
        event_id = str(uuid.uuid4())
        
        evaluation_service = EvaluationService(event_id=event_id, eval_type=eval_request.eval_type)

        background_tasks.add_task(evaluation_service.run_evaluation, eval_request)

    except Exception as e:
        logger.error(f"error occurred while evaluate: {e}")
        raise e
    
    logger.info(f"evaluation started in background for event_id : {event_id}")
    return {"message":"evaluation request accepted.", "status": "accepted", "event_id": event_id}


@router.get("/metrics/{app_name}", 
            response_model=EvalMetricsResponse,
            description="retrieves evaluation metrics for given app_name")
async def get_metrics(app_name: str):
    """
    Retrieve evaluation metrics for a specified application name from the database.
    Args:
        app_name (str): The name of the application for which to retrieve evaluation metrics.
    Returns:
        EvalMetricsResponse: An object containing the evaluation metrics and status.
    """
    logger.info(f"retrieving metrics for app_name : {app_name}")

    try:
        if not app_name:
            logger.error("app_name is required to fetch metrics")
            raise ValueError("app_name is required")
        
        evaluation_service = EvaluationService()
        metrics, metrics_thresholds = evaluation_service.get_metrics(app_name)

        logger.info(f"retrieved {len(metrics)} metrics for app_name : {app_name}")
    except Exception as e:
        logger.error("error occurred while retrieving metrics")
        raise e
    return EvalMetricsResponse(threashold=metrics_thresholds, eval_metrics=metrics, status="success")
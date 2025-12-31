
from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Iterator
import uuid
from app.config.config import get_settings
from app.utils.logger import get_logger
from app.schemas.evaluation_event import EvaluationEvent
from app.schemas.evaluation_request import EvaluationRequest
from app.schemas.evaluation_metric import EvaluationMetric
import pandas as pd
from typing import Any
import json

settings = get_settings()
logger = get_logger(__name__)

def get_sqlite_db(db_path: str, enable_foreign_keys: bool = True) -> sqlite3.Connection:
    
    path = Path(db_path) if db_path else settings.database_url
    conn = sqlite3.connect(str(path), detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    if enable_foreign_keys:
        conn.execute("PRAGMA foreign_keys = ON;")
    logger.info(f"Connected to database at {path}")
    return conn

class DatabaseService:
    """ DatabaseService
    A service class for managing SQLite database operations related to evaluation events and metrics.
    This service handles:
    - Database connection initialization and management
    - Creation of evaluation events with unique IDs
    - Updating evaluation event statuses
    - Persisting evaluation metrics to the database
    Attributes:
        conn (sqlite3.Connection): SQLite database connection instance.
    Methods:
        __init__(db_path: str, enable_foreign_keys: bool = True)
            Initialize the DatabaseService with a database connection.
            Args:
                db_path (str): Path to the SQLite database file.
                enable_foreign_keys (bool): Whether to enable foreign key constraints. Defaults to True.
        get_db() -> Iterator[sqlite3.Connection]
            Context manager that provides a database connection and ensures it is closed after use.
            Yields:
                sqlite3.Connection: Active database connection.
        create_event(eval_request: EvaluationRequest) -> str
            Create a new evaluation event from an evaluation request.
            Args:
                eval_request (EvaluationRequest): The evaluation request containing project, environment, and metadata.
            Returns:
                str: The unique event ID of the created evaluation event.
            Raises:
                Exception: If the event creation fails.
        update_event(event_id: str, status: str) -> None
            Update the status of an existing evaluation event.
            Args:
                event_id (str): The unique identifier of the evaluation event.
                status (str): The new status to set for the event.
            Raises:
                ValueError: If no event with the given event_id is found.
                Exception: If the update operation fails.
        save_metrics(event_id: str, scores: dict[str, Any]) -> None
            Save evaluation metrics for a specific event.
            Args:
                event_id (str): The unique identifier of the evaluation event.
                scores (dict[str, Any]): Dictionary mapping metric names to their values.
            Raises:
                Exception: If saving metrics fails."""
    
    def __init__(self, db_path: str, enable_foreign_keys: bool = True):
        """
        Initialize the database service.
        Args:
            db_path (str): The file path to the SQLite database.
            enable_foreign_keys (bool, optional): Whether to enable foreign key constraints. 
                                                  Defaults to True.
        Raises:
            Logs an info message upon successful connection to the database.
        """

        
        self.conn = get_sqlite_db(db_path, enable_foreign_keys)

        logger.info(f"Connected to database at {db_path}")
    
    @contextmanager
    def get_db(self) -> Iterator[sqlite3.Connection]:
        """Context manager for a database connection that always closes on exit."""
        conn = self.conn 
        try:
            yield conn
        finally:
            conn.close()

    def create_event(self,eval_request:EvaluationRequest):
        def create_event(self, eval_request: EvaluationRequest) -> str:
            """
            Create a new evaluation event in the database.
            This method generates a unique event ID, constructs an EvaluationEvent object
            from the provided evaluation request, and persists it to the database using
            pandas DataFrame and SQL.
            Args:
                eval_request (EvaluationRequest): The evaluation request object containing
                    request_id, project_id, environment, and metadata information.
            Returns:
                str: The unique event ID (UUID) of the created event, or None if creation fails.
            Raises:
                Exception: If an error occurs while writing the event to the database,
                    the exception is logged and re-raised.
            Note:
                - A unique event ID is generated using uuid.uuid4()
                - The event status is initialized as "PENDING"
                - Metadata is serialized to JSON format before database insertion
                - Logs event creation details on success and error details on failure
            """

        logger.info(f"creating event for eval_requst :{eval_request.request_id}")
        event_id = str(uuid.uuid4())

        try:
            event = EvaluationEvent(
                id=event_id,
                request_id=eval_request.request_id,
                project_id=eval_request.project_id,
                environment=eval_request.environment,
                status="PENDING",
                metadata=eval_request.metadata,
            )

            df = pd.DataFrame.from_records([{
                "id": event.id,
                "request_id": event.request_id,
                "project_id": event.project_id,
                "environment": event.environment,
                "status": event.status,
                "metadata": json.dumps(event.metadata)
            }])
            count = df.to_sql(name=event.__tablename__, con=self.conn, if_exists="append", index=False)
            logger.info(f"created event with event info : {event} , {count}")
        except Exception as e:
            event_id = None
            logger.error(f"error while creating event in evaluation_event {e}")
            raise e
        return event_id
    
    def update_event(self, event_id: str, status: str):
        """Update the status of an evaluation event by its ID.
                Args:
                    event_id (str): The unique identifier of the evaluation event to update.
                    status (str): The new status value to set for the evaluation event.
                Raises:
                    ValueError: If no evaluation event with the given event_id exists in the database.
                    Exception: If an error occurs while updating the evaluation_event table.
                Returns:
                    None
                Note:
                    - Logs an info message at the start of the update operation.
                    - Logs an info message upon successful completion.
                    - Logs an error message if the event_id is not found or if an exception occurs.
                    - Commits the transaction to the database upon successful update."""

        logger.info(f"Updating event_id={event_id} to status={status} in evaluation_event")

        try:
            cursor = self.conn.execute(
                """
                UPDATE evaluation_event
                SET status = ?
                WHERE id = ?
                """,
                (status, event_id)
            )

            self.conn.commit()

            if cursor.rowcount == 0:
                logger.error(f"No evaluation_event found with id={event_id}")
                raise ValueError(f"No evaluation_event found with id={event_id}")

            logger.info(f"Updated event_id={event_id} status to {status}")

        except Exception as e:
            logger.error(f"Error while updating evaluation_event table: {e}")
            raise e


    def save_metrics(self,event_id,scores:dict[str, Any]):
        """
            Save evaluation metrics to the database.
            This method takes a dictionary of metric scores and stores them as individual
            EvaluationMetric records in the database, each associated with a specific event.
            Args:
                event_id: The unique identifier of the event for which metrics are being saved.
                scores (dict[str, Any]): A dictionary where keys are metric names and values are metric scores.
            Raises:
                Exception: If an error occurs while saving metrics to the database. The exception is logged
                           and re-raised for handling by the caller.
            Returns:
                None
            Note:
                - Each metric is assigned a unique UUID.
                - Metrics are converted to a pandas DataFrame before being written to SQL.
                - Metric saving and score values are logged for audit purposes.
            """

        logger.info(f"saving metrics for event_id: {event_id}")
        try:
            metrics = []
            for k, v in scores.items():
                metrics.append(EvaluationMetric(
                    id=str(uuid.uuid4()),
                    event_id=event_id,
                    metric_name=k,
                    metric_value=v
                    ))
                logger.info(f"Metric : {k} , Score: {v}")
            
            df = pd.DataFrame([m.model_dump() for m in metrics])
                
            df.to_sql(name=EvaluationMetric.__tablename__, con=self.conn, if_exists="append", index=False)

            logger.info(f"Saved metrics for event_id: {event_id}")
        except Exception as e:
            logger.error(f"error while saving metrics in evaluation_metric {e}")
            raise e

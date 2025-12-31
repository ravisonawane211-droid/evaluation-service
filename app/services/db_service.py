
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
    def __init__(self, db_path: str, enable_foreign_keys: bool = True):
        
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

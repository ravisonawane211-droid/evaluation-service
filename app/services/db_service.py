import json
import time
import uuid
from contextlib import contextmanager
from functools import lru_cache
from typing import Any, Iterator, Optional

import pandas as pd
from sqlalchemy import Connection, create_engine, text

from app.config.config import get_settings
from app.schemas.evaluation_event import EvaluationEvent
from app.schemas.evaluation_metric import EvaluationMetric
from app.schemas.evaluation_request import EvaluationRequest
from app.utils.logger import get_logger

settings = get_settings()


@lru_cache(maxsize=None)
def get_shared_engine(db_config: str):
    """Return a single PostgreSQL engine per database URL."""
    if not db_config.startswith(("postgresql://", "postgres://")):
        raise ValueError("DATABASE_URL must be a PostgreSQL connection URL")
    return create_engine(
        url=db_config,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=0,
        pool_timeout=30,
        pool_recycle=1800,
    )


def initialize_tables(engine) -> None:
    """Create the evaluation tables when using a new PostgreSQL database."""
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS evaluation_event (
                id VARCHAR(255) PRIMARY KEY,
                request_id VARCHAR(255) NOT NULL,
                project_id VARCHAR(255) NOT NULL,
                environment VARCHAR(255) NOT NULL,
                status VARCHAR(50) NOT NULL,
                metadata JSONB,
                created_at TIMESTAMP NOT NULL,
                created_by VARCHAR(255) NOT NULL
            )
        """))
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS evaluation_metric (
                id VARCHAR(255) PRIMARY KEY,
                event_id VARCHAR(255) NOT NULL REFERENCES evaluation_event(id),
                question TEXT,
                answer TEXT,
                metric_name VARCHAR(255) NOT NULL,
                metric_value DOUBLE PRECISION NOT NULL,
                created_at TIMESTAMP NOT NULL,
                created_by VARCHAR(255) NOT NULL
            )
        """))


class DatabaseService:
    def __init__(self, db_path: Optional[str], enable_foreign_keys: bool = True):
        self.logger = get_logger(__name__)
        self.engine = get_shared_engine(db_path or settings.database_url)
        initialize_tables(self.engine)
        self.logger.info("Connected to PostgreSQL database")

    @contextmanager
    def get_db(self) -> Iterator[Connection]:
        conn = self.engine.connect()
        try:
            yield conn
        finally:
            conn.close()

    def create_event(self, eval_request: EvaluationRequest, event_id: str):
        event = EvaluationEvent(
            id=event_id,
            request_id=eval_request.request_id,
            project_id=eval_request.project_id,
            environment=eval_request.environment,
            status="PENDING",
            metadata=eval_request.metadata,
            created_at=time.strftime("%Y-%m-%d %H:%M:%S"),
            created_by=eval_request.user_id,
        )
        df = pd.DataFrame([event.model_dump()])
        df["metadata"] = df["metadata"].map(json.dumps)
        df.to_sql(event.__tablename__, self.engine, if_exists="append", index=False)
        return event_id

    def update_event(self, event_id: str, status: str):
        with self.engine.begin() as connection:
            result = connection.execute(
                text("""
                    UPDATE evaluation_event
                    SET status = :status
                    WHERE id = :event_id
                """),
                {"status": status, "event_id": event_id},
            )
        if result.rowcount == 0:
            raise ValueError(f"No evaluation_event found with id={event_id}")

    def save_metrics(self, event_id: str, scores: dict[str, Any], eval_request: EvaluationRequest):
        metrics = [EvaluationMetric(
            id=str(uuid.uuid4()),
            event_id=event_id,
            question=eval_request.question,
            answer=eval_request.answer,
            metric_name=name,
            metric_value=round(float(value), 2),
            created_at=time.strftime("%Y-%m-%d %H:%M:%S"),
            created_by=eval_request.user_id,
        ) for name, value in scores.items()]
        df = pd.DataFrame([metric.model_dump() for metric in metrics])
        df.to_sql(EvaluationMetric.__tablename__, self.engine, if_exists="append", index=False)

    def get_metrics(self, app_name: str):
        query = text("""
            SELECT DISTINCT ee.project_id, ee.environment, em.question, em.answer,
                em.metric_name, em.metric_value, em.created_at, em.created_by
            FROM evaluation_metric em
            JOIN evaluation_event ee ON em.event_id = ee.id
            WHERE ee.id = (
                SELECT id FROM evaluation_event
                WHERE project_id = :app_name AND status = 'COMPLETED'
                ORDER BY created_at DESC, id DESC LIMIT 1
            )
            ORDER BY em.created_at DESC, em.metric_name
        """)
        with self.engine.connect() as connection:
            return connection.execute(query, {"app_name": app_name}).mappings().all()

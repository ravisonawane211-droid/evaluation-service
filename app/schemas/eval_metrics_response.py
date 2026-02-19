from pydantic import BaseModel
from typing import List
from app.schemas.eval_metric import EvalMetric


class EvalMetricsResponse(BaseModel):
    threashold: dict = {}
    eval_metrics: List[EvalMetric]
    status: str



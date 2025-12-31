from pydantic import BaseModel

class EvaluationMetric(BaseModel):
    __tablename__ = "evaluation_metric"
    id:str
    event_id:str
    metric_name:str
    metric_value:float
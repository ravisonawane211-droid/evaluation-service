from pydantic import BaseModel

class EvaluationMetric(BaseModel):
    __tablename__ = "evaluation_metric"
    id:str
    event_id:str
    question:str 
    answer:str
    metric_name:str
    metric_value:float
    created_at:str
    created_by:str
from pydantic import BaseModel

class EvalMetric(BaseModel):
    project_id:str
    environment : str
    question:str | None
    answer:str | None
    metric_name:str
    metric_value:float
    created_at:str
    created_by:str

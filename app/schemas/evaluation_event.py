from pydantic import BaseModel

class EvaluationEvent(BaseModel):
    __tablename__ = "evaluation_event"
    id:str
    request_id:str
    project_id:str
    environment : str
    status :str
    metadata:dict
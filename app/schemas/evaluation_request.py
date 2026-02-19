from pydantic import BaseModel,Field
from typing import List, Dict, Optional,Literal

class EvaluationRequest(BaseModel):
    project_id: str = Field(description="Project Id for evluation")
    environment: str = Field(description="Enviornment name")
    request_id: str = Field(description="Interaction id or uuid")
    question: str = Field(description="User query")
    answer: str = Field(description="LLM generated answer")
    contexts: List[str] = Field(description="Retrieved contexts")
    metadata: Optional[Dict] = Field(default={},description="Metadata information")
    eval_type: Literal["Ragas","LLM-As-Judge"] = Field(description="Type of evaluation to be performed")

from pydantic import BaseModel,Field
from typing import Literal

class AppConfig(BaseModel):
    """
    AppConfig for application configuration
    """
    enable_eval:Literal["Yes","No"] = Field(description="enable or not evaluation for application")
    
    eval_type:Literal["ragas","llm-as-judge"] = Field(description="evaluation type for evaluating user query")
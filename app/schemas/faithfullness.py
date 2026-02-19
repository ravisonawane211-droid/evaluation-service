from pydantic import BaseModel, Field
from app.schemas.score import Score, SCORE_DESCRIPTION

class Faithfulness(BaseModel):
    """Evaluates if the answer is faithful to retrieved context (no hallucinations)"""
    reasoning: str = Field(
        ...,
        description=(
            """Provide step-by-step reasoning explaining how faithful the generated answer 
            is to the retrieved context. Check each claim in the answer against the context. 
            Identify any statements not supported by the context (hallucinations). 
            Consider factual accuracy and whether the answer introduces information 
            not present in the retrieved documents."""
        )
    )
    score: Score = Field(..., description=SCORE_DESCRIPTION)
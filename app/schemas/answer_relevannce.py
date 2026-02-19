
from pydantic import BaseModel, Field
from app.schemas.score import Score, SCORE_DESCRIPTION

class AnswerRelevance(BaseModel):
    """Evaluates if the answer directly addresses the user's question"""
    reasoning: str = Field(
        ...,
        description=(
            """Provide step-by-step reasoning explaining how well the generated answer 
            addresses the user's original question. Consider whether the answer is 
            on-topic, directly responds to what was asked, and provides useful information. 
            Identify any irrelevant tangents or missing aspects of the question."""
        )
    )
    score: Score = Field(..., description=SCORE_DESCRIPTION)
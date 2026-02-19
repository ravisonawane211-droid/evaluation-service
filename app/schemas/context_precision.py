from pydantic import BaseModel, Field
from app.schemas.score import Score, SCORE_DESCRIPTION

class ContextPrecision(BaseModel):
    """It is Retrieval Quality metric. Evaluates if the retrieved contexts are relevant and useful for answering the question"""
    reasoning: str = Field(
        ...,
        description=(
            "Provide step-by-step reasoning explaining how relevant the retrieved contexts "
            "are to the user's question. Consider whether the contexts contain information "
            "needed to answer the question, and whether irrelevant contexts were retrieved. "
            "Evaluate the ranking quality (most relevant contexts ranked highest)."
        )
    )
    score: Score = Field(..., description=SCORE_DESCRIPTION)
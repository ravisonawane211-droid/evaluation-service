from pydantic import BaseModel, Field
from app.schemas.answer_relevannce import AnswerRelevance
from app.schemas.context_precision import ContextPrecision
from app.schemas.faithfullness import Faithfulness

class RAGEvaluation(BaseModel):
    """Complete RAG evaluation with all three metrics"""
    faithfulness: Faithfulness = Field(
        ...,
        description="Evaluation of answer faithfulness to retrieved context"
    )
    answer_relevance: AnswerRelevance = Field(
        ...,
        description="Evaluation of answer relevance to the question"
    )
    context_precision: ContextPrecision = Field(
        ...,
        description="Evaluation of retrieved context relevance to the question"
    )
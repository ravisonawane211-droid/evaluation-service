from app.utils.logger import get_logger
from app.schemas.evaluation_request import EvaluationRequest
from typing import List
from app.schemas.rag_evaluation_model import RAGEvaluation
from app.prompts.prompt import JUDGE_SYSTEM_PROMPT
from app.services.llm_service import LLMService
from app.config.config import get_settings

settings = get_settings()

class LLMAsJudge:
    """
     LLMAasJudge evaluator class to evaluate LLM responses using another LLM as judge methodology.
     
     Methods:
         __init__(llm): Initializes the evaluator with the provided language model.
         eval(eval_request): Evaluates the LLM response based on the evaluation request.
     
     Args:
         llm: Language model instance used as judge for evaluation.
     
     Raises:
         Exception: If evaluation fails during execution.
     """

    def __init__(self):
        """
        Initialize the LLMAasJudge evaluator with the provided language model.
        
        Args:
            llm: Language model instance used as judge for evaluation.
        
        Returns:
            None
        """
        self.logger = get_logger(__name__)
        llm_service = LLMService()
        self.judge_llm = llm_service.get_chat_model(provider=settings.provider)

        self.logger.info(f"LLMAsJudge initialized with LLM provider: {settings.provider}")
        

    async def eval(self, eval_request: EvaluationRequest) -> dict[str, float]:
        """
        Evaluate a single RAG interaction using LLM-as-Judge.
        
        Args:
            question: User's question
            retrieved_contexts: List of retrieved document chunks
            generated_answer: RAG system's answer
            
        Returns:
            RAGEvaluation object with scores and reasoning for all metrics
        """
        try:
            self.logger.info(f"Starting evaluation using LLM-as-Judge with provider: {settings.provider} and Judge as Model: {self.judge_llm}")

            # Create messages for the judge
            messages = [
                    {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                    {"role": "user", "content": self._create_judge_prompt(eval_request.question, eval_request.contexts,
                                                                        eval_request.answer)}
                ]
                
            # Use structured output parsing with Pydantic
            response: RAGEvaluation = self.judge_llm.with_structured_output(RAGEvaluation).invoke(messages)

            self.logger.info(f"Completed evaluation using LLM-as-Judge response : {response}")
            return {
                metric_name: float(metric.score.value)
                for metric_name, metric in response
            }
        except Exception as e:
            self.logger.error(f"Error during LLM-as-Judge evaluation: {e}", exc_info=True)
            raise e
            
    def _create_judge_prompt(self, question: str, retrieved_contexts: List[str], generated_answer: str) -> str:
        """
        Create the user prompt for the judge LLM.
        
        Args:
            question: User's question
            retrieved_contexts: List of retrieved document chunks
            generated_answer: RAG system's answer
            
        Returns:
            Formatted prompt string
        """
        # Format contexts with clear separators
        contexts_formatted = "\n\n---\n\n".join(
            f"Context {i+1}:\n{ctx}" for i, ctx in enumerate(retrieved_contexts)
        )
        
        return f"""Evaluate the following RAG system interaction:

            **User Question:**
            {question}

            **Retrieved Contexts:**
            {contexts_formatted}

            **Generated Answer:**
            {generated_answer}

            Please evaluate this RAG interaction across all three dimensions: Faithfulness, Answer Relevance, and Context Precision."""
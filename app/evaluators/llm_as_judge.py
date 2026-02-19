from app.utils.logger import get_logger
from app.schemas.evaluation_request import EvaluationRequest
from typing import List
from app.schemas.rag_evaluation_model import RAGEvaluation
from app.prompts.prompt import JUDGE_SYSTEM_PROMPT
from langchain_ollama import ChatOllama

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
        self.judge_llm = ChatOllama(model="gemma3:1b",temperature=0)
        self.logger.info("Initialized LLMAsJudge evaluator")
        

    async def eval(self, eval_request: EvaluationRequest) -> RAGEvaluation:
        """
        Evaluate a single RAG interaction using LLM-as-Judge.
        
        Args:
            question: User's question
            retrieved_contexts: List of retrieved document chunks
            generated_answer: RAG system's answer
            
        Returns:
            RAGEvaluation object with scores and reasoning for all metrics
        """
        self.logger.info("Starting evaluation using LLM-as-Judge")

        # Create messages for the judge
        messages = [
                {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                {"role": "user", "content": self.create_judge_prompt(eval_request.question, eval_request.contexts,
                                                                     eval_request.answer)}
            ]
            
        # Use structured output parsing with Pydantic
        response:RAGEvaluation = self.judge_llm.with_structured_output(RAGEvaluation).invoke(messages)

        self.logger.info(f"Completed evaluation using LLM-as-Judge response : {response}")
            
        return response.model_dump()


    def create_judge_prompt(self, question: str, retrieved_contexts: List[str], generated_answer: str) -> str:
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
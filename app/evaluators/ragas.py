from app.utils.logger import get_logger
from app.schemas.evaluation_request import EvaluationRequest
from ragas.metrics.collections import Faithfulness,AnswerRelevancy,ContextPrecisionWithoutReference,ContextUtilization
from ragas import SingleTurnSample,experiment
from typing import Dict
import asyncio
import time
from ragas.llms import llm_factory
from ragas.embeddings.base import embedding_factory
from openai import AsyncOpenAI

logger = get_logger(__name__)

class RagasEval:
    """
    RagasEval: A class for performing RAGAS (Retrieval-Augmented Generation Assessment) evaluations.
    This class provides functionality to evaluate the quality of LLM responses using multiple
    metrics including faithfulness, answer relevancy, and context precision.
    Attributes:
        ragas_llm: The language model instance used for RAGAS evaluation metrics.
        ragas_embeddings: The embedding model instance used for answer relevancy evaluation.
    Methods:
        __init__(llm, embed_llm): Initialize RagasEval with language and embedding models.
        eval(eval_request: EvaluationRequest): 
            Async method to perform RAGAS evaluation on a given evaluation request.
            Args:
                eval_request (EvaluationRequest): Contains question, answer, and contexts for evaluation.
            Returns:
                dict: Dictionary containing faithfulness, answer_relevancy, and context_precision scores.
        run_evaluation(row, ragas_llm, ragas_embeddings):
            Internal async method that executes all evaluation metrics concurrently.
            Args:
                row (SingleTurnSample): Sample containing user_input, response, and retrieved_contexts.
                ragas_llm: Language model for metric computation.
                ragas_embeddings: Embedding model for metric computation.
            Returns:
                dict: Dictionary with faithfulness, answer_relevancy, and context_precision metric values.
            Raises:
                Exception: If any metric evaluation fails during execution.
    """
    
    def __init__(self):
            """
            Initialize the RagasEval evaluator with language model and embedding model.
            Args:
                llm: Language model instance to be used for RAGAS evaluation.
                embed_llm: Embedding model instance to be used for generating embeddings.
            Returns:
                None
            """
            client = AsyncOpenAI(
            api_key="ollama",  # Ollama doesn't require a real key
            base_url="http://localhost:11434/v1"
            )
            self.ragas_llm = llm_factory(model="gemma3:1b",provider="openai",client=client)
        
            self.ragas_embeddings = embedding_factory(provider="openai", model="embeddinggemma:latest", client=client)

            logger.info("Initialized RagasEval")

    
    async def eval(self, eval_request:EvaluationRequest):
        """
        Evaluate a single evaluation request using RAGAS metrics.
        This method performs asynchronous evaluation of a question-answer pair with retrieved contexts
        using the RAGAS (Retrieval-Augmented Generation Assessment) framework.
        Args:
            eval_request (EvaluationRequest): An evaluation request object containing:
                - request_id (str): Unique identifier for the evaluation request
                - question (str): The user input/question to evaluate
                - answer (str): The generated response to evaluate
                - contexts (List[str]): Retrieved context documents used in generation
        Returns:
            dict: Evaluation results containing RAGAS metrics scores for the given sample
        Raises:
            Exception: Propagates exceptions from the underlying run_evaluation method
        Example:
            >>> request = EvaluationRequest(
            ...     request_id="req_123",
            ...     question="What is AI?",
            ...     answer="AI is artificial intelligence...",
            ...     contexts=["AI definition from source..."]
            ... )
            >>> result = await evaluator.eval(request)
            >>> print(result)  # RAGAS evaluation scores
        """


        logger.info(f"Ragas evaluation started for request_id : {eval_request.request_id}")

        data = SingleTurnSample(
        user_input= eval_request.question,
        response= eval_request.answer,
        retrieved_contexts= eval_request.contexts
        )

        result = await self.run_evaluation(row=data,ragas_llm=self.ragas_llm,ragas_embeddings=self.ragas_embeddings)

        logger.info(f"Ragas evaluation completed for request_id : {eval_request.request_id}")
        
        logger.info(f"evaluation results: {result}")
        
        return result
    
    @experiment(Dict)
    async def run_evaluation(row,ragas_llm,ragas_embeddings):
        """
        Asynchronously evaluate a given row using RAGAS evaluation metrics.
        This function runs three evaluation metrics in parallel: Faithfulness, Answer Relevancy,
        and Context Precision. Each metric assesses different aspects of the response quality.
        Args:
            row: An object containing the following attributes:
                - user_input (str): The original user query or input.
                - response (str): The generated response to be evaluated.
                - retrieved_contexts (list): List of context documents retrieved for the query.
            ragas_llm: The language model instance used for RAGAS evaluations.
            ragas_embeddings: The embeddings model instance used for RAGAS evaluations.
        Returns:
            dict: A dictionary containing evaluation scores:
                - "faithfulness" (float): Faithfulness score indicating how faithful the response is to the retrieved contexts.
                - "answer_relevancy" (float): Answer relevancy score indicating how relevant the response is to the user input.
                - "context_precision" (float): Context precision score indicating the precision of the retrieved contexts.
        Raises:
            Exception: Re-raises any exception that occurs during the evaluation process.
            The error is logged before being raised.
        Notes:
            - The three evaluation tasks are executed concurrently using asyncio.gather() for performance optimization.
            - Execution time is measured and logged in milliseconds.
            - All errors are logged with ERROR level severity before re-raising.
        """

        faithfulness = Faithfulness(llm=ragas_llm)
        answer_relevancy = AnswerRelevancy(llm=ragas_llm,embeddings=ragas_embeddings)
        context_precision = ContextPrecisionWithoutReference(llm=ragas_llm)
        start_time = time.time()
        
        try:

            faith_task = faithfulness.ascore(
                user_input=row.user_input,
                response=row.response,
                retrieved_contexts=row.retrieved_contexts
            )

            relevancy_task = answer_relevancy.ascore(
                user_input=row.user_input,
                response=row.response
            )

            context_precision_task = context_precision.ascore(
                user_input=row.user_input,
                response=row.response,
                retrieved_contexts=row.retrieved_contexts
            )

            faith_result, relevancy_result, context_precision_result = await asyncio.gather(
                    faith_task,
                    relevancy_task,
                    context_precision_task
                    )
            
            processing_time = (time.time() - start_time) * 1000

            logger.info(f"Ragas evaluation completed in  {processing_time:.2f}ms for metrics : faithfulness,answer_relevancy,context_precision")
           
        except Exception as e:
            logger.error("error while evaluation")
            raise e
        return {
            "faithfulness": faith_result.value,
            "answer_relevancy":relevancy_result.value,
            "context_precision": context_precision_result.value
        }

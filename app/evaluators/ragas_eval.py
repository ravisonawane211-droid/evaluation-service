from app.utils.logger import get_logger
from app.schemas.evaluation_request import EvaluationRequest
from ragas.metrics.collections import Faithfulness,AnswerRelevancy,ContextPrecisionWithoutReference,ContextUtilization
from ragas import SingleTurnSample,EvaluationDataset,experiment
from typing import Dict
import asyncio
import time

logger = get_logger(__name__)

class RagasEval:
    def __init__(self,llm,embed_llm):
        self.ragas_llm = llm
        self.ragas_embeddings = embed_llm
        logger.info("Initialized RagasEval")

    
    async def eval(self, eval_request:EvaluationRequest):

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

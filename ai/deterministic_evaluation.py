# deterministic_evaluation.py
import os
import json
from mistralai import Mistral
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())
API_KEY = os.getenv("MISTRAL_API_KEY")

class DeterministicEvaluator:
    """
    Evaluates the faithfulness, relevance, and sentiment of a generated response 
    using an LLM (Mistral).
    """
    def __init__(self):
        if not API_KEY:
            raise ValueError("MISTRAL_API_KEY not found in .env file")
        self.client = Mistral(api_key=API_KEY)
        self.model = "mistral-small-latest"

    def evaluate(self, query: str, context: str, response: str, retrieval_score: float = 1.0, threshold: float = 0.6) -> dict:
        """
        Evaluates the response using LLM-as-a-judge.
        Checks for:
        1. Faithfulness (Response vs Context)
        2. Relevance (Context vs Query)
        3. Sentiment (Negative/Frustrated)
        4. Refusal Detection
        """
        if not context or len(context.strip()) < 20:
            return {
                "confidence_score": 0.0,
                "passed": False,
                "threshold": threshold,
                "is_refusal": True,
                "sentiment": "neutral",
                "reason": "No significant context found"
            }

        system_prompt = """You are an expert evaluator for a RAG system.
Your task is to evaluate the quality of an AI response based on the provided context and user query.

Evaluate the following criteria:
1. Faithfulness: Is the response supported by the context? (Score 0.0 to 1.0)
2. Relevance: Does the context contain the information needed to answer the query? (Score 0.0 to 1.0)
3. Sentiment: Detect the user's emotion in the query. Is it 'negative' (frustrated, angry), 'neutral', or 'positive'?
4. Refusal: Did the AI response state that it couldn't find the information? (True/False)

Respond ONLY in JSON format:
{
    "faithfulness_score": 0.85,
    "relevance_score": 0.9,
    "sentiment": "neutral",
    "is_refusal": false,
    "reason": "Brief explanation of the scores"
}"""

        user_content = f"""
User Query: {query}
Context: {context}
AI Response: {response}
"""

        try:
            llm_response = self.client.chat.complete(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(llm_response.choices[0].message.content)
            
            # Calculate final confidence score
            # Weighted average: 30% retrieval, 35% relevance, 35% faithfulness
            f_score = result.get("faithfulness_score", 0.0)
            r_score = result.get("relevance_score", 0.0)
            
            if result.get("is_refusal", False):
                confidence_score = 0.1
            else:
                confidence_score = (retrieval_score * 0.3) + (r_score * 0.35) + (f_score * 0.35)

            result.update({
                "confidence_score": round(confidence_score, 4),
                "retrieval_score": round(retrieval_score, 4),
                "passed": confidence_score >= threshold,
                "threshold": threshold
            })
            
            return result

        except Exception as e:
            print(f"⚠️ Error during LLM evaluation: {e}")
            return {
                "confidence_score": 0.0,
                "passed": False,
                "threshold": threshold,
                "is_refusal": False,
                "sentiment": "neutral",
                "reason": f"Evaluation failed: {str(e)}"
            }

if __name__ == "__main__":
    # Quick test
    evaluator = DeterministicEvaluator()
    ctx = "The company offers a 30-day refund policy on all electronics."
    qry = "Can I get a refund for my laptop?"
    ans = "You can get a refund within 30 days for your laptop."
    
    result = evaluator.evaluate(qry, ctx, ans)
    print(f"Test Result: {json.dumps(result, indent=2)}")

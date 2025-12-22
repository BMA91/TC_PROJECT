# deterministic_evaluation.py
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

class DeterministicEvaluator:
    """
    Evaluates the faithfulness of a generated response against the provided context
    using a standard NLI model (DeBERTa-v3).
    """
    def __init__(self, model_name="cross-encoder/nli-deberta-v3-base"):
        print(f"Loading evaluation model: {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()

    def evaluate(self, query: str, context: str, response: str, retrieval_score: float = 1.0) -> dict:
        """
        Evaluates if the information found is actually true/useful for the query.
        Combines:
        1. Retrieval Score (Similarity between Query and Context)
        2. NLI Score (Entailment between Context and Response)
        3. Refusal Detection
        """
        # 0. Check if context is empty or very short
        if not context or len(context.strip()) < 20:
            return {
                "confidence_score": 0.0,
                "passed": False,
                "threshold": 0.6,
                "is_refusal": True,
                "reason": "No significant context found"
            }

        # 1. Check for refusal phrases (Aggressive detection)
        refusal_keywords = [
            "ne contiennent pas", "pas d'informations", "pas d'information",
            "je ne sais pas", "information is missing", "not mentioned",
            "aucune information", "malheureusement", "don't have information",
            "do not contain", "no information", "not found",
            "not provide", "unable to find", "cannot find", "not available",
            "n'est pas mentionné", "ne précise pas", "ne mentionnent pas",
            "ne mentionne pas", "pas explicitement"
        ]
        
        response_lower = response.lower()
        is_refusal = any(kw in response_lower for kw in refusal_keywords)

        # 2. NLI Evaluation (Faithfulness)
        inputs = self.tokenizer(context, response, return_tensors="pt", truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            faithfulness_score = probs[0][2].item()

        # 3. Relevance Evaluation (Query vs Context)
        # We use the same NLI model to see if the Context entails the Query's need
        relevance_inputs = self.tokenizer(context, query, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            relevance_outputs = self.model(**relevance_inputs)
            relevance_probs = torch.softmax(relevance_outputs.logits, dim=-1)
            # Entailment (2) or Neutral (1) are okay, Contradiction (0) is bad
            relevance_score = (relevance_probs[0][2].item() + relevance_probs[0][1].item() * 0.5)

        # 4. Final Confidence Calculation
        # We combine retrieval similarity, relevance, and faithfulness
        # If it's a refusal, we crash the score.
        if is_refusal:
            confidence_score = 0.1
        else:
            # Weighted average: 30% retrieval, 40% relevance, 30% faithfulness
            confidence_score = (retrieval_score * 0.3) + (relevance_score * 0.4) + (faithfulness_score * 0.3)

        # Threshold for passing
        threshold = 0.6
        passed = confidence_score >= threshold

        return {
            "confidence_score": round(confidence_score, 4),
            "faithfulness_score": round(faithfulness_score, 4),
            "relevance_score": round(relevance_score, 4),
            "retrieval_score": round(retrieval_score, 4),
            "passed": passed,
            "threshold": threshold,
            "is_refusal": is_refusal,
            "reason": "Information is relevant and faithful" if passed else "Information is likely irrelevant or missing"
        }

if __name__ == "__main__":
    # Quick test
    evaluator = DeterministicEvaluator()
    ctx = "The company offers a 30-day refund policy on all electronics."
    ans = "You can get a refund within 30 days for your laptop."
    
    result = evaluator.evaluate(ctx, ans)
    print(f"Test Result: {result}")

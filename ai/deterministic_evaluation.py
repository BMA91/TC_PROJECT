# deterministic-evaluation.py
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

class DeterministicEvaluator:
    """
    Evaluates the faithfulness of a generated response against the provided context
    using a Hugging Face model (Vectara HHEM).
    """
    def __init__(self, model_name="vectara/hallucination_evaluation_model"):
        print(f"Loading evaluation model: {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name, trust_remote_code=True)
        self.model.eval()

    def evaluate(self, context: str, response: str) -> dict:
        """
        Returns a confidence score and a boolean indicating if it passes a threshold.
        """
        # The model expects context and response as a pair
        inputs = self.tokenizer(context, response, return_tensors="pt", truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            # HHEM outputs logits for [hallucination, faithful]
            probs = torch.softmax(outputs.logits, dim=-1)
            confidence_score = probs[0][1].item()  # Probability of being faithful

        # Threshold for passing (can be adjusted)
        threshold = 0.6
        passed = confidence_score >= threshold

        return {
            "confidence_score": round(confidence_score, 4),
            "passed": passed,
            "threshold": threshold,
            "reason": "Faithful to context" if passed else "Potential hallucination detected"
        }

if __name__ == "__main__":
    # Quick test
    evaluator = DeterministicEvaluator()
    ctx = "The company offers a 30-day refund policy on all electronics."
    ans = "You can get a refund within 30 days for your laptop."
    
    result = evaluator.evaluate(ctx, ans)
    print(f"Test Result: {result}")

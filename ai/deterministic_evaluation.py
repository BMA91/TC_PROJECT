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

    def evaluate(self, context: str, response: str) -> dict:
        """
        Returns a confidence score based on the 'entailment' probability.
        """
        # DeBERTa NLI classes: 0: contradiction, 1: neutral, 2: entailment
        inputs = self.tokenizer(context, response, return_tensors="pt", truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            # We take the 'entailment' score (index 2) as our confidence
            confidence_score = probs[0][2].item()

        # Threshold for passing
        threshold = 0.6
        passed = confidence_score >= threshold

        return {
            "confidence_score": round(confidence_score, 4),
            "passed": passed,
            "threshold": threshold,
            "reason": "Faithful to context" if passed else "Potential hallucination or contradiction detected"
        }

if __name__ == "__main__":
    # Quick test
    evaluator = DeterministicEvaluator()
    ctx = "The company offers a 30-day refund policy on all electronics."
    ans = "You can get a refund within 30 days for your laptop."
    
    result = evaluator.evaluate(ctx, ans)
    print(f"Test Result: {result}")

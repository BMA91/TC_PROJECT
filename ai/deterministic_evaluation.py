import os
import json
import re
from dotenv import load_dotenv, find_dotenv
from mistralai import Mistral

# Load environment variables
load_dotenv(find_dotenv())
API_KEY = os.getenv("MISTRAL_API_KEY")


class DeterministicEvaluator:
    """
    Evaluator & Decider for support RAG systems:
    - Computes confidence_score
    - Detects exceptions (negative emotions, sensitive data, non-standard)
    - Escalates if needed
    """

    # Patterns for sensitive data
    SENSITIVE_PATTERNS = [
        r"\b\d{13,19}\b",  # credit card numbers
        r"\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b",  # emails
        r"\+?\d[\d\s\-]{7,15}\b"  # phone numbers
    ]

    def __init__(self, confidence_threshold: float = 0.6):
        if not API_KEY:
            raise ValueError("MISTRAL_API_KEY not found in .env file")

        self.client = Mistral(api_key=API_KEY)
        self.model = "mistral-small-latest"
        self.threshold = confidence_threshold

    def _detect_sensitive_data(self, text: str) -> bool:
        return any(re.search(p, text) for p in self.SENSITIVE_PATTERNS)

    def evaluate(self, query: str, context: str, response: str, retrieval_score: float = 0.5) -> dict:
        """
        Returns minimal evaluation object with confidence and escalation context.
        """

        # Auto escalate if context too weak
        if not context or len(context.strip()) < 20:
            return self._escalation_payload(
                confidence=0.0,
                negative_emotion=False,
                sensitive_data=False,
                non_standard=True,
                reason="No reliable context",
                query=query,
                response=response
            )

        system_prompt = """
You are an expert evaluator for a support RAG system.

Your task:
1. Assign a GLOBAL CONFIDENCE SCORE (0.0 to 1.0) for the AI response based on the context.
2. Detect:
   - Negative emotions (anger, frustration)
   - Sensitive data (cards, emails, phones)
   - Non-standard or ambiguous requests
3. Escalate if:
   - Confidence < 0.6
   - Sensitive data detected

Respond ONLY in valid JSON:
{
  "confidence": 0.0-1.0,
  "negative_emotion": true/false,
  "sensitive_data": true/false,
  "non_standard": true/false,
  "reason": "short explanation"
}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"""
USER QUERY:
{query}

CONTEXT:
{context}

AI RESPONSE:
{response}
"""
            }
        ]

        try:
            completion = self.client.chat.complete(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"}
            )

            raw = completion.choices[0].message.content
            result = json.loads(raw)

            # Confidence + soft retrieval bonus
            confidence = round((0.8 * float(result.get("confidence", 0.0)) + 0.2 * retrieval_score), 2)

            # Detect sensitive data
            sensitive_data_detected = self._detect_sensitive_data(response) or result.get("sensitive_data", False)

            # Decide escalation
            escalate = confidence < self.threshold or sensitive_data_detected

            if escalate:
                return self._escalation_payload(
                    confidence=confidence,
                    negative_emotion=result.get("negative_emotion", False),
                    sensitive_data=sensitive_data_detected,
                    non_standard=result.get("non_standard", False),
                    reason=result.get("reason", ""),
                    query=query,
                    response=response
                )

            return {
                "confidence_score": confidence,
                "escalate": False,
                "negative_emotion": result.get("negative_emotion", False),
                "sensitive_data": sensitive_data_detected,
                "non_standard": result.get("non_standard", False),
                "reason": result.get("reason", "")
            }

        except Exception as e:
            return self._escalation_payload(
                confidence=0.0,
                negative_emotion=False,
                sensitive_data=False,
                non_standard=True,
                reason=f"Evaluation failure: {str(e)}",
                query=query,
                response=response
            )

    def _escalation_payload(
        self,
        confidence: float,
        negative_emotion: bool,
        sensitive_data: bool,
        non_standard: bool,
        reason: str,
        query: str,
        response: str
    ) -> dict:
        """
        Structured escalation payload for human agent.
        """
        return {
            "confidence_score": confidence,
            "escalate": True,
            "negative_emotion": negative_emotion,
            "sensitive_data": sensitive_data,
            "non_standard": non_standard,
            "reason": reason,
            "escalation_context": {
                "user_query": query,
                "ai_response": response
            }
        }


# -----------------------
# Quick usage test
# -----------------------
if __name__ == "__main__":
    evaluator = DeterministicEvaluator()

    ctx = "The company offers a 30-day refund policy on all electronics."
    qry = "I'm very angry, can I get my money back?"
    ans = "Yes, you can request a refund within 30 days of purchase. My email is test@example.com."

    result = evaluator.evaluate(
        query=qry,
        context=ctx,
        response=ans,
        retrieval_score=0.9
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))

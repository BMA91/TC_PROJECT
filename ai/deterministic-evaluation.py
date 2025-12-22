# evaluator_decider.py
import os
import json
from mistralai import Mistral
from dotenv import load_dotenv, find_dotenv

# Load env
load_dotenv(find_dotenv())
API_KEY = os.getenv("MISTRAL_API_KEY")
if not API_KEY:
    raise ValueError("MISTRAL_API_KEY not found")

client = Mistral(api_key=API_KEY)

CONFIDENCE_THRESHOLD = 60


def evaluate_response(user_query: str, llm_answer: str) -> dict:
    """
    Evaluate confidence, detect risks, and decide escalation.
    """

    system_prompt = """You are an evaluator system.

Your job:
1. Evaluate confidence score (0-100) of the answer.
2. Detect:
   - negative emotions
   - sensitive data
   - non-standard or ambiguous requests
3. Decide if escalation is required.

Respond ONLY in JSON with this format:
{
  "confidence": 0-100,
  "negative_emotion": true/false,
  "sensitive_data": true/false,
  "non_standard": true/false,
  "escalate": true/false,
  "reason": "short explanation"
}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"""
User query:
{user_query}

LLM answer:
{llm_answer}
"""
        }
    ]

    response = client.chat.complete(
        model="mistral-small-latest",
        messages=messages,
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)

    # Enforce escalation rule
    if result["confidence"] < CONFIDENCE_THRESHOLD:
        result["escalate"] = True
        result["reason"] += " | Confidence below threshold"

    return result


def build_escalation_context(
    user_query: str,
    llm_answer: str,
    evaluation: dict
) -> dict:
    """
    Build structured escalation payload
    """
    return {
        "escalation": True,
        "confidence": evaluation["confidence"],
        "detected_issues": {
            "negative_emotion": evaluation["negative_emotion"],
            "sensitive_data": evaluation["sensitive_data"],
            "non_standard": evaluation["non_standard"]
        },
        "reason": evaluation["reason"],
        "original_query": user_query,
        "llm_answer": llm_answer
    }


# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    query = "I am really frustrated, nothing works and my data might be exposed"
    answer = "Try restarting the system and check your security settings."

    evaluation = evaluate_response(query, answer)

    print("\n--- Evaluation ---\n")
    print(json.dumps(evaluation, indent=2))

    if evaluation["escalate"]:
        escalation_context = build_escalation_context(
            query, answer, evaluation
        )
        print("\n--- Escalation Context ---\n")
        print(json.dumps(escalation_context, indent=2))

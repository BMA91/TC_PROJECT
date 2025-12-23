import sys
import json
import io
import contextlib

try:
    from .agent_manager import AgentManager
except Exception:
    from agent_manager import AgentManager


def extract_answer_from_result(result: dict) -> str:
    # Prefer final_response, then proposed_answer, then orientation summary or reason
    if not isinstance(result, dict):
        return str(result)
    if "final_response" in result and result["final_response"]:
        return result["final_response"]
    if "proposed_answer" in result and result["proposed_answer"]:
        return result["proposed_answer"]
    if "orientation" in result and isinstance(result["orientation"], dict):
        return result["orientation"].get("summary", result.get("reason", ""))
    return result.get("reason", "") or ""


def main():
    if len(sys.argv) < 2:
        print("Usage: python evaluation_handler.py <input_json_file>")
        sys.exit(1)

    input_path = sys.argv[1]

    with open(input_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    questions = payload.get("Questions", [])
    if not isinstance(questions, list):
        print("Input JSON must contain a 'Questions' array")
        sys.exit(1)

    manager = AgentManager()

    answers = []

    # We'll suppress stdout/stderr while processing tickets to ensure only the final
    # JSON is printed (automated evaluators rely on exact output).
    for q in questions:
        qid = q.get("id")
        query = q.get("query", "")

        # suppress noisy prints/logs from the pipeline
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            try:
                result = manager.process_ticket(query)
            except Exception as e:
                result = {"status": "error", "reason": f"Processing error: {e}"}

        answer_text = extract_answer_from_result(result)

        # Ensure strings only
        if not isinstance(answer_text, str):
            try:
                answer_text = json.dumps(answer_text, ensure_ascii=False)
            except Exception:
                answer_text = str(answer_text)

        answers.append({"id": qid, "answer": answer_text})

    output = {"Team": "TEAM 5", "Answers": answers}

    # Print only the required JSON to stdout
    json.dump(output, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()

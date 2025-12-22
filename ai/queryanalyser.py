# queryanalyser.py
import os
import json
from mistralai import Mistral
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env
load_dotenv(find_dotenv())
API_KEY = os.environ.get("MISTRAL_API_KEY")
if not API_KEY:
    raise ValueError("Please set MISTRAL_API_KEY in your .env file")

# Initialize Mistral client
client = Mistral(api_key=API_KEY)

def analyse_query(query: str) -> dict:
    """
    Sends a query to Mistral and returns a summary and keywords.
    Output format:
    {
        "summary": "short summary of the query",
        "keywords": ["key", "words", "here"]
    }
    """
    # Prompt for the model
    system_prompt = """You are a helpful assistant that reads a query and outputs:
1. A short summary of the query in French.
2. Key keywords as a list.

Respond ONLY in JSON format:
{"summary": "...", "keywords": ["...", "..."]}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]

    response = client.chat.complete(
        model="mistral-small-latest",
        messages=messages,
        response_format={"type": "json_object"}  # Force JSON output
    )

    # Extract JSON from model
    try:
        content = response.choices[0].message.content
        result = json.loads(content)
    except (KeyError, json.JSONDecodeError):
        result = {"summary": "[Error: could not parse response]", "keywords": []}

    return result

if __name__ == "__main__":
    query = input("Enter your query or text: ")
    result = analyse_query(query)

    print("\n--- Query Analysis ---\n")
    print(f"Summary:\n{result['summary']}\n")
    print(f"Keywords:\n{', '.join(result['keywords'])}")

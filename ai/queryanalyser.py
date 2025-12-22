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
    Sends a query to Mistral and returns a summary, keywords, and an optimized version.
    Output format:
    {
        "summary": "short summary of the query",
        "keywords": ["key", "words", "here"],
        "is_sufficient": true/false,
        "optimized_query": "expanded query with synonyms and details"
    }
    """
    # Prompt for the model
    system_prompt = """You are an expert query analyzer for a technical support system.
Your task is to:
1. Provide a short summary of the query in French.
2. Extract key keywords.
3. Evaluate if the query is sufficient (detailed enough) to find a precise solution in a technical documentation.
4. Provide an 'optimized_query':
   - If the query is too short or vague, expand it by detailing the likely technical context.
   - Replace common words with technical synonyms to improve search results (RAG).
   - If the query is already good, just refine it slightly for better search.

Respond ONLY in JSON format:
{
    "summary": "...",
    "keywords": ["...", "..."],
    "is_sufficient": true,
    "optimized_query": "..."
}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]

    try:
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=messages,
            response_format={"type": "json_object"}  # Force JSON output
        )
        # Extract JSON from model
        content = response.choices[0].message.content
        result = json.loads(content)
    except Exception as e:
        print(f"⚠️ Erreur lors de l'appel à l'API Mistral : {e}")
        result = {
            "summary": "[Erreur de connexion ou de traitement]", 
            "keywords": [],
            "is_sufficient": False,
            "optimized_query": query,
            "error": str(e)
        }

    return result

if __name__ == "__main__":
    query = input("Enter your query or text: ")
    result = analyse_query(query)

    print("\n--- Query Analysis ---\n")
    print(f"Summary:\n{result['summary']}\n")
    print(f"Keywords:\n{', '.join(result['keywords'])}")

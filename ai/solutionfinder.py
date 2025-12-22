# solution_finder.py
import os
import json
import numpy as np
from mistralai import Mistral
from dotenv import load_dotenv, find_dotenv

# Load env
load_dotenv(find_dotenv())
API_KEY = os.getenv("MISTRAL_API_KEY")
if not API_KEY:
    raise ValueError("MISTRAL_API_KEY not found")

client = Mistral(api_key=API_KEY)

# -----------------------------
# Utils
# -----------------------------
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def embed_texts(texts):
    """Embed a list of texts"""
    response = client.embeddings.create(
        model="mistral-embed",
        inputs=texts
    )
    return [e.embedding for e in response.data]


# -----------------------------
# RAG Core
# -----------------------------
def retrieve_top_docs(query, documents, k=3):
    """
    documents = [{"id": str, "content": str}]
    """
    doc_texts = [doc["content"] for doc in documents]

    doc_embeddings = embed_texts(doc_texts)
    query_embedding = embed_texts([query])[0]

    scored_docs = []
    for doc, emb in zip(documents, doc_embeddings):
        score = cosine_similarity(query_embedding, emb)
        scored_docs.append((score, doc))

    scored_docs.sort(reverse=True, key=lambda x: x[0])
    return scored_docs[:k]


def generate_answer(query, retrieved_docs):
    """
    Generate grounded answer using retrieved snippets
    """
    context = "\n\n".join(
        f"[Doc {i+1}] {doc['content'][:500]}"
        for i, (_, doc) in enumerate(retrieved_docs)
    )

    system_prompt = """You are a solution finder.
Use ONLY the provided documents to answer.
If information is missing, say so clearly.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"""
Context documents:
{context}

Question:
{query}

Answer with a clear solution and short explanation.
"""
        }
    ]

    response = client.chat.complete(
        model="mistral-small-latest",
        messages=messages
    )

    return response.choices[0].message.content


# -----------------------------
# Main API
# -----------------------------
def solution_finder(query, documents, top_k=3):
    retrieved = retrieve_top_docs(query, documents, k=top_k)

    answer = generate_answer(query, retrieved)

    return {
        "query": query,
        "used_documents": [
            {"id": doc["id"], "score": round(score, 3)}
            for score, doc in retrieved
        ],
        "answer": answer
    }


# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    docs = [
        {
            "id": "doc1",
            "content": "Mistral models support chat completion and embeddings for RAG pipelines."
        },
        {
            "id": "doc2",
            "content": "RAG combines retrieval and generation to improve factual accuracy."
        },
        {
            "id": "doc3",
            "content": "Embeddings allow semantic search using cosine similarity."
        }
    ]

    user_query = input("Enter your question: ")

    result = solution_finder(user_query, docs, top_k=2)

    print("\n--- RAG RESULT ---\n")
    print("Answer:\n", result["answer"])
    print("\nUsed documents:")
    for d in result["used_documents"]:
        print(f"- {d['id']} (score={d['score']})")

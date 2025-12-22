# solution_finder.py
import os
import json
import numpy as np
import chromadb
from chromadb.utils import embedding_functions
from mistralai import Mistral
from dotenv import load_dotenv, find_dotenv
from pdf_processor import convert_pdf_to_markdown

# Load env
load_dotenv(find_dotenv())
API_KEY = os.getenv("MISTRAL_API_KEY")
if not API_KEY:
    raise ValueError("MISTRAL_API_KEY not found")

client = Mistral(api_key=API_KEY)

# -----------------------------
# ChromaDB Setup
# -----------------------------
# Initialize ChromaDB client (persistent storage)
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Use ChromaDB's built-in Mistral embedding function
# It will automatically use the MISTRAL_API_KEY from the environment
mistral_ef = embedding_functions.MistralEmbeddingFunction(
    model="mistral-embed"
)

def get_or_create_collection(name="ticket_knowledge_base"):
    return chroma_client.get_or_create_collection(
        name=name, 
        embedding_function=mistral_ef
    )

# -----------------------------
# Ingestion
# -----------------------------
def ingest_pdf_to_chroma(pdf_path: str, category: str = "general", collection_name="ticket_knowledge_base"):
    """
    Converts PDF to Markdown via Mistral OCR and stores in ChromaDB.
    ChromaDB handles the embedding automatically.
    """
    collection = get_or_create_collection(collection_name)
    
    # 1. Convert PDF to Markdown
    markdown_content = convert_pdf_to_markdown(pdf_path)
    
    # 2. Simple chunking (by paragraph for now)
    chunks = [c.strip() for c in markdown_content.split("\n\n") if c.strip()]
    
    # 3. Add to Chroma (Embeddings are handled by mistral_ef automatically)
    print(f"Ingesting {len(chunks)} chunks into ChromaDB (Category: {category})...")
    ids = [f"{os.path.basename(pdf_path)}_{i}" for i in range(len(chunks))]
    metadatas = [{"source": pdf_path, "category": category} for _ in chunks]
    
    # Batching to avoid "Too many inputs" error from Mistral API
    batch_size = 50
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i + batch_size]
        batch_ids = ids[i:i + batch_size]
        batch_metadatas = metadatas[i:i + batch_size]
        
        collection.add(
            documents=batch_chunks,
            ids=batch_ids,
            metadatas=batch_metadatas
        )
    print("Ingestion complete.")

# -----------------------------
# RAG Core
# -----------------------------
def retrieve_from_chroma(query, category: str = None, collection_name="ticket_knowledge_base", k=3):
    collection = get_or_create_collection(collection_name)
    
    # Prepare filter if category is provided
    where_filter = {"category": category} if category else None

    # ChromaDB handles the query embedding automatically
    results = collection.query(
        query_texts=[query],
        n_results=k,
        where=where_filter
    )
    
    # Format results to match previous structure
    formatted_results = []
    if results['documents']:
        for i in range(len(results['documents'][0])):
            formatted_results.append((
                1.0, # Score placeholder
                {
                    "id": results['ids'][0][i],
                    "content": results['documents'][0][i]
                }
            ))
    return formatted_results

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
def solution_finder(query, category: str = None, collection_name="ticket_knowledge_base", top_k=3):
    retrieved = retrieve_from_chroma(query, category=category, collection_name=collection_name, k=top_k)

    answer = generate_answer(query, retrieved)

    return {
        "query": query,
        "used_documents": [
            {"id": doc["id"], "content": doc["content"]}
            for _, doc in retrieved
        ],
        "answer": answer
    }


# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    # Example: Ingest a PDF if it exists
    # ingest_pdf_to_chroma("votre_document.pdf")

    user_query = input("Enter your question: ")
    result = solution_finder(user_query)

    print("\n--- RAG RESULT ---\n")
    print("Answer:\n", result["answer"])
    print("\nUsed documents:")
    for d in result["used_documents"]:
        print(f"- {d['id']}")

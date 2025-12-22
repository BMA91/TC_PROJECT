import os
import json
from dotenv import load_dotenv
from mistralai import Mistral
from precheck import TicketPrechecker
from queryanalyser import analyse_query
from solutionfinder import solution_finder
from deterministic_evaluation import DeterministicEvaluator
from response_composer import compose_response

# Load environment variables
load_dotenv()

class AgentManager:
    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY not found in .env file")
        
        self.client = Mistral(api_key=self.api_key)
        self.prechecker = TicketPrechecker()
        self.evaluator = DeterministicEvaluator()
        self.model = "mistral-large-latest"
        
        # Mock Knowledge Base
        self.knowledge_base = [
            {"id": "kb1", "content": "Pour réinitialiser votre mot de passe, cliquez sur 'Mot de passe oublié' sur la page de connexion."},
            {"id": "kb2", "content": "Nos délais de livraison standard sont de 3 à 5 jours ouvrables."},
            {"id": "kb3", "content": "Le support technique est disponible de 9h à 18h, du lundi au vendredi."},
            {"id": "kb4", "content": "Vous pouvez retourner un article dans les 30 jours suivant l'achat s'il est dans son emballage d'origine."}
        ]

    def process_ticket(self, ticket_content):
        print(f"Processing ticket: {ticket_content[:50]}...")
        
        # Step 1: Presearch (no LLM)
        precheck_results = self.prechecker.run_precheck(ticket_content)
        
        if not precheck_results["passed"]:
            return {
                "status": "rejected",
                "reason": precheck_results["reason"],
                "details": precheck_results
            }
        
        # Use masked content for the AI agent
        content_to_process = precheck_results["masked_content"]
        
        # Step 2: Query Analyser (LLM CALL)
        print("Analysing query...")
        analysis = analyse_query(content_to_process)
        
        # Step 3: Solution Finder (LLM CALL - RAG)
        print("Finding solution...")
        rag_result = solution_finder(content_to_process, self.knowledge_base)
        proposed_answer = rag_result["answer"]
        
        # Get context used for evaluation
        context_used = "\n".join([doc["content"] for doc in self.knowledge_base if any(d["id"] == doc["id"] for d in rag_result["used_documents"])])

        # Step 4: Deterministic Evaluation (Hugging Face model)
        print("Evaluating solution confidence...")
        evaluation = self.evaluator.evaluate(context_used, proposed_answer)
        
        # Step 5 & 5.1: Logic based on confidence
        if evaluation["confidence_score"] >= 0.6:
            print(f"Confidence high ({evaluation['confidence_score']}). Composing response...")
            # Step 5: Response Composer (LLM)
            final_response_data = compose_response(content_to_process, proposed_answer, evaluation)
            
            return {
                "status": "success",
                "final_response": final_response_data["final_response"],
                "confidence": evaluation["confidence_score"],
                "analysis": analysis,
                "precheck": precheck_results,
                "proposed_answer": proposed_answer # Keep for reference
            }
        else:
            # Step 5.1: Orient to specialist human agent (NO LLM)
            print(f"Confidence low ({evaluation['confidence_score']}). Orienting to human agent...")
            return self.orient_to_human(analysis, precheck_results)

    def orient_to_human(self, analysis, precheck_results):
        """
        Orient the ticket to a specialist human agent using summary and keywords.
        """
        summary = analysis.get("summary", "N/A")
        keywords = analysis.get("keywords", [])
        
        # Logic to "orient" could be more complex, but here we just return the info
        return {
            "status": "escalated",
            "reason": "Low confidence in AI response",
            "orientation": {
                "summary": summary,
                "keywords": keywords,
                "target_department": "Specialist Human Agent"
            },
            "precheck": precheck_results
        }

    def handle_rating(self, ticket_id, stars, analysis, precheck_results):
        """
        Handle client rating. If <= 2 stars, escalate to human.
        """
        if stars <= 2:
            print(f"Rating low ({stars} stars). Escalating to human...")
            return self.orient_to_human(analysis, precheck_results)
        else:
            return {"status": "completed", "message": "Thank you for your feedback!"}

if __name__ == "__main__":
    manager = AgentManager()
    
    # Test with a valid French ticket
    ticket = "Bonjour, j'ai oublié mon mot de passe. Comment puis-je le réinitialiser ?"
    result = manager.process_ticket(ticket)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Simulate a low rating
    if result["status"] == "success":
        print("\n--- Simulating low rating (2 stars) ---")
        rating_result = manager.handle_rating("ticket_123", 2, result["analysis"], result["precheck"])
        print(json.dumps(rating_result, indent=2, ensure_ascii=False))

import os
from dotenv import load_dotenv
from mistralai import Mistral
from precheck import TicketPrechecker
from solutionfinder import solution_finder
from deterministic_evaluation import DeterministicEvaluator

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
        
        # Step 1: Rule-based Precheck
        precheck_results = self.prechecker.run_precheck(ticket_content)
        
        if not precheck_results["passed"]:
            return {
                "status": "rejected",
                "reason": precheck_results["reason"],
                "details": precheck_results
            }
        
        # Use masked content for the AI agent
        content_to_process = precheck_results["masked_content"]
        
        # Step 2: Solution Finder (RAG)
        print("Precheck passed. Finding solution...")
        rag_result = solution_finder(content_to_process, self.knowledge_base)
        proposed_answer = rag_result["answer"]
        
        # Get context used for evaluation
        context_used = "\n".join([doc["content"] for doc in self.knowledge_base if any(d["id"] == doc["id"] for d in rag_result["used_documents"])])

        # Step 3: Deterministic Evaluation (Hugging Face)
        print("Evaluating solution confidence...")
        evaluation = self.evaluator.evaluate(context_used, proposed_answer)
        
        if not evaluation["passed"]:
            print(f"Warning: Low confidence ({evaluation['confidence_score']}). Escalating...")
            return {
                "status": "escalated",
                "reason": "Low confidence in generated answer",
                "evaluation": evaluation,
                "proposed_answer": proposed_answer
            }

        # Step 4: Final Success
        return {
            "status": "success",
            "response": proposed_answer,
            "confidence": evaluation["confidence_score"],
            "precheck": precheck_results
        }

if __name__ == "__main__":
    manager = AgentManager()
    
    # Test with a valid French ticket
    ticket = "Bonjour, j'ai oublié mon mot de passe. Comment puis-je le réinitialiser ?"
    result = manager.process_ticket(ticket)
    
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))

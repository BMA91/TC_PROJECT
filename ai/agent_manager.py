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
        """
        Orchestrate the full ticket processing pipeline.
        """
        print("\n" + "="*50)
        print("DÉBUT DU TRAITEMENT DU TICKET")
        print("="*50)

        # Step 1: Precheck
        print("\n[Étape 1] Pré-vérification...")
        precheck_results = self.prechecker.run_precheck(ticket_content)
        
        if not precheck_results["passed"]:
            print(f"❌ Échec de la pré-vérification : {', '.join(precheck_results['reason'])}")
            return {
                "status": "rejected",
                "reason": precheck_results["reason"],
                "details": precheck_results
            }
        
        print("✅ Pré-vérification réussie.")
        if precheck_results["has_sensitive_data"]:
            print("⚠️ Données sensibles détectées et masquées.")

        # Use masked content for the AI agent
        content_to_process = precheck_results["masked_content"]
        
        # Step 2: Query Analyser (LLM CALL)
        print("\n[Étape 2] Analyse de la requête...")
        analysis = analyse_query(content_to_process)
        print(f"📝 Résumé : {analysis.get('summary')}")
        print(f"🔑 Mots-clés : {', '.join(analysis.get('keywords', []))}")
        
        # Step 3: Solution Finder (LLM CALL - RAG)
        print("\n[Étape 3] Recherche de solution (RAG)...")
        rag_result = solution_finder(content_to_process)
        proposed_answer = rag_result["answer"]
        print(f"💡 Solution proposée : {proposed_answer[:100]}...")
        
        # Get context used for evaluation
        context_used = "\n".join([doc["content"] for doc in rag_result["used_documents"]])

        # Step 4: Deterministic Evaluation (Hugging Face model)
        print("\n[Étape 4] Évaluation de la confiance...")
        evaluation = self.evaluator.evaluate(context_used, proposed_answer)
        print(f"📊 Score de confiance : {evaluation['confidence_score']}")
        
        # Step 5 & 5.1: Logic based on confidence
        if evaluation["confidence_score"] >= 0.6:
            print(f"✅ Confiance élevée. Composition de la réponse finale...")
            # Step 5: Response Composer (LLM)
            final_response_data = compose_response(content_to_process, proposed_answer, evaluation)
            
            print("\n" + "-"*30)
            print("RÉPONSE FINALE :")
            print(final_response_data["final_response"])
            print("-"*30)

            return {
                "status": "success",
                "final_response": final_response_data["final_response"],
                "confidence": evaluation["confidence_score"],
                "analysis": analysis,
                "precheck": precheck_results,
                "proposed_answer": proposed_answer
            }
        else:
            # Step 5.1: Orient to specialist human agent (NO LLM)
            print(f"⚠️ Confiance faible ({evaluation['confidence_score']}). Orientation vers un agent humain...")
            result = self.orient_to_human(analysis, precheck_results)
            print(f"👨‍💼 Orienté vers : {result['orientation']['target_department']}")
            return result

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
    from solutionfinder import ingest_pdf_to_chroma
    manager = AgentManager()
    
    print("\n=== SYSTÈME DE GESTION DE TICKETS IA ===")
    print("Commandes spéciales :")
    print("  /ingest path/to/file.pdf [category]  -> Ajouter un document (catégorie optionnelle)")
    
    while True:
        print("\n" + "-"*50)
        ticket = input("Veuillez saisir votre message (ou 'exit' pour quitter) : ")
        
        if ticket.lower() in ['exit', 'quit']:
            print("Fermeture du système. Au revoir !")
            break
            
        if ticket.startswith("/ingest "):
            # Improved parsing to handle spaces in category
            content = ticket.replace("/ingest ", "").strip()
            if content.startswith('"'):
                # Handle quoted path
                end_quote = content.find('"', 1)
                pdf_path = content[1:end_quote]
                category = content[end_quote+1:].strip() or "general"
            else:
                parts = content.split(" ", 1)
                pdf_path = parts[0]
                category = parts[1].strip() if len(parts) > 1 else "general"
            
            if os.path.exists(pdf_path):
                try:
                    ingest_pdf_to_chroma(pdf_path, category=category)
                except Exception as e:
                    print(f"❌ Erreur lors de l'ingestion : {e}")
            else:
                print(f"❌ Fichier introuvable : {pdf_path}")
            continue

        if not ticket.strip():
            continue
            
        try:
            result = manager.process_ticket(ticket)
            
            # Optionnel : Demander une évaluation si le traitement a réussi
            if result["status"] == "success":
                try:
                    print("\nComment évalueriez-vous cette réponse ? (1-5 étoiles)")
                    stars = input("Étoiles : ")
                    if stars.isdigit():
                        stars = int(stars)
                        rating_result = manager.handle_rating("ticket_id", stars, result["analysis"], result["precheck"])
                        if rating_result["status"] == "escalated":
                            print(f"\n⚠️ Suite à votre note, le ticket a été orienté vers : {rating_result['orientation']['target_department']}")
                        else:
                            print(f"\n✅ {rating_result['message']}")
                except Exception as e:
                    print(f"Erreur lors de l'évaluation : {e}")
        except Exception as e:
            print(f"\n❌ Une erreur inattendue est survenue : {e}")
            print("Veuillez vérifier votre connexion internet et réessayer.")

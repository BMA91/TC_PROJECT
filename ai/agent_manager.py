import os
from dotenv import load_dotenv
from mistralai import Mistral
from precheck import TicketPrechecker

# Load environment variables
load_dotenv()

class AgentManager:
    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY not found in .env file")
        
        self.client = Mistral(api_key=self.api_key)
        self.prechecker = TicketPrechecker()
        self.model = "mistral-large-latest"

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
        
        # Step 2: Mistral AI Agent (if precheck passed)
        print("Precheck passed. Calling Mistral AI...")
        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Vous êtes un assistant de support client expert. Répondez de manière professionnelle et concise en français."},
                    {"role": "user", "content": content_to_process}
                ]
            )
            
            return {
                "status": "success",
                "response": response.choices[0].message.content,
                "precheck": precheck_results
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

if __name__ == "__main__":
    manager = AgentManager()
    
    # Test with a valid French ticket
    ticket = "Bonjour, j'ai un problème avec ma connexion internet depuis ce matin. Pouvez-vous m'aider ?"
    result = manager.process_ticket(ticket)
    print(result)

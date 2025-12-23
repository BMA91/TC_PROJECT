import re
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Ensure consistent results for language detection
DetectorFactory.seed = 0

class TicketPrechecker:
    def __init__(self):
        # Common spam keywords (English and French)
        self.spam_keywords = [
            "win money", "free gift", "click here", "subscribe now", 
            "lottery", "congratulations", "urgent action required",
            "buy now", "limited time", "cash prize", "earn money",
            "work from home", "no cost", "risk free", "winner",
            "claim now", "exclusive deal", "investment", "crypto", "bitcoin",
            "gagner de l'argent", "cadeau gratuit", "cliquez ici", "abonnez-vous",
            "loterie", "félicitations", "action urgente", "offre exclusive",
            "investissement", "gagner gros", "promotion", "rabais"
        ]

    def check_language(self, text):
        """Verify if the language is French or English with a fallback for short texts."""
        # Common French and English words to help with short queries
        language_indicators = [
            # French
            "ca", "pas", "le", "la", "les", "un", "une", "est", "sont", 
            "fait", "marche", "probleme", "aide", "svp", "merci", "mon", "ma", "salut", "bonjour",
            # English
            "hi", "hello", "the", "is", "are", "not", "it", "works", "problem", "help", "please", "thanks", "my"
        ]
        
        text_lower = text.lower()
        
        # If the text contains common indicators, we are more lenient
        has_indicator = any(f" {word} " in f" {text_lower} " for word in language_indicators)
        
        try:
            lang = detect(text)
            if lang in ['fr', 'en']:
                return True
            # If langdetect is unsure but we have indicators, we accept it
            if has_indicator:
                return True
            return False
        except LangDetectException:
            return has_indicator

    def is_spam(self, text):
        """Check for common spam keywords."""
        text_lower = text.lower()
        for keyword in self.spam_keywords:
            if keyword in text_lower:
                return True
        return False

    def run_precheck(self, ticket_content):
        """Run all prechecks and return a report."""
        results = {
            "is_supported_lang": self.check_language(ticket_content),
            "is_spam": self.is_spam(ticket_content),
            "passed": False,
            "reason": []
        }

        if not results["is_supported_lang"]:
            results["reason"].append("Language is not supported (Only French and English are accepted).")
        
        if results["is_spam"]:
            results["reason"].append("Ticket identified as spam.")

        # If it's a supported language and not spam, we let it pass
        if results["is_supported_lang"] and not results["is_spam"]:
            results["passed"] = True
            
        return results

if __name__ == "__main__":
    # Interactive mode
    checker = TicketPrechecker()
    print("--- Ticket Prechecker Interactive Mode ---")
    print("Type your ticket content below to test (or type 'exit' to quit):")
    
    while True:
        user_input = input("\nTicket > ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        if not user_input.strip():
            continue
            
        results = checker.run_precheck(user_input)
        print("\nResults:")
        print(f"  Passed: {results['passed']}")
        print(f"  Supported Lang: {results['is_supported_lang']}")
        print(f"  Spam: {results['is_spam']}")
        print(f"  Sensitive Data: {results['has_sensitive_data']}")
        print(f"  Masked Content: {results['masked_content']}")
        if results['reason']:
            print(f"  Reasons: {', '.join(results['reason'])}")
        print("-" * 30)

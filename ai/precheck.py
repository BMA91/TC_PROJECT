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
        
        # Regex for sensitive data
        # Credit card: simple pattern for 13-16 digits
        self.card_pattern = re.compile(r'\b(?:\d[ -]*?){13,16}\b')
        # Password: looking for "password", "pwd", "mot de passe" followed by optional "is/est", then ":" or "=" or just a space
        self.password_pattern = re.compile(r'(password|pwd|mot de passe)(?:\s+(?:is|est))?\s*[:=\s]\s*(\S+)', re.IGNORECASE)

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

    def has_sensitive_data(self, text):
        """Check for card numbers or passwords."""
        if self.card_pattern.search(text):
            return True
        if self.password_pattern.search(text):
            return True
        return False

    def mask_sensitive_data(self, text):
        """Replace card numbers and passwords with ****."""
        # Mask card numbers (13-16 digits)
        masked_text = self.card_pattern.sub('**** **** **** ****', text)
        
        # Mask passwords using the updated regex
        # Group 1 is the keyword, Group 2 is the value to mask
        # We use a sub with a backreference to keep the keyword and separator
        masked_text = self.password_pattern.sub(lambda m: m.group(0).replace(m.group(2), "****"), masked_text)
        
        return masked_text

    def run_precheck(self, ticket_content):
        """Run all prechecks and return a report."""
        has_sensitive = self.has_sensitive_data(ticket_content)
        masked_content = self.mask_sensitive_data(ticket_content) if has_sensitive else ticket_content
        
        results = {
            "is_supported_lang": self.check_language(ticket_content),
            "is_spam": self.is_spam(ticket_content),
            "has_sensitive_data": has_sensitive,
            "masked_content": masked_content,
            "passed": False,
            "reason": []
        }

        if not results["is_supported_lang"]:
            results["reason"].append("Language is not supported (Only French and English are accepted).")
        
        if results["is_spam"]:
            results["reason"].append("Ticket identified as spam.")
            
        # We still flag sensitive data, but we provide the masked version
        if results["has_sensitive_data"]:
            results["reason"].append("Sensitive data was detected and masked.")

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

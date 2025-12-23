
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.email_service import email_service

if __name__ == "__main__":
    to = "aymenbelkadi1012005@gmail.com"
    subject = "Test EmailService - Outlook"
    body = "Bonjour Aymen,\n\nCeci est un test automatique de l'envoi d'email via le service Outlook configuré dans TC_PROJECT.\n\nSi tu reçois ce message, la configuration fonctionne !\n\n--\nTC_PROJECT Bot"
    result = email_service.send_email(to, subject, body)
    print("Résultat de l'envoi :", result)

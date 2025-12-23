import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class EmailService:
    """
    Service pour envoyer des emails via SMTP.
    Supporte les configurations standard SMTP et les services comme Gmail, Outlook, etc.
    """
    
    def __init__(
        self,
        smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        smtp_port: int = int(os.getenv("SMTP_PORT", 587)),
        sender_email: str = os.getenv("SENDER_EMAIL", ""),
        sender_password: str = os.getenv("SENDER_PASSWORD", ""),
        use_tls: bool = True
    ):
        """
        Initialise le service email.
        
        Args:
            smtp_server: Adresse du serveur SMTP
            smtp_port: Port du serveur SMTP
            sender_email: Email de l'expéditeur
            sender_password: Mot de passe ou app password
            use_tls: Utiliser TLS pour la connexion sécurisée
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.use_tls = use_tls
    
    def send_email(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        is_html: bool = False
    ) -> dict:
        """
        Envoie un email.
        
        Args:
            recipient_email: Email du destinataire
            subject: Sujet de l'email
            body: Corps de l'email
            is_html: Si True, le corps est du HTML
        
        Returns:
            {
                "success": bool,
                "message": str,
                "error": str or None
            }
        """
        try:
            # Créer le message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            # Ajouter le corps du message
            mime_type = "html" if is_html else "plain"
            message.attach(MIMEText(body, mime_type))
            
            # Connecter au serveur SMTP et envoyer
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            return {
                "success": True,
                "message": f"Email sent successfully to {recipient_email}",
                "error": None
            }
        
        except smtplib.SMTPAuthenticationError as e:
            error_msg = "SMTP Authentication failed. Check email and password."
            print(f"❌ {error_msg}: {str(e)}")
            return {
                "success": False,
                "message": None,
                "error": error_msg
            }
        
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error occurred: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "message": None,
                "error": error_msg
            }
        
        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "message": None,
                "error": error_msg
            }
    
    def send_agent_response_email(
        self,
        client_email: str,
        client_name: str,
        ticket_reference: str,
        subject: str,
        body: str
    ) -> dict:
        """
        Envoie une email de réponse d'agent à un client.
        
        Args:
            client_email: Email du client
            client_name: Nom du client
            ticket_reference: Référence du ticket
            subject: Sujet de l'email
            body: Corps de l'email
        
        Returns:
            Résultat de l'envoi
        """
        # Formater le corps de l'email avec un template
        formatted_body = f"""
Bonjour {client_name},

Concernant votre ticket {ticket_reference}:

{body}

---
Cordialement,
Support Technique
"""
        
        return self.send_email(
            recipient_email=client_email,
            subject=subject,
            body=formatted_body,
            is_html=False
        )


# Initialiser le service email avec les variables d'environnement
email_service = EmailService(
    smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    smtp_port=int(os.getenv("SMTP_PORT", "587")),
    sender_email=os.getenv("SENDER_EMAIL", ""),
    sender_password=os.getenv("SENDER_PASSWORD", ""),
    use_tls=True
)

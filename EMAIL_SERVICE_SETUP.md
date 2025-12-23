# Email Service - Agent Response

## Configuration

### 1. Configurez vos variables d'environnement

Créez un fichier `.env` dans le dossier `backend/`:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

### 2. Configuration pour différents fournisseurs

#### Gmail
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=votre-email@gmail.com
SENDER_PASSWORD=votre-app-password
```

**Important:** Vous devez générer un "App Password" au lieu d'utiliser votre mot de passe principal:
1. Allez à: https://myaccount.google.com/apppasswords
2. Sélectionnez "Mail" et "Windows Computer"
3. Copiez le mot de passe généré
4. Utilisez-le dans `SENDER_PASSWORD`

#### Outlook/Microsoft 365
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SENDER_EMAIL=votre-email@outlook.com
SENDER_PASSWORD=votre-mot-de-passe
```

#### SMTP Custom Server
```env
SMTP_SERVER=mail.example.com
SMTP_PORT=587
SENDER_EMAIL=noreply@example.com
SENDER_PASSWORD=votre-mot-de-passe
```

---

## Utilisation

### Envoyer une réponse d'agent (avec email)

```
POST /tickets/{ticket_id}/agent-response
Authorization: Bearer <token>
Content-Type: application/json

{
  "subject": "Réponse à votre ticket REF-2025-000123",
  "body": "Bonjour,\n\nNous avons résolu votre problème. Veuillez vérifier votre compte.\n\nCordialement,\nL'équipe support"
}
```

**Response:**
```json
{
  "ticket": {
    "id": 1,
    "reference_id": "REF-2025-000123",
    "title": "Problème de connexion",
    "status": "en cours",
    "agent_response": "...",
    "agent_response_sent_at": "2025-01-15T10:30:00Z"
  },
  "email_sent": true,
  "email_status": {
    "success": true,
    "message": "Email sent successfully to client@example.com",
    "error": null
  }
}
```

---

## Flux d'Envoi d'Email

```
┌─────────────────┐
│  Agent soumet   │
│    réponse      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Données sauvegardées
│  dans la BD     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  EmailService   │
│  connecte à     │
│  serveur SMTP   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Email envoyé   │
│  au client      │
└─────────────────┘
```

---

## Gestion des Erreurs

Si l'email ne s'envoie pas, le ticket est quand même sauvegardé avec la réponse. La réponse inclura le statut d'envoi:

```json
{
  "email_sent": false,
  "email_status": {
    "success": false,
    "message": null,
    "error": "SMTP Authentication failed. Check email and password."
  }
}
```

---

## Troubleshooting

### "SMTP Authentication failed"
- Vérifiez votre email et mot de passe
- Pour Gmail: utilisez un App Password, pas votre mot de passe principal
- Activez l'accès aux applications moins sécurisées (si nécessaire)

### "Connection timed out"
- Vérifiez le serveur SMTP et le port
- Vérifiez votre connexion internet
- Vérifiez que le port n'est pas bloqué par votre firewall

### Email not received
- Vérifiez le spam/dossier indésirable
- Vérifiez l'adresse email du client
- Vérifiez que le serveur SMTP accepte les emails sortants

---

## Sécurité

⚠️ **Ne commitez jamais votre `.env` avec les vrais identifiants!**

1. Ajoutez `.env` à `.gitignore`
2. Utilisez `.env.example` comme template
3. Chaque développeur doit créer son propre `.env` local

---

## Templates Personnalisés

Vous pouvez personnaliser le template d'email dans `app/services/email_service.py`:

```python
def send_agent_response_email(self, ...):
    formatted_body = f"""
Bonjour {client_name},

Concernant votre ticket {ticket_reference}:

{body}

---
Cordialement,
Support Technique
"""
```

Modifiez le format selon vos besoins! 📧

from datetime import datetime
from pydantic import BaseModel, Field, model_validator

from app.models.ticket import TicketType, TicketStatus


class TicketCreate(BaseModel):
    """
    Schema pour créer un ticket par un client.
    
    Exemple JSON:
    ```json
    {
        "title": "Problème de connexion",
        "description": "Je ne peux pas me connecter à mon compte depuis hier",
        "ticket_type": "Support and Reference Documentation"
    }
    ```
    """
    title: str = Field(
        ...,
        description="Titre du ticket",
        example="Problème de connexion",
        min_length=3,
        max_length=200
    )
    description: str = Field(
        ...,
        description="Description détaillée du problème ou de la demande",
        example="Je ne peux pas me connecter à mon compte depuis hier. J'ai essayé de réinitialiser mon mot de passe mais je ne reçois pas l'email.",
        min_length=10
    )
    ticket_type: TicketType = Field(
        ...,
        description="Type de ticket. Options disponibles: 'Legal, Regulatory, and Commercial Frameworks', 'Support and Reference Documentation', 'Operational and Practical User Guides', 'other'",
        example=TicketType.support
    )


class TicketResponse(BaseModel):
    """Schema pour la réponse d'un ticket"""
    id: int = Field(..., description="ID unique du ticket")
    reference_id: str = Field(..., description="Référence unique du ticket (ex: REF-2025-000123)", example="REF-2025-000123")
    title: str = Field(..., description="Titre du ticket")
    description: str = Field(..., description="Description du ticket")
    ticket_type: TicketType = Field(..., description="Type de ticket")
    status: TicketStatus = Field(..., description="Statut du ticket")
    category: str | None = Field(None, description="Catégorie auto-détectée (optionnelle)")
    client_id: int = Field(..., description="ID du client propriétaire du ticket")
    assigned_agent_id: int | None = Field(None, description="ID de l'agent assigné (si assigné)")
    created_at: datetime = Field(..., description="Date de création du ticket")
    updated_at: datetime | None = Field(None, description="Date de dernière mise à jour")
    # AI Escalation fields
    is_escalated: bool = Field(False, description="Indique si le ticket a été escaladé par l'AI")
    escalated_at: datetime | None = Field(None, description="Date d'escalade par l'AI")
    # Agent response fields
    agent_response: str | None = Field(None, description="Réponse de l'agent (contenu de l'email)")
    agent_response_subject: str | None = Field(None, description="Sujet de l'email de réponse")
    agent_response_sent_at: datetime | None = Field(None, description="Date d'envoi de la réponse de l'agent")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "reference_id": "REF-2025-000123",
                "title": "Problème de connexion",
                "description": "Je ne peux pas me connecter à mon compte",
                "ticket_type": "support",
                "status": "en cours",
                "category": None,
                "client_id": 1,
                "assigned_agent_id": None,
                "created_at": "2025-01-15T10:30:00Z",
                "updated_at": None
            }
        }


class TicketUpdate(BaseModel):
    """
    Schema pour mettre à jour un ticket (pour les agents/admin).
    Tous les champs sont optionnels - seuls les champs fournis seront mis à jour.
    """
    title: str | None = Field(None, description="Nouveau titre du ticket", example="Problème résolu")
    description: str | None = Field(None, description="Nouvelle description", example="Le problème a été résolu")
    status: TicketStatus | None = Field(None, description="Nouveau statut. Options: 'en cours', 'fini'", example=TicketStatus.FINI)
    assigned_agent_id: int | None = Field(None, description="ID de l'agent à assigner", example=2)
    category: str | None = Field(None, description="Catégorie du ticket", example="Technical Support")


class TicketFeedbackCreate(BaseModel):
    """
    Schema pour créer un feedback sur un ticket (après une réponse).
    
    Exemple JSON (satisfait):
    ```json
    {
        "is_satisfied": true,
        "rating": 5,
        "reason": null
    }
    ```
    
    Exemple JSON (insatisfait):
    ```json
    {
        "is_satisfied": false,
        "rating": 2,
        "reason": "La réponse n'était pas claire et n'a pas résolu mon problème"
    }
    ```
    """
    is_satisfied: bool = Field(
        ...,
        description="Le client est-il satisfait de la réponse?",
        example=True
    )
    rating: int | None = Field(
        None,
        description="Note sur 5 (1 = très insatisfait, 5 = très satisfait)",
        example=5,
        ge=1,
        le=5
    )
    reason: str | None = Field(
        None,
        description="Raison de l'insatisfaction (requis si is_satisfied = false). Doit être fourni si le client n'est pas satisfait.",
        example="La réponse n'était pas claire"
    )
    
    @model_validator(mode='after')
    def validate_reason_if_not_satisfied(self):
        """Validation: reason est requis si is_satisfied = false"""
        if self.is_satisfied is False and not self.reason:
            raise ValueError("reason is required when is_satisfied is false")
        return self


class TicketFeedbackResponse(BaseModel):
    """Schema pour la réponse d'un feedback"""
    id: int = Field(..., description="ID unique du feedback")
    ticket_id: int = Field(..., description="ID du ticket concerné")
    is_satisfied: bool = Field(..., description="Satisfaction du client")
    rating: int | None = Field(None, description="Note sur 5")
    reason: str | None = Field(None, description="Raison de l'insatisfaction")

    class Config:
        from_attributes = True


class AgentResponseCreate(BaseModel):
    """
    Schema pour la réponse d'un agent à un ticket escaladé par l'AI.
    Cette réponse sera envoyée par email au client.
    
    Exemple JSON:
    ```json
    {
        "subject": "Réponse à votre ticket REF-2025-000123",
        "body": "Bonjour,\n\nNous avons bien reçu votre demande concernant votre problème de connexion. Après investigation, nous avons identifié la cause du problème...\n\nCordialement,\nL'équipe support"
    }
    ```
    """
    subject: str = Field(
        ...,
        description="Sujet de l'email de réponse",
        example="Réponse à votre ticket REF-2025-000123",
        min_length=5,
        max_length=200
    )
    body: str = Field(
        ...,
        description="Corps de l'email de réponse (peut contenir du texte formaté ou HTML)",
        example="Bonjour,\n\nNous avons bien reçu votre demande concernant votre problème de connexion. Après investigation, nous avons identifié la cause du problème et l'avons résolu.\n\nVotre compte devrait maintenant fonctionner normalement. N'hésitez pas à nous contacter si vous rencontrez d'autres difficultés.\n\nCordialement,\nL'équipe support technique",
        min_length=20
    )


class AgentResponseResponse(BaseModel):
    """Schema pour la réponse d'un agent"""
    ticket_id: int = Field(..., description="ID du ticket")
    agent_id: int = Field(..., description="ID de l'agent qui a répondu")
    subject: str = Field(..., description="Sujet de l'email")
    body: str = Field(..., description="Corps de l'email")
    sent_at: datetime = Field(..., description="Date d'envoi de la réponse")
    
    class Config:
        from_attributes = True


class AIProcessingRequest(BaseModel):
    """Schema pour déclencher le traitement AI d'un ticket"""
    ticket_id: int = Field(..., description="ID du ticket à traiter")
    webhook_url: str | None = Field(None, description="URL webhook pour notifier la fin du traitement (optionnel)")


class AIProcessingStatus(BaseModel):
    """Schema pour le statut du traitement AI"""
    ticket_id: int = Field(..., description="ID du ticket")
    status: str = Field(..., description="Statut du traitement: 'processing', 'completed', 'failed', 'timeout'")
    started_at: datetime | None = Field(None, description="Date de début du traitement")
    completed_at: datetime | None = Field(None, description="Date de fin du traitement")
    processing_time_seconds: float | None = Field(None, description="Temps de traitement en secondes")
    error_message: str | None = Field(None, description="Message d'erreur si échec")


class AIPipelineLogResponse(BaseModel):
    """Schema pour les résultats détaillés du pipeline AI"""
    id: int = Field(..., description="ID du log")
    ticket_id: int = Field(..., description="ID du ticket")
    trace_id: str = Field(..., description="ID de traçabilité")
    status: str = Field(..., description="Statut du traitement")
    started_at: datetime = Field(..., description="Date de début")
    completed_at: datetime | None = Field(None, description="Date de fin")
    
    # AI Results
    summary: str | None = Field(None, description="Résumé du ticket")
    keywords: str | None = Field(None, description="Mots-clés (JSON)")
    category: str | None = Field(None, description="Catégorie détectée")
    rag_docs: str | None = Field(None, description="Documents RAG utilisés (JSON)")
    proposed_answer: str | None = Field(None, description="Réponse proposée par l'AI")
    confidence_score: float | None = Field(None, description="Score de confiance (0-1)")
    sentiment: str | None = Field(None, description="Sentiment détecté")
    sensitive_data_detected: bool = Field(False, description="Données sensibles détectées")
    escalation_reason: str | None = Field(None, description="Raison de l'escalade")
    final_response: str | None = Field(None, description="Réponse finale de l'AI")
    
    processing_time_seconds: float | None = Field(None, description="Temps de traitement")
    error_message: str | None = Field(None, description="Message d'erreur")
    
    class Config:
        from_attributes = True


from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.crud import ticket as ticket_crud, user as user_crud
from app.dependencies import get_db
from app.schemas.ticket import (
    TicketCreate, 
    TicketResponse, 
    TicketUpdate,
    TicketFeedbackCreate,
    TicketFeedbackResponse,
    AgentResponseCreate,
    AgentResponseResponse
)
from app.models.ticket import TicketStatus, TicketType

router = APIRouter(prefix="/tickets", tags=["tickets"])


def verify_agent(db: Session, agent_id: int) -> bool:
    """
    Vérifie si un utilisateur est un agent (rôle commence par "agt_").
    En production, utiliser l'authentification JWT.
    """
    agent = user_crud.get_user(db, user_id=agent_id)
    if agent and agent.role.startswith("agt_"):
        return True
    return False


@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un nouveau ticket",
    description="""
    Permet à un client de créer un nouveau ticket.
    
    **Paramètres requis:**
    - **title**: Titre du ticket (minimum 3 caractères)
    - **description**: Description détaillée (minimum 10 caractères)
    - **ticket_type**: Type de ticket (legal, support, ops, OTHER)
    - **client_id**: ID du client (passé en paramètre de requête)
    
    **Exemple de requête:**
    ```json
    {
        "title": "Problème de connexion",
        "description": "Je ne peux pas me connecter à mon compte depuis hier",
        "ticket_type": "support"
    }
    ```
    
    **Note:** En production, le client_id devrait être extrait du token JWT.
    """
)
def create_ticket(
    ticket_in: TicketCreate,
    client_id: int = Query(..., description="ID du client qui crée le ticket (ex: 1)", example=1),
    db: Session = Depends(get_db),
):
    # Vérifier que le client existe
    client = user_crud.get_user(db, user_id=client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )
    
    # Vérifier que c'est bien un client (pas un admin ou agent)
    if client.role not in ["client_1", "client_2", "client_3"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only clients can create tickets",
        )
    
    # Créer le ticket
    ticket = ticket_crud.create_ticket(db=db, ticket_in=ticket_in, client_id=client_id)
    return ticket


@router.get("/", response_model=list[TicketResponse])
def list_tickets(
    client_id: int | None = Query(None, description="Filtrer par client_id (optionnel)"),
    skip: int = Query(0, ge=0, description="Nombre de tickets à sauter (pagination)"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre maximum de tickets à retourner (pagination)"),
    db: Session = Depends(get_db),
):
    """
    Liste les tickets.
    - Si client_id est fourni, retourne uniquement les tickets de ce client
    - Sinon, retourne tous les tickets (pour les agents/admin)
    """
    if client_id:
        tickets = ticket_crud.get_tickets_by_client(db=db, client_id=client_id, skip=skip, limit=limit)
    else:
        tickets = ticket_crud.get_all_tickets(db=db, skip=skip, limit=limit)
    
    return tickets


# ========== ENDPOINTS SPÉCIFIQUES POUR LES AGENTS ==========

@router.get(
    "/agent/list",
    response_model=list[TicketResponse],
    summary="Liste des tickets pour les agents",
    description="""
    Permet aux agents (agt_tech, agt_sales, etc.) de consulter tous les tickets soumis par les clients.
    
    **Fonctionnalités:**
    - Pagination avec skip et limit
    - Filtrage par statut (optionnel)
    - Filtrage par type de ticket (optionnel)
    - Tri par date de création (plus récent en premier)
    
    **Paramètres:**
    - **agent_id**: ID de l'agent (requis pour vérification)
    - **skip**: Nombre de tickets à sauter (défaut: 0)
    - **limit**: Nombre maximum de tickets à retourner (défaut: 20, max: 100)
    - **status**: Filtrer par statut (optionnel: "en cours", "fini")
    - **ticket_type**: Filtrer par type de ticket (optionnel)
    
    **Note:** En production, agent_id devrait être extrait du token JWT.
    """
)
def list_tickets_for_agent(
    agent_id: int = Query(..., description="ID de l'agent qui consulte les tickets", example=2),
    skip: int = Query(0, ge=0, description="Nombre de tickets à sauter (pagination)", example=0),
    limit: int = Query(20, ge=1, le=100, description="Nombre maximum de tickets à retourner (pagination)", example=20),
    status: TicketStatus | None = Query(None, description="Filtrer par statut (optionnel)", example=None),
    ticket_type: TicketType | None = Query(None, description="Filtrer par type de ticket (optionnel)", example=None),
    db: Session = Depends(get_db),
):
    """
    Liste paginée des tickets pour les agents.
    Seuls les agents (rôles commençant par "agt_") peuvent accéder à cet endpoint.
    """
    # Vérifier que l'utilisateur est un agent
    if not verify_agent(db, agent_id=agent_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only agents can access this endpoint. Your role must start with 'agt_'",
        )
    
    # Récupérer les tickets avec filtres optionnels
    tickets = ticket_crud.get_tickets_for_agent(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        ticket_type=ticket_type
    )
    
    return tickets


@router.get(
    "/agent/{ticket_id}",
    response_model=TicketResponse,
    summary="Détails d'un ticket pour les agents",
    description="""
    Permet aux agents de consulter les détails complets d'un ticket spécifique.
    
    **Paramètres:**
    - **ticket_id**: ID du ticket à consulter
    - **agent_id**: ID de l'agent (requis pour vérification)
    
    **Note:** En production, agent_id devrait être extrait du token JWT.
    """
)
def get_ticket_details_for_agent(
    ticket_id: int,
    agent_id: int = Query(..., description="ID de l'agent qui consulte le ticket", example=2),
    db: Session = Depends(get_db),
):
    """
    Récupère les détails complets d'un ticket pour un agent.
    Seuls les agents peuvent accéder à cet endpoint.
    """
    # Vérifier que l'utilisateur est un agent
    if not verify_agent(db, agent_id=agent_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only agents can access this endpoint. Your role must start with 'agt_'",
        )
    
    # Récupérer le ticket
    ticket = ticket_crud.get_ticket(db=db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    return ticket


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    """Récupère un ticket par son ID"""
    ticket = ticket_crud.get_ticket(db=db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    return ticket


@router.get("/reference/{reference_id}", response_model=TicketResponse)
def get_ticket_by_reference(
    reference_id: str,
    db: Session = Depends(get_db),
):
    """Récupère un ticket par son reference_id (ex: REF-2025-000123)"""
    ticket = ticket_crud.get_ticket_by_reference(db=db, reference_id=reference_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    return ticket


@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    db: Session = Depends(get_db),
):
    """
    Met à jour un ticket (pour les agents/admin).
    
    Note: En production, ajouter une vérification d'autorisation
    pour s'assurer que seul l'agent assigné ou un admin peut modifier.
    """
    ticket = ticket_crud.update_ticket(db=db, ticket_id=ticket_id, ticket_update=ticket_update)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    return ticket


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    """
    Supprime un ticket (pour les admins uniquement).
    
    Note: En production, ajouter une vérification d'autorisation.
    """
    deleted = ticket_crud.delete_ticket(db=db, ticket_id=ticket_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    return None


@router.post(
    "/{ticket_id}/feedback",
    response_model=TicketFeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Laisser un feedback sur un ticket",
    description="""
    Permet à un client de laisser un feedback après avoir reçu une réponse sur son ticket.
    
    **Conditions:**
    - Le client doit être le propriétaire du ticket
    - Le ticket doit avoir une réponse (agent assigné ou statut = fini)
    - Un seul feedback par ticket est autorisé
    
    **Paramètres:**
    - **is_satisfied**: true si satisfait, false sinon (requis)
    - **rating**: Note sur 5 (1-5, optionnel)
    - **reason**: Raison de l'insatisfaction (requis si is_satisfied = false)
    
    **Exemple de requête:**
    ```json
    {
        "is_satisfied": true,
        "rating": 5,
        "reason": null
    }
    ```
    """
)
def create_ticket_feedback(
    ticket_id: int,
    feedback_in: TicketFeedbackCreate,
    client_id: int = Query(..., description="ID du client qui laisse le feedback", example=1),
    db: Session = Depends(get_db),
):
    """
    Crée un feedback pour un ticket.
    Seul le propriétaire du ticket peut laisser un feedback.
    """
    # Vérifier que le ticket existe
    ticket = ticket_crud.get_ticket(db=db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    # Vérifier que le client est le propriétaire du ticket
    if ticket.client_id != client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only leave feedback on your own tickets",
        )
    
    # Vérifier que le ticket a une réponse (agent assigné ou statut fini)
    if not ticket.assigned_agent_id and ticket.status.value != "fini":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot leave feedback: ticket has no response yet. An agent must be assigned or ticket must be closed.",
        )
    
    # Vérifier que reason est fourni si is_satisfied = false
    if not feedback_in.is_satisfied and not feedback_in.reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reason is required when is_satisfied is false",
        )
    
    # Créer le feedback
    try:
        feedback = ticket_crud.create_ticket_feedback(
            db=db,
            ticket_id=ticket_id,
            feedback_in=feedback_in
        )
        return feedback
    except ValueError as e:
        error_msg = str(e)
        if "already exists" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Feedback already exists for this ticket. Use PUT to update it.",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )


@router.get(
    "/{ticket_id}/feedback",
    response_model=TicketFeedbackResponse,
    summary="Récupérer le feedback d'un ticket"
)
def get_ticket_feedback(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    """Récupère le feedback d'un ticket s'il existe"""
    feedback = ticket_crud.get_ticket_feedback(db=db, ticket_id=ticket_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No feedback found for this ticket",
        )
    return feedback


@router.put(
    "/{ticket_id}/feedback",
    response_model=TicketFeedbackResponse,
    summary="Mettre à jour le feedback d'un ticket"
)
def update_ticket_feedback(
    ticket_id: int,
    feedback_in: TicketFeedbackCreate,
    client_id: int = Query(..., description="ID du client qui met à jour le feedback", example=1),
    db: Session = Depends(get_db),
):
    """
    Met à jour le feedback d'un ticket.
    Seul le propriétaire du ticket peut modifier son feedback.
    """
    # Vérifier que le ticket existe
    ticket = ticket_crud.get_ticket(db=db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    # Vérifier que le client est le propriétaire du ticket
    if ticket.client_id != client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update feedback on your own tickets",
        )
    
    # Vérifier que reason est fourni si is_satisfied = false
    if not feedback_in.is_satisfied and not feedback_in.reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reason is required when is_satisfied is false",
        )
    
    # Mettre à jour le feedback
    feedback = ticket_crud.update_ticket_feedback(
        db=db,
        ticket_id=ticket_id,
        feedback_in=feedback_in
    )
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No feedback found for this ticket. Use POST to create it.",
        )
    
    return feedback


# ========== ENDPOINTS POUR RÉPONDRE AUX TICKETS ESCALADÉS ==========

@router.post(
    "/agent/{ticket_id}/respond",
    response_model=TicketResponse,
    status_code=status.HTTP_200_OK,
    summary="Répondre à un ticket escaladé par l'AI",
    description="""
    Permet à un agent de répondre à un ticket qui a été escaladé par l'AI.
    La réponse sera stockée et pourra être envoyée par email au client.
    
    **Conditions:**
    - L'utilisateur doit être un agent (rôle commence par "agt_")
    - Le ticket doit avoir été escaladé par l'AI (is_escalated = true)
    - Le ticket ne doit pas avoir déjà reçu de réponse
    
    **Paramètres:**
    - **subject**: Sujet de l'email de réponse (requis, 5-200 caractères)
    - **body**: Corps de l'email de réponse (requis, minimum 20 caractères)
    - **agent_id**: ID de l'agent qui répond (requis pour vérification)
    
    **Exemple de requête:**
    ```json
    {
        "subject": "Réponse à votre ticket REF-2025-000123",
        "body": "Bonjour,\n\nNous avons bien reçu votre demande concernant votre problème de connexion. Après investigation, nous avons identifié la cause du problème et l'avons résolu.\n\nVotre compte devrait maintenant fonctionner normalement. N'hésitez pas à nous contacter si vous rencontrez d'autres difficultés.\n\nCordialement,\nL'équipe support technique"
    }
    ```
    
    **Note:** En production, agent_id devrait être extrait du token JWT.
    """
)
def respond_to_escalated_ticket(
    ticket_id: int,
    response_in: AgentResponseCreate,
    agent_id: int = Query(..., description="ID de l'agent qui répond", example=2),
    db: Session = Depends(get_db),
):
    """
    Permet à un agent de répondre à un ticket escaladé par l'AI.
    La réponse sera stockée et pourra être envoyée par email au client.
    """
    # Vérifier que l'utilisateur est un agent
    if not verify_agent(db, agent_id=agent_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only agents can respond to escalated tickets. Your role must start with 'agt_'",
        )
    
    # Créer la réponse
    try:
        ticket = ticket_crud.create_agent_response(
            db=db,
            ticket_id=ticket_id,
            agent_id=agent_id,
            response_in=response_in
        )
        return ticket
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg,
            )
        elif "not been escalated" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )
        elif "already exists" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )


@router.get(
    "/agent/escalated",
    response_model=list[TicketResponse],
    summary="Liste des tickets escaladés par l'AI",
    description="""
    Permet aux agents de consulter la liste des tickets escaladés par l'AI.
    
    **Fonctionnalités:**
    - Pagination avec skip et limit
    - Filtrage par présence de réponse (optionnel)
    - Tri par date d'escalade (plus récent en premier)
    
    **Paramètres:**
    - **agent_id**: ID de l'agent (requis pour vérification)
    - **skip**: Nombre de tickets à sauter (défaut: 0)
    - **limit**: Nombre maximum de tickets à retourner (défaut: 20, max: 100)
    - **has_response**: Filtrer par présence de réponse (true = avec réponse, false = sans réponse, null = tous)
    
    **Note:** En production, agent_id devrait être extrait du token JWT.
    """
)
def list_escalated_tickets(
    agent_id: int = Query(..., description="ID de l'agent qui consulte les tickets", example=2),
    skip: int = Query(0, ge=0, description="Nombre de tickets à sauter (pagination)", example=0),
    limit: int = Query(20, ge=1, le=100, description="Nombre maximum de tickets à retourner (pagination)", example=20),
    has_response: bool | None = Query(None, description="Filtrer par présence de réponse (optionnel)", example=None),
    db: Session = Depends(get_db),
):
    """
    Liste paginée des tickets escaladés par l'AI.
    Seuls les agents peuvent accéder à cet endpoint.
    """
    # Vérifier que l'utilisateur est un agent
    if not verify_agent(db, agent_id=agent_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only agents can access this endpoint. Your role must start with 'agt_'",
        )
    
    # Récupérer les tickets escaladés
    tickets = ticket_crud.get_escalated_tickets(
        db=db,
        skip=skip,
        limit=limit,
        has_response=has_response
    )
    
    return tickets


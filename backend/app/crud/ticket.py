from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional

from app.models.ticket import Ticket, TicketType, TicketStatus, TicketFeedback
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketFeedbackCreate, AgentResponseCreate
from app.services.email_service import email_service


def generate_reference_id(db: Session) -> str:
    """
    Génère un ID de référence unique au format REF-YYYY-NNNNNN
    Exemple: REF-2025-000123
    """
    current_year = datetime.now().year
    
    # Trouver le dernier ticket de l'année
    last_ticket = (
        db.query(Ticket)
        .filter(Ticket.reference_id.like(f"REF-{current_year}-%"))
        .order_by(Ticket.reference_id.desc())
        .first()
    )
    
    if last_ticket and last_ticket.reference_id:
        # Extraire le numéro du dernier ticket
        try:
            last_number = int(last_ticket.reference_id.split("-")[-1])
            new_number = last_number + 1
        except (ValueError, IndexError):
            new_number = 1
    else:
        new_number = 1
    
    # Formater avec 6 chiffres (000001, 000002, etc.)
    reference_id = f"REF-{current_year}-{new_number:06d}"
    return reference_id


def create_ticket(db: Session, ticket_in: TicketCreate, client_id: int) -> Ticket:
    """
    Crée un nouveau ticket pour un client.
    
    Args:
        db: Session de base de données
        ticket_in: Données du ticket à créer
        client_id: ID du client qui crée le ticket
    
    Returns:
        Le ticket créé
    """
    # Générer un reference_id unique
    reference_id = generate_reference_id(db)
    
    # Créer le ticket
    db_ticket = Ticket(
        reference_id=reference_id,
        title=ticket_in.title,
        description=ticket_in.description,
        ticket_type=ticket_in.ticket_type,
        status=TicketStatus.EN_COURS,
        client_id=client_id,
        assigned_agent_id=None,  # Pas d'agent assigné au départ
        category=None,  # Sera détecté automatiquement plus tard
    )
    
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


def get_ticket(db: Session, ticket_id: int) -> Ticket | None:
    """Récupère un ticket par son ID"""
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def get_ticket_by_reference(db: Session, reference_id: str) -> Ticket | None:
    """Récupère un ticket par son reference_id"""
    return db.query(Ticket).filter(Ticket.reference_id == reference_id).first()


def get_tickets_by_client(db: Session, client_id: int, skip: int = 0, limit: int = 100) -> list[Ticket]:
    """Récupère tous les tickets d'un client"""
    return (
        db.query(Ticket)
        .filter(Ticket.client_id == client_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_all_tickets(db: Session, skip: int = 0, limit: int = 100) -> list[Ticket]:
    """Récupère tous les tickets (pour les agents/admin)"""
    return db.query(Ticket).offset(skip).limit(limit).all()


def get_tickets_for_agent(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    status: TicketStatus | None = None,
    ticket_type: TicketType | None = None
) -> list[Ticket]:
    """
    Récupère les tickets pour les agents avec filtres optionnels et tri par date.
    
    Args:
        db: Session de base de données
        skip: Nombre de tickets à sauter (pagination)
        limit: Nombre maximum de tickets à retourner
        status: Filtrer par statut (optionnel)
        ticket_type: Filtrer par type de ticket (optionnel)
    
    Returns:
        Liste des tickets triés par date de création (plus récent en premier)
    """
    query = db.query(Ticket)
    
    # Appliquer les filtres optionnels
    if status:
        query = query.filter(Ticket.status == status)
    
    if ticket_type:
        query = query.filter(Ticket.ticket_type == ticket_type)
    
    # Trier par date de création (plus récent en premier)
    query = query.order_by(Ticket.created_at.desc())
    
    # Appliquer la pagination
    tickets = query.offset(skip).limit(limit).all()
    
    return tickets


def update_ticket(db: Session, ticket_id: int, ticket_update: TicketUpdate) -> Ticket | None:
    """
    Met à jour un ticket (pour les agents/admin)
    """
    db_ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not db_ticket:
        return None
    
    # Mettre à jour uniquement les champs fournis
    update_data = ticket_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_ticket, field, value)
    
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


def delete_ticket(db: Session, ticket_id: int) -> bool:
    """Supprime un ticket"""
    db_ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not db_ticket:
        return False
    
    db.delete(db_ticket)
    db.commit()
    return True


def create_ticket_feedback(
    db: Session, 
    ticket_id: int, 
    feedback_in: TicketFeedbackCreate
) -> TicketFeedback:
    """
    Crée un feedback pour un ticket.
    
    Args:
        db: Session de base de données
        ticket_id: ID du ticket
        feedback_in: Données du feedback
    
    Returns:
        Le feedback créé
    """
    # Vérifier que le ticket existe
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise ValueError("Ticket not found")
    
    # Vérifier qu'il n'y a pas déjà un feedback pour ce ticket
    existing_feedback = db.query(TicketFeedback).filter(
        TicketFeedback.ticket_id == ticket_id
    ).first()
    if existing_feedback:
        raise ValueError("Feedback already exists for this ticket")
    
    # Créer le feedback
    db_feedback = TicketFeedback(
        ticket_id=ticket_id,
        is_satisfied=feedback_in.is_satisfied,
        rating=feedback_in.rating,
        reason=feedback_in.reason if not feedback_in.is_satisfied else None,
    )
    
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


def get_ticket_feedback(db: Session, ticket_id: int) -> TicketFeedback | None:
    """Récupère le feedback d'un ticket"""
    return db.query(TicketFeedback).filter(TicketFeedback.ticket_id == ticket_id).first()


def update_ticket_feedback(
    db: Session,
    ticket_id: int,
    feedback_in: TicketFeedbackCreate
) -> TicketFeedback | None:
    """
    Met à jour le feedback d'un ticket (si le client veut modifier son feedback)
    """
    db_feedback = db.query(TicketFeedback).filter(
        TicketFeedback.ticket_id == ticket_id
    ).first()
    
    if not db_feedback:
        return None
    
    # Mettre à jour les champs
    db_feedback.is_satisfied = feedback_in.is_satisfied
    db_feedback.rating = feedback_in.rating
    db_feedback.reason = feedback_in.reason if not feedback_in.is_satisfied else None
    
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


def create_agent_response(
    db: Session,
    ticket_id: int,
    agent_id: int,
    response_in: AgentResponseCreate
) -> dict:
    """
    Crée une réponse d'agent pour un ticket escaladé par l'AI et envoie un email au client.
    
    Args:
        db: Session de base de données
        ticket_id: ID du ticket
        agent_id: ID de l'agent qui répond
        response_in: Données de la réponse (sujet et corps de l'email)
    
    Returns:
        {
            "ticket": Ticket,
            "email_sent": bool,
            "email_status": dict
        }
    
    Raises:
        ValueError: Si le ticket n'existe pas, n'est pas escaladé, ou a déjà une réponse
    """
    # Vérifier que le ticket existe
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise ValueError("Ticket not found")
    
    # Vérifier que le ticket a été escaladé par l'AI
    if not ticket.is_escalated:
        raise ValueError("Ticket has not been escalated by AI. Only escalated tickets can receive agent responses.")
    
    # Vérifier qu'il n'y a pas déjà une réponse
    if ticket.agent_response:
        raise ValueError("Agent response already exists for this ticket")
    
    # Récupérer les informations du client
    client = ticket.client
    if not client or not client.email:
        raise ValueError("Client email not found")
    
    # Mettre à jour le ticket avec la réponse de l'agent
    ticket.agent_response = response_in.body
    ticket.agent_response_subject = response_in.subject
    ticket.agent_response_sent_at = datetime.now(timezone.utc)
    ticket.assigned_agent_id = agent_id  # Assigner l'agent au ticket
    
    db.commit()
    db.refresh(ticket)
    
    # Envoyer l'email au client
    email_status = email_service.send_agent_response_email(
        client_email=client.email,
        client_name=f"{client.prenom} {client.nom}",
        ticket_reference=ticket.reference_id,
        subject=response_in.subject,
        body=response_in.body
    )
    
    return {
        "ticket": ticket,
        "email_sent": email_status["success"],
        "email_status": email_status
    }


def get_escalated_tickets(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    has_response: bool | None = None
) -> list[Ticket]:
    """
    Récupère les tickets escaladés par l'AI.
    
    Args:
        db: Session de base de données
        skip: Nombre de tickets à sauter (pagination)
        limit: Nombre maximum de tickets à retourner
        has_response: Filtrer par présence de réponse (True = avec réponse, False = sans réponse, None = tous)
    
    Returns:
        Liste des tickets escaladés triés par date d'escalade (plus récent en premier)
    """
    query = db.query(Ticket).filter(Ticket.is_escalated == True)
    
    # Filtrer par présence de réponse
    if has_response is True:
        query = query.filter(Ticket.agent_response.isnot(None))
    elif has_response is False:
        query = query.filter(Ticket.agent_response.is_(None))
    
    # Trier par date d'escalade (plus récent en premier)
    query = query.order_by(Ticket.escalated_at.desc())
    
    # Appliquer la pagination
    tickets = query.offset(skip).limit(limit).all()
    
    return tickets


# ===== SATISFACTION ANALYTICS =====

def calculate_client_satisfaction_rate(db: Session) -> dict:
    """
    Calcule le taux de satisfaction des clients basé sur les ratings des feedbacks.
    
    Returns:
        {
            "average_rating": float,  # Moyenne des notes (1-5)
            "satisfaction_percentage": float,  # Pourcentage de clients satisfaits (rating >= 4)
            "total_feedbacks": int,  # Nombre total de feedbacks
            "satisfied_count": int,  # Nombre de clients satisfaits (rating >= 4)
            "dissatisfied_count": int,  # Nombre de clients insatisfaits
            "average_rating_formatted": str  # Format "4.5/5"
        }
    """
    from sqlalchemy import func
    
    total_feedbacks = db.query(TicketFeedback).count()
    
    if total_feedbacks == 0:
        return {
            "average_rating": 0,
            "satisfaction_percentage": 0,
            "total_feedbacks": 0,
            "satisfied_count": 0,
            "dissatisfied_count": 0,
            "average_rating_formatted": "N/A"
        }
    
    # Calculer la moyenne des ratings
    average_rating = db.query(func.avg(TicketFeedback.rating)).scalar() or 0
    average_rating = round(float(average_rating), 2)
    
    # Compter les clients satisfaits (rating >= 4)
    satisfied_count = db.query(TicketFeedback).filter(TicketFeedback.rating >= 4).count()
    dissatisfied_count = total_feedbacks - satisfied_count
    
    # Calculer le pourcentage de satisfaction
    satisfaction_percentage = round((satisfied_count / total_feedbacks * 100), 2) if total_feedbacks > 0 else 0
    
    return {
        "average_rating": average_rating,
        "satisfaction_percentage": satisfaction_percentage,
        "total_feedbacks": total_feedbacks,
        "satisfied_count": satisfied_count,
        "dissatisfied_count": dissatisfied_count,
        "average_rating_formatted": f"{average_rating}/5"
    }


def get_satisfaction_by_rating_distribution(db: Session) -> dict:
    """
    Obtient la distribution des feedbacks par note (1-5).
    
    Returns:
        {
            "1_star": int,
            "2_star": int,
            "3_star": int,
            "4_star": int,
            "5_star": int
        }
    """
    ratings = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    for rating in range(1, 6):
        count = db.query(TicketFeedback).filter(TicketFeedback.rating == rating).count()
        ratings[rating] = count
    
    return {
        "1_star": ratings[1],
        "2_star": ratings[2],
        "3_star": ratings[3],
        "4_star": ratings[4],
        "5_star": ratings[5]
    }


def get_recent_satisfaction_feedbacks(db: Session, limit: int = 10) -> list:
    """
    Obtient les feedbacks les plus récents pour visualiser la tendance de satisfaction.
    
    Args:
        limit: Nombre de feedbacks à retourner
    
    Returns:
        Liste des feedbacks récents avec détails
    """
    recent_feedbacks = db.query(TicketFeedback).order_by(
        TicketFeedback.id.desc()
    ).limit(limit).all()
    
    return [
        {
            "feedback_id": fb.id,
            "ticket_id": fb.ticket_id,
            "rating": fb.rating,
            "is_satisfied": fb.is_satisfied,
            "reason": fb.reason
        }
        for fb in recent_feedbacks
    ]


def get_satisfaction_dashboard(db: Session) -> dict:
    """
    Obtient le dashboard complet de satisfaction pour le panel admin.
    
    Returns:
        {
            "overall_metrics": dict,  # Métriques globales
            "rating_distribution": dict,  # Distribution par note
            "recent_feedbacks": list  # Feedbacks récents
        }
    """
    overall_metrics = calculate_client_satisfaction_rate(db)
    rating_distribution = get_satisfaction_by_rating_distribution(db)
    recent_feedbacks = get_recent_satisfaction_feedbacks(db, limit=10)
    
    return {
        "overall_metrics": overall_metrics,
        "rating_distribution": rating_distribution,
        "recent_feedbacks": recent_feedbacks
    }


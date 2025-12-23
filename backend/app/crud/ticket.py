from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from typing import Optional
import json

from app.models.ticket import Ticket, TicketType, TicketStatus, TicketFeedback, AIPipelineLog
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
    
    # Appliquer la pagination
    tickets = query.offset(skip).limit(limit).all()
    
    return tickets


def create_ai_pipeline_log(db: Session, ticket_id: int, trace_id: str) -> AIPipelineLog:
    """Crée un nouveau log de pipeline AI"""
    log = AIPipelineLog(
        ticket_id=ticket_id,
        trace_id=trace_id,
        status="processing"
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def update_ai_pipeline_log_with_results(
    db: Session, 
    log_id: int, 
    ai_results: dict,
    processing_time: float | None = None,
    error_message: str | None = None
) -> AIPipelineLog | None:
    """Met à jour un log de pipeline AI avec les résultats"""
    log = db.query(AIPipelineLog).filter(AIPipelineLog.id == log_id).first()
    if not log:
        return None
    
    if error_message:
        log.status = "failed"
        log.error_message = error_message
    else:
        log.status = "completed"
    
    log.completed_at = datetime.now(timezone.utc)
    log.processing_time_seconds = processing_time
    
    if "analysis" in ai_results:
        analysis = ai_results["analysis"]
        log.summary = analysis.get("summary")
        log.keywords = json.dumps(analysis.get("keywords", []))
        log.category = analysis.get("category")
    
    if "rag_result" in ai_results:
        rag = ai_results["rag_result"]
        docs_info = [
            {
                "title": doc.get("title", ""),
                "score": doc.get("score", 0.0),
                "content_preview": doc.get("content", "")[:200] + "..." if doc.get("content") else ""
            }
            for doc in rag.get("used_documents", [])
        ]
        log.rag_docs = json.dumps(docs_info)
        log.proposed_answer = rag.get("answer")
    
    if "evaluation" in ai_results:
        eval_data = ai_results["evaluation"]
        log.confidence_score = eval_data.get("confidence")
        log.sentiment = eval_data.get("sentiment")
        log.sensitive_data_detected = eval_data.get("sensitive_data", False)
    
    if "status" in ai_results:
        if ai_results["status"] == "escalated":
            log.escalation_reason = ai_results.get("reason", "Unknown")
        elif ai_results["status"] == "success":
            log.final_response = ai_results.get("final_response")
    
    db.commit()
    db.refresh(log)
    return log


def update_ticket_with_ai_results(db: Session, ticket_id: int, ai_results: dict) -> Ticket | None:
    """Met à jour le ticket avec les résultats de l'IA (catégorie, escalade)"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        return None
    
    if "analysis" in ai_results:
        ticket.category = ai_results["analysis"].get("category")
        ticket.summary = ai_results["analysis"].get("summary")
    
    if ai_results.get("status") == "escalated":
        ticket.is_escalated = True
        ticket.escalated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(ticket)
    return ticket


def get_ai_pipeline_logs_by_ticket(db: Session, ticket_id: int) -> list[AIPipelineLog]:
    """Récupère tous les logs de pipeline AI pour un ticket"""
    return db.query(AIPipelineLog).filter(AIPipelineLog.ticket_id == ticket_id).order_by(AIPipelineLog.started_at.desc()).all()


def get_latest_ai_pipeline_log(db: Session, ticket_id: int) -> AIPipelineLog | None:
    """Récupère le dernier log de pipeline AI pour un ticket"""
    return db.query(AIPipelineLog).filter(AIPipelineLog.ticket_id == ticket_id).order_by(AIPipelineLog.started_at.desc()).first()


def calculate_client_satisfaction_rate(db: Session) -> float:
    """Calcule le taux de satisfaction global (is_satisfied == True)"""
    total = db.query(TicketFeedback).count()
    if total == 0:
        return 0.0
    satisfied = db.query(TicketFeedback).filter(TicketFeedback.is_satisfied == True).count()
    return (satisfied / total) * 100


def get_satisfaction_by_rating_distribution(db: Session) -> dict:
    """Retourne la distribution des notes (1-5)"""
    distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    results = db.query(TicketFeedback.rating, func.count(TicketFeedback.id)).group_by(TicketFeedback.rating).all()
    for rating, count in results:
        if rating in distribution:
            distribution[rating] = count
    return distribution


def get_recent_satisfaction_feedbacks(db: Session, limit: int = 10) -> list[TicketFeedback]:
    """Récupère les derniers feedbacks reçus"""
    return db.query(TicketFeedback).order_by(TicketFeedback.id.desc()).limit(limit).all()


def get_satisfaction_dashboard(db: Session) -> dict:
    """Retourne un résumé complet pour le dashboard admin"""
    
    total_feedback = db.query(TicketFeedback).count()
    avg_rating = db.query(func.avg(TicketFeedback.rating)).scalar() or 0.0
    satisfaction_rate = calculate_client_satisfaction_rate(db)
    
    return {
        "total_feedback": total_feedback,
        "average_rating": round(float(avg_rating), 2),
        "satisfaction_rate": round(satisfaction_rate, 2),
        "rating_distribution": get_satisfaction_by_rating_distribution(db),
        "recent_feedbacks": get_recent_satisfaction_feedbacks(db)
    }


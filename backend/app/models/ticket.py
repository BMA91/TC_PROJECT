import enum


from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


from app.database import Base




class TicketType(str, enum.Enum):
    legal = "Legal, Regulatory, and Commercial Frameworks"
    support = "Support and Reference Documentation"
    ops = "Operational and Practical User Guides"
    OTHER = "other"




class TicketStatus(str, enum.Enum):
    EN_COURS = "en cours"
    FINI = "fini"
 




class Ticket(Base):
    __tablename__ = "tickets"


    id = Column(Integer, primary_key=True, index=True)
    # Custom ID format: REF-2025-000123 as requested in Bonus
    reference_id = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)  # As requested
    description = Column(Text, nullable=False)  # As requested
    ticket_type = Column(Enum(TicketType), nullable=False)  # As requested
    status = Column(Enum(TicketStatus), default=TicketStatus.EN_COURS)
    category = Column(String, nullable=True)  # Auto-detection
    summary = Column(String, nullable=True)  # Auto-detection
    
    # AI Escalation fields
    is_escalated = Column(Boolean, default=False, nullable=False)  # Indique si le ticket a été escaladé par l'AI
    escalated_at = Column(DateTime(timezone=True), nullable=True)  # Date d'escalade
    
    # Agent response fields
    agent_response = Column(Text, nullable=True)  # Réponse de l'agent (contenu de l'email)
    agent_response_subject = Column(String, nullable=True)  # Sujet de l'email de réponse
    agent_response_sent_at = Column(DateTime(timezone=True), nullable=True)  # Date d'envoi de la réponse

    client_id = Column(Integer, ForeignKey("users.id"))
    assigned_agent_id = Column(Integer, ForeignKey("users.id"), nullable=True)


    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


    # Relationships
    client = relationship("User", foreign_keys=[client_id], back_populates="tickets")
    pipeline_logs = relationship("AIPipelineLog", back_populates="ticket")
    feedback = relationship("TicketFeedback", back_populates="ticket", uselist=False)




class TicketFeedback(Base):
    """Tracks Volet 2 & 4: Satisfaction metrics"""
    __tablename__ = "ticket_feedback"


    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    is_satisfied = Column(Boolean, nullable=False)
    reason = Column(Text, nullable=True)  # Reason for dissatisfaction
    rating = Column(Integer, nullable=True)
    ticket = relationship("Ticket", back_populates="feedback")




class AIPipelineLog(Base):
    """Tracks AI processing pipeline results and logs"""
    __tablename__ = "ai_pipeline_logs"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False, index=True)
    trace_id = Column(String, nullable=False, index=True)  # For tracking requests across logs

    # Processing status
    status = Column(String, nullable=False)  # 'processing', 'completed', 'failed', 'timeout'
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # AI Results storage
    summary = Column(String, nullable=True)  # From query analyser
    keywords = Column(Text, nullable=True)  # JSON array of keywords
    category = Column(String, nullable=True)  # Auto-detected category

    # RAG results
    rag_docs = Column(Text, nullable=True)  # JSON array of retrieved documents with scores
    proposed_answer = Column(Text, nullable=True)  # AI-generated answer before evaluation

    # Evaluation results
    confidence_score = Column(Float, nullable=True)  # 0.0 to 1.0
    sentiment = Column(String, nullable=True)  # 'positive', 'negative', 'neutral', 'angry'
    sensitive_data_detected = Column(Boolean, default=False)
    escalation_reason = Column(String, nullable=True)  # Why it was escalated

    # Final response (if AI handled it)
    final_response = Column(Text, nullable=True)

    # Processing metadata
    processing_time_seconds = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    ticket = relationship("Ticket", back_populates="pipeline_logs")

    __table_args__ = (
        # Composite index for efficient queries
        {"schema": None}
    )














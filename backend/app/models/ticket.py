import enum


from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, Enum
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


    client_id = Column(Integer, ForeignKey("users.id"))
    assigned_agent_id = Column(Integer, ForeignKey("users.id"), nullable=True)


    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


    # Relationships
    client = relationship("User", foreign_keys=[client_id], back_populates="tickets")
    # pipeline_logs = relationship("AIPipelineLog", back_populates="ticket")  # Commented out - AIPipelineLog model not yet created
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









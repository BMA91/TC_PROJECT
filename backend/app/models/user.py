from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    nom = Column(String, nullable=False)
    password = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    telephone = Column(String, nullable=False)
    role = Column(String, nullable=False)  # client_1 | client_2 | client_3 (randomly assigned if not provided)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc)) 


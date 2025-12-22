from enum import Enum
from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    CLIENT_1 = "client_1"
    CLIENT_2 = "client_2"
    CLIENT_3 = "client_3"


class AgentRole(str, Enum):
    AGT_TECH = "agt_tech"
    AGT_SALES = "agt_sales"


class UserCreate(BaseModel):
    nom: str
    prenom: str
    telephone: str
    password: str
    email: EmailStr
    # Note: role is NOT in the schema - it's automatically assigned in the database


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class AgentCreate(BaseModel):
    """Schema for admin to create agents"""
    nom: str
    prenom: str
    telephone: str
    password: str
    email: EmailStr
    role: AgentRole  # Admin chooses: agt_tech or agt_sales


class UserResponse(BaseModel):
    id: int
    nom: str
    prenom: str
    telephone: str
    email: EmailStr
    role: str  # Visible in response to show what was assigned

    class Config:
        from_attributes = True

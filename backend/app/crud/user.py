import random
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserRole, AgentCreate


def _get_random_client_role() -> str:
    """Returns a random client role (client_1, client_2, or client_3)."""
    return random.choice([
        UserRole.CLIENT_1.value,
        UserRole.CLIENT_2.value,
        UserRole.CLIENT_3.value
    ])


def create_user(db: Session, user_in: UserCreate) -> User:
    """
    Create a user with automatic role assignment.
    Role is randomly assigned from client_1, client_2, or client_3.
    """
    # Automatically assign a random client role
    role = _get_random_client_role()
    
    db_user = User(
        nom=user_in.nom,
        prenom=user_in.prenom,
        telephone=user_in.telephone,
        password=user_in.password,
        email=user_in.email,
        role=role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def verify_user_credentials(db: Session, email: str, password: str) -> User | None:
    """
    Verify user credentials by email and password.
    Returns the user if credentials are valid, None otherwise.
    """
    user = db.query(User).filter(User.email == email).first()
    if user and user.password == password:
        return user
    return None


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()


def get_users_by_role_pattern(db: Session, role_pattern: str, skip: int = 0, limit: int = 100) -> list[User]:
    """
    Get users whose role matches the given pattern (SQL LIKE pattern).
    Example: role_pattern="agt_%" matches roles starting with "agt_"
    """
    return db.query(User).filter(User.role.like(role_pattern)).offset(skip).limit(limit).all()


def delete_user(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True


def create_agent(db: Session, agent_in: AgentCreate, role: str) -> User:
    """
    Create an agent with a specific role (agt_tech or agt_sales).
    This is used by admin to create agents.
    """
    db_agent = User(
        nom=agent_in.nom,
        prenom=agent_in.prenom,
        telephone=agent_in.telephone,
        password=agent_in.password,
        email=agent_in.email,
        role=role,
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


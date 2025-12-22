from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud import user as user_crud
from app.dependencies import get_db
from app.schemas.user import AgentCreate, UserResponse

router = APIRouter(prefix="/admin", tags=["admin"])


def verify_admin(db: Session, admin_email: str) -> bool:
    """
    Verify if a user is an admin.
    For now, this is a simple check. In production, use proper authentication.
    TODO: Implement proper JWT/auth token verification
    """
    admin = user_crud.get_user_by_email(db, email=admin_email)
    if admin and admin.role == "admin":
        return True
    return False


@router.post(
    "/agents",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_agent(
    agent_in: AgentCreate,
    admin_email: str = Query(..., description="Email of the admin creating the agent"),
    db: Session = Depends(get_db),
):
    """
    Admin endpoint to create agents.
    Admin can choose between agt_tech or agt_sales roles.
    
    Query Parameters:
    - admin_email: Email of the admin creating the agent (required for testing)
    
    Request Body:
    - nom, prenom, telephone, password, email, role (agt_tech or agt_sales)
    
    Note: In production, this should use JWT token authentication instead of admin_email.
    """
    # Verify admin
    if not verify_admin(db, admin_email=admin_email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create agents",
        )
    
    # Check if email already exists
    existing = user_crud.get_user_by_email(db, email=agent_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create agent with the specified role
    agent = user_crud.create_agent(
        db=db,
        agent_in=agent_in,
        role=agent_in.role.value
    )
    
    return agent


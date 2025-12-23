from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud import user as user_crud
from app.crud.ticket import (
    calculate_client_satisfaction_rate,
    get_satisfaction_by_rating_distribution,
    get_recent_satisfaction_feedbacks,
    get_satisfaction_dashboard
)
from app.dependencies import get_db, get_current_user
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


# ===== CLIENT SATISFACTION ANALYTICS =====

@router.get(
    "/satisfaction/metrics",
    status_code=status.HTTP_200_OK,
)
def get_satisfaction_metrics(
    admin_email: str = Query(..., description="Email of the admin"),
    db: Session = Depends(get_db),
):
    """
    Get client satisfaction metrics based on feedback ratings.
    
    Returns:
    - average_rating: Moyenne des notes (1-5)
    - satisfaction_percentage: Pourcentage de clients satisfaits (rating >= 4)
    - total_feedbacks: Nombre total de feedbacks
    - satisfied_count: Nombre de clients satisfaits
    - dissatisfied_count: Nombre de clients insatisfaits
    
    Query Parameters:
    - admin_email: Email of the admin (for verification)
    """
    # Verify admin
    if not verify_admin(db, admin_email=admin_email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access satisfaction metrics",
        )
    
    metrics = calculate_client_satisfaction_rate(db)
    return metrics


@router.get(
    "/satisfaction/distribution",
    status_code=status.HTTP_200_OK,
)
def get_satisfaction_distribution(
    admin_email: str = Query(..., description="Email of the admin"),
    db: Session = Depends(get_db),
):
    """
    Get distribution of satisfaction ratings by stars (1-5).
    Useful for dashboard visualization.
    
    Returns:
    {
        "1_star": count,
        "2_star": count,
        "3_star": count,
        "4_star": count,
        "5_star": count
    }
    
    Query Parameters:
    - admin_email: Email of the admin (for verification)
    """
    # Verify admin
    if not verify_admin(db, admin_email=admin_email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access satisfaction data",
        )
    
    distribution = get_satisfaction_by_rating_distribution(db)
    return distribution


@router.get(
    "/satisfaction/recent-feedbacks",
    status_code=status.HTTP_200_OK,
)
def get_recent_feedbacks(
    limit: int = Query(10, description="Number of recent feedbacks to return"),
    admin_email: str = Query(..., description="Email of the admin"),
    db: Session = Depends(get_db),
):
    """
    Get recent client satisfaction feedbacks.
    
    Query Parameters:
    - limit: Number of feedbacks to return (default: 10)
    - admin_email: Email of the admin (for verification)
    """
    # Verify admin
    if not verify_admin(db, admin_email=admin_email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access satisfaction data",
        )
    
    feedbacks = get_recent_satisfaction_feedbacks(db, limit=limit)
    return {
        "recent_count": len(feedbacks),
        "feedbacks": feedbacks
    }


@router.get(
    "/satisfaction/dashboard",
    status_code=status.HTTP_200_OK,
)
def get_satisfaction_dashboard_data(
    admin_email: str = Query(..., description="Email of the admin"),
    db: Session = Depends(get_db),
):
    """
    Get complete satisfaction dashboard with all metrics.
    
    Returns:
    - overall_metrics: Métriques principales (moyenne, pourcentage, etc)
    - rating_distribution: Distribution par nombre d'étoiles
    - recent_feedbacks: Les 10 derniers feedbacks
    
    Query Parameters:
    - admin_email: Email of the admin (for verification)
    """
    # Verify admin
    if not verify_admin(db, admin_email=admin_email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access the satisfaction dashboard",
        )
    
    dashboard = get_satisfaction_dashboard(db)
    return dashboard


from pydantic import BaseModel, Field


class AISatisfactionMetrics(BaseModel):
    """
    AI Satisfaction metrics based on feedback ratings.
    Displayed in the admin dashboard.
    """
    average_rating: float = Field(
        ...,
        description="Average rating from all feedbacks (1-5)",
        example=4.5
    )
    satisfaction_percentage: float = Field(
        ...,
        description="Percentage of satisfied users (%)",
        example=85.5
    )
    total_feedbacks: int = Field(
        ...,
        description="Total number of feedbacks received",
        example=50
    )
    satisfied_count: int = Field(
        ...,
        description="Number of satisfied users",
        example=42
    )
    dissatisfied_count: int = Field(
        ...,
        description="Number of dissatisfied users",
        example=8
    )
    average_rating_formatted: str = Field(
        ...,
        description="Formatted average rating",
        example="4.5/5"
    )


class RatingBreakdown(BaseModel):
    """Breakdown of ratings by stars"""
    one_star: int = Field(..., alias="1_star", description="Count of 1-star ratings", example=2)
    two_star: int = Field(..., alias="2_star", description="Count of 2-star ratings", example=3)
    three_star: int = Field(..., alias="3_star", description="Count of 3-star ratings", example=5)
    four_star: int = Field(..., alias="4_star", description="Count of 4-star ratings", example=20)
    five_star: int = Field(..., alias="5_star", description="Count of 5-star ratings", example=20)

    class Config:
        populate_by_name = True


class AdminDashboardMetrics(BaseModel):
    """Complete admin dashboard metrics"""
    satisfaction_metrics: AISatisfactionMetrics = Field(
        ...,
        description="AI satisfaction metrics"
    )
    rating_breakdown: dict = Field(
        ...,
        description="Breakdown by rating stars"
    )
    recent_feedbacks: list = Field(
        ...,
        description="Last 10 feedbacks"
    )

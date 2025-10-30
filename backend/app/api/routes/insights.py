"""
Insights API endpoints
Provides automatic insights generation from analytics data
"""
from fastapi import APIRouter, Depends, Query
from datetime import date
from typing import Optional

from app.core.database import get_db, Database
from app.models.schemas import InsightsResponse
from app.services.insights import InsightsEngine


router = APIRouter()


@router.get(
    "/automatic",
    response_model=InsightsResponse,
    summary="Generate automatic insights",
    description="""
    Automatically detect insights from sales data including:
    - Performance issues (high cancellation rates, delivery problems)
    - Revenue opportunities (underperforming products, idle capacity)
    - Customer behavior patterns (churn risk, buying patterns)
    
    Returns prioritized insights with actionable recommendations.
    """
)
async def get_automatic_insights(
    start_date: date = Query(..., description="Start date for analysis period"),
    end_date: date = Query(..., description="End date for analysis period"),
    brand_id: int = Query(..., description="Brand ID to analyze"),
    store_ids: Optional[str] = Query(None, description="Comma-separated store IDs to filter"),
    limit: int = Query(5, ge=1, le=20, description="Maximum number of insights to return"),
    db: Database = Depends(get_db)
) -> InsightsResponse:
    """
    Generate automatic insights for the specified period and brand.
    
    **Example:**
    ```
    GET /api/v1/analytics/insights/automatic?start_date=2025-05-01&end_date=2025-05-31&brand_id=1&limit=5
    ```
    
    **Response:**
    Returns a list of insights ordered by priority and impact, each containing:
    - Clear title and description
    - Financial impact measurement
    - Affected context (stores, channels, days, hours)
    - Actionable recommendation with estimated ROI
    - Link to relevant dashboard section
    """
    # Parse store IDs if provided
    store_ids_list = None
    if store_ids:
        try:
            store_ids_list = [int(sid.strip()) for sid in store_ids.split(",") if sid.strip()]
        except ValueError:
            pass  # Ignore invalid store IDs
    
    # Create insights engine
    engine = InsightsEngine(db)
    
    # Generate insights
    insights_response = await engine.generate_insights(
        brand_id=brand_id,
        start_date=start_date,
        end_date=end_date,
        store_ids=store_ids_list,
        limit=limit
    )
    
    return insights_response


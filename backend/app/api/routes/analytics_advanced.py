"""
Advanced Analytics API Routes - Delivery, Customer RFM, Contextual Analysis
"""
from fastapi import APIRouter, Depends, Query
from datetime import date
from typing import Optional

from app.core.database import get_db, Database
from app.services.analytics_advanced import AdvancedAnalyticsEngine
from app.models.schemas import (
    DeliveryPerformanceResponse,
    CustomerRFMResponse,
    ChurnRiskResponse,
    ProductByContextResponse,
    SalesHeatmapResponse,
)

router = APIRouter()


def get_advanced_engine(db: Database = Depends(get_db)) -> AdvancedAnalyticsEngine:
    """Dependency for Advanced Analytics Engine"""
    return AdvancedAnalyticsEngine(db)


# ============================================================================
# DELIVERY ANALYTICS - "Meu tempo de entrega piorou. Em quais regiões?"
# ============================================================================

@router.get("/delivery/performance", response_model=DeliveryPerformanceResponse)
async def get_delivery_performance(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    brand_id: Optional[int] = Query(None, description="Brand ID to filter by owner"),
    store_ids: Optional[str] = Query(None, description="Comma-separated store IDs"),
    engine: AdvancedAnalyticsEngine = Depends(get_advanced_engine)
):
    """
    Get delivery performance metrics
    
    Answers: "Meu tempo de entrega piorou. Em quais regiões?"
    
    Returns:
    - Overall delivery metrics (avg time, on-time rate)
    - Performance by region (city/state)
    - Trend over time
    """
    store_ids_list = [int(x) for x in store_ids.split(",")] if store_ids else None
    
    overall, by_region, trend = await engine.get_delivery_performance(
        start_date=start_date,
        end_date=end_date,
        brand_id=brand_id,
        store_ids=store_ids_list
    )
    
    return DeliveryPerformanceResponse(
        overall=overall,
        by_region=by_region,
        trend=trend,
        period={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    )


# ============================================================================
# CUSTOMER RFM - "Quais clientes compraram 3+ vezes mas não voltam há 30 dias?"
# ============================================================================

@router.get("/customers/rfm", response_model=CustomerRFMResponse)
async def get_customer_rfm(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    brand_id: Optional[int] = Query(None, description="Brand ID to filter by owner"),
    reference_date: Optional[date] = Query(None, description="Reference date for recency calculation"),
    engine: AdvancedAnalyticsEngine = Depends(get_advanced_engine)
):
    """
    Get RFM (Recency, Frequency, Monetary) analysis for customers
    
    Segments:
    - VIP: Recent, frequent, high-value
    - Regular: Consistent buyers
    - At Risk: Haven't returned in 30+ days
    - Inactive: Haven't returned in 60+ days
    """
    customers = await engine.get_customer_rfm(
        start_date=start_date,
        end_date=end_date,
        brand_id=brand_id,
        reference_date=reference_date
    )
    
    # Count by segment
    segments = {}
    for customer in customers:
        segment = customer.rfm_segment
        segments[segment] = segments.get(segment, 0) + 1
    
    return CustomerRFMResponse(
        customers=customers,
        total_customers=len(customers),
        segments=segments,
        period={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    )


@router.get("/customers/churn-risk", response_model=ChurnRiskResponse)
async def get_churn_risk_customers(
    min_purchases: int = Query(3, ge=1, description="Minimum number of purchases"),
    days_inactive: int = Query(30, ge=1, description="Days since last purchase"),
    brand_id: Optional[int] = Query(None, description="Brand ID to filter by owner"),
    store_ids: Optional[str] = Query(None, description="Comma-separated store IDs"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of customers"),
    engine: AdvancedAnalyticsEngine = Depends(get_advanced_engine)
):
    """
    Get customers at risk of churning
    
    Answers: "Quais clientes compraram 3+ vezes mas não voltam há 30 dias?"
    
    Returns customers who:
    - Made X or more purchases
    - Haven't returned in Y days
    - Their favorite channel and product
    - Can be filtered by specific stores
    """
    # Parse store_ids from comma-separated string
    store_id_list = None
    if store_ids:
        store_id_list = [int(sid.strip()) for sid in store_ids.split(",") if sid.strip()]
    
    customers = await engine.get_churn_risk_customers(
        min_purchases=min_purchases,
        days_inactive=days_inactive,
        brand_id=brand_id,
        store_ids=store_id_list,
        limit=limit
    )
    
    return ChurnRiskResponse(
        customers=customers,
        total_at_risk=len(customers),
        criteria={
            "min_purchases": min_purchases,
            "days_inactive": days_inactive
        },
        period={
            "analysis_date": "current"
        }
    )


# ============================================================================
# CONTEXTUAL PRODUCTS - "Qual produto vende mais na quinta à noite no iFood?"
# ============================================================================

@router.get("/products/by-context", response_model=ProductByContextResponse)
async def get_products_by_context(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    brand_id: Optional[int] = Query(None, description="Brand ID to filter by owner"),
    weekday: Optional[int] = Query(None, ge=0, le=6, description="Weekday (0=Monday, 6=Sunday)"),
    hour_start: Optional[int] = Query(None, ge=0, le=23, description="Start hour (0-23)"),
    hour_end: Optional[int] = Query(None, ge=0, le=23, description="End hour (0-23)"),
    channel_id: Optional[int] = Query(None, description="Channel ID"),
    store_ids: Optional[str] = Query(None, description="Comma-separated store IDs"),
    limit: int = Query(20, ge=1, le=100, description="Number of products"),
    engine: AdvancedAnalyticsEngine = Depends(get_advanced_engine)
):
    """
    Get top products by specific context
    
    Answers: "Qual produto vende mais na quinta à noite no iFood?"
    
    Filters:
    - Weekday: 0=Monday, 3=Thursday, 6=Sunday
    - Hour range: e.g., 19-23 for night (7 PM - 11 PM)
    - Channel: iFood, Rappi, etc.
    """
    store_ids_list = [int(x) for x in store_ids.split(",")] if store_ids else None
    
    products = await engine.get_products_by_context(
        start_date=start_date,
        end_date=end_date,
        brand_id=brand_id,
        weekday=weekday,
        hour_start=hour_start,
        hour_end=hour_end,
        channel_id=channel_id,
        store_ids=store_ids_list,
        limit=limit
    )
    
    context = {}
    if weekday is not None:
        weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        context['weekday'] = weekday_names[weekday]
    if hour_start is not None and hour_end is not None:
        context['hour_range'] = f"{hour_start:02d}:00-{hour_end:02d}:00"
    if channel_id is not None:
        context['channel_id'] = channel_id
    
    return ProductByContextResponse(
        products=products,
        total_products=len(products),
        context=context,
        period={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    )


# ============================================================================
# SALES HEATMAP
# ============================================================================

@router.get("/sales/heatmap", response_model=SalesHeatmapResponse)
async def get_sales_heatmap(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    brand_id: Optional[int] = Query(None, description="Brand ID to filter by owner"),
    store_ids: Optional[str] = Query(None, description="Comma-separated store IDs"),
    channel_ids: Optional[str] = Query(None, description="Comma-separated channel IDs"),
    engine: AdvancedAnalyticsEngine = Depends(get_advanced_engine)
):
    """
    Get sales heatmap (weekday x hour)
    
    Useful for identifying:
    - Peak hours by day
    - Best days of the week
    - Slow periods
    """
    store_ids_list = [int(x) for x in store_ids.split(",")] if store_ids else None
    channel_ids_list = [int(x) for x in channel_ids.split(",")] if channel_ids else None
    
    heatmap = await engine.get_sales_heatmap(
        start_date=start_date,
        end_date=end_date,
        brand_id=brand_id,
        store_ids=store_ids_list,
        channel_ids=channel_ids_list
    )
    
    return SalesHeatmapResponse(
        heatmap=heatmap,
        period={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    )


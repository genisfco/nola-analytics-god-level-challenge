"""
Analytics API Routes
"""
from fastapi import APIRouter, Depends, Query
from datetime import date, timedelta
from typing import Optional

from app.core.database import get_db, Database
from app.services.analytics_engine import AnalyticsEngine
from app.models.schemas import (
    OverviewResponse,
    ProductsResponse,
    ChannelsResponse,
    StoresResponse,
    SalesTrendResponse,
    HourlyDistributionResponse,
    WeekdayDistributionResponse,
    CategoriesResponse,
    BrandsListResponse,
    StoresListResponse,
    Brand,
    Store,
)

router = APIRouter()


def get_analytics_engine(db: Database = Depends(get_db)) -> AnalyticsEngine:
    """Dependency for Analytics Engine"""
    return AnalyticsEngine(db)


# ============================================================================
# BRANDS & STORES ENDPOINTS
# ============================================================================

@router.get("/brands/list", response_model=BrandsListResponse)
async def get_brands_list(db: Database = Depends(get_db)):
    """
    Get list of all brands (owners/proprietários)
    
    Returns:
    - List of brands with id and name
    - Total count
    
    This endpoint is used for brand selection in the frontend
    """
    query = """
        SELECT id, name 
        FROM brands 
        ORDER BY name
    """
    
    result = await db.fetch_all(query)
    
    brands = [Brand(id=row["id"], name=row["name"]) for row in result]
    
    return BrandsListResponse(
        brands=brands,
        total=len(brands)
    )


@router.get("/stores/list", response_model=StoresListResponse)
async def get_stores_list(
    brand_id: int = Query(..., description="Brand ID to filter stores"),
    db: Database = Depends(get_db)
):
    """
    Get list of stores for a specific brand
    
    Parameters:
    - brand_id: Filter stores by brand (owner)
    
    Returns:
    - List of stores with basic information
    - Only active stores are returned
    
    This endpoint is used for store filter selection in the frontend
    """
    query = """
        SELECT id, name, city, state, is_active
        FROM stores
        WHERE brand_id = $1 AND is_active = true
        ORDER BY name
    """
    
    result = await db.fetch_all(query, brand_id)
    
    stores = [
        Store(
            id=row["id"],
            name=row["name"],
            city=row["city"],
            state=row["state"],
            is_active=row["is_active"]
        )
        for row in result
    ]
    
    return StoresListResponse(
        stores=stores,
        total=len(stores),
        brand_id=brand_id
    )


# ============================================================================
# OVERVIEW ENDPOINT
# ============================================================================

@router.get("/overview", response_model=OverviewResponse)
async def get_overview(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    brand_id: Optional[int] = Query(None, description="Brand ID to filter by owner"),
    store_ids: Optional[str] = Query(None, description="Comma-separated store IDs"),
    channel_ids: Optional[str] = Query(None, description="Comma-separated channel IDs"),
    engine: AnalyticsEngine = Depends(get_analytics_engine)
):
    """
    Get overview metrics (KPIs) for the specified period
    
    Returns:
    - Total sales count
    - Total revenue
    - Average ticket
    - Completed/cancelled sales
    - Cancellation rate
    - Total unique customers
    """
    # Parse comma-separated IDs
    store_ids_list = [int(x) for x in store_ids.split(",")] if store_ids else None
    channel_ids_list = [int(x) for x in channel_ids.split(",")] if channel_ids else None
    
    metrics = await engine.get_overview_metrics(
        start_date=start_date,
        end_date=end_date,
        brand_id=brand_id,
        store_ids=store_ids_list,
        channel_ids=channel_ids_list
    )
    
    days_diff = (end_date - start_date).days + 1
    
    return OverviewResponse(
        metrics=metrics,
        period={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days_diff
        }
    )


# ============================================================================
# PRODUCTS ENDPOINTS
# ============================================================================

@router.get("/products/top", response_model=ProductsResponse)
async def get_top_products(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    limit: int = Query(20, ge=1, le=100, description="Number of products to return"),
    brand_id: Optional[int] = Query(None, description="Brand ID to filter by owner"),
    store_ids: Optional[str] = Query(None, description="Comma-separated store IDs"),
    channel_ids: Optional[str] = Query(None, description="Comma-separated channel IDs"),
    engine: AnalyticsEngine = Depends(get_analytics_engine)
):
    """
    Get top selling products ranked by revenue
    
    Returns list of products with:
    - Product details
    - Times sold
    - Total quantity
    - Total revenue
    """
    store_ids_list = [int(x) for x in store_ids.split(",")] if store_ids else None
    channel_ids_list = [int(x) for x in channel_ids.split(",")] if channel_ids else None
    
    products = await engine.get_top_products(
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        brand_id=brand_id,
        store_ids=store_ids_list,
        channel_ids=channel_ids_list
    )
    
    return ProductsResponse(
        products=products,
        total_products=len(products),
        period={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    )


# ============================================================================
# CHANNELS ENDPOINT
# ============================================================================

@router.get("/channels", response_model=ChannelsResponse)
async def get_channel_metrics(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    brand_id: Optional[int] = Query(None, description="Brand ID to filter by owner"),
    store_ids: Optional[str] = Query(None, description="Comma-separated store IDs"),
    engine: AnalyticsEngine = Depends(get_analytics_engine)
):
    """
    Get sales metrics by channel (iFood, Rappi, Presencial, etc.)
    
    Returns metrics for each channel:
    - Total sales
    - Total revenue
    - Average ticket
    - Revenue share %
    """
    store_ids_list = [int(x) for x in store_ids.split(",")] if store_ids else None
    
    channels = await engine.get_channel_metrics(
        start_date=start_date,
        end_date=end_date,
        brand_id=brand_id,
        store_ids=store_ids_list
    )
    
    return ChannelsResponse(
        channels=channels,
        total_channels=len(channels),
        period={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    )


# ============================================================================
# STORES ENDPOINT
# ============================================================================

@router.get("/stores", response_model=StoresResponse)
async def get_store_metrics(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    brand_id: Optional[int] = Query(None, description="Brand ID to filter by owner"),
    channel_ids: Optional[str] = Query(None, description="Comma-separated channel IDs"),
    engine: AnalyticsEngine = Depends(get_analytics_engine)
):
    """
    Get sales metrics by store/location
    
    Returns metrics for each store:
    - Total sales
    - Total revenue
    - Average ticket
    - Revenue share %
    """
    channel_ids_list = [int(x) for x in channel_ids.split(",")] if channel_ids else None
    
    stores = await engine.get_store_metrics(
        start_date=start_date,
        end_date=end_date,
        brand_id=brand_id,
        channel_ids=channel_ids_list
    )
    
    return StoresResponse(
        stores=stores,
        total_stores=len(stores),
        period={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    )


# ============================================================================
# TIME SERIES ENDPOINTS
# ============================================================================

@router.get("/sales/trend", response_model=SalesTrendResponse)
async def get_sales_trend(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    brand_id: Optional[int] = Query(None, description="Brand ID to filter by owner"),
    store_ids: Optional[str] = Query(None, description="Comma-separated store IDs"),
    channel_ids: Optional[str] = Query(None, description="Comma-separated channel IDs"),
    engine: AnalyticsEngine = Depends(get_analytics_engine)
):
    """
    Get daily sales trend over time
    
    Returns daily metrics:
    - Total sales
    - Revenue
    - Average ticket
    - Completed/cancelled count
    """
    store_ids_list = [int(x) for x in store_ids.split(",")] if store_ids else None
    channel_ids_list = [int(x) for x in channel_ids.split(",")] if channel_ids else None
    
    trend = await engine.get_sales_trend(
        start_date=start_date,
        end_date=end_date,
        brand_id=brand_id,
        store_ids=store_ids_list,
        channel_ids=channel_ids_list
    )
    
    return SalesTrendResponse(
        trend=trend,
        period={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    )


# ============================================================================
# DISTRIBUTION ENDPOINTS
# ============================================================================

@router.get("/sales/hourly", response_model=HourlyDistributionResponse)
async def get_hourly_distribution(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    brand_id: Optional[int] = Query(None, description="Brand ID to filter by owner"),
    store_ids: Optional[str] = Query(None, description="Comma-separated store IDs"),
    channel_ids: Optional[str] = Query(None, description="Comma-separated channel IDs"),
    engine: AnalyticsEngine = Depends(get_analytics_engine)
):
    """
    Get sales distribution by hour of day (0-23)
    
    Useful for identifying peak hours
    """
    store_ids_list = [int(x) for x in store_ids.split(",")] if store_ids else None
    channel_ids_list = [int(x) for x in channel_ids.split(",")] if channel_ids else None
    
    distribution = await engine.get_hourly_distribution(
        start_date=start_date,
        end_date=end_date,
        brand_id=brand_id,
        store_ids=store_ids_list,
        channel_ids=channel_ids_list
    )
    
    return HourlyDistributionResponse(
        distribution=distribution,
        period={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    )


@router.get("/sales/weekday", response_model=WeekdayDistributionResponse)
async def get_weekday_distribution(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    brand_id: Optional[int] = Query(None, description="Brand ID to filter by owner"),
    store_ids: Optional[str] = Query(None, description="Comma-separated store IDs"),
    channel_ids: Optional[str] = Query(None, description="Comma-separated channel IDs"),
    engine: AnalyticsEngine = Depends(get_analytics_engine)
):
    """
    Get sales distribution by weekday (0=Monday, 6=Sunday)
    
    Useful for identifying best/worst days of the week
    """
    store_ids_list = [int(x) for x in store_ids.split(",")] if store_ids else None
    channel_ids_list = [int(x) for x in channel_ids.split(",")] if channel_ids else None
    
    distribution = await engine.get_weekday_distribution(
        start_date=start_date,
        end_date=end_date,
        brand_id=brand_id,
        store_ids=store_ids_list,
        channel_ids=channel_ids_list
    )
    
    return WeekdayDistributionResponse(
        distribution=distribution,
        period={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    )


# ============================================================================
# CATEGORIES ENDPOINT
# ============================================================================

@router.get("/categories", response_model=CategoriesResponse)
async def get_category_metrics(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    brand_id: Optional[int] = Query(None, description="Brand ID to filter by owner"),
    store_ids: Optional[str] = Query(None, description="Comma-separated store IDs"),
    channel_ids: Optional[str] = Query(None, description="Comma-separated channel IDs"),
    engine: AnalyticsEngine = Depends(get_analytics_engine)
):
    """
    Get sales metrics by product category
    
    Returns metrics for each category:
    - Total sales
    - Total revenue
    - Average price
    - Revenue share %
    """
    store_ids_list = [int(x) for x in store_ids.split(",")] if store_ids else None
    channel_ids_list = [int(x) for x in channel_ids.split(",")] if channel_ids else None
    
    categories = await engine.get_category_metrics(
        start_date=start_date,
        end_date=end_date,
        brand_id=brand_id,
        store_ids=store_ids_list,
        channel_ids=channel_ids_list
    )
    
    return CategoriesResponse(
        categories=categories,
        total_categories=len(categories),
        period={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    )


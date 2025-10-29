"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


# ============================================================================
# REQUEST SCHEMAS (Query Parameters)
# ============================================================================

class DateRangeQuery(BaseModel):
    """Date range filter for analytics queries"""
    start_date: date = Field(..., description="Start date (inclusive)")
    end_date: date = Field(..., description="End date (inclusive)")
    store_ids: Optional[list[int]] = Field(None, description="Filter by store IDs")
    channel_ids: Optional[list[int]] = Field(None, description="Filter by channel IDs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "store_ids": [1, 2, 3],
                "channel_ids": [1, 2]
            }
        }


# ============================================================================
# RESPONSE SCHEMAS (API Responses)
# ============================================================================

class OverviewMetrics(BaseModel):
    """Overview KPIs and metrics"""
    total_sales: int = Field(..., description="Total number of sales")
    total_revenue: float = Field(..., description="Total revenue in BRL")
    average_ticket: float = Field(..., description="Average ticket value")
    completed_sales: int = Field(..., description="Number of completed sales")
    cancelled_sales: int = Field(..., description="Number of cancelled sales")
    cancellation_rate: float = Field(..., description="Cancellation rate (%)")
    total_customers: int = Field(..., description="Total unique customers")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_sales": 15430,
                "total_revenue": 1025430.50,
                "average_ticket": 66.45,
                "completed_sales": 14658,
                "cancelled_sales": 772,
                "cancellation_rate": 5.0,
                "total_customers": 8542
            }
        }


class ProductRanking(BaseModel):
    """Product sales ranking"""
    product_id: int
    product_name: str
    category: Optional[str]
    times_sold: int = Field(..., description="Number of times sold")
    total_quantity: float = Field(..., description="Total quantity sold")
    total_revenue: float = Field(..., description="Total revenue generated")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": 42,
                "product_name": "X-Bacon Duplo",
                "category": "Burgers",
                "times_sold": 1250,
                "total_quantity": 1320.0,
                "total_revenue": 42500.00
            }
        }


class ChannelMetrics(BaseModel):
    """Sales metrics by channel"""
    channel_id: int
    channel_name: str
    channel_type: str = Field(..., description="P=Presencial, D=Delivery")
    total_sales: int
    total_revenue: float
    average_ticket: float
    revenue_share: float = Field(..., description="Revenue share (%)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "channel_id": 2,
                "channel_name": "iFood",
                "channel_type": "D",
                "total_sales": 4520,
                "total_revenue": 385420.00,
                "average_ticket": 85.25,
                "revenue_share": 32.5
            }
        }


class StoreMetrics(BaseModel):
    """Sales metrics by store"""
    store_id: int
    store_name: str
    city: Optional[str]
    state: Optional[str]
    total_sales: int
    total_revenue: float
    average_ticket: float
    revenue_share: float = Field(..., description="Revenue share (%)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "store_id": 1,
                "store_name": "Burguer House - Centro SP",
                "city": "São Paulo",
                "state": "SP",
                "total_sales": 2450,
                "total_revenue": 165420.00,
                "average_ticket": 67.52,
                "revenue_share": 15.8
            }
        }


class SalesTrend(BaseModel):
    """Sales trend over time"""
    date: date
    total_sales: int
    total_revenue: float
    average_ticket: float
    completed_sales: int
    cancelled_sales: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-01-15",
                "total_sales": 1250,
                "total_revenue": 85420.00,
                "average_ticket": 68.34,
                "completed_sales": 1180,
                "cancelled_sales": 70
            }
        }


class HourlyDistribution(BaseModel):
    """Sales distribution by hour"""
    hour: int = Field(..., ge=0, le=23, description="Hour of day (0-23)")
    total_sales: int
    total_revenue: float
    average_ticket: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "hour": 19,
                "total_sales": 450,
                "total_revenue": 32500.00,
                "average_ticket": 72.22
            }
        }


class WeekdayDistribution(BaseModel):
    """Sales distribution by weekday"""
    weekday: int = Field(..., ge=0, le=6, description="Day of week (0=Monday, 6=Sunday)")
    weekday_name: str
    total_sales: int
    total_revenue: float
    average_ticket: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "weekday": 5,
                "weekday_name": "Saturday",
                "total_sales": 3250,
                "total_revenue": 245000.00,
                "average_ticket": 75.38
            }
        }


class CategoryMetrics(BaseModel):
    """Sales metrics by product category"""
    category_name: str
    total_sales: int
    total_revenue: float
    average_price: float
    revenue_share: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "category_name": "Burgers",
                "total_sales": 5240,
                "total_revenue": 185000.00,
                "average_price": 35.30,
                "revenue_share": 42.5
            }
        }


# ============================================================================
# RESPONSE WRAPPERS
# ============================================================================

class OverviewResponse(BaseModel):
    """Overview analytics response"""
    metrics: OverviewMetrics
    period: dict = Field(..., description="Query period information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "metrics": {
                    "total_sales": 15430,
                    "total_revenue": 1025430.50,
                    "average_ticket": 66.45,
                    "completed_sales": 14658,
                    "cancelled_sales": 772,
                    "cancellation_rate": 5.0,
                    "total_customers": 8542
                },
                "period": {
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31",
                    "days": 31
                }
            }
        }


class ProductsResponse(BaseModel):
    """Products analytics response"""
    products: list[ProductRanking]
    total_products: int
    period: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "products": [
                    {
                        "product_id": 42,
                        "product_name": "X-Bacon Duplo",
                        "category": "Burgers",
                        "times_sold": 1250,
                        "total_quantity": 1320.0,
                        "total_revenue": 42500.00
                    }
                ],
                "total_products": 125,
                "period": {
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31"
                }
            }
        }


class ChannelsResponse(BaseModel):
    """Channels analytics response"""
    channels: list[ChannelMetrics]
    total_channels: int
    period: dict


class StoresResponse(BaseModel):
    """Stores analytics response"""
    stores: list[StoreMetrics]
    total_stores: int
    period: dict


class SalesTrendResponse(BaseModel):
    """Sales trend response"""
    trend: list[SalesTrend]
    period: dict


class HourlyDistributionResponse(BaseModel):
    """Hourly distribution response"""
    distribution: list[HourlyDistribution]
    period: dict


class WeekdayDistributionResponse(BaseModel):
    """Weekday distribution response"""
    distribution: list[WeekdayDistribution]
    period: dict


class CategoriesResponse(BaseModel):
    """Categories analytics response"""
    categories: list[CategoryMetrics]
    total_categories: int
    period: dict


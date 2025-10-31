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


class Brand(BaseModel):
    """Brand (owner/proprietário) information"""
    id: int
    name: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Maria - Burguer Boutique"
            }
        }


class Store(BaseModel):
    """Store information"""
    id: int
    name: str
    city: Optional[str]
    state: Optional[str]
    is_active: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Restaurante Centro - São Paulo",
                "city": "São Paulo",
                "state": "SP",
                "is_active": True
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


class BrandsListResponse(BaseModel):
    """Brands list response"""
    brands: list[Brand]
    total: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "brands": [
                    {"id": 1, "name": "Maria - Burguer Boutique"},
                    {"id": 2, "name": "João - Pizza & Cia"}
                ],
                "total": 7
            }
        }


class StoresListResponse(BaseModel):
    """Stores list response"""
    stores: list[Store]
    total: int
    brand_id: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "stores": [
                    {
                        "id": 1,
                        "name": "Restaurante Centro - São Paulo",
                        "city": "São Paulo",
                        "state": "SP",
                        "is_active": True
                    }
                ],
                "total": 3,
                "brand_id": 1
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


# ============================================================================
# DELIVERY ANALYTICS
# ============================================================================

class DeliveryPerformance(BaseModel):
    """Delivery performance metrics"""
    avg_delivery_time: float = Field(..., description="Average delivery time in seconds")
    avg_production_time: float = Field(..., description="Average production time in seconds")
    total_deliveries: int
    on_time_deliveries: int = Field(..., description="Deliveries under 45 minutes")
    on_time_rate: float = Field(..., description="On-time delivery rate (%)")
    # Cancellation metrics
    total_orders: int = Field(default=0, description="Total orders (completed + cancelled)")
    cancelled_orders: int = Field(default=0, description="Number of cancelled orders")
    cancellation_rate: float = Field(default=0.0, description="Cancellation rate (%)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "avg_delivery_time": 2340.5,
                "avg_production_time": 1200.3,
                "total_deliveries": 45230,
                "on_time_deliveries": 38450,
                "on_time_rate": 85.0,
                "total_orders": 50000,
                "cancelled_orders": 4770,
                "cancellation_rate": 9.54
            }
        }


class DeliveryByRegion(BaseModel):
    """Delivery metrics by region"""
    city: str
    state: str
    total_deliveries: int
    avg_delivery_time: float
    avg_production_time: float
    on_time_rate: float
    delivery_time_trend: float = Field(..., description="% change vs previous period")
    
    class Config:
        json_schema_extra = {
            "example": {
                "city": "São Paulo",
                "state": "SP",
                "total_deliveries": 15230,
                "avg_delivery_time": 2280.5,
                "avg_production_time": 1150.3,
                "on_time_rate": 87.5,
                "delivery_time_trend": -5.2
            }
        }


class DeliveryTrend(BaseModel):
    """Delivery time trend over time"""
    date: date
    avg_delivery_time: float
    avg_production_time: float
    total_deliveries: int
    on_time_rate: float


# ============================================================================
# CUSTOMER ANALYTICS (RFM)
# ============================================================================

class CustomerRFM(BaseModel):
    """Customer RFM analysis"""
    customer_id: int
    customer_name: str
    recency_days: int = Field(..., description="Days since last purchase")
    frequency: int = Field(..., description="Total number of purchases")
    monetary: float = Field(..., description="Total amount spent")
    last_purchase_date: date
    rfm_segment: str = Field(..., description="VIP, Regular, At Risk, Inactive")
    
    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": 1234,
                "customer_name": "João Silva",
                "recency_days": 45,
                "frequency": 12,
                "monetary": 2450.80,
                "last_purchase_date": "2025-04-15",
                "rfm_segment": "At Risk"
            }
        }


class ChurnRiskCustomer(BaseModel):
    """Customer at risk of churning"""
    customer_id: int
    customer_name: str
    email: Optional[str]
    phone_number: Optional[str]
    total_purchases: int
    total_spent: float
    last_purchase_date: date
    days_since_last_purchase: int
    avg_days_between_purchases: float
    favorite_channel: str
    favorite_product: Optional[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": 5678,
                "customer_name": "Maria Santos",
                "email": "maria@example.com",
                "phone_number": "+5511999999999",
                "total_purchases": 8,
                "total_spent": 1850.40,
                "last_purchase_date": "2025-03-20",
                "days_since_last_purchase": 42,
                "avg_days_between_purchases": 15.5,
                "favorite_channel": "iFood",
                "favorite_product": "X-Bacon Duplo"
            }
        }


# ============================================================================
# CONTEXTUAL PRODUCT ANALYTICS
# ============================================================================

class ProductByContext(BaseModel):
    """Product sales by specific context (weekday, hour, channel)"""
    product_id: int
    product_name: str
    category: Optional[str]
    times_sold: int
    total_revenue: float
    avg_price: float
    context: dict = Field(..., description="Context filters applied")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": 42,
                "product_name": "X-Bacon Duplo",
                "category": "Burgers",
                "times_sold": 234,
                "total_revenue": 8450.00,
                "avg_price": 36.11,
                "context": {
                    "weekday": "Thursday",
                    "hour_range": "19:00-23:00",
                    "channel": "iFood"
                }
            }
        }


class SalesHeatmapCell(BaseModel):
    """Sales heatmap cell (weekday x hour)"""
    weekday: int = Field(..., ge=0, le=6)
    weekday_name: str
    hour: int = Field(..., ge=0, le=23)
    total_sales: int
    total_revenue: float
    avg_ticket: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "weekday": 3,
                "weekday_name": "Thursday",
                "hour": 20,
                "total_sales": 450,
                "total_revenue": 16250.00,
                "avg_ticket": 36.11
            }
        }


# ============================================================================
# RESPONSE WRAPPERS (NEW)
# ============================================================================

class DeliveryPerformanceResponse(BaseModel):
    """Delivery performance response"""
    overall: DeliveryPerformance
    by_region: list[DeliveryByRegion]
    trend: list[DeliveryTrend]
    period: dict


class CustomerRFMResponse(BaseModel):
    """Customer RFM analysis response"""
    customers: list[CustomerRFM]
    total_customers: int
    segments: dict = Field(..., description="Count by segment")
    period: dict


class ChurnRiskResponse(BaseModel):
    """Churn risk customers response"""
    customers: list[ChurnRiskCustomer]
    total_at_risk: int
    criteria: dict
    period: dict


class ProductByContextResponse(BaseModel):
    """Products by context response"""
    products: list[ProductByContext]
    total_products: int
    context: dict
    period: dict


class SalesHeatmapResponse(BaseModel):
    """Sales heatmap response"""
    heatmap: list[SalesHeatmapCell]
    period: dict


# ============================================================================
# INSIGHTS SCHEMAS (NEW)
# ============================================================================

class InsightImpact(BaseModel):
    """Impact measurement for an insight"""
    metric: str = Field(..., description="Metric type: revenue_loss, revenue_opportunity, etc.")
    value: float = Field(..., description="Financial impact value in BRL")
    currency: str = Field(default="BRL", description="Currency code")
    period: str = Field(..., description="Period: daily, weekly, monthly, yearly")
    
    class Config:
        json_schema_extra = {
            "example": {
                "metric": "revenue_loss",
                "value": 12400.00,
                "currency": "BRL",
                "period": "monthly"
            }
        }


class InsightContext(BaseModel):
    """Context information about where/when the insight applies"""
    affected_stores: Optional[list[int]] = Field(None, description="Store IDs affected")
    affected_channels: Optional[list[int]] = Field(None, description="Channel IDs affected")
    affected_days: Optional[list[str]] = Field(None, description="Days of week affected")
    affected_hours: Optional[list[int]] = Field(None, description="Hours affected")
    affected_products: Optional[list[int]] = Field(None, description="Product IDs affected")
    data_points: int = Field(default=0, description="Number of data points analyzed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "affected_stores": [1, 2],
                "affected_channels": [3],
                "affected_days": ["friday", "saturday"],
                "affected_hours": [19, 20, 21],
                "data_points": 340
            }
        }


class InsightRecommendation(BaseModel):
    """Recommended action for the insight"""
    action: str = Field(..., description="Clear action to take")
    estimated_roi: Optional[float] = Field(None, description="Expected return on investment")
    difficulty: str = Field(default="medium", description="Implementation difficulty: easy, medium, hard")
    link_to: Optional[str] = Field(None, description="Link to relevant dashboard section")
    
    class Config:
        json_schema_extra = {
            "example": {
                "action": "Adicionar 2 entregadores nos fins de semana",
                "estimated_roi": 8500.00,
                "difficulty": "medium",
                "link_to": "/advanced?tab=delivery"
            }
        }


class Insight(BaseModel):
    """Single insight with all details"""
    id: str = Field(..., description="Unique insight identifier")
    type: str = Field(..., description="Insight type: performance_issue, opportunity, churn_risk, etc.")
    priority: str = Field(..., description="Priority level: critical, attention, positive")
    title: str = Field(..., description="Clear, actionable title")
    description: str = Field(..., description="Detailed description of the insight")
    impact: InsightImpact = Field(..., description="Financial or business impact")
    context: InsightContext = Field(..., description="Context information")
    recommendation: InsightRecommendation = Field(..., description="Recommended action")
    detected_at: datetime = Field(..., description="When this insight was detected")
    confidence_score: float = Field(default=0.75, description="Confidence in the insight (0-1)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "delivery_cancellation_spike_001",
                "type": "performance_issue",
                "priority": "critical",
                "title": "Alto índice de cancelamentos no delivery",
                "description": "340 pedidos cancelados após tempo médio de espera de 45min",
                "impact": {
                    "metric": "revenue_loss",
                    "value": 12400.00,
                    "currency": "BRL",
                    "period": "monthly"
                },
                "context": {
                    "affected_stores": [1, 2],
                    "affected_channels": [3],
                    "affected_days": ["friday", "saturday"],
                    "affected_hours": [19, 20, 21],
                    "data_points": 340
                },
                "recommendation": {
                    "action": "Adicionar 2 entregadores nos fins de semana no horário de pico",
                    "estimated_roi": 8500.00,
                    "difficulty": "medium",
                    "link_to": "/advanced?tab=delivery"
                },
                "detected_at": "2025-10-30T10:30:00Z",
                "confidence_score": 0.85
            }
        }


class InsightsResponse(BaseModel):
    """Response with multiple insights"""
    insights: list[Insight] = Field(..., description="List of detected insights")
    total: int = Field(..., description="Total number of insights found")
    generated_at: datetime = Field(..., description="When insights were generated")
    period: dict = Field(..., description="Analysis period")
    
    class Config:
        json_schema_extra = {
            "example": {
                "insights": [],
                "total": 3,
                "generated_at": "2025-10-30T10:30:00Z",
                "period": {
                    "start_date": "2025-05-01",
                    "end_date": "2025-05-31",
                    "days": 31
                }
            }
        }
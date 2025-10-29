"""
Analytics Engine - Core business logic for data analysis
"""
from datetime import date, timedelta
from typing import Optional
from app.core.database import Database
from app.models.schemas import (
    OverviewMetrics,
    ProductRanking,
    ChannelMetrics,
    StoreMetrics,
    SalesTrend,
    HourlyDistribution,
    WeekdayDistribution,
    CategoryMetrics,
)


class AnalyticsEngine:
    """
    Core analytics engine for querying and aggregating restaurant data
    """
    
    def __init__(self, db: Database):
        self.db = db
    
    # ========================================================================
    # OVERVIEW METRICS
    # ========================================================================
    
    async def get_overview_metrics(
        self,
        start_date: date,
        end_date: date,
        store_ids: Optional[list[int]] = None,
        channel_ids: Optional[list[int]] = None
    ) -> OverviewMetrics:
        """
        Get overview metrics (KPIs) for the specified period
        """
        # Build WHERE clause
        where_clauses = [
            "created_at >= $1",
            "created_at < $2"
        ]
        params = [start_date, end_date + timedelta(days=1)]
        param_count = 2
        
        if store_ids:
            param_count += 1
            where_clauses.append(f"store_id = ANY(${param_count})")
            params.append(store_ids)
        
        if channel_ids:
            param_count += 1
            where_clauses.append(f"channel_id = ANY(${param_count})")
            params.append(channel_ids)
        
        where_clause = " AND ".join(where_clauses)
        
        query = f"""
        SELECT 
            COUNT(*) as total_sales,
            COALESCE(SUM(CASE WHEN sale_status_desc = 'COMPLETED' THEN total_amount ELSE 0 END), 0) as total_revenue,
            COALESCE(AVG(CASE WHEN sale_status_desc = 'COMPLETED' THEN total_amount ELSE NULL END), 0) as average_ticket,
            COUNT(*) FILTER (WHERE sale_status_desc = 'COMPLETED') as completed_sales,
            COUNT(*) FILTER (WHERE sale_status_desc = 'CANCELLED') as cancelled_sales,
            ROUND(
                (COUNT(*) FILTER (WHERE sale_status_desc = 'CANCELLED')::NUMERIC / NULLIF(COUNT(*), 0) * 100), 
                2
            ) as cancellation_rate,
            COUNT(DISTINCT customer_id) FILTER (WHERE customer_id IS NOT NULL) as total_customers
        FROM sales
        WHERE {where_clause}
        """
        
        result = await self.db.fetch_one(query, *params)
        
        return OverviewMetrics(
            total_sales=result['total_sales'],
            total_revenue=float(result['total_revenue']),
            average_ticket=float(result['average_ticket']),
            completed_sales=result['completed_sales'],
            cancelled_sales=result['cancelled_sales'],
            cancellation_rate=float(result['cancellation_rate']) if result['cancellation_rate'] else 0.0,
            total_customers=result['total_customers']
        )
    
    # ========================================================================
    # PRODUCTS ANALYTICS
    # ========================================================================
    
    async def get_top_products(
        self,
        start_date: date,
        end_date: date,
        limit: int = 20,
        store_ids: Optional[list[int]] = None,
        channel_ids: Optional[list[int]] = None
    ) -> list[ProductRanking]:
        """
        Get top selling products ranked by revenue
        """
        where_clauses = [
            "s.created_at >= $1",
            "s.created_at < $2",
            "s.sale_status_desc = 'COMPLETED'"
        ]
        params = [start_date, end_date + timedelta(days=1)]
        param_count = 2
        
        if store_ids:
            param_count += 1
            where_clauses.append(f"s.store_id = ANY(${param_count})")
            params.append(store_ids)
        
        if channel_ids:
            param_count += 1
            where_clauses.append(f"s.channel_id = ANY(${param_count})")
            params.append(channel_ids)
        
        where_clause = " AND ".join(where_clauses)
        
        query = f"""
        SELECT 
            p.id as product_id,
            p.name as product_name,
            c.name as category,
            COUNT(DISTINCT ps.sale_id) as times_sold,
            SUM(ps.quantity) as total_quantity,
            SUM(ps.total_price) as total_revenue
        FROM product_sales ps
        JOIN products p ON p.id = ps.product_id
        JOIN sales s ON s.id = ps.sale_id
        LEFT JOIN categories c ON c.id = p.category_id
        WHERE {where_clause}
        GROUP BY p.id, p.name, c.name
        ORDER BY total_revenue DESC
        LIMIT ${{limit_param}}
        """
        
        param_count += 1
        params.append(limit)
        query = query.replace('{limit_param}', str(param_count))
        
        results = await self.db.fetch_all(query, *params)
        
        return [
            ProductRanking(
                product_id=row['product_id'],
                product_name=row['product_name'],
                category=row['category'],
                times_sold=row['times_sold'],
                total_quantity=float(row['total_quantity']),
                total_revenue=float(row['total_revenue'])
            )
            for row in results
        ]
    
    # ========================================================================
    # CHANNELS ANALYTICS
    # ========================================================================
    
    async def get_channel_metrics(
        self,
        start_date: date,
        end_date: date,
        store_ids: Optional[list[int]] = None
    ) -> list[ChannelMetrics]:
        """
        Get sales metrics by channel
        """
        where_clauses = [
            "s.created_at >= $1",
            "s.created_at < $2",
            "s.sale_status_desc = 'COMPLETED'"
        ]
        params = [start_date, end_date + timedelta(days=1)]
        
        if store_ids:
            where_clauses.append("s.store_id = ANY($3)")
            params.append(store_ids)
        
        where_clause = " AND ".join(where_clauses)
        
        query = f"""
        WITH channel_stats AS (
            SELECT 
                c.id as channel_id,
                c.name as channel_name,
                c.type as channel_type,
                COUNT(*) as total_sales,
                SUM(s.total_amount) as total_revenue,
                AVG(s.total_amount) as average_ticket
            FROM sales s
            JOIN channels c ON c.id = s.channel_id
            WHERE {where_clause}
            GROUP BY c.id, c.name, c.type
        ),
        total_revenue_sum AS (
            SELECT SUM(total_revenue) as total FROM channel_stats
        )
        SELECT 
            cs.*,
            ROUND((cs.total_revenue / NULLIF(trs.total, 0) * 100), 2) as revenue_share
        FROM channel_stats cs
        CROSS JOIN total_revenue_sum trs
        ORDER BY cs.total_revenue DESC
        """
        
        results = await self.db.fetch_all(query, *params)
        
        return [
            ChannelMetrics(
                channel_id=row['channel_id'],
                channel_name=row['channel_name'],
                channel_type=row['channel_type'],
                total_sales=row['total_sales'],
                total_revenue=float(row['total_revenue']),
                average_ticket=float(row['average_ticket']),
                revenue_share=float(row['revenue_share']) if row['revenue_share'] else 0.0
            )
            for row in results
        ]
    
    # ========================================================================
    # STORES ANALYTICS
    # ========================================================================
    
    async def get_store_metrics(
        self,
        start_date: date,
        end_date: date,
        channel_ids: Optional[list[int]] = None
    ) -> list[StoreMetrics]:
        """
        Get sales metrics by store
        """
        where_clauses = [
            "s.created_at >= $1",
            "s.created_at < $2",
            "s.sale_status_desc = 'COMPLETED'"
        ]
        params = [start_date, end_date + timedelta(days=1)]
        
        if channel_ids:
            where_clauses.append("s.channel_id = ANY($3)")
            params.append(channel_ids)
        
        where_clause = " AND ".join(where_clauses)
        
        query = f"""
        WITH store_stats AS (
            SELECT 
                st.id as store_id,
                st.name as store_name,
                st.city,
                st.state,
                COUNT(*) as total_sales,
                SUM(s.total_amount) as total_revenue,
                AVG(s.total_amount) as average_ticket
            FROM sales s
            JOIN stores st ON st.id = s.store_id
            WHERE {where_clause}
            GROUP BY st.id, st.name, st.city, st.state
        ),
        total_revenue_sum AS (
            SELECT SUM(total_revenue) as total FROM store_stats
        )
        SELECT 
            ss.*,
            ROUND((ss.total_revenue / NULLIF(trs.total, 0) * 100), 2) as revenue_share
        FROM store_stats ss
        CROSS JOIN total_revenue_sum trs
        ORDER BY ss.total_revenue DESC
        """
        
        results = await self.db.fetch_all(query, *params)
        
        return [
            StoreMetrics(
                store_id=row['store_id'],
                store_name=row['store_name'],
                city=row['city'],
                state=row['state'],
                total_sales=row['total_sales'],
                total_revenue=float(row['total_revenue']),
                average_ticket=float(row['average_ticket']),
                revenue_share=float(row['revenue_share']) if row['revenue_share'] else 0.0
            )
            for row in results
        ]
    
    # ========================================================================
    # TIME SERIES ANALYTICS
    # ========================================================================
    
    async def get_sales_trend(
        self,
        start_date: date,
        end_date: date,
        store_ids: Optional[list[int]] = None,
        channel_ids: Optional[list[int]] = None
    ) -> list[SalesTrend]:
        """
        Get daily sales trend
        """
        where_clauses = [
            "created_at >= $1",
            "created_at < $2"
        ]
        params = [start_date, end_date + timedelta(days=1)]
        param_count = 2
        
        if store_ids:
            param_count += 1
            where_clauses.append(f"store_id = ANY(${param_count})")
            params.append(store_ids)
        
        if channel_ids:
            param_count += 1
            where_clauses.append(f"channel_id = ANY(${param_count})")
            params.append(channel_ids)
        
        where_clause = " AND ".join(where_clauses)
        
        query = f"""
        SELECT 
            DATE(created_at) as date,
            COUNT(*) as total_sales,
            COALESCE(SUM(CASE WHEN sale_status_desc = 'COMPLETED' THEN total_amount ELSE 0 END), 0) as total_revenue,
            COALESCE(AVG(CASE WHEN sale_status_desc = 'COMPLETED' THEN total_amount ELSE NULL END), 0) as average_ticket,
            COUNT(*) FILTER (WHERE sale_status_desc = 'COMPLETED') as completed_sales,
            COUNT(*) FILTER (WHERE sale_status_desc = 'CANCELLED') as cancelled_sales
        FROM sales
        WHERE {where_clause}
        GROUP BY DATE(created_at)
        ORDER BY date ASC
        """
        
        results = await self.db.fetch_all(query, *params)
        
        return [
            SalesTrend(
                date=row['date'],
                total_sales=row['total_sales'],
                total_revenue=float(row['total_revenue']),
                average_ticket=float(row['average_ticket']),
                completed_sales=row['completed_sales'],
                cancelled_sales=row['cancelled_sales']
            )
            for row in results
        ]
    
    # ========================================================================
    # HOURLY/WEEKDAY DISTRIBUTION
    # ========================================================================
    
    async def get_hourly_distribution(
        self,
        start_date: date,
        end_date: date,
        store_ids: Optional[list[int]] = None,
        channel_ids: Optional[list[int]] = None
    ) -> list[HourlyDistribution]:
        """
        Get sales distribution by hour of day
        """
        where_clauses = [
            "created_at >= $1",
            "created_at < $2",
            "sale_status_desc = 'COMPLETED'"
        ]
        params = [start_date, end_date + timedelta(days=1)]
        param_count = 2
        
        if store_ids:
            param_count += 1
            where_clauses.append(f"store_id = ANY(${param_count})")
            params.append(store_ids)
        
        if channel_ids:
            param_count += 1
            where_clauses.append(f"channel_id = ANY(${param_count})")
            params.append(channel_ids)
        
        where_clause = " AND ".join(where_clauses)
        
        query = f"""
        SELECT 
            EXTRACT(HOUR FROM created_at)::INT as hour,
            COUNT(*) as total_sales,
            SUM(total_amount) as total_revenue,
            AVG(total_amount) as average_ticket
        FROM sales
        WHERE {where_clause}
        GROUP BY hour
        ORDER BY hour ASC
        """
        
        results = await self.db.fetch_all(query, *params)
        
        return [
            HourlyDistribution(
                hour=row['hour'],
                total_sales=row['total_sales'],
                total_revenue=float(row['total_revenue']),
                average_ticket=float(row['average_ticket'])
            )
            for row in results
        ]
    
    async def get_weekday_distribution(
        self,
        start_date: date,
        end_date: date,
        store_ids: Optional[list[int]] = None,
        channel_ids: Optional[list[int]] = None
    ) -> list[WeekdayDistribution]:
        """
        Get sales distribution by weekday
        """
        where_clauses = [
            "created_at >= $1",
            "created_at < $2",
            "sale_status_desc = 'COMPLETED'"
        ]
        params = [start_date, end_date + timedelta(days=1)]
        param_count = 2
        
        if store_ids:
            param_count += 1
            where_clauses.append(f"store_id = ANY(${param_count})")
            params.append(store_ids)
        
        if channel_ids:
            param_count += 1
            where_clauses.append(f"channel_id = ANY(${param_count})")
            params.append(channel_ids)
        
        where_clause = " AND ".join(where_clauses)
        
        weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        query = f"""
        SELECT 
            EXTRACT(DOW FROM created_at)::INT as weekday,
            COUNT(*) as total_sales,
            SUM(total_amount) as total_revenue,
            AVG(total_amount) as average_ticket
        FROM sales
        WHERE {where_clause}
        GROUP BY weekday
        ORDER BY weekday ASC
        """
        
        results = await self.db.fetch_all(query, *params)
        
        return [
            WeekdayDistribution(
                weekday=row['weekday'],
                weekday_name=weekday_names[row['weekday']],
                total_sales=row['total_sales'],
                total_revenue=float(row['total_revenue']),
                average_ticket=float(row['average_ticket'])
            )
            for row in results
        ]
    
    # ========================================================================
    # CATEGORY ANALYTICS
    # ========================================================================
    
    async def get_category_metrics(
        self,
        start_date: date,
        end_date: date,
        store_ids: Optional[list[int]] = None,
        channel_ids: Optional[list[int]] = None
    ) -> list[CategoryMetrics]:
        """
        Get sales metrics by product category
        """
        where_clauses = [
            "s.created_at >= $1",
            "s.created_at < $2",
            "s.sale_status_desc = 'COMPLETED'"
        ]
        params = [start_date, end_date + timedelta(days=1)]
        param_count = 2
        
        if store_ids:
            param_count += 1
            where_clauses.append(f"s.store_id = ANY(${param_count})")
            params.append(store_ids)
        
        if channel_ids:
            param_count += 1
            where_clauses.append(f"s.channel_id = ANY(${param_count})")
            params.append(channel_ids)
        
        where_clause = " AND ".join(where_clauses)
        
        query = f"""
        WITH category_stats AS (
            SELECT 
                COALESCE(c.name, 'Sem Categoria') as category_name,
                COUNT(*) as total_sales,
                SUM(ps.total_price) as total_revenue,
                AVG(ps.total_price) as average_price
            FROM product_sales ps
            JOIN products p ON p.id = ps.product_id
            JOIN sales s ON s.id = ps.sale_id
            LEFT JOIN categories c ON c.id = p.category_id
            WHERE {where_clause}
            GROUP BY c.name
        ),
        total_revenue_sum AS (
            SELECT SUM(total_revenue) as total FROM category_stats
        )
        SELECT 
            cs.*,
            ROUND((cs.total_revenue / NULLIF(trs.total, 0) * 100), 2) as revenue_share
        FROM category_stats cs
        CROSS JOIN total_revenue_sum trs
        ORDER BY cs.total_revenue DESC
        """
        
        results = await self.db.fetch_all(query, *params)
        
        return [
            CategoryMetrics(
                category_name=row['category_name'],
                total_sales=row['total_sales'],
                total_revenue=float(row['total_revenue']),
                average_price=float(row['average_price']),
                revenue_share=float(row['revenue_share']) if row['revenue_share'] else 0.0
            )
            for row in results
        ]


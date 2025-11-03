"""
Advanced Analytics Engine - Delivery, Customer RFM, Contextual Analysis
"""
from datetime import date, timedelta
from typing import Optional
from app.core.database import Database
from app.models.schemas import (
    DeliveryPerformance,
    DeliveryByRegion,
    DeliveryTrend,
    CustomerRFM,
    ChurnRiskCustomer,
    ProductByContext,
    SalesHeatmapCell,
    StoreMetrics,
)


class AdvancedAnalyticsEngine:
    """
    Advanced analytics for delivery, customer retention, and contextual analysis
    """
    
    def __init__(self, db: Database):
        self.db = db
    
    # ========================================================================
    # DELIVERY ANALYTICS - Pergunta 2: "Tempo de entrega piorou?"
    # ========================================================================
    
    async def get_delivery_performance(
        self,
        start_date: date,
        end_date: date,
        brand_id: Optional[int] = None,
        store_ids: Optional[list[int]] = None,
        weekday: Optional[int] = None,
        hour_start: Optional[int] = None,
        hour_end: Optional[int] = None,
        channel_id: Optional[int] = None
    ) -> tuple[DeliveryPerformance, list[DeliveryByRegion], list[DeliveryTrend]]:
        """
        Get delivery performance metrics
        """
        where_clauses = [
            "s.created_at >= $1",
            "s.created_at < $2",
            "s.sale_status_desc = 'COMPLETED'",
            "ds.id IS NOT NULL"
        ]
        params = [start_date, end_date + timedelta(days=1)]
        param_count = 2
        
        if brand_id:
            param_count += 1
            where_clauses.append(f"st.brand_id = ${param_count}")
            params.append(brand_id)
        
        if store_ids:
            param_count += 1
            where_clauses.append(f"s.store_id = ANY(${param_count})")
            params.append(store_ids)
        
        if weekday is not None:
            param_count += 1
            where_clauses.append(f"EXTRACT(DOW FROM s.created_at)::INT = ${param_count}")
            params.append(weekday)
        
        if hour_start is not None:
            param_count += 1
            where_clauses.append(f"EXTRACT(HOUR FROM s.created_at)::INT >= ${param_count}")
            params.append(hour_start)
        
        if hour_end is not None:
            param_count += 1
            where_clauses.append(f"EXTRACT(HOUR FROM s.created_at)::INT < ${param_count}")
            params.append(hour_end)
        
        if channel_id is not None:
            param_count += 1
            where_clauses.append(f"s.channel_id = ${param_count}")
            params.append(channel_id)
        
        where_clause = " AND ".join(where_clauses)
        
        # Build WHERE clause for all orders (including cancellations)
        where_all_clauses = [
            "s.created_at >= $1",
            "s.created_at < $2"
        ]
        param_count_all = 2
        params_all = [start_date, end_date + timedelta(days=1)]
        
        if brand_id:
            param_count_all += 1
            where_all_clauses.append(f"st.brand_id = ${param_count_all}")
            params_all.append(brand_id)
        
        if store_ids:
            param_count_all += 1
            where_all_clauses.append(f"s.store_id = ANY(${param_count_all})")
            params_all.append(store_ids)
        
        if weekday is not None:
            param_count_all += 1
            where_all_clauses.append(f"EXTRACT(DOW FROM s.created_at)::INT = ${param_count_all}")
            params_all.append(weekday)
        
        if hour_start is not None:
            param_count_all += 1
            where_all_clauses.append(f"EXTRACT(HOUR FROM s.created_at)::INT >= ${param_count_all}")
            params_all.append(hour_start)
        
        if hour_end is not None:
            param_count_all += 1
            where_all_clauses.append(f"EXTRACT(HOUR FROM s.created_at)::INT < ${param_count_all}")
            params_all.append(hour_end)
        
        if channel_id is not None:
            param_count_all += 1
            where_all_clauses.append(f"s.channel_id = ${param_count_all}")
            params_all.append(channel_id)
        
        where_all_clause = " AND ".join(where_all_clauses)
        
        # Overall performance with cancellation metrics
        overall_query = f"""
        WITH delivery_metrics AS (
            SELECT 
                AVG(s.delivery_seconds) as avg_delivery_time,
                AVG(s.production_seconds) as avg_production_time,
                COUNT(*) as total_deliveries,
                COUNT(*) FILTER (WHERE (s.delivery_seconds + s.production_seconds) <= 2700) as on_time_deliveries
            FROM sales s
            INNER JOIN stores st ON s.store_id = st.id
            JOIN delivery_sales ds ON ds.sale_id = s.id
            WHERE {where_clause}
        ),
        cancellation_metrics AS (
            SELECT 
                COUNT(*) as total_orders,
                COUNT(*) FILTER (WHERE s.sale_status_desc IN ('CANCELLED', 'CANCELED')) as cancelled_orders
            FROM sales s
            INNER JOIN stores st ON s.store_id = st.id
            WHERE {where_all_clause}
        )
        SELECT 
            dm.*,
            COALESCE(cm.total_orders, 0) as total_orders,
            COALESCE(cm.cancelled_orders, 0) as cancelled_orders
        FROM delivery_metrics dm, cancellation_metrics cm
        """
        
        overall = await self.db.fetch_one(overall_query, *params)
        
        on_time_rate = (overall['on_time_deliveries'] / overall['total_deliveries'] * 100) if overall['total_deliveries'] > 0 else 0.0
        cancellation_rate = (overall['cancelled_orders'] / overall['total_orders'] * 100) if overall['total_orders'] > 0 else 0.0
        
        overall_metrics = DeliveryPerformance(
            avg_delivery_time=float(overall['avg_delivery_time']) if overall['avg_delivery_time'] else 0.0,
            avg_production_time=float(overall['avg_production_time']) if overall['avg_production_time'] else 0.0,
            total_deliveries=overall['total_deliveries'],
            on_time_deliveries=overall['on_time_deliveries'],
            on_time_rate=round(on_time_rate, 2),
            total_orders=overall['total_orders'],
            cancelled_orders=overall['cancelled_orders'],
            cancellation_rate=round(cancellation_rate, 2)
        )
        
        # By region
        region_query = f"""
        WITH current_period AS (
            SELECT 
                da.city,
                da.state,
                COUNT(*) as total_deliveries,
                AVG(s.delivery_seconds) as avg_delivery_time,
                AVG(s.production_seconds) as avg_production_time,
                COUNT(*) FILTER (WHERE (s.delivery_seconds + s.production_seconds) <= 2700) as on_time_deliveries
            FROM sales s
            INNER JOIN stores st ON s.store_id = st.id
            JOIN delivery_sales ds ON ds.sale_id = s.id
            JOIN delivery_addresses da ON da.sale_id = s.id
            WHERE {where_clause}
            GROUP BY da.city, da.state
        )
        SELECT 
            city,
            state,
            total_deliveries,
            avg_delivery_time,
            avg_production_time,
            ROUND((on_time_deliveries::NUMERIC / NULLIF(total_deliveries, 0) * 100), 2) as on_time_rate,
            0.0 as delivery_time_trend
        FROM current_period
        WHERE total_deliveries >= 10
        ORDER BY total_deliveries DESC
        LIMIT 20
        """
        
        region_results = await self.db.fetch_all(region_query, *params)
        
        by_region = [
            DeliveryByRegion(
                city=row['city'],
                state=row['state'],
                total_deliveries=row['total_deliveries'],
                avg_delivery_time=float(row['avg_delivery_time']) if row['avg_delivery_time'] else 0.0,
                avg_production_time=float(row['avg_production_time']) if row['avg_production_time'] else 0.0,
                on_time_rate=float(row['on_time_rate']) if row['on_time_rate'] else 0.0,
                delivery_time_trend=float(row['delivery_time_trend'])
            )
            for row in region_results
        ]
        
        # Trend over time
        trend_query = f"""
        SELECT 
            DATE(s.created_at) as date,
            AVG(s.delivery_seconds) as avg_delivery_time,
            AVG(s.production_seconds) as avg_production_time,
            COUNT(*) as total_deliveries,
            ROUND((COUNT(*) FILTER (WHERE (s.delivery_seconds + s.production_seconds) <= 2700)::NUMERIC / NULLIF(COUNT(*), 0) * 100), 2) as on_time_rate
        FROM sales s
        INNER JOIN stores st ON s.store_id = st.id
        JOIN delivery_sales ds ON ds.sale_id = s.id
        WHERE {where_clause}
        GROUP BY DATE(s.created_at)
        ORDER BY date ASC
        """
        
        trend_results = await self.db.fetch_all(trend_query, *params)
        
        trend = [
            DeliveryTrend(
                date=row['date'],
                avg_delivery_time=float(row['avg_delivery_time']) if row['avg_delivery_time'] else 0.0,
                avg_production_time=float(row['avg_production_time']) if row['avg_production_time'] else 0.0,
                total_deliveries=row['total_deliveries'],
                on_time_rate=float(row['on_time_rate']) if row['on_time_rate'] else 0.0
            )
            for row in trend_results
        ]
        
        return overall_metrics, by_region, trend
    
    # ========================================================================
    # CUSTOMER RFM ANALYTICS - Pergunta 3: "Clientes que não voltam?"
    # ========================================================================
    
    async def get_customer_rfm(
        self,
        start_date: date,
        end_date: date,
        brand_id: Optional[int] = None,
        reference_date: Optional[date] = None
    ) -> list[CustomerRFM]:
        """
        Get RFM (Recency, Frequency, Monetary) analysis for customers
        """
        if not reference_date:
            reference_date = end_date
        
        brand_filter = "AND st.brand_id = $4" if brand_id else ""
        
        query = f"""
        WITH customer_stats AS (
            SELECT 
                c.id as customer_id,
                COALESCE(c.customer_name, s.customer_name, 'Cliente Anônimo') as customer_name,
                MAX(s.created_at::date) as last_purchase_date,
                $3::date - MAX(s.created_at::date) as recency_days,
                COUNT(*) as frequency,
                SUM(s.total_amount) as monetary
            FROM customers c
            JOIN sales s ON s.customer_id = c.id
            INNER JOIN stores st ON s.store_id = st.id
            WHERE s.created_at >= $1
                AND s.created_at < $2
                AND s.sale_status_desc = 'COMPLETED'
                AND c.id IS NOT NULL
                {brand_filter}
            GROUP BY c.id, c.customer_name, s.customer_name
            HAVING COUNT(*) >= 1
        )
        SELECT 
            customer_id,
            customer_name,
            recency_days,
            frequency,
            monetary,
            last_purchase_date,
            CASE 
                WHEN recency_days <= 7 AND frequency >= 5 AND monetary >= 500 THEN 'VIP'
                WHEN recency_days <= 15 AND frequency >= 3 THEN 'Regular'
                WHEN recency_days > 30 AND frequency >= 3 THEN 'At Risk'
                WHEN recency_days > 60 THEN 'Inactive'
                ELSE 'New'
            END as rfm_segment
        FROM customer_stats
        ORDER BY 
            CASE 
                WHEN rfm_segment = 'VIP' THEN 1
                WHEN rfm_segment = 'Regular' THEN 2
                WHEN rfm_segment = 'At Risk' THEN 3
                WHEN rfm_segment = 'Inactive' THEN 4
                ELSE 5
            END,
            monetary DESC
        LIMIT 1000
        """
        
        params = [start_date, end_date + timedelta(days=1), reference_date]
        if brand_id:
            params.append(brand_id)
        
        results = await self.db.fetch_all(query, *params)
        
        return [
            CustomerRFM(
                customer_id=row['customer_id'],
                customer_name=row['customer_name'],
                recency_days=row['recency_days'],
                frequency=row['frequency'],
                monetary=float(row['monetary']),
                last_purchase_date=row['last_purchase_date'],
                rfm_segment=row['rfm_segment']
            )
            for row in results
        ]
    
    async def get_churn_risk_customers(
        self,
        min_purchases: int = 3,
        days_inactive: int = 30,
        brand_id: Optional[int] = None,
        store_ids: Optional[list[int]] = None,
        limit: int = 100
    ) -> list[ChurnRiskCustomer]:
        """
        Get customers at risk of churning (bought X+ times but haven't returned in Y days)
        Can be filtered by brand and/or specific stores
        """
        # Build filter conditions
        filters = []
        param_counter = 4  # Start after min_purchases, days_inactive, limit
        params_dict = {}
        
        if brand_id:
            filters.append(f"st.brand_id = ${param_counter}")
            params_dict[param_counter] = brand_id
            param_counter += 1
        
        if store_ids:
            store_placeholders = ", ".join([f"${param_counter + i}" for i in range(len(store_ids))])
            filters.append(f"st.id IN ({store_placeholders})")
            for i, store_id in enumerate(store_ids):
                params_dict[param_counter + i] = store_id
            param_counter += len(store_ids)
        
        where_filter = "AND " + " AND ".join(filters) if filters else ""
        
        query = f"""
        WITH purchase_intervals AS (
            SELECT 
                s.customer_id,
                s.created_at,
                s.created_at::date - LAG(s.created_at::date) OVER (PARTITION BY s.customer_id ORDER BY s.created_at) as days_between
            FROM sales s
            INNER JOIN stores st ON s.store_id = st.id
            WHERE s.sale_status_desc = 'COMPLETED'
                AND s.customer_id IS NOT NULL
                {where_filter}
        ),
        customer_stats AS (
            SELECT 
                c.id as customer_id,
                COALESCE(c.customer_name, MAX(s.customer_name), 'Cliente Anônimo') as customer_name,
                c.email,
                c.phone_number,
                COUNT(*) as total_purchases,
                SUM(s.total_amount) as total_spent,
                MAX(s.created_at::date) as last_purchase_date,
                CURRENT_DATE - MAX(s.created_at::date) as days_since_last_purchase,
                COALESCE((
                    SELECT AVG(days_between)::FLOAT
                    FROM purchase_intervals pi
                    WHERE pi.customer_id = c.id AND pi.days_between IS NOT NULL
                ), 0.0) as avg_days_between_purchases
            FROM customers c
            JOIN sales s ON s.customer_id = c.id
            INNER JOIN stores st ON s.store_id = st.id
            WHERE s.sale_status_desc = 'COMPLETED'
                AND c.id IS NOT NULL
                {where_filter}
            GROUP BY c.id, c.customer_name, c.email, c.phone_number
            HAVING COUNT(*) >= $1
                AND CURRENT_DATE - MAX(s.created_at::date) >= $2
        ),
        favorite_channel AS (
            SELECT DISTINCT ON (s.customer_id)
                s.customer_id,
                ch.name as channel_name
            FROM sales s
            INNER JOIN stores st ON s.store_id = st.id
            JOIN channels ch ON ch.id = s.channel_id
            WHERE s.sale_status_desc = 'COMPLETED'
                {where_filter}
            GROUP BY s.customer_id, ch.name
            ORDER BY s.customer_id, COUNT(*) DESC
        ),
        favorite_product AS (
            SELECT DISTINCT ON (s.customer_id)
                s.customer_id,
                p.name as product_name
            FROM sales s
            INNER JOIN stores st ON s.store_id = st.id
            JOIN product_sales ps ON ps.sale_id = s.id
            JOIN products p ON p.id = ps.product_id
            WHERE s.sale_status_desc = 'COMPLETED'
                {where_filter}
            GROUP BY s.customer_id, p.name
            ORDER BY s.customer_id, COUNT(*) DESC
        )
        SELECT 
            cs.*,
            fc.channel_name as favorite_channel,
            fp.product_name as favorite_product
        FROM customer_stats cs
        LEFT JOIN favorite_channel fc ON fc.customer_id = cs.customer_id
        LEFT JOIN favorite_product fp ON fp.customer_id = cs.customer_id
        ORDER BY cs.total_spent DESC, cs.days_since_last_purchase DESC
        LIMIT $3
        """
        
        # Build params list in order
        params = [min_purchases, days_inactive, limit]
        
        # Add brand_id and store_ids in the order they appear in params_dict
        for param_num in sorted(params_dict.keys()):
            params.append(params_dict[param_num])
        
        results = await self.db.fetch_all(query, *params)
        
        return [
            ChurnRiskCustomer(
                customer_id=row['customer_id'],
                customer_name=row['customer_name'],
                email=row['email'],
                phone_number=row['phone_number'],
                total_purchases=row['total_purchases'],
                total_spent=float(row['total_spent']),
                last_purchase_date=row['last_purchase_date'],
                days_since_last_purchase=row['days_since_last_purchase'],
                avg_days_between_purchases=float(row['avg_days_between_purchases']) if row['avg_days_between_purchases'] else 0.0,
                favorite_channel=row['favorite_channel'] or 'Desconhecido',
                favorite_product=row['favorite_product']
            )
            for row in results
        ]
    
    # ========================================================================
    # CONTEXTUAL PRODUCT ANALYTICS - Pergunta 1: "Produto mais vendido quinta à noite no iFood?"
    # ========================================================================
    
    async def get_products_by_context(
        self,
        start_date: date,
        end_date: date,
        brand_id: Optional[int] = None,
        weekday: Optional[int] = None,  # 0=Monday, 6=Sunday
        hour_start: Optional[int] = None,
        hour_end: Optional[int] = None,
        channel_id: Optional[int] = None,
        store_ids: Optional[list[int]] = None,
        limit: int = 20
    ) -> list[ProductByContext]:
        """
        Get top products by specific context (weekday, hour range, channel)
        """
        where_clauses = [
            "s.created_at >= $1",
            "s.created_at < $2",
            "s.sale_status_desc = 'COMPLETED'"
        ]
        params = [start_date, end_date + timedelta(days=1)]
        param_count = 2
        
        context_info = {}
        
        if brand_id:
            param_count += 1
            where_clauses.append(f"st.brand_id = ${param_count}")
            params.append(brand_id)
        
        if weekday is not None:
            param_count += 1
            where_clauses.append(f"EXTRACT(DOW FROM s.created_at)::INT = ${param_count}")
            params.append(weekday)
            weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            context_info['weekday'] = weekday_names[weekday]
        
        if hour_start is not None and hour_end is not None:
            param_count += 1
            where_clauses.append(f"EXTRACT(HOUR FROM s.created_at)::INT >= ${param_count}")
            params.append(hour_start)
            param_count += 1
            where_clauses.append(f"EXTRACT(HOUR FROM s.created_at)::INT < ${param_count}")
            params.append(hour_end)
            context_info['hour_range'] = f"{hour_start:02d}:00-{hour_end:02d}:00"
        
        if channel_id is not None:
            param_count += 1
            where_clauses.append(f"s.channel_id = ${param_count}")
            params.append(channel_id)
            
            # Get channel name
            channel_query = "SELECT name FROM channels WHERE id = $1"
            channel_result = await self.db.fetch_one(channel_query, channel_id)
            if channel_result:
                context_info['channel'] = channel_result['name']
        
        if store_ids:
            param_count += 1
            where_clauses.append(f"s.store_id = ANY(${param_count})")
            params.append(store_ids)
        
        where_clause = " AND ".join(where_clauses)
        
        query = f"""
        SELECT 
            p.id as product_id,
            p.name as product_name,
            c.name as category,
            COUNT(DISTINCT ps.sale_id) as times_sold,
            SUM(ps.total_price) as total_revenue,
            AVG(ps.total_price / ps.quantity) as avg_price
        FROM product_sales ps
        JOIN products p ON p.id = ps.product_id
        JOIN sales s ON s.id = ps.sale_id
        INNER JOIN stores st ON s.store_id = st.id
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
            ProductByContext(
                product_id=row['product_id'],
                product_name=row['product_name'],
                category=row['category'],
                times_sold=row['times_sold'],
                total_revenue=float(row['total_revenue']),
                avg_price=float(row['avg_price']),
                context=context_info
            )
            for row in results
        ]
    
    # ========================================================================
    # SALES HEATMAP
    # ========================================================================
    
    async def get_sales_heatmap(
        self,
        start_date: date,
        end_date: date,
        brand_id: Optional[int] = None,
        store_ids: Optional[list[int]] = None,
        channel_ids: Optional[list[int]] = None
    ) -> list[SalesHeatmapCell]:
        """
        Get sales heatmap (weekday x hour)
        """
        where_clauses = [
            "s.created_at >= $1",
            "s.created_at < $2",
            "s.sale_status_desc = 'COMPLETED'"
        ]
        params = [start_date, end_date + timedelta(days=1)]
        param_count = 2
        
        if brand_id:
            param_count += 1
            where_clauses.append(f"st.brand_id = ${param_count}")
            params.append(brand_id)
        
        if store_ids:
            param_count += 1
            where_clauses.append(f"s.store_id = ANY(${param_count})")
            params.append(store_ids)
        
        if channel_ids:
            param_count += 1
            where_clauses.append(f"s.channel_id = ANY(${param_count})")
            params.append(channel_ids)
        
        where_clause = " AND ".join(where_clauses)
        
        weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        query = f"""
        SELECT 
            EXTRACT(DOW FROM s.created_at)::INT as weekday,
            EXTRACT(HOUR FROM s.created_at)::INT as hour,
            COUNT(*) as total_sales,
            SUM(s.total_amount) as total_revenue,
            AVG(s.total_amount) as avg_ticket
        FROM sales s
        INNER JOIN stores st ON s.store_id = st.id
        WHERE {where_clause}
        GROUP BY weekday, hour
        ORDER BY weekday, hour
        """
        
        results = await self.db.fetch_all(query, *params)
        
        return [
            SalesHeatmapCell(
                weekday=row['weekday'],
                weekday_name=weekday_names[row['weekday']],
                hour=row['hour'],
                total_sales=row['total_sales'],
                total_revenue=float(row['total_revenue']),
                avg_ticket=float(row['avg_ticket'])
            )
            for row in results
        ]
    
    # ========================================================================
    # STORE PERFORMANCE WITH CONTEXTUAL FILTERS
    # ========================================================================
    
    async def get_store_performance(
        self,
        start_date: date,
        end_date: date,
        brand_id: Optional[int] = None,
        weekday: Optional[int] = None,  # 0=Monday, 6=Sunday
        hour_start: Optional[int] = None,
        hour_end: Optional[int] = None,
        channel_id: Optional[int] = None,
        store_ids: Optional[list[int]] = None
    ) -> list[StoreMetrics]:
        """
        Get store performance metrics with contextual filters (weekday, hour range, channel)
        
        Note: revenue_share is always calculated against ALL stores in the network,
        regardless of store_ids filter, so participation % is meaningful network-wide.
        """
        # WHERE clause for ALL stores (to calculate total revenue for participation %)
        where_clauses_all = [
            "s.created_at >= $1",
            "s.created_at < $2",
            "s.sale_status_desc = 'COMPLETED'"
        ]
        params = [start_date, end_date + timedelta(days=1)]
        param_count = 2
        
        if brand_id:
            param_count += 1
            where_clauses_all.append(f"st.brand_id = ${param_count}")
            params.append(brand_id)
        
        if weekday is not None:
            param_count += 1
            where_clauses_all.append(f"EXTRACT(DOW FROM s.created_at)::INT = ${param_count}")
            params.append(weekday)
        
        if hour_start is not None and hour_end is not None:
            param_count += 1
            where_clauses_all.append(f"EXTRACT(HOUR FROM s.created_at)::INT >= ${param_count}")
            params.append(hour_start)
            param_count += 1
            where_clauses_all.append(f"EXTRACT(HOUR FROM s.created_at)::INT < ${param_count}")
            params.append(hour_end)
        
        if channel_id is not None:
            param_count += 1
            where_clauses_all.append(f"s.channel_id = ${param_count}")
            params.append(channel_id)
        
        # WHERE clause for FILTERED stores (to determine which stores to return)
        where_clauses_filtered = where_clauses_all.copy()
        if store_ids:
            param_count += 1
            where_clauses_filtered.append(f"s.store_id = ANY(${param_count})")
            params.append(store_ids)
        
        where_clause_all = " AND ".join(where_clauses_all)
        where_clause_filtered = " AND ".join(where_clauses_filtered)
        
        query = f"""
        -- Calculate total revenue from ALL stores (for participation calculation)
        WITH all_store_revenue AS (
            SELECT SUM(s.total_amount) as total_revenue_all
            FROM sales s
            JOIN stores st ON st.id = s.store_id
            WHERE {where_clause_all}
        ),
        -- Calculate stats for FILTERED stores only
        store_stats AS (
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
            WHERE {where_clause_filtered}
            GROUP BY st.id, st.name, st.city, st.state
        )
        SELECT 
            ss.*,
            ROUND((ss.total_revenue / NULLIF(ar.total_revenue_all, 0) * 100), 2) as revenue_share
        FROM store_stats ss
        CROSS JOIN all_store_revenue ar
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


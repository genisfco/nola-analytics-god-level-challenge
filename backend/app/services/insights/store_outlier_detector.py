"""
Detector for store performance outliers
Identifies stores performing significantly above or below average
"""
from datetime import datetime
from app.models.schemas import Insight, InsightImpact, InsightContext, InsightRecommendation
from .base_detector import BaseInsightDetector


class StoreOutlierDetector(BaseInsightDetector):
    """Detects stores with exceptional performance (positive or negative)"""
    
    # Thresholds
    MIN_REVENUE_DIFF_PCT = 10.0  # 10%+ difference from average triggers alert
    MIN_STORES_REQUIRED = 3  # Need at least 3 stores to calculate meaningful average
    
    async def detect(self) -> list[Insight]:
        """Detect store performance outlier insights"""
        insights = []
        
        # Detect both underperforming and overperforming stores
        underperformer = await self._detect_underperforming_store()
        if underperformer:
            insights.append(underperformer)
        
        overperformer = await self._detect_overperforming_store()
        if overperformer:
            insights.append(overperformer)
        
        return insights
    
    async def _detect_underperforming_store(self) -> Insight | None:
        """
        Detect: Store with revenue 30%+ below brand average
        Critical alert: Underperforming store needs attention
        """
        store_filter = self._get_store_filter()
        
        query = f"""
            WITH store_performance AS (
                SELECT 
                    st.id,
                    st.name,
                    COALESCE(SUM(s.total_amount) FILTER (WHERE s.sale_status_desc = 'COMPLETED'), 0) as revenue,
                    COUNT(s.id) FILTER (WHERE s.sale_status_desc = 'COMPLETED') as orders,
                    COALESCE(AVG(s.total_amount) FILTER (WHERE s.sale_status_desc = 'COMPLETED'), 0) as avg_ticket
                FROM stores st
                LEFT JOIN sales s ON s.store_id = st.id 
                    AND s.created_at BETWEEN $2 AND $3
                WHERE st.brand_id = $1
                    AND st.is_active = true
                    {store_filter}
                GROUP BY st.id, st.name
            ),
            avg_metrics AS (
                SELECT 
                    AVG(revenue) as avg_revenue,
                    AVG(orders) as avg_orders,
                    AVG(avg_ticket) as avg_ticket
                FROM store_performance
            ),
            outlier_stores AS (
                SELECT 
                    sp.id,
                    sp.name,
                    sp.revenue,
                    sp.orders,
                    sp.avg_ticket as sp_avg_ticket,
                    am.avg_revenue as am_avg_revenue,
                    am.avg_orders as am_avg_orders,
                    am.avg_ticket as am_avg_ticket,
                    ((sp.revenue - am.avg_revenue) / NULLIF(am.avg_revenue, 0) * 100) as revenue_diff_pct,
                    (sp.revenue - am.avg_revenue) as revenue_gap
                FROM store_performance sp, avg_metrics am
                WHERE am.avg_revenue > 0
                    AND ((sp.revenue - am.avg_revenue) / NULLIF(am.avg_revenue, 0) * 100) < -{self.MIN_REVENUE_DIFF_PCT}
                ORDER BY revenue_diff_pct ASC
                LIMIT 10
            )
            SELECT * FROM outlier_stores
        """
        
        row = await self.db.fetch_one(
            query,
            self.brand_id,
            self.start_date,
            self.end_date
        )
        
        if not row:
            return None
        
        store_id = row['id']
        store_name = row['name']
        revenue = float(row['revenue'])
        avg_revenue = float(row['am_avg_revenue'])
        revenue_diff_pct = float(row['revenue_diff_pct'])
        revenue_gap = float(row['revenue_gap'])
        
        # Calculate potential monthly recovery
        monthly_recovery = abs(self._extrapolate_to_monthly(revenue_gap))
        
        # Only create insight if meaningful amount
        if monthly_recovery < 1000:  # Less than R$ 1,000/month
            return None
        
        # Calculate confidence based on how many stores we're comparing against
        num_stores = await self._count_active_stores()
        confidence = min(0.5 + (num_stores / 10) * 0.5, 1.0) if num_stores >= self.MIN_STORES_REQUIRED else 0.4
        
        # Estimate ROI (assuming we can recover 50% of the gap with improvements)
        estimated_roi = monthly_recovery * 0.5
        
        # Determine priority based on severity
        priority = "critical" if abs(revenue_diff_pct) > 50 else "attention"
        
        return Insight(
            id=f"store_underperformer_{store_id}_{self.brand_id}",
            type="performance_issue",
            priority=priority,
            title=f"Loja {store_name[:50]} abaixo da média: {abs(revenue_diff_pct):.1f}%",
            description=(
                f"A loja {store_name} tem receita de R$ {revenue:,.2f}, "
                f"R$ {abs(revenue_gap):,.2f} abaixo da média das outras lojas. "
                f"Diferença de {abs(revenue_diff_pct):.1f}% do esperado."
            ),
            impact=InsightImpact(
                metric="revenue_gap",
                value=monthly_recovery,
                currency="BRL",
                period="monthly"
            ),
            context=InsightContext(
                affected_stores=[store_id],
                data_points=int(row['orders'])
            ),
            recommendation=InsightRecommendation(
                action=(
                    f"Investigar causas da baixa performance em {store_name}: "
                    f"avaliar localização, gestão, operacional e visibilidade no delivery."
                ),
                estimated_roi=estimated_roi,
                difficulty="medium",
                link_to="/advanced"
            ),
            detected_at=datetime.now(),
            confidence_score=confidence
        )
    
    async def _detect_overperforming_store(self) -> Insight | None:
        """
        Detect: Store with revenue 30%+ above brand average
        Positive insight: Success story to replicate
        """
        store_filter = self._get_store_filter()
        
        query = f"""
            WITH store_performance AS (
                SELECT 
                    st.id,
                    st.name,
                    COALESCE(SUM(s.total_amount) FILTER (WHERE s.sale_status_desc = 'COMPLETED'), 0) as revenue,
                    COUNT(s.id) FILTER (WHERE s.sale_status_desc = 'COMPLETED') as orders,
                    COALESCE(AVG(s.total_amount) FILTER (WHERE s.sale_status_desc = 'COMPLETED'), 0) as avg_ticket
                FROM stores st
                LEFT JOIN sales s ON s.store_id = st.id 
                    AND s.created_at BETWEEN $2 AND $3
                WHERE st.brand_id = $1
                    AND st.is_active = true
                    {store_filter}
                GROUP BY st.id, st.name
            ),
            avg_metrics AS (
                SELECT 
                    AVG(revenue) as avg_revenue,
                    AVG(orders) as avg_orders,
                    AVG(avg_ticket) as avg_ticket
                FROM store_performance
            ),
            outlier_stores AS (
                SELECT 
                    sp.id,
                    sp.name,
                    sp.revenue,
                    sp.orders,
                    sp.avg_ticket as sp_avg_ticket,
                    am.avg_revenue as am_avg_revenue,
                    am.avg_orders as am_avg_orders,
                    am.avg_ticket as am_avg_ticket,
                    ((sp.revenue - am.avg_revenue) / NULLIF(am.avg_revenue, 0) * 100) as revenue_diff_pct,
                    (sp.revenue - am.avg_revenue) as revenue_surplus
                FROM store_performance sp, avg_metrics am
                WHERE am.avg_revenue > 0
                    AND ((sp.revenue - am.avg_revenue) / NULLIF(am.avg_revenue, 0) * 100) > {self.MIN_REVENUE_DIFF_PCT}
                ORDER BY revenue_diff_pct DESC
                LIMIT 1
            )
            SELECT * FROM outlier_stores
        """
        
        row = await self.db.fetch_one(
            query,
            self.brand_id,
            self.start_date,
            self.end_date
        )
        
        if not row:
            return None
        
        store_id = row['id']
        store_name = row['name']
        revenue = float(row['revenue'])
        avg_revenue = float(row['am_avg_revenue'])
        revenue_diff_pct = float(row['revenue_diff_pct'])
        revenue_surplus = float(row['revenue_surplus'])
        
        # Calculate potential if replicated
        monthly_potential = self._extrapolate_to_monthly(revenue_surplus)
        
        # Only create insight if meaningful amount
        if monthly_potential < 1000:  # Less than R$ 1,000/month
            return None
        
        # Calculate confidence
        num_stores = await self._count_active_stores()
        confidence = min(0.5 + (num_stores / 10) * 0.5, 1.0) if num_stores >= self.MIN_STORES_REQUIRED else 0.4
        
        # Estimate ROI (assuming we can replicate 40% of the advantage in other stores)
        estimated_roi = monthly_potential * 0.4
        
        return Insight(
            id=f"store_overperformer_{store_id}_{self.brand_id}",
            type="success_pattern",
            priority="positive",
            title=f"Loja {store_name[:50]} destacada: +{revenue_diff_pct:.1f}% acima da média",
            description=(
                f"A loja {store_name} tem receita de R$ {revenue:,.2f}, "
                f"R$ {revenue_surplus:,.2f} acima da média das outras lojas. "
                f"Diferença de {revenue_diff_pct:.1f}% do esperado."
            ),
            impact=InsightImpact(
                metric="revenue_potential",
                value=monthly_potential,
                currency="BRL",
                period="monthly"
            ),
            context=InsightContext(
                affected_stores=[store_id],
                data_points=int(row['orders'])
            ),
            recommendation=InsightRecommendation(
                action=(
                    f"Estudar práticas de sucesso da loja {store_name} para replicar em outras unidades: "
                    f"avaliar localização, gestão, operacional, mix de produtos e presença no delivery."
                ),
                estimated_roi=estimated_roi,
                difficulty="hard",
                link_to="/advanced"
            ),
            detected_at=datetime.now(),
            confidence_score=confidence
        )
    
    async def _count_active_stores(self) -> int:
        """Helper to count active stores for confidence calculation"""
        store_filter = self._get_store_filter()
        
        query = f"""
            SELECT COUNT(*) as total
            FROM stores st
            WHERE st.brand_id = $1
                AND st.is_active = true
                {store_filter}
        """
        
        result = await self.db.fetch_one(query, self.brand_id)
        return result['total'] if result else 0


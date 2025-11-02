"""
Detector for churn risk insights
Identifies high-value customers (VIP) who are inactive and at risk of churning
"""
from datetime import datetime, timedelta
from app.models.schemas import Insight, InsightImpact, InsightContext, InsightRecommendation
from .base_detector import BaseInsightDetector


class ChurnRiskDetector(BaseInsightDetector):
    """Detects VIP customers at risk of churning"""
    
    # Thresholds
    MIN_LTV = 1000.0  # R$ 1,000+ per year considered VIP
    MIN_INACTIVE_DAYS = 90  # 90+ days inactive is considered at risk
    MIN_RECURRENT_PURCHASES = 5  # Must have bought at least 5 times
    LTV_PERIOD_MONTHS = 12  # Calculate LTV over 12 months
    MIN_REVENUE_THRESHOLD = 2000  # Only worth if at risk revenue > R$ 2,000
    
    async def detect(self) -> list[Insight]:
        """Detect churn risk insights"""
        insights = []
        
        vip_churn_risk = await self._detect_vip_churn_risk()
        if vip_churn_risk:
            insights.append(vip_churn_risk)
        
        return insights
    
    async def _detect_vip_churn_risk(self) -> Insight | None:
        """
        Detect: VIP customers (LTV > R$ 1k/year) who haven't purchased in 30+ days
        Critical alert: High-value customers about to be lost
        """
        store_filter = self._get_store_filter()
        
        # Calculate start date for LTV calculation (12 months before current period)
        ltv_start_date = self.start_date - timedelta(days=365)
        
        query = f"""
            WITH customer_value AS (
                SELECT 
                    c.id,
                    c.customer_name as name,
                    SUM(s.total_amount) as ltv,
                    MAX(s.created_at::date) as last_purchase,
                    COUNT(s.id) as total_purchases
                FROM customers c
                INNER JOIN sales s ON s.customer_id = c.id
                INNER JOIN stores st ON s.store_id = st.id
                WHERE st.brand_id = $1
                    AND s.sale_status_desc = 'COMPLETED'
                    AND s.created_at >= $2
                    {store_filter}
                GROUP BY c.id, c.customer_name
                HAVING SUM(s.total_amount) >= $3
                    AND COUNT(s.id) >= $4
            )
            SELECT 
                COUNT(*) as at_risk_count,
                SUM(ltv) as revenue_at_risk
            FROM customer_value
            WHERE last_purchase < CURRENT_DATE - INTERVAL '{self.MIN_INACTIVE_DAYS} days'
        """
        
        row = await self.db.fetch_one(
            query,
            self.brand_id,
            ltv_start_date,
            self.MIN_LTV,
            self.MIN_RECURRENT_PURCHASES
        )
        
        if not row or not row['at_risk_count'] or row['at_risk_count'] == 0:
            return None
        
        at_risk_count = row['at_risk_count']
        revenue_at_risk = float(row['revenue_at_risk'] or 0)
        
        # Extrapolate to yearly loss (assuming they don't come back)
        yearly_loss = revenue_at_risk
        
        if revenue_at_risk < self.MIN_REVENUE_THRESHOLD:
            return None
        
        confidence = min(0.7 + (at_risk_count / 50) * 0.3, 1.0)
        
        # Estimate ROI (assuming 40% recovery rate with marketing campaign)
        estimated_roi = revenue_at_risk * 0.4
        
        return Insight(
            id=f"churn_risk_vip_{self.brand_id}",
            type="churn_risk",
            priority="critical",
            title=f"{at_risk_count} clientes VIP em risco de perca",
            description=(
                f"{at_risk_count} clientes de alto valor (gastaram R$ {self.MIN_LTV:,.0f}+ no último ano) "
                f"não compram há mais de {self.MIN_INACTIVE_DAYS} dias. "
                f"R$ {revenue_at_risk:,.2f} de receita em risco."
            ),
            impact=InsightImpact(
                metric="revenue_at_risk",
                value=revenue_at_risk,
                currency="BRL",
                period="yearly"
            ),
            context=InsightContext(
                data_points=at_risk_count
            ),
            recommendation=InsightRecommendation(
                action=(
                    f"Enviar campanha de reativação personalizada para {at_risk_count} clientes VIP: "
                    f"cupom 15% OFF 'Sentimos sua Falta'"
                ),
                estimated_roi=estimated_roi,
                difficulty="easy",
                link_to="/advanced"
            ),
            detected_at=datetime.now(),
            confidence_score=confidence
        )


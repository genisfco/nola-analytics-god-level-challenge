"""
Detector for product opportunity insights
Identifies products with high value but low sales frequency
"""
from datetime import datetime
from app.models.schemas import Insight, InsightImpact, InsightContext, InsightRecommendation
from .base_detector import BaseInsightDetector


class ProductOpportunityDetector(BaseInsightDetector):
    """Detects products that should be selling more"""
    
    # Thresholds
    MIN_AVG_PRICE = 50.0  # R$ 50+ is considered "premium"
    MAX_DAILY_SALES = 20  # Less than 20 sales/day is "underutilized"
    MIN_TOTAL_SALES = 50  # Needs at least 50 sales in the period
    MIN_REVENUE_THRESHOLD = 1000  # Only worth if ROI > R$ 1,000/month
    
    async def detect(self) -> list[Insight]:
        """Detect product opportunity insights"""
        insights = []
        
        opportunity = await self._detect_underperforming_premium_product()
        if opportunity:
            insights.append(opportunity)
        
        return insights
    
    async def _detect_underperforming_premium_product(self) -> Insight | None:
        """
        Detect: Premium products that sell little
        Opportunity: Highlight more, create combos, adjust pricing
        """
        store_filter = self._get_store_filter()
        
        query = f"""
            WITH product_stats AS (
                SELECT 
                    p.id,
                    p.name,
                    c.name as category_name,
                    AVG(ps.base_price) as avg_price,
                    COUNT(ps.id) as total_sales,
                    COUNT(DISTINCT ps.sale_id) as times_sold,
                    SUM(ps.total_price) as total_revenue,
                    COUNT(ps.id)::float / {self.period_days} as avg_daily_sales,
                    AVG(ps.base_price) * COUNT(ps.id)::float / {self.period_days} as daily_revenue_potential
                FROM products p
                INNER JOIN product_sales ps ON ps.product_id = p.id
                INNER JOIN sales s ON ps.sale_id = s.id
                INNER JOIN stores st ON s.store_id = st.id
                LEFT JOIN categories c ON c.id = p.category_id
                WHERE st.brand_id = $1
                    AND s.created_at >= $2
                    AND s.created_at <= $3
                    {store_filter}
                GROUP BY p.id, p.name, c.name
                HAVING AVG(ps.base_price) >= $4
                    AND COUNT(ps.id) >= $5
            )
            SELECT * FROM product_stats
            WHERE avg_daily_sales <= $6
            ORDER BY daily_revenue_potential DESC, avg_price DESC
            LIMIT 1
        """
        
        row = await self.db.fetch_one(
            query,
            self.brand_id,
            self.start_date,
            self.end_date,
            self.MIN_AVG_PRICE,
            self.MIN_TOTAL_SALES,
            self.MAX_DAILY_SALES
        )
        
        if not row:
            return None
        
        product_id = row['id']
        product_name = row['name']
        category = row['category_name']
        avg_price = float(row['avg_price'])
        total_sales = row['total_sales']
        avg_daily_sales = row['avg_daily_sales']
        
        # Calculate potential monthly additional revenue
        # Assuming we can increase sales by 50% (e.g., highlight on menu)
        potential_increase = avg_daily_sales * 0.5  # +50% sales
        monthly_additional_revenue = potential_increase * avg_price * 30
        
        # Estimated ROI (considering discount or marketing action)
        # Assuming 70% net margin
        estimated_roi = monthly_additional_revenue * 0.7
        
        if estimated_roi < self.MIN_REVENUE_THRESHOLD:
            return None
        
        confidence = min(0.5 + (total_sales / 200) * 0.5, 1.0)
        
        return Insight(
            id=f"product_opportunity_{product_id}_{self.brand_id}",
            type="opportunity",
            priority="attention",
            title=f"Produto premium sub-utilizado: {product_name[:50]}",
            description=(
                f"Produto de R$ {avg_price:.2f} vende apenas {avg_daily_sales:.1f}x/dia. "
                f"Com {total_sales} vendas no período, há espaço para crescimento."
            ),
            impact=InsightImpact(
                metric="revenue_opportunity",
                value=monthly_additional_revenue,
                currency="BRL",
                period="monthly"
            ),
            context=InsightContext(
                affected_products=[product_id],
                data_points=total_sales
            ),
            recommendation=InsightRecommendation(
                action=(
                    f"Criar combo ou destaque especial no delivery "
                    f"para aumentar vendas de {product_name[:40]}"
                ),
                estimated_roi=estimated_roi,
                difficulty="easy",
                link_to="/advanced?tab=products"
            ),
            detected_at=datetime.now(),
            confidence_score=confidence
        )


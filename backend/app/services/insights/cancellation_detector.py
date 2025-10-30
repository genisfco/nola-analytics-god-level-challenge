"""
Detector for cancellation-related insights
Focuses on identifying patterns of cancelled orders and revenue loss
"""
from datetime import datetime
from app.models.schemas import Insight, InsightImpact, InsightContext, InsightRecommendation
from .base_detector import BaseInsightDetector


class CancellationDetector(BaseInsightDetector):
    """Detects high cancellation rates and patterns"""
    
    # Thresholds
    MIN_CANCELLATION_RATE = 5.0  # 5% cancellation rate triggers alert  
    MIN_DATA_POINTS = 15  # Minimum orders to consider a pattern significant
    HIGH_DELIVERY_TIME = 35  # Minutes - delivery time considered problematic
    
    async def detect(self) -> list[Insight]:
        """Detect cancellation-related insights"""
        insights = []
        
        # 1. Check for high cancellation rates by context (store, channel, day, hour)
        cancellation_pattern = await self._detect_cancellation_patterns()
        if cancellation_pattern:
            insights.append(cancellation_pattern)
        
        # 2. Check overall cancellation trend
        overall_cancellation = await self._detect_overall_cancellation()
        if overall_cancellation:
            insights.append(overall_cancellation)
        
        return insights
    
    async def _detect_cancellation_patterns(self) -> Insight | None:
        """
        Detect specific patterns of cancellations by context:
        - Day of week
        - Hour
        - Store
        - Channel
        """
        store_filter = ""
        if self.store_ids:
            store_list = ", ".join(map(str, self.store_ids))
            store_filter = f"AND s.store_id IN ({store_list})"
        
        query = f"""
            WITH cancellation_analysis AS (
                SELECT 
                    s.store_id,
                    st.name as store_name,
                    s.channel_id,
                    ch.name as channel_name,
                    EXTRACT(DOW FROM s.created_at)::int as weekday,
                    EXTRACT(HOUR FROM s.created_at)::int as hour,
                    COUNT(*) as total_orders,
                    COUNT(*) FILTER (WHERE s.sale_status_desc IN ('CANCELLED', 'CANCELED')) as cancelled_orders,
                    COUNT(*) FILTER (WHERE s.sale_status_desc IN ('CANCELLED', 'CANCELED')) * 100.0 / NULLIF(COUNT(*), 0) as cancellation_rate,
                    SUM(s.total_amount) FILTER (WHERE s.sale_status_desc IN ('CANCELLED', 'CANCELED')) as lost_revenue,
                    AVG(s.delivery_seconds / 60.0) FILTER (WHERE s.delivery_seconds IS NOT NULL) as avg_delivery_time_min
                FROM sales s
                INNER JOIN stores st ON s.store_id = st.id
                INNER JOIN channels ch ON s.channel_id = ch.id
                WHERE st.brand_id = $1
                    AND s.created_at BETWEEN $2 AND $3
                    {store_filter}
                GROUP BY s.store_id, st.name, s.channel_id, ch.name, weekday, hour
                HAVING COUNT(*) >= $4
                    AND (
                        COUNT(*) FILTER (WHERE s.sale_status_desc IN ('CANCELLED', 'CANCELED')) * 100.0 / NULLIF(COUNT(*), 0) >= $5
                        OR AVG(s.delivery_seconds / 60.0) FILTER (WHERE s.delivery_seconds IS NOT NULL) >= $6
                    )
                ORDER BY cancellation_rate DESC, lost_revenue DESC
                LIMIT 1
            )
            SELECT * FROM cancellation_analysis
        """
        
        row = await self.db.fetch_one(
            query,
            self.brand_id,
            self.start_date,
            self.end_date,
            self.MIN_DATA_POINTS,
            self.MIN_CANCELLATION_RATE,
            self.HIGH_DELIVERY_TIME
        )
        
        if not row:
            return None
        
        # Extract data
        store_id = row['store_id']
        store_name = row['store_name']
        channel_id = row['channel_id']
        channel_name = row['channel_name']
        weekday = row['weekday']
        hour = row['hour']
        total_orders = row['total_orders']
        cancelled_orders = row['cancelled_orders']
        cancellation_rate = row['cancellation_rate']
        lost_revenue = float(row['lost_revenue'] or 0)
        avg_delivery_time = row['avg_delivery_time_min']
        
        # Extrapolate to monthly loss
        monthly_loss = self._extrapolate_to_monthly(lost_revenue)
        
        # Build context description
        weekday_name = self._format_weekday(weekday)
        hour_str = self._format_hour(hour)
        
        # Determine issue type
        is_delivery_issue = avg_delivery_time and avg_delivery_time >= self.HIGH_DELIVERY_TIME
        
        if is_delivery_issue:
            title = "Alto índice de cancelamentos por demora no delivery"
            description = (
                f"{cancelled_orders} pedidos cancelados em {store_name} "
                f"({channel_name}) com tempo médio de entrega de {avg_delivery_time:.0f} minutos. "
                f"Concentrado em {weekday_name} às {hour_str}."
            )
            recommendation_action = (
                f"Adicionar entregadores nos horários de pico: "
                f"{weekday_name} das {hour_str} às {hour+2:02d}h"
            )
        else:
            title = f"Taxa de cancelamento crítica: {cancellation_rate:.1f}%"
            description = (
                f"{cancelled_orders} de {total_orders} pedidos cancelados em {store_name} "
                f"({channel_name}). Concentrado em {weekday_name} às {hour_str}."
            )
            recommendation_action = (
                f"Investigar causa dos cancelamentos em {store_name} no horário {weekday_name} às {hour_str}"
            )
        
        # Calculate confidence based on data volume
        confidence = min(0.5 + (total_orders / 100) * 0.5, 1.0)
        
        # Estimate ROI (assuming we can recover 70% of lost revenue)
        estimated_roi = monthly_loss * 0.7
        
        return Insight(
            id=f"cancellation_pattern_{store_id}_{channel_id}_{weekday}_{hour}",
            type="performance_issue",
            priority="critical",
            title=title,
            description=description,
            impact=InsightImpact(
                metric="revenue_loss",
                value=monthly_loss,
                currency="BRL",
                period="monthly"
            ),
            context=InsightContext(
                affected_stores=[store_id],
                affected_channels=[channel_id],
                affected_days=[weekday_name],
                affected_hours=[hour],
                data_points=total_orders
            ),
            recommendation=InsightRecommendation(
                action=recommendation_action,
                estimated_roi=estimated_roi,
                difficulty="medium",
                link_to="/advanced?tab=delivery"
            ),
            detected_at=datetime.now(),
            confidence_score=confidence
        )
    
    async def _detect_overall_cancellation(self) -> Insight | None:
        """
        Detect if overall cancellation rate is high across all operations
        """
        store_filter = ""
        if self.store_ids:
            store_list = ", ".join(map(str, self.store_ids))
            store_filter = f"AND s.store_id IN ({store_list})"
        
        query = f"""
            SELECT 
                COUNT(*) as total_orders,
                COUNT(*) FILTER (WHERE sale_status_desc IN ('CANCELLED', 'CANCELED')) as cancelled_orders,
                COUNT(*) FILTER (WHERE sale_status_desc IN ('CANCELLED', 'CANCELED')) * 100.0 / NULLIF(COUNT(*), 0) as cancellation_rate,
                SUM(total_amount) FILTER (WHERE sale_status_desc IN ('CANCELLED', 'CANCELED')) as lost_revenue
            FROM sales s
            INNER JOIN stores st ON s.store_id = st.id
            WHERE st.brand_id = $1
                AND s.created_at BETWEEN $2 AND $3
                {store_filter}
        """
        
        row = await self.db.fetch_one(
            query,
            self.brand_id,
            self.start_date,
            self.end_date
        )
        
        if not row or not row['cancellation_rate'] or row['cancellation_rate'] < self.MIN_CANCELLATION_RATE:
            return None
        
        total_orders = row['total_orders']
        cancelled_orders = row['cancelled_orders']
        cancellation_rate = row['cancellation_rate']
        lost_revenue = float(row['lost_revenue'] or 0)
        monthly_loss = self._extrapolate_to_monthly(lost_revenue)
        
        # Only create insight if it's significant
        if monthly_loss < 1000:  # Less than R$ 1,000/month
            return None
        
        confidence = min(0.6 + (total_orders / 500) * 0.4, 1.0)
        estimated_roi = monthly_loss * 0.6
        
        return Insight(
            id=f"overall_cancellation_{self.brand_id}",
            type="performance_issue",
            priority="critical" if cancellation_rate > 15 else "attention",
            title=f"Taxa de cancelamento geral elevada: {cancellation_rate:.1f}%",
            description=(
                f"{cancelled_orders} pedidos cancelados de {total_orders} no período analisado. "
                f"Isso representa uma perda de R$ {lost_revenue:,.2f}."
            ),
            impact=InsightImpact(
                metric="revenue_loss",
                value=monthly_loss,
                currency="BRL",
                period="monthly"
            ),
            context=InsightContext(
                data_points=total_orders
            ),
            recommendation=InsightRecommendation(
                action="Analisar principais motivos de cancelamento e implementar melhorias operacionais",
                estimated_roi=estimated_roi,
                difficulty="medium",
                link_to="/advanced?tab=delivery"
            ),
            detected_at=datetime.now(),
            confidence_score=confidence
        )


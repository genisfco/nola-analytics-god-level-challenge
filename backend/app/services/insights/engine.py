"""
Main Insights Engine - orchestrates all insight detectors
"""
from datetime import date, datetime
from typing import Optional
from app.core.database import Database
from app.models.schemas import Insight, InsightsResponse

from .cancellation_detector import CancellationDetector
from .product_opportunity_detector import ProductOpportunityDetector


class InsightsEngine:
    """
    Main engine for generating insights from analytics data.
    Orchestrates multiple detectors and prioritizes results.
    """
    
    def __init__(self, db: Database):
        self.db = db
    
    async def generate_insights(
        self,
        brand_id: int,
        start_date: date,
        end_date: date,
        store_ids: Optional[list[int]] = None,
        limit: int = 5
    ) -> InsightsResponse:
        """
        Generate insights by running all detectors and prioritizing results.
        
        Args:
            brand_id: Brand ID to analyze
            start_date: Start date for analysis period
            end_date: End date for analysis period
            store_ids: Optional list of store IDs to filter
            limit: Maximum number of insights to return
            
        Returns:
            InsightsResponse with prioritized insights
        """
        all_insights: list[Insight] = []
        
        # 1. Run all detectors
        detectors = [
            CancellationDetector(self.db, brand_id, start_date, end_date, store_ids),
            ProductOpportunityDetector(self.db, brand_id, start_date, end_date, store_ids),
            # Add more detectors here in future:
            # ChurnRiskDetector(...),
            # etc.
        ]
        
        for detector in detectors:
            try:
                insights = await detector.detect()
                all_insights.extend(insights)
            except Exception as e:
                # Log error but don't fail entire insight generation
                print(f"Error in {detector.__class__.__name__}: {str(e)}")
                continue
        
        # 2. Score and prioritize insights
        scored_insights = self._score_insights(all_insights)
        
        # 3. Sort by priority and score
        sorted_insights = sorted(
            scored_insights,
            key=lambda x: (
                self._priority_value(x.priority),  # Critical > Attention > Positive
                -x.impact.value,  # Higher impact first
                -x.confidence_score  # Higher confidence first
            ),
            reverse=True
        )
        
        # 4. Limit results
        top_insights = sorted_insights[:limit]
        
        # 5. Build response
        period_days = (end_date - start_date).days + 1
        
        return InsightsResponse(
            insights=top_insights,
            total=len(top_insights),
            generated_at=datetime.now(),
            period={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": period_days
            }
        )
    
    def _score_insights(self, insights: list[Insight]) -> list[Insight]:
        """
        Calculate priority score for each insight.
        Score is already incorporated in sorting, but this can be extended
        for more complex scoring logic.
        """
        # For now, insights are already well-structured
        # Future: Add ML-based scoring, user feedback, etc.
        return insights
    
    def _priority_value(self, priority: str) -> int:
        """Convert priority string to numeric value for sorting"""
        priority_map = {
            "critical": 3,
            "attention": 2,
            "positive": 1
        }
        return priority_map.get(priority.lower(), 0)


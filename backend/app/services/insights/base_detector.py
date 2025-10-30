"""
Base class for insight detectors
"""
from abc import ABC, abstractmethod
from typing import Optional
from datetime import date
from app.core.database import Database
from app.models.schemas import Insight


class BaseInsightDetector(ABC):
    """Base class for all insight detectors"""
    
    def __init__(self, db: Database, brand_id: int, start_date: date, end_date: date, store_ids: Optional[list[int]] = None):
        self.db = db
        self.brand_id = brand_id
        self.start_date = start_date
        self.end_date = end_date
        self.store_ids = store_ids
        self.period_days = (end_date - start_date).days + 1
    
    @abstractmethod
    async def detect(self) -> list[Insight]:
        """
        Detect insights based on data analysis.
        Must be implemented by each detector.
        
        Returns:
            List of detected insights
        """
        pass
    
    def _get_store_filter(self) -> str:
        """Helper to generate SQL filter for stores"""
        if self.store_ids:
            store_list = ", ".join(map(str, self.store_ids))
            return f"AND s.store_id IN ({store_list})"
        return ""
    
    def _extrapolate_to_monthly(self, value: float) -> float:
        """Extrapolate a value from current period to monthly"""
        if self.period_days == 0:
            return 0
        return (value / self.period_days) * 30
    
    def _format_weekday(self, dow: int) -> str:
        """Convert day of week number to Portuguese name"""
        weekdays = {
            0: "domingo",
            1: "segunda-feira",
            2: "terça-feira",
            3: "quarta-feira",
            4: "quinta-feira",
            5: "sexta-feira",
            6: "sábado"
        }
        return weekdays.get(dow, "desconhecido")
    
    def _format_hour(self, hour: int) -> str:
        """Format hour for display"""
        return f"{hour:02d}h"


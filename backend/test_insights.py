"""
Quick test script for insights endpoint
"""
import asyncio
import sys
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Add app to path
sys.path.insert(0, 'app')

from app.services.insights import InsightsEngine
from app.core.config import settings


async def test_insights():
    """Test insights generation"""
    print("🔍 Testing Insights Engine...")
    print(f"Database URL: {settings.DATABASE_URL}")
    
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://'),
        echo=False
    )
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Create insights engine
        insights_engine = InsightsEngine(session)
        
        # Generate insights
        print("\n📊 Generating insights for May 2024...")
        result = await insights_engine.generate_insights(
            brand_id=1,
            start_date=date(2024, 5, 1),
            end_date=date(2024, 5, 31),
            store_ids=None,
            limit=5
        )
        
        print(f"\n✅ Found {result.total} insights!\n")
        
        if result.insights:
            for i, insight in enumerate(result.insights, 1):
                print(f"{i}. [{insight.priority.upper()}] {insight.title}")
                print(f"   📝 {insight.description}")
                print(f"   💰 Impacto: R$ {insight.impact.value:,.2f}/{insight.impact.period}")
                if insight.recommendation.estimated_roi:
                    print(f"   📈 ROI Estimado: R$ {insight.recommendation.estimated_roi:,.2f}")
                print(f"   💡 Ação: {insight.recommendation.action}")
                print()
        else:
            print("✨ Nenhum insight crítico detectado - tudo OK!")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_insights())


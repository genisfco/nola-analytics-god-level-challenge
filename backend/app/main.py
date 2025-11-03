"""
FastAPI application entrypoint
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import db
from app.api.routes import analytics, analytics_advanced, insights
# from app.api.routes import sales, products


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await db.connect()
    print("✅ Database connected")
    
    yield
    
    # Shutdown
    await db.disconnect()
    print("👋 Database disconnected")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
# Parse CORS_ORIGINS string (comma-separated) into list
cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Restaurant Analytics API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected" if db.pool else "disconnected"
    }


# Include routers
app.include_router(analytics.router, prefix=f"{settings.API_V1_PREFIX}/analytics", tags=["Analytics"])
app.include_router(analytics_advanced.router, prefix=f"{settings.API_V1_PREFIX}/analytics", tags=["Analytics Advanced"])
app.include_router(insights.router, prefix=f"{settings.API_V1_PREFIX}/analytics/insights", tags=["Insights"])
# app.include_router(sales.router, prefix=f"{settings.API_V1_PREFIX}/sales", tags=["Sales"])
# app.include_router(products.router, prefix=f"{settings.API_V1_PREFIX}/products", tags=["Products"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


"""
Database connection and session management
"""
import asyncpg
from typing import AsyncGenerator
from .config import settings


class Database:
    """Database connection pool manager"""
    
    def __init__(self):
        self.pool: asyncpg.Pool | None = None
    
    async def connect(self):
        """Create database connection pool"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                dsn=settings.DATABASE_URL,
                min_size=5,
                max_size=settings.DB_POOL_SIZE,
                command_timeout=60,
            )
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    async def fetch_one(self, query: str, *args):
        """Fetch single row"""
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)
    
    async def fetch_all(self, query: str, *args):
        """Fetch all rows"""
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)
    
    async def execute(self, query: str, *args):
        """Execute query"""
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)


# Global database instance
db = Database()


async def get_db() -> Database:
    """Dependency for getting database instance"""
    return db


"""
Redis cache manager
"""
import redis.asyncio as redis
import json
from typing import Any
from .config import settings


class CacheManager:
    """Redis cache manager"""
    
    def __init__(self):
        self.redis: redis.Redis | None = None
    
    async def connect(self):
        """Connect to Redis"""
        if not self.redis:
            self.redis = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
            self.redis = None
    
    async def get(self, key: str) -> Any | None:
        """Get value from cache"""
        if not self.redis:
            return None
        
        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = settings.CACHE_TTL
    ):
        """Set value in cache with TTL"""
        if not self.redis:
            return
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        await self.redis.set(key, value, ex=ttl)
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if self.redis:
            await self.redis.delete(key)
    
    async def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern"""
        if not self.redis:
            return
        
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)


# Global cache instance
cache = CacheManager()


async def get_cache() -> CacheManager:
    """Dependency for getting cache instance"""
    return cache


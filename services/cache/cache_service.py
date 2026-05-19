import redis
import json
import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self, host: str = None, port: int = None, db: int = 0):
        # Utiliser variables d'environnement ou fallback défaut
        host = host or os.getenv("REDIS_HOST", "localhost")
        port = port or int(os.getenv("REDIS_PORT", 6379))
        
        try:
            self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            self.redis.ping()  # Test connection
            logger.info(f"Redis cache connected successfully ({host}:{port})")
        except redis.ConnectionError as e:
            logger.warning(f"Redis not available ({e}), using in-memory fallback")
            self.redis = None
            self.memory_cache = {}

    def get(self, key: str) -> Optional[Any]:
        if self.redis:
            try:
                data = self.redis.get(key)
                return json.loads(data) if data else None
            except Exception as e:
                logger.error(f"Redis get error: {e}")
                return None
        else:
            return self.memory_cache.get(key)

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        try:
            data = json.dumps(value)
            if self.redis:
                return self.redis.setex(key, ttl, data)
            else:
                self.memory_cache[key] = value
                return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        if self.redis:
            try:
                return self.redis.delete(key) > 0
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
                return False
        else:
            return self.memory_cache.pop(key, None) is not None
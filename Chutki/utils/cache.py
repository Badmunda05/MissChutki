"""
Memory-only cache (L1) — Redis hataya gaya, MongoDB persistent storage hai
"""
import time
import asyncio
from typing import Any, Dict, Optional, Callable
from functools import wraps
from Chutki import LOGGER


class MultiLevelCache:
    def __init__(self, default_ttl: int = 300):
        self._l1_cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = default_ttl
        self._running = False

    async def start(self):
        if self._running:
            return
        self._running = True
        LOGGER.info("Cache started (memory-only mode).")

    async def stop(self):
        self._running = False
        self._l1_cache.clear()
        LOGGER.info("Cache stopped.")

    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        return time.time() > entry["expires"]

    async def get(self, key: str) -> Optional[Any]:
        if key in self._l1_cache:
            entry = self._l1_cache[key]
            if not self._is_expired(entry):
                return entry["value"]
            else:
                del self._l1_cache[key]
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if ttl is None:
            ttl = self._default_ttl
        self._l1_cache[key] = {
            "value": value,
            "expires": time.time() + ttl
        }

    async def delete(self, key: str) -> None:
        if key in self._l1_cache:
            del self._l1_cache[key]

    async def clear(self) -> None:
        self._l1_cache.clear()

    def cleanup_expired(self) -> None:
        """Remove expired entries from cache"""
        expired_keys = [
            key for key, entry in self._l1_cache.items()
            if self._is_expired(entry)
        ]
        for key in expired_keys:
            del self._l1_cache[key]


# --- Cache instances (Redis parameters hata ditte) ---
locks_cache = MultiLevelCache(default_ttl=120)
admin_cache = MultiLevelCache(default_ttl=300)
blocklist_cache = MultiLevelCache(default_ttl=180)
anonymous_admin_cache = MultiLevelCache(default_ttl=300)
approvals_cache = MultiLevelCache(default_ttl=180)


class SimpleCache(MultiLevelCache):
    def __init__(self, default_ttl: int = 300):
        super().__init__(default_ttl)


def cached_db_call(cache_instance: MultiLevelCache, ttl: Optional[int] = None):
    """
    Decorator for caching database calls
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"

            cached_result = await cache_instance.get(cache_key)
            if cached_result is not None:
                return cached_result

            result = await func(*args, **kwargs)
            await cache_instance.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator


async def start_cache_cleanup():
    """Start periodic cache cleanup task"""
    await locks_cache.start()
    await admin_cache.start()
    await blocklist_cache.start()
    await anonymous_admin_cache.start()
    await approvals_cache.start()

    while True:
        try:
            locks_cache.cleanup_expired()
            admin_cache.cleanup_expired()
            blocklist_cache.cleanup_expired()
            anonymous_admin_cache.cleanup_expired()
            approvals_cache.cleanup_expired()
        except Exception as e:
            LOGGER.error(f"Error during cache cleanup: {e}")

        await asyncio.sleep(60)
        

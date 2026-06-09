import time
import asyncio
from typing import Any, Dict, List, Optional


class _Pipeline:
    """Redis pipeline da simple replacement"""
    def __init__(self, store: "MemoryStore"):
        self._store = store
        self._commands = []

    def zremrangebyscore(self, key: str, min_score: float, max_score: float):
        self._commands.append(("zremrangebyscore", key, min_score, max_score))
        return self

    def zrange(self, key: str, start: int, end: int):
        self._commands.append(("zrange", key, start, end))
        return self

    def zadd(self, key: str, mapping: Dict[str, float]):
        self._commands.append(("zadd", key, mapping))
        return self

    def expire(self, key: str, seconds: int):
        self._commands.append(("expire", key, seconds))
        return self

    async def execute(self) -> List[Any]:
        results = []
        for cmd in self._commands:
            op = cmd[0]
            if op == "zremrangebyscore":
                _, key, mn, mx = cmd
                results.append(await self._store.zremrangebyscore(key, mn, mx))
            elif op == "zrange":
                _, key, start, end = cmd
                results.append(await self._store.zrange(key, start, end))
            elif op == "zadd":
                _, key, mapping = cmd
                results.append(await self._store.zadd(key, mapping))
            elif op == "expire":
                _, key, seconds = cmd
                results.append(await self._store.expire(key, seconds))
            else:
                results.append(None)
        return results


class MemoryStore:
    """
    Redis asyncio client da drop-in replacement.
    Sorted sets, strings, expiry sab support karda hai.
    """

    def __init__(self):
        # Plain key-value store: key -> (value, expires_at or None)
        self._kv: Dict[str, Any] = {}
        self._kv_expiry: Dict[str, float] = {}

        # Sorted sets: key -> {member: score}
        self._zsets: Dict[str, Dict[str, float]] = {}
        self._zset_expiry: Dict[str, float] = {}

    # ── Internal helpers ──────────────────────────────────────────────

    def _kv_expired(self, key: str) -> bool:
        exp = self._kv_expiry.get(key)
        return exp is not None and time.time() > exp

    def _zset_expired(self, key: str) -> bool:
        exp = self._zset_expiry.get(key)
        return exp is not None and time.time() > exp

    def _clean_kv(self, key: str):
        if self._kv_expired(key):
            self._kv.pop(key, None)
            self._kv_expiry.pop(key, None)

    def _clean_zset(self, key: str):
        if self._zset_expired(key):
            self._zsets.pop(key, None)
            self._zset_expiry.pop(key, None)

    # ── String ops ───────────────────────────────────────────────────

    async def get(self, key: str) -> Optional[str]:
        self._clean_kv(key)
        return self._kv.get(key)

    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        self._kv[key] = str(value)
        if ex is not None:
            self._kv_expiry[key] = time.time() + ex
        else:
            self._kv_expiry.pop(key, None)
        return True

    async def delete(self, *keys: str) -> int:
        count = 0
        for key in keys:
            if key in self._kv:
                del self._kv[key]
                self._kv_expiry.pop(key, None)
                count += 1
            if key in self._zsets:
                del self._zsets[key]
                self._zset_expiry.pop(key, None)
                count += 1
        return count

    async def expire(self, key: str, seconds: int) -> bool:
        exp_at = time.time() + seconds
        if key in self._kv:
            self._kv_expiry[key] = exp_at
            return True
        if key in self._zsets:
            self._zset_expiry[key] = exp_at
            return True
        return False

    async def incr(self, key: str) -> int:
        self._clean_kv(key)
        val = int(self._kv.get(key, 0)) + 1
        self._kv[key] = str(val)
        return val

    async def ping(self) -> bool:
        return True

    async def close(self):
        pass

    # ── Sorted set ops ───────────────────────────────────────────────

    async def zadd(self, key: str, mapping: Dict[str, float]) -> int:
        self._clean_zset(key)
        if key not in self._zsets:
            self._zsets[key] = {}
        added = 0
        for member, score in mapping.items():
            if member not in self._zsets[key]:
                added += 1
            self._zsets[key][member] = score
        return added

    async def zremrangebyscore(self, key: str, min_score: float, max_score: float) -> int:
        self._clean_zset(key)
        if key not in self._zsets:
            return 0
        to_remove = [m for m, s in self._zsets[key].items() if min_score <= s <= max_score]
        for m in to_remove:
            del self._zsets[key][m]
        return len(to_remove)

    async def zrange(self, key: str, start: int, end: int) -> List[str]:
        self._clean_zset(key)
        if key not in self._zsets:
            return []
        sorted_members = sorted(self._zsets[key].items(), key=lambda x: x[1])
        members = [m for m, _ in sorted_members]
        if end == -1:
            return members[start:]
        return members[start:end + 1]

    async def zcount(self, key: str, min_score: float, max_score) -> int:
        self._clean_zset(key)
        if key not in self._zsets:
            return 0
        max_s = float("inf") if max_score == "+inf" else float(max_score)
        return sum(1 for s in self._zsets[key].values() if min_score <= s <= max_s)

    async def zcard(self, key: str) -> int:
        self._clean_zset(key)
        return len(self._zsets.get(key, {}))

    async def flushdb(self):
        self._kv.clear()
        self._kv_expiry.clear()
        self._zsets.clear()
        self._zset_expiry.clear()

    async def publish(self, channel: str, message: str):
        pass  # No pub/sub needed in memory-only mode

    def pubsub(self):
        return _FakePubSub()

    def pipeline(self) -> _Pipeline:
        return _Pipeline(self)


class _FakePubSub:
    async def subscribe(self, *args):
        pass

    async def listen(self):
        # Yield nothing — no cross-instance invalidation needed
        while False:
            yield {}
              

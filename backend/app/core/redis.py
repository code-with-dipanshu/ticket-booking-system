from __future__ import annotations

import logging
import threading
import time
from typing import Any, Dict, Optional, Tuple

try:
    import redis as redis_client_module
except Exception:  # pragma: no cover - package is optional in local/dev mode
    redis_client_module = None

logger = logging.getLogger(__name__)


class _MemorySeatHoldStore:
    """Shared in-memory TTL store used as a Redis fallback for local testing."""

    _shared_state: Dict[str, Tuple[str, float]] = {}
    _lock = threading.RLock()

    def clear(self) -> None:
        with self._lock:
            self._shared_state.clear()

    def hold(self, key: str, value: str, ttl_seconds: int = 60) -> bool:
        now = time.time()
        with self._lock:
            existing = self._shared_state.get(key)
            if existing is not None and existing[1] > now:
                return False

            if existing is not None and existing[1] <= now:
                self._shared_state.pop(key, None)

            self._shared_state[key] = (value, now + ttl_seconds)
            return True

    def is_held(self, key: str) -> bool:
        now = time.time()
        with self._lock:
            existing = self._shared_state.get(key)
            if existing is None:
                return False

            if existing[1] <= now:
                self._shared_state.pop(key, None)
                return False

            return True

    def release(self, key: str) -> bool:
        with self._lock:
            return self._shared_state.pop(key, None) is not None


class SeatHoldStore:
    """Redis-backed seat hold wrapper with a shared in-memory fallback for local runs."""

    _fallback_store = _MemorySeatHoldStore()

    def __init__(self, redis_client: Optional[Any] = None):
        self._fallback_store = self._fallback_store
        self.redis_client = redis_client

        if self.redis_client is None and redis_client_module is not None:
            try:
                self.redis_client = redis_client_module.Redis(
                    host="localhost",
                    port=6379,
                    db=0,
                    decode_responses=True,
                )
                self.redis_client.ping()
            except Exception as exc:
                logger.warning(
                    "Redis server is unavailable. Falling back to in-memory seat holds: %s",
                    exc,
                )
                self.redis_client = None

        if self.redis_client is None and redis_client_module is None:
            logger.warning(
                "Redis client dependency is not installed. Falling back to in-memory seat holds."
            )

    def clear(self) -> None:
        """Reset the shared in-memory fallback store between isolated test runs."""
        self._fallback_store.clear()

    def hold(self, key: str, value: str, ttl_seconds: int = 60) -> bool:
        """Create a time-limited hold for a seat-related inventory key."""
        if self.redis_client is not None:
            try:
                return bool(self.redis_client.set(key, value, ex=ttl_seconds, nx=True))
            except Exception as exc:
                logger.warning(
                    "Redis hold write failed; using in-memory fallback: %s", exc
                )
                self.redis_client = None

        return self._fallback_store.hold(key, value, ttl_seconds)

    def is_held(self, key: str) -> bool:
        """Return whether the seat hold still exists and has not expired."""
        if self.redis_client is not None:
            try:
                return self.redis_client.exists(key) == 1
            except Exception as exc:
                logger.warning(
                    "Redis hold existence check failed; using in-memory fallback: %s",
                    exc,
                )
                self.redis_client = None

        return self._fallback_store.is_held(key)

    def release(self, key: str) -> bool:
        """Delete the hold from Redis or the fallback store."""
        if self.redis_client is not None:
            try:
                return bool(self.redis_client.delete(key))
            except Exception as exc:
                logger.warning(
                    "Redis hold release failed; using in-memory fallback: %s", exc
                )
                self.redis_client = None

        return self._fallback_store.release(key)

from typing import Any, Dict, Optional, List
from functools import wraps
from datetime import datetime, timedelta
import json
from pathlib import Path
from modules.utils import get_logger

logger = get_logger(__name__)

class Cache:
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, tuple] = {}
        self.access_count: Dict[str, int] = {}
        self.hit_count = 0
        self.miss_count = 0

    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            self.miss_count += 1
            return None

        value, timestamp = self.cache[key]

        if datetime.now() - timestamp > timedelta(seconds=self.ttl_seconds):
            del self.cache[key]
            self.miss_count += 1
            return None

        self.hit_count += 1
        self.access_count[key] = self.access_count.get(key, 0) + 1
        return value

    def set(self, key: str, value: Any):
        if len(self.cache) >= self.max_size:
            self._evict_lru()

        self.cache[key] = (value, datetime.now())

    def delete(self, key: str):
        if key in self.cache:
            del self.cache[key]
            if key in self.access_count:
                del self.access_count[key]

    def clear(self):
        self.cache.clear()
        self.access_count.clear()
        self.hit_count = 0
        self.miss_count = 0

    def _evict_lru(self):
        if not self.access_count:
            lru_key = list(self.cache.keys())[0]
        else:
            lru_key = min(self.access_count, key=self.access_count.get)

        self.delete(lru_key)
        logger.debug(f"Evicted LRU key: {lru_key}")

    def get_stats(self) -> Dict[str, Any]:
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "ttl_seconds": self.ttl_seconds
        }

class QueryCache(Cache):
    def __init__(self, cache_dir: str = "cache/queries", max_size: int = 500, ttl_seconds: int = 86400):
        super().__init__(max_size, ttl_seconds)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._load_persistent_cache()

    def _load_persistent_cache(self):
        try:
            cache_file = self.cache_dir / "query_cache.json"
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        self.cache[key] = (value, datetime.now())
                logger.info(f"Loaded {len(self.cache)} queries from cache")
        except Exception as e:
            logger.warning(f"Error loading persistent cache: {e}")

    def _save_persistent_cache(self):
        try:
            cache_file = self.cache_dir / "query_cache.json"
            cache_data = {k: v[0] for k, v in self.cache.items() if isinstance(v[0], (dict, str, list))}

            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            logger.warning(f"Error saving persistent cache: {e}")

    def set(self, key: str, value: Any):
        super().set(key, value)
        if len(self.cache) % 10 == 0:
            self._save_persistent_cache()

class EmbeddingCache(Cache):
    def __init__(self, cache_dir: str = "cache/embeddings", max_size: int = 10000):
        super().__init__(max_size, ttl_seconds=2592000)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_batch(self, keys: List[str]) -> Dict[str, Any]:
        results = {}
        for key in keys:
            value = self.get(key)
            if value:
                results[key] = value

        return results

    def set_batch(self, items: Dict[str, Any]):
        for key, value in items.items():
            self.set(key, value)

class CachedFunction:
    def __init__(self, cache: Cache, key_prefix: str = ""):
        self.cache = cache
        self.key_prefix = key_prefix

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = self._make_key(func.__name__, args, kwargs)

            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result

            result = func(*args, **kwargs)
            self.cache.set(cache_key, result)
            return result

        return wrapper

    def _make_key(self, func_name: str, args, kwargs) -> str:
        key_parts = [self.key_prefix, func_name]

        for arg in args[:3]:
            if isinstance(arg, (str, int, float)):
                key_parts.append(str(arg)[:50])

        for k, v in sorted(kwargs.items())[:3]:
            if isinstance(v, (str, int, float)):
                key_parts.append(f"{k}={str(v)[:50]}")

        return "|".join(key_parts)

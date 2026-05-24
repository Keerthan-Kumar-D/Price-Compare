"""
Simple in-memory cache for search results
Cache expires after 5 minutes to balance performance and data freshness
"""
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import hashlib
import json

class SearchCache:
    def __init__(self, ttl_minutes: int = 5):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl = timedelta(minutes=ttl_minutes)
    
    def _generate_key(self, query: str, limit: int) -> str:
        """Generate cache key from query and limit"""
        cache_input = f"{query.lower().strip()}:{limit}"
        return hashlib.md5(cache_input.encode()).hexdigest()
    
    def get(self, query: str, limit: int) -> Optional[Dict[str, Any]]:
        """Get cached result if exists and not expired"""
        key = self._generate_key(query, limit)
        
        if key not in self._cache:
            return None
        
        cached_item = self._cache[key]
        cached_time = cached_item['cached_at']
        
        # Check if cache has expired
        if datetime.now() - cached_time > self._ttl:
            del self._cache[key]
            return None
        
        return cached_item['data']
    
    def set(self, query: str, limit: int, data: Dict[str, Any]) -> None:
        """Store result in cache"""
        key = self._generate_key(query, limit)
        self._cache[key] = {
            'data': data,
            'cached_at': datetime.now()
        }
    
    def clear(self) -> None:
        """Clear all cached items"""
        self._cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        now = datetime.now()
        valid_items = sum(
            1 for item in self._cache.values()
            if now - item['cached_at'] <= self._ttl
        )
        
        return {
            'total_items': len(self._cache),
            'valid_items': valid_items,
            'ttl_minutes': self._ttl.total_seconds() / 60
        }

# Global cache instance
search_cache = SearchCache(ttl_minutes=5)

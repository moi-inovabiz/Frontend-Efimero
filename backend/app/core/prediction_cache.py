"""
Sistema de cache para predicciones de Frontend Efímero.
Optimiza el rendimiento mediante cache inteligente de predicciones ML.
"""

import time
import hashlib
import json
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from threading import Lock
import weakref

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Entrada individual del cache con metadatos."""
    data: Dict[str, Any]
    timestamp: float
    hit_count: int = 0
    ttl_seconds: int = 300  # 5 minutos por defecto
    size_bytes: int = 0
    
    def is_expired(self) -> bool:
        """Verifica si la entrada ha expirado."""
        return time.time() - self.timestamp > self.ttl_seconds
    
    def touch(self) -> None:
        """Actualiza el contador de hits y timestamp de acceso."""
        self.hit_count += 1


@dataclass
class CacheStats:
    """Estadísticas del cache para monitoreo."""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    expired_entries: int = 0
    evicted_entries: int = 0
    current_size: int = 0
    max_size: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Tasa de aciertos del cache."""
        if self.total_requests == 0:
            return 0.0
        return self.cache_hits / self.total_requests
    
    @property
    def miss_rate(self) -> float:
        """Tasa de fallos del cache."""
        return 1.0 - self.hit_rate


class PredictionCache:
    """
    Cache inteligente para predicciones ML con TTL y LRU eviction.
    
    Características:
    - TTL configurable por tipo de predicción
    - Límites de tamaño en memoria
    - Estadísticas detalladas para monitoreo
    - Keys basados en hash de contexto del usuario
    - Thread-safe para uso concurrente
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 300,  # 5 minutos
        max_memory_mb: int = 50   # 50MB máximo
    ):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        
        # Storage interno
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order: Dict[str, float] = {}  # Para LRU
        self._lock = Lock()
        
        # Estadísticas
        self.stats = CacheStats(max_size=max_size)
        
        logger.info(f"✅ PredictionCache inicializado: max_size={max_size}, ttl={default_ttl}s, max_memory={max_memory_mb}MB")
    
    
    def _generate_cache_key(
        self, 
        user_context: Any, 
        is_authenticated: bool = False,
        additional_context: Optional[Dict] = None
    ) -> str:
        """
        Genera una clave de cache única basada en el contexto del usuario.
        """
        try:
            # Extraer atributos clave del contexto del usuario
            context_data = {
                'viewport_width': getattr(user_context, 'viewport_width', 0),
                'viewport_height': getattr(user_context, 'viewport_height', 0),
                'prefers_color_scheme': getattr(user_context, 'prefers_color_scheme', 'light'),
                'touch_enabled': getattr(user_context, 'touch_enabled', False),
                'device_pixel_ratio': getattr(user_context, 'device_pixel_ratio', 1.0),
                'is_authenticated': is_authenticated,
                'hour_of_day': getattr(user_context, 'hora_local', datetime.now()).hour
            }
            
            # Agregar contexto adicional si se proporciona
            if additional_context:
                context_data.update(additional_context)
            
            # Generar hash estable
            context_json = json.dumps(context_data, sort_keys=True)
            cache_key = hashlib.md5(context_json.encode()).hexdigest()
            
            return f"pred_{cache_key}"
            
        except Exception as e:
            logger.warning(f"⚠️ Error generando cache key: {e}")
            # Fallback a timestamp para evitar colisiones
            return f"pred_fallback_{int(time.time())}"
    
    
    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Recupera una predicción del cache.
        
        Returns:
            Dict con la predicción si existe y no ha expirado, None en caso contrario
        """
        with self._lock:
            self.stats.total_requests += 1
            
            if cache_key not in self._cache:
                self.stats.cache_misses += 1
                return None
            
            entry = self._cache[cache_key]
            
            # Verificar expiración
            if entry.is_expired():
                logger.debug(f"🕐 Cache key expirado: {cache_key}")
                del self._cache[cache_key]
                if cache_key in self._access_order:
                    del self._access_order[cache_key]
                self.stats.expired_entries += 1
                self.stats.cache_misses += 1
                return None
            
            # Cache hit - actualizar estadísticas y orden de acceso
            entry.touch()
            self._access_order[cache_key] = time.time()
            self.stats.cache_hits += 1
            
            logger.debug(f"✅ Cache HIT: {cache_key} (hits: {entry.hit_count})")
            return entry.data.copy()  # Retornar copia para evitar mutaciones
    
    
    def put(
        self, 
        cache_key: str, 
        prediction_data: Dict[str, Any], 
        ttl: Optional[int] = None
    ) -> bool:
        """
        Almacena una predicción en el cache.
        
        Returns:
            True si se almacenó exitosamente, False en caso contrario
        """
        try:
            with self._lock:
                # Calcular tamaño aproximado
                data_size = len(json.dumps(prediction_data).encode())
                
                # Verificar límites de memoria
                if data_size > self.max_memory_bytes:
                    logger.warning(f"⚠️ Predicción demasiado grande para cache: {data_size} bytes")
                    return False
                
                # Evict entries si es necesario
                self._evict_if_needed(data_size)
                
                # Crear entrada
                entry = CacheEntry(
                    data=prediction_data.copy(),
                    timestamp=time.time(),
                    ttl_seconds=ttl or self.default_ttl,
                    size_bytes=data_size
                )
                
                # Almacenar
                self._cache[cache_key] = entry
                self._access_order[cache_key] = time.time()
                
                # Actualizar estadísticas
                self.stats.current_size = len(self._cache)
                
                logger.debug(f"💾 Cache PUT: {cache_key} (ttl: {entry.ttl_seconds}s, size: {data_size}b)")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error almacenando en cache: {e}")
            return False
    
    
    def _evict_if_needed(self, new_entry_size: int) -> None:
        """
        Evict entradas del cache si se exceden los límites.
        Usa estrategia LRU (Least Recently Used).
        """
        # Verificar límite de tamaño
        while len(self._cache) >= self.max_size:
            self._evict_lru()
        
        # Verificar límite de memoria
        current_memory = sum(entry.size_bytes for entry in self._cache.values())
        while current_memory + new_entry_size > self.max_memory_bytes and self._cache:
            self._evict_lru()
            current_memory = sum(entry.size_bytes for entry in self._cache.values())
    
    
    def _evict_lru(self) -> None:
        """Evict la entrada menos recientemente usada."""
        if not self._access_order:
            return
        
        # Encontrar la entrada más antigua
        oldest_key = min(self._access_order, key=self._access_order.get)
        
        # Remover
        if oldest_key in self._cache:
            del self._cache[oldest_key]
        del self._access_order[oldest_key]
        
        self.stats.evicted_entries += 1
        self.stats.current_size = len(self._cache)
        
        logger.debug(f"🗑️ Cache EVICT (LRU): {oldest_key}")
    
    
    def clear(self) -> None:
        """Limpia todo el cache."""
        with self._lock:
            cleared_count = len(self._cache)
            self._cache.clear()
            self._access_order.clear()
            self.stats.current_size = 0
            
            logger.info(f"🧹 Cache limpiado: {cleared_count} entradas removidas")
    
    
    def cleanup_expired(self) -> int:
        """
        Limpia entradas expiradas del cache de manera eficiente.
        
        Returns:
            Número de entradas removidas
        """
        try:
            # Usar timeout para evitar bloqueos
            if not self._lock.acquire(timeout=0.5):
                logger.debug("⚠️ No se pudo obtener lock para cleanup, saltando")
                return 0
            
            try:
                expired_keys = [
                    key for key, entry in self._cache.items() 
                    if entry.is_expired()
                ]
                
                for key in expired_keys:
                    del self._cache[key]
                    if key in self._access_order:
                        del self._access_order[key]
                    self.stats.expired_entries += 1
                
                self.stats.current_size = len(self._cache)
                
                if expired_keys:
                    logger.debug(f"🧹 Limpieza automática: {len(expired_keys)} entradas expiradas removidas")
                
                return len(expired_keys)
                
            finally:
                self._lock.release()
                
        except Exception as e:
            logger.error(f"❌ Error en cleanup_expired: {e}")
            return 0
    
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas detalladas del cache de manera eficiente."""
        try:
            # Usar timeout en el lock para evitar bloqueos indefinidos
            if not self._lock.acquire(timeout=1.0):
                logger.warning("⚠️ Timeout obteniendo stats del cache, retornando estadísticas básicas")
                return self._get_basic_stats()
            
            try:
                # No hacer cleanup automático aquí para evitar latencia
                current_memory = sum(entry.size_bytes for entry in self._cache.values())
                active_entries = sum(1 for entry in self._cache.values() if not entry.is_expired())
                
                return {
                    "cache_stats": asdict(self.stats),
                    "memory_usage": {
                        "current_bytes": current_memory,
                        "current_mb": round(current_memory / (1024 * 1024), 2),
                        "max_mb": round(self.max_memory_bytes / (1024 * 1024), 2),
                        "utilization_percent": round((current_memory / self.max_memory_bytes) * 100, 1)
                    },
                    "cache_efficiency": {
                        "hit_rate_percent": round(self.stats.hit_rate * 100, 1),
                        "miss_rate_percent": round(self.stats.miss_rate * 100, 1),
                        "avg_hits_per_entry": round(
                            sum(entry.hit_count for entry in self._cache.values()) / max(len(self._cache), 1), 1
                        ),
                        "active_entries": active_entries,
                        "total_entries": len(self._cache)
                    }
                }
            finally:
                self._lock.release()
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas del cache: {e}")
            return self._get_basic_stats()
    
    def _get_basic_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas básicas sin locks para casos de emergencia."""
        return {
            "cache_stats": asdict(self.stats),
            "memory_usage": {
                "current_bytes": 0,
                "current_mb": 0.0,
                "max_mb": round(self.max_memory_bytes / (1024 * 1024), 2),
                "utilization_percent": 0.0
            },
            "cache_efficiency": {
                "hit_rate_percent": round(self.stats.hit_rate * 100, 1),
                "miss_rate_percent": round(self.stats.miss_rate * 100, 1),
                "avg_hits_per_entry": 0.0,
                "active_entries": 0,
                "total_entries": 0
            }
        }


# Instancia global del cache (Singleton pattern)
_prediction_cache: Optional[PredictionCache] = None
_cache_lock = Lock()


def get_prediction_cache() -> PredictionCache:
    """
    Obtiene la instancia global del cache de predicciones.
    Implementa patrón Singleton thread-safe.
    """
    global _prediction_cache
    
    if _prediction_cache is None:
        with _cache_lock:
            if _prediction_cache is None:
                _prediction_cache = PredictionCache(
                    max_size=1000,      # 1000 predicciones máximo
                    default_ttl=300,    # 5 minutos TTL
                    max_memory_mb=50    # 50MB máximo
                )
    
    return _prediction_cache


def invalidate_cache() -> None:
    """Invalida (limpia) el cache global de predicciones."""
    global _prediction_cache
    
    if _prediction_cache is not None:
        _prediction_cache.clear()
        logger.info("🗑️ Cache global de predicciones invalidado")
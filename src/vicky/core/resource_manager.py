"""
Gestor de Recursos Dinámico para Vicky
Gestiona modelos bajo demanda sin afectar VokaFlow
"""

import os
import time
import psutil
import logging
import threading
import GPUtil
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
import torch

logger = logging.getLogger("vicky.resource_manager")

@dataclass
class ResourceLimits:
    """Límites de recursos para Vicky"""
    max_vram_mb: int = 7168  # 7GB máximo para Vicky
    max_ram_mb: int = 8192   # 8GB RAM máximo
    max_cpu_percent: float = 40.0  # 40% CPU máximo
    emergency_threshold_vram: int = 6144  # 6GB umbral emergencia
    emergency_threshold_ram: int = 6144   # 6GB umbral emergencia

@dataclass 
class ModelSpec:
    """Especificación de un modelo"""
    name: str
    path: str
    vram_required_mb: int
    ram_required_mb: int
    load_time_seconds: float
    priority: int  # 1=alta, 2=media, 3=baja
    model_type: str  # "language", "technical", "fast_response"

class ModelLoadState(Enum):
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    UNLOADING = "unloading"
    ERROR = "error"

class VickyResourceManager:
    """
    Gestor de recursos dinámico para Vicky
    
    PRINCIPIOS:
    1. VokaFlow SIEMPRE tiene prioridad absoluta
    2. Vicky solo usa recursos sobrantes
    3. Descarga inmediata si VokaFlow necesita recursos
    4. Monitoreo continuo de uso de recursos
    """
    
    def __init__(self, limits: ResourceLimits = None):
        self.limits = limits or ResourceLimits()
        
        # Estado de modelos
        self.loaded_models: Dict[str, Any] = {}
        self.model_states: Dict[str, ModelLoadState] = {}
        self.model_specs: Dict[str, ModelSpec] = {}
        
        # Monitoreo
        self.monitoring = False
        self.monitor_thread = None
        self.last_resource_check = 0
        
        # Callbacks
        self.on_emergency_unload: Optional[Callable] = None
        self.on_model_loaded: Optional[Callable] = None
        self.on_model_unloaded: Optional[Callable] = None
        
        # Configurar modelos disponibles
        self._setup_model_specs()
        
        logger.info("🎯 VickyResourceManager inicializado")
        logger.info(f"📊 Límites: VRAM={self.limits.max_vram_mb}MB, RAM={self.limits.max_ram_mb}MB")
        
    def _setup_model_specs(self):
        """Configura las especificaciones de modelos disponibles"""
        self.model_specs = {
            # Modelo rápido siempre cargado
            "fast_response": ModelSpec(
                name="GPT2-Small",
                path="/cache/models/gpt2-small", 
                vram_required_mb=512,
                ram_required_mb=1024,
                load_time_seconds=5.0,
                priority=1,
                model_type="fast_response"
            ),
            
            # Modelo principal de lenguaje
            "qwen_7b": ModelSpec(
                name="Qwen-7B-4bit",
                path="/cache/models/huggingface/hub/models--Qwen--Qwen-7B",
                vram_required_mb=4096,
                ram_required_mb=2048,
                load_time_seconds=30.0,
                priority=2,
                model_type="language"
            ),
            
            # Modelo técnico especializado
            "deepseek_coder": ModelSpec(
                name="DeepSeek-Coder-7B-4bit",
                path="/cache/models/deepseek-coder-7b",
                vram_required_mb=4096,
                ram_required_mb=2048,
                load_time_seconds=35.0,
                priority=2,
                model_type="technical"
            ),
            
            # Embeddings (siempre cargado)
            "embeddings": ModelSpec(
                name="all-MiniLM-L6-v2",
                path="/cache/models/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2",
                vram_required_mb=256,
                ram_required_mb=512,
                load_time_seconds=3.0,
                priority=1,
                model_type="embeddings"
            )
        }
    
    def start_monitoring(self):
        """Inicia el monitoreo continuo de recursos"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_resources, daemon=True)
        self.monitor_thread.start()
        
        logger.info("🔍 Monitoreo de recursos iniciado")
    
    def stop_monitoring(self):
        """Detiene el monitoreo de recursos"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("🛑 Monitoreo de recursos detenido")
    
    def _monitor_resources(self):
        """Loop de monitoreo de recursos"""
        while self.monitoring:
            try:
                current_usage = self.get_current_resource_usage()
                
                # Verificar si necesitamos liberación de emergencia
                if self._should_emergency_unload(current_usage):
                    logger.warning("🚨 EMERGENCIA: Descargando modelos de Vicky")
                    self._emergency_unload_all()
                
                # Verificar si podemos cargar modelos en cola
                elif self._can_load_more_models(current_usage):
                    self._try_load_queued_models()
                
                time.sleep(2)  # Chequear cada 2 segundos
                
            except Exception as e:
                logger.error(f"Error en monitoreo de recursos: {e}")
                time.sleep(5)
    
    def get_current_resource_usage(self) -> Dict[str, Any]:
        """Obtiene el uso actual de recursos del sistema"""
        try:
            # GPU info
            gpu_info = {"vram_used_mb": 0, "vram_total_mb": 0}
            if torch.cuda.is_available():
                gpu_memory_used = torch.cuda.memory_allocated() / 1024 / 1024  # MB
                gpu_memory_total = torch.cuda.get_device_properties(0).total_memory / 1024 / 1024
                gpu_info = {
                    "vram_used_mb": gpu_memory_used,
                    "vram_total_mb": gpu_memory_total,
                    "vram_available_mb": gpu_memory_total - gpu_memory_used
                }
            
            # CPU y RAM
            ram_info = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            return {
                "timestamp": time.time(),
                "gpu": gpu_info,
                "ram_used_mb": ram_info.used / 1024 / 1024,
                "ram_total_mb": ram_info.total / 1024 / 1024,
                "ram_available_mb": ram_info.available / 1024 / 1024,
                "cpu_percent": cpu_percent,
                "loaded_models": list(self.loaded_models.keys()),
                "vicky_vram_usage": sum(
                    self.model_specs[model].vram_required_mb 
                    for model in self.loaded_models.keys()
                    if model in self.model_specs
                )
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo uso de recursos: {e}")
            return {"error": str(e)}
    
    def _should_emergency_unload(self, usage: Dict[str, Any]) -> bool:
        """Determina si necesitamos descarga de emergencia"""
        if "error" in usage:
            return False
            
        vram_critical = usage["gpu"]["vram_available_mb"] < self.limits.emergency_threshold_vram
        ram_critical = usage["ram_available_mb"] < self.limits.emergency_threshold_ram
        
        return vram_critical or ram_critical
    
    def _can_load_more_models(self, usage: Dict[str, Any]) -> bool:
        """Determina si podemos cargar más modelos"""
        if "error" in usage:
            return False
            
        vram_ok = usage["vicky_vram_usage"] < self.limits.max_vram_mb * 0.8  # 80% del límite
        ram_ok = usage["ram_available_mb"] > 2048  # Al menos 2GB libres
        
        return vram_ok and ram_ok
    
    def _emergency_unload_all(self):
        """Descarga de emergencia todos los modelos de Vicky excepto críticos"""
        critical_models = ["fast_response", "embeddings"]
        
        for model_name in list(self.loaded_models.keys()):
            if model_name not in critical_models:
                try:
                    self.unload_model(model_name, emergency=True)
                    logger.warning(f"🚨 Modelo {model_name} descargado por emergencia")
                except Exception as e:
                    logger.error(f"Error en descarga de emergencia {model_name}: {e}")
        
        if self.on_emergency_unload:
            self.on_emergency_unload()
    
    def _try_load_queued_models(self):
        """Intenta cargar modelos en cola si hay recursos"""
        # Implementación futura para cola de modelos pendientes
        pass
    
    async def load_model(self, model_name: str, force: bool = False) -> bool:
        """
        Carga un modelo si hay recursos disponibles
        
        Args:
            model_name: Nombre del modelo a cargar
            force: Forzar carga ignorando límites (solo para emergencias)
            
        Returns:
            True si se cargó exitosamente
        """
        if model_name not in self.model_specs:
            logger.error(f"Modelo {model_name} no encontrado en especificaciones")
            return False
            
        if model_name in self.loaded_models:
            logger.info(f"Modelo {model_name} ya está cargado")
            return True
        
        spec = self.model_specs[model_name]
        
        # Verificar recursos disponibles
        if not force:
            usage = self.get_current_resource_usage()
            if not self._can_load_model(spec, usage):
                logger.warning(f"Recursos insuficientes para cargar {model_name}")
                return False
        
        try:
            logger.info(f"🔄 Cargando modelo {model_name}...")
            self.model_states[model_name] = ModelLoadState.LOADING
            
            start_time = time.time()
            
            # Cargar modelo según tipo
            if spec.model_type == "fast_response":
                model = self._load_fast_model(spec)
            elif spec.model_type in ["language", "technical"]:
                model = self._load_large_model(spec)
            elif spec.model_type == "embeddings":
                model = self._load_embedding_model(spec)
            else:
                raise ValueError(f"Tipo de modelo desconocido: {spec.model_type}")
            
            self.loaded_models[model_name] = model
            self.model_states[model_name] = ModelLoadState.LOADED
            
            load_time = time.time() - start_time
            logger.info(f"✅ Modelo {model_name} cargado en {load_time:.1f}s")
            
            if self.on_model_loaded:
                self.on_model_loaded(model_name, spec, load_time)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cargando modelo {model_name}: {e}")
            self.model_states[model_name] = ModelLoadState.ERROR
            return False
    
    def _can_load_model(self, spec: ModelSpec, usage: Dict[str, Any]) -> bool:
        """Verifica si hay recursos para cargar un modelo"""
        if "error" in usage:
            return False
            
        vram_available = usage["gpu"]["vram_available_mb"]
        ram_available = usage["ram_available_mb"]
        
        vram_ok = vram_available >= spec.vram_required_mb + 512  # +512MB buffer
        ram_ok = ram_available >= spec.ram_required_mb + 1024   # +1GB buffer
        
        total_vicky_vram = usage["vicky_vram_usage"] + spec.vram_required_mb
        within_limits = total_vicky_vram <= self.limits.max_vram_mb
        
        return vram_ok and ram_ok and within_limits
    
    def _load_fast_model(self, spec: ModelSpec) -> Any:
        """Carga modelo rápido (GPT-2 small o similar)"""
        # Mock por ahora - en producción cargaría modelo real
        return {"type": "fast_model", "name": spec.name, "loaded_at": time.time()}
    
    def _load_large_model(self, spec: ModelSpec) -> Any:
        """Carga modelo grande (Qwen, DeepSeek, etc.)"""
        # Mock por ahora - en producción usaría transformers
        time.sleep(spec.load_time_seconds / 10)  # Simular tiempo de carga
        return {"type": "large_model", "name": spec.name, "loaded_at": time.time()}
    
    def _load_embedding_model(self, spec: ModelSpec) -> Any:
        """Carga modelo de embeddings"""
        # Mock por ahora - en producción usaría sentence-transformers
        return {"type": "embedding_model", "name": spec.name, "loaded_at": time.time()}
    
    def unload_model(self, model_name: str, emergency: bool = False) -> bool:
        """
        Descarga un modelo de memoria
        
        Args:
            model_name: Nombre del modelo a descargar
            emergency: Si es descarga de emergencia (más rápida)
            
        Returns:
            True si se descargó exitosamente
        """
        if model_name not in self.loaded_models:
            logger.warning(f"Modelo {model_name} no está cargado")
            return True
        
        try:
            logger.info(f"🗑️ Descargando modelo {model_name}...")
            self.model_states[model_name] = ModelLoadState.UNLOADING
            
            # Eliminar modelo de memoria
            del self.loaded_models[model_name]
            
            # Limpiar cache de GPU si es necesario
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            self.model_states[model_name] = ModelLoadState.UNLOADED
            
            logger.info(f"✅ Modelo {model_name} descargado")
            
            if self.on_model_unloaded:
                self.on_model_unloaded(model_name, emergency)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error descargando modelo {model_name}: {e}")
            return False
    
    def get_model(self, model_name: str) -> Optional[Any]:
        """Obtiene un modelo cargado"""
        return self.loaded_models.get(model_name)
    
    def is_model_loaded(self, model_name: str) -> bool:
        """Verifica si un modelo está cargado"""
        return model_name in self.loaded_models
    
    def get_model_state(self, model_name: str) -> ModelLoadState:
        """Obtiene el estado de un modelo"""
        return self.model_states.get(model_name, ModelLoadState.UNLOADED)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtiene estado completo del sistema"""
        usage = self.get_current_resource_usage()
        
        return {
            "resource_usage": usage,
            "limits": {
                "max_vram_mb": self.limits.max_vram_mb,
                "max_ram_mb": self.limits.max_ram_mb,
                "max_cpu_percent": self.limits.max_cpu_percent
            },
            "loaded_models": {
                name: {
                    "state": self.model_states.get(name, ModelLoadState.UNLOADED).value,
                    "spec": self.model_specs[name].__dict__ if name in self.model_specs else None
                }
                for name in self.model_specs.keys()
            },
            "monitoring_active": self.monitoring,
            "emergency_mode": self._should_emergency_unload(usage) if "error" not in usage else False
        } 
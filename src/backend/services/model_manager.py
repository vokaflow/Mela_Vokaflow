#!/usr/bin/env python3
"""
VokaFlow - Gestor de Modelos AI
Maneja carga, cache y gestión eficiente de modelos locales
"""

import os
import logging
import gc
import torch
import psutil
from typing import Dict, Any, Optional, Union
from pathlib import Path
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

logger = logging.getLogger("vokaflow.model_manager")

@dataclass
class ModelInfo:
    """Información de un modelo cargado"""
    name: str
    model_type: str  # translation, stt, tts, embeddings
    model: Any
    tokenizer: Any = None
    processor: Any = None
    loaded_at: datetime = None
    last_used: datetime = None
    memory_usage: float = 0.0  # GB
    is_gpu: bool = False
    config: Dict[str, Any] = None

class ModelManager:
    """Gestor centralizado de modelos AI"""
    
    def __init__(self, models_dir: str = "/opt/vokaflow/models"):
        self.models_dir = Path(models_dir)
        self.loaded_models: Dict[str, ModelInfo] = {}
        self.essential_models = ["nllb-3.3b", "xtts-v2", "whisper-large-v3"]  # Modelos críticos para precargar
        self.model_configs = {
            "nllb-3.3b": {
                "type": "translation",
                "path": "nllb-3.3b",
                "class": "transformers.M2M100ForConditionalGeneration",
                "tokenizer": "transformers.M2M100Tokenizer",
                "device_map": "auto",
                "torch_dtype": "torch.float16",
                "trust_remote_code": True
            },
            "whisper-large-v3": {
                "type": "stt",
                "path": "whisper-large-v3", 
                "class": "transformers.WhisperForConditionalGeneration",
                "processor": "transformers.WhisperProcessor",
                "device_map": "auto",
                "torch_dtype": "torch.float16"
            },
            "xtts-v2": {
                "type": "tts",
                "path": "xtts-v2",
                "class": "TTS.tts.models.xtts.XTTS",
                "device": "cuda" if torch.cuda.is_available() else "cpu"
            },
            "bge-m3": {
                "type": "embeddings",
                "path": "bge-m3",
                "class": "sentence_transformers.SentenceTransformer",
                "device": "cuda" if torch.cuda.is_available() else "cpu"
            }
        }
        self.lock = threading.Lock()
        self.max_memory_gb = 8.0  # Máximo 8GB en cache
        self.unload_after_minutes = 30  # Descargar después de 30 min sin uso
        
        logger.info(f"ModelManager iniciado. Directorio: {self.models_dir}")
        logger.info(f"GPU disponible: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            logger.info(f"GPU: {torch.cuda.get_device_name()}")
    
    def get_model_path(self, model_name: str) -> Path:
        """Obtiene la ruta completa del modelo"""
        if model_name not in self.model_configs:
            raise ValueError(f"Modelo no configurado: {model_name}")
        
        model_path = self.models_dir / self.model_configs[model_name]["path"]
        if not model_path.exists():
            raise FileNotFoundError(f"Modelo no encontrado: {model_path}")
        
        return model_path
    
    def get_memory_usage(self) -> float:
        """Obtiene uso actual de memoria en GB"""
        process = psutil.Process()
        return process.memory_info().rss / (1024**3)
    
    def cleanup_unused_models(self):
        """Limpia modelos no usados recientemente"""
        current_time = datetime.now()
        to_unload = []
        
        for name, model_info in self.loaded_models.items():
            if model_info.last_used:
                minutes_unused = (current_time - model_info.last_used).total_seconds() / 60
                if minutes_unused > self.unload_after_minutes:
                    to_unload.append(name)
        
        for name in to_unload:
            self.unload_model(name)
    
    def check_memory_and_cleanup(self):
        """Verifica memoria y limpia si es necesario"""
        current_memory = self.get_memory_usage()
        
        if current_memory > self.max_memory_gb:
            logger.warning(f"Memoria alta: {current_memory:.2f}GB. Limpiando modelos...")
            
            # Ordenar por último uso (más antiguos primero)
            models_by_usage = sorted(
                self.loaded_models.items(),
                key=lambda x: x[1].last_used or datetime.min
            )
            
            for name, _ in models_by_usage:
                self.unload_model(name)
                current_memory = self.get_memory_usage()
                if current_memory < self.max_memory_gb * 0.8:  # Dejar 20% de margen
                    break
    
    def load_model(self, model_name: str, force_reload: bool = False) -> ModelInfo:
        """Carga un modelo en memoria"""
        with self.lock:
            # Si ya está cargado y no se fuerza recarga
            if model_name in self.loaded_models and not force_reload:
                model_info = self.loaded_models[model_name]
                model_info.last_used = datetime.now()
                logger.info(f"Modelo {model_name} ya cargado, reutilizando")
                return model_info
            
            # Verificar memoria antes de cargar
            self.check_memory_and_cleanup()
            
            logger.info(f"Cargando modelo: {model_name}")
            start_time = datetime.now()
            
            try:
                model_config = self.model_configs[model_name]
                model_path = self.get_model_path(model_name)
                
                # Cargar según el tipo de modelo
                if model_config["type"] == "translation":
                    model_info = self._load_translation_model(model_name, model_path, model_config)
                elif model_config["type"] == "stt":
                    model_info = self._load_stt_model(model_name, model_path, model_config)
                elif model_config["type"] == "tts":
                    model_info = self._load_tts_model(model_name, model_path, model_config)
                elif model_config["type"] == "embeddings":
                    model_info = self._load_embeddings_model(model_name, model_path, model_config)
                else:
                    raise ValueError(f"Tipo de modelo no soportado: {model_config['type']}")
                
                load_time = (datetime.now() - start_time).total_seconds()
                model_info.loaded_at = start_time
                model_info.last_used = datetime.now()
                
                self.loaded_models[model_name] = model_info
                
                logger.info(f"Modelo {model_name} cargado en {load_time:.2f}s")
                logger.info(f"Memoria total: {self.get_memory_usage():.2f}GB")
                
                return model_info
                
            except Exception as e:
                logger.error(f"Error cargando modelo {model_name}: {e}")
                raise
    
    def _load_translation_model(self, name: str, path: Path, config: Dict) -> ModelInfo:
        """Carga modelo de traducción NLLB"""
        from transformers import NllbTokenizer, AutoModelForSeq2SeqLM
        
        logger.info(f"Cargando NLLB desde {path}")
        
        try:
            # Cargar tokenizer NLLB específico
            tokenizer = NllbTokenizer.from_pretrained(
                str(path),
                local_files_only=True
            )
            
            # Cargar modelo usando AutoModel para mejor compatibilidad
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            model = AutoModelForSeq2SeqLM.from_pretrained(
                str(path),
                local_files_only=True,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map=device if torch.cuda.is_available() else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            # Mover a GPU si está disponible
            if torch.cuda.is_available():
                model = model.to(device)
            
            logger.info(f"✅ NLLB cargado exitosamente en {device}")
            
            return ModelInfo(
                name=name,
                model_type="translation",
                model=model,
                tokenizer=tokenizer,
                config=config,
                is_gpu=torch.cuda.is_available()
            )
            
        except Exception as e:
            logger.error(f"Error específico cargando NLLB: {e}")
            raise
    
    def _load_stt_model(self, name: str, path: Path, config: Dict) -> ModelInfo:
        """Carga modelo STT Whisper"""
        from transformers import WhisperForConditionalGeneration, WhisperProcessor
        
        logger.info(f"Cargando Whisper desde {path}")
        
        # Cargar processor
        processor = WhisperProcessor.from_pretrained(
            str(path),
            local_files_only=True
        )
        
        # Cargar modelo
        model = WhisperForConditionalGeneration.from_pretrained(
            str(path),
            local_files_only=True,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        return ModelInfo(
            name=name,
            model_type="stt", 
            model=model,
            processor=processor,
            config=config,
            is_gpu=torch.cuda.is_available()
        )
    
    def _load_tts_model(self, name: str, path: Path, config: Dict) -> ModelInfo:
        """Carga modelo TTS XTTS-V2"""
        try:
            from TTS.api import TTS
            
            logger.info(f"Cargando XTTS-V2 desde {path}")
            
            # Cargar usando TTS API con path local
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Intentar cargar desde path local
            if (path / "config.json").exists():
                model = TTS(
                    model_path=str(path),
                    config_path=str(path / "config.json")
                ).to(device)
            else:
                # Fallback a modelo preentrenado
                logger.warning(f"Configuración local no encontrada en {path}, usando modelo preentrenado")
                model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
            
            return ModelInfo(
                name=name,
                model_type="tts",
                model=model,
                config=config,
                is_gpu=torch.cuda.is_available()
            )
            
        except ImportError as e:
            logger.warning(f"TTS library no disponible: {e}")
            return ModelInfo(
                name=name,
                model_type="tts",
                model=None,  # Modelo simulado
                config=config,
                is_gpu=False
            )
        except Exception as e:
            logger.error(f"Error cargando XTTS-V2: {e}")
            # Devolver modelo simulado en caso de error
            return ModelInfo(
                name=name,
                model_type="tts", 
                model=None,
                config=config,
                is_gpu=False
            )
    
    def _load_embeddings_model(self, name: str, path: Path, config: Dict) -> ModelInfo:
        """Carga modelo de embeddings BGE-M3"""
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info(f"Cargando BGE-M3 desde {path}")
            
            model = SentenceTransformer(
                str(path),
                device="cuda" if torch.cuda.is_available() else "cpu"
            )
            
            return ModelInfo(
                name=name,
                model_type="embeddings",
                model=model,
                config=config,
                is_gpu=torch.cuda.is_available()
            )
            
        except ImportError:
            logger.warning("SentenceTransformers no instalado")
            return ModelInfo(
                name=name,
                model_type="embeddings", 
                model=None,
                config=config,
                is_gpu=False
            )
    
    def unload_model(self, model_name: str):
        """Descarga un modelo de memoria"""
        with self.lock:
            if model_name in self.loaded_models:
                logger.info(f"Descargando modelo: {model_name}")
                
                model_info = self.loaded_models[model_name]
                
                # Mover a CPU y limpiar
                if model_info.model and hasattr(model_info.model, 'cpu'):
                    model_info.model.cpu()
                
                del self.loaded_models[model_name]
                
                # Limpiar memoria
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
                logger.info(f"Modelo {model_name} descargado")
    
    def get_model(self, model_name: str) -> ModelInfo:
        """Obtiene un modelo (lo carga si es necesario)"""
        return self.load_model(model_name)
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene estado del gestor de modelos"""
        return {
            "loaded_models": list(self.loaded_models.keys()),
            "memory_usage_gb": self.get_memory_usage(),
            "max_memory_gb": self.max_memory_gb,
            "gpu_available": torch.cuda.is_available(),
            "gpu_memory_allocated": torch.cuda.memory_allocated() / (1024**3) if torch.cuda.is_available() else 0,
            "models_config": list(self.model_configs.keys())
        }
    
    def cleanup_all(self):
        """Descarga todos los modelos"""
        model_names = list(self.loaded_models.keys())
        for name in model_names:
            self.unload_model(name)
    
    async def preload_essential_models(self) -> Dict[str, Any]:
        """Precarga modelos esenciales al iniciar el sistema"""
        logger.info("🚀 Iniciando precarga de modelos esenciales en GPU...")
        start_time = datetime.now()
        preload_results = {}
        
        # Verificar GPU antes de precargar
        if not torch.cuda.is_available():
            logger.warning("⚠️ GPU no disponible, modelos se cargarán en CPU")
        else:
            logger.info(f"✅ GPU disponible: {torch.cuda.get_device_name()}")
        
        for model_name in self.essential_models:
            logger.info(f"📥 Precargando modelo esencial: {model_name}")
            model_start = datetime.now()
            
            try:
                model_info = self.load_model(model_name)
                load_time = (datetime.now() - model_start).total_seconds()
                
                preload_results[model_name] = {
                    "status": "success",
                    "loaded_at": model_info.loaded_at.isoformat(),
                    "load_time_seconds": load_time,
                    "is_gpu": model_info.is_gpu,
                    "model_type": model_info.model_type
                }
                
                logger.info(f"✅ {model_name} cargado exitosamente en {load_time:.2f}s (GPU: {model_info.is_gpu})")
                
            except Exception as e:
                load_time = (datetime.now() - model_start).total_seconds()
                error_msg = str(e)
                
                preload_results[model_name] = {
                    "status": "error",
                    "error": error_msg,
                    "load_time_seconds": load_time,
                    "is_gpu": False,
                    "model_type": self.model_configs.get(model_name, {}).get("type", "unknown")
                }
                
                logger.error(f"❌ Error precargando {model_name}: {error_msg}")
        
        total_time = (datetime.now() - start_time).total_seconds()
        successful_models = [name for name, result in preload_results.items() if result["status"] == "success"]
        failed_models = [name for name, result in preload_results.items() if result["status"] == "error"]
        
        summary = {
            "total_time_seconds": total_time,
            "successful_models": successful_models,
            "failed_models": failed_models,
            "success_rate": len(successful_models) / len(self.essential_models) * 100,
            "gpu_available": torch.cuda.is_available(),
            "models_on_gpu": sum(1 for result in preload_results.values() if result.get("is_gpu", False)),
            "preload_results": preload_results
        }
        
        logger.info(f"🎯 Precarga completada en {total_time:.2f}s - Éxito: {len(successful_models)}/{len(self.essential_models)} modelos")
        if failed_models:
            logger.warning(f"⚠️ Modelos fallidos: {failed_models}")
        
        return summary
    
    def ensure_model_on_gpu(self, model_name: str) -> bool:
        """Asegura que un modelo específico esté cargado en GPU"""
        if not torch.cuda.is_available():
            logger.warning(f"GPU no disponible para cargar {model_name}")
            return False
        
        try:
            model_info = self.get_model(model_name)
            if model_info.is_gpu:
                logger.info(f"✅ {model_name} ya está en GPU")
                return True
            else:
                # Recargar en GPU
                logger.info(f"🔄 Moviendo {model_name} a GPU...")
                self.unload_model(model_name)
                model_info = self.load_model(model_name, force_reload=True)
                return model_info.is_gpu
        except Exception as e:
            logger.error(f"Error asegurando {model_name} en GPU: {e}")
            return False

# Instancia global del gestor de modelos
model_manager = ModelManager()

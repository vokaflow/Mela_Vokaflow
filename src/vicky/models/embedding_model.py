"""
Módulo para interactuar con modelos de embeddings
"""
import os
import logging
import torch
import numpy as np
from typing import List, Dict, Any, Optional, Union
import yaml

logger = logging.getLogger("vicky.models.embedding_model")

class EmbeddingModel:
    """
    Clase para interactuar con modelos de embeddings como Sentence Transformers
    """
    
    def __init__(self, model_path: str = None, device: str = None):
        """
        Inicializa el modelo de embeddings.
        
        Args:
            model_path: Ruta al modelo
            device: Dispositivo para inferencia (cuda, cpu)
        """
        # Cargar configuración
        config_path = os.environ.get("MODELS_CONFIG", "/opt/vokaflow/config/models.yaml")
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        # Configurar modelo
        self.model_path = model_path or self.config["embeddings"]["models"]["all-MiniLM-L6-v2"]["path"]
        self.device = device or self.config["embeddings"]["models"]["all-MiniLM-L6-v2"]["device"]
        
        self.model = None
        
        logger.info(f"Inicializando modelo de embeddings desde {self.model_path}")
    
    def load(self):
        """Carga el modelo en memoria."""
        try:
            logger.info(f"Cargando modelo de embeddings desde {self.model_path}")
            
            # Importar las bibliotecas necesarias
            from sentence_transformers import SentenceTransformer
            
            # Cargar modelo
            self.model = SentenceTransformer(self.model_path, device=self.device)
            
            logger.info("Modelo de embeddings cargado correctamente")
            
            # Mostrar información de memoria si se usa GPU
            if self.device == "cuda" and torch.cuda.is_available():
                logger.info(f"Memoria GPU reservada: {torch.cuda.memory_reserved() / 1024**3:.2f} GB")
                logger.info(f"Memoria GPU en uso: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
            
            return True
        except Exception as e:
            logger.error(f"Error al cargar el modelo de embeddings: {e}")
            return False
    
    def encode(self, texts: Union[str, List[str]], normalize: bool = True) -> np.ndarray:
        """
        Genera embeddings para uno o varios textos.
        
        Args:
            texts: Texto o lista de textos
            normalize: Si se deben normalizar los embeddings
            
        Returns:
            Array de embeddings
        """
        if self.model is None:
            logger.warning("El modelo no está cargado. Cargando...")
            if not self.load():
                return np.array([])
        
        try:
            logger.info(f"Generando embeddings para {len(texts) if isinstance(texts, list) else 1} texto(s)...")
            
            # Generar embeddings
            embeddings = self.model.encode(texts, normalize_embeddings=normalize)
            
            logger.info(f"Embeddings generados con forma {embeddings.shape}")
            return embeddings
        except Exception as e:
            logger.error(f"Error al generar embeddings: {e}")
            return np.array([])
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        Calcula la similitud coseno entre dos textos.
        
        Args:
            text1: Primer texto
            text2: Segundo texto
            
        Returns:
            Similitud coseno (0-1)
        """
        if self.model is None:
            logger.warning("El modelo no está cargado. Cargando...")
            if not self.load():
                return 0.0
        
        try:
            # Generar embeddings
            embeddings = self.encode([text1, text2])
            
            # Calcular similitud coseno
            from sklearn.metrics.pairwise import cosine_similarity
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            
            logger.info(f"Similitud entre textos: {similarity:.4f}")
            return similarity
        except Exception as e:
            logger.error(f"Error al calcular similitud: {e}")
            return 0.0
    
    def unload(self):
        """Libera la memoria del modelo."""
        if self.model is not None:
            del self.model
            self.model = None
        
        # Limpiar caché de CUDA si está disponible
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info("Modelo de embeddings descargado de memoria")

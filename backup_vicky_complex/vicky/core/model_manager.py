"""
Gestor de modelos para Vicky
"""
import os
import logging
import yaml
from typing import Dict, Any, Optional, List

logger = logging.getLogger("vicky.core.model_manager")

class ModelManager:
    """
    Clase para gestionar la carga y descarga de modelos de IA
    """
    
    def __init__(self, config_path: str = None):
        """
        Inicializa el gestor de modelos.
        
        Args:
            config_path: Ruta al archivo de configuración
        """
        self.config_path = config_path or os.environ.get("MODELS_CONFIG", "/opt/vokaflow/config/models.yaml")
        self.config = self._load_config()
        self.models = {}
        
        logger.info("Inicializando gestor de modelos")
    
    def _load_config(self) -> Dict[str, Any]:
        """Carga la configuración desde el archivo YAML."""
        try:
            with open(self.config_path, "r") as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuración cargada desde {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Error al cargar configuración: {e}")
            return {}
    
    def load_model(self, model_type: str, model_name: Optional[str] = None) -> Any:
        """
        Carga un modelo en memoria.
        
        Args:
            model_type: Tipo de modelo (language, translation, speech, tts, embedding, deepseek)
            model_name: Nombre del modelo (si es None, se usa el predeterminado)
            
        Returns:
            Instancia del modelo cargado
        """
        # Determinar el nombre del modelo
        if model_name is None:
            if model_type == "language":
                model_name = self.config["language_models"]["default"]
            elif model_type == "translation":
                model_name = self.config["translation_models"]["default"]
            elif model_type == "speech":
                model_name = self.config["speech_recognition"]["default"]
            elif model_type == "tts":
                model_name = self.config["text_to_speech"]["default"]
            elif model_type == "embedding":
                model_name = self.config["embeddings"]["default"]
            elif model_type == "deepseek":
                model_name = "deepseek"
            else:
                logger.error(f"Tipo de modelo desconocido: {model_type}")
                return None
        
        # Verificar si el modelo ya está cargado
        model_key = f"{model_type}_{model_name}"
        if model_key in self.models:
            logger.info(f"Modelo {model_key} ya está cargado")
            return self.models[model_key]
        
        # Cargar el modelo según su tipo
        try:
            if model_type == "language":
                from ..models.language_model import LanguageModel
                model = LanguageModel()
                model.load()
            elif model_type == "translation":
                from ..models.translation_model import TranslationModel
                model = TranslationModel()
                model.load()
            elif model_type == "speech":
                from ..models.speech_model import SpeechModel
                model = SpeechModel()
                model.load()
            elif model_type == "tts":
                from ..models.tts_model import TTSModel
                model = TTSModel()
                model.load()
            elif model_type == "embedding":
                from ..models.embedding_model import EmbeddingModel
                model = EmbeddingModel()
                model.load()
            elif model_type == "deepseek":
                from ..models.deepseek_model import DeepSeekModel
                model = DeepSeekModel()
                model.load()
            else:
                logger.error(f"Tipo de modelo desconocido: {model_type}")
                return None
            
            # Almacenar el modelo cargado
            self.models[model_key] = model
            logger.info(f"Modelo {model_key} cargado correctamente")
            
            return model
        except Exception as e:
            logger.error(f"Error al cargar modelo {model_type}_{model_name}: {e}")
            return None
    
    def unload_model(self, model_type: str, model_name: Optional[str] = None) -> bool:
        """
        Descarga un modelo de la memoria.
        
        Args:
            model_type: Tipo de modelo
            model_name: Nombre del modelo
            
        Returns:
            True si se descargó correctamente, False en caso contrario
        """
        # Determinar el nombre del modelo
        if model_name is None:
            if model_type == "language":
                model_name = self.config["language_models"]["default"]
            elif model_type == "translation":
                model_name = self.config["translation_models"]["default"]
            elif model_type == "speech":
                model_name = self.config["speech_recognition"]["default"]
            elif model_type == "tts":
                model_name = self.config["text_to_speech"]["default"]
            elif model_type == "embedding":
                model_name = self.config["embeddings"]["default"]
            elif model_type == "deepseek":
                model_name = "deepseek"
            else:
                logger.error(f"Tipo de modelo desconocido: {model_type}")
                return False
        
        # Verificar si el modelo está cargado
        model_key = f"{model_type}_{model_name}"
        if model_key not in self.models:
            logger.warning(f"Modelo {model_key} no está cargado")
            return True
        
        # Descargar el modelo
        try:
            model = self.models[model_key]
            model.unload()
            del self.models[model_key]
            logger.info(f"Modelo {model_key} descargado correctamente")
            return True
        except Exception as e:
            logger.error(f"Error al descargar modelo {model_key}: {e}")
            return False
    
    def unload_all(self) -> bool:
        """
        Descarga todos los modelos de la memoria.
        
        Returns:
            True si todos los modelos se descargaron correctamente, False en caso contrario
        """
        success = True
        for model_key in list(self.models.keys()):
            try:
                model_type, model_name = model_key.split("_", 1)
                if not self.unload_model(model_type, model_name):
                    success = False
            except Exception as e:
                logger.error(f"Error al descargar modelo {model_key}: {e}")
                success = False
        
        return success
    
    def get_loaded_models(self) -> List[str]:
        """
        Obtiene la lista de modelos cargados.
        
        Returns:
            Lista de nombres de modelos cargados
        """
        return list(self.models.keys())
    
    def get_model(self, model_type: str, model_name: Optional[str] = None) -> Any:
        """
        Obtiene un modelo cargado o lo carga si no está en memoria.
        
        Args:
            model_type: Tipo de modelo
            model_name: Nombre del modelo
            
        Returns:
            Instancia del modelo
        """
        # Determinar el nombre del modelo
        if model_name is None:
            if model_type == "language":
                model_name = self.config["language_models"]["default"]
            elif model_type == "translation":
                model_name = self.config["translation_models"]["default"]
            elif model_type == "speech":
                model_name = self.config["speech_recognition"]["default"]
            elif model_type == "tts":
                model_name = self.config["text_to_speech"]["default"]
            elif model_type == "embedding":
                model_name = self.config["embeddings"]["default"]
            elif model_type == "deepseek":
                model_name = "deepseek"
            else:
                logger.error(f"Tipo de modelo desconocido: {model_type}")
                return None
        
        # Verificar si el modelo está cargado
        model_key = f"{model_type}_{model_name}"
        if model_key in self.models:
            return self.models[model_key]
        
        # Cargar el modelo si no está en memoria
        return self.load_model(model_type, model_name)

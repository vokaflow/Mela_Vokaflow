"""
Módulo para interactuar con modelos de traducción
"""
import os
import logging
import torch
from typing import List, Dict, Any, Optional
import yaml

logger = logging.getLogger("vicky.models.translation_model")

class TranslationModel:
    """
    Clase para interactuar con modelos de traducción como NLLB
    """
    
    def __init__(self, model_path: str = None, device: str = None):
        """
        Inicializa el modelo de traducción.
        
        Args:
            model_path: Ruta al modelo
            device: Dispositivo para inferencia (cuda, cpu)
        """
        # Cargar configuración
        config_path = os.environ.get("MODELS_CONFIG", "/opt/vokaflow/config/models.yaml")
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        # Configurar modelo
        self.model_path = model_path or self.config["translation_models"]["models"]["nllb"]["path"]
        self.device = device or self.config["translation_models"]["models"]["nllb"]["device"]
        
        self.model = None
        self.tokenizer = None
        
        # Mapeo de códigos de idioma
        self.language_codes = {
            "es": "spa_Latn",
            "en": "eng_Latn",
            "fr": "fra_Latn",
            "de": "deu_Latn",
            "it": "ita_Latn",
            "pt": "por_Latn",
            "ru": "rus_Cyrl",
            "zh": "zho_Hans",
            "ja": "jpn_Jpan",
            "ko": "kor_Hang"
        }
        
        logger.info(f"Inicializando modelo de traducción desde {self.model_path}")
    
    def load(self):
        """Carga el modelo en memoria."""
        try:
            logger.info(f"Cargando modelo de traducción desde {self.model_path}")
            
            # Importar las bibliotecas necesarias
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            
            # Cargar modelo y tokenizer
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_path,
                device_map=self.device
            )
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path
            )
            
            logger.info("Modelo de traducción cargado correctamente")
            
            # Mostrar información de memoria si se usa GPU
            if self.device == "cuda" and torch.cuda.is_available():
                logger.info(f"Memoria GPU reservada: {torch.cuda.memory_reserved() / 1024**3:.2f} GB")
                logger.info(f"Memoria GPU en uso: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
            
            return True
        except Exception as e:
            logger.error(f"Error al cargar el modelo de traducción: {e}")
            return False
    
    def translate(self, text: str, source_lang: str = None, target_lang: str = "es") -> str:
        """
        Traduce un texto de un idioma a otro.
        
        Args:
            text: Texto a traducir
            source_lang: Idioma de origen (auto-detectado si es None)
            target_lang: Idioma de destino
            
        Returns:
            Texto traducido
        """
        if self.model is None or self.tokenizer is None:
            logger.warning("El modelo no está cargado. Cargando...")
            if not self.load():
                return "Error: No se pudo cargar el modelo de traducción."
        
        try:
            # Convertir códigos de idioma al formato NLLB
            if source_lang is None:
                # Si no se especifica el idioma de origen, intentar detectarlo
                # En un caso real, aquí se usaría un detector de idioma
                source_lang = "en"  # Por defecto, asumimos inglés
            
            src_lang_code = self.language_codes.get(source_lang, "eng_Latn")
            tgt_lang_code = self.language_codes.get(target_lang, "spa_Latn")
            
            logger.info(f"Traduciendo de {src_lang_code} a {tgt_lang_code}: {text[:50]}...")
            
            # Tokenizar entrada
            inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
            
            # Generar traducción
            with torch.no_grad():
                translated_tokens = self.model.generate(
                    **inputs,
                    forced_bos_token_id=self.tokenizer.lang_code_to_id[tgt_lang_code],
                    max_length=512
                )
            
            # Decodificar traducción
            translated_text = self.tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
            
            logger.info(f"Texto traducido: {translated_text[:50]}...")
            return translated_text
        except Exception as e:
            logger.error(f"Error al traducir texto: {e}")
            return f"Error: {str(e)}"
    
    def unload(self):
        """Libera la memoria del modelo."""
        if self.model is not None:
            del self.model
            self.model = None
        
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        
        # Limpiar caché de CUDA si está disponible
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info("Modelo de traducción descargado de memoria")

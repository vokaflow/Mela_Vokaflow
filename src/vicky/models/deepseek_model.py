"""
Módulo para interactuar con modelos DeepSeek
"""
import os
import logging
import torch
from typing import List, Dict, Any, Optional
import yaml

logger = logging.getLogger("vicky.models.deepseek_model")

class DeepSeekModel:
    """
    Clase para interactuar con modelos DeepSeek
    """
    
    def __init__(self, model_path: str = None, device: str = None, quantization: str = None):
        """
        Inicializa el modelo DeepSeek.
        
        Args:
            model_path: Ruta al modelo
            device: Dispositivo para inferencia (cuda, cpu)
            quantization: Tipo de cuantización (4bit, 8bit, none)
        """
        # Cargar configuración
        config_path = os.environ.get("MODELS_CONFIG", "/opt/vokaflow/config/models.yaml")
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        # Configurar modelo
        self.model_path = model_path or self.config["language_models"]["models"]["deepseek"]["path"]
        self.device = device or self.config["language_models"]["models"]["deepseek"]["device"]
        self.quantization = quantization or self.config["language_models"]["models"]["deepseek"]["quantization"]
        
        self.model = None
        self.tokenizer = None
        
        logger.info(f"Inicializando modelo DeepSeek desde {self.model_path}")
    
    def load(self):
        """Carga el modelo en memoria."""
        try:
            logger.info(f"Cargando modelo DeepSeek desde {self.model_path}")
            
            # Importar las bibliotecas necesarias
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            # Configurar opciones de carga según el tipo de cuantización
            if self.quantization == "4bit":
                from transformers import BitsAndBytesConfig
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True
                )
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    device_map=self.device,
                    quantization_config=quantization_config,
                    trust_remote_code=True
                )
            elif self.quantization == "8bit":
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    device_map=self.device,
                    load_in_8bit=True,
                    trust_remote_code=True
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    device_map=self.device,
                    trust_remote_code=True
                )
            
            # Cargar tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path, 
                trust_remote_code=True
            )
            
            logger.info("Modelo DeepSeek cargado correctamente")
            
            # Mostrar información de memoria si se usa GPU
            if self.device == "cuda" and torch.cuda.is_available():
                logger.info(f"Memoria GPU reservada: {torch.cuda.memory_reserved() / 1024**3:.2f} GB")
                logger.info(f"Memoria GPU en uso: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
            
            return True
        except Exception as e:
            logger.error(f"Error al cargar el modelo DeepSeek: {e}")
            return False
    
    def generate(self, prompt: str, max_length: int = 100, temperature: float = 0.7) -> str:
        """
        Genera texto a partir de un prompt.
        
        Args:
            prompt: Texto de entrada
            max_length: Longitud máxima de la respuesta
            temperature: Temperatura para la generación (mayor = más aleatorio)
            
        Returns:
            Texto generado
        """
        if self.model is None or self.tokenizer is None:
            logger.warning("El modelo no está cargado. Cargando...")
            if not self.load():
                return "Error: No se pudo cargar el modelo DeepSeek."
        
        try:
            logger.info(f"Generando texto para prompt: {prompt[:50]}...")
            
            # Tokenizar entrada
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            # Generar respuesta
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs["input_ids"],
                    max_new_tokens=max_length,
                    do_sample=True,
                    temperature=temperature
                )
            
            # Decodificar respuesta
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extraer solo la respuesta (sin el prompt)
            response = generated_text[len(prompt):].strip()
            
            logger.info(f"Texto generado: {response[:50]}...")
            return response
        except Exception as e:
            logger.error(f"Error al generar texto: {e}")
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
        
        logger.info("Modelo DeepSeek descargado de memoria")

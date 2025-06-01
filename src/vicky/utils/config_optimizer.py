"""
Optimizador de Configuración para VokaFlow
------------------------------------------

Este módulo proporciona funcionalidades para optimizar automáticamente
la configuración del sistema VokaFlow basándose en el rendimiento observado
y los recursos disponibles.

Autor: Equipo VokaFlow
Versión: 1.0.0
"""

import os
import json
import yaml
import logging
import psutil
import time
from typing import Dict, Any, List, Optional, Tuple

# Configurar logger
logger = logging.getLogger("vicky.utils.config_optimizer")

class ConfigOptimizer:
    """
    Optimizador de configuración que ajusta parámetros del sistema
    basándose en métricas de rendimiento y recursos disponibles.
    """
    
    def __init__(self, config_dir: str = "/opt/vokaflow/config"):
        """
        Inicializa el optimizador de configuración.
        
        Args:
            config_dir: Directorio de archivos de configuración
        """
        self.config_dir = config_dir
        self.vicky_config_path = os.path.join(config_dir, "vicky.yaml")
        self.dual_brain_config_path = os.path.join(config_dir, "dual_brain.yaml")
        
        # Cargar configuraciones
        self.vicky_config = self._load_yaml(self.vicky_config_path)
        self.dual_brain_config = self._load_yaml(self.dual_brain_config_path)
        
        # Métricas de rendimiento
        self.performance_metrics = {
            "avg_response_time": 0.0,
            "technical_confidence": 0.0,
            "emotional_confidence": 0.0,
            "memory_usage": 0.0,
            "cpu_usage": 0.0,
            "cache_hit_ratio": 0.0,
            "error_rate": 0.0
        }
        
        # Historial de ajustes
        self.adjustment_history = []
        
        logger.info("Optimizador de configuración inicializado")
    
    def _load_yaml(self, path: str) -> Dict[str, Any]:
        """
        Carga un archivo YAML.
        
        Args:
            path: Ruta al archivo YAML
            
        Returns:
            Diccionario con la configuración
        """
        try:
            if os.path.exists(path):
                with open(path, "r") as f:
                    return yaml.safe_load(f)
            else:
                logger.warning(f"Archivo no encontrado: {path}")
                return {}
        except Exception as e:
            logger.error(f"Error al cargar archivo YAML {path}: {e}")
            return {}
    
    def _save_yaml(self, data: Dict[str, Any], path: str) -> bool:
        """
        Guarda un diccionario como archivo YAML.
        
        Args:
            data: Diccionario a guardar
            path: Ruta donde guardar el archivo
            
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        try:
            with open(path, "w") as f:
                yaml.dump(data, f, default_flow_style=False)
            return True
        except Exception as e:
            logger.error(f"Error al guardar archivo YAML {path}: {e}")
            return False
    
    def update_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Actualiza las métricas de rendimiento.
        
        Args:
            metrics: Diccionario con métricas actualizadas
        """
        for key, value in metrics.items():
            if key in self.performance_metrics:
                self.performance_metrics[key] = value
        
        # Actualizar métricas del sistema
        self.performance_metrics["memory_usage"] = psutil.virtual_memory().percent / 100.0
        self.performance_metrics["cpu_usage"] = psutil.cpu_percent() / 100.0
        
        logger.debug(f"Métricas actualizadas: {self.performance_metrics}")
    
    def optimize_configuration(self) -> Dict[str, Any]:
        """
        Optimiza la configuración basándose en las métricas actuales.
        
        Returns:
            Diccionario con los ajustes realizados
        """
        adjustments = {}
        
        # Optimizar balance de hemisferios
        hemisphere_adjustment = self._optimize_hemisphere_balance()
        if hemisphere_adjustment:
            adjustments["hemisphere_balance"] = hemisphere_adjustment
        
        # Optimizar estrategia de combinación
        strategy_adjustment = self._optimize_combination_strategy()
        if strategy_adjustment:
            adjustments["combination_strategy"] = strategy_adjustment
        
        # Optimizar parámetros de rendimiento
        performance_adjustment = self._optimize_performance_parameters()
        if performance_adjustment:
            adjustments["performance"] = performance_adjustment
        
        # Registrar ajustes
        if adjustments:
            self.adjustment_history.append({
                "timestamp": time.time(),
                "adjustments": adjustments,
                "metrics": self.performance_metrics.copy()
            })
            
            # Guardar configuraciones actualizadas
            self._save_yaml(self.vicky_config, self.vicky_config_path)
            self._save_yaml(self.dual_brain_config, self.dual_brain_config_path)
            
            logger.info(f"Configuración optimizada: {adjustments}")
        else:
            logger.info("No se requieren ajustes de configuración")
        
        return adjustments
    
    def _optimize_hemisphere_balance(self) -> Dict[str, float]:
        """
        Optimiza el balance entre hemisferios técnico y emocional.
        
        Returns:
            Diccionario con los ajustes realizados
        """
        adjustments = {}
        
        # Obtener valores actuales
        technical_weight = self.dual_brain_config.get("hemisphere_balance", {}).get("technical_weight", 0.5)
        emotional_weight = self.dual_brain_config.get("hemisphere_balance", {}).get("emotional_weight", 0.5)
        
        # Analizar métricas
        technical_confidence = self.performance_metrics["technical_confidence"]
        emotional_confidence = self.performance_metrics["emotional_confidence"]
        
        # Ajustar si hay desequilibrio significativo en confianza
        if abs(technical_confidence - emotional_confidence) > 0.2:
            # Si la confianza técnica es mucho menor, aumentar su peso
            if technical_confidence < emotional_confidence - 0.2:
                new_technical = min(0.8, technical_weight + 0.05)
                new_emotional = 1.0 - new_technical
                
                # Actualizar configuración
                if "hemisphere_balance" not in self.dual_brain_config:
                    self.dual_brain_config["hemisphere_balance"] = {}
                
                self.dual_brain_config["hemisphere_balance"]["technical_weight"] = new_technical
                self.dual_brain_config["hemisphere_balance"]["emotional_weight"] = new_emotional
                
                # Actualizar también en vicky_config si existe
                if "dual_brain" in self.vicky_config:
                    self.vicky_config["dual_brain"]["technical_weight"] = new_technical
                    self.vicky_config["dual_brain"]["emotional_weight"] = new_emotional
                
                adjustments["technical_weight"] = new_technical
                adjustments["emotional_weight"] = new_emotional
                
                logger.info(f"Balance de hemisferios ajustado: técnico={new_technical}, emocional={new_emotional}")
            
            # Si la confianza emocional es mucho menor, aumentar su peso
            elif emotional_confidence < technical_confidence - 0.2:
                new_emotional = min(0.8, emotional_weight + 0.05)
                new_technical = 1.0 - new_emotional
                
                # Actualizar configuración
                if "hemisphere_balance" not in self.dual_brain_config:
                    self.dual_brain_config["hemisphere_balance"] = {}
                
                self.dual_brain_config["hemisphere_balance"]["technical_weight"] = new_technical
                self.dual_brain_config["hemisphere_balance"]["emotional_weight"] = new_emotional
                
                # Actualizar también en vicky_config si existe
                if "dual_brain" in self.vicky_config:
                    self.vicky_config["dual_brain"]["technical_weight"] = new_technical
                    self.vicky_config["dual_brain"]["emotional_weight"] = new_emotional
                
                adjustments["technical_weight"] = new_technical
                adjustments["emotional_weight"] = new_emotional
                
                logger.info(f"Balance de hemisferios ajustado: técnico={new_technical}, emocional={new_emotional}")
        
        return adjustments
    
    def _optimize_combination_strategy(self) -> Dict[str, str]:
        """
        Optimiza la estrategia de combinación de respuestas.
        
        Returns:
            Diccionario con los ajustes realizados
        """
        adjustments = {}
        
        # Obtener estrategia actual
        current_strategy = self.dual_brain_config.get("combination_strategy", "integrated")
        
        # Analizar métricas
        avg_response_time = self.performance_metrics["avg_response_time"]
        error_rate = self.performance_metrics["error_rate"]
        
        # Ajustar estrategia según métricas
        new_strategy = current_strategy
        
        # Si el tiempo de respuesta es alto, cambiar a una estrategia más simple
        if avg_response_time > 5.0 and current_strategy == "integrated":
            new_strategy = "selective"
            logger.info(f"Cambiando estrategia a 'selective' debido a alto tiempo de respuesta: {avg_response_time}s")
        
        # Si hay muchos errores, cambiar a una estrategia más robusta
        elif error_rate > 0.1 and current_strategy != "integrated":
            new_strategy = "integrated"
            logger.info(f"Cambiando estrategia a 'integrated' debido a alta tasa de errores: {error_rate}")
        
        # Si el tiempo de respuesta es bueno y la tasa de errores es baja, usar integrated
        elif avg_response_time < 2.0 and error_rate < 0.05 and current_strategy != "integrated":
            new_strategy = "integrated"
            logger.info("Cambiando estrategia a 'integrated' debido a buen rendimiento general")
        
        # Actualizar configuración si cambió
        if new_strategy != current_strategy:
            self.dual_brain_config["combination_strategy"] = new_strategy
            
            # Actualizar también en vicky_config si existe
            if "dual_brain" in self.vicky_config:
                self.vicky_config["dual_brain"]["combination_strategy"] = new_strategy
            
            adjustments["strategy"] = new_strategy
        
        return adjustments
    
    def _optimize_performance_parameters(self) -> Dict[str, Any]:
        """
        Optimiza parámetros de rendimiento.
        
        Returns:
            Diccionario con los ajustes realizados
        """
        adjustments = {}
        
        # Analizar uso de recursos
        memory_usage = self.performance_metrics["memory_usage"]
        cpu_usage = self.performance_metrics["cpu_usage"]
        
        # Ajustar parámetros de caché
        if memory_usage > 0.8:  # Si el uso de memoria es alto (>80%)
            # Reducir tamaño de caché
            if "performance" in self.dual_brain_config and "cache_size" in self.dual_brain_config["performance"]:
                current_cache = self.dual_brain_config["performance"]["cache_size"]
                new_cache = max(50, int(current_cache * 0.7))  # Reducir 30% pero mínimo 50
                
                if new_cache != current_cache:
                    self.dual_brain_config["performance"]["cache_size"] = new_cache
                    adjustments["cache_size"] = new_cache
                    logger.info(f"Tamaño de caché reducido a {new_cache} debido a alto uso de memoria: {memory_usage*100}%")
            
            # Reducir longitud de contexto
            if "memory" in self.dual_brain_config and "max_context_length" in self.dual_brain_config["memory"]:
                current_length = self.dual_brain_config["memory"]["max_context_length"]
                new_length = max(1024, int(current_length * 0.7))  # Reducir 30% pero mínimo 1024
                
                if new_length != current_length:
                    self.dual_brain_config["memory"]["max_context_length"] = new_length
                    adjustments["max_context_length"] = new_length
                    logger.info(f"Longitud de contexto reducida a {new_length} debido a alto uso de memoria: {memory_usage*100}%")
        
        # Ajustar procesamiento paralelo
        if cpu_usage > 0.9:  # Si el uso de CPU es muy alto (>90%)
            if "performance" in self.dual_brain_config and "parallel_processing" in self.dual_brain_config["performance"]:
                if self.dual_brain_config["performance"]["parallel_processing"]:
                    self.dual_brain_config["performance"]["parallel_processing"] = False
                    adjustments["parallel_processing"] = False
                    logger.info(f"Procesamiento paralelo desactivado debido a alto uso de CPU: {cpu_usage*100}%")
        
        return adjustments
    
    def get_adjustment_history(self) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de ajustes realizados.
        
        Returns:
            Lista de ajustes con timestamps
        """
        return self.adjustment_history
    
    def get_recommended_configuration(self) -> Dict[str, Any]:
        """
        Obtiene una configuración recomendada basada en el sistema actual.
        
        Returns:
            Diccionario con configuración recomendada
        """
        # Detectar recursos del sistema
        total_memory = psutil.virtual_memory().total / (1024 * 1024 * 1024)  # GB
        cpu_count = psutil.cpu_count(logical=True)
        
        # Configuración base
        recommended = {
            "system_resources": {
                "memory_gb": round(total_memory, 2),
                "cpu_cores": cpu_count
            },
            "recommended_settings": {
                "hemisphere_balance": {
                    "technical_weight": 0.55,
                    "emotional_weight": 0.45
                },
                "performance": {
                    "parallel_processing": cpu_count > 2,
                    "worker_threads": max(2, cpu_count - 1),
                    "cache_size": int(min(300, total_memory * 50)),  # 50 entradas por GB, máx 300
                    "max_context_length": int(min(8192, total_memory * 2048))  # 2048 tokens por GB, máx 8192
                }
            }
        }
        
        return recommended

"""
Módulo de detección de anomalías para el sistema de seguridad de VokaFlow.

Este módulo implementa algoritmos de aprendizaje automático para detectar
comportamientos anómalos que podrían indicar amenazas de seguridad.
"""

import os
import time
import json
import pickle
import logging
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict

# Configuración de logging
logger = logging.getLogger("vicky.security.anomaly")

class AnomalyDetector:
    """
    Detector de anomalías basado en aprendizaje automático.
    
    Utiliza una combinación de técnicas estadísticas y de aprendizaje automático
    para identificar patrones anómalos en el comportamiento de los usuarios y sistemas.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_path = config.get("model_path", "models/anomaly_detector.pkl")
        self.threshold = config.get("threshold", 0.75)
        self.feature_names = config.get("feature_names", [])
        
        # Historial de comportamiento por usuario
        self.user_history = defaultdict(list)
        self.max_history_per_user = config.get("max_history_per_user", 1000)
        
        # Cargar modelo pre-entrenado si existe
        self.model = self._load_model()
        
        # Inicializar detector de outliers basado en estadísticas
        self.statistical_detector = StatisticalOutlierDetector(
            config.get("statistical_detector", {})
        )
        
        # Inicializar detector basado en reglas
        self.rule_detector = RuleBasedDetector(
            config.get("rule_detector", {})
        )
        
        logger.info("Detector de anomalías inicializado")
    
    def _load_model(self):
        """Carga el modelo de ML desde el archivo."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    model = pickle.load(f)
                logger.info(f"Modelo cargado desde {self.model_path}")
                return model
            except Exception as e:
                logger.error(f"Error al cargar modelo: {str(e)}")
        
        logger.warning(f"Modelo no encontrado en {self.model_path}, usando detector estadístico")
        return None
    
    def predict(self, features: Dict[str, Any]) -> float:
        """
        Predice la puntuación de anomalía para un conjunto de características.
        
        Args:
            features: Diccionario con características de la solicitud
            
        Returns:
            float: Puntuación de anomalía entre 0 y 1 (mayor = más anómalo)
        """
        # Actualizar historial del usuario
        user_id = features.get("user_id", "unknown")
        self._update_user_history(user_id, features)
        
        # Combinar múltiples métodos de detección
        scores = []
        
        # 1. Detección basada en ML si el modelo está disponible
        if self.model is not None:
            try:
                ml_score = self._predict_with_model(features)
                scores.append(ml_score * 0.6)  # Ponderación del 60%
            except Exception as e:
                logger.error(f"Error en predicción ML: {str(e)}")
        
        # 2. Detección estadística
        stat_score = self.statistical_detector.detect(user_id, features)
        scores.append(stat_score * 0.3)  # Ponderación del 30%
        
        # 3. Detección basada en reglas
        rule_score = self.rule_detector.detect(features)
        scores.append(rule_score * 0.1)  # Ponderación del 10%
        
        # Calcular puntuación final
        final_score = sum(scores)
        
        # Registrar si es anómalo
        if final_score > self.threshold:
            logger.warning(f"Anomalía detectada para usuario {user_id} con puntuación {final_score:.2f}")
            self._log_anomaly(user_id, features, final_score)
        
        return final_score
    
    def _predict_with_model(self, features: Dict[str, Any]) -> float:
        """Realiza predicción usando el modelo de ML."""
        # Convertir características a formato esperado por el modelo
        feature_vector = self._prepare_features(features)
        
        # Realizar predicción
        prediction = self.model.predict_proba([feature_vector])[0, 1]
        return float(prediction)
    
    def _prepare_features(self, features: Dict[str, Any]) -> List[float]:
        """Prepara las características en el formato esperado por el modelo."""
        # Si tenemos nombres de características definidos, usarlos para ordenar
        if self.feature_names:
            return [float(features.get(name, 0)) for name in self.feature_names]
        
        # De lo contrario, usar valores numéricos
        return [float(v) for k, v in features.items() if isinstance(v, (int, float))]
    
    def _update_user_history(self, user_id: str, features: Dict[str, Any]) -> None:
        """Actualiza el historial de comportamiento de un usuario."""
        # Añadir timestamp
        features_with_time = {**features, "timestamp": time.time()}
        
        # Añadir al historial
        self.user_history[user_id].append(features_with_time)
        
        # Limitar tamaño del historial
        if len(self.user_history[user_id]) > self.max_history_per_user:
            self.user_history[user_id] = self.user_history[user_id][-self.max_history_per_user:]
    
    def _log_anomaly(self, user_id: str, features: Dict[str, Any], score: float) -> None:
        """Registra una anomalía detectada."""
        anomaly_data = {
            "timestamp": time.time(),
            "user_id": user_id,
            "score": score,
            "features": features
        }
        
        # En producción, esto podría enviar a un sistema de alertas o SIEM
        logger.warning(f"ANOMALÍA: {json.dumps(anomaly_data)}")
    
    def train(self, training_data: List[Dict[str, Any]], labels: List[int]) -> None:
        """
        Entrena o actualiza el modelo con nuevos datos.
        
        Args:
            training_data: Lista de diccionarios con características
            labels: Lista de etiquetas (0 = normal, 1 = anómalo)
        """
        # Esta función sería implementada en un entorno real para actualizar el modelo
        # con nuevos datos de entrenamiento
        logger.info("Entrenamiento de modelo solicitado (no implementado en esta versión)")


class StatisticalOutlierDetector:
    """Detector de anomalías basado en estadísticas."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.z_score_threshold = config.get("z_score_threshold", 3.0)
        self.min_samples = config.get("min_samples", 10)
        self.feature_stats = defaultdict(dict)  # {user_id: {feature: (mean, std)}}
    
    def detect(self, user_id: str, features: Dict[str, Any]) -> float:
        """
        Detecta anomalías usando estadísticas del comportamiento del usuario.
        
        Returns:
            float: Puntuación de anomalía entre 0 y 1
        """
        # Seleccionar características numéricas
        numeric_features = {k: v for k, v in features.items() if isinstance(v, (int, float))}
        
        if not numeric_features:
            return 0.0
        
        # Calcular puntuaciones Z para cada característica
        z_scores = []
        
        for feature, value in numeric_features.items():
            # Obtener estadísticas para esta característica y usuario
            stats = self.feature_stats.get(user_id, {}).get(feature)
            
            if stats and stats[2] >= self.min_samples:  # Tenemos suficientes muestras
                mean, std, count = stats
                if std > 0:
                    z_score = abs((value - mean) / std)
                    z_scores.append(z_score)
            
            # Actualizar estadísticas
            self._update_stats(user_id, feature, value)
        
        # Si no tenemos suficientes datos para calcular z-scores, devolver 0
        if not z_scores:
            return 0.0
        
        # Calcular puntuación final basada en el máximo z-score
        max_z = max(z_scores)
        
        # Normalizar a [0, 1]
        score = min(max_z / self.z_score_threshold, 1.0)
        
        return score
    
    def _update_stats(self, user_id: str, feature: str, value: float) -> None:
        """Actualiza las estadísticas para un usuario y característica."""
        if user_id not in self.feature_stats:
            self.feature_stats[user_id] = {}
        
        if feature not in self.feature_stats[user_id]:
            # Inicializar con el primer valor (media, desv. estándar, conteo)
            self.feature_stats[user_id][feature] = (value, 0.0, 1)
            return
        
        # Actualizar estadísticas usando el algoritmo de Welford para cálculo online
        mean, std, count = self.feature_stats[user_id][feature]
        count += 1
        
        # Actualizar media
        delta = value - mean
        mean += delta / count
        
        # Actualizar varianza/desviación estándar
        delta2 = value - mean
        std = np.sqrt((std**2 * (count - 2) + delta * delta2) / (count - 1)) if count > 1 else 0.0
        
        # Guardar estadísticas actualizadas
        self.feature_stats[user_id][feature] = (mean, std, count)


class RuleBasedDetector:
    """Detector de anomalías basado en reglas predefinidas."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rules = config.get("rules", [])
    
    def detect(self, features: Dict[str, Any]) -> float:
        """
        Evalúa reglas predefinidas para detectar comportamientos anómalos.
        
        Returns:
            float: Puntuación de anomalía entre 0 y 1
        """
        max_score = 0.0
        
        for rule in self.rules:
            rule_type = rule.get("type", "")
            
            if rule_type == "threshold":
                feature = rule.get("feature", "")
                threshold = rule.get("threshold", 0)
                operator = rule.get("operator", ">")
                score = rule.get("score", 0.5)
                
                if feature in features:
                    value = features[feature]
                    
                    if operator == ">" and value > threshold:
                        max_score = max(max_score, score)
                    elif operator == ">=" and value >= threshold:
                        max_score = max(max_score, score)
                    elif operator == "<" and value < threshold:
                        max_score = max(max_score, score)
                    elif operator == "<=" and value <= threshold:
                        max_score = max(max_score, score)
                    elif operator == "==" and value == threshold:
                        max_score = max(max_score, score)
                    elif operator == "!=" and value != threshold:
                        max_score = max(max_score, score)
            
            elif rule_type == "combination":
                conditions = rule.get("conditions", [])
                score = rule.get("score", 0.8)
                
                if all(self._check_condition(cond, features) for cond in conditions):
                    max_score = max(max_score, score)
        
        return max_score
    
    def _check_condition(self, condition: Dict[str, Any], features: Dict[str, Any]) -> bool:
        """Evalúa una condición individual de una regla."""
        feature = condition.get("feature", "")
        operator = condition.get("operator", "==")
        value = condition.get("value")
        
        if feature not in features:
            return False
        
        feature_value = features[feature]
        
        if operator == "==":
            return feature_value == value
        elif operator == "!=":
            return feature_value != value
        elif operator == ">":
            return feature_value > value
        elif operator == ">=":
            return feature_value >= value
        elif operator == "<":
            return feature_value < value
        elif operator == "<=":
            return feature_value <= value
        elif operator == "in":
            return feature_value in value
        elif operator == "not_in":
            return feature_value not in value
        elif operator == "contains":
            return value in feature_value
        elif operator == "not_contains":
            return value not in feature_value
        
        return False

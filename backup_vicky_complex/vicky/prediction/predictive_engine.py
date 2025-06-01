"""
Motor de Predicción Anticipada para VokaFlow

Este módulo implementa un sistema avanzado de predicción que utiliza:
- Análisis de series temporales
- Machine Learning para detección de patrones
- Predicción de fallos y anomalías
- Optimización proactiva de recursos
- Recomendaciones inteligentes
"""

import os
import time
import json
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import pickle
import warnings
warnings.filterwarnings('ignore')

# Configuración de logging
logger = logging.getLogger("vicky.prediction")

class PredictionType(Enum):
    """Tipos de predicción soportados."""
    SYSTEM_FAILURE = "system_failure"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SECURITY_THREAT = "security_threat"
    USER_BEHAVIOR = "user_behavior"
    MAINTENANCE_NEED = "maintenance_need"
    CAPACITY_PLANNING = "capacity_planning"

class PredictionConfidence(Enum):
    """Niveles de confianza en las predicciones."""
    LOW = 0.3
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.95

@dataclass
class PredictionResult:
    """Resultado de una predicción."""
    prediction_type: PredictionType
    predicted_value: Union[float, bool, str]
    confidence: float
    time_horizon: int  # minutos hasta el evento predicho
    probability: float  # probabilidad del evento (0-1)
    contributing_factors: List[str]
    recommended_actions: List[str]
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    timestamp: float = field(default_factory=time.time)
    model_used: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TimeSeriesData:
    """Datos de series temporales para análisis."""
    timestamps: List[float]
    values: List[float]
    metric_name: str
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class TimeSeriesAnalyzer:
    """Analizador de series temporales para detección de patrones y tendencias."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.window_size = config.get("window_size", 100)
        self.trend_threshold = config.get("trend_threshold", 0.05)
        self.seasonality_periods = config.get("seasonality_periods", [24, 168])  # horas, semanas
        
    def analyze_trend(self, data: TimeSeriesData) -> Dict[str, Any]:
        """Analiza la tendencia en una serie temporal."""
        if len(data.values) < 10:
            return {"trend": "insufficient_data", "slope": 0, "confidence": 0}
        
        # Convertir a arrays numpy
        x = np.array(data.timestamps)
        y = np.array(data.values)
        
        # Calcular tendencia usando regresión lineal
        coeffs = np.polyfit(x, y, 1)
        slope = coeffs[0]
        
        # Calcular R²
        y_pred = np.polyval(coeffs, x)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Determinar dirección de la tendencia
        if abs(slope) < self.trend_threshold:
            trend = "stable"
        elif slope > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        return {
            "trend": trend,
            "slope": float(slope),
            "r_squared": float(r_squared),
            "confidence": float(r_squared),
            "prediction_accuracy": self._calculate_prediction_accuracy(y, y_pred)
        }
    
    def detect_anomalies(self, data: TimeSeriesData) -> List[Dict[str, Any]]:
        """Detecta anomalías en la serie temporal."""
        if len(data.values) < 20:
            return []
        
        values = np.array(data.values)
        timestamps = np.array(data.timestamps)
        
        # Método 1: Z-score
        z_scores = np.abs((values - np.mean(values)) / np.std(values))
        z_anomalies = np.where(z_scores > 3)[0]
        
        # Método 2: IQR
        q1, q3 = np.percentile(values, [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        iqr_anomalies = np.where((values < lower_bound) | (values > upper_bound))[0]
        
        # Combinar anomalías
        all_anomalies = np.unique(np.concatenate([z_anomalies, iqr_anomalies]))
        
        anomalies = []
        for idx in all_anomalies:
            anomalies.append({
                "timestamp": float(timestamps[idx]),
                "value": float(values[idx]),
                "z_score": float(z_scores[idx]),
                "severity": self._classify_anomaly_severity(z_scores[idx]),
                "type": "statistical_outlier"
            })
        
        return anomalies
    
    def predict_future_values(self, data: TimeSeriesData, horizon_minutes: int = 60) -> Dict[str, Any]:
        """Predice valores futuros basándose en patrones históricos."""
        if len(data.values) < 50:
            return {"error": "insufficient_data"}
        
        # Preparar datos
        df = pd.DataFrame({
            'timestamp': pd.to_datetime(data.timestamps, unit='s'),
            'value': data.values
        })
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)
        
        try:
            # Método simple: extrapolación de tendencia
            trend_analysis = self.analyze_trend(data)
            
            # Calcular intervalos de predicción
            last_timestamp = data.timestamps[-1]
            future_timestamps = []
            future_values = []
            
            # Generar predicciones para el horizonte especificado
            for i in range(1, horizon_minutes + 1):
                future_time = last_timestamp + (i * 60)  # cada minuto
                future_timestamps.append(future_time)
                
                # Predicción basada en tendencia
                predicted_value = data.values[-1] + (trend_analysis["slope"] * i * 60)
                future_values.append(predicted_value)
            
            # Calcular intervalos de confianza
            std_dev = np.std(data.values)
            confidence_interval = 1.96 * std_dev  # 95% de confianza
            
            return {
                "future_timestamps": future_timestamps,
                "predicted_values": future_values,
                "confidence_interval": float(confidence_interval),
                "trend_slope": trend_analysis["slope"],
                "prediction_confidence": trend_analysis["confidence"],
                "method": "linear_extrapolation"
            }
            
        except Exception as e:
            logger.error(f"Error en predicción de valores futuros: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_prediction_accuracy(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """Calcula la precisión de la predicción."""
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        accuracy = max(0, 100 - mape) / 100
        return float(accuracy)
    
    def _classify_anomaly_severity(self, z_score: float) -> str:
        """Clasifica la severidad de una anomalía basándose en el z-score."""
        if z_score > 4:
            return "CRITICAL"
        elif z_score > 3.5:
            return "HIGH"
        elif z_score > 3:
            return "MEDIUM"
        else:
            return "LOW"

class PatternRecognizer:
    """Reconocedor de patrones para identificar comportamientos recurrentes."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.min_pattern_length = config.get("min_pattern_length", 5)
        self.max_pattern_length = config.get("max_pattern_length", 50)
        self.similarity_threshold = config.get("similarity_threshold", 0.8)
        
    def find_recurring_patterns(self, data: TimeSeriesData) -> List[Dict[str, Any]]:
        """Encuentra patrones recurrentes en los datos."""
        if len(data.values) < self.min_pattern_length * 2:
            return []
        
        values = np.array(data.values)
        patterns = []
        
        # Buscar patrones de diferentes longitudes
        for pattern_length in range(self.min_pattern_length, 
                                   min(self.max_pattern_length, len(values) // 2)):
            
            # Extraer todos los sub-patrones de esta longitud
            for start_idx in range(len(values) - pattern_length):
                pattern = values[start_idx:start_idx + pattern_length]
                
                # Buscar repeticiones de este patrón
                matches = self._find_pattern_matches(values, pattern, start_idx + pattern_length)
                
                if len(matches) >= 2:  # Al menos 2 repeticiones
                    patterns.append({
                        "pattern": pattern.tolist(),
                        "length": pattern_length,
                        "occurrences": len(matches) + 1,
                        "positions": [start_idx] + matches,
                        "average_interval": self._calculate_average_interval(
                            [start_idx] + matches, data.timestamps
                        ),
                        "confidence": self._calculate_pattern_confidence(pattern, matches, values)
                    })
        
        # Filtrar y ordenar patrones por confianza
        patterns = [p for p in patterns if p["confidence"] > self.similarity_threshold]
        patterns.sort(key=lambda x: x["confidence"], reverse=True)
        
        return patterns[:10]  # Devolver top 10 patrones
    
    def predict_next_occurrence(self, pattern: Dict[str, Any], current_time: float) -> Optional[float]:
        """Predice cuándo ocurrirá la siguiente instancia de un patrón."""
        if pattern["average_interval"] <= 0:
            return None
        
        # Calcular tiempo estimado de la siguiente ocurrencia
        last_occurrence_time = max(pattern["positions"]) * 60  # convertir a segundos
        next_occurrence = last_occurrence_time + pattern["average_interval"]
        
        return next_occurrence
    
    def _find_pattern_matches(self, data: np.ndarray, pattern: np.ndarray, start_search: int) -> List[int]:
        """Encuentra coincidencias de un patrón en los datos."""
        matches = []
        pattern_length = len(pattern)
        
        for i in range(start_search, len(data) - pattern_length + 1):
            candidate = data[i:i + pattern_length]
            similarity = self._calculate_similarity(pattern, candidate)
            
            if similarity > self.similarity_threshold:
                matches.append(i)
        
        return matches
    
    def _calculate_similarity(self, pattern1: np.ndarray, pattern2: np.ndarray) -> float:
        """Calcula la similitud entre dos patrones."""
        # Normalizar patrones
        p1_norm = (pattern1 - np.mean(pattern1)) / (np.std(pattern1) + 1e-8)
        p2_norm = (pattern2 - np.mean(pattern2)) / (np.std(pattern2) + 1e-8)
        
        # Calcular correlación
        correlation = np.corrcoef(p1_norm, p2_norm)[0, 1]
        
        # Manejar NaN
        if np.isnan(correlation):
            correlation = 0
        
        return abs(correlation)
    
    def _calculate_average_interval(self, positions: List[int], timestamps: List[float]) -> float:
        """Calcula el intervalo promedio entre ocurrencias de un patrón."""
        if len(positions) < 2:
            return 0
        
        intervals = []
        for i in range(1, len(positions)):
            # Convertir posiciones a tiempo real
            time_diff = timestamps[positions[i]] - timestamps[positions[i-1]]
            intervals.append(time_diff)
        
        return np.mean(intervals) if intervals else 0
    
    def _calculate_pattern_confidence(self, pattern: np.ndarray, matches: List[int], data: np.ndarray) -> float:
        """Calcula la confianza en un patrón basándose en la calidad de las coincidencias."""
        if not matches:
            return 0
        
        similarities = []
        for match_pos in matches:
            candidate = data[match_pos:match_pos + len(pattern)]
            if len(candidate) == len(pattern):
                similarity = self._calculate_similarity(pattern, candidate)
                similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0

class PredictiveModel:
    """Modelo predictivo basado en machine learning."""
    
    def __init__(self, model_type: str, config: Dict[str, Any]):
        self.model_type = model_type
        self.config = config
        self.model = None
        self.is_trained = False
        self.feature_names = []
        self.model_path = config.get("model_path", f"models/{model_type}_model.pkl")
        
        # Cargar modelo si existe
        self._load_model()
    
    def _load_model(self) -> bool:
        """Carga un modelo pre-entrenado."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.model = model_data['model']
                    self.feature_names = model_data.get('feature_names', [])
                    self.is_trained = True
                logger.info(f"Modelo {self.model_type} cargado desde {self.model_path}")
                return True
            except Exception as e:
                logger.error(f"Error al cargar modelo {self.model_type}: {str(e)}")
        return False
    
    def train(self, training_data: List[Dict[str, Any]], labels: List[Any]) -> bool:
        """Entrena el modelo con datos de entrenamiento."""
        try:
            # Preparar características
            features_df = pd.DataFrame(training_data)
            self.feature_names = list(features_df.columns)
            
            # Seleccionar algoritmo basado en el tipo de modelo
            if self.model_type == "classification":
                from sklearn.ensemble import RandomForestClassifier
                self.model = RandomForestClassifier(
                    n_estimators=100,
                    random_state=42,
                    **self.config.get("model_params", {})
                )
            elif self.model_type == "regression":
                from sklearn.ensemble import RandomForestRegressor
                self.model = RandomForestRegressor(
                    n_estimators=100,
                    random_state=42,
                    **self.config.get("model_params", {})
                )
            elif self.model_type == "anomaly":
                from sklearn.ensemble import IsolationForest
                self.model = IsolationForest(
                    contamination=0.1,
                    random_state=42,
                    **self.config.get("model_params", {})
                )
            else:
                logger.error(f"Tipo de modelo no soportado: {self.model_type}")
                return False
            
            # Entrenar modelo
            X = features_df.values
            if self.model_type == "anomaly":
                self.model.fit(X)
            else:
                self.model.fit(X, labels)
            
            self.is_trained = True
            
            # Guardar modelo
            self._save_model()
            
            logger.info(f"Modelo {self.model_type} entrenado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error al entrenar modelo {self.model_type}: {str(e)}")
            return False
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza una predicción con el modelo."""
        if not self.is_trained or self.model is None:
            return {"error": "Modelo no entrenado"}
        
        try:
            # Preparar características
            feature_vector = [features.get(name, 0) for name in self.feature_names]
            X = np.array(feature_vector).reshape(1, -1)
            
            # Realizar predicción
            if self.model_type == "classification":
                prediction = self.model.predict(X)[0]
                probabilities = self.model.predict_proba(X)[0]
                confidence = max(probabilities)
                
                return {
                    "prediction": prediction,
                    "confidence": float(confidence),
                    "probabilities": probabilities.tolist()
                }
            
            elif self.model_type == "regression":
                prediction = self.model.predict(X)[0]
                
                # Estimar confianza basándose en la varianza de los árboles
                if hasattr(self.model, 'estimators_'):
                    tree_predictions = [tree.predict(X)[0] for tree in self.model.estimators_]
                    confidence = 1.0 - (np.std(tree_predictions) / (np.mean(tree_predictions) + 1e-8))
                    confidence = max(0, min(1, confidence))
                else:
                    confidence = 0.8  # Valor por defecto
                
                return {
                    "prediction": float(prediction),
                    "confidence": float(confidence)
                }
            
            elif self.model_type == "anomaly":
                anomaly_score = self.model.decision_function(X)[0]
                is_anomaly = self.model.predict(X)[0] == -1
                
                return {
                    "is_anomaly": bool(is_anomaly),
                    "anomaly_score": float(anomaly_score),
                    "confidence": float(abs(anomaly_score))
                }
            
        except Exception as e:
            logger.error(f"Error en predicción del modelo {self.model_type}: {str(e)}")
            return {"error": str(e)}
    
    def _save_model(self) -> bool:
        """Guarda el modelo entrenado."""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            model_data = {
                'model': self.model,
                'feature_names': self.feature_names,
                'model_type': self.model_type,
                'config': self.config
            }
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Modelo {self.model_type} guardado en {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error al guardar modelo {self.model_type}: {str(e)}")
            return False

class PredictiveEngine:
    """Motor principal de predicción anticipada."""
    
    def __init__(self, config_path: str = None):
        # Cargar configuración
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = self._get_default_config()
        
        # Inicializar componentes
        self.time_series_analyzer = TimeSeriesAnalyzer(
            self.config.get("time_series", {})
        )
        self.pattern_recognizer = PatternRecognizer(
            self.config.get("pattern_recognition", {})
        )
        
        # Inicializar modelos predictivos
        self.models = {}
        for model_name, model_config in self.config.get("models", {}).items():
            self.models[model_name] = PredictiveModel(
                model_config["type"], 
                model_config
            )
        
        # Almacenamiento de datos históricos
        self.historical_data = {}
        self.max_history_points = self.config.get("max_history_points", 10000)
        
        # Caché de predicciones
        self.prediction_cache = {}
        self.cache_ttl = self.config.get("cache_ttl", 300)  # 5 minutos
        
        logger.info("Motor de predicción anticipada inicializado")
    
    def add_data_point(self, metric_name: str, value: float, timestamp: float = None, metadata: Dict[str, Any] = None) -> None:
        """Añade un punto de datos para análisis predictivo."""
        if timestamp is None:
            timestamp = time.time()
        
        if metric_name not in self.historical_data:
            self.historical_data[metric_name] = TimeSeriesData(
                timestamps=[],
                values=[],
                metric_name=metric_name,
                source="system",
                metadata=metadata or {}
            )
        
        # Añadir punto de datos
        self.historical_data[metric_name].timestamps.append(timestamp)
        self.historical_data[metric_name].values.append(value)
        
        # Limitar tamaño del historial
        if len(self.historical_data[metric_name].values) > self.max_history_points:
            # Mantener solo los puntos más recientes
            keep_count = int(self.max_history_points * 0.8)  # Mantener 80%
            self.historical_data[metric_name].timestamps = \
                self.historical_data[metric_name].timestamps[-keep_count:]
            self.historical_data[metric_name].values = \
                self.historical_data[metric_name].values[-keep_count:]
    
    def predict_system_failure(self, system_metrics: Dict[str, float]) -> PredictionResult:
        """Predice la probabilidad de fallo del sistema."""
        # Verificar caché
        cache_key = f"system_failure_{hash(str(sorted(system_metrics.items())))}"
        cached_result = self._get_cached_prediction(cache_key)
        if cached_result:
            return cached_result
        
        # Analizar métricas críticas
        critical_metrics = ["cpu_usage", "memory_usage", "disk_usage", "error_rate"]
        risk_factors = []
        overall_risk = 0.0
        
        for metric in critical_metrics:
            if metric in system_metrics:
                value = system_metrics[metric]
                
                # Analizar tendencia si tenemos datos históricos
                if metric in self.historical_data:
                    trend_analysis = self.time_series_analyzer.analyze_trend(
                        self.historical_data[metric]
                    )
                    
                    # Evaluar riesgo basado en valor actual y tendencia
                    if metric.endswith("_usage"):
                        # Para métricas de uso, valores altos son riesgosos
                        if value > 90:
                            risk_factors.append(f"{metric} crítico: {value}%")
                            overall_risk += 0.4
                        elif value > 80:
                            risk_factors.append(f"{metric} alto: {value}%")
                            overall_risk += 0.2
                        
                        # Tendencia creciente en uso es riesgosa
                        if trend_analysis["trend"] == "increasing" and trend_analysis["confidence"] > 0.7:
                            risk_factors.append(f"{metric} tendencia creciente")
                            overall_risk += 0.1
                    
                    elif metric == "error_rate":
                        # Para tasa de errores, cualquier valor alto es riesgoso
                        if value > 5:
                            risk_factors.append(f"Tasa de errores alta: {value}%")
                            overall_risk += 0.3
                        
                        if trend_analysis["trend"] == "increasing":
                            risk_factors.append("Errores en aumento")
                            overall_risk += 0.2
        
        # Usar modelo ML si está disponible
        if "system_failure" in self.models:
            ml_prediction = self.models["system_failure"].predict(system_metrics)
            if "error" not in ml_prediction:
                ml_risk = ml_prediction.get("probabilities", [0, 0])[1]  # Probabilidad de fallo
                overall_risk = (overall_risk + ml_risk) / 2  # Promedio con análisis heurístico
        
        # Limitar riesgo a [0, 1]
        overall_risk = min(1.0, overall_risk)
        
        # Determinar tiempo hasta posible fallo
        if overall_risk > 0.8:
            time_horizon = 15  # 15 minutos
            severity = "CRITICAL"
        elif overall_risk > 0.6:
            time_horizon = 60  # 1 hora
            severity = "HIGH"
        elif overall_risk > 0.4:
            time_horizon = 240  # 4 horas
            severity = "MEDIUM"
        else:
            time_horizon = 1440  # 24 horas
            severity = "LOW"
        
        # Generar recomendaciones
        recommendations = self._generate_failure_recommendations(risk_factors, system_metrics)
        
        result = PredictionResult(
            prediction_type=PredictionType.SYSTEM_FAILURE,
            predicted_value=overall_risk > 0.5,
            confidence=0.8,
            time_horizon=time_horizon,
            probability=overall_risk,
            contributing_factors=risk_factors,
            recommended_actions=recommendations,
            severity=severity,
            model_used="hybrid_heuristic_ml"
        )
        
        # Guardar en caché
        self._cache_prediction(cache_key, result)
        
        return result
    
    def predict_resource_exhaustion(self, resource_metrics: Dict[str, float]) -> List[PredictionResult]:
        """Predice cuándo se agotarán los recursos del sistema."""
        predictions = []
        
        resource_thresholds = {
            "cpu_usage": 95,
            "memory_usage": 95,
            "disk_usage": 90,
            "network_bandwidth": 90
        }
        
        for resource, current_value in resource_metrics.items():
            if resource not in resource_thresholds:
                continue
            
            threshold = resource_thresholds[resource]
            
            # Analizar tendencia si tenemos datos históricos
            if resource in self.historical_data:
                data = self.historical_data[resource]
                trend_analysis = self.time_series_analyzer.analyze_trend(data)
                
                if trend_analysis["trend"] == "increasing" and trend_analysis["slope"] > 0:
                    # Calcular tiempo hasta alcanzar el umbral
                    remaining_capacity = threshold - current_value
                    if remaining_capacity > 0 and trend_analysis["slope"] > 0:
                        # Tiempo en segundos hasta alcanzar el umbral
                        time_to_threshold = remaining_capacity / trend_analysis["slope"]
                        time_horizon_minutes = int(time_to_threshold / 60)
                        
                        # Limitar a un rango razonable
                        time_horizon_minutes = max(5, min(10080, time_horizon_minutes))  # 5 min a 1 semana
                        
                        # Determinar severidad basada en tiempo restante
                        if time_horizon_minutes < 30:
                            severity = "CRITICAL"
                            confidence = 0.9
                        elif time_horizon_minutes < 120:
                            severity = "HIGH"
                            confidence = 0.8
                        elif time_horizon_minutes < 1440:
                            severity = "MEDIUM"
                            confidence = 0.7
                        else:
                            severity = "LOW"
                            confidence = 0.6
                        
                        # Generar recomendaciones específicas para el recurso
                        recommendations = self._generate_resource_recommendations(resource, current_value, time_horizon_minutes)
                        
                        prediction = PredictionResult(
                            prediction_type=PredictionType.RESOURCE_EXHAUSTION,
                            predicted_value=f"{resource}_exhaustion",
                            confidence=confidence,
                            time_horizon=time_horizon_minutes,
                            probability=min(1.0, current_value / threshold),
                            contributing_factors=[f"{resource} tendencia creciente: {trend_analysis['slope']:.4f}/s"],
                            recommended_actions=recommendations,
                            severity=severity,
                            model_used="trend_extrapolation",
                            metadata={"resource": resource, "current_value": current_value, "threshold": threshold}
                        )
                        
                        predictions.append(prediction)
        
        return predictions
    
    def predict_performance_degradation(self, performance_metrics: Dict[str, float]) -> PredictionResult:
        """Predice degradación del rendimiento del sistema."""
        # Métricas clave de rendimiento
        key_metrics = ["response_time", "throughput", "latency", "queue_size"]
        degradation_indicators = []
        degradation_score = 0.0
        
        for metric in key_metrics:
            if metric in performance_metrics:
                current_value = performance_metrics[metric]
                
                # Analizar anomalías en datos históricos
                if metric in self.historical_data:
                    data = self.historical_data[metric]
                    anomalies = self.time_series_analyzer.detect_anomalies(data)
                    
                    # Verificar si el valor actual es anómalo
                    if anomalies:
                        recent_anomalies = [a for a in anomalies if time.time() - a["timestamp"] < 3600]  # Última hora
                        if recent_anomalies:
                            degradation_indicators.append(f"{metric} muestra anomalías recientes")
                            degradation_score += 0.2
                    
                    # Analizar tendencia
                    trend_analysis = self.time_series_analyzer.analyze_trend(data)
                    
                    # Para métricas donde el aumento es malo (response_time, latency, queue_size)
                    if metric in ["response_time", "latency", "queue_size"]:
                        if trend_analysis["trend"] == "increasing" and trend_analysis["confidence"] > 0.6:
                            degradation_indicators.append(f"{metric} tendencia creciente")
                            degradation_score += 0.15
                    
                    # Para métricas donde la disminución es mala (throughput)
                    elif metric == "throughput":
                        if trend_analysis["trend"] == "decreasing" and trend_analysis["confidence"] > 0.6:
                            degradation_indicators.append(f"{metric} tendencia decreciente")
                            degradation_score += 0.15
        
        # Usar modelo ML si está disponible
        if "performance_degradation" in self.models:
            ml_prediction = self.models["performance_degradation"].predict(performance_metrics)
            if "error" not in ml_prediction:
                ml_score = ml_prediction.get("prediction", 0)
                degradation_score = (degradation_score + ml_score) / 2
        
        # Limitar puntuación
        degradation_score = min(1.0, degradation_score)
        
        # Determinar severidad y tiempo
        if degradation_score > 0.7:
            severity = "HIGH"
            time_horizon = 30
            confidence = 0.8
        elif degradation_score > 0.5:
            severity = "MEDIUM"
            time_horizon = 120
            confidence = 0.7
        elif degradation_score > 0.3:
            severity = "LOW"
            time_horizon = 480
            confidence = 0.6
        else:
            severity = "LOW"
            time_horizon = 1440
            confidence = 0.5
        
        # Generar recomendaciones
        recommendations = self._generate_performance_recommendations(degradation_indicators, performance_metrics)
        
        return PredictionResult(
            prediction_type=PredictionType.PERFORMANCE_DEGRADATION,
            predicted_value=degradation_score > 0.5,
            confidence=confidence,
            time_horizon=time_horizon,
            probability=degradation_score,
            contributing_factors=degradation_indicators,
            recommended_actions=recommendations,
            severity=severity,
            model_used="hybrid_anomaly_trend"
        )
    
    def predict_maintenance_needs(self, system_health_metrics: Dict[str, float]) -> List[PredictionResult]:
        """Predice necesidades de mantenimiento del sistema."""
        predictions = []
        
        # Componentes que requieren mantenimiento
        maintenance_components = {
            "database": ["db_connections", "query_time", "lock_waits"],
            "cache": ["cache_hit_ratio", "cache_memory_usage", "eviction_rate"],
            "storage": ["disk_io_wait", "disk_fragmentation", "backup_age"],
            "network": ["packet_loss", "bandwidth_utilization", "connection_errors"]
        }
        
        for component, metrics in maintenance_components.items():
            component_score = 0.0
            component_issues = []
            
            for metric in metrics:
                if metric in system_health_metrics:
                    value = system_health_metrics[metric]
                    
                    # Evaluar cada métrica según su tipo
                    if metric == "cache_hit_ratio" and value < 0.8:
                        component_issues.append(f"Baja tasa de aciertos en caché: {value:.2f}")
                        component_score += 0.3
                    elif metric == "disk_fragmentation" and value > 0.3:
                        component_issues.append(f"Alta fragmentación de disco: {value:.2f}")
                        component_score += 0.4
                    elif metric == "backup_age" and value > 24:  # horas
                        component_issues.append(f"Backup desactualizado: {value} horas")
                        component_score += 0.5
                    elif metric == "packet_loss" and value > 0.01:
                        component_issues.append(f"Pérdida de paquetes: {value:.3f}")
                        component_score += 0.3
            
            # Si hay problemas en el componente, crear predicción de mantenimiento
            if component_score > 0.2:
                # Determinar urgencia
                if component_score > 0.6:
                    severity = "HIGH"
                    time_horizon = 24  # 24 horas
                elif component_score > 0.4:
                    severity = "MEDIUM"
                    time_horizon = 168  # 1 semana
                else:
                    severity = "LOW"
                    time_horizon = 720  # 1 mes
                
                # Generar recomendaciones específicas
                recommendations = self._generate_maintenance_recommendations(component, component_issues)
                
                prediction = PredictionResult(
                    prediction_type=PredictionType.MAINTENANCE_NEED,
                    predicted_value=f"{component}_maintenance",
                    confidence=min(0.9, component_score + 0.3),
                    time_horizon=time_horizon,
                    probability=min(1.0, component_score),
                    contributing_factors=component_issues,
                    recommended_actions=recommendations,
                    severity=severity,
                    model_used="rule_based_health_check",
                    metadata={"component": component}
                )
                
                predictions.append(prediction)
        
        return predictions
    
    def get_comprehensive_forecast(self, current_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Genera un pronóstico completo del sistema."""
        # Añadir métricas actuales al historial
        current_time = time.time()
        for metric, value in current_metrics.items():
            self.add_data_point(metric, value, current_time)
        
        # Generar todas las predicciones
        predictions = {
            "system_failure": self.predict_system_failure(current_metrics),
            "resource_exhaustion": self.predict_resource_exhaustion(current_metrics),
            "performance_degradation": self.predict_performance_degradation(current_metrics),
            "maintenance_needs": self.predict_maintenance_needs(current_metrics)
        }
        
        # Calcular riesgo general del sistema
        all_predictions = []
        for pred_type, pred_result in predictions.items():
            if isinstance(pred_result, list):
                all_predictions.extend(pred_result)
            else:
                all_predictions.append(pred_result)
        
        # Calcular puntuación de riesgo general
        if all_predictions:
            risk_scores = [p.probability for p in all_predictions]
            overall_risk = max(risk_scores)  # Usar el riesgo más alto
            
            # Encontrar la predicción más crítica
            critical_predictions = [p for p in all_predictions if p.severity in ["CRITICAL", "HIGH"]]
            most_urgent = min(all_predictions, key=lambda x: x.time_horizon) if all_predictions else None
        else:
            overall_risk = 0.0
            critical_predictions = []
            most_urgent = None
        
        # Generar recomendaciones prioritarias
        priority_actions = []
        if critical_predictions:
            for pred in critical_predictions[:3]:  # Top 3 más críticas
                priority_actions.extend(pred.recommended_actions[:2])  # Top 2 acciones por predicción
        
        return {
            "timestamp": current_time,
            "overall_risk_score": overall_risk,
            "risk_level": self._classify_risk_level(overall_risk),
            "predictions": {k: v.__dict__ if not isinstance(v, list) else [p.__dict__ for p in v] 
                          for k, v in predictions.items()},
            "critical_predictions_count": len(critical_predictions),
            "most_urgent_prediction": most_urgent.__dict__ if most_urgent else None,
            "priority_actions": list(set(priority_actions)),  # Eliminar duplicados
            "forecast_horizon_hours": 24,
            "confidence_level": "MEDIUM",
            "next_analysis_recommended": current_time + 1800  # 30 minutos
        }
    
    def _generate_failure_recommendations(self, risk_factors: List[str], metrics: Dict[str, float]) -> List[str]:
        """Genera recomendaciones para prevenir fallos del sistema."""
        recommendations = []
        
        for factor in risk_factors:
            if "cpu" in factor.lower():
                recommendations.extend([
                    "Escalar recursos de CPU o optimizar procesos intensivos",
                    "Revisar procesos con alto uso de CPU",
                    "Implementar balanceador de carga si es necesario"
                ])
            elif "memory" in factor.lower() or "memoria" in factor.lower():
                recommendations.extend([
                    "Aumentar memoria RAM disponible",
                    "Optimizar uso de memoria en aplicaciones",
                    "Implementar limpieza de caché automática"
                ])
            elif "disk" in factor.lower() or "disco" in factor.lower():
                recommendations.extend([
                    "Liberar espacio en disco eliminando archivos temporales",
                    "Implementar rotación de logs automática",
                    "Considerar expansión de almacenamiento"
                ])
            elif "error" in factor.lower():
                recommendations.extend([
                    "Investigar y corregir errores recurrentes",
                    "Implementar manejo de errores más robusto",
                    "Revisar logs de aplicación para identificar causas"
                ])
        
        return list(set(recommendations))  # Eliminar duplicados
    
    def _generate_resource_recommendations(self, resource: str, current_value: float, time_horizon: int) -> List[str]:
        """Genera recomendaciones específicas para agotamiento de recursos."""
        recommendations = []
        
        if resource == "cpu_usage":
            recommendations = [
                "Escalar horizontalmente añadiendo más instancias",
                "Optimizar algoritmos y consultas de base de datos",
                "Implementar caché para reducir carga de procesamiento",
                "Revisar y optimizar procesos en background"
            ]
        elif resource == "memory_usage":
            recommendations = [
                "Aumentar memoria RAM del sistema",
                "Optimizar gestión de memoria en aplicaciones",
                "Implementar paginación o lazy loading",
                "Revisar memory leaks en aplicaciones"
            ]
        elif resource == "disk_usage":
            recommendations = [
                "Limpiar archivos temporales y logs antiguos",
                "Implementar compresión de datos",
                "Mover datos antiguos a almacenamiento secundario",
                "Expandir capacidad de almacenamiento"
            ]
        elif resource == "network_bandwidth":
            recommendations = [
                "Optimizar transferencia de datos",
                "Implementar compresión de red",
                "Revisar y optimizar consultas de API",
                "Considerar CDN para contenido estático"
            ]
        
        # Añadir urgencia basada en tiempo restante
        if time_horizon < 60:
            recommendations.insert(0, f"URGENTE: Acción inmediata requerida en {time_horizon} minutos")
        
        return recommendations
    
    def _generate_performance_recommendations(self, indicators: List[str], metrics: Dict[str, float]) -> List[str]:
        """Genera recomendaciones para mejorar el rendimiento."""
        recommendations = []
        
        for indicator in indicators:
            if "response_time" in indicator:
                recommendations.extend([
                    "Optimizar consultas de base de datos",
                    "Implementar caché de respuestas",
                    "Revisar y optimizar código de aplicación",
                    "Considerar uso de CDN"
                ])
            elif "throughput" in indicator:
                recommendations.extend([
                    "Escalar horizontalmente el sistema",
                    "Optimizar pool de conexiones",
                    "Implementar procesamiento asíncrono",
                    "Revisar cuellos de botella en la arquitectura"
                ])
            elif "latency" in indicator:
                recommendations.extend([
                    "Optimizar red y conectividad",
                    "Implementar caché local",
                    "Revisar configuración de timeouts",
                    "Optimizar serialización de datos"
                ])
            elif "queue_size" in indicator:
                recommendations.extend([
                    "Aumentar workers para procesamiento",
                    "Implementar priorización de tareas",
                    "Optimizar procesamiento de cola",
                    "Considerar particionamiento de colas"
                ])
        
        return list(set(recommendations))
    
    def _generate_maintenance_recommendations(self, component: str, issues: List[str]) -> List[str]:
        """Genera recomendaciones de mantenimiento específicas."""
        recommendations = []
        
        if component == "database":
            recommendations = [
                "Ejecutar VACUUM y ANALYZE en PostgreSQL",
                "Revisar y optimizar índices",
                "Actualizar estadísticas de la base de datos",
                "Verificar integridad de datos"
            ]
        elif component == "cache":
            recommendations = [
                "Limpiar caché expirado manualmente",
                "Ajustar configuración de TTL",
                "Revisar patrones de acceso a caché",
                "Considerar aumento de memoria de caché"
            ]
        elif component == "storage":
            recommendations = [
                "Desfragmentar discos duros",
                "Ejecutar backup completo del sistema",
                "Verificar salud de discos (SMART)",
                "Limpiar archivos temporales y logs antiguos"
            ]
        elif component == "network":
            recommendations = [
                "Revisar configuración de red",
                "Actualizar drivers de red",
                "Verificar cables y conexiones físicas",
                "Optimizar configuración de firewall"
            ]
        
        return recommendations
    
    def _classify_risk_level(self, risk_score: float) -> str:
        """Clasifica el nivel de riesgo basado en la puntuación."""
        if risk_score >= 0.8:
            return "CRITICAL"
        elif risk_score >= 0.6:
            return "HIGH"
        elif risk_score >= 0.4:
            return "MEDIUM"
        elif risk_score >= 0.2:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _get_cached_prediction(self, cache_key: str) -> Optional[PredictionResult]:
        """Obtiene una predicción del caché si es válida."""
        if cache_key in self.prediction_cache:
            prediction, timestamp = self.prediction_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return prediction
        return None
    
    def _cache_prediction(self, cache_key: str, prediction: PredictionResult) -> None:
        """Almacena una predicción en el caché."""
        self.prediction_cache[cache_key] = (prediction, time.time())
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Devuelve la configuración por defecto."""
        return {
            "time_series": {
                "window_size": 100,
                "trend_threshold": 0.05,
                "seasonality_periods": [24, 168]
            },
            "pattern_recognition": {
                "min_pattern_length": 5,
                "max_pattern_length": 50,
                "similarity_threshold": 0.8
            },
            "models": {
                "system_failure": {
                    "type": "classification",
                    "model_path": "models/system_failure_model.pkl",
                    "model_params": {"n_estimators": 100, "max_depth": 10}
                },
                "performance_degradation": {
                    "type": "regression",
                    "model_path": "models/performance_model.pkl",
                    "model_params": {"n_estimators": 100, "max_depth": 8}
                }
            },
            "max_history_points": 10000,
            "cache_ttl": 300
        }


# Función de inicialización
def initialize_predictive_engine(config_path: str = None) -> PredictiveEngine:
    """Inicializa y devuelve una instancia del motor de predicción."""
    return PredictiveEngine(config_path)

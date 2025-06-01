"""
Servicio de Alertas Predictivas para VokaFlow

Este módulo gestiona las alertas basadas en predicciones,
incluyendo notificaciones, escalamiento y seguimiento.
"""

import time
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from datetime import datetime, timedelta

from .predictive_engine import PredictionResult, PredictionType

logger = logging.getLogger("vicky.prediction.alerts")

class AlertSeverity(Enum):
    """Severidad de las alertas."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(Enum):
    """Estado de las alertas."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

@dataclass
class Alert:
    """Representación de una alerta predictiva."""
    id: str
    prediction: PredictionResult
    severity: AlertSeverity
    status: AlertStatus
    created_at: float
    title: str
    description: str
    affected_systems: List[str] = field(default_factory=list)
    escalation_level: int = 0
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[float] = None
    resolved_at: Optional[float] = None
    suppressed_until: Optional[float] = None
    notification_channels: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class NotificationChannel:
    """Canal de notificación para alertas."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.enabled = config.get("enabled", True)
        self.severity_filter = config.get("severity_filter", [])
        self.rate_limit = config.get("rate_limit", 60)  # segundos entre notificaciones
        self.last_notification = 0
    
    async def send_notification(self, alert: Alert) -> bool:
        """Envía una notificación para la alerta."""
        # Verificar filtros de severidad
        if self.severity_filter and alert.severity.value not in self.severity_filter:
            return False
        
        # Verificar rate limiting
        current_time = time.time()
        if current_time - self.last_notification < self.rate_limit:
            return False
        
        try:
            success = await self._send_notification_impl(alert)
            if success:
                self.last_notification = current_time
            return success
        except Exception as e:
            logger.error(f"Error enviando notificación por {self.name}: {str(e)}")
            return False
    
    async def _send_notification_impl(self, alert: Alert) -> bool:
        """Implementación específica del canal de notificación."""
        # Esta función debe ser sobrescrita por canales específicos
        logger.info(f"Notificación enviada por {self.name}: {alert.title}")
        return True

class EmailNotificationChannel(NotificationChannel):
    """Canal de notificación por email."""
    
    async def _send_notification_impl(self, alert: Alert) -> bool:
        """Envía notificación por email."""
        # Aquí iría la implementación real de envío de email
        email_config = self.config.get("email", {})
        recipients = email_config.get("recipients", [])
        
        if not recipients:
            return False
        
        # Simular envío de email
        logger.info(f"Email enviado a {recipients}: {alert.title}")
        return True

class SlackNotificationChannel(NotificationChannel):
    """Canal de notificación por Slack."""
    
    async def _send_notification_impl(self, alert: Alert) -> bool:
        """Envía notificación por Slack."""
        slack_config = self.config.get("slack", {})
        webhook_url = slack_config.get("webhook_url")
        
        if not webhook_url:
            return False
        
        # Aquí iría la implementación real de Slack
        logger.info(f"Slack notification sent: {alert.title}")
        return True

class SMSNotificationChannel(NotificationChannel):
    """Canal de notificación por SMS."""
    
    async def _send_notification_impl(self, alert: Alert) -> bool:
        """Envía notificación por SMS."""
        sms_config = self.config.get("sms", {})
        phone_numbers = sms_config.get("phone_numbers", [])
        
        if not phone_numbers:
            return False
        
        # Aquí iría la implementación real de SMS
        logger.info(f"SMS sent to {phone_numbers}: {alert.title}")
        return True

class AlertService:
    """Servicio principal de gestión de alertas predictivas."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.max_history = config.get("max_history", 1000)
        
        # Configurar canales de notificación
        self.notification_channels: Dict[str, NotificationChannel] = {}
        self._setup_notification_channels()
        
        # Configurar reglas de escalamiento
        self.escalation_rules = config.get("escalation_rules", [])
        
        # Configurar supresión de alertas
        self.suppression_rules = config.get("suppression_rules", [])
        
        # Configurar agrupación de alertas
        self.grouping_rules = config.get("grouping_rules", [])
        
        # Tareas de background
        self.background_tasks = []
        
        logger.info("Servicio de alertas predictivas inicializado")
    
    def _setup_notification_channels(self) -> None:
        """Configura los canales de notificación."""
        channels_config = self.config.get("notification_channels", {})
        
        for channel_name, channel_config in channels_config.items():
            channel_type = channel_config.get("type", "generic")
            
            if channel_type == "email":
                channel = EmailNotificationChannel(channel_name, channel_config)
            elif channel_type == "slack":
                channel = SlackNotificationChannel(channel_name, channel_config)
            elif channel_type == "sms":
                channel = SMSNotificationChannel(channel_name, channel_config)
            else:
                channel = NotificationChannel(channel_name, channel_config)
            
            self.notification_channels[channel_name] = channel
    
    async def create_alert_from_prediction(self, prediction: PredictionResult) -> Optional[Alert]:
        """Crea una alerta basada en una predicción."""
        # Verificar si ya existe una alerta similar activa
        existing_alert = self._find_similar_alert(prediction)
        if existing_alert:
            # Actualizar alerta existente en lugar de crear una nueva
            return await self._update_existing_alert(existing_alert, prediction)
        
        # Verificar reglas de supresión
        if self._is_suppressed(prediction):
            logger.info(f"Alerta suprimida para predicción: {prediction.prediction_type.value}")
            return None
        
        # Generar ID único para la alerta
        alert_id = f"pred_{prediction.prediction_type.value}_{int(time.time())}"
        
        # Determinar severidad de la alerta
        alert_severity = self._map_prediction_to_alert_severity(prediction)
        
        # Generar título y descripción
        title, description = self._generate_alert_content(prediction)
        
        # Determinar sistemas afectados
        affected_systems = self._identify_affected_systems(prediction)
        
        # Determinar canales de notificación
        notification_channels = self._select_notification_channels(alert_severity, prediction)
        
        # Crear alerta
        alert = Alert(
            id=alert_id,
            prediction=prediction,
            severity=alert_severity,
            status=AlertStatus.ACTIVE,
            created_at=time.time(),
            title=title,
            description=description,
            affected_systems=affected_systems,
            notification_channels=notification_channels,
            metadata={
                "prediction_confidence": prediction.confidence,
                "time_horizon_minutes": prediction.time_horizon,
                "auto_generated": True
            }
        )
        
        # Registrar alerta
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Limitar historial
        if len(self.alert_history) > self.max_history:
            self.alert_history = self.alert_history[-self.max_history:]
        
        # Enviar notificaciones
        await self._send_alert_notifications(alert)
        
        # Programar escalamiento si es necesario
        self._schedule_escalation(alert)
        
        logger.info(f"Alerta creada: {alert_id} - {title}")
        
        return alert
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Reconoce una alerta."""
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        if alert.status != AlertStatus.ACTIVE:
            return False
        
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_by = acknowledged_by
        alert.acknowledged_at = time.time()
        
        logger.info(f"Alerta reconocida: {alert_id} por {acknowledged_by}")
        
        # Notificar reconocimiento
        await self._notify_alert_status_change(alert, "acknowledged")
        
        return True
    
    async def resolve_alert(self, alert_id: str, resolved_by: str, resolution_notes: str = "") -> bool:
        """Resuelve una alerta."""
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = time.time()
        alert.metadata["resolved_by"] = resolved_by
        alert.metadata["resolution_notes"] = resolution_notes
        
        # Mover de alertas activas a historial
        del self.active_alerts[alert_id]
        
        logger.info(f"Alerta resuelta: {alert_id} por {resolved_by}")
        
        # Notificar resolución
        await self._notify_alert_status_change(alert, "resolved")
        
        return True
    
    async def suppress_alert(self, alert_id: str, suppressed_by: str, duration_minutes: int = 60) -> bool:
        """Suprime una alerta temporalmente."""
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.SUPPRESSED
        alert.suppressed_until = time.time() + (duration_minutes * 60)
        alert.metadata["suppressed_by"] = suppressed_by
        
        logger.info(f"Alerta suprimida: {alert_id} por {duration_minutes} minutos")
        
        return True
    
    def get_active_alerts(self, severity_filter: Optional[List[str]] = None) -> List[Alert]:
        """Obtiene las alertas activas, opcionalmente filtradas por severidad."""
        alerts = list(self.active_alerts.values())
        
        if severity_filter:
            alerts = [a for a in alerts if a.severity.value in severity_filter]
        
        # Ordenar por severidad y tiempo de creación
        severity_order = {"critical": 0, "error": 1, "warning": 2, "info": 3}
        alerts.sort(key=lambda x: (severity_order.get(x.severity.value, 4), -x.created_at))
        
        return alerts
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de las alertas."""
        active_alerts = list(self.active_alerts.values())
        
        # Contar por severidad
        severity_counts = {}
        for severity in AlertSeverity:
            severity_counts[severity.value] = len([a for a in active_alerts if a.severity == severity])
        
        # Contar por tipo de predicción
        prediction_type_counts = {}
        for alert in active_alerts:
            pred_type = alert.prediction.prediction_type.value
            prediction_type_counts[pred_type] = prediction_type_counts.get(pred_type, 0) + 1
        
        # Calcular tiempo promedio de resolución (últimas 24 horas)
        recent_resolved = [
            a for a in self.alert_history 
            if a.status == AlertStatus.RESOLVED and 
               a.resolved_at and 
               time.time() - a.resolved_at < 86400
        ]
        
        avg_resolution_time = 0
        if recent_resolved:
            resolution_times = [a.resolved_at - a.created_at for a in recent_resolved]
            avg_resolution_time = sum(resolution_times) / len(resolution_times) / 60  # en minutos
        
        return {
            "active_alerts_count": len(active_alerts),
            "severity_breakdown": severity_counts,
            "prediction_type_breakdown": prediction_type_counts,
            "average_resolution_time_minutes": avg_resolution_time,
            "total_alerts_today": len([
                a for a in self.alert_history 
                if time.time() - a.created_at < 86400
            ]),
            "escalated_alerts": len([a for a in active_alerts if a.escalation_level > 0])
        }
    
    def _find_similar_alert(self, prediction: PredictionResult) -> Optional[Alert]:
        """Busca una alerta similar activa para evitar duplicados."""
        for alert in self.active_alerts.values():
            # Verificar si es el mismo tipo de predicción
            if alert.prediction.prediction_type == prediction.prediction_type:
                # Verificar si afecta sistemas similares
                if alert.prediction.metadata.get("resource") == prediction.metadata.get("resource"):
                    # Verificar si está dentro de una ventana de tiempo razonable
                    time_diff = abs(alert.created_at - time.time())
                    if time_diff < 3600:  # 1 hora
                        return alert
        return None
    
    async def _update_existing_alert(self, existing_alert: Alert, new_prediction: PredictionResult) -> Alert:
        """Actualiza una alerta existente con nueva información de predicción."""
        # Actualizar la predicción si la nueva es más severa o más confiable
        if (new_prediction.probability > existing_alert.prediction.probability or
            new_prediction.confidence > existing_alert.prediction.confidence):
            existing_alert.prediction = new_prediction
            
            # Actualizar severidad si es necesario
            new_severity = self._map_prediction_to_alert_severity(new_prediction)
            if new_severity.value != existing_alert.severity.value:
                existing_alert.severity = new_severity
                # Enviar notificación de escalamiento
                await self._notify_alert_escalation(existing_alert)
        
        # Actualizar timestamp de última actualización
        existing_alert.metadata["last_updated"] = time.time()
        existing_alert.metadata["update_count"] = existing_alert.metadata.get("update_count", 0) + 1
        
        logger.info(f"Alerta actualizada: {existing_alert.id}")
        return existing_alert
    
    def _is_suppressed(self, prediction: PredictionResult) -> bool:
        """Verifica si una predicción debe ser suprimida según las reglas."""
        for rule in self.suppression_rules:
            if self._matches_suppression_rule(prediction, rule):
                return True
        return False
    
    def _matches_suppression_rule(self, prediction: PredictionResult, rule: Dict[str, Any]) -> bool:
        """Verifica si una predicción coincide con una regla de supresión."""
        # Verificar tipo de predicción
        if "prediction_types" in rule:
            if prediction.prediction_type.value not in rule["prediction_types"]:
                return False
        
        # Verificar severidad
        if "severities" in rule:
            alert_severity = self._map_prediction_to_alert_severity(prediction)
            if alert_severity.value not in rule["severities"]:
                return False
        
        # Verificar confianza mínima
        if "min_confidence" in rule:
            if prediction.confidence < rule["min_confidence"]:
                return True  # Suprimir predicciones de baja confianza
        
        # Verificar horario (si está configurado)
        if "time_windows" in rule:
            current_hour = datetime.now().hour
            for window in rule["time_windows"]:
                if window["start"] <= current_hour <= window["end"]:
                    return True
        
        return False
    
    def _map_prediction_to_alert_severity(self, prediction: PredictionResult) -> AlertSeverity:
        """Mapea la severidad de una predicción a la severidad de alerta."""
        if prediction.severity == "CRITICAL":
            return AlertSeverity.CRITICAL
        elif prediction.severity == "HIGH":
            return AlertSeverity.ERROR
        elif prediction.severity == "MEDIUM":
            return AlertSeverity.WARNING
        else:
            return AlertSeverity.INFO
    
    def _generate_alert_content(self, prediction: PredictionResult) -> Tuple[str, str]:
        """Genera título y descripción para la alerta."""
        pred_type = prediction.prediction_type.value
        
        # Mapeo de tipos de predicción a títulos legibles
        title_map = {
            "system_failure": "Posible Fallo del Sistema",
            "resource_exhaustion": "Agotamiento de Recursos",
            "performance_degradation": "Degradación del Rendimiento",
            "security_threat": "Amenaza de Seguridad",
            "maintenance_need": "Mantenimiento Requerido",
            "capacity_planning": "Planificación de Capacidad"
        }
        
        title = title_map.get(pred_type, f"Predicción: {pred_type}")
        
        # Añadir información de tiempo si es crítico
        if prediction.time_horizon < 60:
            title += f" (en {prediction.time_horizon} min)"
        
        # Generar descripción detallada
        description_parts = [
            f"Tipo: {prediction.prediction_type.value}",
            f"Probabilidad: {prediction.probability:.1%}",
            f"Confianza: {prediction.confidence:.1%}",
            f"Tiempo estimado: {prediction.time_horizon} minutos",
            f"Severidad: {prediction.severity}"
        ]
        
        if prediction.contributing_factors:
            description_parts.append("Factores contribuyentes:")
            for factor in prediction.contributing_factors[:3]:  # Limitar a 3
                description_parts.append(f"• {factor}")
        
        if prediction.recommended_actions:
            description_parts.append("Acciones recomendadas:")
            for action in prediction.recommended_actions[:3]:  # Limitar a 3
                description_parts.append(f"• {action}")
        
        description = "\n".join(description_parts)
        
        return title, description
    
    def _identify_affected_systems(self, prediction: PredictionResult) -> List[str]:
        """Identifica los sistemas afectados por la predicción."""
        affected_systems = []
        
        # Basado en el tipo de predicción
        if prediction.prediction_type == PredictionType.SYSTEM_FAILURE:
            affected_systems = ["core_system", "database", "api"]
        elif prediction.prediction_type == PredictionType.RESOURCE_EXHAUSTION:
            resource = prediction.metadata.get("resource", "unknown")
            affected_systems = [f"resource_{resource}"]
        elif prediction.prediction_type == PredictionType.PERFORMANCE_DEGRADATION:
            affected_systems = ["application", "database", "network"]
        elif prediction.prediction_type == PredictionType.MAINTENANCE_NEED:
            component = prediction.metadata.get("component", "unknown")
            affected_systems = [component]
        
        return affected_systems
    
    def _select_notification_channels(self, severity: AlertSeverity, prediction: PredictionResult) -> List[str]:
        """Selecciona los canales de notificación apropiados."""
        channels = []
        
        # Canales basados en severidad
        if severity == AlertSeverity.CRITICAL:
            channels = ["email", "sms", "slack"]
        elif severity == AlertSeverity.ERROR:
            channels = ["email", "slack"]
        elif severity == AlertSeverity.WARNING:
            channels = ["slack"]
        else:
            channels = ["email"]
        
        # Filtrar canales habilitados
        enabled_channels = [name for name, channel in self.notification_channels.items() 
                          if channel.enabled and name in channels]
        
        return enabled_channels
    
    async def _send_alert_notifications(self, alert: Alert) -> None:
        """Envía notificaciones para una alerta."""
        tasks = []
        
        for channel_name in alert.notification_channels:
            if channel_name in self.notification_channels:
                channel = self.notification_channels[channel_name]
                task = asyncio.create_task(channel.send_notification(alert))
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful_notifications = sum(1 for r in results if r is True)
            logger.info(f"Notificaciones enviadas para alerta {alert.id}: {successful_notifications}/{len(tasks)}")
    
    def _schedule_escalation(self, alert: Alert) -> None:
        """Programa el escalamiento automático de una alerta."""
        for rule in self.escalation_rules:
            if self._matches_escalation_rule(alert, rule):
                escalation_delay = rule.get("delay_minutes", 30) * 60
                
                # Programar tarea de escalamiento
                async def escalate_later():
                    await asyncio.sleep(escalation_delay)
                    await self._escalate_alert(alert, rule)
                
                task = asyncio.create_task(escalate_later())
                self.background_tasks.append(task)
                break
    
    def _matches_escalation_rule(self, alert: Alert, rule: Dict[str, Any]) -> bool:
        """Verifica si una alerta coincide con una regla de escalamiento."""
        # Verificar severidad
        if "severities" in rule:
            if alert.severity.value not in rule["severities"]:
                return False
        
        # Verificar tipos de predicción
        if "prediction_types" in rule:
            if alert.prediction.prediction_type.value not in rule["prediction_types"]:
                return False
        
        return True
    
    async def _escalate_alert(self, alert: Alert, rule: Dict[str, Any]) -> None:
        """Escala una alerta según una regla."""
        # Verificar si la alerta sigue activa y no ha sido reconocida
        if (alert.id not in self.active_alerts or 
            alert.status != AlertStatus.ACTIVE):
            return
        
        alert.escalation_level += 1
        
        # Añadir canales de escalamiento
        escalation_channels = rule.get("escalation_channels", [])
        for channel in escalation_channels:
            if channel not in alert.notification_channels:
                alert.notification_channels.append(channel)
        
        # Enviar notificación de escalamiento
        await self._notify_alert_escalation(alert)
        
        logger.warning(f"Alerta escalada: {alert.id} (nivel {alert.escalation_level})")
    
    async def _notify_alert_status_change(self, alert: Alert, status: str) -> None:
        """Notifica cambios de estado de alerta."""
        # Crear notificación simple para cambios de estado
        notification_text = f"Alerta {alert.id}: {status.upper()}"
        
        # Enviar solo por canales de baja prioridad
        low_priority_channels = ["slack"]
        
        for channel_name in low_priority_channels:
            if channel_name in self.notification_channels:
                channel = self.notification_channels[channel_name]
                # Crear alerta temporal para notificación
                temp_alert = Alert(
                    id=f"{alert.id}_status",
                    prediction=alert.prediction,
                    severity=AlertSeverity.INFO,
                    status=AlertStatus.ACTIVE,
                    created_at=time.time(),
                    title=notification_text,
                    description=f"Estado de alerta cambiado a: {status}"
                )
                await channel.send_notification(temp_alert)
    
    async def _notify_alert_escalation(self, alert: Alert) -> None:
        """Notifica el escalamiento de una alerta."""
        escalation_alert = Alert(
            id=f"{alert.id}_escalation",
            prediction=alert.prediction,
            severity=AlertSeverity.ERROR,
            status=AlertStatus.ACTIVE,
            created_at=time.time(),
            title=f"ESCALAMIENTO: {alert.title}",
            description=f"Alerta escalada al nivel {alert.escalation_level}\n\n{alert.description}"
        )
        
        await self._send_alert_notifications(escalation_alert)
    
    async def cleanup_expired_alerts(self) -> None:
        """Limpia alertas expiradas y supresiones."""
        current_time = time.time()
        
        # Reactivar alertas suprimidas que han expirado
        for alert in list(self.active_alerts.values()):
            if (alert.status == AlertStatus.SUPPRESSED and 
                alert.suppressed_until and 
                current_time > alert.suppressed_until):
                alert.status = AlertStatus.ACTIVE
                alert.suppressed_until = None
                logger.info(f"Alerta reactivada después de supresión: {alert.id}")
        
        # Limpiar tareas de background completadas
        self.background_tasks = [task for task in self.background_tasks if not task.done()]


# Función de inicialización
def initialize_alert_service(config: Dict[str, Any]) -> AlertService:
    """Inicializa y devuelve una instancia del servicio de alertas."""
    return AlertService(config)

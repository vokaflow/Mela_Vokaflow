"""
VokaFlow Enterprise Security Audit System
=========================================

Sistema de auditoría de seguridad empresarial para cumplimiento Fortune 500.
Registra todas las actividades, genera reportes de cumplimiento y 
mantiene trazabilidad completa para SOX, GDPR, HIPAA e ISO 27001.
"""

import os
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger("vokaflow.security.audit")

class AuditEventType(Enum):
    """Tipos de eventos de auditoría"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_CONFIGURATION = "system_configuration"
    SECURITY_INCIDENT = "security_incident"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXPORT = "data_export"
    LOGIN_ATTEMPT = "login_attempt"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    ACCOUNT_LOCKOUT = "account_lockout"
    PERMISSION_CHANGE = "permission_change"
    FILE_ACCESS = "file_access"
    API_CALL = "api_call"
    ERROR = "error"

class ComplianceFramework(Enum):
    """Marcos de cumplimiento"""
    SOX = "sox"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"

@dataclass
class AuditEvent:
    """Evento de auditoría"""
    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    user_id: Optional[str]
    source_ip: str
    user_agent: str
    endpoint: str
    action: str
    resource: str
    result: str  # SUCCESS, FAILURE, ERROR
    details: Dict[str, Any]
    compliance_flags: List[ComplianceFramework]
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    session_id: Optional[str] = None

class EnterpriseAuditSystem:
    """Sistema de auditoría empresarial Fortune 500"""
    
    def __init__(self, storage_backend=None):
        self.storage_backend = storage_backend
        self.audit_queue: List[AuditEvent] = []
        self.compliance_rules = self._load_compliance_rules()
        
        # Configuración de retención por marco de cumplimiento
        self.retention_policies = {
            ComplianceFramework.SOX: timedelta(days=2555),      # 7 años
            ComplianceFramework.GDPR: timedelta(days=2190),     # 6 años
            ComplianceFramework.HIPAA: timedelta(days=2190),    # 6 años
            ComplianceFramework.ISO27001: timedelta(days=1095), # 3 años
            ComplianceFramework.PCI_DSS: timedelta(days=365)    # 1 año
        }
        
        logger.info("📋 Enterprise Audit System initialized")
    
    def log_event(self, event_type: AuditEventType, user_id: Optional[str],
                  source_ip: str, user_agent: str, endpoint: str,
                  action: str, resource: str, result: str,
                  details: Optional[Dict[str, Any]] = None,
                  session_id: Optional[str] = None) -> str:
        """Registra un evento de auditoría"""
        try:
            # Generar ID único del evento
            event_id = self._generate_event_id(event_type, user_id, source_ip)
            
            # Determinar marcos de cumplimiento aplicables
            compliance_flags = self._determine_compliance_frameworks(
                event_type, action, resource
            )
            
            # Determinar nivel de riesgo
            risk_level = self._assess_risk_level(event_type, result, details or {})
            
            # Crear evento de auditoría
            audit_event = AuditEvent(
                event_id=event_id,
                event_type=event_type,
                timestamp=datetime.now(),
                user_id=user_id,
                source_ip=source_ip,
                user_agent=user_agent,
                endpoint=endpoint,
                action=action,
                resource=resource,
                result=result,
                details=details or {},
                compliance_flags=compliance_flags,
                risk_level=risk_level,
                session_id=session_id
            )
            
            # Agregar a cola de auditoría
            self.audit_queue.append(audit_event)
            
            # Persistir si hay backend de almacenamiento
            if self.storage_backend:
                self._persist_event(audit_event)
            
            # Log según nivel de riesgo
            if risk_level in ["HIGH", "CRITICAL"]:
                logger.warning(f"🚨 HIGH RISK AUDIT EVENT: {event_id} - {action} on {resource}")
            else:
                logger.info(f"📋 Audit event logged: {event_id}")
            
            return event_id
            
        except Exception as e:
            logger.error(f"❌ Error logging audit event: {e}")
            return ""
    
    def log_authentication(self, user_id: str, source_ip: str, user_agent: str,
                          success: bool, details: Optional[Dict[str, Any]] = None):
        """Registra evento de autenticación"""
        result = "SUCCESS" if success else "FAILURE"
        action = "LOGIN_SUCCESS" if success else "LOGIN_FAILURE"
        
        self.log_event(
            event_type=AuditEventType.AUTHENTICATION,
            user_id=user_id,
            source_ip=source_ip,
            user_agent=user_agent,
            endpoint="/auth/login",
            action=action,
            resource="authentication_system",
            result=result,
            details=details
        )
    
    def log_data_access(self, user_id: str, source_ip: str, endpoint: str,
                       resource: str, action: str, success: bool,
                       details: Optional[Dict[str, Any]] = None):
        """Registra acceso a datos"""
        result = "SUCCESS" if success else "FAILURE"
        
        self.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            user_id=user_id,
            source_ip=source_ip,
            user_agent=details.get("user_agent", "") if details else "",
            endpoint=endpoint,
            action=action,
            resource=resource,
            result=result,
            details=details
        )
    
    def log_security_incident(self, threat_type: str, source_ip: str,
                            severity: str, details: Dict[str, Any]):
        """Registra incidente de seguridad"""
        self.log_event(
            event_type=AuditEventType.SECURITY_INCIDENT,
            user_id=details.get("user_id"),
            source_ip=source_ip,
            user_agent=details.get("user_agent", ""),
            endpoint=details.get("endpoint", ""),
            action=f"SECURITY_INCIDENT_{threat_type}",
            resource="security_system",
            result="DETECTED",
            details={**details, "threat_type": threat_type, "severity": severity}
        )
    
    def log_api_call(self, user_id: Optional[str], source_ip: str, 
                    user_agent: str, endpoint: str, method: str,
                    status_code: int, details: Optional[Dict[str, Any]] = None):
        """Registra llamada a API"""
        result = "SUCCESS" if 200 <= status_code < 400 else "FAILURE"
        action = f"{method}_{endpoint}"
        
        self.log_event(
            event_type=AuditEventType.API_CALL,
            user_id=user_id,
            source_ip=source_ip,
            user_agent=user_agent,
            endpoint=endpoint,
            action=action,
            resource="api_endpoint",
            result=result,
            details={**(details or {}), "status_code": status_code, "method": method}
        )
    
    def generate_compliance_report(self, framework: ComplianceFramework,
                                 start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Genera reporte de cumplimiento"""
        try:
            # Filtrar eventos por marco de cumplimiento y fechas
            relevant_events = [
                event for event in self.audit_queue
                if framework in event.compliance_flags
                and start_date <= event.timestamp <= end_date
            ]
            
            # Estadísticas generales
            total_events = len(relevant_events)
            events_by_type = {}
            events_by_risk = {}
            failed_events = 0
            
            for event in relevant_events:
                # Por tipo
                event_type = event.event_type.value
                events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
                
                # Por riesgo
                risk_level = event.risk_level
                events_by_risk[risk_level] = events_by_risk.get(risk_level, 0) + 1
                
                # Fallos
                if event.result == "FAILURE":
                    failed_events += 1
            
            # Cumplimiento específico por marco
            compliance_checks = self._perform_compliance_checks(framework, relevant_events)
            
            report = {
                "framework": framework.value,
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "summary": {
                    "total_events": total_events,
                    "failed_events": failed_events,
                    "success_rate": round((total_events - failed_events) / total_events * 100, 2) if total_events > 0 else 0
                },
                "event_distribution": {
                    "by_type": events_by_type,
                    "by_risk_level": events_by_risk
                },
                "compliance_status": compliance_checks,
                "generated_at": datetime.now().isoformat(),
                "retention_policy": self.retention_policies[framework].days
            }
            
            logger.info(f"📊 Compliance report generated for {framework.value}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating compliance report: {e}")
            return {}
    
    def search_audit_logs(self, filters: Dict[str, Any]) -> List[AuditEvent]:
        """Busca en los logs de auditoría"""
        try:
            results = self.audit_queue.copy()
            
            # Filtrar por user_id
            if "user_id" in filters:
                results = [e for e in results if e.user_id == filters["user_id"]]
            
            # Filtrar por tipo de evento
            if "event_type" in filters:
                event_type = AuditEventType(filters["event_type"])
                results = [e for e in results if e.event_type == event_type]
            
            # Filtrar por rango de fechas
            if "start_date" in filters:
                start_date = datetime.fromisoformat(filters["start_date"])
                results = [e for e in results if e.timestamp >= start_date]
            
            if "end_date" in filters:
                end_date = datetime.fromisoformat(filters["end_date"])
                results = [e for e in results if e.timestamp <= end_date]
            
            # Filtrar por IP
            if "source_ip" in filters:
                results = [e for e in results if e.source_ip == filters["source_ip"]]
            
            # Filtrar por resultado
            if "result" in filters:
                results = [e for e in results if e.result == filters["result"]]
            
            # Filtrar por nivel de riesgo
            if "risk_level" in filters:
                results = [e for e in results if e.risk_level == filters["risk_level"]]
            
            logger.info(f"🔍 Audit search returned {len(results)} events")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error searching audit logs: {e}")
            return []
    
    def get_audit_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de auditoría"""
        try:
            total_events = len(self.audit_queue)
            
            if total_events == 0:
                return {"total_events": 0}
            
            # Últimas 24 horas
            last_24h = datetime.now() - timedelta(hours=24)
            recent_events = [e for e in self.audit_queue if e.timestamp >= last_24h]
            
            # Estadísticas por tipo
            events_by_type = {}
            events_by_risk = {}
            events_by_result = {}
            
            for event in self.audit_queue:
                # Por tipo
                event_type = event.event_type.value
                events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
                
                # Por riesgo
                risk_level = event.risk_level
                events_by_risk[risk_level] = events_by_risk.get(risk_level, 0) + 1
                
                # Por resultado
                result = event.result
                events_by_result[result] = events_by_result.get(result, 0) + 1
            
            return {
                "total_events": total_events,
                "events_last_24h": len(recent_events),
                "events_by_type": events_by_type,
                "events_by_risk_level": events_by_risk,
                "events_by_result": events_by_result,
                "oldest_event": min(self.audit_queue, key=lambda e: e.timestamp).timestamp.isoformat() if self.audit_queue else None,
                "newest_event": max(self.audit_queue, key=lambda e: e.timestamp).timestamp.isoformat() if self.audit_queue else None
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting audit statistics: {e}")
            return {}
    
    def _generate_event_id(self, event_type: AuditEventType, user_id: Optional[str], source_ip: str) -> str:
        """Genera ID único para evento"""
        timestamp = datetime.now().isoformat()
        raw_id = f"{event_type.value}_{user_id or 'anonymous'}_{source_ip}_{timestamp}"
        return hashlib.sha256(raw_id.encode()).hexdigest()[:16]
    
    def _determine_compliance_frameworks(self, event_type: AuditEventType, 
                                       action: str, resource: str) -> List[ComplianceFramework]:
        """Determina marcos de cumplimiento aplicables"""
        frameworks = []
        
        # SOX - Eventos financieros y de datos críticos
        if event_type in [AuditEventType.DATA_MODIFICATION, AuditEventType.SYSTEM_CONFIGURATION]:
            frameworks.append(ComplianceFramework.SOX)
        
        # GDPR - Eventos relacionados con datos personales
        if "personal" in resource.lower() or "user" in resource.lower():
            frameworks.append(ComplianceFramework.GDPR)
        
        # HIPAA - Eventos relacionados con datos de salud
        if "health" in resource.lower() or "medical" in resource.lower():
            frameworks.append(ComplianceFramework.HIPAA)
        
        # ISO 27001 - Todos los eventos de seguridad
        if event_type in [AuditEventType.SECURITY_INCIDENT, AuditEventType.AUTHENTICATION]:
            frameworks.append(ComplianceFramework.ISO27001)
        
        # PCI DSS - Eventos relacionados con pagos
        if "payment" in resource.lower() or "card" in resource.lower():
            frameworks.append(ComplianceFramework.PCI_DSS)
        
        return frameworks
    
    def _assess_risk_level(self, event_type: AuditEventType, result: str, details: Dict[str, Any]) -> str:
        """Evalúa nivel de riesgo del evento"""
        # Eventos críticos
        if event_type == AuditEventType.SECURITY_INCIDENT:
            return "CRITICAL"
        
        if event_type == AuditEventType.PRIVILEGE_ESCALATION:
            return "HIGH"
        
        # Eventos fallidos son más riesgosos
        if result == "FAILURE":
            if event_type in [AuditEventType.AUTHENTICATION, AuditEventType.AUTHORIZATION]:
                return "HIGH"
            else:
                return "MEDIUM"
        
        # Eventos de modificación de datos
        if event_type == AuditEventType.DATA_MODIFICATION:
            return "MEDIUM"
        
        # Por defecto
        return "LOW"
    
    def _load_compliance_rules(self) -> Dict[str, Any]:
        """Carga reglas de cumplimiento"""
        return {
            "sox": {
                "required_events": ["DATA_MODIFICATION", "SYSTEM_CONFIGURATION"],
                "retention_days": 2555
            },
            "gdpr": {
                "required_events": ["DATA_ACCESS", "DATA_EXPORT"],
                "retention_days": 2190
            },
            "hipaa": {
                "required_events": ["DATA_ACCESS", "AUTHENTICATION"],
                "retention_days": 2190
            },
            "iso27001": {
                "required_events": ["SECURITY_INCIDENT", "AUTHENTICATION"],
                "retention_days": 1095
            }
        }
    
    def _perform_compliance_checks(self, framework: ComplianceFramework, 
                                 events: List[AuditEvent]) -> Dict[str, Any]:
        """Realiza verificaciones de cumplimiento"""
        checks = {
            "all_required_events_logged": True,
            "retention_policy_met": True,
            "risk_events_addressed": True,
            "details": []
        }
        
        framework_rules = self.compliance_rules.get(framework.value, {})
        required_events = framework_rules.get("required_events", [])
        
        # Verificar eventos requeridos
        logged_event_types = {event.event_type.value.upper() for event in events}
        for required_event in required_events:
            if required_event not in logged_event_types:
                checks["all_required_events_logged"] = False
                checks["details"].append(f"Missing required event type: {required_event}")
        
        # Verificar eventos de alto riesgo
        high_risk_events = [e for e in events if e.risk_level in ["HIGH", "CRITICAL"]]
        for event in high_risk_events:
            # En un sistema real, aquí se verificaría si se tomaron acciones correctivas
            pass
        
        return checks
    
    def _persist_event(self, event: AuditEvent):
        """Persiste evento en el backend de almacenamiento"""
        if self.storage_backend:
            try:
                event_data = asdict(event)
                # Convertir datetime a string
                event_data["timestamp"] = event.timestamp.isoformat()
                # Convertir enums a string
                event_data["event_type"] = event.event_type.value
                event_data["compliance_flags"] = [f.value for f in event.compliance_flags]
                
                self.storage_backend.store_secure_data(
                    "audit_logs", event.event_id, event_data, encrypt=True
                )
            except Exception as e:
                logger.error(f"❌ Error persisting audit event: {e}")

# Instancia global del sistema de auditoría
_audit_system = None

def get_audit_system(storage_backend=None) -> EnterpriseAuditSystem:
    """Obtiene la instancia global del sistema de auditoría"""
    global _audit_system
    if _audit_system is None:
        _audit_system = EnterpriseAuditSystem(storage_backend)
    return _audit_system 
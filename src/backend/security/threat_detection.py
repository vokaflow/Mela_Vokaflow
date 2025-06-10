"""
VokaFlow Enterprise Threat Detection System
==========================================

Sistema de detección de amenazas en tiempo real para entornos Fortune 500.
Incluye análisis comportamental, detección de anomalías y respuesta automatizada.
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import ipaddress
import re

logger = logging.getLogger("vokaflow.security.threats")

class ThreatLevel(Enum):
    """Niveles de amenaza"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    """Tipos de amenaza"""
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    DDOS = "ddos"
    SUSPICIOUS_IP = "suspicious_ip"
    UNUSUAL_BEHAVIOR = "unusual_behavior"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"

@dataclass
class SecurityThreat:
    """Amenaza de seguridad detectada"""
    threat_id: str
    threat_type: ThreatType
    threat_level: ThreatLevel
    source_ip: str
    user_id: Optional[str]
    description: str
    detected_at: datetime
    evidence: Dict[str, Any]
    mitigated: bool = False

class EnterpriseThreatDetection:
    """Sistema de detección de amenazas empresarial"""
    
    def __init__(self):
        self.active_threats: Dict[str, SecurityThreat] = {}
        self.ip_reputation_cache: Dict[str, Dict[str, Any]] = {}
        self.behavioral_baselines: Dict[str, Dict[str, Any]] = {}
        
        # Patrones de ataque conocidos
        self.attack_patterns = {
            "sql_injection": [
                r"union\s+select", r"drop\s+table", r"exec\s*\(", 
                r"script\s*>", r"insert\s+into", r"delete\s+from"
            ],
            "xss_patterns": [
                r"<script", r"javascript:", r"onload\s*=", 
                r"onerror\s*=", r"eval\s*\(", r"alert\s*\("
            ]
        }
        
        # IPs sospechosas conocidas (simulado)
        self.malicious_ips = {
            "192.168.1.100",  # IP de prueba
            "10.0.0.50"       # IP de prueba
        }
        
        logger.info("🛡️ Enterprise Threat Detection System initialized")
    
    async def analyze_request(self, request_data: Dict[str, Any]) -> Optional[SecurityThreat]:
        """Analiza una petición en busca de amenazas"""
        try:
            ip_address = request_data.get("ip_address", "unknown")
            user_id = request_data.get("user_id")
            endpoint = request_data.get("endpoint", "")
            payload = request_data.get("payload", "")
            user_agent = request_data.get("user_agent", "")
            
            # Análisis de reputación de IP
            if await self._check_ip_reputation(ip_address):
                return self._create_threat(
                    ThreatType.SUSPICIOUS_IP, ThreatLevel.HIGH,
                    ip_address, user_id,
                    f"Request from known malicious IP: {ip_address}",
                    {"endpoint": endpoint, "user_agent": user_agent}
                )
            
            # Detección de inyección SQL
            if self._detect_sql_injection(payload):
                return self._create_threat(
                    ThreatType.SQL_INJECTION, ThreatLevel.CRITICAL,
                    ip_address, user_id,
                    "SQL injection attempt detected",
                    {"payload": payload[:200], "endpoint": endpoint}
                )
            
            # Detección de XSS
            if self._detect_xss_attack(payload):
                return self._create_threat(
                    ThreatType.XSS_ATTACK, ThreatLevel.HIGH,
                    ip_address, user_id,
                    "Cross-site scripting attempt detected",
                    {"payload": payload[:200], "endpoint": endpoint}
                )
            
            # Análisis comportamental
            behavioral_threat = await self._analyze_behavior(request_data)
            if behavioral_threat:
                return behavioral_threat
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error during threat analysis: {e}")
            return None
    
    async def monitor_authentication_attempts(self, auth_data: Dict[str, Any]) -> Optional[SecurityThreat]:
        """Monitorea intentos de autenticación en busca de ataques de fuerza bruta"""
        try:
            ip_address = auth_data.get("ip_address", "unknown")
            username = auth_data.get("username", "unknown")
            success = auth_data.get("success", False)
            
            # Contador de intentos fallidos por IP
            failed_key = f"failed_auth_{ip_address}"
            
            if not success:
                # Incrementar contador de fallos
                current_time = datetime.now()
                if failed_key not in self.behavioral_baselines:
                    self.behavioral_baselines[failed_key] = {
                        "count": 0,
                        "first_attempt": current_time,
                        "last_attempt": current_time
                    }
                
                baseline = self.behavioral_baselines[failed_key]
                baseline["count"] += 1
                baseline["last_attempt"] = current_time
                
                # Detectar ataque de fuerza bruta
                time_window = timedelta(minutes=15)
                if (baseline["count"] >= 10 and 
                    current_time - baseline["first_attempt"] < time_window):
                    
                    return self._create_threat(
                        ThreatType.BRUTE_FORCE, ThreatLevel.HIGH,
                        ip_address, username,
                        f"Brute force attack detected: {baseline['count']} failed attempts",
                        {
                            "failed_attempts": baseline["count"],
                            "time_window_minutes": 15,
                            "target_username": username
                        }
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error monitoring authentication: {e}")
            return None
    
    async def detect_ddos(self, traffic_data: Dict[str, Any]) -> Optional[SecurityThreat]:
        """Detecta ataques DDoS"""
        try:
            ip_address = traffic_data.get("ip_address", "unknown")
            requests_per_minute = traffic_data.get("requests_per_minute", 0)
            
            # Umbral para DDoS (ajustable según entorno)
            ddos_threshold = 100
            
            if requests_per_minute > ddos_threshold:
                return self._create_threat(
                    ThreatType.DDOS, ThreatLevel.CRITICAL,
                    ip_address, None,
                    f"Potential DDoS attack: {requests_per_minute} requests/minute",
                    {
                        "requests_per_minute": requests_per_minute,
                        "threshold": ddos_threshold
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error detecting DDoS: {e}")
            return None
    
    async def _check_ip_reputation(self, ip_address: str) -> bool:
        """Verifica la reputación de una IP"""
        try:
            # Verificar cache local
            if ip_address in self.ip_reputation_cache:
                cache_entry = self.ip_reputation_cache[ip_address]
                if datetime.now() - cache_entry["last_check"] < timedelta(hours=1):
                    return cache_entry["is_malicious"]
            
            # Verificar lista local de IPs maliciosas
            is_malicious = ip_address in self.malicious_ips
            
            # En producción, aquí se consultarían servicios de reputación externos
            # como VirusTotal, AbuseIPDB, etc.
            
            # Actualizar cache
            self.ip_reputation_cache[ip_address] = {
                "is_malicious": is_malicious,
                "last_check": datetime.now()
            }
            
            return is_malicious
            
        except Exception as e:
            logger.error(f"❌ Error checking IP reputation: {e}")
            return False
    
    def _detect_sql_injection(self, payload: str) -> bool:
        """Detecta intentos de inyección SQL"""
        if not payload:
            return False
        
        payload_lower = payload.lower()
        for pattern in self.attack_patterns["sql_injection"]:
            if re.search(pattern, payload_lower, re.IGNORECASE):
                return True
        
        return False
    
    def _detect_xss_attack(self, payload: str) -> bool:
        """Detecta intentos de XSS"""
        if not payload:
            return False
        
        payload_lower = payload.lower()
        for pattern in self.attack_patterns["xss_patterns"]:
            if re.search(pattern, payload_lower, re.IGNORECASE):
                return True
        
        return False
    
    async def _analyze_behavior(self, request_data: Dict[str, Any]) -> Optional[SecurityThreat]:
        """Analiza comportamiento del usuario"""
        try:
            user_id = request_data.get("user_id")
            if not user_id:
                return None
            
            endpoint = request_data.get("endpoint", "")
            ip_address = request_data.get("ip_address", "unknown")
            
            # Inicializar baseline si no existe
            if user_id not in self.behavioral_baselines:
                self.behavioral_baselines[user_id] = {
                    "usual_ips": set(),
                    "usual_endpoints": {},
                    "last_activity": datetime.now()
                }
            
            baseline = self.behavioral_baselines[user_id]
            
            # Detectar acceso desde IP inusual
            if len(baseline["usual_ips"]) > 0 and ip_address not in baseline["usual_ips"]:
                if len(baseline["usual_ips"]) >= 3:  # Usuario ya establecido
                    return self._create_threat(
                        ThreatType.UNUSUAL_BEHAVIOR, ThreatLevel.MEDIUM,
                        ip_address, user_id,
                        f"User accessing from unusual IP: {ip_address}",
                        {
                            "usual_ips": list(baseline["usual_ips"]),
                            "new_ip": ip_address
                        }
                    )
            
            # Actualizar baseline
            baseline["usual_ips"].add(ip_address)
            baseline["usual_endpoints"][endpoint] = baseline["usual_endpoints"].get(endpoint, 0) + 1
            baseline["last_activity"] = datetime.now()
            
            # Mantener solo las últimas 5 IPs
            if len(baseline["usual_ips"]) > 5:
                baseline["usual_ips"] = set(list(baseline["usual_ips"])[-5:])
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error during behavioral analysis: {e}")
            return None
    
    def _create_threat(self, threat_type: ThreatType, level: ThreatLevel,
                      source_ip: str, user_id: Optional[str], 
                      description: str, evidence: Dict[str, Any]) -> SecurityThreat:
        """Crea una nueva amenaza"""
        threat_id = f"{threat_type.value}_{int(datetime.now().timestamp())}"
        
        threat = SecurityThreat(
            threat_id=threat_id,
            threat_type=threat_type,
            threat_level=level,
            source_ip=source_ip,
            user_id=user_id,
            description=description,
            detected_at=datetime.now(),
            evidence=evidence
        )
        
        self.active_threats[threat_id] = threat
        
        logger.warning(f"🚨 THREAT DETECTED: {threat.description} from {source_ip}")
        
        return threat
    
    def get_active_threats(self) -> List[SecurityThreat]:
        """Obtiene amenazas activas"""
        return list(self.active_threats.values())
    
    def mitigate_threat(self, threat_id: str) -> bool:
        """Marca una amenaza como mitigada"""
        if threat_id in self.active_threats:
            self.active_threats[threat_id].mitigated = True
            logger.info(f"✅ Threat mitigated: {threat_id}")
            return True
        return False
    
    def get_threat_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de amenazas"""
        total_threats = len(self.active_threats)
        threats_by_type = {}
        threats_by_level = {}
        mitigated_count = 0
        
        for threat in self.active_threats.values():
            # Por tipo
            threat_type = threat.threat_type.value
            threats_by_type[threat_type] = threats_by_type.get(threat_type, 0) + 1
            
            # Por nivel
            threat_level = threat.threat_level.value
            threats_by_level[threat_level] = threats_by_level.get(threat_level, 0) + 1
            
            # Mitigadas
            if threat.mitigated:
                mitigated_count += 1
        
        return {
            "total_threats": total_threats,
            "active_threats": total_threats - mitigated_count,
            "mitigated_threats": mitigated_count,
            "threats_by_type": threats_by_type,
            "threats_by_level": threats_by_level
        }

# Instancia global del sistema de detección de amenazas
_threat_detection_system = None

def get_threat_detection_system() -> EnterpriseThreatDetection:
    """Obtiene la instancia global del sistema de detección de amenazas"""
    global _threat_detection_system
    if _threat_detection_system is None:
        _threat_detection_system = EnterpriseThreatDetection()
    return _threat_detection_system 
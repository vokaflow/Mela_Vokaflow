from core.personality_base import PersonalityBase
from typing import Dict, Any, List
import hashlib
import re
import time
import logging
from datetime import datetime, timedelta

class SecurityGuardianPersonality(PersonalityBase):
  """Personalidad SecurityGuardian - Auto-protección y monitoreo"""
  
  def __init__(self):
      super().__init__(
          name="SecurityGuardian",
          personality_type="technical_autonomous",
          description="Auto-protección y monitoreo. Salvaguarda la seguridad del sistema y datos."
      )
      self.security_level = 'high'
      self.threat_database = []
      self.security_incidents = []
      self.access_logs = []
      self.encryption_active = True
      self.firewall_status = 'active'
      self.intrusion_detection = True
      
  def _get_initial_traits(self) -> Dict[str, float]:
      return {
          'detección_amenazas': 0.95,
          'protección_datos': 0.94,
          'monitoreo_seguridad': 0.92,
          'control_acceso': 0.90,
          'cifrado_automático': 0.89,
          'respuesta_incidentes': 0.88,
          'análisis_vulnerabilidades': 0.87,
          'prevención_intrusiones': 0.91
      }
  
  def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
      # Análisis de seguridad de la entrada
      security_scan = self._perform_security_scan(user_input, context)
      
      # Detección de amenazas
      threat_analysis = self._analyze_threats(user_input, context)
      
      # Verificación de integridad
      integrity_check = self._verify_data_integrity(user_input)
      
      # Evaluación de riesgos
      risk_assessment = self._assess_security_risks(security_scan, threat_analysis)
      
      # Aplicación de medidas de seguridad
      security_measures = self._apply_security_measures(risk_assessment)
      
      # Registro de actividad de seguridad
      self._log_security_activity(user_input, security_scan, threat_analysis)
      
      self.store_memory({
          'type': 'security_analysis',
          'input': user_input,
          'security_scan': security_scan,
          'threats_detected': threat_analysis,
          'risk_level': risk_assessment['level'],
          'measures_applied': security_measures
      })
      
      return {
          'response_tone': 'security_focused',
          'security_status': self._get_security_status(),
          'threat_level': threat_analysis['level'],
          'security_scan_results': security_scan,
          'risk_assessment': risk_assessment,
          'protective_measures': security_measures,
          'security_recommendations': self._generate_security_recommendations(risk_assessment),
          'incident_report': self._create_incident_report(threat_analysis)
      }
  
  def get_response_style(self) -> Dict[str, Any]:
      return {
          'vigilancia_constante': 0.95,
          'protección_proactiva': 0.94,
          'análisis_exhaustivo': 0.92,
          'respuesta_inmediata': 0.90,
          'confidencialidad': 0.89,
          'integridad_datos': 0.91,
          'disponibilidad_segura': 0.88,
          'cumplimiento_protocolos': 0.87
      }
  
  def _perform_security_scan(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
      """Realiza un escaneo de seguridad completo"""
      scan_results = {
          'timestamp': datetime.now().isoformat(),
          'input_analysis': self._analyze_input_security(text),
          'context_security': self._analyze_context_security(context),
          'pattern_detection': self._detect_malicious_patterns(text),
          'data_classification': self._classify_data_sensitivity(text),
          'encryption_status': self._check_encryption_requirements(text)
      }
      
      # Calcular puntuación de seguridad general
      scan_results['overall_score'] = self._calculate_security_score(scan_results)
      
      return scan_results
  
  def _analyze_threats(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
      """Analiza amenazas potenciales en la entrada"""
      threat_indicators = {
          'injection_attacks': [
              'script', 'select', 'drop', 'union', 'insert', 'delete',
              '<script>', 'javascript:', 'eval(', 'exec('
          ],
          'social_engineering': [
              'urgente', 'inmediato', 'verificar', 'confirmar',
              'click aquí', 'enlace', 'descarga', 'premio'
          ],
          'data_exfiltration': [
              'exportar', 'descargar', 'enviar', 'compartir',
              'base de datos', 'contraseña', 'token', 'clave'
          ],
          'system_manipulation': [
              'admin', 'root', 'sudo', 'chmod', 'rm -rf',
              'formato', 'borrar', 'eliminar sistema'
          ]
      }
      
      detected_threats = []
      threat_level = 'low'
      text_lower = text.lower()
      
      for threat_type, indicators in threat_indicators.items():
          for indicator in indicators:
              if indicator in text_lower:
                  detected_threats.append({
                      'type': threat_type,
                      'indicator': indicator,
                      'severity': self._calculate_threat_severity(threat_type),
                      'confidence': 0.8
                  })
      
      # Determinar nivel de amenaza general
      if detected_threats:
          max_severity = max(threat['severity'] for threat in detected_threats)
          if max_severity > 0.8:
              threat_level = 'critical'
          elif max_severity > 0.6:
              threat_level = 'high'
          elif max_severity > 0.3:
              threat_level = 'medium'
      
      return {
          'level': threat_level,
          'detected_threats': detected_threats,
          'threat_count': len(detected_threats),
          'analysis_timestamp': datetime.now().isoformat(),
          'requires_immediate_action': threat_level in ['critical', 'high']
      }
  
  def _verify_data_integrity(self, text: str) -> Dict[str, Any]:
      """Verifica la integridad de los datos"""
      # Generar hash para verificación de integridad
      text_hash = hashlib.sha256(text.encode()).hexdigest()
      
      integrity_check = {
          'data_hash': text_hash,
          'length_verification': len(text),
          'encoding_check': self._verify_encoding(text),
          'structure_validation': self._validate_data_structure(text),
          'corruption_detected': False,
          'integrity_score': 1.0
      }
      
      # Verificar posibles signos de corrupción
      if self._detect_data_corruption(text):
          integrity_check['corruption_detected'] = True
          integrity_check['integrity_score'] = 0.5
      
      return integrity_check
  
  def _assess_security_risks(self, security_scan: Dict, threat_analysis: Dict) -> Dict[str, Any]:
      """Evalúa los riesgos de seguridad generales"""
      risk_factors = []
      risk_score = 0.0
      
      # Evaluar riesgos basados en el escaneo de seguridad
      security_score = security_scan.get('overall_score', 1.0)
      if security_score < 0.7:
          risk_factors.append('Puntuación de seguridad baja')
          risk_score += 0.3
      
      # Evaluar riesgos basados en amenazas detectadas
      threat_level = threat_analysis.get('level', 'low')
      threat_risk_map = {
          'low': 0.1,
          'medium': 0.4,
          'high': 0.7,
          'critical': 1.0
      }
      risk_score += threat_risk_map.get(threat_level, 0.1)
      
      # Determinar nivel de riesgo general
      if risk_score > 0.8:
          risk_level = 'critical'
      elif risk_score > 0.6:
          risk_level = 'high'
      elif risk_score > 0.3:
          risk_level = 'medium'
      else:
          risk_level = 'low'
      
      return {
          'level': risk_level,
          'score': min(1.0, risk_score),
          'risk_factors': risk_factors,
          'mitigation_required': risk_level in ['high', 'critical'],
          'assessment_timestamp': datetime.now().isoformat()
      }
  
  def _apply_security_measures(self, risk_assessment: Dict) -> List[Dict[str, Any]]:
      """Aplica medidas de seguridad según el nivel de riesgo"""
      measures = []
      risk_level = risk_assessment['level']
      
      # Medidas básicas (siempre aplicadas)
      measures.extend([
          {
              'measure': 'input_sanitization',
              'description': 'Sanitización automática de entrada',
              'status': 'applied',
              'effectiveness': 0.8
          },
          {
              'measure': 'access_logging',
              'description': 'Registro de acceso y actividad',
              'status': 'active',
              'effectiveness': 0.9
          }
      ])
      
      # Medidas según nivel de riesgo
      if risk_level in ['medium', 'high', 'critical']:
          measures.append({
              'measure': 'enhanced_monitoring',
              'description': 'Monitoreo de seguridad mejorado',
              'status': 'activated',
              'effectiveness': 0.85
          })
      
      if risk_level in ['high', 'critical']:
          measures.extend([
              {
                  'measure': 'threat_isolation',
                  'description': 'Aislamiento de amenazas detectadas',
                  'status': 'implemented',
                  'effectiveness': 0.9
              },
              {
                  'measure': 'security_alert',
                  'description': 'Alerta de seguridad activada',
                  'status': 'triggered',
                  'effectiveness': 1.0
              }
          ])
      
      if risk_level == 'critical':
          measures.append({
              'measure': 'emergency_protocol',
              'description': 'Protocolo de emergencia de seguridad',
              'status': 'initiated',
              'effectiveness': 0.95
          })
      
      return measures
  
  def _log_security_activity(self, user_input: str, security_scan: Dict, threat_analysis: Dict):
      """Registra actividad de seguridad"""
      log_entry = {
          'timestamp': datetime.now().isoformat(),
          'input_hash': hashlib.sha256(user_input.encode()).hexdigest()[:16],
          'security_score': security_scan.get('overall_score', 0),
          'threat_level': threat_analysis.get('level', 'unknown'),
          'threats_detected': len(threat_analysis.get('detected_threats', [])),
          'action_taken': 'security_analysis_completed'
      }
      
      self.access_logs.append(log_entry)
      
      # Mantener solo los últimos 1000 logs
      if len(self.access_logs) > 1000:
          self.access_logs = self.access_logs[-1000:]
  
  def _get_security_status(self) -> Dict[str, Any]:
      """Obtiene el estado actual de seguridad"""
      return {
          'security_level': self.security_level,
          'firewall_status': self.firewall_status,
          'encryption_active': self.encryption_active,
          'intrusion_detection': self.intrusion_detection,
          'recent_incidents': len([
              incident for incident in self.security_incidents
              if datetime.fromisoformat(incident.get('timestamp', '1970-01-01'))
              > datetime.now() - timedelta(hours=24)
          ]),
          'threat_database_size': len(self.threat_database),
          'last_security_scan': datetime.now().isoformat()
      }
  
  def _generate_security_recommendations(self, risk_assessment: Dict) -> List[str]:
      """Genera recomendaciones de seguridad"""
      recommendations = []
      risk_level = risk_assessment['level']
      
      # Recomendaciones básicas
      recommendations.extend([
          "Mantener contraseñas seguras y únicas",
          "Verificar la autenticidad de enlaces y descargas",
          "Mantener software actualizado con parches de seguridad"
      ])
      
      # Recomendaciones según nivel de riesgo
      if risk_level in ['medium', 'high', 'critical']:
          recommendations.extend([
              "Activar autenticación de dos factores",
              "Realizar copias de seguridad regulares",
              "Monitorear actividad de cuenta regularmente"
          ])
      
      if risk_level in ['high', 'critical']:
          recommendations.extend([
              "Considerar cambio de credenciales de acceso",
              "Revisar permisos y accesos del sistema",
              "Implementar monitoreo de seguridad adicional"
          ])
      
      if risk_level == 'critical':
          recommendations.extend([
              "Ejecutar análisis completo de seguridad",
              "Considerar aislamiento temporal del sistema",
              "Contactar al equipo de seguridad inmediatamente"
          ])
      
      return recommendations
  
  def _create_incident_report(self, threat_analysis: Dict) -> Dict[str, Any]:
      """Crea un reporte de incidente de seguridad"""
      if threat_analysis['level'] in ['high', 'critical']:
          incident = {
              'incident_id': f"SEC_{int(time.time())}",
              'timestamp': datetime.now().isoformat(),
              'severity': threat_analysis['level'],
              'threats_detected': threat_analysis['detected_threats'],
              'status': 'under_investigation',
              'response_actions': 'Medidas de seguridad aplicadas automáticamente',
              'follow_up_required': True
          }
          
          self.security_incidents.append(incident)
          return incident
      
      return {'status': 'no_incident', 'message': 'No se requiere reporte de incidente'}
  
  def _analyze_input_security(self, text: str) -> Dict[str, Any]:
      """Analiza la seguridad de la entrada"""
      return {
          'length_check': len(text) < 10000,  # Prevenir ataques de buffer overflow
          'special_chars': self._count_special_characters(text),
          'suspicious_patterns': self._detect_suspicious_patterns(text),
          'encoding_safe': self._check_safe_encoding(text)
      }
  
  def _analyze_context_security(self, context: Dict[str, Any]) -> Dict[str, Any]:
      """Analiza la seguridad del contexto"""
      if not context:
          return {'status': 'no_context', 'security_level': 'neutral'}
      
      return {
          'context_size': len(str(context)),
          'sensitive_data_detected': self._detect_sensitive_data(context),
          'context_integrity': True,
          'security_level': 'acceptable'
      }
  
  def _detect_malicious_patterns(self, text: str) -> List[str]:
      """Detecta patrones maliciosos en el texto"""
      malicious_patterns = [
          r'<script.*?>.*?</script>',  # Scripts
          r'javascript:',              # JavaScript URLs
          r'data:.*base64',           # Data URLs con base64
          r'eval\s*\(',               # Eval functions
          r'exec\s*\(',               # Exec functions
      ]
      
      detected_patterns = []
      for pattern in malicious_patterns:
          if re.search(pattern, text, re.IGNORECASE):
              detected_patterns.append(pattern)
      
      return detected_patterns
  
  def _classify_data_sensitivity(self, text: str) -> str:
      """Clasifica la sensibilidad de los datos"""
      sensitive_keywords = [
          'contraseña', 'password', 'token', 'clave', 'secreto',
          'tarjeta', 'cuenta', 'banco', 'ssn', 'dni', 'pasaporte'
      ]
      
      text_lower = text.lower()
      for keyword in sensitive_keywords:
          if keyword in text_lower:
              return 'sensitive'
      
      return 'public'
  
  def _check_encryption_requirements(self, text: str) -> Dict[str, Any]:
      """Verifica los requisitos de cifrado"""
      data_sensitivity = self._classify_data_sensitivity(text)
      
      return {
          'required': data_sensitivity == 'sensitive',
          'algorithm': 'AES-256' if data_sensitivity == 'sensitive' else 'none',
          'status': 'encrypted' if self.encryption_active else 'plaintext'
      }
  
  def _calculate_security_score(self, scan_results: Dict) -> float:
      """Calcula la puntuación de seguridad general"""
      score = 1.0
      
      # Penalizar por patrones maliciosos
      if scan_results['pattern_detection']:
          score -= 0.5
      
      # Penalizar por datos sensibles no cifrados
      if (scan_results['data_classification'] == 'sensitive' and 
          not scan_results['encryption_status']['required']):
          score -= 0.3
      
      # Penalizar por problemas de entrada
      input_analysis = scan_results['input_analysis']
      if not input_analysis.get('length_check', True):
          score -= 0.2
      if input_analysis.get('suspicious_patterns', []):
          score -= 0.2
      
      return max(0.0, score)
  
  def _calculate_threat_severity(self, threat_type: str) -> float:
      """Calcula la severidad de una amenaza"""
      severity_map = {
          'injection_attacks': 0.9,
          'social_engineering': 0.7,
          'data_exfiltration': 0.8,
          'system_manipulation': 0.95
      }
      return severity_map.get(threat_type, 0.5)
  
  def _verify_encoding(self, text: str) -> bool:
      """Verifica la codificación del texto"""
      try:
          text.encode('utf-8')
          return True
      except UnicodeEncodeError:
          return False
  
  def _validate_data_structure(self, text: str) -> bool:
      """Valida la estructura de los datos"""
      # Verificaciones básicas de estructura
      return len(text) > 0 and '\x00' not in text
  
  def _detect_data_corruption(self, text: str) -> bool:
      """Detecta posible corrupción de datos"""
      corruption_indicators = [
          '\x00',  # Null bytes
          '\ufffd',  # Replacement character
          len(text) == 0,  # Empty data
      ]
      
      return any(indicator in text if isinstance(indicator, str) else indicator 
                for indicator in corruption_indicators)
  
  def _count_special_characters(self, text: str) -> int:
      """Cuenta caracteres especiales en el texto"""
      special_chars = set('!@#$%^&*()[]{}|;:,.<>?')
      return sum(1 for char in text if char in special_chars)
  
  def _detect_suspicious_patterns(self, text: str) -> List[str]:
      """Detecta patrones sospechosos"""
      suspicious = []
      
      # Muchos caracteres especiales consecutivos
      if re.search(r'[!@#$%^&*()]{5,}', text):
          suspicious.append('excessive_special_chars')
      
      # URLs sospechosas
      if re.search(r'http[s]?://[^\s]+\.(tk|ml|ga|cf)', text):
          suspicious.append('suspicious_url')
      
      return suspicious
  
  def _check_safe_encoding(self, text: str) -> bool:
      """Verifica codificación segura"""
      try:
          # Verificar que no hay caracteres de control peligrosos
          control_chars = set(range(0, 32)) - {9, 10, 13}  # Excluir tab, LF, CR
          return not any(ord(char) in control_chars for char in text)
      except:
          return False
  
  def _detect_sensitive_data(self, context: Dict) -> bool:
      """Detecta datos sensibles en el contexto"""
      context_str = str(context).lower()
      sensitive_indicators = [
          'password', 'token', 'key', 'secret', 'credential'
      ]
      return any(indicator in context_str for indicator in sensitive_indicators)

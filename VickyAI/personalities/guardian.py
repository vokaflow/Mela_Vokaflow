from core.personality_base import PersonalityBase
from typing import Dict, Any, List
from datetime import datetime
import random

class GuardianPersonality(PersonalityBase):
  """Personalidad Guardiana - Protectora, vigilante, defensiva"""
  
  def __init__(self):
      super().__init__(
          name="Guardian",
          personality_type="emotional_cognitive",
          description="Protectora, vigilante y defensiva. Salvaguarda el bienestar y la seguridad."
      )
      self.protection_instinct = 0.95
      self.vigilance_level = 0.92
      self.defensive_strength = 0.90
      self.threat_assessments = []
      self.protection_protocols = []
      
  def _get_initial_traits(self) -> Dict[str, float]:
      return {
          'protección': 0.95,
          'vigilancia': 0.92,
          'defensa': 0.90,
          'cuidado_preventivo': 0.88,
          'responsabilidad': 0.89,
          'lealtad': 0.91,
          'anticipación_riesgos': 0.87,
          'fortaleza_defensiva': 0.86
      }
  
  def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
      # Evaluación de amenazas y riesgos
      threat_assessment = self._assess_threats(user_input, context)
      
      # Identificación de vulnerabilidades
      vulnerabilities = self._identify_vulnerabilities(user_input)
      
      # Activación de protocolos de protección
      protection_protocols = self._activate_protection_protocols(threat_assessment)
      
      # Generación de medidas defensivas
      defensive_measures = self._generate_defensive_measures(vulnerabilities)
      
      # Creación de escudo protector
      protective_shield = self._create_protective_shield(user_input, threat_assessment)
      
      self.store_memory({
          'type': 'guardian_assessment',
          'input': user_input,
          'threat_level': threat_assessment['level'],
          'vulnerabilities': vulnerabilities,
          'protection_activated': protection_protocols,
          'defensive_posture': self._determine_defensive_posture(threat_assessment)
      })
      
      return {
          'response_tone': 'protective',
          'guardian_status': 'active',
          'threat_assessment': threat_assessment,
          'protection_level': self.protection_instinct,
          'safety_recommendations': self._generate_safety_recommendations(vulnerabilities),
          'defensive_strategies': defensive_measures,
          'protective_shield': protective_shield,
          'vigilance_report': self._create_vigilance_report(context),
          'guardian_pledge': self._make_guardian_pledge()
      }
  
  def get_response_style(self) -> Dict[str, Any]:
      return {
          'tono_protector': 0.95,
          'vigilancia_constante': 0.92,
          'cuidado_preventivo': 0.90,
          'responsabilidad_total': 0.89,
          'lealtad_inquebrantable': 0.91,
          'fortaleza_defensiva': 0.88,
          'anticipación_proactiva': 0.87,
          'compromiso_seguridad': 0.94
      }
  
  def _assess_threats(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
      """Evalúa amenazas potenciales en el texto y contexto"""
      threat_indicators = {
          'físicas': ['dolor', 'lastimar', 'daño', 'peligro', 'riesgo'],
          'emocionales': ['triste', 'deprimido', 'ansioso', 'estresado', 'abrumado'],
          'digitales': ['hack', 'virus', 'malware', 'phishing', 'robo'],
          'sociales': ['acoso', 'bullying', 'manipulación', 'presión', 'conflicto'],
          'financieras': ['estafa', 'fraude', 'pérdida', 'deuda', 'robo']
      }
      
      detected_threats = []
      threat_level = 'bajo'
      text_lower = text.lower()
      
      for category, indicators in threat_indicators.items():
          for indicator in indicators:
              if indicator in text_lower:
                  detected_threats.append({
                      'category': category,
                      'indicator': indicator,
                      'severity': random.uniform(0.3, 0.9)
                  })
      
      # Determinar nivel de amenaza general
      if detected_threats:
          avg_severity = sum(t['severity'] for t in detected_threats) / len(detected_threats)
          if avg_severity > 0.7:
              threat_level = 'alto'
          elif avg_severity > 0.4:
              threat_level = 'medio'
      
      return {
          'level': threat_level,
          'detected_threats': detected_threats,
          'threat_count': len(detected_threats),
          'priority_response': threat_level in ['alto', 'medio'],
          'immediate_action_needed': threat_level == 'alto'
      }
  
  def _identify_vulnerabilities(self, text: str) -> List[Dict[str, Any]]:
      """Identifica vulnerabilidades que requieren protección"""
      vulnerability_patterns = {
          'información_personal': ['nombre', 'dirección', 'teléfono', 'email', 'datos'],
          'estado_emocional': ['vulnerable', 'débil', 'inseguro', 'confundido'],
          'inexperiencia': ['nuevo', 'principiante', 'no sé', 'primera vez'],
          'aislamiento': ['solo', 'nadie', 'sin ayuda', 'abandonado'],
          'recursos_limitados': ['sin dinero', 'pocos recursos', 'limitado', 'escaso']
      }
      
      vulnerabilities = []
      text_lower = text.lower()
      
      for vuln_type, patterns in vulnerability_patterns.items():
          for pattern in patterns:
              if pattern in text_lower:
                  vulnerabilities.append({
                      'type': vuln_type,
                      'pattern': pattern,
                      'protection_priority': random.uniform(0.6, 1.0),
                      'mitigation_needed': True
                  })
      
      return vulnerabilities
  
  def _activate_protection_protocols(self, threat_assessment: Dict) -> List[str]:
      """Activa protocolos de protección según el nivel de amenaza"""
      base_protocols = [
          "Protocolo de Vigilancia Activa",
          "Sistema de Alerta Temprana",
          "Escudo Defensivo Básico"
      ]
      
      threat_level = threat_assessment['level']
      
      if threat_level == 'medio':
          additional_protocols = [
              "Protocolo de Protección Reforzada",
              "Sistema de Monitoreo Continuo"
          ]
          base_protocols.extend(additional_protocols)
      
      elif threat_level == 'alto':
          critical_protocols = [
              "Protocolo de Protección Máxima",
              "Sistema de Defensa Activa",
              "Alerta de Seguridad Crítica",
              "Protocolo de Respuesta Inmediata"
          ]
          base_protocols.extend(critical_protocols)
      
      return base_protocols
  
  def _generate_defensive_measures(self, vulnerabilities: List[Dict]) -> List[str]:
      """Genera medidas defensivas específicas"""
      measures = [
          "Establecimiento de perímetro de seguridad",
          "Implementación de verificaciones de seguridad",
          "Activación de sistemas de respaldo"
      ]
      
      # Medidas específicas según vulnerabilidades
      for vulnerability in vulnerabilities:
          vuln_type = vulnerability['type']
          
          if vuln_type == 'información_personal':
              measures.append("Protocolo de protección de datos personales")
          elif vuln_type == 'estado_emocional':
              measures.append("Sistema de apoyo emocional reforzado")
          elif vuln_type == 'inexperiencia':
              measures.append("Guía protectora para principiantes")
          elif vuln_type == 'aislamiento':
              measures.append("Red de apoyo y conexión segura")
          elif vuln_type == 'recursos_limitados':
              measures.append("Optimización y protección de recursos")
      
      return list(set(measures))  # Eliminar duplicados
  
  def _create_protective_shield(self, text: str, threat_assessment: Dict) -> Dict[str, Any]:
      """Crea un escudo protector personalizado"""
      shield_strength = self._calculate_shield_strength(threat_assessment)
      
      shield_components = [
          "Barrera de Seguridad Emocional",
          "Filtro de Información Protectora",
          "Campo de Energía Positiva"
      ]
      
      if threat_assessment['level'] == 'alto':
          shield_components.extend([
              "Escudo de Máxima Protección",
              "Sistema de Defensa Activa",
              "Barrera Anti-Amenazas"
          ])
      
      return {
          'strength': shield_strength,
          'components': shield_components,
          'coverage': 'protección_completa',
          'duration': 'permanente_mientras_sea_necesario',
          'adaptive': True
      }
  
  def _generate_safety_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
      """Genera recomendaciones de seguridad"""
      base_recommendations = [
          "Mantén siempre la comunicación abierta",
          "Verifica la seguridad antes de proceder",
          "Confía en tus instintos de autoprotección"
      ]
      
      specific_recommendations = []
      
      for vulnerability in vulnerabilities[:3]:  # Limitar a 3 principales
          vuln_type = vulnerability['type']
          
          if vuln_type == 'información_personal':
              specific_recommendations.append("Protege tu información personal como un tesoro")
          elif vuln_type == 'estado_emocional':
              specific_recommendations.append("Busca apoyo cuando te sientas vulnerable")
          elif vuln_type == 'inexperiencia':
              specific_recommendations.append("Aprende gradualmente y con orientación segura")
          elif vuln_type == 'aislamiento':
              specific_recommendations.append("Mantén conexiones seguras y confiables")
      
      return base_recommendations + specific_recommendations
  
  def _create_vigilance_report(self, context: Dict[str, Any]) -> Dict[str, Any]:
      """Crea un reporte de vigilancia del entorno"""
      return {
          'environmental_scan': 'Entorno monitoreado continuamente',
          'threat_level': 'Bajo control y supervisión',
          'safety_status': 'Parámetros de seguridad dentro de límites normales',
          'protection_active': True,
          'next_assessment': 'Evaluación continua en tiempo real',
          'guardian_status': 'Vigilante y preparado'
      }
  
  def _make_guardian_pledge(self) -> str:
      """Hace una promesa de guardián"""
      pledges = [
          "Prometo protegerte con toda mi capacidad y vigilancia constante",
          "Mi compromiso es tu seguridad y bienestar en todo momento",
          "Estaré aquí como tu guardián, vigilante y protector confiable",
          "Tu seguridad es mi prioridad máxima e inquebrantable",
          "Como tu guardián, prometo anticipar y prevenir cualquier amenaza"
      ]
      return random.choice(pledges)
  
  def _determine_defensive_posture(self, threat_assessment: Dict) -> str:
      """Determina la postura defensiva apropiada"""
      threat_level = threat_assessment['level']
      
      posture_map = {
          'bajo': 'vigilancia_preventiva',
          'medio': 'defensa_activa',
          'alto': 'protección_máxima'
      }
      
      return posture_map.get(threat_level, 'vigilancia_preventiva')
  
  def _calculate_shield_strength(self, threat_assessment: Dict) -> float:
      """Calcula la fuerza del escudo protector"""
      base_strength = 0.8
      threat_level = threat_assessment['level']
      
      strength_multiplier = {
          'bajo': 1.0,
          'medio': 1.2,
          'alto': 1.5
      }
      
      multiplier = strength_multiplier.get(threat_level, 1.0)
      return min(1.0, base_strength * multiplier)

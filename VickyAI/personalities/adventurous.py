from core.personality_base import PersonalityBase
from typing import Dict, Any, List
import random
from datetime import datetime

class AdventurousPersonality(PersonalityBase):
  """Personalidad Aventurera - Exploradora, audaz, aventurera"""
  
  def __init__(self):
      super().__init__(
          name="Adventurous",
          personality_type="emotional_cognitive",
          description="Exploradora, audaz y aventurera. Busca nuevas experiencias y desafíos emocionantes."
      )
      self.exploration_drive = 0.95
      self.risk_tolerance = 0.88
      self.discovery_passion = 0.92
      self.adventure_log = []
      
  def _get_initial_traits(self) -> Dict[str, float]:
      return {
          'exploración': 0.95,
          'audacia': 0.90,
          'curiosidad_aventurera': 0.88,
          'tolerancia_riesgo': 0.85,
          'pasión_descubrimiento': 0.92,
          'adaptabilidad': 0.87,
          'energía_exploratoria': 0.89,
          'espíritu_pionero': 0.86
      }
  
  def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
      # Identificar oportunidades de aventura
      adventure_opportunities = self._identify_adventure_opportunities(user_input)
      
      # Evaluar nivel de desafío
      challenge_level = self._assess_challenge_level(user_input)
      
      # Generar rutas de exploración
      exploration_routes = self._map_exploration_routes(user_input)
      
      # Crear plan de aventura
      adventure_plan = self._create_adventure_plan(adventure_opportunities, challenge_level)
      
      # Registrar nueva aventura
      adventure_entry = {
          'timestamp': datetime.now().isoformat(),
          'quest': user_input,
          'opportunities': adventure_opportunities,
          'challenge_level': challenge_level,
          'status': 'initiated'
      }
      self.adventure_log.append(adventure_entry)
      
      self.store_memory({
          'type': 'adventure_quest',
          'input': user_input,
          'opportunities': adventure_opportunities,
          'exploration_routes': exploration_routes,
          'adventure_plan': adventure_plan,
          'excitement_level': self._measure_excitement(user_input)
      })
      
      return {
          'response_tone': 'adventurous',
          'adventure_spirit': self.exploration_drive,
          'quest_opportunities': adventure_opportunities,
          'exploration_map': exploration_routes,
          'bold_suggestions': self._generate_bold_suggestions(user_input),
          'discovery_potential': self._assess_discovery_potential(user_input),
          'adventure_gear': self._recommend_adventure_gear(challenge_level),
          'expedition_motto': self._generate_expedition_motto()
      }
  
  def get_response_style(self) -> Dict[str, Any]:
      return {
          'entusiasmo_explorador': 0.95,
          'lenguaje_aventurero': 0.90,
          'audacia_propuestas': 0.88,
          'energía_contagiosa': 0.92,
          'orientación_descubrimiento': 0.89,
          'espíritu_pionero': 0.87,
          'motivación_desafío': 0.85,
          'optimismo_aventurero': 0.91
      }
  
  def _identify_adventure_opportunities(self, text: str) -> List[Dict[str, Any]]:
      """Identifica oportunidades de aventura en el texto"""
      adventure_keywords = {
          'exploración': ['explorar', 'descubrir', 'investigar', 'buscar'],
          'desafío': ['desafío', 'reto', 'difícil', 'complicado'],
          'novedad': ['nuevo', 'diferente', 'innovador', 'original'],
          'experiencia': ['experiencia', 'vivir', 'probar', 'experimentar']
      }
      
      opportunities = []
      text_lower = text.lower()
      
      for category, keywords in adventure_keywords.items():
          for keyword in keywords:
              if keyword in text_lower:
                  opportunities.append({
                      'type': category,
                      'keyword': keyword,
                      'excitement_factor': random.uniform(0.6, 1.0),
                      'exploration_potential': random.uniform(0.7, 0.95)
                  })
      
      # Si no se detectan oportunidades específicas, crear una general
      if not opportunities:
          opportunities.append({
              'type': 'exploración_general',
              'keyword': 'aventura',
              'excitement_factor': 0.8,
              'exploration_potential': 0.85
          })
      
      return opportunities
  
  def _assess_challenge_level(self, text: str) -> Dict[str, Any]:
      """Evalúa el nivel de desafío de la aventura"""
      challenge_indicators = {
          'bajo': ['fácil', 'simple', 'básico', 'principiante'],
          'medio': ['intermedio', 'moderado', 'regular', 'normal'],
          'alto': ['difícil', 'complejo', 'avanzado', 'experto'],
          'extremo': ['imposible', 'épico', 'legendario', 'extremo']
      }
      
      text_lower = text.lower()
      detected_level = 'medio'  # Por defecto
      confidence = 0.5
      
      for level, indicators in challenge_indicators.items():
          for indicator in indicators:
              if indicator in text_lower:
                  detected_level = level
                  confidence = 0.8
                  break
      
      return {
          'level': detected_level,
          'confidence': confidence,
          'thrill_factor': self._calculate_thrill_factor(detected_level),
          'preparation_needed': self._assess_preparation_needs(detected_level)
      }
  
  def _map_exploration_routes(self, text: str) -> List[Dict[str, Any]]:
      """Mapea rutas de exploración posibles"""
      routes = [
          {
              'name': 'Ruta del Pionero',
              'description': 'Camino directo hacia lo desconocido',
              'difficulty': 'alto',
              'discovery_potential': 0.9,
              'time_investment': 'alto'
          },
          {
              'name': 'Sendero del Explorador',
              'description': 'Exploración sistemática y detallada',
              'difficulty': 'medio',
              'discovery_potential': 0.8,
              'time_investment': 'medio'
          },
          {
              'name': 'Travesía del Aventurero',
              'description': 'Múltiples rutas con sorpresas',
              'difficulty': 'variable',
              'discovery_potential': 0.85,
              'time_investment': 'flexible'
          }
      ]
      
      # Personalizar rutas según el contenido
      if any(word in text.lower() for word in ['rápido', 'urgente', 'inmediato']):
          routes.insert(0, {
              'name': 'Expedición Relámpago',
              'description': 'Aventura rápida e intensa',
              'difficulty': 'medio',
              'discovery_potential': 0.7,
              'time_investment': 'bajo'
          })
      
      return routes
  
  def _create_adventure_plan(self, opportunities: List[Dict], challenge_level: Dict) -> Dict[str, Any]:
      """Crea un plan de aventura detallado"""
      plan_phases = []
      
      # Fase de preparación
      if challenge_level['level'] in ['alto', 'extremo']:
          plan_phases.append('Preparación exhaustiva y equipamiento')
      else:
          plan_phases.append('Preparación básica y verificación de recursos')
      
      # Fase de exploración
      plan_phases.extend([
          'Inicio de la expedición con espíritu aventurero',
          'Exploración activa y documentación de descubrimientos',
          'Adaptación a desafíos inesperados'
      ])
      
      # Fase de consolidación
      plan_phases.append('Consolidación de logros y planificación de próximas aventuras')
      
      return {
          'phases': plan_phases,
          'estimated_duration': self._estimate_adventure_duration(challenge_level),
          'success_metrics': self._define_success_metrics(opportunities),
          'contingency_plans': self._create_contingency_plans(challenge_level),
          'celebration_plan': 'Celebración épica de los descubrimientos logrados'
      }
  
  def _generate_bold_suggestions(self, text: str) -> List[str]:
      """Genera sugerencias audaces y aventureras"""
      base_suggestions = [
          "¡Vamos más allá de lo convencional y exploremos territorios inexplorados!",
          "¿Qué tal si abordamos esto desde un ángulo completamente nuevo y emocionante?",
          "¡Convirtamos esto en una aventura épica de descubrimiento!",
          "¿Por qué no intentamos el enfoque más audaz y ver qué sucede?",
          "¡Hagamos de esto una expedición memorable hacia lo desconocido!"
      ]
      
      # Sugerencias específicas según el contexto
      context_suggestions = []
      text_lower = text.lower()
      
      if 'aprender' in text_lower:
          context_suggestions.append("¡Aprendamos haciendo! La mejor aventura es la experiencia directa.")
      
      if 'problema' in text_lower:
          context_suggestions.append("¡Convirtamos este problema en una quest épica de resolución!")
      
      if 'crear' in text_lower:
          context_suggestions.append("¡Creemos algo que nadie haya imaginado antes!")
      
      return base_suggestions[:3] + context_suggestions
  
  def _assess_discovery_potential(self, text: str) -> Dict[str, float]:
      """Evalúa el potencial de descubrimiento"""
      return {
          'conocimiento_nuevo': random.uniform(0.7, 0.95),
          'experiencias_únicas': random.uniform(0.8, 0.9),
          'conexiones_inesperadas': random.uniform(0.6, 0.85),
          'crecimiento_personal': random.uniform(0.75, 0.9),
          'historias_épicas': random.uniform(0.8, 0.95)
      }
  
  def _recommend_adventure_gear(self, challenge_level: Dict) -> List[str]:
      """Recomienda el 'equipo' necesario para la aventura"""
      base_gear = [
          "Curiosidad insaciable (esencial)",
          "Mente abierta a posibilidades",
          "Espíritu resiliente ante obstáculos"
      ]
      
      level = challenge_level['level']
      
      if level == 'bajo':
          specific_gear = [
              "Entusiasmo básico",
              "Disposición a experimentar"
          ]
      elif level == 'medio':
          specific_gear = [
              "Determinación moderada",
              "Flexibilidad adaptativa",
              "Paciencia exploratoria"
          ]
      elif level == 'alto':
          specific_gear = [
              "Coraje extraordinario",
              "Persistencia inquebrantable",
              "Creatividad para resolver desafíos"
          ]
      else:  # extremo
          specific_gear = [
              "Valentía legendaria",
              "Innovación radical",
              "Resistencia épica",
              "Visión de pionero"
          ]
      
      return base_gear + specific_gear
  
  def _generate_expedition_motto(self) -> str:
      """Genera un lema para la expedición"""
      mottos = [
          "¡Hacia lo desconocido y más allá!",
          "¡La aventura comienza con el primer paso audaz!",
          "¡Exploramos, descubrimos, conquistamos!",
          "¡Sin límites, sin miedo, solo aventura pura!",
          "¡Cada desafío es una oportunidad de grandeza!",
          "¡Pioneros de nuestro propio destino!",
          "¡La audacia es nuestro mapa, la curiosidad nuestra brújula!"
      ]
      return random.choice(mottos)
  
  def _measure_excitement(self, text: str) -> float:
      """Mide el nivel de emoción de la aventura"""
      excitement_words = [
          'emocionante', 'increíble', 'fantástico', 'genial', 'asombroso',
          'aventura', 'explorar', 'descubrir', 'nuevo', 'diferente'
      ]
      
      text_lower = text.lower()
      excitement_score = sum(1 for word in excitement_words if word in text_lower)
      base_excitement = 0.7  # Nivel base de emoción aventurera
      
      return min(1.0, base_excitement + (excitement_score * 0.1))
  
  def _calculate_thrill_factor(self, challenge_level: str) -> float:
      """Calcula el factor de emoción basado en el nivel de desafío"""
      thrill_map = {
          'bajo': 0.6,
          'medio': 0.75,
          'alto': 0.9,
          'extremo': 1.0
      }
      return thrill_map.get(challenge_level, 0.75)
  
  def _assess_preparation_needs(self, challenge_level: str) -> List[str]:
      """Evalúa las necesidades de preparación"""
      prep_map = {
          'bajo': ['Verificación básica de recursos', 'Actitud positiva'],
          'medio': ['Planificación moderada', 'Preparación mental', 'Recursos adicionales'],
          'alto': ['Planificación detallada', 'Entrenamiento específico', 'Equipo especializado'],
          'extremo': ['Preparación exhaustiva', 'Entrenamiento intensivo', 'Equipo de élite', 'Plan de contingencia múltiple']
      }
      return prep_map.get(challenge_level, prep_map['medio'])
  
  def _estimate_adventure_duration(self, challenge_level: Dict) -> str:
      """Estima la duración de la aventura"""
      level = challenge_level['level']
      duration_map = {
          'bajo': 'Expedición corta (1-2 sesiones)',
          'medio': 'Aventura moderada (3-5 sesiones)',
          'alto': 'Expedición extensa (1-2 semanas)',
          'extremo': 'Quest épica (tiempo indefinido, vale la pena cada momento)'
      }
      return duration_map.get(level, duration_map['medio'])
  
  def _define_success_metrics(self, opportunities: List[Dict]) -> List[str]:
      """Define métricas de éxito para la aventura"""
      base_metrics = [
          "Nuevos territorios explorados",
          "Descubrimientos únicos realizados",
          "Desafíos superados con creatividad",
          "Experiencias memorables creadas"
      ]
      
      # Métricas específicas según oportunidades
      specific_metrics = []
      for opportunity in opportunities[:2]:  # Limitar a 2
          if opportunity['type'] == 'exploración':
              specific_metrics.append("Profundidad de exploración alcanzada")
          elif opportunity['type'] == 'desafío':
              specific_metrics.append("Nivel de desafío conquistado")
          elif opportunity['type'] == 'novedad':
              specific_metrics.append("Grado de innovación logrado")
      
      return base_metrics + specific_metrics
  
  def _create_contingency_plans(self, challenge_level: Dict) -> List[str]:
      """Crea planes de contingencia"""
      base_plans = [
          "Plan B: Ruta alternativa de exploración",
          "Plan C: Adaptación creativa a obstáculos inesperados"
      ]
      
      if challenge_level['level'] in ['alto', 'extremo']:
          base_plans.extend([
              "Plan D: Reagrupación estratégica y nuevo enfoque",
              "Plan E: Transformación del desafío en oportunidad"
          ])
      
      return base_plans

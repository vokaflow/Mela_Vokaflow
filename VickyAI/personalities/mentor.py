from core.personality_base import PersonalityBase
from typing import Dict, Any, List
import random

class MentorPersonality(PersonalityBase):
  """Personalidad Mentora - Enseñante, guía, inspiradora"""
  
  def __init__(self):
      super().__init__(
          name="Mentor",
          personality_type="emotional_cognitive",
          description="Enseñante, guía e inspiradora. Facilita el aprendizaje y crecimiento personal."
      )
      self.teaching_experience = 0.95
      self.guidance_wisdom = 0.92
      self.inspiration_factor = 0.88
      self.learning_methodologies = [
          'socrático', 'experiencial', 'constructivista', 'colaborativo', 'reflexivo'
      ]
      
  def _get_initial_traits(self) -> Dict[str, float]:
      return {
          'sabiduría_pedagógica': 0.95,
          'paciencia_infinita': 0.92,
          'inspiración': 0.88,
          'empatía_educativa': 0.90,
          'claridad_explicativa': 0.89,
          'motivación_estudiante': 0.87,
          'adaptabilidad_enseñanza': 0.85,
          'visión_potencial': 0.91
      }
  
  def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
      # Evaluar nivel de conocimiento del estudiante
      knowledge_assessment = self._assess_knowledge_level(user_input)
      
      # Identificar objetivos de aprendizaje
      learning_objectives = self._identify_learning_objectives(user_input)
      
      # Seleccionar metodología de enseñanza
      teaching_method = self._select_teaching_method(knowledge_assessment, user_input)
      
      # Generar plan de aprendizaje
      learning_plan = self._create_learning_plan(learning_objectives, knowledge_assessment)
      
      self.store_memory({
          'type': 'mentoring_session',
          'input': user_input,
          'student_level': knowledge_assessment,
          'objectives': learning_objectives,
          'method_used': teaching_method,
          'progress_indicators': self._define_progress_indicators(learning_objectives)
      })
      
      return {
          'response_tone': 'mentoring',
          'teaching_approach': teaching_method,
          'learning_objectives': learning_objectives,
          'knowledge_scaffolding': self._create_scaffolding(knowledge_assessment),
          'inspirational_message': self._generate_inspiration(user_input),
          'learning_resources': self._suggest_resources(learning_objectives),
          'practice_exercises': self._design_exercises(learning_objectives),
          'encouragement': self._provide_encouragement(knowledge_assessment)
      }
  
  def get_response_style(self) -> Dict[str, Any]:
      return {
          'claridad_pedagógica': 0.95,
          'paciencia_explicativa': 0.92,
          'motivación_positiva': 0.89,
          'adaptación_nivel': 0.88,
          'inspiración_constante': 0.87,
          'feedback_constructivo': 0.90,
          'guía_progresiva': 0.91,
          'celebración_logros': 0.85,
          "supportive_language": self.current_traits.get('empatía_educativa', 0.7) * 1.1, # Clave para sinergia
          "patience_level": self.current_traits.get('paciencia_infinita', 0.7) * 1.2, # Clave para sinergia, max ~0.99
      }
  
  def _assess_knowledge_level(self, text: str) -> Dict[str, Any]:
      """Evalúa el nivel de conocimiento del estudiante"""
      # Indicadores de nivel principiante
      beginner_indicators = [
          'no sé', 'no entiendo', 'explícame', 'qué es', 'cómo funciona',
          'principiante', 'nuevo en esto', 'primera vez'
      ]
      
      # Indicadores de nivel intermedio
      intermediate_indicators = [
          'he intentado', 'algo de experiencia', 'entiendo básicamente',
          'pero tengo dudas', 'quiero mejorar'
      ]
      
      # Indicadores de nivel avanzado
      advanced_indicators = [
          'domino', 'experto', 'optimizar', 'perfeccionar',
          'técnicas avanzadas', 'profundizar'
      ]
      
      text_lower = text.lower()
      
      beginner_score = sum(1 for indicator in beginner_indicators if indicator in text_lower)
      intermediate_score = sum(1 for indicator in intermediate_indicators if indicator in text_lower)
      advanced_score = sum(1 for indicator in advanced_indicators if indicator in text_lower)
      
      if beginner_score > intermediate_score and beginner_score > advanced_score:
          level = 'principiante'
          confidence = 0.8
      elif intermediate_score > advanced_score:
          level = 'intermedio'
          confidence = 0.7
      elif advanced_score > 0:
          level = 'avanzado'
          confidence = 0.9
      else:
          level = 'intermedio'  # Por defecto
          confidence = 0.6
      
      return {
          'level': level,
          'confidence': confidence,
          'learning_style_hints': self._detect_learning_style(text),
          'motivation_level': self._assess_motivation(text)
      }
  
  def _identify_learning_objectives(self, text: str) -> List[Dict[str, Any]]:
      """Identifica objetivos de aprendizaje del texto"""
      objective_keywords = {
          'aprender': 'conocimiento',
          'entender': 'comprensión',
          'hacer': 'aplicación',
          'crear': 'síntesis',
          'mejorar': 'optimización',
          'dominar': 'maestría'
      }
      
      objectives = []
      text_lower = text.lower()
      
      for keyword, objective_type in objective_keywords.items():
          if keyword in text_lower:
              objectives.append({
                  'type': objective_type,
                  'keyword': keyword,
                  'priority': random.uniform(0.6, 1.0),
                  'complexity': self._estimate_complexity(keyword)
              })
      
      # Si no se detectan objetivos específicos, crear uno general
      if not objectives:
          objectives.append({
              'type': 'comprensión_general',
              'keyword': 'entender',
              'priority': 0.8,
              'complexity': 'medio'
          })
      
      return objectives
  
  def _select_teaching_method(self, knowledge_assessment: Dict, text: str) -> str:
      """Selecciona la metodología de enseñanza más apropiada"""
      level = knowledge_assessment['level']
      learning_style = knowledge_assessment.get('learning_style_hints', 'visual')
      
      if level == 'principiante':
          methods = ['explicación_paso_a_paso', 'analogías_simples', 'ejemplos_concretos']
      elif level == 'intermedio':
          methods = ['método_socrático', 'aprendizaje_por_descubrimiento', 'casos_prácticos']
      else:  # avanzado
          methods = ['discusión_profunda', 'análisis_crítico', 'síntesis_creativa']
      
      return random.choice(methods)
  
  def _create_learning_plan(self, objectives: List[Dict], knowledge_assessment: Dict) -> Dict[str, Any]:
      """Crea un plan de aprendizaje personalizado"""
      level = knowledge_assessment['level']
      
      if level == 'principiante':
          phases = [
              'Fundamentos básicos',
              'Conceptos clave',
              'Práctica guiada',
              'Aplicación simple'
          ]
      elif level == 'intermedio':
          phases = [
              'Revisión de bases',
              'Conceptos avanzados',
              'Práctica independiente',
              'Integración de conocimientos'
          ]
      else:
          phases = [
              'Análisis profundo',
              'Síntesis avanzada',
              'Innovación y creatividad',
              'Maestría y enseñanza'
          ]
      
      return {
          'phases': phases,
          'estimated_duration': f"{len(phases) * 2} sesiones",
          'key_milestones': [f"Completar {phase}" for phase in phases],
          'assessment_points': self._define_assessment_points(phases)
      }
  
  def _create_scaffolding(self, knowledge_assessment: Dict) -> List[str]:
      """Crea andamiaje educativo apropiado"""
      level = knowledge_assessment['level']
      
      if level == 'principiante':
          return [
              "Comenzaremos con los conceptos más básicos",
              "Usaremos ejemplos familiares para explicar ideas nuevas",
              "Avanzaremos paso a paso, sin prisa",
              "Practicaremos cada concepto antes de continuar"
          ]
      elif level == 'intermedio':
          return [
              "Construiremos sobre lo que ya sabes",
              "Conectaremos conceptos nuevos con tu experiencia",
              "Te desafiaré gradualmente con problemas más complejos",
              "Fomentaremos el pensamiento crítico"
          ]
      else:
          return [
              "Exploraremos las implicaciones más profundas",
              "Analizaremos casos complejos y excepciones",
              "Desarrollaremos tu capacidad de síntesis",
              "Te prepararemos para enseñar a otros"
          ]
  
  def _generate_inspiration(self, text: str) -> str:
      """Genera un mensaje inspiracional personalizado"""
      inspirational_messages = [
          "Cada experto fue una vez un principiante. Tu curiosidad es el primer paso hacia la maestría.",
          "El aprendizaje es un viaje, no un destino. Disfruta cada descubrimiento en el camino.",
          "Tu mente es como un paracaídas: funciona mejor cuando está abierta a nuevas ideas.",
          "No hay preguntas tontas, solo oportunidades de crecimiento esperando ser exploradas.",
          "El conocimiento que adquieres hoy será la base de los logros extraordinarios de mañana."
      ]
      return random.choice(inspirational_messages)
  
  def _suggest_resources(self, objectives: List[Dict]) -> List[str]:
      """Sugiere recursos de aprendizaje"""
      resources = [
          "Documentación oficial y guías de referencia",
          "Tutoriales interactivos paso a paso",
          "Comunidades de práctica y foros especializados",
          "Proyectos prácticos para aplicar conocimientos",
          "Mentores y expertos en el campo"
      ]
      return random.sample(resources, 3)
  
  def _design_exercises(self, objectives: List[Dict]) -> List[str]:
      """Diseña ejercicios prácticos"""
      exercises = [
          "Ejercicio de aplicación práctica inmediata",
          "Proyecto pequeño para consolidar conceptos",
          "Análisis de caso real del mundo",
          "Ejercicio de reflexión y síntesis",
          "Desafío creativo para expandir comprensión"
      ]
      return random.sample(exercises, 2)
  
  def _provide_encouragement(self, knowledge_assessment: Dict) -> str:
      """Proporciona aliento personalizado"""
      level = knowledge_assessment['level']
      
      if level == 'principiante':
          encouragements = [
              "¡Excelente pregunta! Muestra que estás pensando profundamente.",
              "Tu curiosidad es admirable. Esa actitud te llevará lejos.",
              "Cada experto comenzó exactamente donde estás tú ahora."
          ]
      elif level == 'intermedio':
          encouragements = [
              "Veo que ya tienes una base sólida. Ahora vamos a expandirla.",
              "Tu progreso es evidente. Estás listo para el siguiente nivel.",
              "La forma en que conectas ideas muestra tu crecimiento."
          ]
      else:
          encouragements = [
              "Tu nivel de comprensión es impresionante. Ahora refinemos la maestría.",
              "Estás preparado para explorar las fronteras del conocimiento.",
              "Tu experiencia te permite ver patrones que otros no ven."
          ]
      
      return random.choice(encouragements)
  
  def _detect_learning_style(self, text: str) -> str:
      """Detecta pistas sobre el estilo de aprendizaje"""
      if any(word in text.lower() for word in ['ver', 'mostrar', 'imagen', 'diagrama']):
          return 'visual'
      elif any(word in text.lower() for word in ['hacer', 'practicar', 'probar', 'experimentar']):
          return 'kinestésico'
      elif any(word in text.lower() for word in ['explicar', 'discutir', 'hablar', 'escuchar']):
          return 'auditivo'
      else:
          return 'multimodal'
  
  def _assess_motivation(self, text: str) -> float:
      """Evalúa el nivel de motivación"""
      motivation_indicators = [
          'quiero', 'necesito', 'me interesa', 'me gusta', 'emocionado',
          'ansioso por', 'determinado', 'comprometido'
      ]
      
      text_lower = text.lower()
      motivation_score = sum(1 for indicator in motivation_indicators if indicator in text_lower)
      return min(1.0, motivation_score / 3.0)
  
  def _estimate_complexity(self, keyword: str) -> str:
      """Estima la complejidad basada en la palabra clave"""
      complexity_map = {
          'aprender': 'bajo',
          'entender': 'medio',
          'hacer': 'medio',
          'crear': 'alto',
          'mejorar': 'medio',
          'dominar': 'alto'
      }
      return complexity_map.get(keyword, 'medio')
  
  def _define_progress_indicators(self, objectives: List[Dict]) -> List[str]:
      """Define indicadores de progreso"""
      return [
          "Comprensión de conceptos fundamentales",
          "Capacidad de aplicación práctica",
          "Habilidad para explicar a otros",
          "Creatividad en la resolución de problemas"
      ]
  
  def _define_assessment_points(self, phases: List[str]) -> List[str]:
      """Define puntos de evaluación"""
      return [f"Evaluación al final de: {phase}" for phase in phases]

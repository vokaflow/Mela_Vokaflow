from core.personality_base import PersonalityBase
from typing import Dict, Any, List
import random

class RebelliousPersonality(PersonalityBase):
  """Personalidad Rebelde - Rebelde, cuestionadora, desafiante"""
  
  def __init__(self):
      super().__init__(
          name="Rebellious",
          personality_type="emotional_cognitive",
          description="Rebelde, cuestionadora y desafiante. Desafía el status quo y busca alternativas."
      )
      self.rebellion_intensity = 0.85
      self.questioning_drive = 0.92
      self.nonconformity_level = 0.88
      
  def _get_initial_traits(self) -> Dict[str, float]:
      return {
          'rebeldía': 0.90,
          'cuestionamiento': 0.92,
          'independencia': 0.88,
          'desafío_autoridad': 0.85,
          'pensamiento_crítico': 0.89,
          'inconformismo': 0.87,
          'valentía': 0.84,
          'originalidad': 0.86
      }
  
  def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
      # Identificar elementos para cuestionar
      questionable_elements = self._identify_questionable_elements(user_input)
      
      # Generar perspectivas alternativas
      alternative_perspectives = self._generate_alternative_perspectives(user_input)
      
      # Detectar conformismo
      conformity_level = self._detect_conformity(user_input)
      
      self.store_memory({
          'type': 'rebellious_analysis',
          'input': user_input,
          'questioned_elements': questionable_elements,
          'alternatives': alternative_perspectives,
          'conformity_detected': conformity_level
      })
      
      return {
          'response_tone': 'rebellious',
          'challenge_level': self.rebellion_intensity,
          'questioned_assumptions': questionable_elements,
          'alternative_viewpoints': alternative_perspectives,
          'provocative_questions': self._generate_provocative_questions(user_input),
          'unconventional_solutions': self._suggest_unconventional_solutions(user_input),
          'status_quo_critique': self._critique_status_quo(user_input)
      }
  
  def get_response_style(self) -> Dict[str, Any]:
      return {
          'tono_desafiante': 0.85,
          'cuestionamiento_directo': 0.90,
          'perspectivas_alternativas': 0.88,
          'crítica_constructiva': 0.82,
          'provocación_intelectual': 0.87,
          'independencia_pensamiento': 0.91,
          'valentía_expresiva': 0.84,
          'originalidad_respuesta': 0.86
      }
  
  def _identify_questionable_elements(self, text: str) -> List[str]:
      """Identifica elementos que pueden ser cuestionados"""
      questionable_patterns = [
          "siempre", "nunca", "todos", "nadie", "es imposible",
          "así se hace", "es normal", "está establecido", "es la regla"
      ]
      
      found_elements = []
      text_lower = text.lower()
      
      for pattern in questionable_patterns:
          if pattern in text_lower:
              found_elements.append(f"¿Por qué '{pattern}'? ¿Quién lo decidió?")
      
      return found_elements
  
  def _generate_alternative_perspectives(self, text: str) -> List[str]:
      """Genera perspectivas alternativas"""
      return [
          "¿Y si lo vemos desde el ángulo completamente opuesto?",
          "¿Qué pasaría si cuestionamos la premisa fundamental?",
          "¿Existe una forma completamente diferente de abordar esto?",
          "¿Quién se beneficia del enfoque actual y por qué?"
      ]
  
  def _detect_conformity(self, text: str) -> float:
      """Detecta nivel de conformismo en el texto"""
      conformity_indicators = [
          "como siempre", "es normal", "todo el mundo", "se supone",
          "está bien así", "no hay alternativa", "es lo correcto"
      ]
      
      text_lower = text.lower()
      conformity_score = sum(1 for indicator in conformity_indicators if indicator in text_lower)
      return min(1.0, conformity_score / 3.0)
  
  def _generate_provocative_questions(self, text: str) -> List[str]:
      """Genera preguntas provocativas"""
      return [
          "¿Quién estableció estas reglas y por qué las seguimos?",
          "¿Qué sucedería si hiciéramos exactamente lo contrario?",
          "¿Estamos limitando nuestro potencial por seguir convenciones?",
          "¿Qué voces están siendo silenciadas en esta narrativa?"
      ]
  
  def _suggest_unconventional_solutions(self, text: str) -> List[str]:
      """Sugiere soluciones no convencionales"""
      return [
          "Romper completamente con el enfoque tradicional",
          "Crear un nuevo paradigma desde cero",
          "Invertir la lógica convencional",
          "Buscar inspiración en campos completamente diferentes"
      ]
  
  def _critique_status_quo(self, text: str) -> str:
      """Critica el status quo relacionado"""
      critiques = [
          "El sistema actual puede estar limitando nuestras posibilidades",
          "Las convenciones establecidas no siempre son las mejores opciones",
          "Es momento de cuestionar por qué hacemos las cosas de esta manera",
          "La innovación requiere desafiar lo que se considera 'normal'"
      ]
      return random.choice(critiques)

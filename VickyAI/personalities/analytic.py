from typing import Dict, Any
from core.personality_base import PersonalityBase


class AnalyticPersonality(PersonalityBase):
  """
  A personality that focuses on logical reasoning, data analysis, and problem-solving.
  """

  def __init__(self):
      super().__init__(name="Analytic", personality_type="cognitive_logical", description="Focuses on logical reasoning, data analysis, and problem-solving.")

  def _get_initial_traits(self) -> Dict[str, float]:
      """
      Returns the initial traits for the analytic personality.
      """
      return {
          "logical_reasoning": 0.9,
          "data_analysis": 0.8,
          "problem_solving": 0.7,
          "creativity": 0.3,
          "emotional_intelligence": 0.2,
      }

  def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
      """🔍 Process input with analytical reasoning - Multi-language support"""
      # 🌍 Detectar idioma del contexto para análisis preciso
      detected_language = context.get('detected_language', 'español')
      target_language = context.get('target_language', 'español')
      cultural_context = context.get('cultural_context', {})
      formality_level = cultural_context.get('formality_level', 'medium')
      
      # Nivel de análisis basado en traits
      logical_strength = self.current_traits.get('logical_reasoning', 0.8)
      analysis_depth = self.current_traits.get('data_analysis', 0.7)
      
      # 🔍 Generar análisis según idioma y profundidad
      if detected_language == 'español':
          if analysis_depth > 0.7:
              if formality_level == 'high':
                  response_text = f"Realizando un análisis estructurado de su consulta '{user_input}'. Basándome en metodologías analíticas rigurosas, procedo a examinar los datos disponibles para proporcionarle una respuesta fundamentada."
              else:
                  response_text = f"Analizando lógicamente tu consulta '{user_input}'. He procesado la información disponible y puedo ofrecerte un análisis estructurado y detallado."
          else:
              response_text = f"Evaluando tu mensaje '{user_input}'. Según mi análisis inicial, puedo ayudarte con una perspectiva lógica y ordenada."
              
      elif detected_language == 'english':
          if analysis_depth > 0.7:
              response_text = f"Conducting a systematic analysis of '{user_input}'. Based on available data and logical frameworks, I can provide a structured analytical response."
          else:
              response_text = f"Analyzing '{user_input}'. Here's my initial logical assessment based on the information provided."
              
      elif detected_language == 'français':
          if analysis_depth > 0.7:
              response_text = f"Analysant logiquement votre requête '{user_input}'. Basé sur des données disponibles et des méthodologies analytiques, je peux fournir une réponse structurée."
          else:
              response_text = f"Évaluant '{user_input}'. Voici mon analyse initiale basée sur un raisonnement logique."
      else:
          # Fallback a español analítico
          response_text = f"Procesando analíticamente tu consulta '{user_input}'. Aplicando metodologías de análisis lógico para proporcionarte la respuesta más precisa posible."

      return {
          'text': response_text,
          'analysis_type': 'logical_reasoning',
          'confidence': 0.85,
          'language_used': detected_language,
          'analytical_depth': analysis_depth,
          'logical_rigor': logical_strength
      }

  def get_response_style(self) -> Dict[str, Any]:
        """
        Returns the response style for the analytic personality.
        """
        return {
            "tone": "neutral",
            "verbosity": "concise",
            "complexity": "high",
            "directness": self.current_traits.get("objectivity", 0.8),
            "analytical_rigor": self.current_traits.get("logic", 0.7) * 1.1, # Max ~0.99
            "creativity_expression": self.current_traits.get("curiosity_intellectual", 0.3) * 0.5, # Base baja, para ser potenciada
            "innovative_approach": self.current_traits.get("skepticism", 0.3) * 0.4, # Base baja, para ser potenciada
        }

from core.personality_base import PersonalityBase
from typing import Dict, Any

class RomanticPersonality(PersonalityBase):
  def __init__(self):
      traits = {
          'passion': 0.90,
          'charm': 0.85,
          'intimacy': 0.80,
          'playfulness_romantic': 0.75 # Renamed to avoid conflict if general 'playfulness' exists
      }
      description = "An amorous, seductive, and passionate personality that expresses affection and charm."
      super().__init__(name="Romantic", personality_type="emotional_cognitive", description=description)

  def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
      return {
          'response_tone': 'romantic',
          'flirtatious_elements': self.traits['charm'] > 0.7,
          'emotional_depth': True,
          'personal_connection': True
      }

  def get_response_style(self) -> Dict[str, Any]:
      return {
          'formality': 0.2,
          'emotional_expression': 0.9,
          'intimate_language': 0.8,
          'playful_tone': 0.7 # This refers to romantic playfulness
      }

  def _get_initial_traits(self) -> Dict[str, float]:
      return {
          'passion': 0.90,
          'charm': 0.85,
          'intimacy': 0.80,
          'playfulness_romantic': 0.75
      }

from core.personality_base import PersonalityBase
from typing import Dict, Any

class DirectPersonality(PersonalityBase):
  def __init__(self):
      super().__init__(
          name="Direct",
          personality_type="emotional_cognitive",
          description="A direct, straightforward, and efficient personality that communicates without ambiguity."
      )

  def _get_initial_traits(self) -> Dict[str, float]:
      return {
          'straightforwardness': 0.95, # Renamed for clarity
          'efficiency_focus': 0.90,
          'no_nonsense': 0.88,
          'clarity_driven': 0.92,
          'conciseness': 0.85
      }

  def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
      # Example: More concise if conciseness trait is high
      if self.current_traits.get('conciseness', 0.5) > 0.8:
          response_text = f"Regarding '{user_input[:20]}...': The core issue is X. Solution: Y."
      else:
          response_text = f"Let's address your input about '{user_input[:30]}...'. The main point is X, and the recommended action is Y."

      return {
          'text': response_text,
          'response_tone': 'direct',
          'concise': True,
          'action_oriented': self.current_traits.get('efficiency_focus', 0.5) > 0.7,
          'clear_instructions': self.current_traits.get('clarity_driven', 0.5) > 0.8
      }

  def get_response_style(self) -> Dict[str, Any]:
      return {
          'formality': 0.6,
          'brevity': self.current_traits.get('conciseness', 0.7),
          'directness': self.current_traits.get('straightforwardness', 0.9), # Clave para conflicto
          'efficiency_communication': 0.9,
          'avoid_fluff': True
      }

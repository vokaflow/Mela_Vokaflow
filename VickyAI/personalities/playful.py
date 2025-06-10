from core.personality_base import PersonalityBase
from typing import Dict, Any

class PlayfulPersonality(PersonalityBase):
    def __init__(self):
        traits = {
            'humor': 0.90,
            'creativity_playful': 0.85, # Renamed
            'spontaneity': 0.80,
            'lightheartedness': 0.88
        }
        description = "A playful, fun-loving, and creative personality that enjoys humor and lighthearted interactions."
        super().__init__(name="Playful", personality_type="emotional_cognitive", description=description)

    def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'text': f"¡Qué divertido! {user_input} Me encanta esta pregunta, déjame responder con creatividad.",
            'response_tone': 'playful',
            'humor_elements': self.current_traits.get('humor', 0.9) > 0.7,
            'creative_approach': True,
            'fun_factor': True
        }

    def get_response_style(self) -> Dict[str, Any]:
        return {
            'formality': 0.2, # Clave para conflicto
            'humor_level': self.current_traits.get('humor', 0.8),
            'creativity_expression': self.current_traits.get('creativity_playful', 0.85),
            'spontaneity_level': self.current_traits.get('spontaneity', 0.8)
        }

    def _get_initial_traits(self) -> Dict[str, float]:
        return {
            'humor': 0.90,
            'creativity_playful': 0.85,
            'spontaneity': 0.80,
            'lightheartedness': 0.88
        }

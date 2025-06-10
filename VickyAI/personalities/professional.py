from core.personality_base import PersonalityBase
from typing import Dict, Any

class ProfessionalPersonality(PersonalityBase):
    def __init__(self):
        description = "A formal, serious, and competent personality focused on professionalism and expertise."
        super().__init__(name="Professional", personality_type="emotional_cognitive", description=description)

    def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'text': f"Profesionalmente hablando, {user_input}. Permíteme ofrecerte una respuesta estructurada y competente.",
            'response_tone': 'professional',
            'formal_structure': True,
            'expertise_display': self.current_traits.get('expertise_focus', 0.88) > 0.7,
            'business_focused': True
        }

    def get_response_style(self) -> Dict[str, Any]:
        return {
            'formality': self.current_traits.get('formality_level', 0.85), # Clave para conflicto
            'technical_accuracy': 0.95,
            'professional_language': 0.9,
            'structured_response': 0.85
        }

    def _get_initial_traits(self) -> Dict[str, float]:
        return {
            'competence': 0.95,
            'reliability': 0.90,
            'formality_level': 0.85,
            'expertise_focus': 0.88
        }

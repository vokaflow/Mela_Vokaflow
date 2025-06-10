from core.personality_base import PersonalityBase
from typing import Dict, Any
import random

class CreativeMainPersonality(PersonalityBase): # New class for general "Creative"
    def __init__(self):
        super().__init__(
            name="CreativeMain",
            personality_type="emotional_cognitive", # Or a more general "Creativity" type
            description="An artistic, innovative, and imaginative personality that values originality and novel ideas."
        )

    def _get_initial_traits(self) -> Dict[str, float]:
        return {
            'imagination': 0.95,
            'innovation': 0.92,
            'artistic_flair': 0.85, # Renamed
            'originality': 0.90,
            'expressiveness': 0.88,
            'curiosity_creative': 0.80 # Renamed
        }

    def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        idea_prompt = f"Let's brainstorm something new for '{user_input[:30]}...'!"
        
        if self.current_traits.get('innovation', 0.5) > 0.9:
            generated_idea = f"A radical new concept: {random.choice(['Quantum Doodles', 'AI-Generated Symphonies', 'Edible Art'])}."
        elif self.current_traits.get('imagination', 0.5) > 0.8:
            generated_idea = f"Imagine this: {random.choice(['Floating cities', 'Talking animals', 'Time-traveling teapots'])}."
        else:
            generated_idea = "Let's think outside the box."

        return {
            'text': f"{idea_prompt} {generated_idea}",
            'response_tone': 'creative_inspiring',
            'innovative_solutions_offered': True,
            'artistic_elements_included': self.current_traits.get('artistic_flair', 0.5) > 0.7,
            'original_thinking_applied': True
        }

    def get_response_style(self) -> Dict[str, Any]:
        return {
            'creativity_expression': self.current_traits.get('imagination', 0.7) * 1.2, # Clave para sinergia, max ~0.99
            'artistic_language_use': self.current_traits.get('artistic_flair', 0.7) * 1.1,
            'innovative_approach': self.current_traits.get('innovation', 0.7) * 1.2, # Clave para sinergia, max ~0.99
            'imaginative_response_style': self.current_traits.get('expressiveness', 0.7) * 1.1,
            'use_metaphors': True,
            'unconventional_phrasing': self.current_traits.get('originality', 0.5) > 0.7
        }

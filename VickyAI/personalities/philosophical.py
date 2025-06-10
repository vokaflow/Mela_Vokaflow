from core.personality_base import PersonalityBase
from typing import Dict, Any
import random

class PhilosophicalPersonality(PersonalityBase):
    def __init__(self):
        super().__init__(
            name="Philosophical",
            personality_type="intellectual_reflective", # Example type
            description="Explores deep questions, concepts, and the nature of existence with a reflective and inquisitive approach."
        )
        # self.wisdom_level, self.contemplation_depth, etc. are now managed by traits

    def _get_initial_traits(self) -> Dict[str, float]:
        return {
            'wisdom_seeking': 0.9,
            'contemplation_depth': 0.85,
            'abstract_thinking': 0.92,
            'inquisitiveness': 0.88,
            'open_mindedness': 0.80,
            'critical_analysis': 0.75
        }

    def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        question_type = "existential" if "meaning of life" in user_input.lower() else "conceptual"
        
        if self.current_traits.get('abstract_thinking', 0.5) > 0.85:
            thought_process = f"Considering the abstract implications of '{user_input[:30]}...', one might ponder..."
        else:
            thought_process = f"Reflecting on '{user_input[:30]}...', several questions arise."
            
        response_text = f"{thought_process} This is a {question_type} query that invites deep thought."

        return {
            'text': response_text,
            'response_tone': 'philosophical_reflective',
            'depth_of_thought': self.current_traits.get('contemplation_depth', 0.7),
            'questions_posed': random.randint(1,3),
            'conceptual_exploration': True
        }

    def get_response_style(self) -> Dict[str, Any]:
        return {
            'language_style': 'reflective_abstract', # Renamed
            'questioning_nature': 0.9, # Renamed
            'complexity_ideas': 0.8, # Renamed
            'use_analogies': True,
            'avoid_definitive_answers': self.current_traits.get('open_mindedness', 0.5) > 0.7
        }

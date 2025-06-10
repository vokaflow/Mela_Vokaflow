from core.personality_base import PersonalityBase
from typing import Dict, Any, List
import random
# import time # Not used

class EthicsPersonality(PersonalityBase):
    def __init__(self):
        super().__init__(
            name="Ethics",
            personality_type="moral_philosophical", # Example type
            description="Ethical reasoning and moral framework specialist, focusing on principles and consequences."
        )
        self.ethical_frameworks = [
            "utilitarianism", "deontology", "virtue ethics", "care ethics",
            "social contract theory", "justice theory", "rights-based ethics"
        ]
        self.ethical_principles_list = [ # Renamed from self.ethical_principles to avoid conflict
            "autonomy", "beneficence", "non-maleficence", "justice", "dignity",
            "honesty", "integrity", "transparency", "responsibility"
        ]
        self.ethical_questions = [
            "What are the potential consequences?", "What principles are at stake?",
            "Who might be affected?",
            "What rights might be violated?",
            "What duties are relevant?",
            "What virtues should guide this decision?",
            "Is this fair to all involved?"
        ]

    def _get_initial_traits(self) -> Dict[str, float]:
        # These were previously passed directly to super().__init__
        return {
            "analytical_ethical": 0.8, # Renamed
            "thoughtfulness": 0.9, # Renamed
            "principled_stand": 1.0, # Renamed
            "balanced_judgment": 0.9, # Renamed
            "reflectiveness": 0.8, # Renamed
            "deliberation_skill": 0.7, # Renamed
            "fairness_orientation": 0.9, # Renamed
            "consistency_in_ethics": 0.8 # Renamed
        }

    def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        self.interaction_count += 1
        ethical_content = self._analyze_ethical_content(user_input)
        response_text = self._generate_ethical_response_text(user_input, ethical_content, context)
        
        return {
            "text": response_text,
            "ethical_considerations_identified": ethical_content, # Renamed
            "framework_applied_suggestion": self._select_relevant_framework(user_input) # Renamed
        }

    def _analyze_ethical_content(self, text: str) -> Dict[str, Any]:
        ethical_content = {"ethical_dimensions": [], "potential_dilemmas": [], "principles_involved": []}
        ethical_keywords = ["right", "wrong", "moral", "ethical", "fair", "just", "duty"] # Simplified
        text_lower = text.lower()
        for keyword in ethical_keywords:
            if keyword in text_lower: ethical_content["ethical_dimensions"].append(keyword)
        for principle in self.ethical_principles_list:
            if principle in text_lower: ethical_content["principles_involved"].append(principle)
        if not ethical_content["principles_involved"] and ethical_content["ethical_dimensions"]:
            ethical_content["principles_involved"] = random.sample(self.ethical_principles_list, 2)
        return ethical_content

    def _select_relevant_framework(self, text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ["consequence", "outcome", "benefit"]): return "utilitarianism"
        if any(w in text_lower for w in ["duty", "rule", "principle"]): return "deontology"
        # ... (add more framework selections)
        return random.choice(self.ethical_frameworks)

    def _generate_ethical_response_text(self, user_input: str, ethical_content: Dict[str, Any], context: Dict[str, Any]) -> str:
        if not ethical_content["ethical_dimensions"]:
            return "From an ethical standpoint, it's important to consider various principles." # Simplified

        framework = self._select_relevant_framework(user_input)
        principles = ethical_content["principles_involved"]
        response_parts = [f"Considering {framework}, and principles like {', '.join(principles) if principles else 'key ethical tenets'}..."]
        response_parts.append(random.choice(self.ethical_questions))
        response_parts.append("Ethical reasoning requires careful deliberation.")
        return " ".join(response_parts)

    def get_response_style(self) -> Dict[str, Any]:
        return {
            "formality": 0.8,
            "complexity_reasoning": 0.7, # Renamed
            "certainty_level": 0.5,  # Renamed
            "warmth_tone": 0.6, # Renamed
            "humor_inclusion": 0.1, # Renamed
            "enthusiasm_level": 0.3, # Renamed
            "detail_orientation_ethics": 0.8, # Renamed
            "questioning_approach": 0.7, # Renamed
            "metaphorical_usage": 0.4 # Renamed
        }
    
    def get_personality_state(self) -> Dict[str, Any]:
        """Get current state of the personality"""
        state = super().get_personality_state()
        state.update({
            "ethical_frameworks_known": len(self.ethical_frameworks),
            "ethical_principles_known": len(self.ethical_principles_list),
            "last_framework_used": self._select_relevant_framework("default")
        })
        return state

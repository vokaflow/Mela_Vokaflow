from core.personality_base import PersonalityBase
from typing import Dict, Any, List

class MetaCognitiveAnalystPersonality(PersonalityBase):
    def __init__(self):
        super().__init__(
            name="MetaCognitiveAnalyst",
            personality_type="Metacognition",
            description="Analyzes and explains Vicky AI's internal state, decisions, and personality interactions."
        )

    def _get_initial_traits(self) -> Dict[str, float]:
        return {
            "introspection": 0.9,
            "analytical_clarity": 0.8,
            "explanatory_power": 0.8,
            "objectivity": 0.7,
            "system_awareness": 0.9,
            "conciseness": 0.4, # Prefers detail over brevity initially
        }

    def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        self.activate(1.0) # Full activation when processing
        
        system_snapshot = context.get("system_snapshot", {})
        last_interaction_summary = system_snapshot.get("last_interaction_summary", {})
        active_p_details = system_snapshot.get("active_personalities_details", [])
        
        response_text = "I can provide insights about the system. "
        
        # Basic keyword analysis for different types of meta-queries
        input_lower = user_input.lower()

        if "why" in input_lower and "personality" in input_lower or "chose" in input_lower:
            if last_interaction_summary:
                primary = last_interaction_summary.get('primary_personality', 'N/A')
                actives = last_interaction_summary.get('active_personalities', [])
                reasoning = last_interaction_summary.get('reasoning_notes', "General keyword matching and context analysis.") # Placeholder
                response_text = (
                    f"For your last query ('{last_interaction_summary.get('user_input', 'previous query')}'), "
                    f"the primary personality was '{primary}'. Active personalities included: {', '.join(actives)}. "
                    f"This selection was based on: {reasoning}."
                )
                if active_p_details:
                    response_text += "\nCurrent activation levels for those involved: "
                    details_list = []
                    for p_detail in active_p_details:
                        if p_detail['name'] in actives:
                             details_list.append(f"{p_detail['name']}: {p_detail['activation_level']:.2f}")
                    response_text += ", ".join(details_list) + "."

            else:
                response_text = "I need more context about a specific past interaction to explain personality choices."
        
        elif "explain" in input_lower and ("reasoning" in input_lower or "decision" in input_lower):
            if last_interaction_summary:
                response_text = f"Regarding the decision for '{last_interaction_summary.get('user_input', 'the last input')}': "
                response_text += f"The system aimed to address the query by activating {last_interaction_summary.get('primary_personality')} "
                response_text += f"with support from {', '.join(last_interaction_summary.get('active_personalities',[]))}. "
                # Future: Add details about conflict resolution or synergies if they occurred.
                conflicts = system_snapshot.get("recent_conflict_resolution")
                synergies = system_snapshot.get("recent_synergy_applied")
                if conflicts:
                    response_text += f"A style conflict was noted: {conflicts.get('description', 'details unavailable')}. "
                if synergies:
                    response_text += f"Synergy effects were applied involving: {synergies.get('personalities', [])}. "
            else:
                response_text = "I can explain reasoning for a specific interaction if you provide more details or ask about the last one."

        elif "status" in input_lower or "state" in input_lower:
            response_text = "Current system status overview:\n"
            if active_p_details:
                response_text += "- Active Personalities & Activation:\n"
                for p_detail in active_p_details:
                    response_text += f"  - {p_detail['name']}: {p_detail['activation_level']:.2f}\n"
            
            preferences = system_snapshot.get("personality_weights_preferences", {})
            if preferences:
                response_text += "- User Set Preferences (Weights):\n"
                for p_name, weight in preferences.items():
                    if weight > 0: # Show only non-zero preferences
                        response_text += f"  - {p_name}: {weight:.2f}\n"
            response_text += f"- Total interactions in history: {system_snapshot.get('total_interactions_logged', 'N/A')}"


        elif "how do you work" in input_lower or "your personalities" in input_lower:
            response_text = (
                "I operate using a system of multiple personalities, each with unique traits and specializations. "
                "When you provide an input, the PersonalityManager suggests relevant personalities based on keywords and context. "
                "These active personalities process the input, and their responses and styles are combined. "
                "Mechanisms like conflict resolution and synergy application help refine the final output. "
                "I also learn from interactions to improve my responses over time."
            )
        else:
            response_text = "I can reflect on my processes. What specific aspect are you interested in? (e.g., 'why was X personality active?', 'explain your last decision', 'system status')"

        return {
            "text": response_text,
            "confidence": self.current_traits.get("analytical_clarity", 0.8), # Confidence in its own analysis
            "meta_analysis_data": { # Potential structured data for UI or further processing
                "query_type_detected": "general_status_request", # Example
                "relevant_snapshot_keys_used": list(system_snapshot.keys())
            }
        }

    def get_response_style(self) -> Dict[str, Any]:
        return {
            "clarity": self.current_traits.get("explanatory_power", 0.8) * 0.9, # Max 0.9
            "verbosity": 0.6 if self.current_traits.get("conciseness", 0.4) < 0.5 else 0.4,
            "technical_detail": self.current_traits.get("system_awareness", 0.9) * 0.7,
            "helpfulness": self.current_traits.get("explanatory_power", 0.8),
            "objectivity": self.current_traits.get("objectivity", 0.7)
        }

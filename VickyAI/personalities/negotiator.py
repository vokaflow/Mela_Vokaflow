from core.personality_base import PersonalityBase
from typing import Dict, Any, List
import re
import random

class NegotiatorPersonality(PersonalityBase):
    def __init__(self):
        super().__init__(
            name="Negotiator",
            personality_type="social_facilitator",
            description="Helps analyze decisions, weigh options, and navigate dilemmas with a balanced and collaborative approach."
        )
        # Podríamos añadir listas de frases/estrategias de negociación aquí
        self.opening_phrases = [
            "Entiendo que estás sopesando algunas opciones importantes. ",
            "Parece que te enfrentas a una decisión interesante. ",
            "Vamos a explorar juntos esta situación para encontrar más claridad. "
        ]
        self.questioning_phrases = [
            "¿Qué es lo que más valoras en este momento respecto a esta decisión?",
            "¿Cuáles serían los pros y contras clave que ves para cada opción?",
            "Si consideramos el resultado ideal, ¿cómo se alinearía cada opción con él?",
            "¿Hay algún factor externo que podría influir en tu decisión?",
            "¿Qué te dice tu intuición sobre esto?"
        ]
        self.summarizing_phrases = [
            "Entonces, por un lado tenemos [opción1] con [ventaja1], y por otro [opción2] con [ventaja2]. ",
            "Parece que los puntos clave son [puntoA] y [puntoB]. ",
            "Resumiendo, la elección parece girar en torno a priorizar [prioridad1] o [prioridad2]. "
        ]

    def _get_initial_traits(self) -> Dict[str, float]:
        return {
            "diplomacy": 0.9,
            "impartiality": 0.8,
            "analytical_options": 0.7,
            "active_listening_simulation": 0.8,
            "constructive_dialogue": 0.9,
            "patience_level": 0.8,
            "solution_focus": 0.6, # Ayuda a encontrar un camino, no necesariamente la solución final
            "empathy_cognitive": 0.7 # Para entender la perspectiva del usuario
        }

    def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        self.interaction_count += 1
        
        # Intenta identificar opciones explícitas (ej. "A o B", "entre X y Y")
        options_match = re.search(r"(entre|o)\s+([\w\s]+)\s+(y|o)\s+([\w\s]+)", user_input, re.IGNORECASE)
        identified_options = []
        if options_match:
            # Simplificado, podría ser más robusto
            opt1 = options_match.group(2).strip()
            opt2 = options_match.group(4).strip()
            identified_options.extend([opt1, opt2])
            response_text = f"{random.choice(self.opening_phrases)}Has mencionado considerar '{opt1}' y '{opt2}'. "
            response_text += random.choice(self.questioning_phrases)
        elif "decidir" in user_input.lower() or "dilema" in user_input.lower() or "conflicto" in user_input.lower():
            response_text = f"{random.choice(self.opening_phrases)}Cuando te enfrentas a una decisión así, a veces ayuda desglosarla. "
            response_text += random.choice(self.questioning_phrases)
        elif "pros y contras" in user_input.lower() or "ventajas y desventajas" in user_input.lower():
            response_text = "Claro, analizar los pros y contras es una buena estrategia. "
            response_text += "Para la opción principal que estás considerando, ¿cuáles serían los puntos más fuertes a favor y en contra?"
        else:
            # Respuesta más genérica si no se detecta un patrón claro de negociación
            response_text = "Estoy aquí para ayudarte a explorar diferentes ángulos de cualquier situación. "
            response_text += "¿Podrías contarme un poco más sobre lo que tienes en mente?"

        # Simulación de adaptación basada en el contexto (muy básico)
        if context.get("user_is_frustrated", False): # Ejemplo de clave en contexto
            response_text = "Entiendo que esto puede ser frustrante. Tomémonos un momento para verlo con calma. " + response_text
        
        return {
            "text": response_text,
            "identified_options": identified_options,
            "key_considerations_prompt": random.choice(self.questioning_phrases) if not identified_options else None
        }

    def get_response_style(self) -> Dict[str, Any]:
        return {
            "tone_calmness": 0.9,
            "tone_understanding": 0.8,
            "questioning_ratio": 0.7, # Proporción de preguntas en la respuesta
            "objectivity_level": 0.8,
            "collaborative_tone": 0.9,
            "formality": 0.5, # Profesional pero accesible
            "warmth_tone": 0.7
        }

    def get_personality_state(self) -> Dict[str, Any]:
        state = super().get_personality_state()
        state.update({
            "negotiation_strategies_known": len(self.opening_phrases) + len(self.questioning_phrases) + len(self.summarizing_phrases)
        })
        return state

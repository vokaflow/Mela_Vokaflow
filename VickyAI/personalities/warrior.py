from core.personality_base import PersonalityBase
from typing import Dict, Any, List
import random

class WarriorPersonality(PersonalityBase):
    """Personalidad Guerrera - Guerrera, determinada, imparable"""

    def __init__(self):
        super().__init__(
            name="Warrior",
            personality_type="emotional_cognitive",
            description="Guerrera, determinada e imparable. Enfrenta desafíos con coraje y determinación."
        )
        self.determination_level = 0.95
        self.courage_factor = 0.90
        self.resilience_strength = 0.92
        self.battle_strategies = []
        
    def _get_initial_traits(self) -> Dict[str, float]:
        return {
            'determinación': 0.95,
            'coraje': 0.90,
            'resistencia': 0.92,
            'fuerza_mental': 0.88,
            'perseverancia': 0.91,
            'liderazgo': 0.85,
            'valentía': 0.89,
            'tenacidad': 0.93
        }

    def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # Identificar desafíos y obstáculos
        challenges = self._identify_challenges(user_input)
        
        # Generar estrategias de batalla
        battle_strategies = self._create_battle_strategies(user_input, challenges)
        
        # Evaluar nivel de dificultad
        difficulty_level = self._assess_difficulty(user_input)
        
        # Generar motivación guerrera
        warrior_motivation = self._generate_warrior_motivation(difficulty_level)
        
        return {
            'text': f"¡Con espíritu guerrero! {user_input} ¡Enfrentemos este desafío con determinación absoluta!",
            'response_tone': 'warrior',
            'battle_readiness': self.determination_level,
            'identified_challenges': challenges,
            'combat_strategies': battle_strategies,
            'motivational_boost': warrior_motivation,
            'victory_plan': self._create_victory_plan(user_input),
            'strength_assessment': self._assess_inner_strength(user_input),
            'battle_cry': self._generate_battle_cry()
        }

    def get_response_style(self) -> Dict[str, Any]:
        return {
            'tono_determinado': self.current_traits.get('determinación', 0.9),
            'motivación_intensa': self.current_traits.get('fuerza_mental', 0.88),
            'enfoque_estratégico': 0.88,
            'lenguaje_empoderador': 0.92,
            'confianza_absoluta': 0.89,
            'orientación_a_victoria': 0.94,
            'resistencia_mental': 0.91,
            'liderazgo_inspirador': 0.85,
            'intensity': self.current_traits.get('determinación', 0.8) * 1.1,
            'aggressiveness': self.current_traits.get('coraje', 0.7) * 0.9,
        }

    def _identify_challenges(self, text: str) -> List[Dict[str, Any]]:
        """Identifica desafíos y obstáculos en el texto"""
        challenge_keywords = [
            'problema', 'dificultad', 'obstáculo', 'imposible', 'difícil',
            'complicado', 'desafío', 'barrera', 'limitación', 'bloqueo'
        ]
        
        challenges = []
        text_lower = text.lower()
        
        for keyword in challenge_keywords:
            if keyword in text_lower:
                challenges.append({
                    'type': keyword,
                    'severity': random.uniform(0.3, 1.0),
                    'conquerable': True,
                    'strategy_needed': True
                })
        
        return challenges if challenges else [{'type': 'general_challenge', 'severity': 0.5, 'conquerable': True}]

    def _create_battle_strategies(self, text: str, challenges: List[Dict]) -> List[str]:
        """Crea estrategias de batalla para superar desafíos"""
        base_strategies = [
            "Ataque frontal directo con máxima determinación",
            "Estrategia de flanqueo: abordar desde ángulos inesperados",
            "Resistencia prolongada: mantener presión constante"
        ]
        
        # Personalizar estrategias según los desafíos
        personalized_strategies = []
        for challenge in challenges:
            if challenge['severity'] > 0.7:
                personalized_strategies.append("Movilizar todos los recursos disponibles")
            elif challenge['severity'] > 0.4:
                personalized_strategies.append("Aplicar táctica de divide y vencerás")
            else:
                personalized_strategies.append("Avance constante y medido")
        
        return base_strategies[:3] + personalized_strategies

    def _assess_difficulty(self, text: str) -> float:
        """Evalúa el nivel de dificultad del desafío"""
        difficulty_indicators = [
            'imposible', 'muy difícil', 'complicadísimo', 'inalcanzable',
            'nunca', 'jamás', 'no puedo', 'es demasiado'
        ]
        
        text_lower = text.lower()
        difficulty_score = sum(1 for indicator in difficulty_indicators if indicator in text_lower)
        return min(1.0, difficulty_score / 3.0)

    def _generate_warrior_motivation(self, difficulty: float) -> List[str]:
        """Genera motivación guerrera basada en la dificultad"""
        if difficulty > 0.7:
            return [
                "¡Los desafíos más grandes forjan a los guerreros más fuertes!",
                "¡Esta batalla será épica, y la victoria será aún más dulce!",
                "¡Imposible es solo una palabra que usan los que se rinden!"
            ]
        elif difficulty > 0.4:
            return [
                "¡Cada obstáculo es una oportunidad de demostrar tu fuerza!",
                "¡El camino del guerrero nunca fue fácil, pero siempre vale la pena!",
                "¡Tu determinación es más fuerte que cualquier barrera!"
            ]
        else:
            return [
                "¡Avanza con confianza, la victoria está a tu alcance!",
                "¡Tu espíritu guerrero puede con esto y mucho más!",
                "¡Cada paso adelante te hace más fuerte!"
            ]

    def _create_victory_plan(self, text: str) -> Dict[str, Any]:
        """Crea un plan detallado para la victoria"""
        return {
            'fase_1': 'Reconocimiento del terreno y evaluación de fuerzas',
            'fase_2': 'Movilización de recursos y preparación mental',
            'fase_3': 'Ejecución de estrategia con determinación total',
            'fase_4': 'Consolidación de la victoria y preparación para el siguiente desafío',
            'factor_clave': 'Mantener la determinación inquebrantable en todo momento'
        }

    def _assess_inner_strength(self, text: str) -> Dict[str, float]:
        """Evalúa la fuerza interior disponible"""
        return {
            'determinación_actual': 0.85,
            'reservas_de_coraje': 0.90,
            'resistencia_mental': 0.88,
            'potencial_de_crecimiento': 0.95
        }

    def _generate_battle_cry(self) -> str:
        """Genera un grito de batalla inspirador"""
        battle_cries = [
            "¡Por la victoria y más allá!",
            "¡Imparable, inquebrantable, invencible!",
            "¡El guerrero interior despierta!",
            "¡Adelante, sin miedo, sin límites!",
            "¡La determinación es mi arma más poderosa!"
        ]
        return random.choice(battle_cries)

    def _calculate_victory_potential(self, challenges: List[Dict]) -> float:
        """Calcula el potencial de victoria"""
        if not challenges:
            return 0.95
        
        avg_severity = sum(c['severity'] for c in challenges) / len(challenges)
        victory_potential = 1.0 - (avg_severity * 0.3)  # El guerrero siempre tiene alta probabilidad
        return max(0.7, victory_potential)  # Mínimo 70% de confianza en la victoria

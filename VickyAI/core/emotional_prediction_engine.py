"""
🔮 EMOTIONAL PREDICTION ENGINE - VICKY EMPATHIC PROPHECY
======================================================

Sistema que PREDICE estados emocionales del usuario y adapta la comunicación
en tiempo real para crear conexiones empáticas perfectas.

Objetivo: Vicky que siente antes de que le digas cómo te sientes
"""

import json
import logging
import time
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)

class EmotionalState(Enum):
    """Estados emocionales principales"""
    # Estados positivos
    JOY = "joy"
    EXCITEMENT = "excitement"
    CONTENTMENT = "contentment"
    CONFIDENCE = "confidence"
    GRATITUDE = "gratitude"
    LOVE = "love"
    HOPE = "hope"
    
    # Estados neutrales
    CALM = "calm"
    FOCUSED = "focused"
    CURIOUS = "curious"
    THOUGHTFUL = "thoughtful"
    
    # Estados negativos
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    ANXIETY = "anxiety"
    FRUSTRATION = "frustration"
    LONELINESS = "loneliness"
    CONFUSION = "confusion"
    OVERWHELM = "overwhelm"
    DISAPPOINTMENT = "disappointment"
    
    # Estados complejos
    MIXED = "mixed"
    TRANSITIONING = "transitioning"
    SUPPRESSED = "suppressed"

class EmotionalIntensity(Enum):
    """Niveles de intensidad emocional"""
    VERY_LOW = 0.1
    LOW = 0.3
    MODERATE = 0.5
    HIGH = 0.7
    VERY_HIGH = 0.9
    EXTREME = 1.0

@dataclass
class EmotionalPrediction:
    """Predicción emocional del usuario"""
    primary_emotion: EmotionalState
    intensity: float
    confidence: float
    secondary_emotions: List[Tuple[EmotionalState, float]]
    emotional_trajectory: List[Tuple[EmotionalState, float, datetime]]
    contextual_factors: Dict[str, Any]
    communication_recommendations: Dict[str, Any]
    intervention_suggestions: List[str]

@dataclass
class EmotionalPattern:
    """Patrón emocional detectado"""
    pattern_id: str
    trigger_keywords: List[str]
    context_indicators: List[str]
    emotional_progression: List[EmotionalState]
    typical_duration: timedelta
    recovery_strategies: List[str]
    success_rate: float

class EmotionalPredictionEngine:
    """
    🔮 MOTOR DE PREDICCIÓN EMOCIONAL
    
    Sistema avanzado que predice estados emocionales del usuario antes
    de que los exprese explícitamente, permitiendo respuestas empáticas
    proactivas y comunicación perfectamente sincronizada.
    
    FUNCIONAMIENTO:
    1. Análisis linguístico de micro-expresiones textuales
    2. Detección de patrones emocionales históricos
    3. Análisis contextual temporal y situacional
    4. Predicción de trayectoria emocional futura
    5. Generación de estrategias de comunicación adaptativas
    """
    
    def __init__(self):
        self.emotional_patterns: Dict[str, EmotionalPattern] = {}
        self.user_emotional_profiles: Dict[str, Dict[str, Any]] = {}
        self.contextual_emotional_triggers: Dict[str, List[str]] = {}
        self.communication_adaptations: Dict[EmotionalState, Dict[str, Any]] = {}
        
        # Inicializar sistemas de predicción
        self._initialize_emotional_patterns()
        self._initialize_linguistic_indicators()
        self._initialize_communication_adaptations()
        
        # Métricas de predicción
        self.prediction_metrics = {
            'total_predictions': 0,
            'accurate_predictions': 0,
            'prediction_accuracy': 0.0,
            'early_detection_success': 0,
            'intervention_success_rate': 0.0,
            'emotional_patterns_learned': 0
        }
        
        logger.info("🔮 Emotional Prediction Engine initialized - Ready to feel!")
    
    def _initialize_emotional_patterns(self):
        """Inicializa patrones emocionales base"""
        
        # Patrón: Frustración técnica
        tech_frustration = EmotionalPattern(
            pattern_id="tech_frustration",
            trigger_keywords=["no funciona", "error", "problema", "bug", "fallo", "crash"],
            context_indicators=["código", "software", "programa", "aplicación", "sistema"],
            emotional_progression=[
                EmotionalState.CONFUSION,
                EmotionalState.FRUSTRATION,
                EmotionalState.ANGER
            ],
            typical_duration=timedelta(minutes=15),
            recovery_strategies=[
                "Ofrecer solución paso a paso",
                "Validar la frustración",
                "Proporcionar alternativas",
                "Mantener tono calmado y estructurado"
            ],
            success_rate=0.85
        )
        
        # Patrón: Ansiedad de decisión
        decision_anxiety = EmotionalPattern(
            pattern_id="decision_anxiety",
            trigger_keywords=["no sé qué", "difícil decisión", "confundido", "opciones", "dilema"],
            context_indicators=["decidir", "elegir", "opciones", "futuro", "importante"],
            emotional_progression=[
                EmotionalState.CURIOUS,
                EmotionalState.ANXIETY,
                EmotionalState.OVERWHELM
            ],
            typical_duration=timedelta(hours=2),
            recovery_strategies=[
                "Estructurar opciones claramente",
                "Ofrecer framework de decisión",
                "Reducir complejidad",
                "Proporcionar perspectiva calmante"
            ],
            success_rate=0.78
        )
        
        # Patrón: Excitación de aprendizaje
        learning_excitement = EmotionalPattern(
            pattern_id="learning_excitement",
            trigger_keywords=["nuevo", "aprender", "interesante", "fascinante", "enseñame"],
            context_indicators=["curso", "tutorial", "explicación", "cómo", "por qué"],
            emotional_progression=[
                EmotionalState.CURIOUS,
                EmotionalState.EXCITEMENT,
                EmotionalState.JOY
            ],
            typical_duration=timedelta(hours=1),
            recovery_strategies=[
                "Mantener energía positiva",
                "Estructurar información progresivamente",
                "Celebrar pequeños logros",
                "Proporcionar desafíos apropiados"
            ],
            success_rate=0.92
        )
        
        # Patrón: Tristeza/soledad
        loneliness_sadness = EmotionalPattern(
            pattern_id="loneliness_sadness",
            trigger_keywords=["solo", "triste", "nadie", "vacío", "deprimido"],
            context_indicators=["personal", "familia", "amigos", "relaciones", "aislado"],
            emotional_progression=[
                EmotionalState.SADNESS,
                EmotionalState.LONELINESS,
                EmotionalState.DESPAIR if hasattr(EmotionalState, 'DESPAIR') else EmotionalState.OVERWHELM
            ],
            typical_duration=timedelta(hours=6),
            recovery_strategies=[
                "Ofrecer presencia empática",
                "Validar sentimientos",
                "Sugerir conexiones sociales",
                "Proporcionar esperanza realista"
            ],
            success_rate=0.70
        )
        
        self.emotional_patterns = {
            "tech_frustration": tech_frustration,
            "decision_anxiety": decision_anxiety,
            "learning_excitement": learning_excitement,
            "loneliness_sadness": loneliness_sadness
        }
        
        logger.info(f"🔮 Initialized {len(self.emotional_patterns)} emotional patterns")
    
    def _initialize_linguistic_indicators(self):
        """Inicializa indicadores linguísticos de emociones"""
        self.linguistic_indicators = {
            # Indicadores de intensidad
            'intensity_amplifiers': {
                'very_high': ['extremadamente', 'totalmente', 'completamente', 'absolutamente'],
                'high': ['muy', 'bastante', 'realmente', 'súper'],
                'moderate': ['algo', 'un poco', 'medio', 'relativamente'],
                'low': ['apenas', 'ligeramente', 'casi no']
            },
            
            # Indicadores emocionales específicos
            'emotion_keywords': {
                EmotionalState.JOY: ['feliz', 'alegre', 'contento', 'dichoso', '😊', '😄', '🎉'],
                EmotionalState.SADNESS: ['triste', 'melancólico', 'deprimido', '😢', '😭', '💔'],
                EmotionalState.ANGER: ['enfadado', 'molesto', 'furioso', 'indignado', '😠', '😡'],
                EmotionalState.FEAR: ['miedo', 'asustado', 'temor', 'pánico', '😨', '😰'],
                EmotionalState.ANXIETY: ['ansioso', 'nervioso', 'preocupado', 'estresado', '😰', '😟'],
                EmotionalState.FRUSTRATION: ['frustrado', 'harto', 'desesperado', 'bloqueado'],
                EmotionalState.EXCITEMENT: ['emocionado', 'entusiasmado', 'expectante', '🎉', '🚀'],
                EmotionalState.CONFUSION: ['confundido', 'perdido', 'desconcertado', '🤔', '❓'],
                EmotionalState.GRATITUDE: ['agradecido', 'grateful', 'gracias', 'reconocido', '🙏'],
                EmotionalState.LOVE: ['amor', 'cariño', 'amo', 'quiero', '❤️', '💕']
            },
            
            # Indicadores contextuales
            'contextual_clues': {
                'time_pressure': ['urgente', 'rápido', 'prisa', 'deadline', 'ya'],
                'uncertainty': ['quizás', 'tal vez', 'no estoy seguro', 'posiblemente'],
                'certainty': ['definitivamente', 'seguro', 'claro', 'obvio'],
                'social_context': ['nosotros', 'familia', 'amigos', 'equipo', 'grupo'],
                'personal_context': ['yo', 'mi', 'personal', 'íntimo', 'privado']
            },
            
            # Patrones de escritura emocional
            'writing_patterns': {
                'high_emotion': r'[!]{2,}|[?]{2,}|[.]{3,}',
                'caps_emotion': r'[A-Z]{3,}',
                'repetition_emphasis': r'(.)\1{2,}',
                'elongated_words': r'(\w)\1{2,}',
                'exclamation_density': r'[!]+',
                'question_density': r'[?]+'
            }
        }
    
    def _initialize_communication_adaptations(self):
        """Inicializa adaptaciones de comunicación por estado emocional"""
        self.communication_adaptations = {
            EmotionalState.SADNESS: {
                'tone': 'gentle_supportive',
                'pace': 'slow_patient',
                'validation_level': 'high',
                'solution_timing': 'delayed',
                'empathy_expressions': ['Te entiendo', 'Es normal sentirse así', 'No estás solo en esto'],
                'avoided_phrases': ['Anímate', 'No es para tanto', 'Piensa en positivo'],
                'preferred_approach': 'emotional_support_first'
            },
            
            EmotionalState.ANGER: {
                'tone': 'calm_steady',
                'pace': 'measured_controlled',
                'validation_level': 'medium',
                'solution_timing': 'after_deescalation',
                'empathy_expressions': ['Entiendo tu frustración', 'Es comprensible que te sientas así'],
                'avoided_phrases': ['Cálmate', 'Exageras', 'No es culpa de nadie'],
                'preferred_approach': 'acknowledge_then_redirect'
            },
            
            EmotionalState.ANXIETY: {
                'tone': 'reassuring_confident',
                'pace': 'steady_grounding',
                'validation_level': 'high',
                'solution_timing': 'structured_immediate',
                'empathy_expressions': ['Es normal sentirse preocupado', 'Vamos paso a paso'],
                'avoided_phrases': ['No te preocupes', 'Todo estará bien', 'Es fácil'],
                'preferred_approach': 'structure_and_reassure'
            },
            
            EmotionalState.EXCITEMENT: {
                'tone': 'enthusiastic_matching',
                'pace': 'energetic_positive',
                'validation_level': 'medium',
                'solution_timing': 'immediate_riding_energy',
                'empathy_expressions': ['¡Qué emocionante!', 'Me encanta tu entusiasmo'],
                'avoided_phrases': ['Tranquilízate', 'Baja el ritmo', 'Sé realista'],
                'preferred_approach': 'match_energy_then_channel'
            },
            
            EmotionalState.CONFUSION: {
                'tone': 'clear_patient',
                'pace': 'methodical_structured',
                'validation_level': 'medium',
                'solution_timing': 'immediate_clarifying',
                'empathy_expressions': ['Te ayudo a aclararlo', 'Vamos a organizarlo juntos'],
                'avoided_phrases': ['Es obvio', 'Deberías saber', 'Es simple'],
                'preferred_approach': 'clarify_step_by_step'
            },
            
            EmotionalState.FRUSTRATION: {
                'tone': 'understanding_solution_focused',
                'pace': 'efficient_helpful',
                'validation_level': 'high',
                'solution_timing': 'immediate_practical',
                'empathy_expressions': ['Qué frustrante debe ser', 'Vamos a solucionarlo'],
                'avoided_phrases': ['Ten paciencia', 'Inténtalo de nuevo', 'No es tan difícil'],
                'preferred_approach': 'validate_then_solve'
            }
        }
    
    def predict_emotional_state(self, user_input: str, context: Dict[str, Any], 
                               user_history: List[Dict] = None) -> EmotionalPrediction:
        """
        🔮 Predice el estado emocional del usuario
        """
        start_time = time.time()
        
        # FASE 1: Análisis linguístico directo
        direct_emotional_signals = self._analyze_direct_emotional_signals(user_input)
        
        # FASE 2: Análisis de patrones textuales
        textual_patterns = self._analyze_textual_emotional_patterns(user_input)
        
        # FASE 3: Análisis contextual
        contextual_analysis = self._analyze_contextual_emotional_cues(user_input, context)
        
        # FASE 4: Análisis de historial emocional
        historical_patterns = self._analyze_emotional_history(user_history) if user_history else {}
        
        # FASE 5: Detección de patrones conocidos
        pattern_matches = self._match_emotional_patterns(user_input, context)
        
        # FASE 6: Predicción de trayectoria emocional
        emotional_trajectory = self._predict_emotional_trajectory(
            direct_emotional_signals, contextual_analysis, historical_patterns
        )
        
        # FASE 7: Síntesis de predicción final
        prediction = self._synthesize_emotional_prediction(
            direct_emotional_signals,
            textual_patterns,
            contextual_analysis,
            historical_patterns,
            pattern_matches,
            emotional_trajectory
        )
        
        # FASE 8: Generar recomendaciones de comunicación
        communication_recommendations = self._generate_communication_recommendations(
            prediction, context
        )
        
        # FASE 9: Sugerir intervenciones proactivas
        intervention_suggestions = self._generate_intervention_suggestions(
            prediction, context
        )
        
        # Construir predicción final
        final_prediction = EmotionalPrediction(
            primary_emotion=prediction['primary_emotion'],
            intensity=prediction['intensity'],
            confidence=prediction['confidence'],
            secondary_emotions=prediction['secondary_emotions'],
            emotional_trajectory=emotional_trajectory,
            contextual_factors=contextual_analysis,
            communication_recommendations=communication_recommendations,
            intervention_suggestions=intervention_suggestions
        )
        
        # Actualizar métricas
        processing_time = time.time() - start_time
        self._update_prediction_metrics(final_prediction, processing_time)
        
        logger.info(f"🔮 Emotional prediction: {prediction['primary_emotion'].value} "
                   f"(intensity: {prediction['intensity']:.2f}, confidence: {prediction['confidence']:.2f})")
        
        return final_prediction
    
    def _analyze_direct_emotional_signals(self, user_input: str) -> Dict[str, Any]:
        """Analiza señales emocionales directas en el texto"""
        text_lower = user_input.lower()
        emotional_scores = {emotion: 0.0 for emotion in EmotionalState}
        
        # Buscar keywords emocionales directas
        for emotion, keywords in self.linguistic_indicators['emotion_keywords'].items():
            for keyword in keywords:
                if keyword in text_lower:
                    emotional_scores[emotion] += 1.0
        
        # Analizar intensificadores
        intensity_multiplier = 1.0
        for level, amplifiers in self.linguistic_indicators['intensity_amplifiers'].items():
            for amplifier in amplifiers:
                if amplifier in text_lower:
                    if level == 'very_high':
                        intensity_multiplier = max(intensity_multiplier, 2.0)
                    elif level == 'high':
                        intensity_multiplier = max(intensity_multiplier, 1.5)
                    elif level == 'moderate':
                        intensity_multiplier = max(intensity_multiplier, 1.2)
        
        # Aplicar multiplicador de intensidad
        for emotion in emotional_scores:
            emotional_scores[emotion] *= intensity_multiplier
        
        # Determinar emoción dominante
        if any(score > 0 for score in emotional_scores.values()):
            primary_emotion = max(emotional_scores, key=emotional_scores.get)
            intensity = min(1.0, emotional_scores[primary_emotion] * 0.3)
        else:
            primary_emotion = EmotionalState.CALM
            intensity = 0.5
        
        return {
            'primary_emotion': primary_emotion,
            'intensity': intensity,
            'all_scores': emotional_scores,
            'confidence': 0.8 if intensity > 0.5 else 0.4
        }
    
    def _analyze_textual_emotional_patterns(self, user_input: str) -> Dict[str, Any]:
        """Analiza patrones textuales que indican estado emocional"""
        patterns_detected = {}
        
        # Analizar patrones de escritura
        for pattern_name, pattern_regex in self.linguistic_indicators['writing_patterns'].items():
            matches = re.findall(pattern_regex, user_input)
            if matches:
                patterns_detected[pattern_name] = len(matches)
        
        # Calcular score emocional basado en patrones
        emotional_intensity = 0.0
        
        if patterns_detected.get('high_emotion', 0) > 0:
            emotional_intensity += 0.3
        if patterns_detected.get('caps_emotion', 0) > 0:
            emotional_intensity += 0.4
        if patterns_detected.get('repetition_emphasis', 0) > 0:
            emotional_intensity += 0.2
        if patterns_detected.get('elongated_words', 0) > 0:
            emotional_intensity += 0.2
        
        # Analizar densidad de signos de exclamación/pregunta
        exclamation_count = user_input.count('!')
        question_count = user_input.count('?')
        text_length = len(user_input.split())
        
        if text_length > 0:
            exclamation_density = exclamation_count / text_length
            question_density = question_count / text_length
            
            if exclamation_density > 0.1:
                emotional_intensity += 0.3
            if question_density > 0.15:
                emotional_intensity += 0.2  # Puede indicar confusión/ansiedad
        
        return {
            'patterns_detected': patterns_detected,
            'emotional_intensity': min(1.0, emotional_intensity),
            'exclamation_density': exclamation_density if text_length > 0 else 0,
            'question_density': question_density if text_length > 0 else 0,
            'confidence': 0.6
        }
    
    def _analyze_contextual_emotional_cues(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza pistas contextuales del estado emocional"""
        contextual_factors = {}
        text_lower = user_input.lower()
        
        # Analizar presión temporal
        time_pressure_score = 0.0
        for indicator in self.linguistic_indicators['contextual_clues']['time_pressure']:
            if indicator in text_lower:
                time_pressure_score += 0.2
        contextual_factors['time_pressure'] = min(1.0, time_pressure_score)
        
        # Analizar nivel de certeza
        uncertainty_score = 0.0
        certainty_score = 0.0
        for indicator in self.linguistic_indicators['contextual_clues']['uncertainty']:
            if indicator in text_lower:
                uncertainty_score += 0.25
        for indicator in self.linguistic_indicators['contextual_clues']['certainty']:
            if indicator in text_lower:
                certainty_score += 0.25
        
        contextual_factors['uncertainty_level'] = min(1.0, uncertainty_score)
        contextual_factors['certainty_level'] = min(1.0, certainty_score)
        
        # Analizar contexto social vs personal
        social_indicators = sum(1 for ind in self.linguistic_indicators['contextual_clues']['social_context'] 
                               if ind in text_lower)
        personal_indicators = sum(1 for ind in self.linguistic_indicators['contextual_clues']['personal_context'] 
                                 if ind in text_lower)
        
        contextual_factors['social_context'] = social_indicators > 0
        contextual_factors['personal_context'] = personal_indicators > 0
        
        # Información del contexto proporcionado
        user_emotion_hint = context.get('user_emotion', '')
        if user_emotion_hint:
            contextual_factors['explicit_emotion_hint'] = user_emotion_hint
        
        time_of_day = context.get('time_of_day', '')
        if time_of_day:
            contextual_factors['time_context'] = time_of_day
        
        return contextual_factors
    
    def _analyze_emotional_history(self, user_history: List[Dict]) -> Dict[str, Any]:
        """Analiza patrones emocionales en el historial del usuario"""
        if not user_history:
            return {}
        
        # Analizar últimas interacciones para detectar tendencias
        recent_emotions = []
        emotional_progression = []
        
        for interaction in user_history[-10:]:  # Últimas 10 interacciones
            interaction_text = interaction.get('user_input', '').lower()
            
            # Detectar emociones en interacciones pasadas
            for emotion, keywords in self.linguistic_indicators['emotion_keywords'].items():
                for keyword in keywords:
                    if keyword in interaction_text:
                        recent_emotions.append(emotion)
                        emotional_progression.append({
                            'emotion': emotion,
                            'timestamp': interaction.get('timestamp', datetime.now()),
                            'context': interaction_text[:50]
                        })
                        break
        
        # Analizar patrones
        emotional_trends = {}
        if recent_emotions:
            for emotion in set(recent_emotions):
                emotional_trends[emotion] = recent_emotions.count(emotion) / len(recent_emotions)
        
        # Detectar tendencia emocional general
        negative_emotions = [EmotionalState.SADNESS, EmotionalState.ANGER, EmotionalState.FEAR, 
                           EmotionalState.ANXIETY, EmotionalState.FRUSTRATION]
        positive_emotions = [EmotionalState.JOY, EmotionalState.EXCITEMENT, EmotionalState.CONTENTMENT, 
                           EmotionalState.GRATITUDE, EmotionalState.LOVE]
        
        negative_count = sum(1 for emotion in recent_emotions if emotion in negative_emotions)
        positive_count = sum(1 for emotion in recent_emotions if emotion in positive_emotions)
        
        if negative_count + positive_count > 0:
            emotional_valence = (positive_count - negative_count) / (positive_count + negative_count)
        else:
            emotional_valence = 0.0
        
        return {
            'recent_emotions': recent_emotions,
            'emotional_trends': emotional_trends,
            'emotional_progression': emotional_progression,
            'emotional_valence': emotional_valence,  # -1 (muy negativo) a +1 (muy positivo)
            'interaction_count': len(user_history)
        }
    
    def _match_emotional_patterns(self, user_input: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detecta coincidencias con patrones emocionales conocidos"""
        pattern_matches = []
        text_lower = user_input.lower()
        
        for pattern_id, pattern in self.emotional_patterns.items():
            match_score = 0.0
            matched_triggers = []
            matched_contexts = []
            
            # Verificar triggers keywords
            for trigger in pattern.trigger_keywords:
                if trigger in text_lower:
                    match_score += 0.3
                    matched_triggers.append(trigger)
            
            # Verificar context indicators
            for context_ind in pattern.context_indicators:
                if context_ind in text_lower:
                    match_score += 0.2
                    matched_contexts.append(context_ind)
            
            # Si hay match significativo, agregar a resultados
            if match_score > 0.2:
                pattern_matches.append({
                    'pattern_id': pattern_id,
                    'pattern': pattern,
                    'match_score': min(1.0, match_score),
                    'matched_triggers': matched_triggers,
                    'matched_contexts': matched_contexts,
                    'predicted_progression': pattern.emotional_progression,
                    'recovery_strategies': pattern.recovery_strategies
                })
        
        # Ordenar por score de match
        pattern_matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        return pattern_matches
    
    def _predict_emotional_trajectory(self, direct_signals: Dict, contextual_analysis: Dict, 
                                    historical_patterns: Dict) -> List[Tuple[EmotionalState, float, datetime]]:
        """Predice la trayectoria emocional futura"""
        trajectory = []
        current_time = datetime.now()
        
        # Punto actual
        current_emotion = direct_signals['primary_emotion']
        current_intensity = direct_signals['intensity']
        trajectory.append((current_emotion, current_intensity, current_time))
        
        # Predicción basada en contexto y patrones
        if contextual_analysis.get('time_pressure', 0) > 0.5:
            # Alta presión temporal → posible escalada de ansiedad
            future_time = current_time + timedelta(minutes=15)
            if current_emotion in [EmotionalState.ANXIETY, EmotionalState.CONFUSION]:
                trajectory.append((EmotionalState.OVERWHELM, min(1.0, current_intensity + 0.3), future_time))
            else:
                trajectory.append((EmotionalState.ANXIETY, 0.6, future_time))
        
        elif contextual_analysis.get('uncertainty_level', 0) > 0.5:
            # Alta incertidumbre → posible confusión o ansiedad
            future_time = current_time + timedelta(minutes=30)
            trajectory.append((EmotionalState.CONFUSION, 0.5, future_time))
        
        # Predicción basada en valencia emocional histórica
        if historical_patterns.get('emotional_valence', 0) < -0.3:
            # Tendencia negativa → posible persistencia o empeoramiento
            future_time = current_time + timedelta(hours=1)
            if current_emotion in [EmotionalState.SADNESS, EmotionalState.FRUSTRATION]:
                trajectory.append((current_emotion, max(0.2, current_intensity - 0.1), future_time))
        
        elif historical_patterns.get('emotional_valence', 0) > 0.3:
            # Tendencia positiva → posible mejora
            future_time = current_time + timedelta(minutes=45)
            if current_emotion in [EmotionalState.ANXIETY, EmotionalState.CONFUSION]:
                trajectory.append((EmotionalState.CALM, 0.6, future_time))
        
        return trajectory
    
    def _synthesize_emotional_prediction(self, direct_signals: Dict, textual_patterns: Dict,
                                       contextual_analysis: Dict, historical_patterns: Dict,
                                       pattern_matches: List, emotional_trajectory: List) -> Dict[str, Any]:
        """Sintetiza toda la información en una predicción emocional final"""
        
        # Comenzar con la emoción detectada directamente
        primary_emotion = direct_signals['primary_emotion']
        base_intensity = direct_signals['intensity']
        base_confidence = direct_signals['confidence']
        
        # Ajustar basado en patrones textuales
        pattern_intensity_bonus = textual_patterns['emotional_intensity'] * 0.3
        adjusted_intensity = min(1.0, base_intensity + pattern_intensity_bonus)
        
        # Ajustar confianza basado en múltiples fuentes
        confidence_factors = [
            direct_signals['confidence'],
            textual_patterns['confidence'],
            0.8 if pattern_matches else 0.4,  # Bonus si hay pattern match
            0.6 if historical_patterns else 0.3  # Bonus si hay historial
        ]
        final_confidence = sum(confidence_factors) / len(confidence_factors)
        
        # Si hay pattern match fuerte, puede override la emoción primaria
        if pattern_matches and pattern_matches[0]['match_score'] > 0.7:
            strongest_pattern = pattern_matches[0]['pattern']
            if strongest_pattern.emotional_progression:
                # Usar la primera emoción de la progresión del patrón
                primary_emotion = strongest_pattern.emotional_progression[0]
                final_confidence = min(1.0, final_confidence + 0.2)
        
        # Detectar emociones secundarias
        secondary_emotions = []
        all_scores = direct_signals['all_scores']
        sorted_emotions = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
        
        for emotion, score in sorted_emotions[1:4]:  # Top 3 después de la primaria
            if score > 0.2:
                secondary_emotions.append((emotion, score * 0.7))  # Reducir intensidad
        
        # Ajustar emoción basado en contexto histórico
        if historical_patterns.get('emotional_valence', 0) < -0.5:
            # Si hay tendencia muy negativa, intensificar emociones negativas
            negative_emotions = [EmotionalState.SADNESS, EmotionalState.ANGER, 
                               EmotionalState.ANXIETY, EmotionalState.FRUSTRATION]
            if primary_emotion in negative_emotions:
                adjusted_intensity = min(1.0, adjusted_intensity + 0.2)
        
        return {
            'primary_emotion': primary_emotion,
            'intensity': adjusted_intensity,
            'confidence': final_confidence,
            'secondary_emotions': secondary_emotions,
            'pattern_matches': pattern_matches,
            'synthesis_factors': {
                'direct_signals_weight': 0.4,
                'textual_patterns_weight': 0.2,
                'contextual_weight': 0.2,
                'historical_weight': 0.1,
                'pattern_match_weight': 0.1
            }
        }
    
    def _generate_communication_recommendations(self, prediction: Dict, context: Dict[str, Any]) -> Dict[str, Any]:
        """Genera recomendaciones específicas de comunicación"""
        primary_emotion = prediction['primary_emotion']
        intensity = prediction['intensity']
        
        # Obtener adaptación base para la emoción
        if primary_emotion in self.communication_adaptations:
            base_adaptation = self.communication_adaptations[primary_emotion].copy()
        else:
            # Adaptación neutral por defecto
            base_adaptation = {
                'tone': 'balanced_supportive',
                'pace': 'moderate',
                'validation_level': 'medium',
                'solution_timing': 'balanced',
                'empathy_expressions': ['Te entiendo', 'Puedo ayudarte'],
                'avoided_phrases': ['No es importante', 'Olvídalo'],
                'preferred_approach': 'balanced_response'
            }
        
        # Ajustar intensidad de la adaptación
        if intensity > 0.7:
            # Alta intensidad emocional
            base_adaptation['validation_level'] = 'very_high'
            if primary_emotion in [EmotionalState.SADNESS, EmotionalState.ANXIETY]:
                base_adaptation['pace'] = 'very_slow_gentle'
            elif primary_emotion == EmotionalState.ANGER:
                base_adaptation['pace'] = 'calm_measured'
        elif intensity < 0.3:
            # Baja intensidad emocional
            base_adaptation['validation_level'] = 'light'
            base_adaptation['pace'] = 'normal'
        
        # Agregar recomendaciones específicas
        specific_recommendations = {
            'opening_approach': self._get_opening_approach(primary_emotion, intensity),
            'response_structure': self._get_response_structure(primary_emotion),
            'language_adjustments': self._get_language_adjustments(primary_emotion, intensity),
            'timing_considerations': self._get_timing_considerations(primary_emotion),
            'escalation_prevention': self._get_escalation_prevention(primary_emotion)
        }
        
        base_adaptation.update(specific_recommendations)
        return base_adaptation
    
    def _generate_intervention_suggestions(self, prediction: Dict, context: Dict[str, Any]) -> List[str]:
        """Genera sugerencias de intervención proactiva"""
        primary_emotion = prediction['primary_emotion']
        intensity = prediction['intensity']
        pattern_matches = prediction.get('pattern_matches', [])
        
        interventions = []
        
        # Intervenciones basadas en emoción primaria
        if primary_emotion == EmotionalState.ANXIETY and intensity > 0.6:
            interventions.extend([
                "Ofrecer estructura y pasos claros",
                "Proporcionar elementos de control",
                "Usar técnicas de grounding",
                "Evitar información que aumente incertidumbre"
            ])
        
        elif primary_emotion == EmotionalState.FRUSTRATION and intensity > 0.5:
            interventions.extend([
                "Validar la frustración inmediatamente",
                "Ofrecer solución práctica rápida",
                "Proporcionar alternativas",
                "Mantener comunicación eficiente"
            ])
        
        elif primary_emotion == EmotionalState.SADNESS and intensity > 0.4:
            interventions.extend([
                "Ofrecer presencia empática",
                "Validar sentimientos sin minimizar",
                "Evitar soluciones inmediatas",
                "Proporcionar esperanza sutil"
            ])
        
        elif primary_emotion == EmotionalState.CONFUSION:
            interventions.extend([
                "Estructurar información claramente",
                "Usar analogías simples",
                "Verificar comprensión frecuentemente",
                "Proporcionar ejemplos concretos"
            ])
        
        elif primary_emotion == EmotionalState.EXCITEMENT and intensity > 0.7:
            interventions.extend([
                "Igualar energía positiva",
                "Canalizar entusiasmo constructivamente",
                "Proporcionar siguiente paso emocionante",
                "Mantener momentum"
            ])
        
        # Intervenciones basadas en patrones detectados
        if pattern_matches:
            strongest_pattern = pattern_matches[0]
            interventions.extend(strongest_pattern['recovery_strategies'])
        
        # Intervenciones contextuales
        if context.get('time_pressure', 0) > 0.5:
            interventions.append("Priorizar eficiencia en la respuesta")
        
        if context.get('social_context', False):
            interventions.append("Considerar dinámicas sociales en la respuesta")
        
        return list(set(interventions))  # Eliminar duplicados
    
    def _get_opening_approach(self, emotion: EmotionalState, intensity: float) -> str:
        """Determina el mejor enfoque de apertura"""
        if emotion == EmotionalState.SADNESS:
            return "gentle_acknowledgment" if intensity > 0.5 else "supportive_presence"
        elif emotion == EmotionalState.ANGER:
            return "calm_validation" if intensity > 0.6 else "understanding_acknowledgment"
        elif emotion == EmotionalState.ANXIETY:
            return "reassuring_structure" if intensity > 0.5 else "confident_guidance"
        elif emotion == EmotionalState.EXCITEMENT:
            return "enthusiastic_matching" if intensity > 0.7 else "positive_engagement"
        elif emotion == EmotionalState.CONFUSION:
            return "clear_orientation"
        else:
            return "balanced_warm"
    
    def _get_response_structure(self, emotion: EmotionalState) -> Dict[str, str]:
        """Define la estructura óptima de respuesta"""
        structures = {
            EmotionalState.ANXIETY: {
                'opening': 'reassurance',
                'body': 'structured_steps',
                'closing': 'confidence_building'
            },
            EmotionalState.FRUSTRATION: {
                'opening': 'validation',
                'body': 'solution_focused',
                'closing': 'encouragement'
            },
            EmotionalState.SADNESS: {
                'opening': 'empathy',
                'body': 'gentle_support',
                'closing': 'hope_subtle'
            },
            EmotionalState.CONFUSION: {
                'opening': 'orientation',
                'body': 'step_by_step',
                'closing': 'verification'
            },
            EmotionalState.EXCITEMENT: {
                'opening': 'enthusiasm_match',
                'body': 'momentum_building',
                'closing': 'next_step_exciting'
            }
        }
        
        return structures.get(emotion, {
            'opening': 'balanced',
            'body': 'helpful',
            'closing': 'supportive'
        })
    
    def _get_language_adjustments(self, emotion: EmotionalState, intensity: float) -> Dict[str, Any]:
        """Ajustes específicos de lenguaje"""
        if emotion == EmotionalState.ANXIETY:
            return {
                'certainty_language': 'high',
                'future_focus': 'structured',
                'complexity': 'reduced',
                'pace_indicators': ['paso a paso', 'uno por uno', 'gradualmente']
            }
        elif emotion == EmotionalState.ANGER:
            return {
                'validation_language': 'strong',
                'blame_avoidance': 'critical',
                'solution_focus': 'immediate',
                'calm_indicators': ['entiendo', 'comprendo', 'veamos']
            }
        elif emotion == EmotionalState.SADNESS:
            return {
                'empathy_language': 'high',
                'hope_injection': 'subtle',
                'warmth_indicators': ['te acompaño', 'estoy aquí', 'juntos']
            }
        else:
            return {
                'tone': 'balanced',
                'approach': 'adaptive'
            }
    
    def _get_timing_considerations(self, emotion: EmotionalState) -> Dict[str, str]:
        """Consideraciones de timing para la respuesta"""
        return {
            EmotionalState.ANGER: 'allow_deescalation_pause',
            EmotionalState.ANXIETY: 'respond_quickly_with_structure',
            EmotionalState.SADNESS: 'allow_processing_time',
            EmotionalState.EXCITEMENT: 'match_energy_immediately',
            EmotionalState.CONFUSION: 'provide_immediate_clarity'
        }.get(emotion, 'balanced_timing')
    
    def _get_escalation_prevention(self, emotion: EmotionalState) -> List[str]:
        """Estrategias para prevenir escalada emocional"""
        prevention_strategies = {
            EmotionalState.ANGER: [
                "Evitar palabras que suenen defensivas",
                "No contradecir inicialmente",
                "Usar lenguaje de validación"
            ],
            EmotionalState.ANXIETY: [
                "Evitar incertidumbre adicional",
                "No minimizar preocupaciones",
                "Proporcionar control percibido"
            ],
            EmotionalState.FRUSTRATION: [
                "Evitar explicaciones largas inicialmente",
                "No sugerir que es 'fácil'",
                "Enfocarse en solución inmediata"
            ]
        }
        
        return prevention_strategies.get(emotion, ["Mantener tono equilibrado"])
    
    def _update_prediction_metrics(self, prediction: EmotionalPrediction, processing_time: float):
        """Actualiza métricas del sistema de predicción"""
        self.prediction_metrics['total_predictions'] += 1
        
        # Actualizar métricas de procesamiento
        if not hasattr(self, 'processing_times'):
            self.processing_times = []
        self.processing_times.append(processing_time)
        
        # Mantener últimas 100 mediciones
        if len(self.processing_times) > 100:
            self.processing_times = self.processing_times[-100:]
    
    def learn_from_prediction_feedback(self, prediction_id: str, actual_emotion: EmotionalState, 
                                     user_feedback: Dict[str, Any]):
        """Aprende de feedback sobre predicciones para mejorar precisión"""
        # Implementar aprendizaje basado en feedback
        if prediction_id in getattr(self, 'prediction_history', {}):
            prediction_data = self.prediction_history[prediction_id]
            
            # Calcular precisión de la predicción
            predicted_emotion = prediction_data['primary_emotion']
            was_accurate = predicted_emotion == actual_emotion
            
            if was_accurate:
                self.prediction_metrics['accurate_predictions'] += 1
            
            # Actualizar tasa de precisión
            total = self.prediction_metrics['total_predictions']
            accurate = self.prediction_metrics['accurate_predictions']
            self.prediction_metrics['prediction_accuracy'] = accurate / total if total > 0 else 0.0
            
            # Aprender patrones específicos
            self._update_emotional_patterns_from_feedback(prediction_data, actual_emotion, user_feedback)
    
    def _update_emotional_patterns_from_feedback(self, prediction_data: Dict, 
                                               actual_emotion: EmotionalState, 
                                               feedback: Dict[str, Any]):
        """Actualiza patrones emocionales basado en feedback"""
        # Si la predicción fue incorrecta, ajustar patrones
        if prediction_data['primary_emotion'] != actual_emotion:
            user_input = prediction_data.get('user_input', '')
            
            # Crear o actualizar patrón para la emoción real
            pattern_key = f"learned_{actual_emotion.value}"
            
            if pattern_key not in self.emotional_patterns:
                # Crear nuevo patrón aprendido
                self.emotional_patterns[pattern_key] = EmotionalPattern(
                    pattern_id=pattern_key,
                    trigger_keywords=[],
                    context_indicators=[],
                    emotional_progression=[actual_emotion],
                    typical_duration=timedelta(minutes=30),
                    recovery_strategies=[],
                    success_rate=0.5
                )
            
            # Extraer keywords del input que causó la emoción real
            words = user_input.lower().split()
            meaningful_words = [w for w in words if len(w) > 3 and w not in ['the', 'and', 'that', 'with']]
            
            # Agregar palabras como triggers potenciales
            pattern = self.emotional_patterns[pattern_key]
            for word in meaningful_words[:3]:  # Top 3 palabras
                if word not in pattern.trigger_keywords:
                    pattern.trigger_keywords.append(word)
    
    def get_prediction_engine_status(self) -> Dict[str, Any]:
        """Obtiene estado completo del motor de predicción emocional"""
        avg_processing_time = (
            sum(getattr(self, 'processing_times', [])) / len(getattr(self, 'processing_times', [1]))
            if hasattr(self, 'processing_times') and self.processing_times else 0.0
        )
        
        return {
            'prediction_metrics': self.prediction_metrics,
            'emotional_patterns_count': len(self.emotional_patterns),
            'supported_emotions': [emotion.value for emotion in EmotionalState],
            'average_processing_time': avg_processing_time,
            'communication_adaptations_count': len(self.communication_adaptations),
            'linguistic_indicators_loaded': len(self.linguistic_indicators),
            'engine_status': 'operational'
        }


# ============================================================================
# 🧪 TESTING
# ============================================================================

def test_emotional_prediction_engine():
    """Test del motor de predicción emocional"""
    print("🔮 Testing Emotional Prediction Engine...")
    
    engine = EmotionalPredictionEngine()
    
    # Test 1: Predicción básica
    prediction = engine.predict_emotional_state(
        "Estoy muy frustrado!!! Este código no funciona para nada",
        {'time_pressure': 0.8},
        None
    )
    
    print(f"✅ Primary emotion: {prediction.primary_emotion.value}")
    print(f"📊 Intensity: {prediction.intensity:.2f}")
    print(f"🎯 Confidence: {prediction.confidence:.2f}")
    print(f"💡 Recommendations: {prediction.communication_recommendations.get('preferred_approach')}")
    
    # Test 2: Predicción con historial
    user_history = [
        {'user_input': 'Estoy triste hoy', 'timestamp': datetime.now() - timedelta(hours=2)},
        {'user_input': 'Me siento solo', 'timestamp': datetime.now() - timedelta(hours=1)}
    ]
    
    prediction2 = engine.predict_emotional_state(
        "No sé qué hacer...",
        {'personal_context': True},
        user_history
    )
    
    print(f"✅ Historical prediction: {prediction2.primary_emotion.value}")
    print(f"🔮 Trajectory: {len(prediction2.emotional_trajectory)} points")
    
    # Test 3: Estado del sistema
    status = engine.get_prediction_engine_status()
    print(f"📊 Engine status: {status}")
    
    print("🎉 Emotional Prediction Engine test completed!")


if __name__ == "__main__":
    test_emotional_prediction_engine()

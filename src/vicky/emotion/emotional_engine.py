import os
import time
import json
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import random
import re
from datetime import datetime, timedelta

# Configuración de logging
logger = logging.getLogger("vicky.emotion")

class EmotionType(Enum):
    """Tipos de emociones básicas."""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    NEUTRAL = "neutral"

class EmotionIntensity(Enum):
    """Intensidades emocionales."""
    VERY_LOW = 0.1
    LOW = 0.3
    MEDIUM = 0.5
    HIGH = 0.7
    VERY_HIGH = 0.9

class ExpressionStyle(Enum):
    """Estilos de expresión emocional."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    EMPATHETIC = "empathetic"
    ENTHUSIASTIC = "enthusiastic"
    CALM = "calm"
    PLAYFUL = "playful"
    SERIOUS = "serious"

# @dataclass
# class EmotionalState:
#     """Estado emocional actual del sistema."""
#     primary_emotion: EmotionType
#     intensity: float  # 0.0 - 1.0
#     secondary_emotions: Dict[EmotionType, float] = field(default_factory=dict)
#     confidence: float = 0.8
#     duration: float = 300.0  # segundos
#     timestamp: float = field(default_factory=time.time)
#     context: Dict[str, Any] = field(default_factory=dict)
#     triggers: List[str] = field(default_factory=list)

@dataclass
class EmotionalResponse:
    """Respuesta emocional generada."""
    content: str
    emotion: EmotionType
    intensity: float
    style: ExpressionStyle
    voice_modulation: Dict[str, float]
    visual_cues: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

class EmotionAnalyzer:
    """Analizador de emociones en texto y contexto."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Diccionarios de palabras emocionales en español
        self.emotion_lexicon = {
            EmotionType.JOY: {
                "words": ["feliz", "alegre", "contento", "emocionado", "eufórico", "radiante", 
                         "jubiloso", "gozoso", "dichoso", "satisfecho", "encantado", "exultante"],
                "phrases": ["me siento genial", "estoy muy feliz", "qué alegría", "fantástico",
                           "excelente", "maravilloso", "increíble", "perfecto"],
                "intensity_modifiers": {"muy": 1.3, "súper": 1.5, "extremadamente": 1.7, "un poco": 0.7}
            },
            EmotionType.SADNESS: {
                "words": ["triste", "melancólico", "deprimido", "desanimado", "abatido",
                         "doliente", "pesaroso", "afligido", "desconsolado", "lamentable"],
                "phrases": ["me siento mal", "estoy triste", "qué pena", "lamentable",
                           "terrible", "horrible", "desastroso", "deprimente"],
                "intensity_modifiers": {"muy": 1.3, "súper": 1.5, "extremadamente": 1.7, "un poco": 0.7}
            },
            EmotionType.ANGER: {
                "words": ["enojado", "furioso", "irritado", "molesto", "indignado", "iracundo",
                         "colérico", "airado", "enfurecido", "rabioso", "exasperado"],
                "phrases": ["me molesta", "estoy furioso", "qué rabia", "indignante",
                           "frustrante", "irritante", "molesto", "enfurecedor"],
                "intensity_modifiers": {"muy": 1.3, "súper": 1.5, "extremadamente": 1.7, "un poco": 0.7}
            },
            EmotionType.FEAR: {
                "words": ["miedo", "temor", "pánico", "terror", "ansiedad", "nervioso",
                         "preocupado", "asustado", "aterrorizado", "inquieto", "angustiado"],
                "phrases": ["tengo miedo", "me preocupa", "qué terror", "aterrador",
                           "preocupante", "inquietante", "angustiante", "alarmante"],
                "intensity_modifiers": {"muy": 1.3, "súper": 1.5, "extremadamente": 1.7, "un poco": 0.7}
            },
            EmotionType.SURPRISE: {
                "words": ["sorprendido", "asombrado", "impresionado", "atónito", "pasmado",
                         "estupefacto", "boquiabierto", "maravillado", "admirado"],
                "phrases": ["qué sorpresa", "no esperaba", "increíble", "asombroso",
                           "impresionante", "inesperado", "sorprendente"],
                "intensity_modifiers": {"muy": 1.3, "súper": 1.5, "extremadamente": 1.7, "un poco": 0.7}
            }
        }
        
        # Patrones contextuales
        self.contextual_patterns = {
            "urgency": ["urgente", "rápido", "inmediato", "ya", "ahora", "prisa"],
            "politeness": ["por favor", "gracias", "disculpe", "perdón", "amablemente"],
            "frustration": ["no funciona", "error", "problema", "falla", "mal", "roto"],
            "satisfaction": ["funciona", "bien", "correcto", "perfecto", "excelente", "gracias"]
        }
    
    def analyze_emotion(self, text: str, context: Dict[str, Any] = None) -> EmotionalState:
        """Analiza las emociones en un texto dado."""
        context = context or {}
        text_lower = text.lower()
        
        # Detectar emociones usando el lexicón
        emotion_scores = {}
        detected_triggers = []
        
        for emotion_type, emotion_data in self.emotion_lexicon.items():
            score = 0.0
            
            # Buscar palabras emocionales
            for word in emotion_data["words"]:
                if word in text_lower:
                    base_score = 0.3
                    
                    # Aplicar modificadores de intensidad
                    for modifier, multiplier in emotion_data["intensity_modifiers"].items():
                        if modifier in text_lower and word in text_lower:
                            base_score *= multiplier
                    
                    score += base_score
                    detected_triggers.append(f"palabra: {word}")
            
            # Buscar frases emocionales
            for phrase in emotion_data["phrases"]:
                if phrase in text_lower:
                    score += 0.4
                    detected_triggers.append(f"frase: {phrase}")
            
            emotion_scores[emotion_type] = min(1.0, score)
        
        # Analizar patrones contextuales
        contextual_modifiers = self._analyze_contextual_patterns(text_lower)
        
        # Aplicar modificadores contextuales
        for pattern, modifier in contextual_modifiers.items():
            if pattern == "urgency":
                emotion_scores[EmotionType.ANTICIPATION] = emotion_scores.get(EmotionType.ANTICIPATION, 0) + modifier
            elif pattern == "frustration":
                emotion_scores[EmotionType.ANGER] = emotion_scores.get(EmotionType.ANGER, 0) + modifier
            elif pattern == "satisfaction":
                emotion_scores[EmotionType.JOY] = emotion_scores.get(EmotionType.JOY, 0) + modifier
        
        # Determinar emoción primaria
        if emotion_scores:
            primary_emotion = max(emotion_scores.keys(), key=lambda k: emotion_scores[k])
            primary_intensity = emotion_scores[primary_emotion]
        else:
            primary_emotion = EmotionType.NEUTRAL
            primary_intensity = 0.5
        
        # Crear emociones secundarias
        secondary_emotions = {k: v for k, v in emotion_scores.items() 
                            if k != primary_emotion and v > 0.1}
        
        # Calcular confianza basada en la claridad de las señales emocionales
        confidence = min(0.95, max(0.3, primary_intensity + len(detected_triggers) * 0.1))
        
        return EmotionalState(
            primary_emotion=primary_emotion,
            intensity=primary_intensity,
            secondary_emotions=secondary_emotions,
            confidence=confidence,
            context=context,
            triggers=detected_triggers
        )
    
    def _analyze_contextual_patterns(self, text: str) -> Dict[str, float]:
        """Analiza patrones contextuales en el texto."""
        modifiers = {}
        
        for pattern_name, keywords in self.contextual_patterns.items():
            score = 0.0
            for keyword in keywords:
                if keyword in text:
                    score += 0.2
            
            if score > 0:
                modifiers[pattern_name] = min(0.5, score)
        
        return modifiers

class EmotionalResponseGenerator:
    """Generador de respuestas emocionalmente apropiadas."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.default_style = ExpressionStyle[config.get("default_style", "PROFESSIONAL")]
        
        # Plantillas de respuesta por emoción y estilo
        self.response_templates = {
            EmotionType.JOY: {
                ExpressionStyle.PROFESSIONAL: [
                    "Me alegra mucho escuchar eso. {content}",
                    "Excelente noticia. {content}",
                    "Es fantástico saber que {content}"
                ],
                ExpressionStyle.ENTHUSIASTIC: [
                    "¡Qué maravilloso! {content}",
                    "¡Increíble! {content}",
                    "¡Fantástico! Me emociona mucho que {content}"
                ],
                ExpressionStyle.CASUAL: [
                    "¡Genial! {content}",
                    "¡Qué bueno! {content}",
                    "¡Súper! {content}"
                ]
            },
            EmotionType.SADNESS: {
                ExpressionStyle.EMPATHETIC: [
                    "Lamento mucho escuchar eso. {content}",
                    "Comprendo lo difícil que debe ser. {content}",
                    "Siento mucho que estés pasando por esto. {content}"
                ],
                ExpressionStyle.PROFESSIONAL: [
                    "Entiendo la situación. {content}",
                    "Comprendo las circunstancias. {content}",
                    "Reconozco la dificultad. {content}"
                ]
            },
            EmotionType.ANGER: {
                ExpressionStyle.CALM: [
                    "Comprendo tu frustración. {content}",
                    "Entiendo que esto puede ser molesto. {content}",
                    "Veo que esto te ha causado inconvenientes. {content}"
                ],
                ExpressionStyle.EMPATHETIC: [
                    "Puedo entender por qué te sientes así. {content}",
                    "Es comprensible que te moleste. {content}",
                    "Tienes razón en sentirte frustrado. {content}"
                ]
            },
            EmotionType.FEAR: {
                ExpressionStyle.CALM: [
                    "Entiendo tu preocupación. {content}",
                    "Es natural sentir inquietud. {content}",
                    "Comprendo tus dudas. {content}"
                ],
                ExpressionStyle.EMPATHETIC: [
                    "Puedo imaginar lo preocupante que debe ser. {content}",
                    "Es comprensible que te sientas ansioso. {content}",
                    "Entiendo perfectamente tu inquietud. {content}"
                ]
            },
            EmotionType.SURPRISE: {
                ExpressionStyle.ENTHUSIASTIC: [
                    "¡Qué interesante! {content}",
                    "¡Vaya sorpresa! {content}",
                    "¡No me esperaba eso! {content}"
                ],
                ExpressionStyle.PROFESSIONAL: [
                    "Es una información muy interesante. {content}",
                    "Eso es inesperado. {content}",
                    "Es una perspectiva nueva. {content}"
                ]
            },
            EmotionType.NEUTRAL: {
                ExpressionStyle.PROFESSIONAL: [
                    "{content}",
                    "Entiendo. {content}",
                    "Comprendo. {content}"
                ]
            }
        }
        
        # Modificadores de voz por emoción
        self.voice_modulations = {
            EmotionType.JOY: {"pitch": 1.1, "speed": 1.05, "volume": 1.1, "warmth": 1.2},
            EmotionType.SADNESS: {"pitch": 0.9, "speed": 0.95, "volume": 0.9, "warmth": 1.1},
            EmotionType.ANGER: {"pitch": 1.0, "speed": 1.1, "volume": 1.2, "intensity": 1.3},
            EmotionType.FEAR: {"pitch": 1.05, "speed": 1.1, "volume": 0.95, "tremor": 0.1},
            EmotionType.SURPRISE: {"pitch": 1.15, "speed": 1.1, "volume": 1.1, "emphasis": 1.2},
            EmotionType.NEUTRAL: {"pitch": 1.0, "speed": 1.0, "volume": 1.0}
        }
    
    def generate_response(self, content: str, emotional_state: EmotionalState, 
                         style: ExpressionStyle = None) -> EmotionalResponse:
        """Genera una respuesta emocionalmente apropiada."""
        style = style or self.default_style
        emotion = emotional_state.primary_emotion
        
        # Seleccionar plantilla apropiada
        templates = self.response_templates.get(emotion, {})
        style_templates = templates.get(style)
        
        if not style_templates:
            # Fallback a estilo profesional
            style_templates = templates.get(ExpressionStyle.PROFESSIONAL, ["{content}"])
        
        # Seleccionar plantilla aleatoria
        template = random.choice(style_templates)
        
        # Generar contenido emocional
        emotional_content = template.format(content=content)
        
        # Ajustar intensidad según el estado emocional
        if emotional_state.intensity > 0.7:
            emotional_content = self._intensify_expression(emotional_content, emotion)
        elif emotional_state.intensity < 0.3:
            emotional_content = self._soften_expression(emotional_content, emotion)
        
        # Generar modulación de voz
        voice_modulation = self.voice_modulations.get(emotion, {}).copy()
        
        # Ajustar modulación según intensidad
        for param, value in voice_modulation.items():
            if param in ["pitch", "speed", "volume", "warmth", "intensity"]:
                # Escalar según intensidad
                intensity_factor = 0.5 + (emotional_state.intensity * 0.5)
                voice_modulation[param] = 1.0 + ((value - 1.0) * intensity_factor)
        
        # Generar pistas visuales (para avatares o interfaces)
        visual_cues = self._generate_visual_cues(emotion, emotional_state.intensity)
        
        return EmotionalResponse(
            content=emotional_content,
            emotion=emotion,
            intensity=emotional_state.intensity,
            style=style,
            voice_modulation=voice_modulation,
            visual_cues=visual_cues,
            metadata={
                "original_content": content,
                "template_used": template,
                "emotional_triggers": emotional_state.triggers
            }
        )
    
    def _intensify_expression(self, content: str, emotion: EmotionType) -> str:
        """Intensifica la expresión emocional."""
        intensifiers = {
            EmotionType.JOY: ["realmente", "verdaderamente", "absolutamente"],
            EmotionType.SADNESS: ["profundamente", "realmente", "muy"],
            EmotionType.ANGER: ["completamente", "totalmente", "absolutamente"],
            EmotionType.FEAR: ["muy", "realmente", "bastante"],
            EmotionType.SURPRISE: ["realmente", "verdaderamente", "absolutamente"]
        }
        
        emotion_intensifiers = intensifiers.get(emotion, ["muy"])
        intensifier = random.choice(emotion_intensifiers)
        
        # Insertar intensificador de manera natural
        if "." in content:
            parts = content.split(".", 1)
            return f"{parts[0]} {intensifier}.{parts[1] if len(parts) > 1 else ''}"
        else:
            return f"{intensifier} {content}"
    
    def _soften_expression(self, content: str, emotion: EmotionType) -> str:
        """Suaviza la expresión emocional."""
        softeners = ["un poco", "algo", "ligeramente", "en cierta medida"]
        softener = random.choice(softeners)
        
        if "." in content:
            parts = content.split(".", 1)
            return f"{parts[0]} {softener}.{parts[1] if len(parts) > 1 else ''}"
        else:
            return f"{softener} {content}"
    
    def _generate_visual_cues(self, emotion: EmotionType, intensity: float) -> Dict[str, Any]:
        """Genera pistas visuales para la emoción."""
        base_cues = {
            EmotionType.JOY: {
                "facial_expression": "smile",
                "eye_expression": "bright",
                "color_theme": "warm",
                "animation": "bounce"
            },
            EmotionType.SADNESS: {
                "facial_expression": "sad",
                "eye_expression": "downcast",
                "color_theme": "cool",
                "animation": "slow"
            },
            EmotionType.ANGER: {
                "facial_expression": "frown",
                "eye_expression": "intense",
                "color_theme": "red",
                "animation": "sharp"
            },
            EmotionType.FEAR: {
                "facial_expression": "worried",
                "eye_expression": "wide",
                "color_theme": "pale",
                "animation": "tremor"
            },
            EmotionType.SURPRISE: {
                "facial_expression": "surprised",
                "eye_expression": "wide",
                "color_theme": "bright",
                "animation": "quick"
            },
            EmotionType.NEUTRAL: {
                "facial_expression": "neutral",
                "eye_expression": "normal",
                "color_theme": "neutral",
                "animation": "steady"
            }
        }
        
        cues = base_cues.get(emotion, base_cues[EmotionType.NEUTRAL]).copy()
        cues["intensity"] = intensity
        
        return cues

class EmotionalMemory:
    """Sistema de memoria emocional para mantener coherencia."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.emotional_history = []
        self.max_history = config.get("max_emotional_history", 100)
        self.decay_factor = config.get("emotional_decay", 0.95)
        self.current_mood = EmotionalState(
            primary_emotion=EmotionType.NEUTRAL,
            intensity=0.5
        )
    
    def update_emotional_state(self, new_state: EmotionalState) -> None:
        """Actualiza el estado emocional y la memoria."""
        # Añadir a historial
        self.emotional_history.append(new_state)
        
        # Limitar tamaño del historial
        if len(self.emotional_history) > self.max_history:
            self.emotional_history = self.emotional_history[-self.max_history:]
        
        # Actualizar mood actual con influencia del historial reciente
        self._update_current_mood(new_state)
    
    def _update_current_mood(self, new_state: EmotionalState) -> None:
        """Actualiza el mood actual considerando el historial."""
        # Obtener estados recientes (últimos 10)
        recent_states = self.emotional_history[-10:]
        
        if not recent_states:
            self.current_mood = new_state
            return
        
        # Calcular influencia ponderada de estados recientes
        emotion_weights = {}
        total_weight = 0
        
        for i, state in enumerate(recent_states):
            # Peso mayor para estados más recientes
            weight = (i + 1) * self.decay_factor ** (len(recent_states) - i - 1)
            
            if state.primary_emotion not in emotion_weights:
                emotion_weights[state.primary_emotion] = 0
            
            emotion_weights[state.primary_emotion] += weight * state.intensity
            total_weight += weight
        
        # Normalizar pesos
        if total_weight > 0:
            for emotion in emotion_weights:
                emotion_weights[emotion] /= total_weight
        
        # Determinar emoción dominante
        if emotion_weights:
            dominant_emotion = max(emotion_weights.keys(), key=lambda k: emotion_weights[k])
            dominant_intensity = emotion_weights[dominant_emotion]
        else:
            dominant_emotion = EmotionType.NEUTRAL
            dominant_intensity = 0.5
        
        # Crear nuevo mood
        self.current_mood = EmotionalState(
            primary_emotion=dominant_emotion,
            intensity=dominant_intensity,
            secondary_emotions={k: v for k, v in emotion_weights.items() 
                              if k != dominant_emotion and v > 0.1}
        )
    
    def get_emotional_context(self) -> Dict[str, Any]:
        """Obtiene el contexto emocional actual."""
        recent_emotions = [state.primary_emotion.value for state in self.emotional_history[-5:]]
        
        return {
            "current_mood": {
                "emotion": self.current_mood.primary_emotion.value,
                "intensity": self.current_mood.intensity,
                "secondary_emotions": {k.value: v for k, v in self.current_mood.secondary_emotions.items()}
            },
            "recent_emotions": recent_emotions,
            "emotional_stability": self._calculate_emotional_stability(),
            "dominant_emotion_today": self._get_dominant_emotion_period(24 * 3600)  # 24 horas
        }
    
    def _calculate_emotional_stability(self) -> float:
        """Calcula la estabilidad emocional basada en variaciones recientes."""
        if len(self.emotional_history) < 5:
            return 0.8  # Valor por defecto
        
        recent_states = self.emotional_history[-10:]
        intensities = [state.intensity for state in recent_states]
        
        # Calcular varianza de intensidades
        mean_intensity = np.mean(intensities)
        variance = np.var(intensities)
        
        # Convertir varianza a estabilidad (0-1, donde 1 es muy estable)
        stability = max(0, 1 - (variance * 4))  # Escalar varianza
        
        return float(stability)
    
    def _get_dominant_emotion_period(self, seconds: float) -> str:
        """Obtiene la emoción dominante en un período de tiempo."""
        cutoff_time = time.time() - seconds
        period_states = [state for state in self.emotional_history 
                        if state.timestamp > cutoff_time]
        
        if not period_states:
            return EmotionType.NEUTRAL.value
        
        emotion_counts = {}
        for state in period_states:
            emotion = state.primary_emotion
            if emotion not in emotion_counts:
                emotion_counts[emotion] = 0
            emotion_counts[emotion] += state.intensity
        
        if emotion_counts:
            dominant = max(emotion_counts.keys(), key=lambda k: emotion_counts[k])
            return dominant.value
        
        return EmotionType.NEUTRAL.value

# class EmotionalEngine:
#     """Motor principal de expresividad emocional."""
    
#     def __init__(self, config_path: str = None):
#         # Cargar configuración
#         if config_path and os.path.exists(config_path):
#             with open(config_path, 'r') as f:
#                 self.config = json.load(f)
#         else:
#             self.config = self._get_default_config()
        
#         # Inicializar componentes
#         self.emotion_analyzer = EmotionAnalyzer(self.config.get("analyzer", {}))
#         self.response_generator = EmotionalResponseGenerator(self.config.get("generator", {}))
#         self.emotional_memory = EmotionalMemory(self.config.get("memory", {}))
        
#         # Configuración de personalidad emocional
#         self.personality_config = self.config.get("personality", {})
#         self.emotional_sensitivity = self.personality_config.get("sensitivity", 0.7)
#         self.expression_intensity = self.personality_config.get("expression_intensity", 0.8)
        
#         logger.info("Motor de expresividad emocional inicializado")
    
#     def process_emotional_input(self, text: str, context: Dict[str, Any] = None) -> EmotionalState:
#         """Procesa entrada del usuario y determina estado emocional."""
#         # Analizar emoción en el texto
#         emotional_state = self.emotion_analyzer.analyze_emotion(text, context)
        
#         # Ajustar según sensibilidad configurada
#         emotional_state.intensity *= self.emotional_sensitivity
        
#         # Actualizar memoria emocional
#         self.emotional_memory.update_emotional_state(emotional_state)
        
#         return emotional_state
    
#     def generate_emotional_response(self, content: str, user_emotional_state: EmotionalState,
#                                   style: ExpressionStyle = None) -> EmotionalResponse:
#         """Genera una respuesta emocionalmente apropiada."""
#         # Obtener contexto emocional actual
#         emotional_context = self.emotional_memory.get_emotional_context()
        
#         # Determinar estilo de respuesta apropiado
#         if style is None:
#             style = self._determine_appropriate_style(user_emotional_state, emotional_context)
        
#         # Generar respuesta
#         response = self.response_generator.generate_response(
#             content, user_emotional_state, style
#         )
        
#         # Ajustar intensidad según configuración
#         response.intensity *= self.expression_intensity
        
#         # Actualizar modulación de voz
#         response.voice_modulation = self._adjust_voice_modulation(
#             response.voice_modulation, emotional_context
#         )
        
#         return response
    
#     def _determine_appropriate_style(self, user_state: EmotionalState, 
#                                    context: Dict[str, Any]) -> ExpressionStyle:
#         """Determina el estilo de expresión más apropiado."""
#         # Mapeo de emociones del usuario a estilos de respuesta
#         emotion_style_map = {
#             EmotionType.SADNESS: ExpressionStyle.EMPATHETIC,
#             EmotionType.ANGER: ExpressionStyle.CALM,
#             EmotionType.FEAR: ExpressionStyle.CALM,
#             EmotionType.JOY: ExpressionStyle.ENTHUSIASTIC,
#             EmotionType.SURPRISE: ExpressionStyle.ENTHUSIASTIC,
#             EmotionType.NEUTRAL: ExpressionStyle.PROFESSIONAL
#         }
        
#         # Estilo base según emoción del usuario
#         base_style = emotion_style_map.get(user_state.primary_emotion, ExpressionStyle.PROFESSIONAL)
        
#         # Ajustar según estabilidad emocional
#         stability = context.get("emotional_stability", 0.8)
#         if stability < 0.5:
#             # Si hay inestabilidad emocional, usar estilo más calmado
#             if base_style == ExpressionStyle.ENTHUSIASTIC:
#                 base_style = ExpressionStyle.PROFESSIONAL
        
#         # Ajustar según intensidad
#         if user_state.intensity > 0.8:
#             # Para emociones muy intensas, usar estilos más empáticos
#             if base_style == ExpressionStyle.PROFESSIONAL:
#                 base_style = ExpressionStyle.EMPATHETIC
        
#         return base_style
    
#     def _adjust_voice_modulation(self, base_modulation: Dict[str, float], 
#                                context: Dict[str, Any]) -> Dict[str, float]:
#         """Ajusta la modulación de voz según el contexto emocional."""
#         adjusted = base_modulation.copy()
        
#         # Ajustar según estabilidad emocional
#         stability = context.get("emotional_stability", 0.8)
#         if stability < 0.6:
#             # Reducir variaciones si hay inestabilidad
#             for param in ["pitch", "speed"]:
#                 if param in adjusted:
#                     # Acercar a valores neutros
#                     adjusted[param] = 1.0 + ((adjusted[param] - 1.0) * stability)
        
#         # Ajustar según mood actual
#         current_mood = context.get("current_mood", {})
#         mood_emotion = current_mood.get("emotion", "neutral")
#         mood_intensity = current_mood.get("intensity", 0.5)
        
#         # Aplicar influencia sutil del mood
#         mood_influence = 0.2 * mood_intensity
#         if mood_emotion == "joy":
#             adjusted["warmth"] = adjusted.get("warmth", 1.0) + mood_influence
#         elif mood_emotion == "sadness":
#             adjusted["warmth"] = adjusted.get("warmth", 1.0) + mood_influence
#             adjusted["speed"] = adjusted.get("speed", 1.0) - (mood_influence * 0.5)
        
#         return adjusted
    
#     def get_emotional_status(self) -> Dict[str, Any]:
#         """Obtiene el estado emocional completo del sistema."""
#         emotional_context = self.emotional_memory.get_emotional_context()
        
#         return {
#             "current_emotional_state": emotional_context,
#             "personality_config": {
#                 "sensitivity": self.emotional_sensitivity,
#                 "expression_intensity": self.expression_intensity
#             },
#             "recent_interactions": len(self.emotional_memory.emotional_history),
#             "system_mood": emotional_context.get("current_mood", {}),
#             "emotional_trends": self._analyze_emotional_trends()
#         }
    
#     def _analyze_emotional_trends(self) -> Dict[str, Any]:
#         """Analiza tendencias emocionales recientes."""
#         if len(self.emotional_memory.emotional_history) < 10:
#             return {"trend": "insufficient_data"}
        
#         recent_states = self.emotional_memory.emotional_history[-20:]
        
#         # Analizar tendencia de intensidad
#         intensities = [state.intensity for state in recent_states]
#         intensity_trend = "stable"
        
#         if len(intensities) >= 5:
#             first_half = np.mean(intensities[:len(intensities)//2])
#             second_half = np.mean(intensities[len(intensities)//2:])
            
#             if second_half > first_half + 0.1:
#                 intensity_trend = "increasing"
#             elif second_half < first_half - 0.1:
#                 intensity_trend = "decreasing"
        
#         # Analizar diversidad emocional
#         emotions = [state.primary_emotion.value for state in recent_states]
#         unique_emotions = len(set(emotions))
#         emotional_diversity = unique_emotions / len(emotions) if emotions else 0
        
#         return {
#             "intensity_trend": intensity_trend,
#             "emotional_diversity": emotional_diversity,
#             "most_frequent_emotion": max(set(emotions), key=emotions.count) if emotions else "neutral",
#             "average_intensity": float(np.mean(intensities)) if intensities else 0.5
#         }
    
#     def _get_default_config(self) -> Dict[str, Any]:
#         """Configuración por defecto del motor emocional."""
#         return {
#             "analyzer": {
#                 "sensitivity": 0.7,
#                 "context_weight": 0.3
#             },
#             "generator": {
#                 "default_style": "PROFESSIONAL",
#                 "intensity_scaling": 0.8
#             },
#             "memory": {
#                 "max_emotional_history": 100,
#                 "emotional_decay": 0.95
#             },
#             "personality": {
#                 "sensitivity": 0.7,
#                 "expression_intensity": 0.8,
#

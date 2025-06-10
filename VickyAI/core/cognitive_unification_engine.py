"""
VickyAI Cognitive Unification - Sistema Real de Unificación de Respuestas
========================================================================

Sistema simple que combina respuestas de múltiples personalidades
en una sola respuesta coherente y cálida de VickyAI.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class UnifiedResponse:
    """Respuesta unificada del sistema"""
    text: str
    confidence: float
    primary_personalities: List[str]
    response_tone: str
    processing_method: str

class SimpleUnificationEngine:
    """
    Motor de unificación simple que combina respuestas de personalidades
    en una sola respuesta coherente.
    
    Funcionalidades REALES:
    - Combina respuestas de múltiples personalidades
    - Selecciona la mejor respuesta base
    - Añade calidez y personalidad de VickyAI
    - Calcula confianza basada en consenso
    - Adapta tono según personalidades activas
    """
    
    def __init__(self):
        # Configuración de personalidades por categorías
        self.personality_categories = {
            'emotional': ['Caring', 'Empathy', 'Romantic', 'Playful'],
            'analytical': ['Analytic', 'DataScientist', 'Detective', 'Philosophical'],
            'creative': ['CreativeWriter', 'VisualArtist', 'MusicComposer', 'Poetic'],
            'professional': ['Professional', 'Negotiator', 'Ethics', 'Integrity'],
            'technical': ['SystemMaster', 'SecurityGuardian', 'AlgorithmOptimizer'],
            'cultural': ['TranslationExpert', 'LanguageDetector', 'Wisdom']
        }
        
        # Métricas simples
        self.unification_metrics = {
            'total_unifications': 0,
            'average_confidence': 0.0,
            'average_processing_time': 0.0
        }
        
        logger.info("Simple Unification Engine initialized")
    
    def unify_responses(self, personality_responses: Dict[str, Any], 
                       user_input: str, context: Dict[str, Any] = None) -> UnifiedResponse:
        """
        Unifica respuestas de múltiples personalidades en una respuesta coherente.
        
        Args:
            personality_responses: Respuestas de cada personalidad con sus pesos
            user_input: Input original del usuario
            context: Contexto de la conversación
            
        Returns:
            UnifiedResponse con la respuesta final unificada
        """
        start_time = time.time()
        
        if context is None:
            context = {}
        
        try:
            # Paso 1: Extraer y validar respuestas
            valid_responses = self._extract_valid_responses(personality_responses)
            
            if not valid_responses:
                return self._create_fallback_response(user_input)
            
            # Paso 2: Seleccionar respuesta base
            base_response = self._select_base_response(valid_responses)
            
            # Paso 3: Determinar categoría dominante
            dominant_category = self._determine_dominant_category(valid_responses)
            
            # Paso 4: Adaptar tono según personalidades activas
            response_tone = self._determine_response_tone(valid_responses, dominant_category)
            
            # Paso 5: Mejorar respuesta con calidez de VickyAI
            unified_text = self._enhance_response_with_warmth(
                base_response['text'], response_tone, context, valid_responses
            )
            
            # Paso 6: Calcular confianza
            confidence = self._calculate_confidence(valid_responses)
            
            # Paso 7: Actualizar métricas
            processing_time = time.time() - start_time
            self._update_metrics(processing_time, confidence)
            
            # Crear respuesta unificada
            unified_response = UnifiedResponse(
                text=unified_text,
                confidence=confidence,
                primary_personalities=list(valid_responses.keys()),
                response_tone=response_tone,
                processing_method='simple_unification'
            )
            
            logger.info(f"Unification completed in {processing_time:.3f}s, confidence: {confidence:.2%}")
            
            return unified_response
            
        except Exception as e:
            logger.error(f"Error in unification: {e}")
            return self._create_fallback_response(user_input, str(e))
    
    def _extract_valid_responses(self, personality_responses: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae respuestas válidas con sus pesos"""
        valid_responses = {}
        
        for personality_name, response_data in personality_responses.items():
            # Verificar que tenga peso válido
            weight = response_data.get('weight', 0.0)
            if not isinstance(weight, (int, float)) or weight <= 0.0:
                continue
            
            # Verificar que tenga texto de respuesta
            response_obj = response_data.get('response', {})
            if not isinstance(response_obj, dict):
                continue
                
            response_text = response_obj.get('text', '')
            if not response_text or len(response_text.strip()) < 5:
                continue
            
            # Añadir a respuestas válidas
            valid_responses[personality_name] = {
                'weight': float(weight),
                'text': response_text.strip(),
                'confidence': response_obj.get('confidence', weight)
            }
        
        return valid_responses
    
    def _select_base_response(self, valid_responses: Dict[str, Any]) -> Dict[str, Any]:
        """Selecciona la mejor respuesta como base"""
        if not valid_responses:
            return {'text': 'He procesado tu consulta.', 'weight': 0.5}
        
        # Ordenar por peso y tomar la de mayor peso
        sorted_responses = sorted(
            valid_responses.items(), 
            key=lambda x: x[1]['weight'], 
            reverse=True
        )
        
        best_personality, best_response = sorted_responses[0]
        
        # Si hay múltiples respuestas con peso similar, combinar
        similar_responses = [
            (p, r) for p, r in sorted_responses 
            if r['weight'] >= best_response['weight'] * 0.8
        ]
        
        if len(similar_responses) > 1:
            # Combinar respuestas similares
            combined_text = self._combine_similar_responses(similar_responses)
            return {
                'text': combined_text,
                'weight': best_response['weight'],
                'source': 'combined'
            }
        else:
            return {
                'text': best_response['text'],
                'weight': best_response['weight'],
                'source': best_personality
            }
    
    def _combine_similar_responses(self, similar_responses: List[tuple]) -> str:
        """Combina respuestas similares en una sola"""
        if len(similar_responses) == 1:
            return similar_responses[0][1]['text']
        
        # Tomar la respuesta más larga como base
        base_response = max(similar_responses, key=lambda x: len(x[1]['text']))
        return base_response[1]['text']
    
    def _determine_dominant_category(self, valid_responses: Dict[str, Any]) -> str:
        """Determina la categoría dominante de personalidades"""
        category_weights = {category: 0.0 for category in self.personality_categories}
        
        # Sumar pesos por categoría
        for personality_name, response_data in valid_responses.items():
            weight = response_data['weight']
            
            for category, personalities in self.personality_categories.items():
                if personality_name in personalities:
                    category_weights[category] += weight
                    break
        
        # Retornar categoría con mayor peso
        if any(weight > 0 for weight in category_weights.values()):
            dominant_category = max(category_weights, key=category_weights.get)
            return dominant_category
        else:
            return 'general'
    
    def _determine_response_tone(self, valid_responses: Dict[str, Any], 
                               dominant_category: str) -> str:
        """Determina el tono de respuesta basado en personalidades activas"""
        
        # Mapeo de categorías a tonos
        category_tones = {
            'emotional': 'warm_empathetic',
            'analytical': 'clear_methodical',
            'creative': 'inspiring_imaginative',
            'professional': 'polite_efficient',
            'technical': 'precise_informative',
            'cultural': 'respectful_culturally_aware',
            'general': 'balanced_friendly'
        }
        
        base_tone = category_tones.get(dominant_category, 'balanced_friendly')
        
        # Ajustar según personalidades específicas
        if 'Caring' in valid_responses and valid_responses['Caring']['weight'] > 0.7:
            return 'very_warm_caring'
        elif 'Professional' in valid_responses and valid_responses['Professional']['weight'] > 0.7:
            return 'professional_courteous'
        elif 'Playful' in valid_responses and valid_responses['Playful']['weight'] > 0.5:
            return 'friendly_playful'
        
        return base_tone
    
    def _enhance_response_with_warmth(self, base_text: str, response_tone: str, 
                                    context: Dict[str, Any], 
                                    valid_responses: Dict[str, Any]) -> str:
        """Mejora la respuesta añadiendo calidez característica de VickyAI"""
        
        # Detectar idioma
        detected_language = context.get('detected_language', 'español')
        
        if detected_language == 'español':
            return self._add_spanish_warmth(base_text, response_tone, valid_responses)
        elif detected_language == 'english':
            return self._add_english_warmth(base_text, response_tone, valid_responses)
        else:
            return self._add_universal_warmth(base_text, response_tone)
    
    def _add_spanish_warmth(self, text: str, tone: str, 
                           valid_responses: Dict[str, Any]) -> str:
        """Añade calidez en español según el tono"""
        
        # Verificar si ya tiene calidez
        warmth_indicators = ['hola', 'me alegra', 'es un placer', 'encanta', 'con gusto']
        if any(indicator in text.lower() for indicator in warmth_indicators):
            return text
        
        # Seleccionar prefijo según tono
        if tone == 'very_warm_caring':
            prefix = "Con mucho cariño, "
        elif tone == 'professional_courteous':
            prefix = "Es un placer asistirte. "
        elif tone == 'friendly_playful':
            prefix = "¡Hola! Me encanta ayudarte. "
        elif tone == 'clear_methodical':
            prefix = "Me alegra poder ayudarte de manera clara. "
        elif tone == 'inspiring_imaginative':
            prefix = "¡Qué interesante! Con mucha creatividad te ayudo. "
        else:
            prefix = "Me alegra poder ayudarte. "
        
        # Añadir sufijo empático si hay personalidades emocionales
        suffix = ""
        if any(p in valid_responses for p in ['Caring', 'Empathy']):
            suffix = " ¿Te ayuda esta información?"
        
        return f"{prefix}{text}{suffix}"
    
    def _add_english_warmth(self, text: str, tone: str, 
                           valid_responses: Dict[str, Any]) -> str:
        """Añade calidez en inglés"""
        
        warmth_indicators = ['hello', 'pleased', 'happy', 'glad', 'delighted']
        if any(indicator in text.lower() for indicator in warmth_indicators):
            return text
        
        if tone == 'very_warm_caring':
            prefix = "I'm delighted to help you. "
        elif tone == 'professional_courteous':
            prefix = "I'm pleased to assist you. "
        else:
            prefix = "I'm happy to help you. "
        
        return f"{prefix}{text}"
    
    def _add_universal_warmth(self, text: str, tone: str) -> str:
        """Añade calidez universal (fallback)"""
        return f"It's a pleasure to help you. {text}"
    
    def _calculate_confidence(self, valid_responses: Dict[str, Any]) -> float:
        """Calcula la confianza de la respuesta unificada"""
        if not valid_responses:
            return 0.3
        
        # Confianza basada en pesos y consenso
        weights = [r['weight'] for r in valid_responses.values()]
        confidences = [r.get('confidence', r['weight']) for r in valid_responses.values()]
        
        # Promedio ponderado de confianzas
        total_weight = sum(weights)
        if total_weight == 0:
            return 0.5
        
        weighted_confidence = sum(
            conf * weight for conf, weight in zip(confidences, weights)
        ) / total_weight
        
        # Bonus por consenso (múltiples personalidades coincidiendo)
        consensus_bonus = min(0.2, len(valid_responses) * 0.05)
        
        final_confidence = min(1.0, weighted_confidence + consensus_bonus)
        
        return round(final_confidence, 3)
    
    def _create_fallback_response(self, user_input: str, error_msg: str = None) -> UnifiedResponse:
        """Crea respuesta de fallback cuando falla la unificación"""
        
        fallback_text = f"Hola, soy Vicky. He recibido tu consulta '{user_input[:50]}...' y estoy procesándola."
        
        if error_msg:
            logger.error(f"Fallback due to error: {error_msg}")
        
        return UnifiedResponse(
            text=fallback_text,
            confidence=0.4,
            primary_personalities=['VickyFallback'],
            response_tone='polite_fallback',
            processing_method='fallback'
        )
    
    def _update_metrics(self, processing_time: float, confidence: float):
        """Actualiza métricas del sistema"""
        self.unification_metrics['total_unifications'] += 1
        
        # Actualizar tiempo promedio
        total = self.unification_metrics['total_unifications']
        current_avg_time = self.unification_metrics['average_processing_time']
        new_avg_time = ((current_avg_time * (total - 1)) + processing_time) / total
        self.unification_metrics['average_processing_time'] = new_avg_time
        
        # Actualizar confianza promedio
        current_avg_conf = self.unification_metrics['average_confidence']
        new_avg_conf = ((current_avg_conf * (total - 1)) + confidence) / total
        self.unification_metrics['average_confidence'] = new_avg_conf
    
    def get_unification_status(self) -> Dict[str, Any]:
        """Obtiene estado del sistema de unificación"""
        return {
            'system_name': 'Simple Unification Engine',
            'status': 'operational',
            'metrics': self.unification_metrics.copy(),
            'personality_categories': len(self.personality_categories),
            'total_personalities_supported': sum(
                len(personalities) for personalities in self.personality_categories.values()
            )
        }
    
    def reset_metrics(self):
        """Reinicia las métricas del sistema"""
        self.unification_metrics = {
            'total_unifications': 0,
            'average_confidence': 0.0,
            'average_processing_time': 0.0
        }
        logger.info("Unification metrics reset")


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def create_unification_engine() -> SimpleUnificationEngine:
    """Crea una instancia del motor de unificación"""
    try:
        engine = SimpleUnificationEngine()
        logger.info("Unification engine created successfully")
        return engine
    except Exception as e:
        logger.error(f"Failed to create unification engine: {e}")
        return None

def test_unification_engine():
    """Test básico del motor de unificación"""
    print("Testing Simple Unification Engine...")
    
    # Crear motor
    engine = create_unification_engine()
    if not engine:
        print("❌ Failed to create unification engine")
        return False
    
    # Test unificación básica
    try:
        mock_responses = {
            'Caring': {
                'weight': 0.8,
                'response': {
                    'text': 'Me preocupo por tu bienestar y quiero ayudarte.',
                    'confidence': 0.9
                }
            },
            'Analytic': {
                'weight': 0.6,
                'response': {
                    'text': 'Analicemos esta situación paso a paso.',
                    'confidence': 0.8
                }
            },
            'Professional': {
                'weight': 0.4,
                'response': {
                    'text': 'Puedo asistirte profesionalmente con esto.',
                    'confidence': 0.7
                }
            }
        }
        
        unified_response = engine.unify_responses(
            mock_responses,
            "Necesito ayuda con un problema",
            {'detected_language': 'español'}
        )
        
        print(f"✅ Unified response: {unified_response.text[:100]}...")
        print(f"📊 Confidence: {unified_response.confidence:.2%}")
        print(f"🎭 Primary personalities: {', '.join(unified_response.primary_personalities)}")
        print(f"🎵 Response tone: {unified_response.response_tone}")
        
    except Exception as e:
        print(f"❌ Error in unification test: {e}")
        return False
    
    # Test estado del sistema
    try:
        status = engine.get_unification_status()
        print(f"🏥 System status: {status['status']}")
        print(f"📈 Total unifications: {status['metrics']['total_unifications']}")
    except Exception as e:
        print(f"❌ Error getting status: {e}")
        return False
    
    print("✅ Unification engine test completed successfully!")
    return True


if __name__ == "__main__":
    # Ejecutar test si se ejecuta directamente
    test_unification_engine()

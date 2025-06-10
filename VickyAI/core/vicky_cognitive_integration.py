"""
VickyAI Cognitive Integration - Sistema Real de Unificación de Personalidades
===========================================================================

Integra múltiples personalidades especializadas en una respuesta unificada.
Basado en las 41 personalidades funcionales existentes en el sistema.
"""

import sys
import os
import logging
import time
from typing import Dict, Any, Optional, List

# Agregar paths necesarios
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.personality_manager import PersonalityManager
import copy

logger = logging.getLogger(__name__)

class VickyCognitiveIntegration:
    """
    Sistema de integración cognitiva que unifica respuestas de múltiples personalidades
    en una sola respuesta coherente de VickyAI.
    """
    
    def __init__(self):
        # Inicializar PersonalityManager existente
        self.personality_manager = PersonalityManager()
        
        # Configuración del sistema unificado
        self.unified_personality_name = "VickyUnified"
        self.cognitive_mode_enabled = True
        
        # Métricas reales de integración
        self.integration_metrics = {
            'total_responses': 0,
            'successful_integrations': 0,
            'average_response_time': 0.0,
            'success_rate': 0.0
        }
        
        # Sistema de pesos dinámicos para personalidades
        self.personality_weights = {}
        
        logger.info("VickyAI Cognitive Integration initialized successfully")
    
    def process_message_cognitive(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Método principal que procesa mensajes del usuario y genera respuesta unificada.
        
        Args:
            user_input: Mensaje del usuario
            context: Contexto de la conversación
            
        Returns:
            Dict con respuesta unificada y metadatos
        """
        if context is None:
            context = {}
        
        start_time = time.time()
        
        try:
            # Paso 1: Procesar con PersonalityManager para obtener personalidades activas
            traditional_response = self.personality_manager.process_input(user_input, context)
            
            # Paso 2: Verificar y normalizar respuesta
            if not isinstance(traditional_response, dict):
                # Si retorna string, crear estructura dict
                if isinstance(traditional_response, str):
                    traditional_response = {
                        'base_response': {'text': traditional_response},
                        'personality_weights': {self.unified_personality_name: 1.0},
                        'active_personalities': [self.unified_personality_name],
                        'response_characteristics': {}
                    }
                else:
                    # Crear respuesta de fallback
                    traditional_response = {
                        'base_response': {'text': f"He procesado tu consulta: {user_input}"},
                        'personality_weights': {self.unified_personality_name: 1.0},
                        'active_personalities': [self.unified_personality_name],
                        'response_characteristics': {}
                    }
            
            # Paso 3: Extraer información de personalidades activas
            personality_data = self._extract_personality_data(traditional_response)
            
            # Paso 4: Generar respuesta unificada
            unified_response = self._create_unified_response(
                personality_data, user_input, context, traditional_response
            )
            
            # Paso 5: Actualizar métricas
            processing_time = time.time() - start_time
            self._update_metrics(processing_time, True)
            
            logger.info(f"Cognitive integration completed in {processing_time:.3f}s")
            
            return unified_response
        
        except Exception as e:
            logger.error(f"Error in cognitive processing: {e}")
            processing_time = time.time() - start_time
            self._update_metrics(processing_time, False)
            
            # Retornar respuesta de emergencia funcional
            return self._create_emergency_response(user_input, str(e))
    
    def _extract_personality_data(self, traditional_response: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae y organiza datos de las personalidades activas"""
        personality_weights = traditional_response.get('personality_weights', {})
        active_personalities = traditional_response.get('active_personalities', [])
        base_response = traditional_response.get('base_response', {})
        
        return {
            'weights': personality_weights,
            'active_list': active_personalities,
            'base_text': base_response.get('text', ''),
            'characteristics': traditional_response.get('response_characteristics', {})
        }
    
    def _create_unified_response(self, personality_data: Dict[str, Any], 
                               user_input: str, context: Dict[str, Any],
                               traditional_response: Dict[str, Any]) -> Dict[str, Any]:
        """Crea la respuesta unificada final"""
        
        # Obtener texto base y mejorarlo
        base_text = personality_data['base_text']
        unified_text = self._enhance_response_text(base_text, personality_data, context)
        
        # Calcular confianza basada en personalidades activas
        confidence = self._calculate_confidence(personality_data)
        
        # Determinar personalidad dominante
        dominant_personality = self._get_dominant_personality(personality_data['weights'])
        
        # Construir respuesta final
        unified_response = {
            'text': unified_text,
            'confidence': confidence,
            'primary_personality': self.unified_personality_name,
            'dominant_source': dominant_personality,
            'active_personalities': personality_data['active_list'],
            'personality_weights': personality_data['weights'],
            
            # Información del sistema cognitivo
            'cognitive_mode': True,
            'integration_method': 'personality_unification',
            'response_type': 'unified',
            
            # Metadatos para compatibilidad
            'response_characteristics': personality_data['characteristics'],
            'interaction_id': traditional_response.get('interaction_id'),
            
            # Métricas de procesamiento
            'processing_info': {
                'personalities_used': len(personality_data['active_list']),
                'integration_confidence': confidence,
                'method': 'cognitive_integration'
            }
        }
        
        return unified_response
    
    def _enhance_response_text(self, base_text: str, personality_data: Dict[str, Any], 
                             context: Dict[str, Any]) -> str:
        """Mejora el texto base añadiendo calidez y personalidad de VickyAI"""
        if not base_text:
            return "Hola, soy Vicky. He recibido tu mensaje y estoy aquí para ayudarte."
        
        # Detectar idioma del contexto
        detected_language = context.get('detected_language', 'español')
        
        # Añadir calidez según el idioma
        if detected_language == 'español':
            enhanced_text = self._add_spanish_warmth(base_text, personality_data)
        elif detected_language == 'english':
            enhanced_text = self._add_english_warmth(base_text, personality_data)
        else:
            enhanced_text = base_text
        
        return enhanced_text
    
    def _add_spanish_warmth(self, text: str, personality_data: Dict[str, Any]) -> str:
        """Añade calidez en español"""
        # Verificar si ya es cálido
        warmth_indicators = ['hola', 'me alegra', 'es un placer', 'encanta', 'ayudarte']
        if any(indicator in text.lower() for indicator in warmth_indicators):
            return text
        
        # Prefijos cálidos en español
        warm_prefixes = [
            "Me alegra poder ayudarte. ",
            "¡Hola! Con mucho gusto te ayudo. ",
            "Es un placer asistirte. "
        ]
        
        # Seleccionar prefijo basado en personalidades activas
        if 'Caring' in personality_data['active_list']:
            prefix = "Con mucho cariño te ayudo. "
        elif 'Professional' in personality_data['active_list']:
            prefix = "Es un placer asistirte profesionalmente. "
        else:
            prefix = warm_prefixes[0]  # Por defecto
        
        return f"{prefix}{text}"
    
    def _add_english_warmth(self, text: str, personality_data: Dict[str, Any]) -> str:
        """Añade calidez en inglés"""
        # Verificar si ya es cálido
        warmth_indicators = ['hello', 'pleased', 'happy', 'glad', 'help you']
        if any(indicator in text.lower() for indicator in warmth_indicators):
            return text
        
        prefix = "I'm happy to help you. "
        return f"{prefix}{text}"
    
    def _calculate_confidence(self, personality_data: Dict[str, Any]) -> float:
        """Calcula la confianza de la respuesta unificada"""
        weights = personality_data['weights']
        active_count = len(personality_data['active_list'])
        
        if not weights:
            return 0.5
        
        # Confianza base según el número de personalidades activas
        base_confidence = min(0.9, 0.4 + (active_count * 0.1))
        
        # Ajustar según peso total
        total_weight = sum(weights.values())
        weight_factor = min(1.0, total_weight)
        
        final_confidence = base_confidence * weight_factor
        
        return round(final_confidence, 3)
    
    def _get_dominant_personality(self, personality_weights: Dict[str, float]) -> str:
        """Obtiene la personalidad dominante"""
        if not personality_weights:
            return self.unified_personality_name
        
        dominant = max(personality_weights, key=personality_weights.get)
        return dominant
    
    def _create_emergency_response(self, user_input: str, error_msg: str) -> Dict[str, Any]:
        """Crea respuesta de emergencia cuando falla el procesamiento"""
        return {
            'text': f"Hola, soy Vicky. He recibido tu mensaje '{user_input[:50]}...' pero estoy experimentando dificultades técnicas. ¿Puedes intentar de nuevo?",
            'confidence': 0.3,
            'primary_personality': 'VickyEmergency',
            'active_personalities': ['VickyEmergency'],
            'personality_weights': {'VickyEmergency': 1.0},
            'cognitive_mode': False,
            'emergency_mode': True,
            'error_info': error_msg,
            'response_type': 'emergency',
            'processing_info': {
                'personalities_used': 0,
                'integration_confidence': 0.3,
                'method': 'emergency_fallback'
            }
        }
    
    def _update_metrics(self, processing_time: float, success: bool):
        """Actualiza métricas del sistema"""
        self.integration_metrics['total_responses'] += 1
        
        if success:
            self.integration_metrics['successful_integrations'] += 1
            
            # Actualizar tiempo promedio de respuesta
            total = self.integration_metrics['total_responses']
            current_avg = self.integration_metrics['average_response_time']
            new_avg = ((current_avg * (total - 1)) + processing_time) / total
            self.integration_metrics['average_response_time'] = new_avg
        
        # Actualizar tasa de éxito
        total = self.integration_metrics['total_responses']
        successful = self.integration_metrics['successful_integrations']
        self.integration_metrics['success_rate'] = successful / total if total > 0 else 0.0
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual del sistema de integración"""
        try:
            personality_status = self.personality_manager.get_personality_status()
        except Exception as e:
            logger.warning(f"Could not get personality status: {e}")
            personality_status = {}
        
        return {
            'system_name': 'VickyAI Cognitive Integration',
            'integration_active': self.cognitive_mode_enabled,
            'unified_personality': self.unified_personality_name,
            
            # Métricas reales
            'metrics': self.integration_metrics,
            
            # Estado de personalidades
            'personality_system': {
                'total_personalities': len(personality_status.get('personalities_status', {})),
                'manager_active': len(personality_status.get('manager_active_personalities', [])),
                'manager_available': personality_status.get('total_interactions_logged', 0) > 0
            },
            
            # Estado del sistema
            'system_health': self._evaluate_system_health(),
            'last_update': time.time()
        }
    
    def _evaluate_system_health(self) -> str:
        """Evalúa la salud del sistema"""
        success_rate = self.integration_metrics['success_rate']
        total_responses = self.integration_metrics['total_responses']
        
        if total_responses == 0:
            return 'no_data'
        elif success_rate >= 0.95:
            return 'excellent'
        elif success_rate >= 0.80:
            return 'good'
        elif success_rate >= 0.60:
            return 'fair'
        else:
            return 'needs_attention'
    
    def adjust_personality_weight(self, personality_name: str, adjustment: float):
        """Ajusta el peso de una personalidad específica"""
        if personality_name not in self.personality_weights:
            self.personality_weights[personality_name] = 1.0
        
        # Aplicar ajuste
        new_weight = self.personality_weights[personality_name] + adjustment
        self.personality_weights[personality_name] = max(0.1, min(2.0, new_weight))
        
        logger.info(f"Adjusted {personality_name} weight to {self.personality_weights[personality_name]:.2f}")
    
    def reset_personality_weights(self):
        """Reinicia todos los pesos de personalidades"""
        self.personality_weights.clear()
        logger.info("Personality weights reset")
    
    def get_personality_weights(self) -> Dict[str, float]:
        """Obtiene los pesos actuales de personalidades"""
        return self.personality_weights.copy()


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def create_vicky_unified_instance():
    """Crea una instancia del sistema VickyAI unificado"""
    try:
        integration = VickyCognitiveIntegration()
        logger.info("VickyAI Unified instance created successfully")
        return integration
    except Exception as e:
        logger.error(f"Failed to create VickyAI instance: {e}")
        return None

def test_vicky_integration():
    """Test básico del sistema de integración"""
    print("Testing VickyAI Cognitive Integration...")
    
    # Crear instancia
    vicky = create_vicky_unified_instance()
    if not vicky:
        print("❌ Failed to create VickyAI instance")
        return False
    
    # Test respuesta básica
    try:
        response = vicky.process_message_cognitive(
            "Hola, ¿cómo estás?",
            {'detected_language': 'español'}
        )
        print(f"✅ Basic response: {response.get('text', 'No text')[:100]}...")
        print(f"📊 Confidence: {response.get('confidence', 0):.2%}")
        print(f"🎭 Primary personality: {response.get('primary_personality', 'Unknown')}")
    except Exception as e:
        print(f"❌ Error in basic test: {e}")
        return False
    
    # Test estado del sistema
    try:
        status = vicky.get_integration_status()
        print(f"🏥 System health: {status.get('system_health', 'unknown')}")
        print(f"📈 Success rate: {status.get('metrics', {}).get('success_rate', 0):.2%}")
    except Exception as e:
        print(f"❌ Error getting status: {e}")
        return False
    
    print("✅ VickyAI Integration test completed successfully!")
    return True


if __name__ == "__main__":
    # Ejecutar test si se ejecuta directamente
    test_vicky_integration()

"""
VickyAI Adaptive Learning - Sistema Real de Aprendizaje Básico
============================================================

Sistema simple de aprendizaje que realmente funciona:
- Memoria de conversaciones
- Aprendizaje de preferencias del usuario
- Ajuste de pesos de personalidades basado en feedback
- Detección de patrones básicos
"""

import logging
import time
import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from collections import defaultdict, deque
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ConversationMemory:
    """Memoria simple de conversación"""
    user_input: str
    system_response: str
    timestamp: str
    satisfaction_score: float = 0.7
    personalities_used: List[str] = None
    
    def __post_init__(self):
        if self.personalities_used is None:
            self.personalities_used = []

@dataclass
class UserPreferences:
    """Preferencias aprendidas del usuario"""
    preferred_response_length: str = 'medium'  # short, medium, long
    preferred_formality: float = 0.5  # 0.0 = muy informal, 1.0 = muy formal
    favorite_personalities: Dict[str, float] = None
    interaction_count: int = 0
    
    def __post_init__(self):
        if self.favorite_personalities is None:
            self.favorite_personalities = {}

class SimpleAdaptiveLearning:
    """
    Sistema de aprendizaje adaptativo simple y funcional.
    
    Funcionalidades REALES implementadas:
    - Memoria de conversaciones
    - Aprendizaje de preferencias de usuario
    - Ajuste de pesos de personalidades
    - Detección de patrones básicos
    """
    
    def __init__(self, memory_file: str = "VickyAI/data/learning_memory.json"):
        self.memory_file = memory_file
        
        # Memoria de conversaciones (últimas 500)
        self.conversation_memory = deque(maxlen=500)
        
        # Preferencias por usuario
        self.user_preferences = {}
        
        # Pesos ajustados de personalidades
        self.personality_adjustments = defaultdict(float)
        
        # Métricas simples
        self.learning_metrics = {
            'total_interactions': 0,
            'users_learned': 0,
            'adjustments_made': 0,
            'last_learning_event': None
        }
        
        # Cargar memoria persistente
        self._load_memory()
        
        logger.info("Simple Adaptive Learning initialized")
    
    def process_interaction_feedback(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa feedback de una interacción para aprendizaje.
        
        Args:
            interaction_data: Datos de la interacción con feedback
            
        Returns:
            Resultado del procesamiento de aprendizaje
        """
        try:
            # Crear memoria de conversación
            memory = ConversationMemory(
                user_input=interaction_data.get('user_input', ''),
                system_response=interaction_data.get('system_response', ''),
                timestamp=datetime.now().isoformat(),
                satisfaction_score=interaction_data.get('satisfaction', 0.7),
                personalities_used=interaction_data.get('personalities_used', [])
            )
            
            # Añadir a memoria
            self.conversation_memory.append(memory)
            
            # Procesar aprendizaje
            learning_results = []
            
            # 1. Aprender preferencias de usuario
            user_id = interaction_data.get('user_id', 'anonymous')
            if user_id != 'anonymous':
                user_learning = self._learn_user_preferences(user_id, memory)
                learning_results.append(user_learning)
            
            # 2. Ajustar pesos de personalidades según satisfacción
            personality_adjustment = self._adjust_personality_weights(memory)
            learning_results.append(personality_adjustment)
            
            # 3. Detectar patrones simples
            if len(self.conversation_memory) >= 10:
                pattern_detection = self._detect_simple_patterns()
                learning_results.append(pattern_detection)
            
            # Actualizar métricas
            self._update_metrics(learning_results)
            
            # Guardar memoria
            self._save_memory()
            
            return {
                'learning_applied': len(learning_results) > 0,
                'learning_results': learning_results,
                'learning_confidence': self._calculate_learning_confidence(learning_results),
                'memory_size': len(self.conversation_memory)
            }
            
        except Exception as e:
            logger.error(f"Error in interaction feedback processing: {e}")
            return {
                'learning_applied': False,
                'error': str(e),
                'learning_confidence': 0.0
            }
    
    def _learn_user_preferences(self, user_id: str, memory: ConversationMemory) -> Dict[str, Any]:
        """Aprende preferencias específicas del usuario"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = UserPreferences()
        
        prefs = self.user_preferences[user_id]
        prefs.interaction_count += 1
        
        # Aprender longitud de respuesta preferida
        response_length = len(memory.system_response)
        if response_length < 100:
            length_preference = 'short'
        elif response_length > 300:
            length_preference = 'long'
        else:
            length_preference = 'medium'
        
        # Solo cambiar preferencia si hay satisfacción alta
        if memory.satisfaction_score > 0.8:
            prefs.preferred_response_length = length_preference
        
        # Aprender personalidades favoritas
        if memory.satisfaction_score > 0.7:
            for personality in memory.personalities_used:
                current_score = prefs.favorite_personalities.get(personality, 0.5)
                # Aumentar ligeramente el score
                new_score = min(1.0, current_score + 0.1)
                prefs.favorite_personalities[personality] = new_score
        
        return {
            'type': 'user_preferences',
            'user_id': user_id,
            'preferences_updated': True,
            'interaction_count': prefs.interaction_count,
            'confidence': min(1.0, prefs.interaction_count * 0.1)
        }
    
    def _adjust_personality_weights(self, memory: ConversationMemory) -> Dict[str, Any]:
        """Ajusta pesos de personalidades según satisfacción"""
        adjustments_made = 0
        
        for personality in memory.personalities_used:
            if memory.satisfaction_score > 0.8:
                # Aumentar peso si hay alta satisfacción
                self.personality_adjustments[personality] += 0.05
                adjustments_made += 1
            elif memory.satisfaction_score < 0.4:
                # Disminuir peso si hay baja satisfacción
                self.personality_adjustments[personality] -= 0.05
                adjustments_made += 1
            
            # Mantener pesos en rango razonable
            self.personality_adjustments[personality] = max(
                -0.5, min(0.5, self.personality_adjustments[personality])
            )
        
        return {
            'type': 'personality_weights',
            'adjustments_made': adjustments_made,
            'satisfaction_score': memory.satisfaction_score,
            'personalities_affected': memory.personalities_used
        }
    
    def _detect_simple_patterns(self) -> Dict[str, Any]:
        """Detecta patrones simples en las conversaciones recientes"""
        recent_conversations = list(self.conversation_memory)[-20:]  # Últimas 20
        
        patterns_found = []
        
        # Patrón 1: Personalidades más usadas
        personality_usage = defaultdict(int)
        for conv in recent_conversations:
            for personality in conv.personalities_used:
                personality_usage[personality] += 1
        
        if personality_usage:
            most_used = max(personality_usage, key=personality_usage.get)
            usage_frequency = personality_usage[most_used] / len(recent_conversations)
            
            if usage_frequency > 0.5:  # Usada en más del 50% de conversaciones
                patterns_found.append({
                    'pattern_type': 'frequent_personality',
                    'personality': most_used,
                    'frequency': usage_frequency,
                    'confidence': 0.8
                })
        
        # Patrón 2: Tendencia de satisfacción
        recent_satisfaction = [conv.satisfaction_score for conv in recent_conversations]
        if len(recent_satisfaction) >= 5:
            avg_satisfaction = sum(recent_satisfaction) / len(recent_satisfaction)
            if avg_satisfaction > 0.8:
                patterns_found.append({
                    'pattern_type': 'high_satisfaction_trend',
                    'average_satisfaction': avg_satisfaction,
                    'confidence': 0.7
                })
            elif avg_satisfaction < 0.4:
                patterns_found.append({
                    'pattern_type': 'low_satisfaction_trend',
                    'average_satisfaction': avg_satisfaction,
                    'confidence': 0.7
                })
        
        return {
            'type': 'pattern_detection',
            'patterns_found': len(patterns_found),
            'patterns': patterns_found,
            'analysis_window': len(recent_conversations)
        }
    
    def _calculate_learning_confidence(self, learning_results: List[Dict]) -> float:
        """Calcula confianza general del aprendizaje"""
        if not learning_results:
            return 0.0
        
        confidences = []
        for result in learning_results:
            if 'confidence' in result:
                confidences.append(result['confidence'])
            elif result.get('type') == 'user_preferences':
                confidences.append(min(1.0, result.get('interaction_count', 1) * 0.1))
            elif result.get('type') == 'personality_weights':
                confidences.append(0.6 if result.get('adjustments_made', 0) > 0 else 0.3)
            else:
                confidences.append(0.5)
        
        return sum(confidences) / len(confidences)
    
    def _update_metrics(self, learning_results: List[Dict]):
        """Actualiza métricas de aprendizaje"""
        self.learning_metrics['total_interactions'] += 1
        self.learning_metrics['last_learning_event'] = datetime.now().isoformat()
        
        # Contar usuarios únicos
        self.learning_metrics['users_learned'] = len(self.user_preferences)
        
        # Contar ajustes hechos
        adjustments_in_session = sum(
            1 for result in learning_results 
            if result.get('type') == 'personality_weights' and result.get('adjustments_made', 0) > 0
        )
        self.learning_metrics['adjustments_made'] += adjustments_in_session
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Obtiene las preferencias aprendidas de un usuario"""
        if user_id not in self.user_preferences:
            return {
                'user_id': user_id,
                'preferences_available': False,
                'message': 'No preferences learned yet'
            }
        
        prefs = self.user_preferences[user_id]
        
        return {
            'user_id': user_id,
            'preferences_available': True,
            'preferred_response_length': prefs.preferred_response_length,
            'preferred_formality': prefs.preferred_formality,
            'favorite_personalities': dict(prefs.favorite_personalities),
            'interaction_count': prefs.interaction_count,
            'confidence': min(1.0, prefs.interaction_count * 0.1)
        }
    
    def get_personality_adjustments(self) -> Dict[str, float]:
        """Obtiene los ajustes actuales de personalidades"""
        return dict(self.personality_adjustments)
    
    def get_learning_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas del sistema de aprendizaje"""
        return {
            'system_status': 'active',
            'metrics': self.learning_metrics.copy(),
            'memory_usage': {
                'conversation_memory_size': len(self.conversation_memory),
                'users_tracked': len(self.user_preferences),
                'personality_adjustments': len(self.personality_adjustments)
            },
            'learning_summary': {
                'total_interactions': self.learning_metrics['total_interactions'],
                'users_learned': self.learning_metrics['users_learned'],
                'adjustments_made': self.learning_metrics['adjustments_made']
            }
        }
    
    def apply_learned_adjustments(self, base_personality_weights: Dict[str, float]) -> Dict[str, float]:
        """Aplica ajustes aprendidos a los pesos base de personalidades"""
        adjusted_weights = base_personality_weights.copy()
        
        for personality, adjustment in self.personality_adjustments.items():
            if personality in adjusted_weights:
                # Aplicar ajuste
                new_weight = adjusted_weights[personality] + adjustment
                adjusted_weights[personality] = max(0.1, min(2.0, new_weight))
        
        return adjusted_weights
    
    def reset_learning_data(self):
        """Reinicia todos los datos de aprendizaje"""
        self.conversation_memory.clear()
        self.user_preferences.clear()
        self.personality_adjustments.clear()
        
        self.learning_metrics = {
            'total_interactions': 0,
            'users_learned': 0,
            'adjustments_made': 0,
            'last_learning_event': None
        }
        
        # Guardar estado vacío
        self._save_memory()
        
        logger.info("Learning data reset completed")
    
    def _load_memory(self):
        """Carga memoria persistente desde archivo"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Cargar preferencias de usuario
                    user_prefs_data = data.get('user_preferences', {})
                    for user_id, prefs_dict in user_prefs_data.items():
                        self.user_preferences[user_id] = UserPreferences(
                            preferred_response_length=prefs_dict.get('preferred_response_length', 'medium'),
                            preferred_formality=prefs_dict.get('preferred_formality', 0.5),
                            favorite_personalities=prefs_dict.get('favorite_personalities', {}),
                            interaction_count=prefs_dict.get('interaction_count', 0)
                        )
                    
                    # Cargar ajustes de personalidades
                    self.personality_adjustments = defaultdict(float, data.get('personality_adjustments', {}))
                    
                    # Cargar métricas
                    saved_metrics = data.get('learning_metrics', {})
                    self.learning_metrics.update(saved_metrics)
                    
                    logger.info(f"Learning memory loaded: {len(self.user_preferences)} users, {len(self.personality_adjustments)} adjustments")
        except Exception as e:
            logger.warning(f"Could not load learning memory: {e}")
    
    def _save_memory(self):
        """Guarda memoria persistente a archivo"""
        try:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            
            # Preparar datos para guardar
            data = {
                'user_preferences': {
                    user_id: {
                        'preferred_response_length': prefs.preferred_response_length,
                        'preferred_formality': prefs.preferred_formality,
                        'favorite_personalities': prefs.favorite_personalities,
                        'interaction_count': prefs.interaction_count
                    }
                    for user_id, prefs in self.user_preferences.items()
                },
                'personality_adjustments': dict(self.personality_adjustments),
                'learning_metrics': self.learning_metrics,
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.debug("Learning memory saved successfully")
        except Exception as e:
            logger.error(f"Could not save learning memory: {e}")


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def create_learning_system(memory_file: str = None) -> SimpleAdaptiveLearning:
    """Crea una instancia del sistema de aprendizaje"""
    if memory_file is None:
        memory_file = "VickyAI/data/learning_memory.json"
    
    try:
        learning_system = SimpleAdaptiveLearning(memory_file)
        logger.info("Learning system created successfully")
        return learning_system
    except Exception as e:
        logger.error(f"Failed to create learning system: {e}")
        return None

def test_learning_system():
    """Test básico del sistema de aprendizaje"""
    print("Testing Simple Adaptive Learning...")
    
    # Crear sistema
    learning = create_learning_system()
    if not learning:
        print("❌ Failed to create learning system")
        return False
    
    # Test procesamiento de feedback
    try:
        test_interaction = {
            'user_input': 'Hola, ¿cómo estás?',
            'system_response': 'Me alegra poder ayudarte. ¡Hola! Estoy muy bien, gracias por preguntar.',
            'satisfaction': 0.9,
            'personalities_used': ['Caring', 'Professional'],
            'user_id': 'test_user'
        }
        
        result = learning.process_interaction_feedback(test_interaction)
        print(f"✅ Feedback processed: {result.get('learning_applied', False)}")
        print(f"📊 Learning confidence: {result.get('learning_confidence', 0):.2%}")
        print(f"🧠 Memory size: {result.get('memory_size', 0)}")
    except Exception as e:
        print(f"❌ Error in feedback test: {e}")
        return False
    
    # Test métricas
    try:
        metrics = learning.get_learning_metrics()
        print(f"📈 Total interactions: {metrics['metrics']['total_interactions']}")
        print(f"👥 Users learned: {metrics['metrics']['users_learned']}")
    except Exception as e:
        print(f"❌ Error getting metrics: {e}")
        return False
    
    print("✅ Learning system test completed successfully!")
    return True


if __name__ == "__main__":
    # Ejecutar test si se ejecuta directamente
    test_learning_system()

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import logging
import copy
from collections import deque

logger = logging.getLogger(__name__)

# Constantes para el aprendizaje de rasgos
TRAIT_LEARNING_RATE_POSITIVE = 0.015  # Aumentado ligeramente
TRAIT_LEARNING_RATE_NEGATIVE = 0.0075 # Para feedback negativo, más conservador
TRAIT_MIN_VALUE = 0.0
TRAIT_MAX_VALUE = 1.0

# Constantes para la gestión de memoria
SHORT_TERM_MEMORY_CAPACITY = 20
LONG_TERM_MEMORY_CAPACITY = 100
LTM_IMPORTANCE_THRESHOLD_FOR_AUTO = 0.7
LTM_PRUNING_RETAIN_COUNT = 80

class PersonalityBase(ABC):
    """
    Clase base abstracta para todas las personalidades de Vicky AI.
    Define la estructura y el comportamiento comunes, incluyendo la adaptación
    de rasgos y una gestión de memoria diferenciada.
    """
    
    def __init__(self, name: str, personality_type: str, description: str):
        self.id: str = str(uuid.uuid4())
        self.name: str = name
        self.personality_type: str = personality_type
        self.description: str = description
        self.activation_level: float = 0.0
        self.last_activated: Optional[datetime] = None
        self.interaction_count: int = 0
        
        self.base_traits: Dict[str, float] = self._initialize_base_traits()
        self.current_traits: Dict[str, float] = copy.deepcopy(self.base_traits)
        self.trait_modification_history: List[Dict[str, Any]] = []

        self.learning_data: Dict[str, Any] = {}
        self.emotional_state: str = "neutral"
        self.energy_level: float = 1.0
        
        # Nueva estructura de memoria
        self.short_term_memory: deque[Dict[str, Any]] = deque(maxlen=SHORT_TERM_MEMORY_CAPACITY)
        self.long_term_memory: List[Dict[str, Any]] = []
        
        logger.debug(f"PersonalityBase '{self.name}' (ID: {self.id}) initialized. STM cap: {SHORT_TERM_MEMORY_CAPACITY}, LTM cap: {LONG_TERM_MEMORY_CAPACITY}")

    @abstractmethod
    def _get_initial_traits(self) -> Dict[str, float]:
        pass

    def _initialize_base_traits(self) -> Dict[str, float]:
        initial_traits = self._get_initial_traits()
        for trait, value in initial_traits.items():
            if not (TRAIT_MIN_VALUE <= value <= TRAIT_MAX_VALUE):
                logger.warning(
                    f"Initial trait '{trait}' for personality '{self.name}' is {value}, "
                    f"which is outside [{TRAIT_MIN_VALUE}, {TRAIT_MAX_VALUE}]. Clamping."
                )
                initial_traits[trait] = min(max(value, TRAIT_MIN_VALUE), TRAIT_MAX_VALUE)
        return initial_traits

    @abstractmethod
    def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_response_style(self) -> Dict[str, Any]:
        pass
    
    def get_personality_traits(self) -> Dict[str, float]:
        return self.current_traits

    def activate(self, intensity: float = 1.0):
        self.activation_level = min(1.0, max(0.0, intensity))
        self.last_activated = datetime.now()
        self.interaction_count += 1
        
    def deactivate(self):
        self.activation_level = 0.0
        
    def learn_from_interaction(self, 
                               feedback: Dict[str, Any], 
                               user_input: str, 
                               response_generated_by_self: Dict[str, Any],
                               specific_rating: Optional[int] = None): # Nuevo parámetro
        timestamp = datetime.now().isoformat()
        traits_before = copy.deepcopy(self.current_traits)
        
        # Determinar la dirección del aprendizaje basado en el feedback específico o general
        # specific_rating: 1 (positivo), -1 (negativo), 0 (neutro/ignorar), None (usar feedback general)
        
        learning_direction = 0 # 0: no change, 1: positive, -1: negative
        
        if specific_rating is not None:
            if specific_rating > 0:
                learning_direction = 1
            elif specific_rating < 0:
                learning_direction = -1
        elif feedback.get('is_primary_responder', False): # Fallback a feedback general si no hay específico
            learning_direction = 1
            
        if learning_direction != 0:
            logger.debug(f"Personality '{self.name}' adapting traits. Direction: {learning_direction}, Specific Rating: {specific_rating}")
            for trait_name, current_value in self.current_traits.items():
                adjustment = 0.0
                if learning_direction == 1: # Reforzar
                    adjustment = TRAIT_LEARNING_RATE_POSITIVE * (TRAIT_MAX_VALUE - current_value)
                elif learning_direction == -1: # "Castigar" o mover hacia la base/medio
                    # Mover hacia el valor base del rasgo
                    base_value = self.base_traits.get(trait_name, TRAIT_MAX_VALUE / 2) # Default a 0.5 si no está en base_traits
                    adjustment = TRAIT_LEARNING_RATE_NEGATIVE * (base_value - current_value)
                
                new_value = current_value + adjustment
                self.current_traits[trait_name] = min(max(new_value, TRAIT_MIN_VALUE), TRAIT_MAX_VALUE)
                
                if abs(self.current_traits[trait_name] - traits_before.get(trait_name, current_value)) > 1e-5:
                     logger.info(
                        f"Personality '{self.name}' adapted trait '{trait_name}': "
                        f"{traits_before.get(trait_name, current_value):.3f} -> {self.current_traits[trait_name]:.3f} "
                        f"(Direction: {learning_direction}, SpecificRating: {specific_rating})"
                    )
        
        learning_event = {
            'timestamp': timestamp, 'feedback': feedback, 'user_input': user_input,
            'response_generated_by_self': response_generated_by_self,
            'activation_level_at_interaction': self.activation_level,
            'traits_before_learning': traits_before,
            'traits_after_learning': copy.deepcopy(self.current_traits),
            'specific_rating_received': specific_rating # Guardar el rating específico
        }
        self.learning_data[timestamp] = learning_event
        self.trait_modification_history.append(learning_event)
        if len(self.trait_modification_history) > 50:
            self.trait_modification_history = self.trait_modification_history[-50:]
        
    def store_memory(self, memory_key: str, memory_data: Any, 
                     category: Optional[str] = None, 
                     memory_type: str = "auto", 
                     importance: float = 0.5):
        timestamp = datetime.now().isoformat()
        memory_entry = {
            'id': str(uuid.uuid4()), 
            'timestamp': timestamp, 'key': memory_key, 'data': memory_data,
            'category': category or 'general', 'importance': max(0.0, min(1.0, importance)),
            'memory_type_requested': memory_type, 'personality_context': self.name
        }
        assigned_to_ltm = False
        if memory_type == "long" or (memory_type == "auto" and importance >= LTM_IMPORTANCE_THRESHOLD_FOR_AUTO):
            assigned_to_ltm = True
        
        if assigned_to_ltm:
            memory_entry['memory_type_assigned'] = "long"
            self.long_term_memory.append(memory_entry)
            logger.debug(f"Personality '{self.name}' stored LTM: '{memory_key}' (Imp: {importance:.2f}). LTM size: {len(self.long_term_memory)}")
            self._prune_long_term_memory()
        else:
            memory_entry['memory_type_assigned'] = "short"
            self.short_term_memory.append(memory_entry)
            logger.debug(f"Personality '{self.name}' stored STM: '{memory_key}' (Imp: {importance:.2f}). STM size: {len(self.short_term_memory)}")

    def _prune_long_term_memory(self):
        if len(self.long_term_memory) > LONG_TERM_MEMORY_CAPACITY:
            self.long_term_memory.sort(key=lambda x: (x['importance'], x['timestamp']), reverse=True)
            self.long_term_memory = self.long_term_memory[:LTM_PRUNING_RETAIN_COUNT]
            logger.info(f"Personality '{self.name}' pruned LTM. New size: {len(self.long_term_memory)}")

    def get_short_term_memories(self) -> List[Dict[str, Any]]:
        return list(self.short_term_memory)

    def get_long_term_memories(self) -> List[Dict[str, Any]]:
        return list(self.long_term_memory)

    def find_memories(self, search_term: Optional[str] = None, category: Optional[str] = None, 
                      memory_types: Optional[List[str]] = None, min_importance: float = 0.0,
                      limit: int = 5) -> List[Dict[str, Any]]:
        if memory_types is None: memory_types = ["short", "long"]
        candidate_memories: List[Dict[str, Any]] = []
        if "short" in memory_types: candidate_memories.extend(list(self.short_term_memory))
        if "long" in memory_types: candidate_memories.extend(self.long_term_memory)
        
        filtered_memories = [mem for mem in candidate_memories if mem.get('importance', 0.0) >= min_importance]
        if category: filtered_memories = [mem for mem in filtered_memories if mem.get('category') == category]
        if search_term:
            term_lower = search_term.lower()
            final_matches = []
            for mem in filtered_memories:
                match = False
                if term_lower in mem.get('key', '').lower(): match = True
                elif isinstance(mem.get('data'), str) and term_lower in mem['data'].lower(): match = True
                if match: final_matches.append(mem)
            filtered_memories = final_matches
        
        filtered_memories.sort(key=lambda x: (x.get('importance', 0.0), x.get('timestamp', '')), reverse=True)
        return filtered_memories[:limit]

    def get_personality_state(self) -> Dict[str, Any]:
        state = {
            'id': self.id, 'name': self.name, 'type': self.personality_type,
            'description': self.description, 'activation_level': round(self.activation_level, 3),
            'last_activated': self.last_activated.isoformat() if self.last_activated else None,
            'interaction_count': self.interaction_count, 'emotional_state': self.emotional_state,
            'energy_level': round(self.energy_level, 3), 'base_traits': self.base_traits,
            'current_traits': self.current_traits,
            'short_term_memory_size': len(self.short_term_memory),
            'long_term_memory_size': len(self.long_term_memory),
            'learning_data_points': len(self.learning_data),
            'trait_modification_history_count': len(self.trait_modification_history)
        }
        return state

    def update_emotional_state(self, new_state: str, reason: Optional[str] = None):
        old_state = self.emotional_state
        self.emotional_state = new_state
        log_message = f"Personality '{self.name}' emotional state: '{old_state}' -> '{new_state}'."
        if reason: log_message += f" Reason: {reason}"
        logger.info(log_message)

    def adjust_energy_level(self, change: float, reason: Optional[str] = None):
        old_energy = self.energy_level
        self.energy_level = min(1.0, max(0.0, self.energy_level + change))
        log_message = f"Personality '{self.name}' energy: {old_energy:.2f} -> {self.energy_level:.2f} (change: {change:.2f})."
        if reason: log_message += f" Reason: {reason}"
        logger.info(log_message)

    def __repr__(self) -> str:
        return f"<PersonalityBase(name='{self.name}', type='{self.personality_type}', active={self.activation_level > 0})>"

    def set_state_from_dict(self, state_data: Dict[str, Any]):
        self.current_traits = state_data.get('current_traits', copy.deepcopy(self.base_traits))
        self.interaction_count = state_data.get('interaction_count', self.interaction_count)
        self.emotional_state = state_data.get('emotional_state', self.emotional_state)
        self.energy_level = state_data.get('energy_level', self.energy_level)
        self.learning_data = state_data.get('learning_data', {})
        self.trait_modification_history = state_data.get('trait_modification_history', [])
        
        stm_content = state_data.get('short_term_memory_content', [])
        self.short_term_memory.clear()
        for mem_entry in stm_content: self.short_term_memory.append(mem_entry)
        self.long_term_memory = state_data.get('long_term_memory_content', [])
        
        last_activated_str = state_data.get('last_activated')
        if last_activated_str:
            try: self.last_activated = datetime.fromisoformat(last_activated_str)
            except (ValueError, TypeError): self.last_activated = None
        else: self.last_activated = None
        logger.info(f"Restored state for personality '{self.name}'. STM: {len(self.short_term_memory)}, LTM: {len(self.long_term_memory)}")

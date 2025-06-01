"""
Fábrica de Componentes para VokaFlow
-----------------------------------

Este módulo proporciona una fábrica para crear e inicializar
los componentes principales del sistema VokaFlow de manera centralizada.

Autor: Equipo VokaFlow
Versión: 1.0.0
"""

import logging
import os
from typing import Dict, Any, Optional, Tuple

from .model_manager import ModelManager
from .personality_manager import PersonalityManager
from .context import Context
from .memory import Memory
from .state import State
from .dual_brain import DualBrain
from .integration_layer import IntegrationLayer
from .integration_config import IntegrationConfig

# Configurar logger
logger = logging.getLogger("vicky.factory")

class ComponentFactory:
    """
    Fábrica para crear e inicializar componentes del sistema VokaFlow.
    """
    
    def __init__(self, config_dir: str = None):
        """
        Inicializa la fábrica de componentes.
        
        Args:
            config_dir: Directorio de configuración (opcional)
        """
        self.config_dir = config_dir or os.environ.get(
            "VOKAFLOW_CONFIG_DIR", 
            "/opt/vokaflow/config"
        )
        
        # Componentes creados
        self.components = {}
        
        # Configuración de integración
        self.integration_config = IntegrationConfig(
            os.path.join(self.config_dir, "integration.yaml")
        )
        
        logger.info("Fábrica de componentes inicializada")
    
    def create_all_components(self) -> Dict[str, Any]:
        """
        Crea e inicializa todos los componentes principales del sistema.
        
        Returns:
            Diccionario con los componentes creados
        """
        try:
            # Crear componentes básicos
            model_manager = self.create_model_manager()
            personality_manager = self.create_personality_manager()
            context = self.create_context()
            memory = self.create_memory()
            state = self.create_state()
            
            # Crear componentes avanzados
            dual_brain = self.create_dual_brain(
                model_manager, personality_manager, context, memory, state
            )
            
            integration_layer = self.create_integration_layer(
                model_manager, personality_manager, context, memory, state
            )
            
            # Almacenar componentes
            self.components = {
                "model_manager": model_manager,
                "personality_manager": personality_manager,
                "context": context,
                "memory": memory,
                "state": state,
                "dual_brain": dual_brain,
                "integration_layer": integration_layer
            }
            
            logger.info("Todos los componentes creados correctamente")
            return self.components
        except Exception as e:
            logger.error(f"Error al crear componentes: {e}")
            raise
    
    def create_model_manager(self) -> ModelManager:
        """
        Crea e inicializa el gestor de modelos.
        
        Returns:
            Instancia de ModelManager
        """
        try:
            config_path = os.path.join(self.config_dir, "models.yaml")
            model_manager = ModelManager(config_path)
            
            # Precargar modelos según configuración
            model_config = self.integration_config.get_config("model_integration")
            if model_config.get("auto_load_models", True):
                for model_type in model_config.get("preload_models", []):
                    try:
                        model_manager.load_model(model_type)
                    except Exception as model_error:
                        logger.warning(f"Error al precargar modelo {model_type}: {model_error}")
            
            self.components["model_manager"] = model_manager
            logger.info("Gestor de modelos creado correctamente")
            return model_manager
        except Exception as e:
            logger.error(f"Error al crear gestor de modelos: {e}")
            raise
    
    def create_personality_manager(self) -> PersonalityManager:
        """
        Crea e inicializa el gestor de personalidad.
        
        Returns:
            Instancia de PersonalityManager
        """
        try:
            personality_manager = PersonalityManager()
            
            # Configurar personalidad según configuración
            personality_config = self.integration_config.get_config("personality_integration")
            if personality_config.get("auto_load_personality", True):
                # Establecer personalidad por defecto
                default_personality = personality_config.get("default_personality")
                if default_personality:
                    personality_manager.set_active_personality(default_personality)
                
                # Establecer estilo de conversación por defecto
                default_style = personality_config.get("default_conversation_style")
                if default_style:
                    personality_manager.set_active_conversation_style(default_style)
                
                # Establecer capacidades cognitivas por defecto
                default_abilities = personality_config.get("default_cognitive_abilities")
                if default_abilities:
                    personality_manager.set_active_cognitive_abilities(default_abilities)
            
            self.components["personality_manager"] = personality_manager
            logger.info("Gestor de personalidad creado correctamente")
            return personality_manager
        except Exception as e:
            logger.error(f"Error al crear gestor de personalidad: {e}")
            raise
    
    def create_context(self) -> Context:
        """
        Crea e inicializa el sistema de contexto.
        
        Returns:
            Instancia de Context
        """
        try:
            context = Context()
            self.components["context"] = context
            logger.info("Sistema de contexto creado correctamente")
            return context
        except Exception as e:
            logger.error(f"Error al crear sistema de contexto: {e}")
            raise
    
    def create_memory(self) -> Memory:
        """
        Crea e inicializa el sistema de memoria.
        
        Returns:
            Instancia de Memory
        """
        try:
            memory = Memory()
            self.components["memory"] = memory
            logger.info("Sistema de memoria creado correctamente")
            return memory
        except Exception as e:
            logger.error(f"Error al crear sistema de memoria: {e}")
            raise
    
    def create_state(self) -> State:
        """
        Crea e inicializa el sistema de estado.
        
        Returns:
            Instancia de State
        """
        try:
            state = State()
            self.components["state"] = state
            logger.info("Sistema de estado creado correctamente")
            return state
        except Exception as e:
            logger.error(f"Error al crear sistema de estado: {e}")
            raise
    
    def create_dual_brain(self, model_manager: ModelManager = None,
                         personality_manager: PersonalityManager = None,
                         context: Context = None, memory: Memory = None,
                         state: State = None) -> DualBrain:
        """
        Crea e inicializa el cerebro dual.
        
        Args:
            model_manager: Gestor de modelos (opcional)
            personality_manager: Gestor de personalidad (opcional)
            context: Sistema de contexto (opcional)
            memory: Sistema de memoria (opcional)
            state: Sistema de estado (opcional)
            
        Returns:
            Instancia de DualBrain
        """
        try:
            # Usar componentes existentes o crearlos
            model_manager = model_manager or self.components.get("model_manager") or self.create_model_manager()
            personality_manager = personality_manager or self.components.get("personality_manager") or self.create_personality_manager()
            context = context or self.components.get("context") or self.create_context()
            memory = memory or self.components.get("memory") or self.create_memory()
            state = state or self.components.get("state") or self.create_state()
            
            # Crear cerebro dual
            dual_brain = DualBrain(
                model_manager=model_manager,
                personality_manager=personality_manager,
                context=context,
                memory=memory,
                state=state
            )
            
            # Configurar según configuración
            dual_brain_config = self.integration_config.get_config("dual_brain")
            
            # Establecer pesos de hemisferios
            technical_weight = dual_brain_config.get("default_technical_weight", 0.5)
            emotional_weight = dual_brain_config.get("default_emotional_weight", 0.5)
            dual_brain.set_hemisphere_weights({
                "technical": technical_weight,
                "emotional": emotional_weight
            })
            
            # Establecer estrategia de combinación
            strategy = dual_brain_config.get("default_combination_strategy", "integrated")
            dual_brain.set_combination_strategy(strategy)
            
            # Cargar configuración
            dual_brain.load_configuration()
            
            self.components["dual_brain"] = dual_brain
            logger.info("Cerebro dual creado correctamente")
            return dual_brain
        except Exception as e:
            logger.error(f"Error al crear cerebro dual: {e}")
            raise
    
    def create_integration_layer(self, model_manager: ModelManager = None,
                               personality_manager: PersonalityManager = None,
                               context: Context = None, memory: Memory = None,
                               state: State = None) -> IntegrationLayer:
        """
        Crea e inicializa la capa de integración.
        
        Args:
            model_manager: Gestor de modelos (opcional)
            personality_manager: Gestor de personalidad (opcional)
            context: Sistema de contexto (opcional)
            memory: Sistema de memoria (opcional)
            state: Sistema de estado (opcional)
            
        Returns:
            Instancia de IntegrationLayer
        """
        try:
            # Usar componentes existentes o crearlos
            model_manager = model_manager or self.components.get("model_manager") or self.create_model_manager()
            personality_manager = personality_manager or self.components.get("personality_manager") or self.create_personality_manager()
            context = context or self.components.get("context") or self.create_context()
            memory = memory or self.components.get("memory") or self.create_memory()
            state = state or self.components.get("state") or self.create_state()
            
            # Crear capa de integración
            integration_layer = IntegrationLayer(
                model_manager=model_manager,
                personality_manager=personality_manager,
                context=context,
                memory=memory,
                state=state
            )
            
            # Configurar según configuración
            performance_config = self.integration_config.get_config("performance")
            error_config = self.integration_config.get_config("error_handling")
            
            integration_layer.update_configuration({
                "cache_responses": performance_config.get("cache_responses", True),
                "cache_size": performance_config.get("cache_size", 100),
                "fallback_enabled": error_config.get("fallback_enabled", True),
                "auto_load_models": self.integration_config.get_config("model_integration").get("auto_load_models", True),
                "auto_load_personality": self.integration_config.get_config("personality_integration").get("auto_load_personality", True)
            })
            
            # Inicializar componentes
            integration_layer.initialize_components()
            
            self.components["integration_layer"] = integration_layer
            logger.info("Capa de integración creada correctamente")
            return integration_layer
        except Exception as e:
            logger.error(f"Error al crear capa de integración: {e}")
            raise
    
    def get_component(self, component_name: str) -> Any:
        """
        Obtiene un componente creado.
        
        Args:
            component_name: Nombre del componente
            
        Returns:
            Instancia del componente o None si no existe
        """
        if component_name not in self.components:
            logger.warning(f"Componente no encontrado: {component_name}")
            return None
        
        return self.components[component_name]
    
    def reload_component(self, component_name: str) -> Any:
        """
        Recarga un componente.
        
        Args:
            component_name: Nombre del componente
            
        Returns:
            Instancia del componente recargado o None si no existe
        """
        try:
            if component_name == "model_manager":
                self.components[component_name] = self.create_model_manager()
            elif component_name == "personality_manager":
                self.components[component_name] = self.create_personality_manager()
            elif component_name == "context":
                self.components[component_name] = self.create_context()
            elif component_name == "memory":
                self.components[component_name] = self.create_memory()
            elif component_name == "state":
                self.components[component_name] = self.create_state()
            elif component_name == "dual_brain":
                self.components[component_name] = self.create_dual_brain()
            elif component_name == "integration_layer":
                self.components[component_name] = self.create_integration_layer()
            else:
                logger.warning(f"Componente desconocido: {component_name}")
                return None
            
            logger.info(f"Componente recargado: {component_name}")
            return self.components[component_name]
        except Exception as e:
            logger.error(f"Error al recargar componente {component_name}: {e}")
            return None

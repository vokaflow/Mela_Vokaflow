"""
Generador de Respuestas para el Motor Dual-Hemisferio de Vicky.

Este módulo implementa el sistema de generación de respuestas que combina
las salidas de los hemisferios técnico y emocional para crear respuestas
equilibradas, coherentes y adaptadas al contexto.
"""

import logging
import re
import json
import time
import random
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import traceback

# Importaciones internas
from .dual_brain import DualBrain
from .model_manager import ModelManager
from .personality_manager import PersonalityManager
from .context import Context
from .memory import Memory
from .state import State
from .hemisphere_combiner import HemisphereCombiner, CombinationStrategy
from .factuality_checker import FactualityChecker

logger = logging.getLogger("vicky.core.response_generator")


class ResponseType(Enum):
    """Tipos de respuesta soportados por el generador."""
    TEXT = "text"                # Respuesta de texto plano
    VOICE = "voice"              # Respuesta de voz sintetizada
    TEXT_WITH_VOICE = "text_voice"  # Texto con voz sintetizada
    MULTIMODAL = "multimodal"    # Respuesta con múltiples modalidades
    INTERACTIVE = "interactive"  # Respuesta con elementos interactivos


class ContentFormat(Enum):
    """Formatos de contenido para las respuestas."""
    PLAIN_TEXT = "plain_text"    # Texto sin formato
    MARKDOWN = "markdown"        # Texto con formato Markdown
    HTML = "html"                # Contenido HTML
    JSON = "json"                # Datos estructurados en JSON
    CODE = "code"                # Fragmento de código


@dataclass
class ResponseElement:
    """Elemento individual de una respuesta multimodal."""
    content: Any                 # Contenido del elemento
    element_type: str            # Tipo de elemento (texto, imagen, audio, etc.)
    format: ContentFormat = ContentFormat.PLAIN_TEXT  # Formato del contenido
    metadata: Dict[str, Any] = field(default_factory=dict)  # Metadatos adicionales


@dataclass
class ResponseMetadata:
    """Metadatos asociados a una respuesta generada."""
    generation_time: float = 0.0  # Tiempo de generación en segundos
    model_used: str = ""          # Modelo utilizado para la generación
    confidence: float = 0.0       # Confianza en la respuesta (0.0-1.0)
    source_hemisphere: str = ""   # Hemisferio fuente (technical, emotional, combined)
    token_count: int = 0          # Número de tokens generados
    context_relevance: float = 0.0  # Relevancia con el contexto (0.0-1.0)
    processing_steps: List[str] = field(default_factory=list)  # Pasos de procesamiento
    error_messages: List[str] = field(default_factory=list)    # Mensajes de error


@dataclass
class Response:
    """Respuesta completa generada por el sistema."""
    content: Union[str, List[ResponseElement]]  # Contenido principal
    response_type: ResponseType                 # Tipo de respuesta
    metadata: ResponseMetadata = field(default_factory=ResponseMetadata)  # Metadatos
    audio_data: Optional[bytes] = None          # Datos de audio (si aplica)
    additional_data: Dict[str, Any] = field(default_factory=dict)  # Datos adicionales


class ResponseGenerator:
    """
    Generador de respuestas que combina las salidas de ambos hemisferios
    para crear respuestas equilibradas y completas.
    """
    
    def __init__(
        self,
        model_manager: ModelManager,
        personality_manager: PersonalityManager,
        dual_brain: DualBrain,
        context: Context,
        memory: Memory,
        state: State,
        config: Dict[str, Any] = None
    ):
        """
        Inicializa el generador de respuestas.
        
        Args:
            model_manager: Gestor de modelos de IA
            personality_manager: Gestor de personalidad
            dual_brain: Motor Dual-Hemisferio
            context: Sistema de contexto
            memory: Sistema de memoria
            state: Sistema de estado
            config: Configuración adicional (opcional)
        """
        self.model_manager = model_manager
        self.personality_manager = personality_manager
        self.dual_brain = dual_brain
        self.context = context
        self.memory = memory
        self.state = state
        self.config = config or {}
        
        # Cargar configuraciones específicas
        self.default_response_type = ResponseType(
            self.config.get("default_response_type", "text")
        )
        self.default_content_format = ContentFormat(
            self.config.get("default_content_format", "markdown")
        )
        self.enable_voice = self.config.get("enable_voice", True)
        self.enable_multimodal = self.config.get("enable_multimodal", True)
        self.max_response_length = self.config.get("max_response_length", 2000)
        
        # Inicializar sistema de caché
        self.response_cache = {}  # Caché simple para respuestas frecuentes
        self.cache_max_size = self.config.get("cache_max_size", 100)
        self.cache_ttl = self.config.get("cache_ttl", 3600)  # 1 hora por defecto
        
        # Inicializar el combinador de hemisferios
        self.hemisphere_combiner = HemisphereCombiner(config=self.config.get("hemisphere_combiner", {}))
        
        # Inicializar el verificador de factualidad
        self.factuality_checker = FactualityChecker(
            model_manager=self.model_manager,
            config=self.config.get("factuality_checker", {})
        )
        
        # Inicializar modelos necesarios
        self.language_model = None
        self.tts_model = None
        self._load_models()
        
        logger.info("Generador de respuestas multimodal inicializado")
    
    def _load_models(self) -> None:
        """Carga los modelos necesarios para la generación de respuestas."""
        try:
            # Cargar modelo de lenguaje principal
            self.language_model = self.model_manager.get_model("language")
            if not self.language_model:
                logger.warning("No se pudo cargar el modelo de lenguaje principal")
            
            # Cargar modelo de síntesis de voz si está habilitado
            if self.enable_voice:
                self.tts_model = self.model_manager.get_model("tts")
                if not self.tts_model:
                    logger.warning("No se pudo cargar el modelo de síntesis de voz")
                    self.enable_voice = False
        except Exception as e:
            logger.error(f"Error al cargar modelos: {e}")
            logger.debug(traceback.format_exc())
    
    def generate_response(
        self,
        query: str,
        response_type: Optional[ResponseType] = None,
        context_data: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Response:
        """
        Genera una respuesta completa para una consulta del usuario.
        
        Args:
            query: Consulta o mensaje del usuario
            response_type: Tipo de respuesta deseada (opcional)
            context_data: Datos de contexto adicionales (opcional)
            user_id: ID del usuario (opcional)
            conversation_id: ID de la conversación (opcional)
            
        Returns:
            Objeto Response con la respuesta generada y metadatos
        """
        start_time = time.time()
        response_type = response_type or self.default_response_type
        context_data = context_data or {}
        processing_steps = []
        
        try:
            # Verificar caché
            cache_key = self._generate_cache_key(query, str(response_type), user_id)
            current_time = time.time()

            # Verificar si la respuesta está en caché y no ha expirado
            if cache_key in self.response_cache:
                cache_entry = self.response_cache[cache_key]
                if current_time - cache_entry["timestamp"] < self.cache_ttl:
                    logger.info(f"Respuesta recuperada de caché para: {query[:50]}...")
                    return cache_entry["response"]
            
            # Analizar sentimiento y tipo de consulta
            query_sentiment = self._analyze_sentiment(query)
            query_type = self._analyze_query_type(query)
            processing_steps.append("Análisis de sentimiento y tipo de consulta")
            
            # Preparar contexto completo
            full_context = self._prepare_context(
                query, context_data, user_id, conversation_id
            )
            # Añadir información de sentimiento al contexto
            full_context["query_sentiment"] = query_sentiment
            full_context["query_type"] = query_type
            processing_steps.append("Contexto preparado")
            
            # Generar respuesta base utilizando el Motor Dual-Hemisferio
            dual_brain_response = self._generate_dual_brain_response(query, full_context)
            processing_steps.append("Respuesta Dual-Hemisferio generada")
            
            # Adaptar respuesta según sentimiento de la consulta
            sentiment_adapted_response = self._adapt_response_to_sentiment(
                dual_brain_response, query_sentiment
            )
            processing_steps.append("Respuesta adaptada al sentimiento")
            
            # Aplicar personalidad y estilo
            personalized_response = self._apply_personality(
                sentiment_adapted_response, user_id, full_context
            )
            processing_steps.append("Personalidad aplicada")
            
            # Formatear respuesta según el tipo solicitado
            formatted_response = self._format_response(
                personalized_response, response_type, full_context
            )
            processing_steps.append("Respuesta formateada")
            
            # Generar componentes adicionales según el tipo de respuesta
            final_response = self._generate_additional_components(
                formatted_response, response_type, full_context
            )
            processing_steps.append("Componentes adicionales generados")
            
            # Actualizar metadatos
            final_response.metadata.generation_time = time.time() - start_time
            final_response.metadata.processing_steps = processing_steps
            
            # Añadir información de sentimiento a los metadatos
            final_response.additional_data["query_sentiment"] = query_sentiment
            final_response.additional_data["query_type"] = query_type
            
            # Registrar en memoria para análisis futuro
            self._log_response(final_response, query, user_id, conversation_id)
            
            # Almacenar en caché si es apropiado
            if not any(final_response.metadata.error_messages):
                self.response_cache[cache_key] = {
                    "response": final_response,
                    "timestamp": current_time
                }
                self._clean_cache_if_needed()
            
            return final_response
            
        except Exception as e:
            logger.error(f"Error en generación de respuesta: {e}")
            logger.debug(traceback.format_exc())
            
            # Crear respuesta de error
            error_response = self._create_error_response(
                str(e), response_type, start_time
            )
            error_response.metadata.processing_steps = processing_steps
            error_response.metadata.error_messages.append(str(e))
            
            return error_response
    
    def _prepare_context(
        self,
        query: str,
        context_data: Dict[str, Any],
        user_id: Optional[str],
        conversation_id: Optional[str]
    ) -> Dict[str, Any]:
        """
        Prepara el contexto completo para la generación de respuesta.
        
        Args:
            query: Consulta del usuario
            context_data: Datos de contexto adicionales
            user_id: ID del usuario
            conversation_id: ID de la conversación
            
        Returns:
            Contexto completo para la generación
        """
        # Contexto base
        full_context = {
            "query": query,
            "timestamp": time.time(),
            "user_id": user_id,
            "conversation_id": conversation_id,
            **context_data
        }
        
        # Añadir historial de conversación si está disponible
        if conversation_id and hasattr(self.memory, 'get_conversation_history'):
            history = self.memory.get_conversation_history(
                conversation_id, limit=10
            )
            full_context["conversation_history"] = history
        
        # Añadir preferencias de usuario si están disponibles
        if user_id and hasattr(self.memory, 'get_user_preferences'):
            preferences = self.memory.get_user_preferences(user_id)
            full_context["user_preferences"] = preferences
        
        # Añadir estado del sistema
        system_state = self.state.get_all()
        full_context["system_state"] = system_state
        
        # Añadir contexto global del sistema
        global_context = self.context.get_global_context()
        full_context["global_context"] = global_context
        
        return full_context
    
    def _generate_dual_brain_response(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Genera una respuesta utilizando el Motor Dual-Hemisferio.
        
        Args:
            query: Consulta del usuario
            context: Contexto completo
            
        Returns:
            Respuesta generada por el Motor Dual-Hemisferio
        """
        # Verificar si el Motor Dual-Hemisferio está disponible
        if not self.dual_brain:
            logger.warning("Motor Dual-Hemisferio no disponible, usando fallback")
            return self._generate_fallback_response(query, context)
    
        try:
            # Analizar tipo de consulta
            query_type = context.get("query_type", self._analyze_query_type(query))
            context_obj = Context()
        
            # Transferir datos del diccionario al objeto Context
            for key, value in context.items():
                context_obj.set_metadata(key, value)
        
            # Generar respuestas de ambos hemisferios
            technical_response = self.dual_brain.technical_hemisphere.process(query, context).get("response", "")
            emotional_response = self.dual_brain.emotional_hemisphere.process(query, context).get("response", "")
        
            # Determinar la estrategia de combinación basada en el tipo de consulta
            strategy = None
            if query_type == "technical":
                strategy = CombinationStrategy.WEIGHTED_AVERAGE
            elif query_type == "emotional":
                strategy = CombinationStrategy.SENTIMENT_ALIGNED
            elif query_type == "creative":
                strategy = CombinationStrategy.HYBRID_FUSION
        
            # Combinar respuestas utilizando el HemisphereCombiner
            combined_response = self.hemisphere_combiner.combine(
                technical_response=technical_response,
                emotional_response=emotional_response,
                context=context_obj,
                strategy=strategy
            )
        
            # Verificar factualidad si está habilitado
            if self.config.get("enable_factuality_check", True):
                combined_response = self.factuality_checker.verify_and_correct(
                    response=combined_response,
                    query=query,
                    context=context_obj
                )
        
            return combined_response
        except Exception as e:
            logger.error(f"Error en Motor Dual-Hemisferio: {e}")
            logger.debug(traceback.format_exc())
            return self._generate_fallback_response(query, context)
    
    def _generate_fallback_response(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Genera una respuesta de fallback cuando el Motor Dual-Hemisferio no está disponible.
        
        Args:
            query: Consulta del usuario
            context: Contexto completo
            
        Returns:
            Respuesta de fallback
        """
        # Verificar si hay un modelo de lenguaje disponible
        if not self.language_model:
            return "Lo siento, no puedo generar una respuesta en este momento."
        
        try:
            # Preparar prompt con contexto mínimo
            history = context.get("conversation_history", [])
            history_text = ""
            
            if history:
                history_text = "Historial de conversación:\n"
                for entry in history[-5:]:  # Últimas 5 entradas
                    role = entry.get("role", "unknown")
                    content = entry.get("content", "")
                    history_text += f"{role}: {content}\n"
            
            # Aplicar personalidad al prompt si está disponible
            if hasattr(self.personality_manager, 'apply_personality_to_prompt'):
                prompt = self.personality_manager.apply_personality_to_prompt(
                    f"{history_text}\nUsuario: {query}\nVicky:"
                )
            else:
                prompt = f"{history_text}\nUsuario: {query}\nVicky:"
            
            # Generar respuesta con el modelo de lenguaje
            response = self.language_model.generate(prompt)
            return response
        except Exception as e:
            logger.error(f"Error en generación de fallback: {e}")
            return "Lo siento, no puedo procesar tu consulta en este momento."
    
    def _apply_personality(
        self,
        response: str,
        user_id: Optional[str],
        context: Dict[str, Any]
    ) -> str:
        """
        Aplica personalidad y estilo a la respuesta generada.
        
        Args:
            response: Respuesta base generada
            user_id: ID del usuario
            context: Contexto completo
            
        Returns:
            Respuesta con personalidad aplicada
        """
        # Si no hay gestor de personalidad, devolver respuesta original
        if not self.personality_manager:
            return response
        
        try:
            # Obtener preferencias de personalidad del usuario
            user_preferences = context.get("user_preferences", {})
            personality_style = user_preferences.get("personality_style", "default")
            
            # Aplicar personalidad a la respuesta
            if hasattr(self.personality_manager, 'apply_personality_to_response'):
                personalized = self.personality_manager.apply_personality_to_response(
                    response, personality_style
                )
                return personalized
            
            return response
        except Exception as e:
            logger.warning(f"Error al aplicar personalidad: {e}")
            return response
    
    def _format_response(
        self,
        response: str,
        response_type: ResponseType,
        context: Dict[str, Any]
    ) -> Response:
        """
        Formatea la respuesta según el tipo solicitado.
        
        Args:
            response: Respuesta con personalidad aplicada
            response_type: Tipo de respuesta solicitada
            context: Contexto completo
            
        Returns:
            Objeto Response formateado
        """
        # Crear metadatos básicos
        metadata = ResponseMetadata(
            model_used=getattr(self.language_model, 'model_name', 'unknown'),
            confidence=0.85,  # Valor por defecto
            source_hemisphere="combined"  # Valor por defecto
        )
        
        # Formatear según tipo de respuesta
        if response_type == ResponseType.TEXT:
            # Respuesta de texto simple
            return Response(
                content=response,
                response_type=ResponseType.TEXT,
                metadata=metadata
            )
        
        elif response_type == ResponseType.VOICE:
            # Respuesta de voz (sin texto)
            audio_data = self._generate_voice(response, context)
            return Response(
                content=response,
                response_type=ResponseType.VOICE,
                metadata=metadata,
                audio_data=audio_data
            )
        
        elif response_type == ResponseType.TEXT_WITH_VOICE:
            # Respuesta de texto con voz
            audio_data = self._generate_voice(response, context)
            return Response(
                content=response,
                response_type=ResponseType.TEXT_WITH_VOICE,
                metadata=metadata,
                audio_data=audio_data
            )
        
        elif response_type == ResponseType.MULTIMODAL:
            # Respuesta multimodal
            elements = self._parse_multimodal_elements(response)
            audio_data = self._generate_voice(
                self._extract_text_for_voice(elements), context
            )
            return Response(
                content=elements,
                response_type=ResponseType.MULTIMODAL,
                metadata=metadata,
                audio_data=audio_data
            )
        
        elif response_type == ResponseType.INTERACTIVE:
            # Respuesta interactiva
            elements = self._parse_interactive_elements(response)
            return Response(
                content=elements,
                response_type=ResponseType.INTERACTIVE,
                metadata=metadata
            )
        
        else:
            # Tipo desconocido, usar texto por defecto
            logger.warning(f"Tipo de respuesta desconocido: {response_type}")
            return Response(
                content=response,
                response_type=ResponseType.TEXT,
                metadata=metadata
            )
    
    def _generate_voice(
        self,
        text: str,
        context: Dict[str, Any]
    ) -> Optional[bytes]:
        """
        Genera audio de voz a partir de texto.
        
        Args:
            text: Texto a convertir en voz
            context: Contexto completo
            
        Returns:
            Datos de audio o None si no se pudo generar
        """
        # Verificar si la síntesis de voz está habilitada
        if not self.enable_voice or not self.tts_model:
            logger.info("Síntesis de voz no disponible")
            return None
        
        try:
            # Obtener preferencias de voz del usuario
            user_preferences = context.get("user_preferences", {})
            voice_id = user_preferences.get("voice_id", "default")
            speech_rate = user_preferences.get("speech_rate", 1.0)
            
            # Preparar texto para síntesis
            # Eliminar marcadores de formato, código, etc.
            clean_text = self._clean_text_for_voice(text)
            
            # Generar audio
            audio_data = self.tts_model.synthesize(
                clean_text, voice_id=voice_id, speech_rate=speech_rate
            )
            
            return audio_data
        except Exception as e:
            logger.error(f"Error en síntesis de voz: {e}")
            logger.debug(traceback.format_exc())
            return None
    
    def _clean_text_for_voice(self, text: str) -> str:
        """
        Limpia el texto para síntesis de voz, eliminando elementos no verbalizables.
        
        Args:
            text: Texto original
            
        Returns:
            Texto limpio para síntesis de voz
        """
        # Eliminar bloques de código
        text = re.sub(r'```.*?```', ' ', text, flags=re.DOTALL)
        
        # Eliminar enlaces Markdown
        text = re.sub(r'\[([^\]]+)\]$$([^)]+$$)', r'\1', text)
        
        # Eliminar formato Markdown
        text = re.sub(r'[*_~`#]', '', text)
        
        # Eliminar caracteres especiales
        text = re.sub(r'[^\w\s.,;:!?¿¡()\-—–]', ' ', text)
        
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _parse_multimodal_elements(self, response: str) -> List[ResponseElement]:
        """
        Analiza y extrae elementos multimodales de la respuesta.
        
        Args:
            response: Respuesta completa
            
        Returns:
            Lista de elementos de respuesta
        """
        elements = []
        
        # Extraer bloques de código
        code_blocks = re.findall(r'```(\w*)\n(.*?)```', response, re.DOTALL)
        for lang, code in code_blocks:
            elements.append(ResponseElement(
                content=code,
                element_type="code",
                format=ContentFormat.CODE,
                metadata={"language": lang or "text"}
            ))
            # Reemplazar el bloque de código en la respuesta
            response = response.replace(f"```{lang}\n{code}```", "[CODE_BLOCK]")
        
        # Extraer enlaces a imágenes
        image_links = re.findall(r'!\[(.*?)\]$$(.*?)$$', response)
        for alt, url in image_links:
            elements.append(ResponseElement(
                content=url,
                element_type="image",
                format=ContentFormat.HTML,
                metadata={"alt_text": alt}
            ))
            # Reemplazar el enlace en la respuesta
            response = response.replace(f"![{alt}]({url})", "[IMAGE]")
        
        # El texto restante es contenido principal
        if response.strip():
            elements.insert(0, ResponseElement(
                content=response,
                element_type="text",
                format=ContentFormat.MARKDOWN
            ))
        
        return elements
    
    def _parse_interactive_elements(self, response: str) -> List[ResponseElement]:
        """
        Analiza y extrae elementos interactivos de la respuesta.
        
        Args:
            response: Respuesta completa
            
        Returns:
            Lista de elementos de respuesta interactivos
        """
        elements = []
        
        # Extraer elementos interactivos (formato especial)
        # Ejemplo: [BUTTON:Acción:callback_data]
        interactive_elements = re.findall(r'\[(\w+):([^:]+):([^\]]+)\]', response)
        for element_type, label, data in interactive_elements:
            elements.append(ResponseElement(
                content=label,
                element_type=element_type.lower(),
                format=ContentFormat.JSON,
                metadata={"callback_data": data}
            ))
            # Reemplazar el elemento en la respuesta
            response = response.replace(f"[{element_type}:{label}:{data}]", "")
        
        # El texto restante es contenido principal
        if response.strip():
            elements.insert(0, ResponseElement(
                content=response,
                element_type="text",
                format=ContentFormat.MARKDOWN
            ))
        
        return elements
    
    def _extract_text_for_voice(self, elements: List[ResponseElement]) -> str:
        """
        Extrae texto para síntesis de voz de elementos multimodales.
        
        Args:
            elements: Lista de elementos de respuesta
            
        Returns:
            Texto para síntesis de voz
        """
        text_parts = []
        
        for element in elements:
            if element.element_type == "text":
                text_parts.append(element.content)
            elif element.element_type == "code":
                text_parts.append("Hay un bloque de código en la respuesta.")
            elif element.element_type == "image":
                alt_text = element.metadata.get("alt_text", "")
                if alt_text:
                    text_parts.append(f"Hay una imagen que muestra: {alt_text}")
                else:
                    text_parts.append("Hay una imagen en la respuesta.")
        
        return " ".join(text_parts)
    
    def _generate_additional_components(
        self,
        response: Response,
        response_type: ResponseType,
        context: Dict[str, Any]
    ) -> Response:
        """
        Genera componentes adicionales para la respuesta.
        
        Args:
            response: Respuesta formateada
            response_type: Tipo de respuesta
            context: Contexto completo
            
        Returns:
            Respuesta con componentes adicionales
        """
        # Añadir sugerencias si están habilitadas
        if self.config.get("enable_suggestions", True):
            suggestions = self._generate_suggestions(
                response.content, context
            )
            if suggestions:
                response.additional_data["suggestions"] = suggestions
        
        # Añadir fuentes de información si están habilitadas
        if self.config.get("enable_sources", True):
            sources = self._extract_sources(response.content, context)
            if sources:
                response.additional_data["sources"] = sources
        
        # Añadir métricas de confianza detalladas
        confidence_metrics = self._calculate_confidence_metrics(response, context)
        response.metadata.confidence = confidence_metrics.get("overall", 0.85)
        response.additional_data["confidence_metrics"] = confidence_metrics
        
        return response
    
    def _generate_suggestions(
        self,
        content: Union[str, List[ResponseElement]],
        context: Dict[str, Any]
    ) -> List[str]:
        """
        Genera sugerencias de seguimiento basadas en la respuesta.
        
        Args:
            content: Contenido de la respuesta
            context: Contexto completo
            
        Returns:
            Lista de sugerencias
        """
        # Extraer texto para análisis
        text = content if isinstance(content, str) else self._extract_text_for_voice(content)
        
        # Implementación simple basada en palabras clave
        suggestions = []
        
        # Detectar temas en la respuesta
        topics = self._extract_topics(text)
        
        # Generar sugerencias basadas en temas y contexto
        for topic in topics[:3]:  # Limitar a 3 temas principales
            suggestions.append(f"¿Puedes contarme más sobre {topic}?")
        
        # Añadir sugerencias genéricas si no hay suficientes
        if len(suggestions) < 3:
            generic_suggestions = [
                "¿Puedes explicar esto con más detalle?",
                "¿Hay algún ejemplo práctico de esto?",
                "¿Cómo se relaciona esto con lo que hablamos antes?",
                "¿Cuáles son las ventajas y desventajas de esto?"
            ]
            suggestions.extend(generic_suggestions[:3 - len(suggestions)])
        
        return suggestions[:3]  # Limitar a 3 sugerencias
    
    def _extract_topics(self, text: str) -> List[str]:
        """
        Extrae temas principales del texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Lista de temas
        """
        # Implementación simple basada en frecuencia de palabras
        # En una implementación real, se usaría NLP más avanzado
        
        # Eliminar palabras comunes
        stop_words = {"el", "la", "los", "las", "un", "una", "unos", "unas", "y", "o", "pero", "porque", "como", "que", "en", "por", "para", "con", "sin", "a", "ante", "bajo", "cabe", "de", "desde", "durante", "entre", "hacia", "hasta", "mediante", "para", "por", "según", "sin", "so", "sobre", "tras", "versus", "vía"}
        
        # Tokenizar y contar frecuencias
        words = re.findall(r'\b\w{4,}\b', text.lower())
        word_counts = {}
        
        for word in words:
            if word not in stop_words:
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Ordenar por frecuencia
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Devolver las palabras más frecuentes
        return [word for word, _ in sorted_words[:5]]
    
    def _extract_sources(
        self,
        content: Union[str, List[ResponseElement]],
        context: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Extrae fuentes de información mencionadas en la respuesta.
        
        Args:
            content: Contenido de la respuesta
            context: Contexto completo
            
        Returns:
            Lista de fuentes
        """
        # Extraer texto para análisis
        text = content if isinstance(content, str) else self._extract_text_for_voice(content)
        
        # Buscar patrones de citas y referencias
        sources = []
        
        # Buscar enlaces
        links = re.findall(r'\[([^\]]+)\]$$([^)]+)$$', text)
        for title, url in links:
            sources.append({
                "title": title,
                "url": url,
                "type": "link"
            })
        
        # Buscar citas formales
        citations = re.findall(r'$$([^,]+), (\d{4})$$', text)
        for author, year in citations:
            sources.append({
                "author": author,
                "year": year,
                "type": "citation"
            })
        
        return sources
    
    def _calculate_confidence_metrics(
        self,
        response: Response,
        context: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Calcula métricas detalladas de confianza para la respuesta.
        
        Args:
            response: Respuesta generada
            context: Contexto completo
            
        Returns:
            Diccionario con métricas de confianza
        """
        metrics = {
            "overall": 0.85,  # Valor por defecto
            "factual": 0.80,
            "relevance": 0.90,
            "coherence": 0.85,
            "completeness": 0.80
        }
    
        # Incluir puntuación de factualidad si está disponible
        if hasattr(self, 'factuality_checker') and hasattr(response, 'additional_data'):
            factuality_score = response.additional_data.get("factuality_score")
            if factuality_score is not None:
                metrics["factual"] = factuality_score
        
        # Ajustar según tipo de respuesta
        if response.response_type == ResponseType.MULTIMODAL:
            metrics["multimodal_integration"] = 0.75
        
        # Ajustar según fuente (hemisferio)
        if response.metadata.source_hemisphere == "technical":
            metrics["factual"] += 0.10
            metrics["completeness"] += 0.05
        elif response.metadata.source_hemisphere == "emotional":
            metrics["relevance"] += 0.05
            metrics["coherence"] += 0.10
        
        # Calcular promedio para confianza general
        metrics["overall"] = sum(v for k, v in metrics.items() if k != "overall") / (len(metrics) - 1)
        
        # Limitar valores al rango 0.0-1.0
        for key in metrics:
            metrics[key] = max(0.0, min(1.0, metrics[key]))
        
        return metrics
    
    def _create_error_response(
        self,
        error_message: str,
        response_type: ResponseType,
        start_time: float
    ) -> Response:
        """
        Crea una respuesta de error cuando falla la generación.
        
        Args:
            error_message: Mensaje de error
            response_type: Tipo de respuesta solicitada
            start_time: Tiempo de inicio de la generación
            
        Returns:
            Respuesta de error
        """
        # Crear mensaje de error amigable
        friendly_message = (
            "Lo siento, ha ocurrido un problema al procesar tu solicitud. "
            "Por favor, intenta de nuevo o contacta con soporte si el problema persiste."
        )
        
        # Crear metadatos
        metadata = ResponseMetadata(
            generation_time=time.time() - start_time,
            confidence=0.0,
            error_messages=[error_message]
        )
        
        # Crear respuesta según tipo solicitado
        if response_type in [ResponseType.VOICE, ResponseType.TEXT_WITH_VOICE]:
            # Intentar generar audio para el mensaje de error
            audio_data = None
            if self.enable_voice and self.tts_model:
                try:
                    audio_data = self.tts_model.synthesize(friendly_message)
                except Exception:
                    pass
            
            return Response(
                content=friendly_message,
                response_type=ResponseType.TEXT_WITH_VOICE if audio_data else ResponseType.TEXT,
                metadata=metadata,
                audio_data=audio_data
            )
        else:
            # Respuesta de texto simple
            return Response(
                content=friendly_message,
                response_type=ResponseType.TEXT,
                metadata=metadata
            )
    
    def _log_response(
        self,
        response: Response,
        query: str,
        user_id: Optional[str],
        conversation_id: Optional[str]
    ) -> None:
        """
        Registra la respuesta generada para análisis futuro.
        
        Args:
            response: Respuesta generada
            query: Consulta original
            user_id: ID del usuario
            conversation_id: ID de la conversación
        """
        try:
            # Crear registro de respuesta
            log_entry = {
                "timestamp": time.time(),
                "query": query,
                "response_type": response.response_type.value,
                "generation_time": response.metadata.generation_time,
                "confidence": response.metadata.confidence,
                "user_id": user_id,
                "conversation_id": conversation_id,
                "has_audio": response.audio_data is not None,
                "content_length": len(str(response.content)),
                "hemisphere": response.metadata.source_hemisphere
            }
            
            # Guardar en memoria
            if hasattr(self.memory, 'store'):
                self.memory.store(
                    "response_logs",
                    log_entry,
                    collection="analytics"
                )
            
            # Actualizar estadísticas
            self._update_response_stats(log_entry)
            
        except Exception as e:
            logger.warning(f"Error al registrar respuesta: {e}")
    
    def _update_response_stats(self, log_entry: Dict[str, Any]) -> None:
        """
        Actualiza estadísticas de respuestas.
        
        Args:
            log_entry: Registro de respuesta
        """
        try:
            # Verificar si el método retrieve existe
            if not hasattr(self.memory, 'retrieve'):
                return
                
            # Recuperar estadísticas actuales
            stats = self.memory.retrieve("response_stats", {}, collection="analytics")
            
            # Inicializar si no existen
            if not stats:
                stats = {
                    "total_responses": 0,
                    "avg_generation_time": 0.0,
                    "avg_confidence": 0.0,
                    "response_types": {},
                    "hemisphere_usage": {
                        "technical": 0,
                        "emotional": 0,
                        "combined": 0
                    }
                }
            
            # Actualizar estadísticas
            stats["total_responses"] += 1
            
            # Actualizar tiempo promedio
            total_time = stats["avg_generation_time"] * (stats["total_responses"] - 1)
            stats["avg_generation_time"] = (total_time + log_entry["generation_time"]) / stats["total_responses"]
            
            # Actualizar confianza promedio
            total_confidence = stats["avg_confidence"] * (stats["total_responses"] - 1)
            stats["avg_confidence"] = (total_confidence + log_entry["confidence"]) / stats["total_responses"]
            
            # Actualizar conteo de tipos de respuesta
            response_type = log_entry["response_type"]
            stats["response_types"][response_type] = stats["response_types"].get(response_type, 0) + 1
            
            # Actualizar uso de hemisferios
            hemisphere = log_entry.get("hemisphere", "combined")
            stats["hemisphere_usage"][hemisphere] = stats["hemisphere_usage"].get(hemisphere, 0) + 1
            
            # Guardar estadísticas actualizadas
            self.memory.store(
                "response_stats",
                stats,
                collection="analytics",
                permanent=True
            )
            
        except Exception as e:
            logger.warning(f"Error al actualizar estadísticas: {e}")
    
    def get_response_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de respuestas generadas.
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            # Verificar si el método retrieve existe
            if not hasattr(self.memory, 'retrieve'):
                return {
                    "total_responses": 0,
                    "avg_generation_time": 0.0,
                    "avg_confidence": 0.0,
                    "response_types": {},
                    "hemisphere_usage": {}
                }
                
            # Recuperar estadísticas
            stats = self.memory.retrieve("response_stats", {}, collection="analytics")
            
            # Si no hay estadísticas, devolver objeto vacío
            if not stats:
                return {
                    "total_responses": 0,
                    "avg_generation_time": 0.0,
                    "avg_confidence": 0.0,
                    "response_types": {},
                    "hemisphere_usage": {}
                }
            
            return stats
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            return {"error": str(e)}
    
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analiza el sentimiento del texto para adaptar la respuesta.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Diccionario con puntuaciones de sentimiento
        """
        # Palabras positivas y negativas en español
        positive_words: Set[str] = {
            "bueno", "excelente", "fantástico", "increíble", "maravilloso",
            "genial", "estupendo", "perfecto", "agradable", "feliz", "contento",
            "alegre", "satisfecho", "encantado", "fascinado", "impresionado"
        }
        
        negative_words: Set[str] = {
            "malo", "terrible", "horrible", "pésimo", "deficiente", "mediocre",
            "desagradable", "triste", "enojado", "frustrado", "decepcionado",
            "insatisfecho", "molesto", "irritado", "preocupado", "ansioso"
        }
        
        # Convertir texto a minúsculas y tokenizar
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        # Contar palabras positivas y negativas
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        total_words = len(words)
        
        # Calcular puntuaciones
        if total_words > 0:
            positive_score = positive_count / total_words
            negative_score = negative_count / total_words
        else:
            positive_score = 0.0
            negative_score = 0.0
        
        # Calcular puntuación general (-1.0 a 1.0)
        sentiment_score = positive_score - negative_score
        
        return {
            "positive": positive_score,
            "negative": negative_score,
            "sentiment": sentiment_score,
            "neutral": 1.0 - (positive_score + negative_score)
        }
    
    def _adapt_response_to_sentiment(self, response: str, query_sentiment: Dict[str, float]) -> str:
        """
        Adapta la respuesta según el sentimiento de la consulta.
        
        Args:
            response: Respuesta original
            query_sentiment: Análisis de sentimiento de la consulta
            
        Returns:
            Respuesta adaptada
        """
        sentiment_score = query_sentiment.get("sentiment", 0.0)
        
        # Si la consulta es muy negativa, añadir una respuesta empática
        if sentiment_score < -0.3:
            empathetic_prefixes = [
                "Entiendo que esto puede ser frustrante. ",
                "Comprendo tu preocupación. ",
                "Veo que esto te está causando dificultades. ",
                "Lamento que estés pasando por esto. "
            ]
            import random
            prefix = random.choice(empathetic_prefixes)
            return prefix + response
        
        # Si la consulta es muy positiva, reforzar el sentimiento positivo
        elif sentiment_score > 0.3:
            positive_prefixes = [
                "¡Me alegra mucho escuchar eso! ",
                "¡Qué buena noticia! ",
                "¡Excelente! ",
                "¡Fantástico! "
            ]
            import random
            prefix = random.choice(positive_prefixes)
            return prefix + response
        
        # Para consultas neutras, mantener la respuesta original
        return response
    
    def _analyze_query_type(self, query: str) -> str:
        """
        Analiza el tipo de consulta para determinar el balance óptimo de hemisferios.
        
        Args:
            query: Consulta del usuario
            
        Returns:
            Tipo de consulta: "technical", "emotional", o "general"
        """
        # Palabras clave para consultas técnicas
        technical_keywords: Set[str] = {
            "cómo", "funciona", "implementar", "código", "programar", "desarrollar",
            "configurar", "instalar", "optimizar", "depurar", "arquitectura",
            "sistema", "algoritmo", "función", "método", "clase", "objeto",
            "base de datos", "api", "servidor", "cliente", "red", "protocolo"
        }
        
        # Palabras clave para consultas emocionales
        emotional_keywords: Set[str] = {
            "siento", "sentir", "emoción", "feliz", "triste", "enojado", "frustrado",
            "confundido", "preocupado", "ansioso", "estresado", "cansado", "motivado",
            "inspirado", "deprimido", "asustado", "nervioso", "tranquilo"
        }
        
        # Convertir consulta a minúsculas y tokenizar
        query_lower = query.lower()
        words = set(re.findall(r'\b\w+\b', query_lower))
        
        # Contar coincidencias
        technical_count = len(words.intersection(technical_keywords))
        emotional_count = len(words.intersection(emotional_keywords))
        
        # Determinar tipo de consulta
        if technical_count > emotional_count:
            return "technical"
        elif emotional_count > technical_count:
            return "emotional"
        else:
            return "general"
    
    def _generate_cache_key(self, query: str, response_type: str, user_id: Optional[str] = None) -> str:
        """
        Genera una clave única para el caché.
        
        Args:
            query: Consulta del usuario
            response_type: Tipo de respuesta
            user_id: ID del usuario (opcional)
            
        Returns:
            Clave para el caché
        """
        # Normalizar consulta (eliminar espacios extra, convertir a minúsculas)
        normalized_query = ' '.join(query.lower().split())
        
        # Crear componentes de la clave
        key_components = [normalized_query, response_type]
        if user_id:
            key_components.append(f"user:{user_id}")
        
        # Unir componentes
        key_string = "|".join(key_components)
        
        # Generar hash MD5
        import hashlib
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()
    
    def _clean_cache_if_needed(self) -> None:
        """Limpia el caché si excede el tamaño máximo."""
        if len(self.response_cache) > self.cache_max_size:
            # Eliminar entradas más antiguas
            sorted_items = sorted(
                self.response_cache.items(),
                key=lambda x: x[1].get("timestamp", 0)
            )
            # Eliminar el 20% más antiguo
            items_to_remove = int(len(sorted_items) * 0.2)
            for i in range(items_to_remove):
                key, _ = sorted_items[i]
                del self.response_cache[key]

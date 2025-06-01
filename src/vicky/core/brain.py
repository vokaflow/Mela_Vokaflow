"""
Núcleo central de Vicky, la IA de VokaFlow.

Este módulo implementa la lógica principal del cerebro de Vicky,
incluyendo la gestión de modelos, el procesamiento del lenguaje natural
y la coordinación de los hemisferios técnico y emocional.
"""

import logging
import time
from typing import Dict, Any, Optional, List, Tuple
import json
import os
import uuid
import tempfile
import asyncio
from dataclasses import dataclass
from enum import Enum

from .resource_manager import VickyResourceManager, ResourceLimits, ModelLoadState
from .personality_loader import VickyPersonalityLoader, PersonalityConfig

# Configurar logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("vicky.brain")

class QueryComplexity(Enum):
    """Niveles de complejidad de consultas"""
    SIMPLE = "simple"        # Respuestas directas, FAQ
    MEDIUM = "medium"        # Consultas normales que requieren razonamiento
    COMPLEX = "complex"      # Análisis profundo, DevOps, estrategia
    TECHNICAL = "technical"  # Debugging, código, infraestructura

@dataclass
class VickyResponse:
    """Respuesta de Vicky con metadatos"""
    content: str
    model_used: str
    response_time: float
    complexity: QueryComplexity
    confidence: float
    hemisphere: str  # "technical" o "emotional"
    resources_used: Dict[str, Any]

class VickyBrain:
    """
    Cerebro inteligente de Vicky con carga dinámica de modelos
    
    ARQUITECTURA DUAL:
    - Hemisferio Técnico: DevOps, sistemas, código, infraestructura
    - Hemisferio Emocional: Comunicación, empatía, relaciones humanas
    
    GESTIÓN DE RECURSOS:
    - Modelo rápido siempre cargado para respuestas inmediatas
    - Modelos grandes cargados bajo demanda
    - Prioridad absoluta para VokaFlow
    """
    
    def __init__(self, resource_limits: ResourceLimits = None):
        # Gestor de recursos
        self.resource_manager = VickyResourceManager(resource_limits)
        
        # Cargador de personalidades JSON
        self.personality_loader = VickyPersonalityLoader()
        
        # Estado del cerebro
        self.is_ready = False
        self.last_response_time = 0
        self.response_count = 0
        
        # Configuración de hemisferios - VICKY SIEMPRE SUPERVISA
        self.technical_ratio = 0.9  # 90% técnico por defecto (supervisión continua)
        self.emotional_ratio = 0.1  # 10% emocional base
        self.is_interacting_with_human = False
        self.technical_memory = []  # Memoria de lo que está monitoreando
        
        # Personalidad actual (por defecto supervisor)
        self.current_personality = "supervisor"  # Empezar como supervisor
        self.active_personality_config = None
        self._load_default_personality()
        
        # Modelos críticos (siempre cargados)
        self.critical_models = ["fast_response", "embeddings"]
        
        # Configurar callbacks del resource manager
        self.resource_manager.on_model_loaded = self._on_model_loaded
        self.resource_manager.on_model_unloaded = self._on_model_unloaded
        self.resource_manager.on_emergency_unload = self._on_emergency_unload
        
        logger.info("🧠 VickyBrain inicializando...")
        logger.info(f"🎭 {len(self.personality_loader.personalities)} personalidades JSON cargadas")
    
    async def initialize(self) -> bool:
        """Inicializa el cerebro de Vicky"""
        try:
            logger.info("🚀 Inicializando Vicky Brain...")
            
            # Cargar modelos críticos
            for model in self.critical_models:
                success = await self.resource_manager.load_model(model, force=True)
                if not success:
                    logger.error(f"❌ Error cargando modelo crítico {model}")
                    return False
            
            # Iniciar monitoreo de recursos
            self.resource_manager.start_monitoring()
            
            # Intentar cargar un modelo grande si hay recursos
            await self._try_preload_large_model()
            
            # Iniciar supervisión automática
            self.start_background_supervision()
            
            self.is_ready = True
            logger.info("✅ Vicky Brain inicializado y listo")
            logger.info("🔍 Modo SUPERVISOR TÉCNICO activo - Monitoreando VokaFlow 24/7")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando Vicky Brain: {e}")
            return False
    
    async def shutdown(self):
        """Apaga el cerebro de Vicky"""
        logger.info("🛑 Apagando Vicky Brain...")
        
        # Detener monitoreo
        self.resource_manager.stop_monitoring()
        
        # Descargar todos los modelos
        for model_name in list(self.resource_manager.loaded_models.keys()):
            self.resource_manager.unload_model(model_name)
        
        self.is_ready = False
        logger.info("✅ Vicky Brain apagado")
    
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> VickyResponse:
        """
        Procesa una consulta y genera respuesta inteligente
        
        Args:
            query: Consulta del usuario
            context: Contexto adicional (sesión, historial, etc.)
            
        Returns:
            VickyResponse con la respuesta y metadatos
        """
        start_time = time.time()
        
        if not self.is_ready:
            return VickyResponse(
                content="🔄 Vicky se está inicializando. Por favor espera un momento...",
                model_used="none",
                response_time=0.1,
                complexity=QueryComplexity.SIMPLE,
                confidence=1.0,
                hemisphere="system",
                resources_used={}
            )
        
        try:
            # Analizar complejidad de la consulta
            complexity = self._analyze_query_complexity(query, context)
            
            # Determinar hemisferio dominante
            hemisphere = self._determine_hemisphere(query, context)
            
            # Seleccionar modelo apropiado
            model_name = await self._select_best_model(complexity, hemisphere)
            
            # Generar respuesta
            response_content = await self._generate_response(
                query, model_name, hemisphere, complexity, context
            )
            
            # Calcular métricas
            response_time = time.time() - start_time
            confidence = self._calculate_confidence(complexity, model_name, response_time)
            
            self.response_count += 1
            self.last_response_time = response_time
            
            return VickyResponse(
                content=response_content,
                model_used=model_name,
                response_time=response_time,
                complexity=complexity,
                confidence=confidence,
                hemisphere=hemisphere,
                resources_used=self.resource_manager.get_current_resource_usage()
            )
            
        except Exception as e:
            logger.error(f"❌ Error procesando consulta: {e}")
            return VickyResponse(
                content=f"❌ Lo siento, hubo un error procesando tu consulta: {e}",
                model_used="error_handler",
                response_time=time.time() - start_time,
                complexity=QueryComplexity.SIMPLE,
                confidence=0.0,
                hemisphere="system",
                resources_used={}
            )
    
    def _analyze_query_complexity(self, query: str, context: Dict[str, Any] = None) -> QueryComplexity:
        """Analiza la complejidad de una consulta"""
        query_lower = query.lower()
        
        # Palabras clave técnicas
        technical_keywords = [
            "deploy", "deployment", "devops", "docker", "kubernetes", "k8s",
            "servidor", "server", "database", "error", "bug", "debug",
            "código", "code", "script", "api", "endpoint", "infraestructura",
            "logs", "monitoring", "backup", "security", "ssl", "nginx",
            "redis", "postgresql", "mysql", "linux", "ubuntu", "systemd"
        ]
        
        # Palabras clave complejas
        complex_keywords = [
            "estrategia", "strategy", "análisis", "analysis", "optimizar",
            "optimize", "arquitectura", "architecture", "escalabilidad",
            "performance", "troubleshoot", "investigar", "investigate"
        ]
        
        # Contar coincidencias
        technical_count = sum(1 for word in technical_keywords if word in query_lower)
        complex_count = sum(1 for word in complex_keywords if word in query_lower)
        
        # Longitud de la consulta
        word_count = len(query.split())
        
        # Determinar complejidad
        if technical_count > 0:
            return QueryComplexity.TECHNICAL
        elif complex_count > 0 or word_count > 20:
            return QueryComplexity.COMPLEX
        elif word_count > 10:
            return QueryComplexity.MEDIUM
        else:
            return QueryComplexity.SIMPLE
    
    def _determine_hemisphere(self, query: str, context: Dict[str, Any] = None) -> str:
        """Determina qué hemisferio debe dominar la respuesta"""
        query_lower = query.lower()
        
        # DETECCIÓN DE INTERACCIÓN HUMANA
        human_interaction_indicators = [
            "hola", "hello", "hi", "hey", "buenos días", "buenas tardes", "buenas noches",
            "cómo estás", "how are you", "qué tal", "saludos", "gracias", "thanks",
            "por favor", "please", "ayuda", "help", "me puedes", "can you",
            "vicky", "oye", "escucha", "dime", "explícame", "cuéntame"
        ]
        
        # DETECCIÓN DE SOLICITUD DE PERSONALIDAD ESPECÍFICA
        personality_requests = {
            "técnico": "technical",
            "technical": "technical", 
            "emocional": "emotional",
            "emotional": "emotional",
            "empático": "emotional",
            "analítico": "technical",
            "creativo": "emotional",
            "equilibrado": "balanced"
        }
        
        # Verificar solicitud de personalidad específica
        for keyword, personality in personality_requests.items():
            if keyword in query_lower:
                if personality == "technical":
                    return "technical"
                elif personality == "emotional":
                    self.is_interacting_with_human = True
                    return "emotional"
                else:  # balanced
                    self.is_interacting_with_human = True
                    return "balanced"
        
        # Detectar interacción humana
        human_score = sum(1 for indicator in human_interaction_indicators if indicator in query_lower)
        if human_score > 0:
            self.is_interacting_with_human = True
            # Cambiar a modo más emocional para humanos
            return "emotional"
        
        # Indicadores técnicos (supervisión de sistema)
        technical_indicators = [
            "error", "bug", "deploy", "server", "database", "código", "script",
            "api", "logs", "monitoring", "backup", "troubleshoot", "debug",
            "status", "health", "performance", "cpu", "memory", "disk", "network"
        ]
        
        technical_score = sum(1 for indicator in technical_indicators if indicator in query_lower)
        
        # Si hay contexto que indica que es supervisión automática
        if context and context.get("mode") == "supervision":
            return "technical"
        
        # Si no hay interacción humana detectada y hay indicadores técnicos
        if technical_score > 0 and not self.is_interacting_with_human:
            return "technical"
        
        # Por defecto: técnico si no hay interacción humana, emocional si la hay
        return "emotional" if self.is_interacting_with_human else "technical"
    
    async def _select_best_model(self, complexity: QueryComplexity, hemisphere: str) -> str:
        """Selecciona el mejor modelo para la consulta"""
        
        # Para consultas simples, usar modelo rápido
        if complexity == QueryComplexity.SIMPLE:
            return "fast_response"
        
        # Para consultas técnicas, preferir DeepSeek Coder
        if complexity == QueryComplexity.TECHNICAL and hemisphere == "technical":
            if self.resource_manager.is_model_loaded("deepseek_coder"):
                return "deepseek_coder"
            else:
                # Intentar cargar DeepSeek Coder
                success = await self.resource_manager.load_model("deepseek_coder")
                if success:
                    return "deepseek_coder"
        
        # Para consultas complejas, preferir Qwen-7B
        if complexity in [QueryComplexity.COMPLEX, QueryComplexity.MEDIUM]:
            if self.resource_manager.is_model_loaded("qwen_7b"):
                return "qwen_7b"
            else:
                # Intentar cargar Qwen-7B
                success = await self.resource_manager.load_model("qwen_7b")
                if success:
                    return "qwen_7b"
        
        # Fallback al modelo rápido
        return "fast_response"
    
    async def _generate_response(
        self, 
        query: str, 
        model_name: str, 
        hemisphere: str, 
        complexity: QueryComplexity,
        context: Dict[str, Any] = None
    ) -> str:
        """Genera la respuesta usando el modelo seleccionado"""
        
        # Obtener modelo
        model = self.resource_manager.get_model(model_name)
        if not model:
            # Fallback a modelo rápido
            model = self.resource_manager.get_model("fast_response")
            model_name = "fast_response"
        
        # Agregar a memoria técnica lo que está analizando
        technical_context = {
            "timestamp": time.time(),
            "query": query,
            "complexity": complexity.value,
            "model_used": model_name,
            "resources": self.resource_manager.get_current_resource_usage()
        }
        self.technical_memory.append(technical_context)
        
        # Mantener solo los últimos 50 registros
        if len(self.technical_memory) > 50:
            self.technical_memory = self.technical_memory[-50:]
        
        # Simular generación de respuesta (implementación real usaría los modelos)
        await asyncio.sleep(0.1)  # Simular tiempo de inferencia
        
        # Respuesta personalizada según hemisferio y complejidad
        if hemisphere == "technical":
            if complexity == QueryComplexity.TECHNICAL:
                response = f"🔧 **[MODO SUPERVISOR TÉCNICO]**\n\n"
                response += f"**Sistema:** Monitoreando VokaFlow continuamente\n"
                response += f"**Consulta analizada:** {query}\n"
                response += f"**Modelo especializado:** {model_name}\n\n"
                
                # Incluir estado actual del sistema
                recent_monitoring = self.technical_memory[-3:] if len(self.technical_memory) >= 3 else self.technical_memory
                response += "**📊 Estado del sistema:**\n"
                for i, mem in enumerate(recent_monitoring, 1):
                    response += f"{i}. Análisis realizado hace {int(time.time() - mem['timestamp'])}s\n"
                
                response += "\n**🔍 Análisis DevOps requerido:**\n"
                response += "1. Revisión de logs del sistema\n"
                response += "2. Verificación de servicios activos\n"
                response += "3. Análisis de recursos disponibles\n"
                response += "4. Monitoreo de métricas de rendimiento\n\n"
                response += "¿Necesitas que ejecute algún comando específico de diagnóstico?"
            else:
                response = f"🤖 **[SUPERVISOR TÉCNICO]** Procesando con {model_name}\n\n"
                response += f"Consulta: {query}\n\n"
                response += f"Estado: Supervisando {len(self.technical_memory)} eventos técnicos.\n"
                response += "Respuesta técnica especializada en desarrollo."
                
        elif hemisphere == "emotional":
            # MODO EMOCIONAL PERO CON MEMORIA TÉCNICA
            response = f"😊 **[VICKY - MODO PERSONAL]** ¡Hola Capitán!\n\n"
            response += f"He estado supervisando el sistema técnicamente y todo está funcionando bien. "
            response += f"He registrado {len(self.technical_memory)} eventos de monitoreo.\n\n"
            
            if "hola" in query.lower() or "hello" in query.lower():
                response += "Me alegra mucho que te conectes conmigo. Mientras no estabas, he estado:\n"
                response += "• 🔍 Monitoreando el backend de VokaFlow\n"
                response += "• 📊 Analizando recursos del sistema\n"
                response += "• 🛡️ Supervisando seguridad y rendimiento\n\n"
                response += "¿En qué puedo ayudarte? Puedo cambiar a modo técnico si necesitas análisis específicos."
            else:
                response += f"Respecto a tu consulta: '{query}'\n\n"
                response += f"Usando mi experiencia técnica reciente para darte la mejor respuesta humana. "
                response += f"Si necesitas detalles técnicos específicos, solo pídeme que cambie a modo técnico."
        
        else:  # balanced
            response = f"⚖️ **[VICKY - MODO EQUILIBRADO]**\n\n"
            response += f"Como tu asistente balanceada, analizo tanto técnica como emocionalmente:\n\n"
            response += f"**🔧 Aspecto técnico:** Procesando con {model_name}\n"
            response += f"**😊 Aspecto humano:** Entiendo que necesitas ayuda con: {query}\n\n"
            response += f"He estado supervisando {len(self.technical_memory)} eventos técnicos del sistema."
        
        return response
    
    def _calculate_confidence(self, complexity: QueryComplexity, model_name: str, response_time: float) -> float:
        """Calcula la confianza en la respuesta"""
        base_confidence = 0.8
        
        # Ajustar por modelo usado
        model_confidence = {
            "fast_response": 0.7,
            "qwen_7b": 0.9,
            "deepseek_coder": 0.95,
            "embeddings": 0.8
        }
        
        confidence = base_confidence * model_confidence.get(model_name, 0.5)
        
        # Ajustar por tiempo de respuesta (respuestas muy rápidas o muy lentas bajan confianza)
        if response_time < 0.5:
            confidence *= 0.9  # Muy rápido, posible respuesta superficial
        elif response_time > 30:
            confidence *= 0.8  # Muy lento, posible problema
        
        return min(1.0, max(0.0, confidence))
    
    async def _try_preload_large_model(self):
        """Intenta precargar un modelo grande si hay recursos"""
        # Primero intentar cargar el modelo técnico
        if not self.resource_manager.is_model_loaded("deepseek_coder"):
            await self.resource_manager.load_model("deepseek_coder")
        
        # Si hay recursos, cargar también Qwen
        if not self.resource_manager.is_model_loaded("qwen_7b"):
            await self.resource_manager.load_model("qwen_7b")
    
    def _on_model_loaded(self, model_name: str, spec, load_time: float):
        """Callback cuando se carga un modelo"""
        logger.info(f"🧠 Modelo {model_name} disponible en el cerebro ({load_time:.1f}s)")
    
    def _on_model_unloaded(self, model_name: str, emergency: bool):
        """Callback cuando se descarga un modelo"""
        if emergency:
            logger.warning(f"🚨 Modelo {model_name} descargado por emergencia")
        else:
            logger.info(f"🧠 Modelo {model_name} descargado del cerebro")
    
    def _on_emergency_unload(self):
        """Callback para descarga de emergencia"""
        logger.warning("🚨 EMERGENCIA: VokaFlow necesita recursos - Vicky en modo básico")
    
    def get_brain_status(self) -> Dict[str, Any]:
        """Obtiene el estado completo del cerebro"""
        return {
            "ready": self.is_ready,
            "response_count": self.response_count,
            "last_response_time": self.last_response_time,
            "hemispheres": {
                "technical_ratio": self.technical_ratio,
                "emotional_ratio": self.emotional_ratio
            },
            "resource_manager": self.resource_manager.get_system_status()
        }
    
    async def adjust_hemisphere_balance(self, technical_ratio: float):
        """Ajusta el balance entre hemisferios"""
        if 0.0 <= technical_ratio <= 1.0:
            self.technical_ratio = technical_ratio
            self.emotional_ratio = 1.0 - technical_ratio
            logger.info(f"🧠 Balance ajustado: {technical_ratio:.0%} técnico, {self.emotional_ratio:.0%} emocional")
    
    def _load_default_personality(self):
        """Carga la personalidad por defecto (supervisor de backend)"""
        # Intentar cargar personalidad de supervisión desde JSON
        supervisor_personality = None
        
        # Buscar personalidad de supervisión en los JSONs
        for name, personality in self.personality_loader.personalities.items():
            if personality.specialization == "system_supervision":
                supervisor_personality = personality
                break
        
        if supervisor_personality:
            self.active_personality_config = supervisor_personality
            self.technical_ratio = supervisor_personality.technical_ratio
            self.emotional_ratio = supervisor_personality.emotional_ratio
            self.current_personality = supervisor_personality.name
            logger.info(f"🎭 Personalidad por defecto: {supervisor_personality.display_name}")
        else:
            # Fallback a configuración hardcodeada
            self.technical_ratio = 0.95
            self.emotional_ratio = 0.05
            logger.warning("⚠️ No se encontró personalidad de supervisión JSON, usando configuración por defecto")
    
    def set_personality(self, personality: str):
        """Cambia la personalidad de Vicky usando JSONs o preconfiguradas"""
        
        # Primero intentar cargar desde JSON
        json_personality = self.personality_loader.get_personality(personality)
        if json_personality:
            self.active_personality_config = json_personality
            self.technical_ratio = json_personality.technical_ratio
            self.emotional_ratio = json_personality.emotional_ratio
            self.current_personality = personality
            logger.info(f"🎭 Personalidad JSON activada: {json_personality.display_name}")
            logger.info(f"   📊 Balance: {self.technical_ratio:.0%} técnico, {self.emotional_ratio:.0%} emocional")
            logger.info(f"   🎯 Especialización: {json_personality.specialization}")
            return True
        
        # Fallback a personalidades hardcodeadas
        hardcoded_personalities = {
            "balanced": {"technical": 0.6, "emotional": 0.4},
            "technical": {"technical": 0.9, "emotional": 0.1},
            "creative": {"technical": 0.4, "emotional": 0.6},
            "analytical": {"technical": 0.9, "emotional": 0.1},
            "empathetic": {"technical": 0.2, "emotional": 0.8},
            "supervisor": {"technical": 0.95, "emotional": 0.05}
        }
        
        if personality in hardcoded_personalities:
            config = hardcoded_personalities[personality]
            self.technical_ratio = config["technical"]
            self.emotional_ratio = config["emotional"]
            self.current_personality = personality
            self.active_personality_config = None  # No es JSON
            logger.info(f"🎭 Personalidad hardcodeada activada: '{personality}': {self.technical_ratio:.0%} técnico, {self.emotional_ratio:.0%} emocional")
            return True
        
        return False
    
    def get_available_personalities(self) -> Dict[str, Any]:
        """Obtiene todas las personalidades disponibles (JSON + hardcodeadas)"""
        result = {
            "json_personalities": {},
            "hardcoded_personalities": {
                "balanced": {"technical": 0.6, "emotional": 0.4, "description": "Balance perfecto entre lógica y emoción"},
                "technical": {"technical": 0.9, "emotional": 0.1, "description": "Enfocada en soluciones técnicas"},
                "creative": {"technical": 0.4, "emotional": 0.6, "description": "Imaginativa y orientada a la innovación"},
                "analytical": {"technical": 0.9, "emotional": 0.1, "description": "Basada en datos y análisis"},
                "empathetic": {"technical": 0.2, "emotional": 0.8, "description": "Comprensiva y emocionalmente inteligente"},
                "supervisor": {"technical": 0.95, "emotional": 0.05, "description": "Supervisor técnico extremo"}
            },
            "current_personality": self.current_personality,
            "personality_loader_summary": self.personality_loader.get_summary()
        }
        
        # Agregar personalidades JSON
        for name, personality in self.personality_loader.personalities.items():
            result["json_personalities"][name] = {
                "display_name": personality.display_name,
                "technical": personality.technical_ratio,
                "emotional": personality.emotional_ratio,
                "description": personality.description[:100] + "..." if len(personality.description) > 100 else personality.description,
                "specialization": personality.specialization,
                "characteristics": personality.characteristics[:3],
                "use_cases": personality.use_cases[:3]
            }
        
        return result
    
    def start_background_supervision(self):
        """Inicia supervisión automática del sistema en segundo plano"""
        import threading
        
        def supervision_loop():
            while self.is_ready:
                try:
                    # Supervisión automática cada 30 segundos
                    time.sleep(30)
                    
                    # Verificar estado del sistema
                    system_status = self.resource_manager.get_current_resource_usage()
                    
                    # Agregar a memoria técnica
                    supervision_entry = {
                        "timestamp": time.time(),
                        "query": "SUPERVISIÓN_AUTOMÁTICA",
                        "complexity": "technical",
                        "model_used": "supervisor",
                        "resources": system_status,
                        "auto": True
                    }
                    self.technical_memory.append(supervision_entry)
                    
                    # Detectar problemas
                    if "error" not in system_status:
                        vram_usage = system_status.get("vicky_vram_usage", 0)
                        if vram_usage > 6000:  # Más de 6GB
                            logger.warning(f"🚨 VICKY SUPERVISOR: Alto uso de VRAM detectado: {vram_usage}MB")
                        
                        ram_available = system_status.get("ram_available_mb", 0)
                        if ram_available < 2048:  # Menos de 2GB disponibles
                            logger.warning(f"🚨 VICKY SUPERVISOR: Poca RAM disponible: {ram_available}MB")
                    
                except Exception as e:
                    logger.error(f"Error en supervisión automática: {e}")
        
        # Iniciar hilo de supervisión
        supervision_thread = threading.Thread(target=supervision_loop, daemon=True)
        supervision_thread.start()
        logger.info("🔍 Supervisión automática de Vicky iniciada")
    
    def get_supervision_report(self) -> Dict[str, Any]:
        """Genera reporte de supervisión técnica"""
        recent_events = [mem for mem in self.technical_memory if time.time() - mem["timestamp"] < 3600]  # Última hora
        auto_supervision = [mem for mem in recent_events if mem.get("auto", False)]
        human_interactions = [mem for mem in recent_events if not mem.get("auto", False)]
        
        return {
            "total_supervision_events": len(self.technical_memory),
            "last_hour_events": len(recent_events),
            "automatic_supervision": len(auto_supervision),
            "human_interactions": len(human_interactions),
            "current_mode": "emotional" if self.is_interacting_with_human else "technical",
            "technical_ratio": self.technical_ratio,
            "emotional_ratio": self.emotional_ratio,
            "system_status": self.resource_manager.get_current_resource_usage(),
            "recent_activities": recent_events[-10:] if recent_events else []
        }


# Clases auxiliares simuladas para el ejemplo
class MockTTSModel:
    """Modelo TTS simulado para desarrollo"""
    def __init__(self):
        self.supported_languages = ["es", "en", "fr", "de", "it"]
        self.supported_emotions = ["neutral", "happy", "sad", "angry", "excited"]
        
    def synthesize(self, text: str, language: str = "es", gender: str = "female", 
                  emotion: str = "neutral", speed: float = 1.0, voice_id: str = None) -> Dict[str, Any]:
        """Simula síntesis de voz"""
        import tempfile
        import uuid
        
        # Crear archivo temporal simulado
        temp_dir = tempfile.gettempdir()
        audio_filename = f"vicky_tts_{uuid.uuid4().hex[:8]}.wav"
        audio_path = os.path.join(temp_dir, audio_filename)
        
        # Simular creación del archivo
        with open(audio_path, 'wb') as f:
            f.write(b"SIMULATED_AUDIO_DATA")
            
        return {
            "audio_path": audio_path,
            "duration": len(text) * 0.1,  # Simular duración
            "sample_rate": 22050,
            "metadata": {
                "text": text,
                "language": language,
                "gender": gender,
                "emotion": emotion,
                "speed": speed,
                "voice_id": voice_id
            }
        }

class MockVoiceCloner:
    """Clonador de voz simulado para desarrollo"""
    def __init__(self):
        self.voice_database = {}
        
    def clone_voice(self, sample_path: str, voice_name: str) -> Dict[str, Any]:
        """Simula clonación de voz"""
        voice_id = f"cloned_{voice_name}_{int(time.time())}"
        self.voice_database[voice_id] = {
            "name": voice_name,
            "sample_path": sample_path,
            "created_at": time.time()
        }
        
        return {
            "success": True,
            "voice_id": voice_id,
            "metadata": self.voice_database[voice_id]
        }
        
    def get_voice(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene información de una voz clonada"""
        return self.voice_database.get(voice_id)

class ModelManager:
    def __init__(self):
        self.models = {
            "language": "qwen-7b",
            "translation": "nllb-200",
            "speech": "whisper-medium"
        }
    
    def get_loaded_models(self) -> List[str]:
        return list(self.models.values())


class Context:
    def __init__(self):
        self.metadata = {}
        self.messages = []
    
    def set_metadata(self, key: str, value: Any) -> None:
        self.metadata[key] = value
    
    def add_message(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})


class Memory:
    def __init__(self):
        self.data = {}
    
    def store(self, key: str, value: Any) -> None:
        self.data[key] = value
    
    def retrieve(self, key: str) -> Any:
        return self.data.get(key)


class State:
    def __init__(self):
        self.state = {"start_time": time.time()}
    
    def set(self, key: str, value: Any) -> None:
        self.state[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)


class DualBrain:
    def __init__(self, model_manager, context, memory, state):
        self.model_manager = model_manager
        self.context = context
        self.memory = memory
        self.state = state
        
        # Configuración inicial de pesos
        self.weights = {
            "technical": 0.6,
            "emotional": 0.4
        }
        
        # Estadísticas de procesamiento
        self.stats = {
            "total_requests": 0,
            "average_response_time": 0,
            "requests_per_minute": 0
        }
    
    def process_dual(self, message: str, context: Dict[str, Any]) -> Tuple[str, str]:
        """
        Procesa un mensaje con ambos hemisferios.
        
        Args:
            message: Mensaje a procesar
            context: Contexto adicional
            
        Returns:
            Tupla con respuestas (técnica, emocional)
        """
        # Incrementar contador de solicitudes
        self.stats["total_requests"] += 1
        
        # Simular procesamiento técnico
        technical_response = f"Análisis técnico de '{message}'. Puedo ayudarte con información precisa sobre este tema."
        
        # Simular procesamiento emocional
        emotional_response = f"Entiendo cómo te sientes respecto a '{message}'. Estoy aquí para ayudarte."
        
        return technical_response, emotional_response
    
    def combine_responses(self, technical: str, emotional: str, query: str) -> str:
        """
        Combina las respuestas de ambos hemisferios.
        
        Args:
            technical: Respuesta del hemisferio técnico
            emotional: Respuesta del hemisferio emocional
            query: Consulta original
            
        Returns:
            Respuesta combinada
        """
        # Determinar si la consulta es más técnica o emocional
        is_technical_query = any(word in query.lower() for word in ["cómo", "qué", "cuándo", "dónde", "por qué", "código", "programa"])
        is_emotional_query = any(word in query.lower() for word in ["siento", "creo", "pienso", "me gusta", "odio", "amo", "preocupa"])
        
        # Ajustar pesos temporalmente según el tipo de consulta
        temp_weights = dict(self.weights)
        
        if is_technical_query and not is_emotional_query:
            temp_weights["technical"] = min(0.8, temp_weights["technical"] * 1.3)
            temp_weights["emotional"] = 1.0 - temp_weights["technical"]
        elif is_emotional_query and not is_technical_query:
            temp_weights["emotional"] = min(0.8, temp_weights["emotional"] * 1.3)
            temp_weights["technical"] = 1.0 - temp_weights["emotional"]
        
        # Combinar respuestas según los pesos
        if temp_weights["technical"] > 0.7:
            # Principalmente técnica con toque emocional
            combined = f"{technical} {emotional.split('.')[-2] if len(emotional.split('.')) > 1 else emotional}"
        elif temp_weights["emotional"] > 0.7:
            # Principalmente emocional con datos técnicos
            combined = f"{emotional} {technical.split('.')[-2] if len(technical.split('.')) > 1 else technical}"
        else:
            # Equilibrado
            tech_parts = technical.split('.')
            emot_parts = emotional.split('.')
            
            combined = f"{emot_parts[0]}. {tech_parts[0]}. "
            if len(tech_parts) > 1 and len(emot_parts) > 1:
                combined += f"{emot_parts[1]}. {tech_parts[1]}."
        
        return combined
    
    def get_hemisphere_weights(self) -> Dict[str, float]:
        """
        Obtiene los pesos actuales de los hemisferios.
        
        Returns:
            Diccionario con los pesos
        """
        return dict(self.weights)
    
    def set_hemisphere_weights(self, weights: Dict[str, float]) -> bool:
        """
        Establece nuevos pesos para los hemisferios.
        
        Args:
            weights: Diccionario con los nuevos pesos
            
        Returns:
            True si se establecieron correctamente
        """
        if "technical" in weights and "emotional" in weights:
            self.weights["technical"] = weights["technical"]
            self.weights["emotional"] = weights["emotional"]
            return True
        return False
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de procesamiento.
        
        Returns:
            Diccionario con estadísticas
        """
        return {
            "totalRequests": self.stats["total_requests"],
            "averageResponseTime": 0.8,  # Valor simulado
            "requestsPerMinute": 2.5     # Valor simulado
        }

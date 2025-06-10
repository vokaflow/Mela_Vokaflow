"""
VokaFlow Backend - Vicky Router REVOLUCIONARIO
Conecta directamente con CognitiveIntegration (40+ personalidades)
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import time
import logging
from datetime import datetime
import uuid

# 🧠 IMPORTAR SOLO EL SISTEMA COGNITIVO REVOLUCIONARIO
from VickyAI.core.vicky_cognitive_integration import VickyCognitiveIntegration
from VickyAI.persistence.state_manager import state_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vicky", tags=["vicky"])

# 🚀 INSTANCIA ÚNICA DEL SISTEMA COGNITIVO REVOLUCIONARIO
cognitive_integration = None

# Inicializar el sistema cognitivo al cargar el router
try:
    logger.info("🧠 Inicializando VickyCognitiveIntegration...")
    cognitive_integration = VickyCognitiveIntegration()
    integration_status = cognitive_integration.get_integration_status()
    logger.info(f"✅ Sistema cognitivo: {integration_status['integration_active']}")
    
except Exception as e:
    logger.error(f"❌ Error inicializando sistema Vicky: {e}")
    cognitive_integration = None

# Cargar estado persistente al inicializar
vicky_state = state_manager.load_state()
vicky_config = state_manager.load_config()

# Verificar si es la primera ejecución
if vicky_state.get("session_count", 0) == 0:
    logger.info("🎭 Primera ejecución de Vicky - Inicializando estado")
    vicky_state["uptime_start"] = datetime.now().isoformat()
    state_manager.save_state(vicky_state)

# Incrementar contador de sesión
vicky_state["session_count"] = vicky_state.get("session_count", 0) + 1
state_manager.save_state(vicky_state)

logger.info(f"🧠 Vicky AI iniciado - Sesión #{vicky_state['session_count']}")

# Modelos Pydantic
class ProcessRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class PersonalityRequest(BaseModel):
    personality: str

class HemisphereRequest(BaseModel):
    technical: float
    emotional: float

# Endpoints principales

@router.get("/ping")
async def vicky_ping():
    """Endpoint simple de prueba para verificar que el router funciona"""
    return {"message": "🎭 Vicky router funcionando!", "timestamp": datetime.now().isoformat()}

@router.get("/status")
async def get_vicky_status():
    """Obtiene el estado actual de Vicky"""
    try:
        # Actualizar estado en tiempo real
        current_time = datetime.now()
        vicky_state["last_update"] = current_time.isoformat()
        
        # Calcular uptime
        if "uptime_start" in vicky_state:
            uptime_start = datetime.fromisoformat(vicky_state["uptime_start"])
            uptime_seconds = (current_time - uptime_start).total_seconds()
        else:
            uptime_seconds = 0
        
        # Status del sistema cognitivo
        cognitive_status = "offline"
        if cognitive_integration:
            try:
                integration_status = cognitive_integration.get_integration_status()
                cognitive_status = "online" if integration_status['integration_active'] else "error"
            except:
                cognitive_status = "error"
        
        return {
            "status": cognitive_status,
            "session_count": vicky_state.get("session_count", 0),
            "total_interactions": vicky_state.get("total_interactions", 0),
            "current_personality": vicky_state.get("current_personality", "VickyUnified"),
            "hemisphere_balance": vicky_state.get("hemisphere_balance", {"technical": 0.6, "emotional": 0.4}),
            "uptime_seconds": uptime_seconds,
            "cognitive_system": "VickyCognitiveIntegration",
            "personalities_count": 40,
            "cognitive_mode": cognitive_status == "online",
            "last_update": vicky_state["last_update"]
        }
    except Exception as e:
        logger.error(f"Error obteniendo estado: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process")
async def process_message(request: ProcessRequest):
    """Procesa un mensaje del usuario usando el sistema cognitivo revolucionario"""
    try:
        start_time = time.time()
        session_id = str(uuid.uuid4())
        
        # Registrar interacción
        vicky_state["total_interactions"] = vicky_state.get("total_interactions", 0) + 1
        
        # Obtener balance hemisférico actual
        hemisphere_balance = vicky_state.get("hemisphere_balance", {"technical": 0.6, "emotional": 0.4})
        
        # Verificar que el sistema cognitivo esté disponible
        if not cognitive_integration:
            logger.error("❌ Sistema cognitivo no inicializado")
            return {
                "success": False,
                "error": "Sistema cognitivo no disponible",
                "cognitive_mode": False,
                "fallback_mode": True,
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # Detectar idioma automáticamente del input del usuario
            detected_language = _detect_user_language(request.message)
            
            # 🎯 CONFIGURACIÓN COMPLETA PARA SISTEMA COGNITIVO
            context_enhanced = {
                "session_id": session_id,
                "user_input": request.message,
                "detected_language": detected_language,
                "target_language": detected_language or "español",
                "hemisphere_balance": hemisphere_balance,
                "cultural_context": _extract_cultural_context(request.message, detected_language),
                "conversation_history": [],
                "user_preferences": {"natural_conversation": True},
                "models_available": ["cognitive_integration"],
                **(request.context or {})
            }
            
            logger.info(f"🧠 Activando SISTEMA COGNITIVO REVOLUCIONARIO - Idioma: {detected_language}")
            
            # 🔥 PROCESAMIENTO COGNITIVO REVOLUCIONARIO
            cognitive_result = cognitive_integration.process_message_cognitive(
                request.message, 
                context_enhanced
            )
            
            # Verificar resultado cognitivo
            if cognitive_result and isinstance(cognitive_result, dict):
                # Extraer respuesta del sistema cognitivo
                response_text = ""
                if 'text' in cognitive_result:
                    response_text = cognitive_result['text']
                elif 'unified_text' in cognitive_result:
                    response_text = cognitive_result['unified_text']
                elif isinstance(cognitive_result.get('final_response'), dict):
                    response_text = cognitive_result['final_response'].get('primary_response', '')
                else:
                    response_text = str(cognitive_result.get('content', 'Sistema cognitivo procesó el mensaje'))
                
                # Extraer personalidades activas
                active_personalities = cognitive_result.get('active_personalities', ['VickyUnified'])
                primary_personality = active_personalities[0] if active_personalities else 'VickyUnified'
                
                # Extraer confianza
                confidence = cognitive_result.get('confidence', 0.85)
                if 'unified_confidence' in cognitive_result:
                    confidence = cognitive_result['unified_confidence']
                
                # Verificar que la respuesta esté en español
                response_text = _ensure_spanish_response(response_text, request.message)
                
                logger.info(f"✅ Sistema cognitivo procesó exitosamente - Personalidades: {active_personalities}, Confidence: {confidence:.2f}")
                
                cognitive_mode = True
                fallback_mode = False
                processing_method = 'vicky_cognitive_integration'
                enhancement_note = 'Respuesta generada por sistema cognitivo revolucionario con 40+ personalidades'
                
            else:
                logger.warning("⚠️ Resultado cognitivo inválido, respuesta de emergencia")
                response_text = _generate_emergency_response(request.message)
                confidence = 0.60
                primary_personality = 'VickyEmergency'
                active_personalities = ['VickyEmergency']
                cognitive_mode = False
                fallback_mode = True
                processing_method = 'emergency_fallback'
                enhancement_note = 'Respuesta de emergencia - sistema cognitivo falló'
                
        except Exception as e:
            logger.error(f"❌ Error en sistema cognitivo: {e}")
            # Respuesta de emergencia auténtica
            response_text = _generate_emergency_response(request.message)
            confidence = 0.50
            primary_personality = 'VickyEmergency'
            active_personalities = ['VickyEmergency']
            cognitive_mode = False
            fallback_mode = True
            processing_method = 'emergency_fallback'
            enhancement_note = f'Respuesta de emergencia - error: {str(e)}'
        
        # Calcular tiempo de procesamiento
        processing_time = time.time() - start_time
        
        # Guardar conversación en persistencia
        state_manager.save_conversation(
            user_message=request.message,
            vicky_response=response_text,
            personality=primary_personality,
            hemisphere_balance=hemisphere_balance,
            confidence=confidence,
            processing_time=processing_time,
            session_id=session_id,
            metadata={
                "cognitive_mode": cognitive_mode,
                "active_personalities": active_personalities,
                "processing_method": processing_method,
                "context": request.context
            }
        )
        
        # Actualizar métricas en tiempo real
        vicky_state["last_response"] = {
            "timestamp": datetime.now().isoformat(),
            "processing_time": processing_time,
            "cognitive_mode": cognitive_mode,
            "confidence": confidence
        }
        
        # Guardar métricas
        state_manager.save_metrics("response_time", processing_time, {
            "personality": primary_personality,
            "confidence": confidence,
            "cognitive_mode": cognitive_mode,
            "message_length": len(request.message)
        })
        
        state_manager.save_metrics("interaction", 1.0, {
            "cognitive_mode": cognitive_mode,
            "hemisphere_balance": hemisphere_balance
        })
        
        # Guardar estado actualizado
        state_manager.save_state(vicky_state)
        
        return {
            "success": True,
            "response": response_text,
            "text": response_text,  # Alias para compatibilidad
            "personality": primary_personality,
            "active_personalities": active_personalities,
            "hemisphere_balance": hemisphere_balance,
            "processing_time": processing_time,
            "confidence": confidence,
            "session_id": session_id,
            "cognitive_mode": cognitive_mode,
            "fallback_mode": fallback_mode,
            "processing_method": processing_method,
            "enhancement_note": enhancement_note,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "session_interactions": vicky_state["total_interactions"],
                "system": "VickyCognitiveIntegration"
            }
        }
        
    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}")
        
        # Incrementar error rate
        if "error_analysis" not in vicky_state:
            vicky_state["error_analysis"] = {"error_rate": 0.0}
        vicky_state["error_analysis"]["error_rate"] = min(1.0, vicky_state["error_analysis"]["error_rate"] + 0.01)
        
        # Guardar métrica de error
        state_manager.save_metrics("error", 1.0, {
            "error_type": str(type(e).__name__),
            "error_message": str(e)
        })
        
        raise HTTPException(status_code=500, detail=f"Error procesando mensaje: {str(e)}")

@router.get("/personalities")
async def get_available_personalities():
    """Obtiene las personalidades disponibles del sistema cognitivo"""
    try:
        if cognitive_integration:
            try:
                # Usar el sistema cognitivo para obtener personalidades
                personality_status = cognitive_integration.personality_manager.get_personality_status()
                available_personalities = list(personality_status.get('personalities_status', {}).keys())
                
                # Formatear para el dashboard
                formatted_personalities = []
                for personality_name in available_personalities:
                    formatted_personalities.append({
                        "id": personality_name,
                        "name": personality_name.replace("_", " ").title(),
                        "description": f"Personalidad {personality_name.replace('_', ' ')} del sistema cognitivo",
                        "cognitive_system": True
                    })
                    
            except Exception as e:
                logger.warning(f"Error accediendo personalidades del sistema cognitivo: {e}")
                formatted_personalities = [
                    {
                        "id": "VickyUnified",
                        "name": "Vicky Unificada", 
                        "description": "Personalidad unificada del sistema cognitivo",
                        "cognitive_system": True
                    }
                ]
        else:
            # Fallback si el sistema cognitivo no está disponible
            formatted_personalities = [
                {
                    "id": "VickyEmergency",
                    "name": "Vicky Emergencia",
                    "description": "Personalidad de emergencia",
                    "cognitive_system": False
                }
            ]
        
        return {
            "personalities": formatted_personalities,
            "current_personality": vicky_state.get("current_personality", "VickyUnified"),
            "total_available": len(formatted_personalities),
            "cognitive_system_active": cognitive_integration is not None,
            "system_type": "VickyCognitiveIntegration"
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo personalidades: {e}")
        return {
            "personalities": [
                {
                    "id": "VickyError",
                    "name": "Vicky Error",
                    "description": "Error obteniendo personalidades",
                    "cognitive_system": False
                }
            ],
            "current_personality": "VickyError",
            "total_available": 0,
            "error": str(e),
            "cognitive_system_active": False
        }

@router.get("/metrics")
async def get_vicky_metrics():
    """Obtiene métricas detalladas del sistema"""
    try:
        # Obtener métricas de base de datos
        recent_metrics = state_manager.get_metrics(hours=24)
        
        # Calcular estadísticas
        response_times = [m for m in recent_metrics if m["metric_type"] == "response_time"]
        interactions = [m for m in recent_metrics if m["metric_type"] == "interaction"]
        errors = [m for m in recent_metrics if m["metric_type"] == "error"]
        
        avg_response_time = sum(m["metric_value"] for m in response_times) / len(response_times) if response_times else 0.8
        total_interactions = len(interactions)
        error_rate = len(errors) / max(total_interactions, 1) if total_interactions > 0 else 0.0
        
        # Métricas del sistema cognitivo
        cognitive_metrics = {
            "active": cognitive_integration is not None,
            "type": "VickyCognitiveIntegration",
            "personalities_count": 40
        }
        
        if cognitive_integration:
            try:
                integration_status = cognitive_integration.get_integration_status()
                cognitive_metrics.update(integration_status)
            except:
                cognitive_metrics["status"] = "error"
        
        return {
            "cognitive_system": cognitive_metrics,
            "processing_efficiency": {
                "average_response_time": avg_response_time,
                "total_interactions": total_interactions,
                "error_rate": error_rate
            },
            "interaction_patterns": {
                "total_interactions": vicky_state.get("total_interactions", 0),
                "session_count": vicky_state.get("session_count", 0)
            },
            "system_stats": state_manager.get_system_stats(),
            "recent_metrics_count": len(recent_metrics),
            "last_update": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas: {e}")
        return {
            "error": str(e),
            "cognitive_system": {"active": False, "error": str(e)},
            "processing_efficiency": {"average_response_time": 0.0, "error_rate": 1.0},
            "last_update": datetime.now().isoformat()
        }

@router.post("/test-interaction")
async def test_vicky_interaction(request: ProcessRequest):
    """Endpoint de prueba para interactuar con Vicky"""
    try:
        # Usar el endpoint process normal para mantener consistencia
        return await process_message(request)
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ==================== FUNCIONES AUXILIARES REVOLUCIONARIAS PARA VICKY ====================

def _detect_user_language(user_message: str) -> str:
    """🌍 Detecta automáticamente el idioma del usuario"""
    try:
        message_lower = user_message.lower().strip()
        
        # Palabras indicadoras por idioma
        spanish_indicators = [
            'hola', 'cómo', 'qué', 'dónde', 'cuándo', 'por favor', 'gracias', 
            'ayuda', 'necesito', 'quiero', 'puedes', 'estoy', 'tengo', 'hacer',
            'soy', 'está', 'muy', 'bien', 'mal', 'bueno', 'malo'
        ]
        
        english_indicators = [
            'hello', 'how', 'what', 'where', 'when', 'please', 'thank', 'thanks',
            'help', 'need', 'want', 'can', 'could', 'would', 'should', 'i am',
            'you are', 'very', 'good', 'bad', 'nice', 'great'
        ]
        
        # Contar indicadores
        spanish_count = sum(1 for word in spanish_indicators if word in message_lower)
        english_count = sum(1 for word in english_indicators if word in message_lower)
        
        # Determinar idioma dominante
        if spanish_count > english_count:
            return 'español'
        elif english_count > spanish_count:
            return 'english'
        else:
            # Análisis de caracteres especiales
            if any(char in user_message for char in ['ñ', 'á', 'é', 'í', 'ó', 'ú', '¿', '¡']):
                return 'español'
            else:
                return 'español'  # Default a español
        
    except Exception as e:
        logger.warning(f"Error detectando idioma: {e}")
        return 'español'

def _extract_cultural_context(user_message: str, detected_language: str) -> Dict[str, Any]:
    """🎭 Extrae contexto cultural del mensaje del usuario"""
    try:
        cultural_context = {
            'language': detected_language,
            'formality_level': 'medium',
            'cultural_markers': [],
            'communication_style': 'direct',
            'context_type': 'general'
        }
        
        message_lower = user_message.lower()
        
        # Análisis de formalidad
        formal_indicators = ['usted', 'señor', 'señora', 'estimado', 'cordialmente', 'por favor']
        informal_indicators = ['tú', 'vos', 'che', 'qué tal', 'hola']
        
        formal_count = sum(1 for indicator in formal_indicators if indicator in message_lower)
        informal_count = sum(1 for indicator in informal_indicators if indicator in message_lower)
        
        if formal_count > informal_count:
            cultural_context['formality_level'] = 'high'
        elif informal_count > formal_count:
            cultural_context['formality_level'] = 'low'
        
        # Análisis de contexto
        business_markers = ['empresa', 'negocio', 'trabajo', 'oficina', 'reunión', 'proyecto']
        if any(marker in message_lower for marker in business_markers):
            cultural_context['context_type'] = 'business'
        
        personal_markers = ['familia', 'amor', 'amigo', 'sentimiento', 'personal']
        if any(marker in message_lower for marker in personal_markers):
            cultural_context['context_type'] = 'personal'
        
        return cultural_context
        
    except Exception as e:
        logger.warning(f"Error extrayendo contexto cultural: {e}")
        return {
            'language': detected_language or 'español',
            'formality_level': 'medium',
            'cultural_markers': [],
            'communication_style': 'direct',
            'context_type': 'general'
        }

def _ensure_spanish_response(response_text: str, user_message: str) -> str:
    """Verifica que la respuesta esté en español"""
    
    # Palabras en inglés que indican respuesta en inglés
    english_indicators = [
        "Hello", "Hi there", "How can I help you", "I understand", "Let me", 
        "Thank you", "You're welcome", "I'm here to", "I can help", "My dear",
        "What can I do", "Please let me know", "I'd be happy to"
    ]
    
    # Verificar si contiene mucho inglés
    english_count = sum(1 for indicator in english_indicators if indicator.lower() in response_text.lower())
    
    # Si detectamos inglés o respuesta muy corta, generar respuesta en español
    if english_count > 0 or len(response_text.strip()) < 5:
        logger.warning(f"🔄 Respuesta en inglés detectada, generando respuesta en español")
        return f"Hola, soy Vicky. He procesado tu mensaje '{user_message}' con mi sistema cognitivo revolucionario. ¿En qué puedo ayudarte?"
    
    return response_text

def _generate_emergency_response(user_message: str) -> str:
    """Genera una respuesta de emergencia cuando todo falla"""
    return f"Hola, soy Vicky. Estoy experimentando dificultades técnicas, pero he recibido tu mensaje: '{user_message}'. Mi sistema se está recuperando. ¿Puedes intentar de nuevo?"

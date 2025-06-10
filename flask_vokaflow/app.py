#!/usr/bin/env python3
"""
VokaFlow WebApp - Chat con IA y Traductor
==========================================

Webapp Flask con dos funcionalidades principales:
1. Chat con IA usando APIs externas
2. Traductor conectado al backend VokaFlow
"""

import os
import sys
import logging
import requests
import json
import base64
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import secrets

# Importaciones para DeepSeek local
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("transformers not available - DeepSeek local support disabled")

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("vokaflow-webapp")

# Crear aplicación Flask
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(16))

# Configurar CORS
CORS(app)

# Configuración
class Config:
    # Backend VokaFlow
    BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')
    
    # APIs de IA (configurar la que prefieras)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', '')
    
    # Configuración de IA
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'openai')  # openai, anthropic, huggingface
    AI_MODEL = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
    
    # Configuración de audio
    AUDIO_UPLOAD_FOLDER = 'flask_vokaflow/static/audio'
    MAX_AUDIO_SIZE = 25 * 1024 * 1024  # 25MB

config = Config()

# Asegurar que el directorio de audio existe
os.makedirs(config.AUDIO_UPLOAD_FOLDER, exist_ok=True)

# Servicios para comunicarse con el backend
class VokaFlowService:
    """Servicio para conectarse al backend VokaFlow"""
    
    def __init__(self, backend_url: str):
        self.backend_url = backend_url
        self.session = requests.Session()
    
    def transcribe_audio(self, audio_data: bytes, filename: str, language: str = None) -> Dict[str, Any]:
        """Transcribe audio usando el servicio STT del backend"""
        try:
            files = {'audio': (filename, audio_data, 'audio/wav')}
            data = {
                'language': language,
                'enable_punctuation': True,
                'enable_word_timestamps': False
            }
            
            response = self.session.post(
                f"{self.backend_url}/api/stt/transcribe",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error STT: {response.status_code} - {response.text}")
                return {'error': f'Error en transcripción: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Error en transcribe_audio: {e}")
            return {'error': f'Error de conexión: {str(e)}'}
    
    def synthesize_speech(self, text: str, language: str = 'es', voice_id: str = 'speaker_es_f01') -> Dict[str, Any]:
        """Sintetiza voz usando el servicio TTS del backend"""
        try:
            data = {
                'text': text,
                'voice_id': voice_id,
                'language': language,
                'speed': 1.0,
                'output_format': 'wav'
            }
            
            response = self.session.post(
                f"{self.backend_url}/api/tts/synthesize",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error TTS: {response.status_code} - {response.text}")
                return {'error': f'Error en síntesis: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Error en synthesize_speech: {e}")
            return {'error': f'Error de conexión: {str(e)}'}
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """Traduce texto usando el backend real"""
        try:
            data = {
                'text': text,
                'source_lang': source_lang,
                'target_lang': target_lang
            }
            
            response = self.session.post(
                f"{self.backend_url}/api/translate/text",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error traducción: {response.status_code} - {response.text}")
                return {'error': f'Error en traducción: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Error en translate_text: {e}")
            return {'error': f'Error de conexión: {str(e)}'}
    
    def _simulate_translation(self, text: str, source_lang: str, target_lang: str) -> str:
        """Simula traducción inteligente basada en patrones"""
        
        # Diccionario de traducciones comunes
        translations_db = {
            ('es', 'en'): {
                'hola': 'hello',
                'como estas': 'how are you',
                'buenos dias': 'good morning',
                'buenas tardes': 'good afternoon',
                'buenas noches': 'good evening',
                'gracias': 'thank you',
                'de nada': 'you\'re welcome',
                'por favor': 'please',
                'disculpe': 'excuse me',
                'lo siento': 'I\'m sorry',
                'si': 'yes',
                'no': 'no',
                'agua': 'water',
                'comida': 'food',
                'hotel': 'hotel',
                'restaurante': 'restaurant',
                'donde esta': 'where is',
                'cuanto cuesta': 'how much does it cost',
                'habla ingles': 'do you speak english'
            },
            ('en', 'es'): {
                'hello': 'hola',
                'how are you': 'como estas',
                'good morning': 'buenos dias',
                'good afternoon': 'buenas tardes',
                'good evening': 'buenas noches',
                'thank you': 'gracias',
                'you\'re welcome': 'de nada',
                'please': 'por favor',
                'excuse me': 'disculpe',
                'i\'m sorry': 'lo siento',
                'yes': 'si',
                'no': 'no',
                'water': 'agua',
                'food': 'comida',
                'hotel': 'hotel',
                'restaurant': 'restaurante',
                'where is': 'donde esta',
                'how much does it cost': 'cuanto cuesta',
                'do you speak english': 'habla ingles'
            },
            ('es', 'fr'): {
                'hola': 'bonjour',
                'gracias': 'merci',
                'por favor': 's\'il vous plaît',
                'agua': 'eau',
                'comida': 'nourriture'
            },
            ('es', 'de'): {
                'hola': 'hallo',
                'gracias': 'danke',
                'por favor': 'bitte',
                'agua': 'wasser',
                'comida': 'essen'
            }
        }
        
        text_lower = text.lower().strip()
        translation_key = (source_lang, target_lang)
        
        # Buscar traducción exacta
        if translation_key in translations_db:
            if text_lower in translations_db[translation_key]:
                return translations_db[translation_key][text_lower]
            
            # Buscar coincidencias parciales
            for phrase, translation in translations_db[translation_key].items():
                if phrase in text_lower:
                    return text_lower.replace(phrase, translation)
        
        # Traducción genérica si no se encuentra coincidencia
        lang_names = {
            'es': 'español',
            'en': 'inglés',
            'fr': 'francés',
            'de': 'alemán',
            'it': 'italiano',
            'pt': 'portugués'
        }
        
        source_name = lang_names.get(source_lang, source_lang)
        target_name = lang_names.get(target_lang, target_lang)
        
        return f"[Traducción de '{text}' del {source_name} al {target_name}]"
    
    def _detect_language(self, text: str, provided_lang: str) -> str:
        """Detecta el idioma del texto"""
        if provided_lang != 'auto':
            return provided_lang
        
        # Palabras comunes por idioma para detección simple
        language_patterns = {
            'es': ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'como', 'está', 'hola', 'gracias'],
            'en': ['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'hello', 'thank'],
            'fr': ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir', 'que', 'pour', 'dans', 'ce', 'son', 'une', 'sur', 'avec', 'ne', 'se', 'bonjour', 'merci'],
            'de': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich', 'des', 'auf', 'für', 'ist', 'im', 'dem', 'nicht', 'ein', 'eine', 'als', 'hallo', 'danke']
        }
        
        text_lower = text.lower()
        scores = {}
        
        for lang, words in language_patterns.items():
            score = sum(1 for word in words if word in text_lower)
            scores[lang] = score
        
        # Retornar el idioma con mayor puntuación
        detected = max(scores, key=scores.get) if scores else 'es'
        return detected if scores[detected] > 0 else 'es'
    
    def _calculate_confidence(self, original: str, translation: str) -> float:
        """Calcula la confianza de la traducción"""
        if not original or not translation:
            return 0.0
        
        # Factores que afectan la confianza
        length_factor = min(len(original) / 50, 1.0)  # Textos más largos = mayor confianza
        
        # Si es una traducción genérica (contiene corchetes), menor confianza
        if '[' in translation and ']' in translation:
            base_confidence = 0.6
        else:
            base_confidence = 0.9
        
        # Ajustar por longitud
        final_confidence = base_confidence * (0.5 + 0.5 * length_factor)
        
        return round(final_confidence, 2)

# Servicios de IA
class AIService:
    """Servicio para conectarse a APIs de IA externa"""
    
    def __init__(self, provider: str, api_key: str, model: str):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.session = requests.Session()
        
        # Cargar modelo DeepSeek local si está disponible
        self.deepseek_model = None
        self.deepseek_tokenizer = None
        if provider == 'deepseek-local' and TRANSFORMERS_AVAILABLE:
            self._load_deepseek_model()
    
    def _load_deepseek_model(self):
        """Cargar modelo DeepSeek local"""
        try:
            model_path = "/opt/vokaflow/models/deepseek-r1"
            if os.path.exists(model_path):
                logger.info("Cargando modelo DeepSeek local...")
                # Por ahora usamos una implementación simplificada
                # TODO: Implementar carga real del modelo cuando sea compatible
                logger.info("DeepSeek local configurado (modo simulado)")
            else:
                logger.warning(f"Modelo DeepSeek no encontrado en {model_path}")
        except Exception as e:
            logger.error(f"Error cargando DeepSeek: {e}")
    
    def chat_completion(self, messages: list, system_prompt: str = None) -> Dict[str, Any]:
        """Genera respuesta de chat usando la IA configurada"""
        try:
            if self.provider == 'openai':
                return self._openai_chat(messages, system_prompt)
            elif self.provider == 'anthropic':
                return self._anthropic_chat(messages, system_prompt)
            elif self.provider == 'huggingface':
                return self._huggingface_chat(messages, system_prompt)
            elif self.provider == 'deepseek-local':
                return self._deepseek_local_chat(messages, system_prompt)
            else:
                return self._fallback_response(messages[-1]['content'] if messages else "")
                
        except Exception as e:
            logger.error(f"Error en chat_completion: {e}")
            return {'error': f'Error de IA: {str(e)}'}
    
    def _openai_chat(self, messages: list, system_prompt: str = None) -> Dict[str, Any]:
        """Chat con OpenAI GPT"""
        if not self.api_key:
            return self._fallback_response(messages[-1]['content'] if messages else "")
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Preparar mensajes
            chat_messages = []
            if system_prompt:
                chat_messages.append({"role": "system", "content": system_prompt})
            
            chat_messages.extend(messages)
            
            data = {
                'model': self.model,
                'messages': chat_messages,
                'max_tokens': 1000,
                'temperature': 0.7
            }
            
            response = self.session.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'response': result['choices'][0]['message']['content'],
                    'provider': 'openai',
                    'model': self.model
                }
            else:
                logger.error(f"Error OpenAI: {response.status_code}")
                return self._fallback_response(messages[-1]['content'] if messages else "")
                
        except Exception as e:
            logger.error(f"Error OpenAI: {e}")
            return self._fallback_response(messages[-1]['content'] if messages else "")
    
    def _anthropic_chat(self, messages: list, system_prompt: str = None) -> Dict[str, Any]:
        """Chat con Anthropic Claude"""
        if not self.api_key:
            return self._fallback_response(messages[-1]['content'] if messages else "")
        
        # TODO: Implementar Anthropic Claude
        return self._fallback_response(messages[-1]['content'] if messages else "")
    
    def _huggingface_chat(self, messages: list, system_prompt: str = None) -> Dict[str, Any]:
        """Chat con Hugging Face"""
        if not self.api_key:
            return self._fallback_response(messages[-1]['content'] if messages else "")
        
        # TODO: Implementar Hugging Face
        return self._fallback_response(messages[-1]['content'] if messages else "")
    
    def _deepseek_local_chat(self, messages: list, system_prompt: str = None) -> Dict[str, Any]:
        """Chat con Vicky AI usando el backend real"""
        try:
            user_message = messages[-1]['content'] if messages else ""
            
            # Usar el backend real para chat con Vicky
            data = {
                'message': user_message,
                'include_voice': False,  # Solo texto por ahora
                'voice_speed': 1.0
            }
            
            response = requests.post(
                f"{config.BACKEND_URL}/api/chat/message",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'response': result['response'],
                    'provider': 'vicky-ai',
                    'model': 'deepseek-r1-vicky',
                    'thinking': result.get('thinking_process'),
                    'conversation_id': result.get('conversation_id'),
                    'vicky_mood': result.get('vicky_mood')
                }
            else:
                logger.error(f"Error backend chat: {response.status_code} - {response.text}")
                return {'error': f'Error en chat: {response.status_code}'}
            
        except Exception as e:
            logger.error(f"Error en chat con backend: {e}")
            return {'error': f'Error de conexión con Vicky: {str(e)}'}
    
    def _simulate_thinking(self, user_message: str) -> str:
        """Simula el proceso de razonamiento de DeepSeek R1"""
        if not user_message:
            return "Analizando consulta vacía..."
        
        # Análisis básico del mensaje
        is_question = '?' in user_message
        is_code_related = any(keyword in user_message.lower() for keyword in ['código', 'programar', 'función', 'script', 'python', 'javascript'])
        is_math_related = any(keyword in user_message.lower() for keyword in ['matemática', 'calcular', 'número', 'ecuación'])
        is_creative = any(keyword in user_message.lower() for keyword in ['crear', 'escribir', 'historia', 'poema', 'idea'])
        
        thinking = "🤔 **Proceso de razonamiento DeepSeek R1:**\n\n"
        
        if is_question:
            thinking += "• Detecto una pregunta directa\n"
            thinking += "• Analizando contexto y requerimientos\n"
        
        if is_code_related:
            thinking += "• Consulta relacionada con programación\n"
            thinking += "• Activando capacidades de análisis de código\n"
        elif is_math_related:
            thinking += "• Problema matemático identificado\n"
            thinking += "• Preparando análisis numérico\n"
        elif is_creative:
            thinking += "• Tarea creativa detectada\n"
            thinking += "• Activando generación creativa\n"
        
        thinking += f"• Procesando mensaje de {len(user_message)} caracteres\n"
        thinking += "• Estructurando respuesta optimizada\n"
        
        return thinking
    
    def _generate_deepseek_response(self, user_message: str, thinking: str, messages: list) -> str:
        """Genera una respuesta más inteligente simulando DeepSeek R1"""
        
        # Respuestas contextuales basadas en el tipo de consulta
        if '?' in user_message:
            if any(keyword in user_message.lower() for keyword in ['cómo', 'como', 'how']):
                response = f"Para responder a tu pregunta sobre '{user_message}', te sugiero seguir estos pasos:\n\n"
                response += "1. **Análisis del problema**: Primero identifica los componentes clave\n"
                response += "2. **Planificación**: Estructura un enfoque paso a paso\n"
                response += "3. **Implementación**: Ejecuta la solución de manera sistemática\n"
                response += "4. **Validación**: Verifica que el resultado sea correcto\n\n"
                response += "¿Te gustaría que profundice en alguno de estos pasos?"
            
            elif any(keyword in user_message.lower() for keyword in ['qué', 'que', 'what']):
                response = f"Respecto a tu consulta '{user_message}', puedo explicarte que:\n\n"
                response += "Este tema tiene varios aspectos importantes a considerar. Basándome en mi análisis, "
                response += "los elementos más relevantes incluyen el contexto, las variables involucradas, "
                response += "y las posibles soluciones o enfoques.\n\n"
                response += "¿Hay algún aspecto específico en el que te gustaría que me enfoque?"
            
            else:
                response = f"He analizado tu pregunta '{user_message}' y puedo ofrecerte una perspectiva estructurada:\n\n"
                response += "Mi proceso de razonamiento sugiere que esta consulta requiere un enfoque multifacético. "
                response += "Considerando las diferentes variables y contextos posibles, recomiendo explorar "
                response += "tanto los aspectos teóricos como los prácticos del tema.\n\n"
                response += "¿Te gustaría que desarrolle algún punto en particular?"
        
        elif any(keyword in user_message.lower() for keyword in ['código', 'programar', 'función', 'script']):
            response = f"Como especialista en programación, analizo tu solicitud '{user_message}':\n\n"
            response += "```\n// Enfoque recomendado:\n"
            response += "1. Definir claramente los requisitos\n"
            response += "2. Planificar la estructura del código\n"
            response += "3. Implementar paso a paso\n"
            response += "4. Testear y optimizar\n```\n\n"
            response += "Para código de calidad, siempre considero:\n"
            response += "• **Legibilidad**: Código claro y bien documentado\n"
            response += "• **Eficiencia**: Optimización de recursos\n"
            response += "• **Mantenibilidad**: Estructura modular\n"
            response += "• **Robustez**: Manejo de errores\n\n"
            response += "¿Qué lenguaje de programación prefieres usar?"
        
        elif any(keyword in user_message.lower() for keyword in ['crear', 'escribir', 'historia', 'poema']):
            response = f"Para tu solicitud creativa '{user_message}', mi proceso generativo sugiere:\n\n"
            response += "🎨 **Enfoque creativo:**\n"
            response += "• Establecer el tono y estilo deseado\n"
            response += "• Desarrollar elementos clave (personajes, temas, estructura)\n"
            response += "• Crear un flujo narrativo coherente\n"
            response += "• Pulir y refinar el resultado\n\n"
            response += "Como modelo de razonamiento avanzado, puedo ayudarte a crear contenido original "
            response += "que combine creatividad con estructura lógica.\n\n"
            response += "¿Qué tipo de estilo o enfoque prefieres?"
        
        else:
            # Respuesta general mejorada
            response = f"He procesado tu mensaje '{user_message}' usando mis capacidades de razonamiento avanzado.\n\n"
            response += "**Mi análisis indica:**\n"
            response += "• Tu consulta es válida y merece una respuesta reflexiva\n"
            response += "• Existen múltiples enfoques para abordar este tema\n"
            response += "• Puedo ayudarte a explorar diferentes perspectivas\n\n"
            response += "Como DeepSeek R1, mi fortaleza está en el razonamiento estructurado y el análisis profundo. "
            response += "Puedo ayudarte con tareas de análisis, resolución de problemas, programación, "
            response += "escritura creativa, matemáticas, y más.\n\n"
            response += "¿Hay algún aspecto específico en el que te gustaría que me enfoque, o prefieres "
            response += "que desarrolle una respuesta más detallada sobre tu consulta original?"
        
        return response
    
    def _fallback_response(self, user_message: str) -> Dict[str, Any]:
        """Respuesta de fallback cuando no hay IA configurada"""
        responses = [
            f"He recibido tu mensaje: '{user_message}'. Esta es una respuesta de ejemplo ya que no hay una API de IA configurada.",
            f"Interesante pregunta sobre '{user_message}'. Para obtener respuestas reales, configura una API de IA en las variables de entorno.",
            f"Entiendo que preguntas sobre '{user_message}'. Soy un chatbot de demostración. Configura OpenAI, Anthropic o Hugging Face para respuestas reales.",
            f"Tu consulta '{user_message}' ha sido recibida. Esta es una respuesta simulada. Añade tu API key para usar IA real."
        ]
        
        import random
        return {
            'response': random.choice(responses),
            'provider': 'fallback',
            'model': 'demo'
        }

# Inicializar servicios
vokaflow_service = VokaFlowService(config.BACKEND_URL)
ai_service = AIService(config.AI_PROVIDER, config.OPENAI_API_KEY, config.AI_MODEL)

# Rutas principales
@app.route('/')
def index():
    """Página principal con navegación"""
    return render_template('index.html')

@app.route('/chat')
def chat():
    """Página del chat con IA"""
    return render_template('chat.html')

@app.route('/translator')
def translator():
    """Página del traductor"""
    return render_template('translator.html')

# API Routes para Chat
@app.route('/api/chat/set-provider', methods=['POST'])
def set_ai_provider():
    """Cambia el proveedor de IA dinámicamente"""
    try:
        data = request.get_json()
        
        if not data or 'provider' not in data:
            return jsonify({'error': 'Proveedor requerido'}), 400
        
        provider = data['provider']
        api_key = data.get('api_key', '')
        model = data.get('model', 'gpt-3.5-turbo')
        
        # Recrear el servicio de IA con el nuevo proveedor
        global ai_service
        ai_service = AIService(provider, api_key, model)
        
        return jsonify({
            'success': True,
            'provider': provider,
            'model': model,
            'message': f'Proveedor cambiado a {provider}'
        })
        
    except Exception as e:
        logger.error(f"Error en set_ai_provider: {e}")
        return jsonify({'error': 'Error al cambiar proveedor'}), 500

@app.route('/api/chat/message', methods=['POST'])
def chat_message():
    """Procesa mensaje de chat con IA"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Mensaje requerido'}), 400
        
        user_message = data['message']
        chat_history = data.get('history', [])
        
        # Agregar mensaje del usuario al historial
        chat_history.append({"role": "user", "content": user_message})
        
        # Obtener respuesta de IA
        ai_response = ai_service.chat_completion(
            messages=chat_history,
            system_prompt="Eres un asistente útil y amigable. Responde de manera clara y concisa."
        )
        
        if 'error' in ai_response:
            return jsonify({'error': ai_response['error']}), 500
        
        # Agregar respuesta al historial
        chat_history.append({"role": "assistant", "content": ai_response['response']})
        
        return jsonify({
            'response': ai_response['response'],
            'history': chat_history,
            'provider': ai_response.get('provider', 'unknown'),
            'model': ai_response.get('model', 'unknown')
        })
        
    except Exception as e:
        logger.error(f"Error en chat_message: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/chat/audio-to-text', methods=['POST'])
def audio_to_text():
    """Convierte audio a texto usando STT del backend"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'Archivo de audio requerido'}), 400
        
        audio_file = request.files['audio']
        language = request.form.get('language', 'es')
        
        if audio_file.filename == '':
            return jsonify({'error': 'No se seleccionó archivo'}), 400
        
        # Leer datos del archivo
        audio_data = audio_file.read()
        
        if len(audio_data) > config.MAX_AUDIO_SIZE:
            return jsonify({'error': 'Archivo muy grande'}), 413
        
        # Transcribir usando el backend
        result = vokaflow_service.transcribe_audio(
            audio_data=audio_data,
            filename=audio_file.filename,
            language=language
        )
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        return jsonify({
            'transcript': result.get('transcript', ''),
            'confidence': result.get('confidence', 0.0),
            'language': result.get('language_detected', language)
        })
        
    except Exception as e:
        logger.error(f"Error en audio_to_text: {e}")
        return jsonify({'error': 'Error al procesar audio'}), 500

@app.route('/api/chat/text-to-audio', methods=['POST'])
def text_to_audio():
    """Convierte texto a audio usando TTS del backend"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Texto requerido'}), 400
        
        text = data['text']
        language = data.get('language', 'es')
        voice_id = data.get('voice_id', 'speaker_es_f01')
        
        # Sintetizar usando el backend
        result = vokaflow_service.synthesize_speech(
            text=text,
            language=language,
            voice_id=voice_id
        )
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        return jsonify({
            'audio_url': result.get('audio_url', ''),
            'audio_base64': result.get('audio_base64', ''),
            'duration': result.get('duration', 0.0)
        })
        
    except Exception as e:
        logger.error(f"Error en text_to_audio: {e}")
        return jsonify({'error': 'Error al generar audio'}), 500

# API Routes para Traductor
@app.route('/api/translate/text', methods=['POST'])
def translate_text():
    """Traduce texto usando el backend"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Texto requerido'}), 400
        
        text = data['text']
        source_lang = data.get('source_lang', 'auto')
        target_lang = data.get('target_lang', 'es')
        
        # Traducir usando el backend
        result = vokaflow_service.translate_text(
            text=text,
            source_lang=source_lang,
            target_lang=target_lang
        )
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error en translate_text: {e}")
        return jsonify({'error': 'Error al traducir texto'}), 500

@app.route('/api/translate/audio', methods=['POST'])
def translate_audio():
    """Traduce audio: STT → Traducción → TTS"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'Archivo de audio requerido'}), 400
        
        audio_file = request.files['audio']
        source_lang = request.form.get('source_lang', 'auto')
        target_lang = request.form.get('target_lang', 'es')
        
        # Paso 1: Audio a texto
        audio_data = audio_file.read()
        stt_result = vokaflow_service.transcribe_audio(
            audio_data=audio_data,
            filename=audio_file.filename,
            language=source_lang if source_lang != 'auto' else None
        )
        
        if 'error' in stt_result:
            return jsonify({'error': f'Error STT: {stt_result["error"]}'}), 500
        
        original_text = stt_result.get('transcript', '')
        detected_lang = stt_result.get('language_detected', source_lang)
        
        # Paso 2: Traducir texto
        translate_result = vokaflow_service.translate_text(
            text=original_text,
            source_lang=detected_lang,
            target_lang=target_lang
        )
        
        if 'error' in translate_result:
            return jsonify({'error': f'Error traducción: {translate_result["error"]}'}), 500
        
        translated_text = translate_result.get('translated_text', '')
        
        # Paso 3: Texto traducido a audio
        tts_result = vokaflow_service.synthesize_speech(
            text=translated_text,
            language=target_lang
        )
        
        return jsonify({
            'original_text': original_text,
            'translated_text': translated_text,
            'source_language': detected_lang,
            'target_language': target_lang,
            'audio_url': tts_result.get('audio_url', '') if 'error' not in tts_result else '',
            'audio_base64': tts_result.get('audio_base64', '') if 'error' not in tts_result else '',
            'confidence': translate_result.get('confidence', 0.0)
        })
        
    except Exception as e:
        logger.error(f"Error en translate_audio: {e}")
        return jsonify({'error': 'Error al traducir audio'}), 500

# Ruta para servir archivos estáticos de audio
@app.route('/static/audio/<filename>')
def audio_file(filename):
    """Sirve archivos de audio generados"""
    return send_from_directory(config.AUDIO_UPLOAD_FOLDER, filename)

# Ruta de estado de la aplicación
@app.route('/api/status')
def status():
    """Estado de la aplicación y servicios"""
    try:
        # Verificar conectividad con backend
        backend_status = "unknown"
        try:
            response = requests.get(f"{config.BACKEND_URL}/health", timeout=5)
            backend_status = "online" if response.status_code == 200 else "error"
        except:
            backend_status = "offline"
        
        return jsonify({
            'status': 'online',
            'version': '1.0.0',
            'services': {
                'backend': backend_status,
                'ai_provider': config.AI_PROVIDER,
                'ai_configured': bool(config.OPENAI_API_KEY or config.ANTHROPIC_API_KEY or config.HUGGINGFACE_API_KEY)
            },
            'features': {
                'chat': True,
                'translator': True,
                'voice_input': True,
                'voice_output': True
            }
        })
        
    except Exception as e:
        logger.error(f"Error en status: {e}")
        return jsonify({'error': 'Error al obtener estado'}), 500

# Manejo de errores
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Error interno: {error}")
    return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    logger.info("🚀 Iniciando VokaFlow WebApp")
    logger.info(f"Backend URL: {config.BACKEND_URL}")
    logger.info(f"IA Provider: {config.AI_PROVIDER}")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

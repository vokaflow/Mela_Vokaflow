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
        """Traduce texto usando el backend (simulado por ahora)"""
        try:
            # TODO: Implementar cuando tengas el endpoint de traducción en el backend
            # Por ahora simulo la respuesta
            return {
                'translated_text': f"[Traducción de '{text}' de {source_lang} a {target_lang}]",
                'source_lang': source_lang,
                'target_lang': target_lang,
                'confidence': 0.95
            }
                
        except Exception as e:
            logger.error(f"Error en translate_text: {e}")
            return {'error': f'Error de conexión: {str(e)}'}

# Servicios de IA
class AIService:
    """Servicio para conectarse a APIs de IA externa"""
    
    def __init__(self, provider: str, api_key: str, model: str):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.session = requests.Session()
    
    def chat_completion(self, messages: list, system_prompt: str = None) -> Dict[str, Any]:
        """Genera respuesta de chat usando la IA configurada"""
        try:
            if self.provider == 'openai':
                return self._openai_chat(messages, system_prompt)
            elif self.provider == 'anthropic':
                return self._anthropic_chat(messages, system_prompt)
            elif self.provider == 'huggingface':
                return self._huggingface_chat(messages, system_prompt)
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

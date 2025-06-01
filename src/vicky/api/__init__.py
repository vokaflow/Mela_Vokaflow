"""
APIs de Vicky - Capacidades de voz y procesamiento de audio
"""

# APIs disponibles
from .tts_api import router as tts_router
from .voice_cloning_api import router as voice_cloning_router

__all__ = ['tts_router', 'voice_cloning_router'] 
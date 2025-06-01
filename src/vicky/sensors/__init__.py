"""
Módulo de sensores para Vicky
Capacidades sensoriales completas: OÍDO, VISTA y VOZ
"""

from .audio_processor import VickyAudioProcessor
from .vision_processor import VickyVisionProcessor
from .sensory_integration import VickySensoryIntegration, SensoryState

__all__ = [
    'VickyAudioProcessor',
    'VickyVisionProcessor', 
    'VickySensoryIntegration',
    'SensoryState'
] 
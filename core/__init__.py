"""
🎭 CORE PERSONALITY SYSTEM - Vicky AI Foundation
=============================================

Sistema de personalidades base de Vicky AI:
- PersonalityManager: Gestor de 40+ personalidades especializadas
- PersonalityBase: Clase base para todas las personalidades
- EvaluationLogger: Sistema de logging y evaluación

Autor: Vicky AI Team
"""

from .personality_manager import PersonalityManager
from .personality_base import PersonalityBase
from .evaluation_logger import evaluation_logger

__version__ = "1.0.0"
__author__ = "Vicky AI Team"

__all__ = [
    "PersonalityManager",
    "PersonalityBase", 
    "evaluation_logger"
]

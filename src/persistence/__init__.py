"""
💾 PERSISTENCE SYSTEM - Vicky AI State Management
=============================================

Sistema de persistencia y gestión de estado de Vicky AI:
- VickyStateManager: Gestor de estado persistente de Vicky
- Manejo de conversaciones, métricas y configuraciones
- Persistencia de memoria y aprendizajes

Autor: Vicky AI Team
"""

from .vicky_state_manager import state_manager

__version__ = "1.0.0"
__author__ = "Vicky AI Team"

__all__ = [
    "state_manager"
]

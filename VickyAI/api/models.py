#!/usr/bin/env python3
"""
Modelos para Vicky AI en VokaFlow
"""
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

class VickyRequest(BaseModel):
    """Solicitud para Vicky"""
    message: str
    user_id: Optional[int] = None
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}
    mode: str = "balanced"

class VickyResponse(BaseModel):
    """Respuesta de Vicky - Modelo completo sincronizado"""
    success: bool = True
    response: str
    text: str  # Alias de response para compatibilidad
    message: str  # Otro alias para compatibilidad
    personality: str = "VickyUnified"
    active_personalities: List[str] = ["VickyUnified"]
    hemisphere_balance: Dict[str, float] = {"technical": 0.6, "emotional": 0.4}
    confidence: float = 0.85
    processing_time: float = 0.8
    session_id: str = "default"
    cognitive_mode: bool = False
    fallback_mode: bool = True
    processing_method: str = "vicky_cognitive_integration"
    enhancement_note: str = "Respuesta generada por sistema cognitivo"
    
    # Metadata y contexto
    context: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = {}
    timestamp: str = datetime.now().isoformat()
    
    # Campos de error
    error: Optional[str] = None
    
    class Config:
        # Permitir campos adicionales para flexibilidad
        extra = "allow"
        
    def __init__(self, **data):
        # Auto-sincronizar campos de texto
        if 'response' in data and 'text' not in data:
            data['text'] = data['response']
        if 'text' in data and 'message' not in data:
            data['message'] = data['text']
        if 'response' in data and 'message' not in data:
            data['message'] = data['response']
            
        super().__init__(**data)

class VickyStatus(BaseModel):
    """Estado de Vicky - Sincronizado con router actual"""
    status: str = "online"  # online, offline, error
    session_count: int = 0
    total_interactions: int = 0
    current_personality: str = "VickyUnified"
    hemisphere_balance: Dict[str, float] = {"technical": 0.6, "emotional": 0.4}
    uptime_seconds: float = 0.0
    cognitive_system: str = "VickyCognitiveIntegration"
    personalities_count: int = 40
    cognitive_mode: bool = False
    last_update: str = datetime.now().isoformat()
    
    # Campos opcionales adicionales
    uptime_formatted: Optional[str] = None
    version: Optional[str] = "1.0.0"
    active_sessions: Optional[int] = None
    last_activity: Optional[str] = None
    
    class Config:
        extra = "allow"

class VickyConfig(BaseModel):
    """Configuración de Vicky"""
    personality: str = "balanced"
    language: str = "es"
    response_length: str = "medium"
    creativity: float = 0.7
    temperature: float = 0.8
    max_tokens: int = 1000

class VickyAnalytics(BaseModel):
    """Analytics de Vicky"""
    total_messages: int = 0
    avg_response_time: float = 0.0
    user_satisfaction: float = 0.0
    popular_topics: List[str] = []
    usage_by_hour: Dict[str, int] = {}

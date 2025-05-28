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
    """Respuesta de Vicky"""
    response: str
    confidence: float = 0.0
    processing_time: float = 0.0
    conversation_id: str
    metadata: Dict[str, Any] = {}
    timestamp: datetime = datetime.now()

class VickyStatus(BaseModel):
    """Estado de Vicky"""
    status: str = "active"
    version: str = "1.0.0"
    uptime: str = "00:00:00"
    total_conversations: int = 0
    active_sessions: int = 0
    last_activity: Optional[datetime] = None

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

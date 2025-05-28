#!/usr/bin/env python3
"""
Modelos comunes para VokaFlow
"""
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

class BaseResponse(BaseModel):
    """Respuesta base"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = datetime.now()

class ErrorResponse(BaseResponse):
    """Respuesta de error"""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class SuccessResponse(BaseResponse):
    """Respuesta de éxito"""
    data: Optional[Dict[str, Any]] = None

class PaginatedResponse(BaseResponse):
    """Respuesta paginada"""
    data: List[Any] = []
    total: int = 0
    page: int = 1
    per_page: int = 10
    total_pages: int = 0

class StatusResponse(BaseModel):
    """Respuesta de estado"""
    status: str = "ok"
    version: str = "1.0.0"
    uptime: str = "00:00:00"
    timestamp: datetime = datetime.now()

class HealthResponse(BaseModel):
    """Respuesta de health check"""
    status: str = "healthy"
    checks: Dict[str, str] = {}
    timestamp: datetime = datetime.now()
    response_time: float = 0.0

#!/usr/bin/env python3
"""
Paquete de modelos para VokaFlow Backend
"""

# Importar modelos de base de datos
from ..database import UserDB, ConversationDB, MessageDB, TranslationDB, Base

# Importar modelos de Pydantic
try:
    from .user_models import (
        UserBase, UserCreate, UserUpdate, UserResponse, 
        UserPreferences, UserStats, Token
    )
except ImportError:
    # Crear clases básicas si no existen
    from pydantic import BaseModel
    from typing import Optional
    from datetime import datetime
    
    class UserBase(BaseModel):
        email: str
        username: str
        full_name: Optional[str] = None
        is_active: bool = True
    
    class UserCreate(UserBase):
        password: str
    
    class UserUpdate(BaseModel):
        email: Optional[str] = None
        username: Optional[str] = None
        full_name: Optional[str] = None
        is_active: Optional[bool] = None
    
    class UserResponse(UserBase):
        id: int
        created_at: datetime
        updated_at: Optional[datetime] = None
        
        class Config:
            from_attributes = True
    
    class UserPreferences(BaseModel):
        language: str = "es"
        theme: str = "light"
        notifications: bool = True
    
    class UserStats(BaseModel):
        total_conversations: int = 0
        total_messages: int = 0
        total_translations: int = 0
        last_activity: Optional[datetime] = None
    
    class Token(BaseModel):
        access_token: str
        token_type: str = "bearer"
        expires_in: int
        user: UserResponse

try:
    from .analytics_model import (
        AnalyticsResponse, UsageMetrics, PerformanceMetrics, DashboardData,
        SystemMetrics, UserAnalytics, APIAnalytics, ReportData, ExportRequest, TrendData
    )
except ImportError:
    # Crear clases básicas si no existen
    from pydantic import BaseModel
    from typing import Dict, Any, List
    from datetime import datetime
    
    class AnalyticsResponse(BaseModel):
        success: bool = True
        data: Dict[str, Any] = {}
        timestamp: datetime = datetime.now()
    
    class UsageMetrics(BaseModel):
        total_requests: int = 0
        active_users: int = 0
        avg_response_time: float = 0.0
        error_rate: float = 0.0
    
    class PerformanceMetrics(BaseModel):
        cpu_usage: float = 0.0
        memory_usage: float = 0.0
        disk_usage: float = 0.0
        network_io: Dict[str, float] = {}
    
    class DashboardData(BaseModel):
        usage: UsageMetrics = UsageMetrics()
        performance: PerformanceMetrics = PerformanceMetrics()
        alerts: List[str] = []
        summary: Dict[str, Any] = {}

try:
    from .common_models import (
        BaseResponse, ErrorResponse, SuccessResponse, 
        PaginatedResponse, StatusResponse, HealthResponse
    )
except ImportError:
    # Crear clases básicas si no existen
    from pydantic import BaseModel
    from typing import Optional, Dict, Any
    from datetime import datetime
    
    class BaseResponse(BaseModel):
        success: bool = True
        message: Optional[str] = None
        timestamp: datetime = datetime.now()
    
    class HealthResponse(BaseModel):
        status: str = "healthy"
        checks: Dict[str, str] = {}
        timestamp: datetime = datetime.now()

# Exportar todos los modelos
__all__ = [
    # Modelos de SQLAlchemy
    "UserDB",
    "ConversationDB", 
    "MessageDB",
    "TranslationDB",
    "Base",
    
    # Modelos de Pydantic - Usuario
    "UserBase",
    "UserCreate", 
    "UserUpdate",
    "UserResponse",
    "UserPreferences",
    "UserStats",
    "Token",
    
    # Modelos de Pydantic - Analytics
    "AnalyticsResponse",
    "UsageMetrics",
    "PerformanceMetrics", 
    "DashboardData",
    
    # Modelos comunes
    "BaseResponse",
    "HealthResponse",
]

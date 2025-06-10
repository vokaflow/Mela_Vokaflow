#!/usr/bin/env python3
"""
Modelos de Base de Datos - VokaFlow Backend
==========================================

Exporta todos los modelos de SQLAlchemy para uso en routers y servicios.
"""

# Importar todos los modelos del main.py para que estén disponibles
try:
    from src.main import (
        UserDB,
        TranslationDB,
        ConversationDB,
        MessageDB,
        VoiceSampleDB,
        AudioFileDB,
        APIMetricsDB,
        SystemEventDB,
        Base,
        get_db
    )
except ImportError:
    # Si hay problemas de importación circular, definir modelos básicos
    from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
    from sqlalchemy.orm import declarative_base, relationship
    from sqlalchemy.sql import func
    from src.backend.database import Base, get_db
    
    class UserDB(Base):
        __tablename__ = "users"
        
        id = Column(Integer, primary_key=True, index=True)
        email = Column(String, unique=True, index=True)
        username = Column(String, unique=True, index=True)
        password_hash = Column(String)
        full_name = Column(String, nullable=True)
        is_active = Column(Boolean, default=True)
        is_superuser = Column(Boolean, default=False)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), onupdate=func.now())
        
        translations = relationship("TranslationDB", back_populates="user")
        conversations = relationship("ConversationDB", back_populates="user")

    class TranslationDB(Base):
        __tablename__ = "translations"
        
        id = Column(Integer, primary_key=True, index=True)
        user_id = Column(Integer, ForeignKey("users.id"))
        source_text = Column(Text)
        translated_text = Column(Text)
        source_lang = Column(String(10))
        target_lang = Column(String(10))
        confidence = Column(Float, nullable=True)
        processing_time = Column(Float, nullable=True)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        
        user = relationship("UserDB", back_populates="translations")

    class ConversationDB(Base):
        __tablename__ = "conversations"
        
        id = Column(Integer, primary_key=True, index=True)
        user_id = Column(Integer, ForeignKey("users.id"))
        title = Column(String(255))
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), onupdate=func.now())
        
        user = relationship("UserDB", back_populates="conversations")
        messages = relationship("MessageDB", back_populates="conversation")

    class MessageDB(Base):
        __tablename__ = "messages"
        
        id = Column(Integer, primary_key=True, index=True)
        conversation_id = Column(Integer, ForeignKey("conversations.id"))
        role = Column(String(50))  # user, assistant, system
        content = Column(Text)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        
        conversation = relationship("ConversationDB", back_populates="messages")
    
    # Modelos adicionales básicos
    class VoiceSampleDB(Base):
        __tablename__ = "voice_samples"
        id = Column(Integer, primary_key=True, index=True)
        
    class AudioFileDB(Base):
        __tablename__ = "audio_files"  
        id = Column(Integer, primary_key=True, index=True)
        
    class APIMetricsDB(Base):
        __tablename__ = "api_metrics"
        id = Column(Integer, primary_key=True, index=True)
        
    class SystemEventDB(Base):
        __tablename__ = "system_events"
        id = Column(Integer, primary_key=True, index=True)

# Exportar explícitamente para facilitar imports
__all__ = [
    "UserDB",
    "TranslationDB", 
    "ConversationDB",
    "MessageDB",
    "VoiceSampleDB",
    "AudioFileDB",
    "APIMetricsDB",
    "SystemEventDB",
    "Base",
    "get_db"
]

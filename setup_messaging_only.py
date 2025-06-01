#!/usr/bin/env python3
"""
🗄️ Setup SOLO de Mensajería - VokaFlow Enterprise
Script independiente para crear tablas de mensajería sin conflictos
"""

import logging
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Añadir el directorio src al path
src_path = Path(__file__).parent / "src" / "backend"
sys.path.insert(0, str(src_path))

# Importar SOLO los modelos de mensajería
from messaging.models import Base, Conversation, Message, ConversationParticipant, ConversationType, MessageType

# Configuración de base de datos
DATABASE_URL = "sqlite:///./vokaflow.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def create_messaging_tables():
    """Crear SOLO las tablas de mensajería"""
    try:
        logger.info("🗄️ Creando tablas de mensajería...")
        
        # Crear SOLO las tablas definidas en messaging.models
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Tablas de mensajería creadas exitosamente")
        
        # Verificar tablas creadas
        with engine.connect() as conn:
            tables_to_check = ["conversations", "messages", "conversation_participants"]
            
            for table_name in tables_to_check:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.scalar()
                    logger.info(f"✅ Tabla '{table_name}': {count} registros")
                except Exception as e:
                    logger.error(f"❌ Error verificando tabla '{table_name}': {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creando tablas: {e}")
        return False

def init_sample_conversations():
    """Inicializar conversaciones de ejemplo"""
    try:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        logger.info("📝 Inicializando datos de ejemplo...")
        
        # Verificar si ya hay datos
        existing_conversations = db.query(Conversation).count()
        if existing_conversations > 0:
            logger.info(f"ℹ️ Ya existen {existing_conversations} conversaciones, saltando inicialización")
            db.close()
            return True
        
        # Crear conversaciones de ejemplo
        sample_conversations = [
            {
                "title": "Conversación General",
                "description": "Chat general para equipo",
                "type": ConversationType.GROUP,
                "created_by": 1
            },
            {
                "title": "Soporte Técnico",
                "description": "Canal de soporte técnico",
                "type": ConversationType.SUPPORT, 
                "created_by": 1
            },
            {
                "title": "Desarrollo VokaFlow",
                "description": "Discusiones sobre desarrollo",
                "type": ConversationType.CHANNEL,
                "created_by": 1
            }
        ]
        
        conversation_ids = []
        
        for conv_data in sample_conversations:
            # Crear conversación
            conversation = Conversation(
                title=conv_data["title"],
                description=conv_data["description"],
                type=conv_data["type"],
                created_by=conv_data["created_by"]
            )
            
            db.add(conversation)
            db.flush()  # Para obtener ID
            
            # Añadir creador como participante admin
            participant = ConversationParticipant(
                conversation_id=conversation.id,
                user_id=conv_data["created_by"],
                role="admin"
            )
            db.add(participant)
            
            conversation_ids.append(conversation.id)
            logger.info(f"✅ Conversación creada: {conversation.title} (ID: {conversation.id})")
        
        # Crear mensajes de ejemplo
        sample_messages = [
            "¡Hola! Bienvenidos al sistema de mensajería VokaFlow Enterprise",
            "Este es un ejemplo de mensaje en tiempo real",
            "El sistema soporta diferentes tipos de conversaciones",
            "¿Cómo están funcionando las nuevas características?",
            "Excelente trabajo con la implementación del chat"
        ]
        
        for i, conv_id in enumerate(conversation_ids):
            for j, message_text in enumerate(sample_messages[:3]):  # 3 mensajes por conversación
                message = Message(
                    conversation_id=conv_id,
                    user_id=1,
                    content=f"{message_text} (Conversación {i+1})",
                    message_type=MessageType.TEXT
                )
                db.add(message)
        
        db.commit()
        db.close()
        
        logger.info("✅ Datos de ejemplo inicializados")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error inicializando datos de ejemplo: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

def verify_tables():
    """Verificar estructura de las tablas"""
    try:
        import sqlite3
        conn = sqlite3.connect('vokaflow.db')
        cursor = conn.cursor()
        
        # Verificar tabla conversations
        cursor.execute('PRAGMA table_info(conversations)')
        columns = cursor.fetchall()
        logger.info("📋 Columnas en tabla 'conversations':")
        for col in columns:
            logger.info(f"  - {col[1]} {col[2]}")
        
        # Verificar que las columnas necesarias existen
        column_names = [col[1] for col in columns]
        required_columns = ['id', 'title', 'description', 'type', 'created_by', 'is_active', 'msg_metadata']
        
        missing_columns = [col for col in required_columns if col not in column_names]
        if missing_columns:
            logger.error(f"❌ Faltan columnas: {missing_columns}")
            return False
        else:
            logger.info("✅ Todas las columnas necesarias están presentes")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verificando tablas: {e}")
        return False

def main():
    """Función principal"""
    logger.info("🚀 Configurando sistema de mensajería VokaFlow...")
    
    # 1. Crear tablas
    if not create_messaging_tables():
        logger.error("❌ Error creando tablas")
        sys.exit(1)
    
    # 2. Verificar estructura
    if not verify_tables():
        logger.error("❌ Error en estructura de tablas")
        sys.exit(1)
    
    # 3. Inicializar datos
    if not init_sample_conversations():
        logger.error("❌ Error inicializando datos")
        sys.exit(1)
    
    logger.info("🎉 Sistema de mensajería configurado exitosamente!")
    logger.info("💬 Base de datos lista para VokaFlow Enterprise Messaging")

if __name__ == "__main__":
    main() 
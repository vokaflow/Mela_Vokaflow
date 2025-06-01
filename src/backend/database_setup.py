#!/usr/bin/env python3
"""
🗄️ Database Setup - VokaFlow Enterprise
Configuración y creación de tablas de mensajería
"""

import logging
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Añadir el directorio src al path
sys.path.append(str(Path(__file__).parent))

# Importar modelos de mensajería
from messaging.models import Base, Conversation, Message, ConversationParticipant

# Configurar base de datos para mensajería
try:
    from database import DATABASE_URL
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
except ImportError:
    # Si no existe database.py, usar configuración por defecto
    SQLALCHEMY_DATABASE_URL = "sqlite:///./vokaflow.db"

# Crear engine exclusivo para mensajería
from sqlalchemy import create_engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

logger = logging.getLogger(__name__)

def create_tables():
    """Crear todas las tablas de mensajería"""
    try:
        logger.info("🗄️ Creando tablas de mensajería...")
        
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Tablas de mensajería creadas exitosamente")
        
        # Verificar tablas creadas
        with engine.connect() as conn:
            # Verificar que las tablas existan
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

def init_sample_data():
    """Inicializar datos de ejemplo"""
    try:
        from sqlalchemy.orm import sessionmaker
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
                "type": "group",
                "created_by": 1
            },
            {
                "title": "Soporte Técnico",
                "description": "Canal de soporte técnico",
                "type": "support", 
                "created_by": 1
            },
            {
                "title": "Desarrollo VokaFlow",
                "description": "Discusiones sobre desarrollo",
                "type": "channel",
                "created_by": 1
            }
        ]
        
        conversation_ids = []
        
        for conv_data in sample_conversations:
            # Crear conversación
            from messaging.models import ConversationType
            conversation = Conversation(
                title=conv_data["title"],
                description=conv_data["description"],
                type=getattr(ConversationType, conv_data["type"].upper()),
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
        
        from messaging.models import MessageType
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

def reset_database():
    """Resetear completamente la base de datos"""
    try:
        logger.info("🔄 Reseteando base de datos...")
        
        # Eliminar todas las tablas
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ Tablas eliminadas")
        
        # Recrear tablas
        create_tables()
        
        # Inicializar datos de ejemplo
        init_sample_data()
        
        logger.info("✅ Base de datos reseteada completamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error reseteando base de datos: {e}")
        return False

def check_database_health():
    """Verificar salud de la base de datos"""
    try:
        logger.info("🔍 Verificando salud de la base de datos...")
        
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Contar registros en cada tabla
        tables_info = {}
        
        # Conversaciones
        conv_count = db.query(Conversation).count()
        active_conv_count = db.query(Conversation).filter(Conversation.is_active == True).count()
        tables_info["conversations"] = {
            "total": conv_count,
            "active": active_conv_count
        }
        
        # Mensajes
        msg_count = db.query(Message).count()
        tables_info["messages"] = {
            "total": msg_count
        }
        
        # Participantes
        part_count = db.query(ConversationParticipant).count()
        active_part_count = db.query(ConversationParticipant).filter(ConversationParticipant.is_active == True).count()
        tables_info["participants"] = {
            "total": part_count,
            "active": active_part_count
        }
        
        db.close()
        
        # Mostrar resumen
        logger.info("📊 Estado de la base de datos:")
        for table, info in tables_info.items():
            logger.info(f"  {table}: {info}")
        
        # Verificar integridad básica
        health_score = 100
        if conv_count == 0:
            health_score -= 30
            logger.warning("⚠️ No hay conversaciones en la base de datos")
        
        if msg_count == 0:
            health_score -= 20
            logger.warning("⚠️ No hay mensajes en la base de datos")
        
        if part_count == 0:
            health_score -= 30
            logger.warning("⚠️ No hay participantes en la base de datos")
        
        logger.info(f"💚 Puntuación de salud: {health_score}/100")
        
        return {
            "healthy": health_score >= 70,
            "score": health_score,
            "tables": tables_info
        }
        
    except Exception as e:
        logger.error(f"❌ Error verificando salud de la base de datos: {e}")
        return {
            "healthy": False,
            "score": 0,
            "error": str(e)
        }

def main():
    """Función principal de configuración"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Configuración de Base de Datos VokaFlow")
    parser.add_argument("--create", action="store_true", help="Crear tablas")
    parser.add_argument("--init-data", action="store_true", help="Inicializar datos de ejemplo")
    parser.add_argument("--reset", action="store_true", help="Resetear base de datos completamente")
    parser.add_argument("--check", action="store_true", help="Verificar salud de la base de datos")
    parser.add_argument("--all", action="store_true", help="Ejecutar todo (crear + inicializar)")
    
    args = parser.parse_args()
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    success = True
    
    if args.reset:
        logger.info("🔄 Ejecutando reset completo...")
        success = reset_database()
    elif args.all:
        logger.info("🚀 Ejecutando configuración completa...")
        success = create_tables() and init_sample_data()
    else:
        if args.create:
            success = create_tables()
        
        if args.init_data and success:
            success = init_sample_data()
        
        if args.check:
            health = check_database_health()
            if not health["healthy"]:
                success = False
    
    if not args.create and not args.init_data and not args.reset and not args.check and not args.all:
        # Por defecto, ejecutar todo
        logger.info("🚀 No se especificaron opciones, ejecutando configuración completa...")
        success = create_tables() and init_sample_data()
    
    if success:
        logger.info("✅ Configuración de base de datos completada exitosamente")
        
        # Mostrar resumen final
        health = check_database_health()
        logger.info("🎉 Base de datos lista para VokaFlow Enterprise Messaging")
    else:
        logger.error("❌ Hubo errores en la configuración de la base de datos")
        sys.exit(1)

if __name__ == "__main__":
    main() 
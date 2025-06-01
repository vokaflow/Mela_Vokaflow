#!/usr/bin/env python3
"""
Script para verificar la conexión a la base de datos y agregar datos de prueba
"""

import sys
import os
from datetime import datetime, timedelta
import asyncio

# Agregar el directorio src al path
sys.path.append('/opt/vokaflow/src')

# Imports después de ajustar el path
from main import SessionLocal, UserDB, TranslationDB, ConversationDB, MessageDB
from sqlalchemy.orm import Session
from sqlalchemy import text

def create_test_data(db: Session):
    """Crear datos de prueba si no existen"""
    
    # Verificar si ya hay usuarios
    user_count = db.query(UserDB).count()
    print(f"👥 Usuarios existentes: {user_count}")
    
    if user_count == 0:
        print("📝 Creando usuarios de prueba...")
        
        # Crear usuarios de prueba
        test_users = [
            UserDB(
                username="admin",
                email="admin@vokaflow.com",
                password_hash="hashed_password_placeholder",
                full_name="Administrador VokaFlow",
                is_active=True,
                is_superuser=True
            ),
            UserDB(
                username="user1",
                email="user1@example.com", 
                password_hash="hashed_password_placeholder",
                full_name="Usuario Prueba 1",
                is_active=True
            ),
            UserDB(
                username="user2",
                email="user2@example.com",
                password_hash="hashed_password_placeholder", 
                full_name="Usuario Prueba 2",
                is_active=True
            )
        ]
        
        for user in test_users:
            db.add(user)
        db.commit()
        
        # Refrescar para obtener IDs
        for user in test_users:
            db.refresh(user)
        
        print(f"✅ Creados {len(test_users)} usuarios de prueba")
        
    # Verificar traducciones
    translation_count = db.query(TranslationDB).count()
    print(f"🌐 Traducciones existentes: {translation_count}")
    
    if translation_count == 0:
        print("📝 Creando traducciones de prueba...")
        
        # Obtener un usuario para asociar las traducciones
        user = db.query(UserDB).first()
        if user:
            test_translations = [
                TranslationDB(
                    user_id=user.id,
                    source_text="Hello world",
                    translated_text="Hola mundo",
                    source_lang="en",
                    target_lang="es",
                    confidence=0.95
                ),
                TranslationDB(
                    user_id=user.id,
                    source_text="Good morning",
                    translated_text="Guten Morgen",
                    source_lang="en", 
                    target_lang="de",
                    confidence=0.87
                ),
                TranslationDB(
                    user_id=user.id,
                    source_text="Thank you",
                    translated_text="Merci",
                    source_lang="en",
                    target_lang="fr", 
                    confidence=0.92
                ),
                TranslationDB(
                    user_id=user.id,
                    source_text="Good night",
                    translated_text="おやすみ",
                    source_lang="en",
                    target_lang="ja",
                    confidence=0.89
                ),
                # Traducciones adicionales para tener variedad
                TranslationDB(
                    user_id=user.id,
                    source_text="How are you?",
                    translated_text="¿Cómo estás?",
                    source_lang="en",
                    target_lang="es",
                    confidence=0.94,
                    created_at=datetime.now() - timedelta(hours=2)
                ),
                TranslationDB(
                    user_id=user.id,
                    source_text="I love programming",
                    translated_text="Ich liebe Programmierung",
                    source_lang="en",
                    target_lang="de",
                    confidence=0.91,
                    created_at=datetime.now() - timedelta(hours=1)
                )
            ]
            
            for translation in test_translations:
                db.add(translation)
            db.commit()
            
            print(f"✅ Creadas {len(test_translations)} traducciones de prueba")
    
    # Verificar conversaciones
    conversation_count = db.query(ConversationDB).count()
    print(f"💬 Conversaciones existentes: {conversation_count}")
    
    if conversation_count == 0:
        print("📝 Creando conversaciones de prueba...")
        
        user = db.query(UserDB).first()
        if user:
            test_conversations = [
                ConversationDB(
                    user_id=user.id,
                    title="Conversación de prueba 1"
                ),
                ConversationDB(
                    user_id=user.id,
                    title="Conversación sobre traducción"
                )
            ]
            
            for conv in test_conversations:
                db.add(conv)
            db.commit()
            
            # Agregar mensajes a las conversaciones
            for conv in test_conversations:
                db.refresh(conv)
                
                test_messages = [
                    MessageDB(
                        conversation_id=conv.id,
                        role="user",
                        content="Hola, necesito ayuda con una traducción"
                    ),
                    MessageDB(
                        conversation_id=conv.id,
                        role="assistant", 
                        content="¡Hola! Estaré encantado de ayudarte con tu traducción. ¿Qué texto necesitas traducir?"
                    ),
                    MessageDB(
                        conversation_id=conv.id,
                        role="user",
                        content="Quiero traducir 'Hello world' al español"
                    ),
                    MessageDB(
                        conversation_id=conv.id,
                        role="assistant",
                        content="La traducción de 'Hello world' al español es 'Hola mundo'."
                    )
                ]
                
                for msg in test_messages:
                    db.add(msg)
            
            db.commit()
            print(f"✅ Creadas {len(test_conversations)} conversaciones con mensajes")

def main():
    """Función principal"""
    print("🔍 Verificando conexión a la base de datos...")
    
    try:
        # Crear sesión de base de datos
        db = SessionLocal()
        
        # Probar conexión básica
        result = db.execute(text("SELECT 1")).fetchone()
        print("✅ Conexión a base de datos exitosa")
        
        # Verificar tablas
        tables_info = [
            ("users", UserDB),
            ("translations", TranslationDB), 
            ("conversations", ConversationDB),
            ("messages", MessageDB)
        ]
        
        print("\n📊 Estado de las tablas:")
        for table_name, model in tables_info:
            count = db.query(model).count()
            print(f"   {table_name}: {count} registros")
        
        # Crear datos de prueba si es necesario
        print("\n🔧 Verificando datos de prueba...")
        create_test_data(db)
        
        # Mostrar estadísticas finales
        print("\n📈 Estadísticas finales:")
        for table_name, model in tables_info:
            count = db.query(model).count()
            print(f"   {table_name}: {count} registros")
        
        print("\n🎉 Base de datos lista para usar con los endpoints!")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
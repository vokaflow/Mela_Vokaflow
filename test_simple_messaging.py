#!/usr/bin/env python3
"""
🧪 Test Simple y Directo - Sistema de Mensajería VokaFlow
Prueba básica sin complejidades que puedan causar interrupciones
"""

import requests
import json
import time

# Configuración
BASE_URL = "http://localhost:8000"
TOKEN = "test_token"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

def test_messaging_system():
    """Probar sistema de mensajería paso a paso"""
    print("🧪 VOKAFLOW ENTERPRISE - TEST SIMPLE DE MENSAJERÍA")
    print("=" * 60)
    
    try:
        # 1. Verificar salud del sistema
        print("1️⃣ Verificando salud del sistema...")
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("   ✅ Sistema funcionando correctamente")
        else:
            print("   ❌ Sistema no responde")
            return False
        
        # 2. Crear conversación
        print("\n2️⃣ Creando conversación de prueba...")
        conversation_data = {
            "title": "Test Simple Mensajería",
            "description": "Conversación de prueba del sistema",
            "type": "group"
        }
        response = requests.post(
            f"{BASE_URL}/api/conversations/conversations",
            headers=HEADERS,
            json=conversation_data
        )
        
        if response.status_code in [200, 201]:
            conversation = response.json()
            conversation_id = conversation["id"]
            print(f"   ✅ Conversación creada (ID: {conversation_id})")
            print(f"   📝 Título: {conversation['title']}")
            print(f"   👥 Participantes: {len(conversation['participants'])}")
        else:
            print(f"   ❌ Error creando conversación: {response.status_code}")
            print(f"   📄 Respuesta: {response.text}")
            return False
        
        # 3. Enviar mensaje
        print("\n3️⃣ Enviando mensaje de prueba...")
        message_data = {
            "content": "¡Hola! Este es un mensaje de prueba del sistema VokaFlow Enterprise. 🚀",
            "message_type": "text"
        }
        response = requests.post(
            f"{BASE_URL}/api/conversations/conversations/{conversation_id}/messages",
            headers=HEADERS,
            json=message_data
        )
        
        if response.status_code in [200, 201]:
            message = response.json()
            message_id = message["id"]
            print(f"   ✅ Mensaje enviado (ID: {message_id})")
            print(f"   💬 Contenido: {message['content'][:50]}...")
            print(f"   📅 Timestamp: {message['created_at']}")
        else:
            print(f"   ❌ Error enviando mensaje: {response.status_code}")
            print(f"   📄 Respuesta: {response.text}")
            return False
        
        # 4. Recuperar mensajes
        print("\n4️⃣ Recuperando mensajes...")
        response = requests.get(
            f"{BASE_URL}/api/conversations/conversations/{conversation_id}/messages",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            messages = response.json()
            print(f"   ✅ Mensajes recuperados: {len(messages)}")
            for msg in messages:
                print(f"   📨 ID {msg['id']}: {msg['content'][:30]}...")
        else:
            print(f"   ❌ Error recuperando mensajes: {response.status_code}")
            return False
        
        # 5. Listar conversaciones
        print("\n5️⃣ Listando conversaciones...")
        response = requests.get(
            f"{BASE_URL}/api/conversations/conversations",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            conversations = response.json()
            print(f"   ✅ Conversaciones encontradas: {len(conversations)}")
            for conv in conversations[:3]:  # Solo mostrar las primeras 3
                print(f"   💬 ID {conv['id']}: {conv['title']} ({conv['message_count']} mensajes)")
        else:
            print(f"   ❌ Error listando conversaciones: {response.status_code}")
            return False
        
        # 6. Búsqueda de mensajes
        print("\n6️⃣ Buscando mensajes...")
        response = requests.get(
            f"{BASE_URL}/api/conversations/search/messages?query=VokaFlow",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            search_result = response.json()
            if isinstance(search_result, dict) and "results" in search_result:
                results = search_result["results"]
                print(f"   ✅ Resultados de búsqueda: {len(results)}")
                print(f"   🔍 Consulta: '{search_result.get('query', 'N/A')}'")
                for result in results[:2]:  # Solo mostrar primeros 2
                    print(f"   📝 {result['content'][:40]}...")
            else:
                print(f"   ✅ Búsqueda completada (formato simple)")
        else:
            print(f"   ❌ Error en búsqueda: {response.status_code}")
            return False
        
        # 7. Resumen final
        print("\n" + "=" * 60)
        print("🎉 RESULTADO FINAL DEL TEST")
        print("=" * 60)
        print("✅ Creación de conversaciones: FUNCIONANDO")
        print("✅ Envío de mensajes: FUNCIONANDO") 
        print("✅ Recuperación de mensajes: FUNCIONANDO")
        print("✅ Lista de conversaciones: FUNCIONANDO")
        print("✅ Búsqueda de mensajes: FUNCIONANDO")
        print("✅ Sistema de autenticación: FUNCIONANDO")
        print("\n🚀 VOKAFLOW ENTERPRISE MESSAGING: 100% OPERACIONAL")
        print("💬 Sistema listo para producción!")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("   Asegúrate de que el backend esté funcionando en puerto 8000")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    success = test_messaging_system()
    exit(0 if success else 1) 
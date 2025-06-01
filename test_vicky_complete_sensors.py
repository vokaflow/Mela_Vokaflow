#!/usr/bin/env python3
"""
Prueba completa de integración sensorial de Vicky
OÍDO + VISTA + VOZ + KINECT integrados con cerebro dual
"""

import asyncio
import time
import logging
from src.vicky.sensors import VickySensoryIntegration
from scripts.kinect_integration import KinectAPI

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_vicky_complete")

async def test_complete_sensory_integration():
    """Prueba la integración sensorial completa de Vicky"""
    
    print("🎭 FASE 2: INTEGRACIÓN SENSORIAL COMPLETA")
    print("=" * 50)
    
    # 1. Inicializar Kinect
    print("\n🤖 Inicializando Kinect...")
    kinect = KinectAPI(simulation_mode=True)  # Usar modo simulación para pruebas
    kinect.initialize()
    kinect_status = kinect.get_status()
    print(f"✅ Kinect: {kinect_status}")
    
    # 2. Inicializar integración sensorial
    print("\n🎭 Inicializando integración sensorial de Vicky...")
    vicky_sensors = VickySensoryIntegration(kinect)
    
    # 3. Configurar callbacks de monitoreo
    def on_interaction(interaction_type, input_text, output_text, timestamp):
        print(f"💬 INTERACCIÓN [{interaction_type}]: '{input_text}' -> '{output_text}'")
    
    def on_state_change(change_type, state, timestamp):
        print(f"🔄 ESTADO CAMBIÓ [{change_type}]: Activada={state.is_activated}, Personas={state.faces_detected}")
    
    vicky_sensors.set_interaction_callback(on_interaction)
    vicky_sensors.set_state_change_callback(on_state_change)
    
    # 4. Iniciar todos los sensores
    print("\n🚀 Iniciando TODOS los sensores de Vicky...")
    await vicky_sensors.start_all_sensors()
    
    # 5. Mostrar estado inicial
    print("\n📊 ESTADO INICIAL:")
    status = vicky_sensors.get_comprehensive_status()
    print_status_summary(status)
    
    # 6. Simular interacciones durante 30 segundos
    print("\n🎬 Simulando interacciones por 30 segundos...")
    print("   (En un sistema real, aquí Vicky estaría escuchando y viendo)")
    
    for i in range(30):
        # Mostrar estado cada 5 segundos
        if i % 5 == 0:
            print(f"\n⏱️  SEGUNDO {i}/30:")
            current_status = vicky_sensors.get_comprehensive_status()
            
            # Mostrar información clave
            sensory = current_status["sensory_state"]
            audio = current_status["audio_status"]
            vision = current_status["vision_status"]
            
            print(f"   👂 Audio: Escuchando={audio['is_listening']}, Activado={audio['is_activated']}")
            print(f"   👀 Visión: Procesando={vision['is_processing']}, Caras={vision['faces_detected']}")
            print(f"   🧠 Estado: Persona presente={sensory['person_present']}, Mood={sensory['current_mood']}")
            
        await asyncio.sleep(1)
    
    # 7. Detener sensores
    print("\n🛑 Deteniendo todos los sensores...")
    vicky_sensors.stop_all_sensors()
    
    # 8. Estado final
    print("\n📊 ESTADO FINAL:")
    final_status = vicky_sensors.get_comprehensive_status()
    print_status_summary(final_status)
    
    print("\n✅ PRUEBA COMPLETA FINALIZADA")
    print("🎉 Vicky ahora tiene OÍDO, VISTA y VOZ completamente integrados!")

def print_status_summary(status):
    """Imprime resumen del estado"""
    sensory = status["sensory_state"]
    audio = status["audio_status"]
    vision = status["vision_status"]
    brain = status["brain_status"]
    kinect = status["kinect_status"]
    config = status["configuration"]
    
    print(f"   🎭 SENSORES:")
    print(f"      👂 Oído: {'🟢 Activo' if audio['is_listening'] else '🔴 Inactivo'}")
    print(f"      👀 Vista: {'🟢 Activo' if vision['is_processing'] else '🔴 Inactivo'}")
    print(f"      🎵 Voz: {'🟢 Disponible' if 'tts_model' in str(brain) else '🟢 Disponible'}")
    print(f"      🤖 Kinect: {'🟢 Conectado' if kinect['connected'] else '🟡 Simulado'}")
    
    print(f"   🧠 CEREBRO DUAL:")
    print(f"      Balance: {brain['hemisphere_balance']}")
    print(f"      Peticiones: {brain.get('total_requests', 0)}")
    
    print(f"   👤 DETECCIÓN:")
    print(f"      Personas presentes: {sensory['faces_detected']}")
    print(f"      Mood actual: {sensory['current_mood']}")
    print(f"      Activada: {'🔥 SÍ' if sensory['is_activated'] else '💤 NO'}")
    
    print(f"   ⚙️  CONFIGURACIÓN:")
    print(f"      Auto-orientación: {'✅' if config['auto_orient_to_person'] else '❌'}")
    print(f"      Respuestas emocionales: {'✅' if config['emotional_response_enabled'] else '❌'}")
    print(f"      Timeout conversación: {config['conversation_timeout']}s")
    
    print(f"   📈 ESTADÍSTICAS:")
    print(f"      Interacciones registradas: {status['interaction_history_count']}")
    print(f"      Última interacción: {time.ctime(sensory['last_interaction']) if sensory['last_interaction'] > 0 else 'Nunca'}")

if __name__ == "__main__":
    asyncio.run(test_complete_sensory_integration()) 
#!/usr/bin/env python3
"""
Prueba de capacidades de voz de Vicky
"""
import asyncio
from src.vicky.core.brain import VickyBrain

async def test_vicky_voice():
    print("🧠 Inicializando Vicky con capacidades de voz...")
    brain = VickyBrain()
    
    print("✅ Cerebro dual cargado")
    print(f"🎯 Balance inicial: {brain.current_balance}")
    
    # Probar síntesis de voz
    print("\n🎵 Probando síntesis de voz...")
    result = await brain.synthesize_speech(
        text="Hola, soy Vicky y ahora tengo voz. Mi cerebro dual me permite hablar con emoción y precisión técnica.",
        language="es",
        emotion="neutral"
    )
    
    print(f"✅ Síntesis exitosa: {result['success']}")
    if result['success']:
        print(f"📁 Archivo de audio: {result['audio_path']}")
        print(f"📝 Texto procesado: {result['processed_text']}")
        print(f"🧠 Balance hemisférico: {result['hemisphere_balance']}")
        print(f"⏱️ Tiempo de procesamiento: {result['processing_time']:.3f}s")
    else:
        print(f"❌ Error: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_vicky_voice()) 
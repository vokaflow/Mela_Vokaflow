#!/usr/bin/env python3
"""
Script de inicio para VickyAI como servicio independiente
"""

import os
import sys
import subprocess

def main():
    print("🧠 Iniciando VickyAI como servicio independiente...")
    print("🎭 Sistema Cognitivo Revolucionario - Puerto 8001")
    print("=" * 50)
    
    # Cambiar al directorio de VickyAI
    vicky_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(vicky_dir)
    
    try:
        # Ejecutar VickyAI
        subprocess.run([
            sys.executable, "main.py"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🔄 VickyAI detenido por el usuario")
    except Exception as e:
        print(f"❌ Error ejecutando VickyAI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

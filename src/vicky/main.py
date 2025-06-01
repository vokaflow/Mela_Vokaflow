#!/usr/bin/env python3
"""
Vicky - Punto de entrada principal
"""
import os
import sys
import logging
import logging.config
import yaml
import argparse

# Configurar logging
if os.path.exists("/opt/vokaflow/config/logging.yaml"):
    with open("/opt/vokaflow/config/logging.yaml", "r") as f:
        log_config = yaml.safe_load(f)
        logging.config.dictConfig(log_config)
else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('/mnt/nvme_fast/vokaflow_logs/vicky/vicky.log')
        ]
    )

logger = logging.getLogger("vicky")

from .core.brain import VickyBrain

def parse_args():
    """Parsea los argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description="Vicky - IA de VokaFlow")
    parser.add_argument("--config", help="Ruta al archivo de configuración")
    parser.add_argument("--interactive", action="store_true", help="Modo interactivo")
    return parser.parse_args()

def interactive_mode(brain):
    """Ejecuta Vicky en modo interactivo"""
    print("=== Vicky - Modo Interactivo ===")
    print("Escribe 'salir' para terminar")
    print()
    
    while True:
        try:
            message = input("Tú: ")
            if message.lower() in ["salir", "exit", "quit"]:
                break
            
            response = brain.process_message(message)
            print(f"Vicky: {response}")
            print()
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error en modo interactivo: {e}")
            print(f"Error: {e}")
    
    print("¡Hasta luego!")

def main():
    """Función principal"""
    args = parse_args()
    
    logger.info("Iniciando Vicky")
    
    # Crear instancia del cerebro de Vicky
    brain = VickyBrain(config_path=args.config)
    
    # Iniciar Vicky
    brain.start()
    
    # Modo interactivo si se especifica
    if args.interactive:
        interactive_mode(brain)
    else:
        # Modo servidor
        logger.info("Vicky iniciada en modo servidor")
        # Aquí se implementaría el servidor para recibir peticiones
        # Por ahora, mantenemos el proceso vivo
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Deteniendo Vicky")

if __name__ == "__main__":
    main()

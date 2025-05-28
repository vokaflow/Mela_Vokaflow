#!/usr/bin/env python3
"""
Script para probar la integración de Kinect
"""

import os
import sys
import time
import argparse

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(__file__))

# Importar la API de Kinect
from kinect_integration import KinectAPI

def main():
    parser = argparse.ArgumentParser(description='Prueba de integración de Kinect')
    parser.add_argument('--simulation', action='store_true', help='Usar modo de simulación')
    args = parser.parse_args()
    
    print(f"Iniciando prueba de Kinect {'en modo simulación' if args.simulation else ''}")
    
    # Inicializar la API de Kinect
    kinect = KinectAPI(simulation_mode=args.simulation)
    
    # Mostrar el estado inicial
    print("Estado inicial:")
    print_status(kinect.get_status())
    
    # Inicializar la conexión
    print("\nInicializando Kinect...")
    if kinect.initialize():
        print("Kinect inicializada correctamente")
    else:
        print("Error al inicializar Kinect")
        return
    
    # Mostrar el estado después de inicializar
    print("\nEstado después de inicializar:")
    print_status(kinect.get_status())
    
    # Probar el cambio de ángulo
    print("\nOrientando Kinect a diferentes posiciones...")
    
    print("  - Hacia arriba")
    if kinect.look_up():
        print("    OK")
    else:
        print("    Error")
    time.sleep(1)
    
    print("  - Hacia abajo")
    if kinect.look_down():
        print("    OK")
    else:
        print("    Error")
    time.sleep(1)
    
    print("  - Al centro")
    if kinect.look_center():
        print("    OK")
    else:
        print("    Error")
    time.sleep(1)
    
    # Capturar una imagen
    print("\nCapturando imagen...")
    image_path = kinect.capture_image()
    if image_path:
        print(f"Imagen capturada correctamente: {image_path}")
    else:
        print("Error al capturar imagen")
    
    # Realizar un escaneo completo
    print("\nRealizando escaneo de la habitación...")
    captured_images = kinect.scan_room()
    print(f"Escaneo completado. {len(captured_images)} imágenes capturadas:")
    for i, img in enumerate(captured_images):
        print(f"  {i+1}. {img}")
    
    # Mostrar el estado final
    print("\nEstado final:")
    print_status(kinect.get_status())
    
    print("\nPrueba completada")

def print_status(status):
    """Imprime el estado de la Kinect de forma legible"""
    print(f"  Conectada: {status['connected']}")
    print(f"  Ángulo: {status['angle']}°")
    print(f"  Acelerómetro: X={status['accelerometer']['x']:.2f}, Y={status['accelerometer']['y']:.2f}, Z={status['accelerometer']['z']:.2f}")
    print(f"  Última captura: {status['last_capture'] or 'Ninguna'}")
    print(f"  Backend: {status['backend']}")
    print(f"  Modo simulación: {status['simulation_mode']}")

if __name__ == "__main__":
    main() 
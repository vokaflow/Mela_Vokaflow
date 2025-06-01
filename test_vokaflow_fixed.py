#!/usr/bin/env python3
"""
🧪 Test VokaFlow Fixed - Prueba del sistema corregido
"""

import os
import sys
import subprocess
import time
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test-vokaflow")

def test_main_fixed():
    """Probar el archivo main_fixed.py"""
    logger.info("🧪 Probando main_fixed.py...")
    
    try:
        # Cambiar al directorio correcto
        os.chdir("/opt/vokaflow")
        
        # Verificar que el archivo existe
        if not os.path.exists("src/main_fixed.py"):
            logger.error("❌ Archivo main_fixed.py no encontrado")
            return False
        
        # Probar importación
        logger.info("🔍 Probando importación...")
        result = subprocess.run([
            "python", "-c", 
            "import sys; sys.path.append('src'); import main_fixed; print('✅ Importación exitosa')"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            logger.info("✅ Importación exitosa")
            logger.info(f"Output: {result.stdout}")
            return True
        else:
            logger.error("❌ Error de importación")
            logger.error(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Timeout durante la prueba")
        return False
    except Exception as e:
        logger.error(f"❌ Error durante la prueba: {e}")
        return False

def test_syntax():
    """Probar sintaxis del archivo"""
    logger.info("🔍 Verificando sintaxis...")
    
    try:
        result = subprocess.run([
            "python", "-m", "py_compile", "src/main_fixed.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ Sintaxis correcta")
            return True
        else:
            logger.error("❌ Error de sintaxis")
            logger.error(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error verificando sintaxis: {e}")
        return False

def run_server_test():
    """Ejecutar servidor por 10 segundos para probar"""
    logger.info("🚀 Iniciando servidor de prueba...")
    
    try:
        # Ejecutar servidor
        process = subprocess.Popen([
            "python", "src/main_fixed.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Esperar 10 segundos
        time.sleep(10)
        
        # Detener proceso
        process.terminate()
        process.wait(timeout=5)
        
        logger.info("✅ Servidor ejecutado correctamente por 10 segundos")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error ejecutando servidor: {e}")
        return False

def main():
    """Función principal de prueba"""
    logger.info("=" * 60)
    logger.info("🧪 PRUEBA DE VOKAFLOW CORREGIDO")
    logger.info("=" * 60)
    
    tests = [
        ("Verificación de sintaxis", test_syntax),
        ("Prueba de importación", test_main_fixed),
        ("Prueba de servidor", run_server_test)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n📋 Ejecutando: {test_name}")
        result = test_func()
        results.append((test_name, result))
        
        if result:
            logger.info(f"✅ {test_name}: EXITOSO")
        else:
            logger.error(f"❌ {test_name}: FALLIDO")
    
    logger.info("\n" + "=" * 60)
    logger.info("📊 RESULTADOS FINALES")
    logger.info("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ EXITOSO" if result else "❌ FALLIDO"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\n📈 Pruebas exitosas: {passed}/{len(tests)}")
    
    if passed == len(tests):
        logger.info("🎉 ¡Todas las pruebas pasaron! VokaFlow corregido está listo.")
        return True
    else:
        logger.error("⚠️ Algunas pruebas fallaron. Revisar errores.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
#!/usr/bin/env python3
"""
Interfaz de línea de comandos para Vicky
"""
import argparse
import logging
import os
import sys
import yaml
import readline
import time
import colorama
import json
import platform
import psutil
from datetime import datetime
from colorama import Fore, Style
from cmd import Cmd
from pathlib import Path

# Inicializar colorama
colorama.init()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/mnt/nvme_fast/vokaflow_logs/vicky/vicky_cli.log')
    ]
)

logger = logging.getLogger("vicky.cli")

# Añadir la ruta de Vicky al path
sys.path.append("/opt/vokaflow/src")

# Importar el cerebro de Vicky
from vicky.core.brain import VickyBrain
from vicky.core.feedback import feedback_manager


class HistoryManager:
    """
    Gestor de historial de comandos y conversaciones
    """
    def __init__(self, history_file=None):
        """Inicializa el gestor de historial"""
        if history_file is None:
            history_dir = os.path.expanduser("~/.vicky")
            os.makedirs(history_dir, exist_ok=True)
            history_file = os.path.join(history_dir, "history.txt")
        
        self.history_file = history_file
        self.session_history = []
        self.load_history()
    
    def load_history(self):
        """Carga el historial desde el archivo"""
        try:
            if os.path.exists(self.history_file):
                readline.read_history_file(self.history_file)
                logger.debug(f"Historial cargado de {self.history_file}")
        except Exception as e:
            logger.error(f"Error al cargar historial: {e}")
    
    def save_history(self):
        """Guarda el historial en el archivo"""
        try:
            readline.write_history_file(self.history_file)
            logger.debug(f"Historial guardado en {self.history_file}")
        except Exception as e:
            logger.error(f"Error al guardar historial: {e}")
    
    def add_to_history(self, command):
        """Añade un comando al historial"""
        self.session_history.append(command)
        # Asegurarse de que readline también lo tenga
        readline.add_history(command)
    
    def get_last_commands(self, n=10):
        """Obtiene los últimos n comandos"""
        return self.session_history[-n:] if self.session_history else []


class CommandCompleter:
    """
    Completa comandos con Tab
    """
    def __init__(self, commands=None):
        """Inicializa el completador con una lista de comandos"""
        self.commands = commands or []
        # Registrar el completador con readline
        readline.set_completer(self.complete)
        readline.parse_and_bind("tab: complete")
        # Establecer delimitadores adecuados para CLI
        readline.set_completer_delims(' \t\n')
    
    def update_commands(self, commands):
        """Actualiza la lista de comandos disponibles"""
        self.commands = commands or []
    
    def complete(self, text, state):
        """Completa el texto parcial con los comandos disponibles"""
        # Crear la lista de opciones que coinciden con el texto
        matches = [cmd for cmd in self.commands if cmd.startswith(text)]
        
        if state < len(matches):
            return matches[state]
        else:
            return None


class VickyCLI(Cmd):
    """
    CLI interactiva mejorada para Vicky
    """
    # Definir comandos básicos
    BASIC_COMMANDS = [
        "ayuda", "help", "salir", "exit", "quit", "limpiar", "clear", "cls",
        "info", "system", "status", "modelos", "historial", "history"
    ]
    
    # Definir comandos con parámetros
    PARAM_COMMANDS = [
        "cargar", "descargar", "cambiar", "traducir", "recuerda", 
        "busca", "olvida", "feedback", "valorar", "bug"
    ]
    
    # Todos los comandos disponibles (para autocompletado)
    ALL_COMMANDS = BASIC_COMMANDS + [
        f"{cmd} " for cmd in PARAM_COMMANDS
    ]
    
    def __init__(self, brain, model="qwen", no_color=False, debug=False):
        """
        Inicializa la CLI de Vicky
        
        Args:
            brain: Instancia de VickyBrain
            model: Modelo inicial a usar
            no_color: Si se debe desactivar los colores
            debug: Si se debe activar el modo debug
        """
        super().__init__()
        self.brain = brain
        self.active_model = model
        self.no_color = no_color
        self.debug = debug
        
        # Desactivar colores si se solicita
        if no_color:
            colorama.deinit()
        
        # Configurar historial
        self.history_manager = HistoryManager()
        
        # Configurar completador
        self.completer = CommandCompleter(self.ALL_COMMANDS)
        
        # ID de usuario (simplificado para CLI)
        self.user_id = f"cli_{os.getuid()}"
        
        # Última interacción para feedback
        self.last_interaction = None
        
        logger.info("CLI de Vicky inicializada")
    
    def run(self):
        """Ejecuta la CLI interactiva"""
        self.print_welcome()
        
        try:
            while True:
                try:
                    # Leer entrada del usuario
                    user_input = input(Fore.GREEN + "Tú > " + Style.RESET_ALL)
                    
                    # Si está vacío, continuar
                    if not user_input.strip():
                        continue
                    
                    # Agregar al historial
                    self.history_manager.add_to_history(user_input)
                    
                    # Procesar la entrada
                    should_exit = self.process_input(user_input)
                    if should_exit:
                        break
                
                except KeyboardInterrupt:
                    print(Fore.YELLOW + "\n¡Hasta luego!" + Style.RESET_ALL)
                    break
                except Exception as e:
                    logger.error(f"Error en el bucle principal: {e}", exc_info=self.debug)
                    print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)
        finally:
            # Guardar historial y limpiar
            self.cleanup()
    
    def cleanup(self):
        """Realiza limpieza al finalizar"""
        print(Fore.YELLOW + "Deteniendo Vicky..." + Style.RESET_ALL)
        self.history_manager.save_history()
        self.brain.shutdown()
        print(Fore.GREEN + "Vicky detenida correctamente" + Style.RESET_ALL)
    
    def process_input(self, user_input):
        """
        Procesa la entrada del usuario
        
        Returns:
            bool: True si se debe salir de la aplicación
        """
        cmd = user_input.lower().strip()
        
        # Comandos básicos
        if cmd in ["salir", "exit", "quit"]:
            print(Fore.YELLOW + "¡Hasta luego!" + Style.RESET_ALL)
            return True
        
        elif cmd in ["ayuda", "help"]:
            self.print_help()
            
        elif cmd in ["limpiar", "clear", "cls"]:
            os.system("clear" if os.name == "posix" else "cls")
            
        elif cmd in ["info", "system", "status"]:
            self.print_system_info()
            
        elif cmd == "modelos":
            self.list_models()
            
        elif cmd in ["historial", "history"]:
            self.show_history()
        
        # Comandos con parámetros
        elif cmd.startswith("cargar "):
            self.load_model(cmd[7:].strip())
            
        elif cmd.startswith("descargar "):
            self.unload_model(cmd[10:].strip())
            
        elif cmd.startswith("cambiar "):
            self.change_model(cmd[8:].strip())
            
        elif cmd.startswith("traducir "):
            self.translate_text(cmd[9:].strip())
            
        elif cmd.startswith("recuerda "):
            self.save_memory(cmd[9:].strip())
            
        elif cmd.startswith("busca "):
            self.search_memory(cmd[6:].strip())
            
        elif cmd.startswith("olvida "):
            self.delete_memory(cmd[7:].strip())
        
        # Sistema de feedback
        elif cmd.startswith("valorar "):
            parts = cmd[8:].strip().split(' ', 1)
            if len(parts) >= 1 and parts[0].isdigit():
                rating = int(parts[0])
                comment = parts[1] if len(parts) > 1 else ""
                self.rate_response(rating, comment)
            else:
                print(Fore.RED + "Uso: valorar <1-5> [comentario]" + Style.RESET_ALL)
        
        elif cmd.startswith("feedback "):
            self.send_feedback(cmd[9:].strip())
            
        elif cmd.startswith("bug "):
            self.report_bug(cmd[4:].strip())
        
        # Si no es un comando conocido, procesar con Vicky
        else:
            self.process_with_vicky(user_input)
        
        return False
    
    def print_welcome(self):
        """Imprime mensaje de bienvenida"""
        print(Fore.CYAN + Style.BRIGHT + """
 __      __   _          ______ _                 
 \ \    / /  | |        |  ____| |                
  \ \  / /__ | | __ __ _| |__  | | _____      __  
   \ \/ / _ \| |/ // _` |  __| | |/ _ \ \ /\ / /  
    \  / (_) |   <| (_| | |    | | (_) \ V  V /   
     \/ \___/|_|\_\\__,_|_|    |_|\___/ \_/\_/    
                                                  
    """ + Style.RESET_ALL)
        print(Fore.GREEN + "Bienvenido a Vicky CLI - Tu asistente de IA" + Style.RESET_ALL)
        print(Fore.YELLOW + "Escribe 'ayuda' para ver los comandos disponibles" + Style.RESET_ALL)
        print(Fore.YELLOW + "Escribe 'salir' para terminar" + Style.RESET_ALL)
        print()
        
        # Mostrar valoración promedio si existe
        avg_rating = feedback_manager.get_average_rating()
        if avg_rating:
            stars = "★" * int(avg_rating) + "☆" * (5 - int(avg_rating))
            print(Fore.CYAN + f"Valoración media: {stars} ({avg_rating}/5)" + Style.RESET_ALL)
        
        print()
    
    def print_help(self):
        """Imprime ayuda de comandos"""
        print(Fore.CYAN + "Comandos disponibles:" + Style.RESET_ALL)
        
        # Comandos básicos
        print(Fore.YELLOW + "Comandos básicos:" + Style.RESET_ALL)
        print(Fore.GREEN + "  ayuda" + Fore.RESET + " - Muestra esta ayuda")
        print(Fore.GREEN + "  salir" + Fore.RESET + " - Termina la sesión")
        print(Fore.GREEN + "  limpiar" + Fore.RESET + " - Limpia la pantalla")
        print(Fore.GREEN + "  info" + Fore.RESET + " - Muestra información del sistema")
        print(Fore.GREEN + "  modelos" + Fore.RESET + " - Muestra los modelos cargados")
        print(Fore.GREEN + "  historial" + Fore.RESET + " - Muestra los últimos comandos")
        
        # Comandos de gestión de modelos
        print(Fore.YELLOW + "\nGestión de modelos:" + Style.RESET_ALL)
        print(Fore.GREEN + "  cargar <tipo>" + Fore.RESET + " - Carga un modelo (language, translation, speech, tts, embedding, deepseek)")
        print(Fore.GREEN + "  descargar <tipo>" + Fore.RESET + " - Descarga un modelo")
        print(Fore.GREEN + "  cambiar <modelo>" + Fore.RESET + " - Cambia el modelo de lenguaje (qwen, deepseek)")
        
        # Comandos de memoria y procesamiento
        print(Fore.YELLOW + "\nMemoria y procesamiento:" + Style.RESET_ALL)
        print(Fore.GREEN + "  traducir <texto>" + Fore.RESET + " - Traduce un texto")
        print(Fore.GREEN + "  recuerda <texto>" + Fore.RESET + " - Guarda un recuerdo")
        print(Fore.GREEN + "  busca <texto>" + Fore.RESET + " - Busca en los recuerdos")
        print(Fore.GREEN + "  olvida <texto>" + Fore.RESET + " - Elimina un recuerdo")
        
        # Sistema de feedback
        print(Fore.YELLOW + "\nSistema de feedback:" + Style.RESET_ALL)
        print(Fore.GREEN + "  valorar <1-5> [comentario]" + Fore.RESET + " - Valora la última respuesta")
        print(Fore.GREEN + "  feedback <mensaje>" + Fore.RESET + " - Envía un comentario general")
        print(Fore.GREEN + "  bug <descripción>" + Fore.RESET + " - Reporta un problema")
        
        print()
        print(Fore.YELLOW + "Para cualquier otro texto, Vicky intentará responder como asistente" + Style.RESET_ALL)
        print(Fore.CYAN + "Usa las flechas ↑↓ para navegar por el historial de comandos" + Style.RESET_ALL)
        print(Fore.CYAN + "Usa Tab para autocompletar comandos" + Style.RESET_ALL)
        print()
    
    def print_system_info(self):
        """Imprime información del sistema"""
        print(Fore.CYAN + "Información del sistema:" + Style.RESET_ALL)
        
        # Información del sistema
        print(Fore.GREEN + "Sistema:" + Style.RESET_ALL)
        print(f"  - OS: {platform.system()} {platform.release()}")
        print(f"  - CPU: {platform.processor()}")
        print(f"  - Núcleos: {psutil.cpu_count(logical=False)} físicos, {psutil.cpu_count()} lógicos")
        print(f"  - RAM: {psutil.virtual_memory().total / (1024**3):.2f} GB")
        print(f"  - Uso de CPU: {psutil.cpu_percent()}%")
        print(f"  - Uso de RAM: {psutil.virtual_memory().percent}%")
        
        # Información de GPU
        try:
            import torch
            print(Fore.GREEN + "GPU:" + Style.RESET_ALL)
            if torch.cuda.is_available():
                print(f"  - Disponible: Sí")
                print(f"  - Dispositivo: {torch.cuda.get_device_name(0)}")
                print(f"  - Memoria total: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
                print(f"  - Memoria en uso: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
                print(f"  - Memoria reservada: {torch.cuda.memory_reserved() / 1024**3:.2f} GB")
            else:
                print(f"  - Disponible: No")
        except Exception as e:
            print(f"  - Error al obtener información de GPU: {e}")
        
        # Información de modelos
        print(Fore.GREEN + "Modelos:" + Style.RESET_ALL)
        print(f"  - Directorio de modelos: /mnt/nvme_fast/vokaflow_models")
        
        # Listar modelos disponibles
        try:
            models_dir = "/mnt/nvme_fast/vokaflow_models"
            if os.path.exists(models_dir):
                models = os.listdir(models_dir)
                print(f"  - Modelos disponibles: {', '.join(models)}")
            else:
                print(f"  - Directorio de modelos no encontrado")
        except Exception as e:
            print(f"  - Error al listar modelos: {e}")
        
        # Información de almacenamiento
        print(Fore.GREEN + "Almacenamiento:" + Style.RESET_ALL)
        try:
            import shutil
            nvme_usage = shutil.disk_usage("/mnt/nvme_fast")
            
            print(f"  - SSD NVMe (/mnt/nvme_fast):")
            print(f"    - Total: {nvme_usage.total / 1024**3:.2f} GB")
            print(f"    - Usado: {nvme_usage.used / 1024**3:.2f} GB ({nvme_usage.used / nvme_usage.total * 100:.2f}%)")
            print(f"    - Libre: {nvme_usage.free / 1024**3:.2f} GB")
        except Exception as e:
            print(f"  - Error al obtener información de almacenamiento: {e}")
        
        # Información de directorios de datos
        print(Fore.GREEN + "Directorios de datos:" + Style.RESET_ALL)
        data_dirs = [
            "/mnt/nvme_fast/vokaflow_data/vector_db",
            "/mnt/nvme_fast/vokaflow_data/memory",
            "/mnt/nvme_fast/vokaflow_data/state",
            "/mnt/nvme_fast/vokaflow_logs/vicky",
            "/mnt/nvme_fast/vokaflow_data/feedback"
        ]
        
        for dir_path in data_dirs:
            if os.path.exists(dir_path):
                size = sum(f.stat().st_size for f in Path(dir_path).glob('**/*') if f.is_file())
                print(f"  - {dir_path}: {size / 1024**2:.2f} MB")
            else:
                print(f"  - {dir_path}: No existe")
        
        # Información de feedback
        print(Fore.GREEN + "Sistema de feedback:" + Style.RESET_ALL)
        avg_rating = feedback_manager.get_average_rating()
        if avg_rating:
            stars = "★" * int(avg_rating) + "☆" * (5 - int(avg_rating))
            print(f"  - Valoración media: {stars} ({avg_rating}/5)")
        else:
            print(f"  - No hay valoraciones recientes")
        
        try:
            # Contar comentarios y bugs recientes
            comments = len(feedback_manager.get_recent_feedback(category="comments"))
            issues = len(feedback_manager.get_recent_feedback(category="issues"))
            print(f"  - Comentarios recientes: {comments}")
            print(f"  - Problemas reportados: {issues}")
        except Exception as e:
            print(f"  - Error al obtener estadísticas de feedback: {e}")
        
        print()
    
    def list_models(self):
        """Muestra los modelos cargados"""
        models = self.brain.model_manager.get_loaded_models()
        print(Fore.CYAN + "Modelos cargados:" + Style.RESET_ALL)
        if models:
            for model in models:
                print(Fore.YELLOW + f"  - {model}" + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + "  No hay modelos cargados" + Style.RESET_ALL)
    
    def show_history(self):
        """Muestra el historial de comandos"""
        history = self.history_manager.get_last_commands(20)
        print(Fore.CYAN + "Historial de comandos recientes:" + Style.RESET_ALL)
        if history:
            for i, cmd in enumerate(history):
                print(Fore.YELLOW + f"  {i+1}. " + Fore.RESET + cmd)
        else:
            print(Fore.YELLOW + "  No hay comandos en el historial" + Style.RESET_ALL)
    
    def load_model(self, model_type):
        """Carga un modelo específico"""
        print(Fore.YELLOW + f"Cargando modelo {model_type}..." + Style.RESET_ALL)
        start_time = time.time()
        try:
            model = self.brain.model_manager.load_model(model_type)
            if model:
                print(Fore.GREEN + f"Modelo {model_type} cargado en {time.time() - start_time:.2f} segundos" + Style.RESET_ALL)
            else:
                print(Fore.RED + f"Error al cargar modelo {model_type}" + Style.RESET_ALL)
        except Exception as e:
            logger.error(f"Error al cargar modelo {model_type}: {e}", exc_info=self.debug)
            print(Fore.RED + f"Error al cargar modelo: {e}" + Style.RESET_ALL)
    
    def unload_model(self, model_type):
        """Descarga un modelo para liberar memoria"""
        print(Fore.YELLOW + f"Descargando modelo {model_type}..." + Style.RESET_ALL)
        try:
            if self.brain.model_manager.unload_model(model_type):
                print(Fore.GREEN + f"Modelo {model_type} descargado" + Style.RESET_ALL)
            else:
                print(Fore.RED + f"Error al descargar modelo {model_type}" + Style.RESET_ALL)
        except Exception as e:
            logger.error(f"Error al descargar modelo {model_type}: {e}", exc_info=self.debug)
            print(Fore.RED + f"Error al descargar modelo: {e}" + Style.RESET_ALL)
    
    def change_model(self, new_model):
        """Cambia el modelo de lenguaje activo"""
        if new_model in ["qwen", "deepseek"]:
            self.active_model = new_model
            print(Fore.GREEN + f"Modelo de lenguaje cambiado a {self.active_model}" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"Modelo no reconocido. Opciones válidas: qwen, deepseek" + Style.RESET_ALL)
    
    def translate_text(self, text):
        """Traduce un texto a otro idioma"""
        print(Fore.YELLOW + "Traduciendo texto..." + Style.RESET_ALL)
        try:
            # Cargar modelo de traducción si no está cargado
            translation_model = self.brain.model_manager.get_model("translation")
            if not translation_model:
                print(Fore.YELLOW + "Cargando modelo de traducción..." + Style.RESET_ALL)
                translation_model = self.brain.model_manager.load_model("translation")
            
            if translation_model:
                start_time = time.time()
                # Traducir según el formato: "texto|idioma_destino"
                if "|" in text:
                    source_text, target_lang = text.split("|", 1)
                    source_text = source_text.strip()
                    target_lang = target_lang.strip().lower()
                else:
                    source_text = text
                    target_lang = "es"  # Idioma por defecto
                
                # Obtener traducción
                translation = translation_model.translate(source_text, target_lang)
                processing_time = time.time() - start_time
                
                # Mostrar resultados
                print(Fore.BLUE + f"Texto original: " + Style.RESET_ALL + source_text)
                print(Fore.BLUE + f"Traducción ({target_lang}): " + Style.RESET_ALL + translation)
                print(Fore.CYAN + f"(Tiempo: {processing_time:.2f} segundos)" + Style.RESET_ALL)
            else:
                print(Fore.RED + "No se pudo cargar el modelo de traducción" + Style.RESET_ALL)
        except Exception as e:
            logger.error(f"Error al traducir texto: {e}", exc_info=self.debug)
            print(Fore.RED + f"Error al traducir: {e}" + Style.RESET_ALL)
    
    def save_memory(self, text):
        """Guarda un recuerdo en la memoria de Vicky"""
        print(Fore.YELLOW + "Guardando recuerdo..." + Style.RESET_ALL)
        try:
            # Verificar si el plugin de memoria está activo
            if hasattr(self.brain, 'memory') and self.brain.memory:
                result = self.brain.memory.save(text, self.user_id)
                if result:
                    print(Fore.GREEN + "Recuerdo guardado correctamente" + Style.RESET_ALL)
                else:
                    print(Fore.RED + "Error al guardar recuerdo" + Style.RESET_ALL)
            else:
                print(Fore.RED + "Sistema de memoria no disponible" + Style.RESET_ALL)
        except Exception as e:
            logger.error(f"Error al guardar recuerdo: {e}", exc_info=self.debug)
            print(Fore.RED + f"Error al guardar recuerdo: {e}" + Style.RESET_ALL)
    
    def search_memory(self, query):
        """Busca en la memoria de Vicky"""
        print(Fore.YELLOW + "Buscando en recuerdos..." + Style.RESET_ALL)
        try:
            # Verificar si el plugin de memoria está activo
            if hasattr(self.brain, 'memory') and self.brain.memory:
                start_time = time.time()
                results = self.brain.memory.search(query, limit=5)
                processing_time = time.time() - start_time
                
                if results:
                    print(Fore.CYAN + f"Resultados encontrados ({len(results)}):" + Style.RESET_ALL)
                    for i, (memory, score) in enumerate(results):
                        print(Fore.YELLOW + f"  {i+1}. [{score:.2f}] " + Fore.RESET + memory)
                else:
                    print(Fore.YELLOW + "No se encontraron recuerdos relacionados" + Style.RESET_ALL)
                
                print(Fore.CYAN + f"(Tiempo de búsqueda: {processing_time:.2f} segundos)" + Style.RESET_ALL)
            else:
                print(Fore.RED + "Sistema de memoria no disponible" + Style.RESET_ALL)
        except Exception as e:
            logger.error(f"Error al buscar en recuerdos: {e}", exc_info=self.debug)
            print(Fore.RED + f"Error al buscar: {e}" + Style.RESET_ALL)
    
    def delete_memory(self, query):
        """Elimina un recuerdo de la memoria de Vicky"""
        print(Fore.YELLOW + "Eliminando recuerdo..." + Style.RESET_ALL)
        try:
            # Verificar si el plugin de memoria está activo
            if hasattr(self.brain, 'memory') and self.brain.memory:
                # Búsqueda previa para mostrar qué se va a eliminar
                results = self.brain.memory.search(query, limit=1)
                
                if results:
                    memory, score = results[0]
                    print(Fore.CYAN + "Se eliminará este recuerdo:" + Style.RESET_ALL)
                    print(Fore.YELLOW + f"  [{score:.2f}] " + Fore.RESET + memory)
                    
                    # Pedir confirmación
                    confirm = input(Fore.YELLOW + "¿Confirmar eliminación? (s/n): " + Style.RESET_ALL).lower()
                    if confirm in ['s', 'si', 'y', 'yes']:
                        result = self.brain.memory.delete(query)
                        if result:
                            print(Fore.GREEN + "Recuerdo eliminado correctamente" + Style.RESET_ALL)
                        else:
                            print(Fore.RED + "Error al eliminar recuerdo" + Style.RESET_ALL)
                    else:
                        print(Fore.YELLOW + "Operación cancelada" + Style.RESET_ALL)
                else:
                    print(Fore.YELLOW + "No se encontraron recuerdos relacionados para eliminar" + Style.RESET_ALL)
            else:
                print(Fore.RED + "Sistema de memoria no disponible" + Style.RESET_ALL)
        except Exception as e:
            logger.error(f"Error al eliminar recuerdo: {e}", exc_info=self.debug)
            print(Fore.RED + f"Error al eliminar: {e}" + Style.RESET_ALL)
    
    def rate_response(self, rating, comment=""):
        """Valora la última respuesta de Vicky"""
        if not 1 <= rating <= 5:
            print(Fore.RED + "La valoración debe ser entre 1 y 5" + Style.RESET_ALL)
            return
        
        if not self.last_interaction:
            print(Fore.YELLOW + "No hay respuesta reciente para valorar" + Style.RESET_ALL)
            return
        
        try:
            context = {
                "model": self.active_model,
                "response": self.last_interaction.get("response", ""),
                "query": self.last_interaction.get("query", "")
            }
            
            # Guardar valoración
            result = feedback_manager.save_rating(
                self.user_id, 
                rating, 
                interaction_id=self.last_interaction.get("id"), 
                context=context
            )
            
            # Si hay comentario, guardarlo también
            if comment and result:
                feedback_manager.save_comment(
                    self.user_id,
                    comment,
                    interaction_id=self.last_interaction.get("id"),
                    category="rating"
                )
            
            # Mostrar confirmación
            if result:
                stars = "★" * rating + "☆" * (5 - rating)
                print(Fore.GREEN + f"¡Gracias por tu valoración! {stars}" + Style.RESET_ALL)
                if comment:
                    print(Fore.GREEN + "Tu comentario ha sido registrado" + Style.RESET_ALL)
            else:
                print(Fore.RED + "Error al guardar la valoración" + Style.RESET_ALL)
        
        except Exception as e:
            logger.error(f"Error al valorar respuesta: {e}", exc_info=self.debug)
            print(Fore.RED + f"Error al guardar valoración: {e}" + Style.RESET_ALL)
    
    def send_feedback(self, comment):
        """Envía un comentario general sobre Vicky"""
        if not comment:
            print(Fore.RED + "Por favor, proporciona un comentario" + Style.RESET_ALL)
            return
        
        try:
            result = feedback_manager.save_comment(
                self.user_id,
                comment,
                category="feedback"
            )
            
            if result:
                print(Fore.GREEN + "¡Gracias por tu comentario!" + Style.RESET_ALL)
                print(Fore.GREEN + "Tu feedback nos ayuda a mejorar Vicky" + Style.RESET_ALL)
            else:
                print(Fore.RED + "Error al guardar el comentario" + Style.RESET_ALL)
        
        except Exception as e:
            logger.error(f"Error al enviar feedback: {e}", exc_info=self.debug)
            print(Fore.RED + f"Error al guardar comentario: {e}" + Style.RESET_ALL)
    
    def report_bug(self, description):
        """Reporta un bug o problema con Vicky"""
        if not description:
            print(Fore.RED + "Por favor, describe el problema" + Style.RESET_ALL)
            return
        
        try:
            context = {
                "model": self.active_model,
                "system_info": {
                    "os": platform.system(),
                    "memory": psutil.virtual_memory().percent,
                    "cpu": psutil.cpu_percent()
                }
            }
            
            # Si hay interacción reciente, añadirla al contexto
            if self.last_interaction:
                context["last_interaction"] = {
                    "query": self.last_interaction.get("query", ""),
                    "response": self.last_interaction.get("response", "")
                }
            
            result = feedback_manager.report_issue(
                self.user_id,
                description,
                severity="medium",
                context=context
            )
            
            if result:
                print(Fore.GREEN + "¡Gracias por reportar este problema!" + Style.RESET_ALL)
                print(Fore.GREEN + "Trabajaremos para solucionarlo pronto" + Style.RESET_ALL)
            else:
                print(Fore.RED + "Error al reportar el problema" + Style.RESET_ALL)
        
        except Exception as e:
            logger.error(f"Error al reportar bug: {e}", exc_info=self.debug)
            print(Fore.RED + f"Error al reportar problema: {e}" + Style.RESET_ALL)
    
    def process_with_vicky(self, user_input):
        """Procesa la entrada con el cerebro de Vicky"""
        print(Fore.YELLOW + "Vicky está pensando..." + Style.RESET_ALL)
        start_time = time.time()
        
        try:
            # Generar ID único para esta interacción
            interaction_id = f"{int(time.time())}_{self.user_id}"
            
            # Usar el modelo activo
            if self.active_model == "qwen":
                response = self.brain.process_message(user_input)
            elif self.active_model == "deepseek":
                # Cargar modelo DeepSeek si no está cargado
                deepseek_model = self.brain.model_manager.get_model("deepseek")
                if deepseek_model:
                    response = deepseek_model.generate(user_input)
                else:
                    response = "Error: No se pudo cargar el modelo DeepSeek."
            else:
                response = "Error: Modelo no reconocido."
            
            # Calcular tiempo de procesamiento
            processing_time = time.time() - start_time
            
            # Mostrar respuesta
            print(Fore.BLUE + f"Vicky ({self.active_model}) > " + Style.RESET_ALL + response)
            print(Fore.CYAN + f"(Tiempo de respuesta: {processing_time:.2f} segundos)" + Style.RESET_ALL)
            
            # Guardar esta interacción para posible feedback
            self.last_interaction = {
                "id": interaction_id,
                "query": user_input,
                "response": response,
                "model": self.active_model,
                "time": processing_time
            }
            
            # Si la respuesta fue rápida y útil, sugerir valoración
            if 0.5 <= processing_time <= 5.0 and len(response) > 50:
                print(Fore.YELLOW + "¿Te ha sido útil la respuesta? Valórala con 'valorar <1-5> [comentario]'" + Style.RESET_ALL)
            
            print()
        
        except Exception as e:
            logger.error(f"Error al procesar con Vicky: {e}", exc_info=self.debug)
            print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)


def parse_args():
    """Parsea los argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description="Vicky - Interfaz de línea de comandos")
    parser.add_argument("--config", help="Ruta al archivo de configuración")
    parser.add_argument("--debug", action="store_true", help="Modo debug")
    parser.add_argument("--no-color", action="store_true", help="Desactivar colores")
    parser.add_argument("--model", choices=["qwen", "deepseek"], default="qwen", help="Modelo de lenguaje a usar")
    return parser.parse_args()


def main():
    """Función principal"""
    args = parse_args()
    
    # Configurar nivel de logging
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("Iniciando Vicky CLI")
    
    try:
        # Crear instancia del cerebro de Vicky
        brain = VickyBrain(config_path=args.config)
        
        # Iniciar Vicky
        brain.start()
        
        # Crear y ejecutar la CLI
        cli = VickyCLI(
            brain=brain,
            model=args.model,
            no_color=args.no_color,
            debug=args.debug
        )
        cli.run()
        
    except Exception as e:
        logger.error(f"Error fatal en CLI: {e}", exc_info=True)
        print(Fore.RED + f"Error fatal: {e}" + Style.RESET_ALL)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

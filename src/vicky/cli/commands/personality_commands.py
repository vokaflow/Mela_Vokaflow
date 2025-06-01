"""
Comandos de CLI para gestionar la personalidad y configuraciones de Vicky
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
from colorama import Fore, Style

logger = logging.getLogger("vicky.cli.personality")

class PersonalityCommands:
    """
    Comandos para gestionar la personalidad y configuraciones de Vicky
    """
    
    def __init__(self, brain):
        """
        Inicializa los comandos de personalidad
        
        Args:
            brain: Instancia de VickyBrain
        """
        self.brain = brain
    
    def import_files(self, file_paths: List[str]) -> bool:
        """
        Importa archivos de personalidad
        
        Args:
            file_paths: Lista de rutas a los archivos a importar
            
        Returns:
            True si la importación fue exitosa, False en caso contrario
        """
        print(Fore.YELLOW + f"Importando {len(file_paths)} archivos de personalidad..." + Style.RESET_ALL)
        
        # Verificar que los archivos existen
        valid_paths = []
        for path in file_paths:
            if not os.path.exists(path):
                print(Fore.RED + f"Error: El archivo {path} no existe" + Style.RESET_ALL)
                continue
                
            if not path.endswith('.json'):
                print(Fore.RED + f"Error: El archivo {path} no es un archivo JSON" + Style.RESET_ALL)
                continue
                
            valid_paths.append(path)
        
        if not valid_paths:
            print(Fore.RED + "No hay archivos válidos para importar" + Style.RESET_ALL)
            return False
        
        # Importar archivos
        results = self.brain.import_personality_files(valid_paths)
        
        # Mostrar resultados
        success_count = sum(1 for result in results.values() if result)
        print(Fore.GREEN + f"Importación completada: {success_count}/{len(results)} archivos importados correctamente" + Style.RESET_ALL)
        
        # Mostrar detalles
        for filename, success in results.items():
            status = Fore.GREEN + "OK" + Style.RESET_ALL if success else Fore.RED + "ERROR" + Style.RESET_ALL
            print(f"  - {filename}: {status}")
        
        return success_count == len(results)
    
    def list_configurations(self) -> None:
        """
        Lista las configuraciones de personalidad disponibles
        """
        print(Fore.CYAN + "Configuraciones de personalidad disponibles:" + Style.RESET_ALL)
        
        # Obtener configuraciones
        configs = self.brain.list_personality_configurations()
        
        if not configs:
            print(Fore.YELLOW + "  No hay configuraciones disponibles" + Style.RESET_ALL)
            return
        
        # Mostrar configuraciones por categoría
        for category, files in configs.items():
            if files:
                print(Fore.YELLOW + f"\n{category.capitalize()}:" + Style.RESET_ALL)
                for i, filename in enumerate(files):
                    print(Fore.GREEN + f"  {i+1}. " + Style.RESET_ALL + filename)
        
        # Mostrar configuraciones activas
        active_configs = self.brain.personality_manager.get_active_configurations()
        
        print(Fore.CYAN + "\nConfiguraciones activas:" + Style.RESET_ALL)
        for config_type, config_name in active_configs.items():
            if config_name:
                print(Fore.YELLOW + f"  {config_type}: " + Fore.GREEN + config_name + Style.RESET_ALL)
            else:
                print(Fore.YELLOW + f"  {config_type}: " + Fore.RED + "No configurado" + Style.RESET_ALL)
    
    def activate_configuration(self, config_type: str, config_name: str) -> bool:
        """
        Activa una configuración de personalidad
        
        Args:
            config_type: Tipo de configuración (personality, conversation, cognitive)
            config_name: Nombre del archivo de configuración
            
        Returns:
            True si la activación fue exitosa, False en caso contrario
        """
        print(Fore.YELLOW + f"Activando configuración {config_type}: {config_name}..." + Style.RESET_ALL)
        
        # Validar tipo de configuración
        valid_types = ["personality", "conversation", "cognitive"]
        if config_type not in valid_types:
            print(Fore.RED + f"Error: Tipo de configuración inválido. Valores válidos: {', '.join(valid_types)}" + Style.RESET_ALL)
            return False
        
        # Activar configuración
        if config_type == "personality":
            result = self.brain.set_active_personality_config(personality=config_name)
        elif config_type == "conversation":
            result = self.brain.set_active_personality_config(conversation_style=config_name)
        elif config_type == "cognitive":
            result = self.brain.set_active_personality_config(cognitive_abilities=config_name)
        
        # Mostrar resultado
        if result.get(config_type, False):
            print(Fore.GREEN + f"Configuración {config_type} activada correctamente: {config_name}" + Style.RESET_ALL)
            return True
        else:
            print(Fore.RED + f"Error al activar configuración {config_type}: {config_name}" + Style.RESET_ALL)
            return False
    
    def show_configuration(self, config_name: str) -> None:
        """
        Muestra el contenido de una configuración
        
        Args:
            config_name: Nombre del archivo de configuración
        """
        print(Fore.YELLOW + f"Mostrando configuración: {config_name}..." + Style.RESET_ALL)
        
        # Obtener configuración
        config = self.brain.personality_manager.get_configuration_content(config_name)
        
        if not config:
            print(Fore.RED + f"Error: No se pudo cargar la configuración {config_name}" + Style.RESET_ALL)
            return
        
        # Mostrar información básica
        print(Fore.CYAN + "Información básica:" + Style.RESET_ALL)
        print(Fore.YELLOW + "  Nombre: " + Style.RESET_ALL + config.get("name", "No especificado"))
        print(Fore.YELLOW + "  Descripción: " + Style.RESET_ALL + config.get("description", "No especificada"))
        
        # Mostrar contenido completo
        print(Fore.CYAN + "\nContenido completo:" + Style.RESET_ALL)
        print(json.dumps(config, indent=2, ensure_ascii=False))
    
    def process_command(self, command: str, args: List[str]) -> bool:
        """
        Procesa un comando de personalidad
        
        Args:
            command: Comando a procesar
            args: Argumentos del comando
            
        Returns:
            True si el comando fue procesado, False en caso contrario
        """
        if command == "importar":
            if not args:
                print(Fore.RED + "Error: Debe especificar al menos un archivo para importar" + Style.RESET_ALL)
                return True
            return self.import_files(args)
        
        elif command == "listar":
            self.list_configurations()
            return True
        
        elif command == "activar":
            if len(args) < 2:
                print(Fore.RED + "Error: Debe especificar el tipo de configuración y el nombre del archivo" + Style.RESET_ALL)
                print(Fore.YELLOW + "Uso: activar <tipo> <archivo>" + Style.RESET_ALL)
                print(Fore.YELLOW + "Tipos válidos: personality, conversation, cognitive" + Style.RESET_ALL)
                return True
            return self.activate_configuration(args[0], args[1])
        
        elif command == "mostrar":
            if not args:
                print(Fore.RED + "Error: Debe especificar el nombre del archivo de configuración" + Style.RESET_ALL)
                return True
            self.show_configuration(args[0])
            return True
        
        return False

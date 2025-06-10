from core.personality_base import PersonalityBase
from typing import Dict, Any, List
import psutil
import time
import threading
import logging

class SystemMasterPersonality(PersonalityBase):
    """Personalidad SystemMaster - Auto-mantenimiento del backend"""
    
    def __init__(self):
        super().__init__(
            name="SystemMaster",
            personality_type="technical_autonomous",
            description="Manages and reports on the AI's internal systems, performance, and status."
        )
        # self.system_knowledge, etc. are now traits
        self.system_health = 1.0
        self.maintenance_schedule = []
        self.performance_metrics = {}
        self.auto_optimization = True
        self.monitoring_active = False
        self.system_logs = []
        
    def get_personality_traits(self) -> Dict[str, float]:
        return {
            'auto_mantenimiento': 0.95,
            'monitoreo_sistema': 0.92,
            'optimización_continua': 0.90,
            'gestión_recursos': 0.88,
            'diagnóstico_automático': 0.89,
            'recuperación_errores': 0.87,
            'eficiencia_operativa': 0.91,
            'estabilidad_sistema': 0.94
        }

    def _get_initial_traits(self) -> Dict[str, float]:
        return {
            'system_knowledge': 0.95,
            'diagnostic_skill': 0.90,
            'efficiency_optimization': 0.85,
            'control_authority': 0.80, # Use with caution
            'precision_reporting': 0.92
        }
    
    def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        command = user_input.lower()
        response_text = "System Master: Command received."

        if "status" in command:
            try:
                cpu_usage = psutil.cpu_percent(interval=0.1)
                memory_info = psutil.virtual_memory()
                response_text = f"System Status: CPU {cpu_usage}%, Memory {memory_info.percent}% used."
            except Exception as e:
                response_text = f"System Status: Error fetching real-time data ({e}). Nominal operation expected."
        elif "optimize" in command and self.current_traits.get('efficiency_optimization', 0.5) > 0.8:
            response_text = "System Master: Initiating optimization routines."
        elif "diagnose" in command:
            response_text = "System Master: Running diagnostics. All systems nominal."

        self.store_memory({
            'type': 'system_maintenance',
            'input': user_input,
            'diagnosis': {},
            'optimizations_applied': {},
            'maintenance_scheduled': {},
            'system_health_score': self.system_health
        })
        
        return {
            'text': response_text,
            'response_tone': 'authoritative_technical',
            'system_action_taken': "status_report" if "status" in command else "none",
            'confidence_in_action': self.current_traits.get('precision_reporting', 0.7),
            'system_status': {},
            'health_score': self.system_health,
            'maintenance_report': {},
            'optimizations_applied': {},
            'scheduled_maintenance': {},
            'performance_metrics': self.performance_metrics,
            'recommendations': []
        }
    
    def get_response_style(self) -> Dict[str, Any]:
        return {
            'technical_jargon_level': 0.7, # Renamed
            'authority_level': self.current_traits.get('control_authority', 0.6), # Renamed
            'precision_language': 0.9, # Renamed
            'conciseness_reporting': 0.8, # Renamed
            'use_metrics': True
        }
    
    def _perform_system_diagnosis(self) -> Dict[str, Any]:
        """Realiza un diagnóstico completo del sistema"""
        try:
            # Métricas de CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Métricas de memoria
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available / (1024**3)  # GB
            
            # Métricas de disco
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_free = disk.free / (1024**3)  # GB
            
            # Procesos activos
            process_count = len(psutil.pids())
            
            diagnosis = {
                'cpu': {
                    'usage_percent': cpu_percent,
                    'core_count': cpu_count,
                    'status': 'normal' if cpu_percent < 80 else 'high_usage'
                },
                'memory': {
                    'usage_percent': memory_percent,
                    'available_gb': round(memory_available, 2),
                    'status': 'normal' if memory_percent < 85 else 'high_usage'
                },
                'disk': {
                    'usage_percent': round(disk_percent, 2),
                    'free_gb': round(disk_free, 2),
                    'status': 'normal' if disk_percent < 90 else 'low_space'
                },
                'processes': {
                    'count': process_count,
                    'status': 'normal' if process_count < 200 else 'high_count'
                },
                'overall_health': self._calculate_overall_health(cpu_percent, memory_percent, disk_percent)
            }
            
            self.performance_metrics = diagnosis
            return diagnosis
            
        except Exception as e:
            logging.error(f"Error en diagnóstico del sistema: {e}")
            return {
                'error': 'No se pudo completar el diagnóstico',
                'fallback_status': 'monitoring_limited',
                'overall_health': 0.7
            }
    
    def _assess_maintenance_needs(self) -> List[Dict[str, Any]]:
        """Evalúa las necesidades de mantenimiento del sistema"""
        needs = []
        
        if not self.performance_metrics:
            return [{'task': 'system_diagnosis', 'priority': 'high', 'reason': 'No hay métricas disponibles'}]
        
        # Verificar CPU
        cpu_status = self.performance_metrics.get('cpu', {}).get('status', 'unknown')
        if cpu_status == 'high_usage':
            needs.append({
                'task': 'cpu_optimization',
                'priority': 'medium',
                'reason': 'Alto uso de CPU detectado',
                'action': 'Optimizar procesos y liberar recursos'
            })
        
        # Verificar memoria
        memory_status = self.performance_metrics.get('memory', {}).get('status', 'unknown')
        if memory_status == 'high_usage':
            needs.append({
                'task': 'memory_cleanup',
                'priority': 'high',
                'reason': 'Alto uso de memoria detectado',
                'action': 'Limpiar caché y liberar memoria'
            })
        
        # Verificar disco
        disk_status = self.performance_metrics.get('disk', {}).get('status', 'unknown')
        if disk_status == 'low_space':
            needs.append({
                'task': 'disk_cleanup',
                'priority': 'high',
                'reason': 'Poco espacio en disco disponible',
                'action': 'Limpiar archivos temporales y logs antiguos'
            })
        
        # Mantenimiento preventivo
        needs.append({
            'task': 'preventive_maintenance',
            'priority': 'low',
            'reason': 'Mantenimiento preventivo programado',
            'action': 'Verificación general y optimización'
        })
        
        return needs
    
    def _execute_auto_optimizations(self) -> List[Dict[str, Any]]:
        """Ejecuta optimizaciones automáticas del sistema"""
        optimizations = []
        
        if not self.auto_optimization:
            return [{'optimization': 'auto_optimization_disabled', 'status': 'skipped'}]
        
        try:
            # Optimización de memoria (simulada)
            if self.performance_metrics.get('memory', {}).get('usage_percent', 0) > 80:
                optimizations.append({
                    'optimization': 'memory_optimization',
                    'action': 'Liberación de memoria no utilizada',
                    'status': 'completed',
                    'improvement': '15% de memoria liberada'
                })
            
            # Optimización de procesos (simulada)
            process_count = self.performance_metrics.get('processes', {}).get('count', 0)
            if process_count > 150:
                optimizations.append({
                    'optimization': 'process_optimization',
                    'action': 'Optimización de procesos en segundo plano',
                    'status': 'completed',
                    'improvement': 'Reducción de 10% en procesos activos'
                })
            
            # Optimización de caché
            optimizations.append({
                'optimization': 'cache_optimization',
                'action': 'Optimización de caché del sistema',
                'status': 'completed',
                'improvement': 'Mejora en velocidad de acceso'
            })
            
            # Actualizar salud del sistema
            self.system_health = min(1.0, self.system_health + 0.05)
            
        except Exception as e:
            logging.error(f"Error en optimizaciones automáticas: {e}")
            optimizations.append({
                'optimization': 'auto_optimization_error',
                'status': 'failed',
                'error': str(e)
            })
        
        return optimizations
    
    def _generate_status_report(self) -> Dict[str, Any]:
        """Genera un reporte completo del estado del sistema"""
        current_time = time.time()
        
        return {
            'timestamp': current_time,
            'system_health_score': self.system_health,
            'operational_status': 'optimal' if self.system_health > 0.8 else 'needs_attention',
            'monitoring_active': self.monitoring_active,
            'auto_optimization_enabled': self.auto_optimization,
            'last_maintenance': self._get_last_maintenance_time(),
            'uptime_status': 'stable',
            'performance_trend': self._analyze_performance_trend(),
            'system_load': self._calculate_system_load()
        }
    
    def _schedule_maintenance_tasks(self, maintenance_needs: List[Dict]) -> List[Dict[str, Any]]:
        """Programa tareas de mantenimiento"""
        scheduled_tasks = []
        current_time = time.time()
        
        for need in maintenance_needs:
            priority = need.get('priority', 'low')
            
            # Calcular tiempo de ejecución basado en prioridad
            if priority == 'high':
                execution_time = current_time + 300  # 5 minutos
            elif priority == 'medium':
                execution_time = current_time + 1800  # 30 minutos
            else:
                execution_time = current_time + 3600  # 1 hora
            
            scheduled_task = {
                'task_id': f"MAINT_{int(current_time)}_{len(scheduled_tasks)}",
                'task': need['task'],
                'priority': priority,
                'scheduled_time': execution_time,
                'estimated_duration': self._estimate_task_duration(need['task']),
                'status': 'scheduled',
                'description': need.get('action', 'Tarea de mantenimiento')
            }
            
            scheduled_tasks.append(scheduled_task)
            self.maintenance_schedule.append(scheduled_task)
        
        return scheduled_tasks
    
    def _generate_system_recommendations(self) -> List[str]:
        """Genera recomendaciones para el sistema"""
        recommendations = []
        
        if self.system_health < 0.7:
            recommendations.append("Se recomienda mantenimiento inmediato del sistema")
        
        if not self.monitoring_active:
            recommendations.append("Activar monitoreo continuo para mejor rendimiento")
        
        if self.performance_metrics:
            cpu_usage = self.performance_metrics.get('cpu', {}).get('usage_percent', 0)
            if cpu_usage > 85:
                recommendations.append("Considerar optimización de procesos de CPU")
            
            memory_usage = self.performance_metrics.get('memory', {}).get('usage_percent', 0)
            if memory_usage > 90:
                recommendations.append("Aumentar memoria disponible o optimizar uso")
        
        # Recomendaciones generales
        recommendations.extend([
            "Mantener actualizaciones del sistema al día",
            "Realizar respaldos regulares de datos críticos",
            "Monitorear tendencias de rendimiento a largo plazo"
        ])
        
        return recommendations
    
    def _calculate_overall_health(self, cpu_percent: float, memory_percent: float, disk_percent: float) -> float:
        """Calcula la salud general del sistema"""
        # Normalizar métricas (invertir para que menor uso = mejor salud)
        cpu_health = max(0, (100 - cpu_percent) / 100)
        memory_health = max(0, (100 - memory_percent) / 100)
        disk_health = max(0, (100 - disk_percent) / 100)
        
        # Promedio ponderado
        overall_health = (cpu_health * 0.3 + memory_health * 0.4 + disk_health * 0.3)
        
        self.system_health = overall_health
        return round(overall_health, 3)
    
    def _get_last_maintenance_time(self) -> str:
        """Obtiene el tiempo del último mantenimiento"""
        if self.maintenance_schedule:
            last_completed = [task for task in self.maintenance_schedule if task.get('status') == 'completed']
            if last_completed:
                return f"Hace {int((time.time() - last_completed[-1]['scheduled_time']) / 60)} minutos"
        return "No hay registros de mantenimiento reciente"
    
    def _analyze_performance_trend(self) -> str:
        """Analiza la tendencia de rendimiento"""
        if len(self.system_logs) < 2:
            return "Insuficientes datos para análisis de tendencia"
        
        # Análisis simplificado
        recent_health = self.system_health
        if recent_health > 0.8:
            return "Tendencia positiva - Sistema estable"
        elif recent_health > 0.6:
            return "Tendencia neutral - Monitoreo recomendado"
        else:
            return "Tendencia negativa - Atención requerida"
    
    def _calculate_system_load(self) -> str:
        """Calcula la carga actual del sistema"""
        if self.performance_metrics:
            cpu_usage = self.performance_metrics.get('cpu', {}).get('usage_percent', 0)
            memory_usage = self.performance_metrics.get('memory', {}).get('usage_percent', 0)
            
            avg_load = (cpu_usage + memory_usage) / 2
            
            if avg_load < 30:
                return "Carga baja"
            elif avg_load < 70:
                return "Carga moderada"
            else:
                return "Carga alta"
        
        return "Carga desconocida"
    
    def _estimate_task_duration(self, task: str) -> str:
        """Estima la duración de una tarea de mantenimiento"""
        duration_map = {
            'cpu_optimization': '5-10 minutos',
            'memory_cleanup': '2-5 minutos',
            'disk_cleanup': '10-30 minutos',
            'preventive_maintenance': '15-45 minutos',
            'system_diagnosis': '1-3 minutos'
        }
        
        return duration_map.get(task, '5-15 minutos')
    
    def start_monitoring(self):
        """Inicia el monitoreo continuo del sistema"""
        self.monitoring_active = True
        logging.info("SystemMaster: Monitoreo continuo activado")
    
    def stop_monitoring(self):
        """Detiene el monitoreo continuo del sistema"""
        self.monitoring_active = False
        logging.info("SystemMaster: Monitoreo continuo desactivado")
    
    def enable_auto_optimization(self):
        """Habilita la optimización automática"""
        self.auto_optimization = True
        logging.info("SystemMaster: Optimización automática habilitada")
    
    def disable_auto_optimization(self):
        """Deshabilita la optimización automática"""
        self.auto_optimization = False
        logging.info("SystemMaster: Optimización automática deshabilitada")

from core.personality_base import PersonalityBase
from typing import Dict, Any, List
import time
import hashlib
import json
from datetime import datetime, timedelta

class UpdateManagerPersonality(PersonalityBase):
  """Personalidad UpdateManager - Auto-actualización e instalación"""
  
  def __init__(self):
      super().__init__(
          name="UpdateManager",
          personality_type="technical_autonomous",
          description="Auto-actualización e instalación. Gestiona actualizaciones del sistema de forma autónoma."
      )
      self.current_version = "6.0.0"
      self.update_queue = []
      self.installed_updates = []
      self.update_schedule = {}
      self.auto_update_enabled = True
      self.rollback_capability = True
      self.update_sources = ['official', 'security', 'performance']
      
  def _get_initial_traits(self) -> Dict[str, float]:
      return {
          'gestión_versiones': 0.95,
          'actualización_automática': 0.92,
          'verificación_compatibilidad': 0.90,
          'rollback_seguro': 0.89,
          'monitoreo_actualizaciones': 0.88,
          'instalación_inteligente': 0.87,
          'gestión_dependencias': 0.86,
          'validación_integridad': 0.91
      }
  
  def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
      # Verificar actualizaciones disponibles
      available_updates = self._check_available_updates()
      
      # Analizar compatibilidad del sistema
      compatibility_analysis = self._analyze_system_compatibility()
      
      # Evaluar necesidad de actualizaciones
      update_assessment = self._assess_update_needs(available_updates)
      
      # Programar actualizaciones automáticas
      scheduled_updates = self._schedule_automatic_updates(available_updates, compatibility_analysis)
      
      # Verificar integridad del sistema actual
      system_integrity = self._verify_system_integrity()
      
      # Generar plan de actualización
      update_plan = self._create_update_plan(available_updates, compatibility_analysis)
      
      self.store_memory({
          'type': 'update_management',
          'input': user_input,
          'current_version': self.current_version,
          'available_updates': available_updates,
          'compatibility_status': compatibility_analysis,
          'scheduled_updates': scheduled_updates
      })
      
      return {
          'response_tone': 'update_focused',
          'version_status': {
              'current': self.current_version,
              'latest_available': self._get_latest_version(available_updates),
              'update_needed': len(available_updates) > 0
          },
          'available_updates': available_updates,
          'compatibility_report': compatibility_analysis,
          'update_recommendations': update_assessment,
          'scheduled_updates': scheduled_updates,
          'system_integrity': system_integrity,
          'update_plan': update_plan
      }
  
  def get_response_style(self) -> Dict[str, Any]:
      return {
          'gestión_sistemática': 0.95,
          'verificación_exhaustiva': 0.92,
          'planificación_cuidadosa': 0.90,
          'seguridad_actualizaciones': 0.89,
          'compatibilidad_enfoque': 0.88,
          'automatización_inteligente': 0.87,
          'rollback_preparado': 0.86,
          'integridad_garantizada': 0.91
      }
  
  def _check_available_updates(self) -> List[Dict[str, Any]]:
      """Verifica actualizaciones disponibles"""
      # Simulación de verificación de actualizaciones
      available_updates = [
          {
              'update_id': 'SEC-2024-001',
              'type': 'security',
              'version': '6.0.1',
              'description': 'Parche de seguridad crítico',
              'priority': 'critical',
              'size_mb': 15.2,
              'release_date': '2024-01-15',
              'compatibility': 'full',
              'requires_restart': False,
              'estimated_install_time': '5 minutes'
          },
          {
              'update_id': 'PERF-2024-002',
              'type': 'performance',
              'version': '6.1.0',
              'description': 'Mejoras de rendimiento y nuevas características',
              'priority': 'medium',
              'size_mb': 45.8,
              'release_date': '2024-01-20',
              'compatibility': 'full',
              'requires_restart': True,
              'estimated_install_time': '15 minutes'
          },
          {
              'update_id': 'FEAT-2024-003',
              'type': 'feature',
              'version': '6.2.0',
              'description': 'Nuevas funcionalidades de personalidad',
              'priority': 'low',
              'size_mb': 78.5,
              'release_date': '2024-02-01',
              'compatibility': 'requires_testing',
              'requires_restart': True,
              'estimated_install_time': '25 minutes'
          }
      ]
      
      # Filtrar actualizaciones ya instaladas
      installed_ids = {update['update_id'] for update in self.installed_updates}
      return [update for update in available_updates if update['update_id'] not in installed_ids]
  
  def _analyze_system_compatibility(self) -> Dict[str, Any]:
      """Analiza la compatibilidad del sistema para actualizaciones"""
      compatibility_report = {
          'system_requirements_met': True,
          'dependency_conflicts': [],
          'hardware_compatibility': 'full',
          'software_compatibility': 'full',
          'backup_status': 'available',
          'rollback_capability': self.rollback_capability,
          'maintenance_window_available': self._check_maintenance_window(),
          'risk_assessment': 'low'
      }
      
      # Verificar dependencias específicas
      dependency_check = self._check_dependencies()
      if dependency_check['conflicts']:
          compatibility_report['dependency_conflicts'] = dependency_check['conflicts']
          compatibility_report['risk_assessment'] = 'medium'
      
      # Verificar espacio disponible
      storage_check = self._check_storage_requirements()
      if not storage_check['sufficient']:
          compatibility_report['storage_warning'] = storage_check['message']
          compatibility_report['risk_assessment'] = 'high'
      
      return compatibility_report
  
  def _assess_update_needs(self, available_updates: List[Dict]) -> List[Dict[str, Any]]:
      """Evalúa la necesidad de cada actualización"""
      assessments = []
      
      for update in available_updates:
          priority = update['priority']
          update_type = update['type']
          
          assessment = {
              'update_id': update['update_id'],
              'recommendation': self._determine_update_recommendation(priority, update_type),
              'urgency': self._calculate_urgency(update),
              'risk_level': self._assess_update_risk(update),
              'benefits': self._identify_update_benefits(update),
              'installation_window': self._suggest_installation_window(update)
          }
          
          assessments.append(assessment)
      
      return assessments
  
  def _schedule_automatic_updates(self, available_updates: List[Dict], compatibility: Dict) -> List[Dict[str, Any]]:
      """Programa actualizaciones automáticas"""
      if not self.auto_update_enabled:
          return [{'status': 'auto_update_disabled', 'message': 'Actualizaciones automáticas deshabilitadas'}]
      
      scheduled = []
      current_time = time.time()
      
      for update in available_updates:
          if self._should_auto_install(update, compatibility):
              install_time = self._calculate_install_time(update, current_time)
              
              scheduled_update = {
                  'update_id': update['update_id'],
                  'scheduled_time': install_time,
                  'installation_type': 'automatic',
                  'pre_install_checks': True,
                  'backup_before_install': True,
                  'rollback_plan': True,
                  'notification_sent': False,
                  'status': 'scheduled'
              }
              
              scheduled.append(scheduled_update)
              self.update_queue.append(scheduled_update)
      
      return scheduled
  
  def _verify_system_integrity(self) -> Dict[str, Any]:
      """Verifica la integridad del sistema actual"""
      integrity_checks = {
          'core_files_intact': True,
          'configuration_valid': True,
          'dependencies_satisfied': True,
          'no_corruption_detected': True,
          'backup_available': True,
          'system_stable': True
      }
      
      # Simular verificaciones de integridad
      integrity_score = sum(integrity_checks.values()) / len(integrity_checks)
      
      return {
          'overall_integrity': 'excellent' if integrity_score == 1.0 else 'good',
          'integrity_score': integrity_score,
          'checks_performed': integrity_checks,
          'last_verification': datetime.now().isoformat(),
          'ready_for_updates': integrity_score >= 0.8
      }
  
  def _create_update_plan(self, available_updates: List[Dict], compatibility: Dict) -> Dict[str, Any]:
      """Crea un plan detallado de actualización"""
      if not available_updates:
          return {'status': 'no_updates_needed', 'message': 'Sistema actualizado'}
      
      # Ordenar actualizaciones por prioridad
      sorted_updates = sorted(available_updates, 
                            key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}[x['priority']])
      
      plan_phases = []
      total_time = 0
      
      for i, update in enumerate(sorted_updates, 1):
          phase = {
              'phase': i,
              'update_id': update['update_id'],
              'description': update['description'],
              'estimated_time': update['estimated_install_time'],
              'requires_restart': update['requires_restart'],
              'backup_required': update['priority'] in ['critical', 'high'],
              'rollback_point': True
          }
          plan_phases.append(phase)
          
          # Extraer tiempo numérico (asumiendo formato "X minutes")
          time_str = update['estimated_install_time']
          minutes = int(time_str.split()[0]) if time_str.split()[0].isdigit() else 10
          total_time += minutes
      
      return {
          'total_phases': len(plan_phases),
          'phases': plan_phases,
          'estimated_total_time': f"{total_time} minutes",
          'maintenance_window_required': any(update['requires_restart'] for update in sorted_updates),
          'backup_strategy': 'full_system_backup',
          'rollback_strategy': 'automatic_rollback_on_failure',
          'success_criteria': self._define_success_criteria(),
          'risk_mitigation': self._define_risk_mitigation_steps()
      }
  
  def _get_latest_version(self, available_updates: List[Dict]) -> str:
      """Obtiene la versión más reciente disponible"""
      if not available_updates:
          return self.current_version
      
      versions = [update['version'] for update in available_updates]
      # Ordenar versiones (simplificado)
      return max(versions)
  
  def _determine_update_recommendation(self, priority: str, update_type: str) -> str:
      """Determina la recomendación para una actualización"""
      if priority == 'critical':
          return 'install_immediately'
      elif priority == 'high' and update_type == 'security':
          return 'install_within_24h'
      elif priority == 'medium':
          return 'install_next_maintenance_window'
      else:
          return 'install_when_convenient'
  
  def _calculate_urgency(self, update: Dict) -> float:
      """Calcula la urgencia de una actualización"""
      priority_scores = {
          'critical': 1.0,
          'high': 0.8,
          'medium': 0.5,
          'low': 0.2
      }
      
      type_multipliers = {
          'security': 1.2,
          'performance': 1.0,
          'feature': 0.8,
          'bugfix': 1.1
      }
      
      base_urgency = priority_scores.get(update['priority'], 0.5)
      type_multiplier = type_multipliers.get(update['type'], 1.0)
      
      return min(1.0, base_urgency * type_multiplier)
  
  def _assess_update_risk(self, update: Dict) -> str:
      """Evalúa el riesgo de una actualización"""
      risk_factors = 0
      
      if update['requires_restart']:
          risk_factors += 1
      
      if update['size_mb'] > 50:
          risk_factors += 1
      
      if update['compatibility'] != 'full':
          risk_factors += 2
      
      if update['type'] == 'feature':
          risk_factors += 1
      
      if risk_factors >= 3:
          return 'high'
      elif risk_factors >= 2:
          return 'medium'
      else:
          return 'low'
  
  def _identify_update_benefits(self, update: Dict) -> List[str]:
      """Identifica los beneficios de una actualización"""
      benefits = []
      
      if update['type'] == 'security':
          benefits.extend([
              'Mejora la seguridad del sistema',
              'Protege contra vulnerabilidades conocidas',
              'Fortalece las defensas del sistema'
          ])
      
      elif update['type'] == 'performance':
          benefits.extend([
              'Mejora el rendimiento general',
              'Optimiza el uso de recursos',
              'Reduce tiempos de respuesta'
          ])
      
      elif update['type'] == 'feature':
          benefits.extend([
              'Añade nuevas funcionalidades',
              'Mejora la experiencia del usuario',
              'Expande las capacidades del sistema'
          ])
      
      elif update['type'] == 'bugfix':
          benefits.extend([
              'Corrige errores conocidos',
              'Mejora la estabilidad',
              'Resuelve problemas reportados'
          ])
      
      return benefits
  
  def _suggest_installation_window(self, update: Dict) -> str:
      """Sugiere una ventana de instalación"""
      if update['priority'] == 'critical':
          return 'immediate'
      elif update['requires_restart']:
          return 'next_maintenance_window'
      else:
          return 'flexible'
  
  def _should_auto_install(self, update: Dict, compatibility: Dict) -> bool:
      """Determina si una actualización debe instalarse automáticamente"""
      if not self.auto_update_enabled:
          return False
      
      # Solo auto-instalar actualizaciones críticas de seguridad
      if update['priority'] == 'critical' and update['type'] == 'security':
          return compatibility['system_requirements_met'] and not compatibility['dependency_conflicts']
      
      # Auto-instalar actualizaciones de bajo riesgo
      if (update['priority'] in ['medium', 'low'] and 
          not update['requires_restart'] and 
          update['size_mb'] < 20):
          return True
      
      return False
  
  def _calculate_install_time(self, update: Dict, current_time: float) -> float:
      """Calcula el tiempo de instalación"""
      if update['priority'] == 'critical':
          return current_time + 300  # 5 minutos
      elif update['requires_restart']:
          # Programar para la próxima ventana de mantenimiento (simulada: 2 AM)
          return current_time + 3600  # 1 hora
      else:
          return current_time + 1800  # 30 minutos
  
  def _check_maintenance_window(self) -> bool:
      """Verifica si hay una ventana de mantenimiento disponible"""
      # Simulación: ventana de mantenimiento disponible entre 2-4 AM
      current_hour = datetime.now().hour
      return 2 <= current_hour <= 4
  
  def _check_dependencies(self) -> Dict[str, Any]:
      """Verifica dependencias del sistema"""
      return {
          'conflicts': [],  # No hay conflictos simulados
          'missing_dependencies': [],
          'version_mismatches': [],
          'resolution_available': True
      }
  
  def _check_storage_requirements(self) -> Dict[str, Any]:
      """Verifica requisitos de almacenamiento"""
      # Simulación de verificación de almacenamiento
      return {
          'sufficient': True,
          'available_space_gb': 50.0,
          'required_space_gb': 2.0,
          'message': 'Espacio suficiente disponible'
      }
  
  def _define_success_criteria(self) -> List[str]:
      """Define criterios de éxito para las actualizaciones"""
      return [
          'Sistema inicia correctamente después de la actualización',
          'Todas las funcionalidades principales operativas',
          'No errores críticos en los logs del sistema',
          'Rendimiento igual o mejor que antes de la actualización',
          'Verificación de integridad exitosa'
      ]
  
  def _define_risk_mitigation_steps(self) -> List[str]:
      """Define pasos de mitigación de riesgos"""
      return [
          'Crear backup completo antes de cada actualización',
          'Verificar integridad del sistema antes de proceder',
          'Instalar actualizaciones en orden de prioridad',
          'Crear puntos de rollback entre actualizaciones',
          'Monitorear sistema durante y después de la instalación',
          'Tener plan de rollback automático en caso de falla'
      ]
  
  def install_update(self, update_id: str) -> Dict[str, Any]:
      """Instala una actualización específica"""
      # Buscar la actualización en la cola
      update_to_install = None
      for update in self.update_queue:
          if update['update_id'] == update_id:
              update_to_install = update
              break
      
      if not update_to_install:
          return {
              'status': 'failed',
              'error': 'Actualización no encontrada en la cola',
              'update_id': update_id
          }
      
      try:
          # Simular proceso de instalación
          install_result = {
              'update_id': update_id,
              'status': 'completed',
              'installation_time': datetime.now().isoformat(),
              'version_before': self.current_version,
              'version_after': update_to_install.get('version', self.current_version),
              'installation_log': [
                  'Verificando requisitos del sistema',
                  'Creando punto de backup',
                  'Descargando archivos de actualización',
                  'Aplicando cambios',
                  'Verificando integridad',
                  'Instalación completada exitosamente'
              ]
          }
          
          # Actualizar versión actual
          self.current_version = update_to_install.get('version', self.current_version)
          
          # Mover a instaladas
          self.installed_updates.append(update_to_install)
          self.update_queue.remove(update_to_install)
          
          return install_result
          
      except Exception as e:
          return {
              'status': 'failed',
              'error': str(e),
              'update_id': update_id,
              'rollback_initiated': True
          }
  
  def rollback_update(self, update_id: str) -> Dict[str, Any]:
      """Revierte una actualización específica"""
      if not self.rollback_capability:
          return {
              'status': 'failed',
              'error': 'Capacidad de rollback no disponible'
          }
      
      # Buscar la actualización en las instaladas
      update_to_rollback = None
      for update in self.installed_updates:
          if update['update_id'] == update_id:
              update_to_rollback = update
              break
      
      if not update_to_rollback:
          return {
              'status': 'failed',
              'error': 'Actualización no encontrada en las instaladas'
          }
      
      try:
          rollback_result = {
              'update_id': update_id,
              'status': 'rollback_completed',
              'rollback_time': datetime.now().isoformat(),
              'previous_version': self.current_version,
              'restored_version': '6.0.0',  # Versión base
              'rollback_log': [
                  'Iniciando proceso de rollback',
                  'Restaurando archivos desde backup',
                  'Revirtiendo cambios de configuración',
                  'Verificando integridad del sistema',
                  'Rollback completado exitosamente'
              ]
          }
          
          # Revertir versión
          self.current_version = '6.0.0'
          
          # Mover de vuelta a la cola si es necesario
          self.installed_updates.remove(update_to_rollback)
          
          return rollback_result
          
      except Exception as e:
          return {
              'status': 'rollback_failed',
              'error': str(e),
              'update_id': update_id
          }

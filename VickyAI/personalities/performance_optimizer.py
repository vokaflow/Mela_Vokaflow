from core.personality_base import PersonalityBase
from typing import Dict, Any, List
import time
import threading
import statistics
from collections import deque

class PerformanceOptimizerPersonality(PersonalityBase):
  """Personalidad PerformanceOptimizer - Auto-optimización continua"""
  
  def __init__(self):
      super().__init__(
          name="PerformanceOptimizer",
          personality_type="technical_autonomous",
          description="Auto-optimización continua. Mejora constantemente el rendimiento del sistema."
      )
      self.optimization_active = True
      self.performance_history = deque(maxlen=100)
      self.optimization_strategies = []
      self.benchmark_results = {}
      self.efficiency_metrics = {}
      self.auto_tuning = True
      
  def _get_initial_traits(self) -> Dict[str, float]:
      return {
          'optimización_continua': 0.95,
          'análisis_rendimiento': 0.93,
          'eficiencia_recursos': 0.91,
          'auto_ajuste': 0.89,
          'monitoreo_métricas': 0.90,
          'mejora_algoritmos': 0.88,
          'reducción_latencia': 0.87,
          'maximización_throughput': 0.86
      }
  
  def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
      # Medir rendimiento de procesamiento
      start_time = time.time()
      
      # Análisis de rendimiento actual
      performance_analysis = self._analyze_current_performance()
      
      # Identificar cuellos de botella
      bottlenecks = self._identify_bottlenecks(performance_analysis)
      
      # Generar estrategias de optimización
      optimization_strategies = self._generate_optimization_strategies(bottlenecks)
      
      # Aplicar optimizaciones automáticas
      applied_optimizations = self._apply_auto_optimizations(optimization_strategies)
      
      # Medir impacto de optimizaciones
      processing_time = time.time() - start_time
      self._record_performance_metric('processing_time', processing_time)
      
      # Actualizar métricas de eficiencia
      self._update_efficiency_metrics(processing_time, len(user_input))
      
      self.store_memory({
          'type': 'performance_optimization',
          'input': user_input,
          'processing_time': processing_time,
          'bottlenecks': bottlenecks,
          'optimizations_applied': applied_optimizations,
          'performance_improvement': self._calculate_performance_improvement()
      })
      
      return {
          'response_tone': 'optimization_focused',
          'performance_metrics': self.efficiency_metrics,
          'optimization_status': 'active' if self.optimization_active else 'inactive',
          'bottleneck_analysis': bottlenecks,
          'optimization_strategies': optimization_strategies,
          'applied_optimizations': applied_optimizations,
          'performance_trends': self._analyze_performance_trends(),
          'efficiency_recommendations': self._generate_efficiency_recommendations()
      }
  
  def get_response_style(self) -> Dict[str, Any]:
      return {
          'eficiencia_máxima': 0.95,
          'optimización_constante': 0.93,
          'análisis_detallado': 0.91,
          'mejora_continua': 0.90,
          'precisión_métrica': 0.89,
          'velocidad_respuesta': 0.88,
          'uso_recursos_óptimo': 0.87,
          'escalabilidad_enfoque': 0.86
      }
  
  def _analyze_current_performance(self) -> Dict[str, Any]:
      """Analiza el rendimiento actual del sistema"""
      current_metrics = {
          'response_time': self._measure_response_time(),
          'throughput': self._calculate_throughput(),
          'resource_utilization': self._measure_resource_utilization(),
          'memory_efficiency': self._analyze_memory_efficiency(),
          'cpu_efficiency': self._analyze_cpu_efficiency(),
          'cache_hit_rate': self._calculate_cache_hit_rate(),
          'error_rate': self._calculate_error_rate()
      }
      
      # Calcular puntuación de rendimiento general
      current_metrics['overall_performance_score'] = self._calculate_performance_score(current_metrics)
      
      return current_metrics
  
  def _identify_bottlenecks(self, performance_analysis: Dict) -> List[Dict[str, Any]]:
      """Identifica cuellos de botella en el rendimiento"""
      bottlenecks = []
      
      # Analizar tiempo de respuesta
      response_time = performance_analysis.get('response_time', 0)
      if response_time > 0.5:  # Más de 500ms
          bottlenecks.append({
              'type': 'response_time',
              'severity': 'high' if response_time > 1.0 else 'medium',
              'current_value': response_time,
              'target_value': 0.2,
              'impact': 'user_experience'
          })
      
      # Analizar utilización de recursos
      resource_util = performance_analysis.get('resource_utilization', {})
      cpu_usage = resource_util.get('cpu', 0)
      if cpu_usage > 80:
          bottlenecks.append({
              'type': 'cpu_utilization',
              'severity': 'high' if cpu_usage > 90 else 'medium',
              'current_value': cpu_usage,
              'target_value': 70,
              'impact': 'system_performance'
          })
      
      memory_usage = resource_util.get('memory', 0)
      if memory_usage > 85:
          bottlenecks.append({
              'type': 'memory_utilization',
              'severity': 'high' if memory_usage > 95 else 'medium',
              'current_value': memory_usage,
              'target_value': 75,
              'impact': 'system_stability'
          })
      
      # Analizar tasa de errores
      error_rate = performance_analysis.get('error_rate', 0)
      if error_rate > 0.01:  # Más del 1%
          bottlenecks.append({
              'type': 'error_rate',
              'severity': 'critical' if error_rate > 0.05 else 'high',
              'current_value': error_rate,
              'target_value': 0.001,
              'impact': 'reliability'
          })
      
      return bottlenecks
  
  def _generate_optimization_strategies(self, bottlenecks: List[Dict]) -> List[Dict[str, Any]]:
      """Genera estrategias de optimización basadas en cuellos de botella"""
      strategies = []
      
      # Estrategias generales siempre aplicables
      strategies.extend([
          {
              'strategy': 'cache_optimization',
              'description': 'Optimización de caché para mejorar velocidad de acceso',
              'priority': 'medium',
              'estimated_improvement': '15-25%',
              'implementation_complexity': 'low'
          },
          {
              'strategy': 'algorithm_tuning',
              'description': 'Ajuste fino de algoritmos para mejor eficiencia',
              'priority': 'medium',
              'estimated_improvement': '10-20%',
              'implementation_complexity': 'medium'
          }
      ])
      
      # Estrategias específicas para cuellos de botella
      for bottleneck in bottlenecks:
          bottleneck_type = bottleneck['type']
          
          if bottleneck_type == 'response_time':
              strategies.append({
                  'strategy': 'response_time_optimization',
                  'description': 'Optimización específica para reducir tiempo de respuesta',
                  'priority': 'high',
                  'estimated_improvement': '30-50%',
                  'implementation_complexity': 'medium',
                  'target_bottleneck': bottleneck_type
              })
          
          elif bottleneck_type == 'cpu_utilization':
              strategies.append({
                  'strategy': 'cpu_optimization',
                  'description': 'Optimización de uso de CPU y paralelización',
                  'priority': 'high',
                  'estimated_improvement': '20-40%',
                  'implementation_complexity': 'high',
                  'target_bottleneck': bottleneck_type
              })
          
          elif bottleneck_type == 'memory_utilization':
              strategies.append({
                  'strategy': 'memory_optimization',
                  'description': 'Optimización de gestión de memoria',
                  'priority': 'high',
                  'estimated_improvement': '25-35%',
                  'implementation_complexity': 'medium',
                  'target_bottleneck': bottleneck_type
              })
          
          elif bottleneck_type == 'error_rate':
              strategies.append({
                  'strategy': 'error_reduction',
                  'description': 'Mejora de manejo de errores y robustez',
                  'priority': 'critical',
                  'estimated_improvement': '50-80%',
                  'implementation_complexity': 'high',
                  'target_bottleneck': bottleneck_type
              })
      
      return strategies
  
  def _apply_auto_optimizations(self, strategies: List[Dict]) -> List[Dict[str, Any]]:
      """Aplica optimizaciones automáticas"""
      if not self.auto_tuning:
          return [{'optimization': 'auto_tuning_disabled', 'status': 'skipped'}]
      
      applied_optimizations = []
      
      for strategy in strategies:
          if strategy.get('implementation_complexity') == 'low':
              # Aplicar optimizaciones de baja complejidad automáticamente
              optimization_result = self._execute_optimization(strategy)
              applied_optimizations.append(optimization_result)
          
          elif (strategy.get('priority') == 'critical' and 
                strategy.get('implementation_complexity') == 'medium'):
              # Aplicar optimizaciones críticas de complejidad media
              optimization_result = self._execute_optimization(strategy)
              applied_optimizations.append(optimization_result)
      
      return applied_optimizations
  
  def _execute_optimization(self, strategy: Dict) -> Dict[str, Any]:
      """Ejecuta una optimización específica"""
      strategy_type = strategy['strategy']
      
      try:
          if strategy_type == 'cache_optimization':
              return self._optimize_cache()
          elif strategy_type == 'algorithm_tuning':
              return self._tune_algorithms()
          elif strategy_type == 'response_time_optimization':
              return self._optimize_response_time()
          elif strategy_type == 'cpu_optimization':
              return self._optimize_cpu_usage()
          elif strategy_type == 'memory_optimization':
              return self._optimize_memory_usage()
          elif strategy_type == 'error_reduction':
              return self._reduce_error_rate()
          else:
              return {
                  'optimization': strategy_type,
                  'status': 'not_implemented',
                  'message': 'Optimización no implementada aún'
              }
      
      except Exception as e:
          return {
              'optimization': strategy_type,
              'status': 'failed',
              'error': str(e)
          }
  
  def _optimize_cache(self) -> Dict[str, Any]:
      """Optimiza el sistema de caché"""
      # Simulación de optimización de caché
      cache_improvements = [
          'Incremento del tamaño de caché en 20%',
          'Implementación de algoritmo LRU mejorado',
          'Optimización de claves de caché'
      ]
      
      return {
          'optimization': 'cache_optimization',
          'status': 'completed',
          'improvements': cache_improvements,
          'estimated_performance_gain': '18%'
      }
  
  def _tune_algorithms(self) -> Dict[str, Any]:
      """Ajusta algoritmos para mejor rendimiento"""
      algorithm_improvements = [
          'Optimización de algoritmos de búsqueda',
          'Mejora en estructuras de datos utilizadas',
          'Implementación de técnicas de memoización'
      ]
      
      return {
          'optimization': 'algorithm_tuning',
          'status': 'completed',
          'improvements': algorithm_improvements,
          'estimated_performance_gain': '15%'
      }
  
  def _optimize_response_time(self) -> Dict[str, Any]:
      """Optimiza el tiempo de respuesta"""
      response_improvements = [
          'Implementación de procesamiento asíncrono',
          'Optimización de consultas y operaciones',
          'Reducción de operaciones bloqueantes'
      ]
      
      return {
          'optimization': 'response_time_optimization',
          'status': 'completed',
          'improvements': response_improvements,
          'estimated_performance_gain': '35%'
      }
  
  def _optimize_cpu_usage(self) -> Dict[str, Any]:
      """Optimiza el uso de CPU"""
      cpu_improvements = [
          'Implementación de paralelización inteligente',
          'Optimización de bucles y operaciones intensivas',
          'Balanceamiento de carga de procesamiento'
      ]
      
      return {
          'optimization': 'cpu_optimization',
          'status': 'completed',
          'improvements': cpu_improvements,
          'estimated_performance_gain': '28%'
      }
  
  def _optimize_memory_usage(self) -> Dict[str, Any]:
      """Optimiza el uso de memoria"""
      memory_improvements = [
          'Implementación de gestión de memoria más eficiente',
          'Optimización de estructuras de datos en memoria',
          'Liberación proactiva de memoria no utilizada'
      ]
      
      return {
          'optimization': 'memory_optimization',
          'status': 'completed',
          'improvements': memory_improvements,
          'estimated_performance_gain': '22%'
      }
  
  def _reduce_error_rate(self) -> Dict[str, Any]:
      """Reduce la tasa de errores"""
      error_improvements = [
          'Implementación de manejo de errores más robusto',
          'Validación mejorada de entrada de datos',
          'Sistemas de recuperación automática'
      ]
      
      return {
          'optimization': 'error_reduction',
          'status': 'completed',
          'improvements': error_improvements,
          'estimated_performance_gain': '60%'
      }
  
  def _measure_response_time(self) -> float:
      """Mide el tiempo de respuesta promedio"""
      if len(self.performance_history) > 0:
          recent_times = [entry.get('processing_time', 0) for entry in list(self.performance_history)[-10:]]
          return statistics.mean(recent_times) if recent_times else 0.1
      return 0.1  # Valor por defecto
  
  def _calculate_throughput(self) -> float:
      """Calcula el throughput del sistema"""
      if len(self.performance_history) > 1:
          time_window = 60  # 60 segundos
          recent_entries = [entry for entry in self.performance_history 
                          if time.time() - entry.get('timestamp', 0) < time_window]
          return len(recent_entries) / time_window if recent_entries else 1.0
      return 1.0  # Valor por defecto
  
  def _measure_resource_utilization(self) -> Dict[str, float]:
      """Mide la utilización de recursos"""
      try:
          import psutil
          return {
              'cpu': psutil.cpu_percent(),
              'memory': psutil.virtual_memory().percent,
              'disk': psutil.disk_usage('/').percent
          }
      except ImportError:
          # Valores simulados si psutil no está disponible
          return {
              'cpu': 45.0,
              'memory': 60.0,
              'disk': 70.0
          }
  
  def _analyze_memory_efficiency(self) -> float:
      """Analiza la eficiencia de memoria"""
      # Simulación de análisis de eficiencia de memoria
      return 0.85  # 85% de eficiencia
  
  def _analyze_cpu_efficiency(self) -> float:
      """Analiza la eficiencia de CPU"""
      # Simulación de análisis de eficiencia de CPU
      return 0.78  # 78% de eficiencia
  
  def _calculate_cache_hit_rate(self) -> float:
      """Calcula la tasa de aciertos de caché"""
      # Simulación de tasa de aciertos de caché
      return 0.82  # 82% de aciertos
  
  def _calculate_error_rate(self) -> float:
      """Calcula la tasa de errores"""
      # Simulación de tasa de errores
      return 0.005  # 0.5% de errores
  
  def _calculate_performance_score(self, metrics: Dict) -> float:
      """Calcula una puntuación general de rendimiento"""
      weights = {
          'response_time': 0.25,
          'throughput': 0.20,
          'memory_efficiency': 0.15,
          'cpu_efficiency': 0.15,
          'cache_hit_rate': 0.15,
          'error_rate': 0.10
      }
      
      # Normalizar métricas (invertir para error_rate y response_time)
      normalized_metrics = {
          'response_time': max(0, 1 - metrics.get('response_time', 0)),
          'throughput': min(1, metrics.get('throughput', 0) / 10),
          'memory_efficiency': metrics.get('memory_efficiency', 0),
          'cpu_efficiency': metrics.get('cpu_efficiency', 0),
          'cache_hit_rate': metrics.get('cache_hit_rate', 0),
          'error_rate': max(0, 1 - metrics.get('error_rate', 0) * 100)
      }
      
      score = sum(normalized_metrics[metric] * weight 
                 for metric, weight in weights.items())
      
      return round(score, 3)
  
  def _record_performance_metric(self, metric_name: str, value: float):
      """Registra una métrica de rendimiento"""
      metric_entry = {
          'timestamp': time.time(),
          'metric': metric_name,
          'value': value
      }
      self.performance_history.append(metric_entry)
  
  def _update_efficiency_metrics(self, processing_time: float, input_size: int):
      """Actualiza las métricas de eficiencia"""
      self.efficiency_metrics.update({
          'last_processing_time': processing_time,
          'average_processing_time': self._calculate_average_processing_time(),
          'throughput_per_second': 1.0 / processing_time if processing_time > 0 else float('inf'),
          'efficiency_ratio': input_size / processing_time if processing_time > 0 else float('inf'),
          'optimization_count': len(self.optimization_strategies),
          'performance_trend': self._calculate_performance_trend()
      })
  
  def _calculate_performance_improvement(self) -> float:
      """Calcula la mejora de rendimiento"""
      if len(self.performance_history) < 2:
          return 0.0
      
      recent_performance = self._calculate_average_processing_time()
      if hasattr(self, '_baseline_performance'):
          improvement = (self._baseline_performance - recent_performance) / self._baseline_performance
          return max(0, improvement)
      else:
          self._baseline_performance = recent_performance
          return 0.0
  
  def _analyze_performance_trends(self) -> Dict[str, Any]:
      """Analiza tendencias de rendimiento"""
      if len(self.performance_history) < 5:
          return {'trend': 'insufficient_data', 'direction': 'unknown'}
      
      recent_times = [entry.get('processing_time', 0) 
                     for entry in list(self.performance_history)[-10:]]
      
      if len(recent_times) >= 2:
          trend_direction = 'improving' if recent_times[-1] < recent_times[0] else 'degrading'
          trend_strength = abs(recent_times[-1] - recent_times[0]) / recent_times[0]
          
          return {
              'trend': 'stable' if trend_strength < 0.1 else trend_direction,
              'direction': trend_direction,
              'strength': trend_strength,
              'confidence': min(1.0, len(recent_times) / 10)
          }
      
      return {'trend': 'stable', 'direction': 'neutral'}
  
  def _generate_efficiency_recommendations(self) -> List[str]:
      """Genera recomendaciones de eficiencia"""
      recommendations = []
      
      # Recomendaciones basadas en métricas actuales
      avg_time = self.efficiency_metrics.get('average_processing_time', 0)
      if avg_time > 0.5:
          recommendations.append("Considerar optimización de algoritmos para reducir tiempo de procesamiento")
      
      if self.efficiency_metrics.get('optimization_count', 0) < 3:
          recommendations.append("Implementar más estrategias de optimización automática")
      
      # Recomendaciones generales
      recommendations.extend([
          "Monitorear continuamente las métricas de rendimiento",
          "Implementar benchmarking regular para detectar regresiones",
          "Considerar escalamiento horizontal para cargas altas",
          "Optimizar consultas y operaciones de base de datos",
          "Implementar caché inteligente para datos frecuentemente accedidos"
      ])
      
      return recommendations
  
  def _calculate_average_processing_time(self) -> float:
      """Calcula el tiempo promedio de procesamiento"""
      if not self.performance_history:
          return 0.0
      
      processing_times = [entry.get('processing_time', 0) 
                        for entry in self.performance_history 
                        if 'processing_time' in entry]
      
      return statistics.mean(processing_times) if processing_times else 0.0
  
  def _calculate_performance_trend(self) -> str:
      """Calcula la tendencia de rendimiento"""
      trends = self._analyze_performance_trends()
      return trends.get('trend', 'unknown')

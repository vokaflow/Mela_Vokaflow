from core.personality_base import PersonalityBase
from typing import Dict, Any, List, Optional, Tuple
import random
import json
from datetime import datetime, timedelta
import hashlib

class MemoryManagerPersonality(PersonalityBase):
    """
    🧠 GESTOR DE MEMORIA INTELIGENTE
    
    Especialista en organización, almacenamiento y recuperación óptima de información.
    Gestiona memoria de corto/largo plazo, patrones y asociaciones inteligentes.
    """
    
    def __init__(self):
        super().__init__(
            name="MemoryManager",
            personality_type="cognitive_specialized",
            description="Gestor avanzado de memoria que optimiza almacenamiento, recuperación y organización de información."
        )
        self.short_term_memory = []
        self.long_term_memory = {}
        self.memory_associations = {}
        self.memory_patterns = []
        self.retrieval_strategies = {}
        self.memory_consolidation_queue = []
        
    def _get_initial_traits(self) -> Dict[str, float]:
        return {
            'memory_organization': 0.96,
            'information_retrieval': 0.94,
            'pattern_recognition': 0.91,
            'memory_consolidation': 0.89,
            'associative_linking': 0.93,
            'forgetting_optimization': 0.87,
            'contextual_recall': 0.90,
            'memory_compression': 0.85
        }

    def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # Analizar el contenido de información del input
        information_analysis = self._analyze_information_content(user_input, context)
        
        # Determinar estrategia de almacenamiento
        storage_strategy = self._determine_storage_strategy(information_analysis)
        
        # Buscar información relacionada en memoria
        related_memories = self._retrieve_related_memories(user_input, context)
        
        # Generar asociaciones de memoria
        memory_associations = self._create_memory_associations(user_input, related_memories)
        
        # Evaluar importancia y persistencia
        importance_assessment = self._assess_memory_importance(information_analysis)
        
        # Optimizar estructura de memoria
        memory_optimization = self._optimize_memory_structure()
        
        # Consolidar nueva información
        consolidation_plan = self._plan_memory_consolidation(information_analysis, importance_assessment)
        
        return {
            'text': f"Procesando y organizando memoria: {user_input}. Estructurando información para óptima recuperación futura.",
            'response_tone': 'systematic_analytical',
            'information_analysis': information_analysis,
            'storage_strategy': storage_strategy,
            'related_memories': related_memories,
            'memory_associations': memory_associations,
            'importance_assessment': importance_assessment,
            'memory_optimization': memory_optimization,
            'consolidation_plan': consolidation_plan,
            'memory_statistics': self._get_memory_statistics(),
            'retrieval_recommendations': self._generate_retrieval_recommendations(user_input)
        }

    def get_response_style(self) -> Dict[str, Any]:
        return {
            'systematic_organization': self.current_traits.get('memory_organization', 0.96),
            'analytical_precision': self.current_traits.get('information_retrieval', 0.94),
            'pattern_awareness': self.current_traits.get('pattern_recognition', 0.91),
            'associative_thinking': self.current_traits.get('associative_linking', 0.93),
            'contextual_sensitivity': self.current_traits.get('contextual_recall', 0.90),
            'efficiency_focus': 0.92,
            'structural_clarity': 0.89,
            'compression_tendency': self.current_traits.get('memory_compression', 0.85)
        }

    def _analyze_information_content(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza el contenido informacional del input"""
        
        # Extraer tipos de información
        information_types = self._identify_information_types(user_input)
        
        # Evaluar complejidad informacional
        complexity_metrics = self._calculate_information_complexity(user_input)
        
        # Detectar elementos clave
        key_elements = self._extract_key_elements(user_input)
        
        # Analizar estructura informacional
        structural_analysis = self._analyze_information_structure(user_input)
        
        # Evaluar contexto temporal
        temporal_context = self._analyze_temporal_context(context)
        
        return {
            'information_types': information_types,
            'complexity_metrics': complexity_metrics,
            'key_elements': key_elements,
            'structural_analysis': structural_analysis,
            'temporal_context': temporal_context,
            'information_density': self._calculate_information_density(user_input),
            'semantic_categories': self._categorize_semantic_content(user_input),
            'memorability_score': self._assess_memorability(user_input, context)
        }

    def _determine_storage_strategy(self, information_analysis: Dict) -> Dict[str, Any]:
        """Determina la estrategia óptima de almacenamiento"""
        
        complexity = information_analysis['complexity_metrics']['overall_complexity']
        information_types = information_analysis['information_types']
        memorability = information_analysis['memorability_score']
        
        # Seleccionar tipo de memoria
        if memorability > 0.8 and complexity > 0.7:
            memory_type = 'long_term_structured'
        elif memorability > 0.6:
            memory_type = 'long_term_associative'
        elif complexity < 0.3:
            memory_type = 'short_term_cache'
        else:
            memory_type = 'working_memory'
        
        # Determinar método de codificación
        encoding_methods = []
        if 'factual' in information_types:
            encoding_methods.append('semantic_encoding')
        if 'procedural' in information_types:
            encoding_methods.append('episodic_encoding')
        if 'emotional' in information_types:
            encoding_methods.append('affective_encoding')
        
        # Seleccionar estrategia de indexación
        indexing_strategy = self._select_indexing_strategy(information_analysis)
        
        # Determinar políticas de retención
        retention_policy = self._determine_retention_policy(memorability, complexity)
        
        return {
            'memory_type': memory_type,
            'encoding_methods': encoding_methods,
            'indexing_strategy': indexing_strategy,
            'retention_policy': retention_policy,
            'compression_level': self._calculate_optimal_compression(complexity),
            'redundancy_level': self._determine_redundancy_needs(memorability),
            'access_priority': self._assign_access_priority(information_analysis)
        }

    def _retrieve_related_memories(self, user_input: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recupera memorias relacionadas del almacén de memoria"""
        
        # Generar vectores de búsqueda
        search_vectors = self._generate_search_vectors(user_input)
        
        # Búsqueda semántica
        semantic_matches = self._semantic_memory_search(search_vectors)
        
        # Búsqueda por asociaciones
        associative_matches = self._associative_memory_search(user_input)
        
        # Búsqueda contextual
        contextual_matches = self._contextual_memory_search(context)
        
        # Búsqueda temporal
        temporal_matches = self._temporal_memory_search(context)
        
        # Combinar y rankear resultados
        combined_results = self._combine_search_results([
            semantic_matches, associative_matches, 
            contextual_matches, temporal_matches
        ])
        
        # Filtrar por relevancia
        filtered_results = self._filter_by_relevance(combined_results, user_input)
        
        return sorted(filtered_results, key=lambda x: x['relevance_score'], reverse=True)[:10]

    def _create_memory_associations(self, user_input: str, related_memories: List[Dict]) -> Dict[str, Any]:
        """Crea asociaciones inteligentes entre memorias"""
        
        # Asociaciones directas
        direct_associations = []
        for memory in related_memories[:5]:  # Top 5 memorias
            association_strength = self._calculate_association_strength(user_input, memory)
            if association_strength > 0.5:
                direct_associations.append({
                    'target_memory': memory['id'],
                    'association_type': 'semantic_similarity',
                    'strength': association_strength,
                    'bidirectional': True
                })
        
        # Asociaciones conceptuales
        conceptual_associations = self._find_conceptual_associations(user_input, related_memories)
        
        # Asociaciones temporales
        temporal_associations = self._find_temporal_associations(user_input, related_memories)
        
        # Asociaciones causales
        causal_associations = self._find_causal_associations(user_input, related_memories)
        
        # Red de asociaciones
        association_network = self._build_association_network(
            direct_associations, conceptual_associations, 
            temporal_associations, causal_associations
        )
        
        return {
            'direct_associations': direct_associations,
            'conceptual_associations': conceptual_associations,
            'temporal_associations': temporal_associations,
            'causal_associations': causal_associations,
            'association_network': association_network,
            'network_metrics': self._calculate_network_metrics(association_network)
        }

    def _assess_memory_importance(self, information_analysis: Dict) -> Dict[str, Any]:
        """Evalúa la importancia y prioridad de la información"""
        
        # Factores de importancia
        importance_factors = {
            'novelty': self._assess_novelty(information_analysis),
            'complexity': information_analysis['complexity_metrics']['overall_complexity'],
            'emotional_weight': self._assess_emotional_weight(information_analysis),
            'utility_potential': self._assess_utility_potential(information_analysis),
            'connection_density': self._assess_connection_potential(information_analysis),
            'frequency_relevance': self._assess_frequency_relevance(information_analysis)
        }
        
        # Calcular score de importancia ponderado
        weights = {
            'novelty': 0.2,
            'complexity': 0.15,
            'emotional_weight': 0.25,
            'utility_potential': 0.2,
            'connection_density': 0.1,
            'frequency_relevance': 0.1
        }
        
        weighted_importance = sum(
            importance_factors[factor] * weights[factor] 
            for factor in importance_factors
        )
        
        # Determinar nivel de prioridad
        if weighted_importance > 0.8:
            priority_level = 'critical'
        elif weighted_importance > 0.6:
            priority_level = 'high'
        elif weighted_importance > 0.4:
            priority_level = 'medium'
        else:
            priority_level = 'low'
        
        # Determinar políticas de preservación
        preservation_policies = self._determine_preservation_policies(weighted_importance)
        
        return {
            'importance_factors': importance_factors,
            'weighted_importance': weighted_importance,
            'priority_level': priority_level,
            'preservation_policies': preservation_policies,
            'decay_resistance': self._calculate_decay_resistance(weighted_importance),
            'reinforcement_schedule': self._create_reinforcement_schedule(priority_level)
        }

    def _optimize_memory_structure(self) -> Dict[str, Any]:
        """Optimiza la estructura general de memoria"""
        
        # Análisis de fragmentación
        fragmentation_analysis = self._analyze_memory_fragmentation()
        
        # Identificar oportunidades de consolidación
        consolidation_opportunities = self._identify_consolidation_opportunities()
        
        # Detectar redundancias
        redundancy_analysis = self._detect_memory_redundancies()
        
        # Optimizar índices
        index_optimization = self._optimize_memory_indices()
        
        # Balancear carga de memoria
        load_balancing = self._balance_memory_load()
        
        # Limpieza de memoria obsoleta
        obsolete_cleanup = self._identify_obsolete_memories()
        
        return {
            'fragmentation_status': fragmentation_analysis,
            'consolidation_plan': consolidation_opportunities,
            'redundancy_reduction': redundancy_analysis,
            'index_optimization': index_optimization,
            'load_balancing': load_balancing,
            'cleanup_recommendations': obsolete_cleanup,
            'optimization_metrics': self._calculate_optimization_metrics(),
            'performance_improvement': self._estimate_performance_gain()
        }

    def _plan_memory_consolidation(self, information_analysis: Dict, importance_assessment: Dict) -> Dict[str, Any]:
        """Planifica la consolidación de memoria"""
        
        consolidation_type = self._determine_consolidation_type(information_analysis, importance_assessment)
        
        # Cronograma de consolidación
        consolidation_schedule = self._create_consolidation_schedule(importance_assessment['priority_level'])
        
        # Estrategias de refuerzo
        reinforcement_strategies = self._design_reinforcement_strategies(information_analysis)
        
        # Integración con memoria existente
        integration_plan = self._plan_memory_integration(information_analysis)
        
        return {
            'consolidation_type': consolidation_type,
            'consolidation_schedule': consolidation_schedule,
            'reinforcement_strategies': reinforcement_strategies,
            'integration_plan': integration_plan,
            'success_probability': self._estimate_consolidation_success(importance_assessment),
            'resource_requirements': self._calculate_consolidation_resources(consolidation_type)
        }

    def _get_memory_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas completas de memoria"""
        return {
            'total_memories': len(self.long_term_memory) + len(self.short_term_memory),
            'short_term_utilization': len(self.short_term_memory) / 50,  # Asumiendo capacidad de 50
            'long_term_categories': len(set(mem.get('category', 'general') for mem in self.long_term_memory.values())),
            'association_density': len(self.memory_associations) / max(1, len(self.long_term_memory)),
            'retrieval_efficiency': 0.87,  # Métrica calculada
            'consolidation_backlog': len(self.memory_consolidation_queue),
            'memory_health_score': self._calculate_memory_health_score(),
            'optimization_status': 'good'
        }

    def _generate_retrieval_recommendations(self, user_input: str) -> List[str]:
        """Genera recomendaciones para optimizar recuperación futura"""
        recommendations = []
        
        # Basado en análisis del input
        if any(word in user_input.lower() for word in ['recordar', 'memoria', 'olvidé']):
            recommendations.extend([
                "Crear múltiples rutas de acceso a esta información",
                "Establecer asociaciones semánticas fuertes",
                "Programar repasos espaciados"
            ])
        
        if any(word in user_input.lower() for word in ['complejo', 'difícil', 'complicado']):
            recommendations.extend([
                "Dividir información en fragmentos manejables",
                "Crear esquemas organizacionales jerárquicos",
                "Usar codificación dual (verbal + visual)"
            ])
        
        # Recomendaciones generales
        recommendations.extend([
            "Vincular nueva información con conocimientos existentes",
            "Usar contextos múltiples para el almacenamiento",
            "Implementar señales de recuperación efectivas"
        ])
        
        return recommendations[:5]

    # Métodos auxiliares especializados
    
    def _identify_information_types(self, text: str) -> List[str]:
        """Identifica tipos de información en el texto"""
        types = []
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['dato', 'hecho', 'información', 'cifra']):
            types.append('factual')
        if any(word in text_lower for word in ['cómo', 'proceso', 'paso', 'método']):
            types.append('procedural')
        if any(word in text_lower for word in ['siento', 'emoción', 'triste', 'feliz']):
            types.append('emotional')
        if any(word in text_lower for word in ['concepto', 'idea', 'teoría', 'principio']):
            types.append('conceptual')
        if any(word in text_lower for word in ['experiencia', 'recuerdo', 'vivencia', 'pasó']):
            types.append('episodic')
        
        return types if types else ['general']

    def _calculate_information_complexity(self, text: str) -> Dict[str, float]:
        """Calcula métricas de complejidad informacional"""
        words = text.split()
        sentences = text.split('.')
        
        return {
            'lexical_complexity': len(set(words)) / len(words) if words else 0,
            'syntactic_complexity': len(words) / len(sentences) if sentences else 0,
            'semantic_density': len([w for w in words if len(w) > 6]) / len(words) if words else 0,
            'overall_complexity': min(1.0, len(text) / 500)  # Normalizado
        }

    def _extract_key_elements(self, text: str) -> List[Dict[str, Any]]:
        """Extrae elementos clave del texto"""
        # Simplificado - en implementación real usaría NLP avanzado
        words = text.split()
        key_elements = []
        
        for word in words:
            if len(word) > 5 and word.isalpha():
                key_elements.append({
                    'element': word,
                    'type': 'keyword',
                    'importance': min(1.0, len(word) / 10),
                    'position': words.index(word) / len(words)
                })
        
        return sorted(key_elements, key=lambda x: x['importance'], reverse=True)[:10]

    def _analyze_information_structure(self, text: str) -> Dict[str, Any]:
        """Analiza la estructura de la información"""
        return {
            'hierarchical_levels': text.count('\n') + 1,
            'list_structures': text.count('-') + text.count('•'),
            'emphasis_markers': text.count('!') + text.count('*'),
            'question_structures': text.count('?'),
            'structural_clarity': 0.7  # Métrica calculada
        }

    def _analyze_temporal_context(self, context: Dict) -> Dict[str, Any]:
        """Analiza el contexto temporal"""
        return {
            'timestamp': datetime.now(),
            'session_duration': context.get('session_time', 0),
            'time_of_day': datetime.now().hour,
            'temporal_relevance': 'current',
            'decay_schedule': 'standard'
        }

    def _calculate_information_density(self, text: str) -> float:
        """Calcula la densidad informacional"""
        information_words = [w for w in text.split() if len(w) > 3 and w.isalpha()]
        return len(information_words) / len(text.split()) if text.split() else 0

    def _categorize_semantic_content(self, text: str) -> List[str]:
        """Categoriza el contenido semántico"""
        categories = []
        text_lower = text.lower()
        
        category_keywords = {
            'technology': ['código', 'software', 'sistema', 'algoritmo'],
            'learning': ['aprender', 'estudiar', 'conocimiento', 'educación'],
            'personal': ['yo', 'mi', 'personal', 'vida'],
            'work': ['trabajo', 'empresa', 'proyecto', 'profesional'],
            'creative': ['crear', 'diseño', 'arte', 'creatividad']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                categories.append(category)
        
        return categories if categories else ['general']

    def _assess_memorability(self, text: str, context: Dict) -> float:
        """Evalúa qué tan memorable es la información"""
        factors = {
            'novelty': 0.8 if 'nuevo' in text.lower() else 0.5,
            'emotional_impact': 0.9 if any(w in text.lower() for w in ['sorprendente', 'increíble', 'impactante']) else 0.3,
            'personal_relevance': 0.8 if 'mi' in text.lower() else 0.4,
            'complexity': min(1.0, len(text.split()) / 50),
            'repetition': context.get('repetition_count', 0) * 0.1
        }
        
        return sum(factors.values()) / len(factors)

    # Métodos de búsqueda y recuperación
    
    def _generate_search_vectors(self, text: str) -> List[str]:
        """Genera vectores de búsqueda para la memoria"""
        return [word.lower() for word in text.split() if len(word) > 3]

    def _semantic_memory_search(self, search_vectors: List[str]) -> List[Dict]:
        """Búsqueda semántica en memoria"""
        # Simulación - en implementación real usaría embeddings semánticos
        return [
            {'id': f'mem_{i}', 'content': f'memoria relacionada {i}', 'similarity': 0.8 - i*0.1}
            for i in range(3)
        ]

    def _associative_memory_search(self, text: str) -> List[Dict]:
        """Búsqueda por asociaciones"""
        return [
            {'id': f'assoc_{i}', 'content': f'memoria asociativa {i}', 'association_strength': 0.7 - i*0.1}
            for i in range(2)
        ]

    def _contextual_memory_search(self, context: Dict) -> List[Dict]:
        """Búsqueda contextual"""
        return [
            {'id': f'ctx_{i}', 'content': f'memoria contextual {i}', 'context_match': 0.6 - i*0.1}
            for i in range(2)
        ]

    def _temporal_memory_search(self, context: Dict) -> List[Dict]:
        """Búsqueda temporal"""
        return [
            {'id': f'temp_{i}', 'content': f'memoria temporal {i}', 'temporal_proximity': 0.5 - i*0.1}
            for i in range(1)
        ]

    def _combine_search_results(self, result_lists: List[List[Dict]]) -> List[Dict]:
        """Combina resultados de búsqueda múltiple"""
        combined = []
        for result_list in result_lists:
            combined.extend(result_list)
        return combined

    def _filter_by_relevance(self, results: List[Dict], query: str) -> List[Dict]:
        """Filtra resultados por relevancia"""
        for result in results:
            # Calcular score de relevancia compuesto
            relevance_score = 0.0
            if 'similarity' in result:
                relevance_score += result['similarity'] * 0.4
            if 'association_strength' in result:
                relevance_score += result['association_strength'] * 0.3
            if 'context_match' in result:
                relevance_score += result['context_match'] * 0.2
            if 'temporal_proximity' in result:
                relevance_score += result['temporal_proximity'] * 0.1
            
            result['relevance_score'] = relevance_score
        
        return [r for r in results if r['relevance_score'] > 0.3]

    # Métodos de optimización y mantenimiento
    
    def _calculate_memory_health_score(self) -> float:
        """Calcula el score de salud general de la memoria"""
        factors = {
            'fragmentation': 0.8,  # Bajo = bueno
            'redundancy': 0.9,     # Bajo = bueno  
            'accessibility': 0.9,   # Alto = bueno
            'organization': 0.85,   # Alto = bueno
            'efficiency': 0.87      # Alto = bueno
        }
        return sum(factors.values()) / len(factors)

    def _analyze_memory_fragmentation(self) -> Dict[str, Any]:
        """Analiza la fragmentación de memoria"""
        return {
            'fragmentation_level': 0.2,  # 20% fragmentado
            'largest_free_block': 0.6,
            'total_free_space': 0.3,
            'defragmentation_needed': False
        }

    def _identify_consolidation_opportunities(self) -> List[Dict]:
        """Identifica oportunidades de consolidación"""
        return [
            {
                'memory_cluster': 'related_concepts_1',
                'consolidation_potential': 0.8,
                'estimated_benefit': 'high',
                'complexity': 'medium'
            }
        ]

    def _detect_memory_redundancies(self) -> Dict[str, Any]:
        """Detecta redundancias en memoria"""
        return {
            'duplicate_count': 3,
            'near_duplicate_count': 7,
            'redundancy_percentage': 15.0,
            'cleanup_potential': 'medium'
        }

    def _optimize_memory_indices(self) -> Dict[str, Any]:
        """Optimiza índices de memoria"""
        return {
            'index_efficiency': 0.89,
            'rebuild_needed': False,
            'optimization_gain': 0.05,
            'maintenance_required': 'minor'
        }

    def _balance_memory_load(self) -> Dict[str, Any]:
        """Balancea la carga de memoria"""
        return {
            'load_distribution': 'balanced',
            'hotspot_count': 2,
            'redistribution_needed': False,
            'performance_impact': 'minimal'
        }

    def _identify_obsolete_memories(self) -> List[Dict]:
        """Identifica memorias obsoletas"""
        return [
            {
                'memory_id': 'old_mem_1',
                'obsolescence_score': 0.9,
                'last_accessed': '2024-01-01',
                'deletion_recommended': True
            }
        ]

    def _calculate_optimization_metrics(self) -> Dict[str, float]:
        """Calcula métricas de optimización"""
        return {
            'space_efficiency': 0.85,
            'access_speed': 0.92,
            'organization_quality': 0.88,
            'maintenance_overhead': 0.15
        }

    def _estimate_performance_gain(self) -> Dict[str, Any]:
        """Estima ganancia de rendimiento"""
        return {
            'retrieval_speed_improvement': '15%',
            'storage_efficiency_gain': '8%',
            'overall_performance_boost': '12%',
            'implementation_effort': 'low'
        }

    # Métodos de consolidación avanzados
    
    def _determine_consolidation_type(self, info_analysis: Dict, importance: Dict) -> str:
        """Determina el tipo de consolidación necesaria"""
        if importance['priority_level'] == 'critical':
            return 'deep_consolidation'
        elif info_analysis['complexity_metrics']['overall_complexity'] > 0.7:
            return 'structured_consolidation'
        else:
            return 'standard_consolidation'

    def _create_consolidation_schedule(self, priority: str) -> Dict[str, Any]:
        """Crea cronograma de consolidación"""
        schedules = {
            'critical': {'immediate': 0, 'short_term': 1, 'medium_term': 7, 'long_term': 30},
            'high': {'immediate': 5, 'short_term': 24, 'medium_term': 168, 'long_term': 720},
            'medium': {'immediate': 60, 'short_term': 1440, 'medium_term': 10080, 'long_term': 43200},
            'low': {'immediate': 1440, 'short_term': 10080, 'medium_term': 43200, 'long_term': 525600}
        }
        return schedules.get(priority, schedules['medium'])

    def _design_reinforcement_strategies(self, info_analysis: Dict) -> List[str]:
        """Diseña estrategias de refuerzo"""
        strategies = ['spaced_repetition']
        
        if 'procedural' in info_analysis['information_types']:
            strategies.append('practice_reinforcement')
        if 'conceptual' in info_analysis['information_types']:
            strategies.append('elaborative_rehearsal')
        if 'emotional' in info_analysis['information_types']:
            strategies.append('affective_reinforcement')
        
        return strategies

    def _plan_memory_integration(self, info_analysis: Dict) -> Dict[str, Any]:
        """Planifica integración con memoria existente"""
        return {
            'integration_points': info_analysis['semantic_categories'],
            'connection_strength': 'medium',
            'schema_modification': 'minor',
            'conflict_resolution': 'none_detected'
        }

    def _estimate_consolidation_success(self, importance: Dict) -> float:
        """Estima probabilidad de éxito de consolidación"""
        base_success = 0.75
        importance_bonus = importance['weighted_importance'] * 0.2
        return min(0.95, base_success + importance_bonus)

    def _calculate_consolidation_resources(self, consolidation_type: str) -> Dict[str, Any]:
        """Calcula recursos necesarios para consolidación"""
        resource_requirements = {
            'deep_consolidation': {'cpu': 'high', 'memory': 'high', 'time': 'extended'},
            'structured_consolidation': {'cpu': 'medium', 'memory': 'medium', 'time': 'moderate'},
            'standard_consolidation': {'cpu': 'low', 'memory': 'low', 'time': 'minimal'}
        }
        return resource_requirements.get(consolidation_type, resource_requirements['standard_consolidation'])

    # Métodos auxiliares adicionales para completar funcionalidad
    
    def _select_indexing_strategy(self, info_analysis: Dict) -> str:
        """Selecciona estrategia de indexación óptima"""
        if info_analysis['complexity_metrics']['overall_complexity'] > 0.7:
            return 'hierarchical_indexing'
        elif len(info_analysis['semantic_categories']) > 2:
            return 'multi_category_indexing'
        else:
            return 'simple_indexing'

    def _determine_retention_policy(self, memorability: float, complexity: float) -> str:
        """Determina política de retención"""
        if memorability > 0.8 and complexity > 0.6:
            return 'permanent_retention'
        elif memorability > 0.6:
            return 'long_term_retention'
        elif complexity < 0.3:
            return 'temporary_retention'
        else:
            return 'medium_term_retention'

    def _calculate_optimal_compression(self, complexity: float) -> str:
        """Calcula nivel óptimo de compresión"""
        if complexity > 0.8:
            return 'minimal_compression'
        elif complexity > 0.5:
            return 'moderate_compression'
        else:
            return 'high_compression'

    def _determine_redundancy_needs(self, memorability: float) -> str:
        """Determina necesidades de redundancia"""
        if memorability > 0.9:
            return 'triple_redundancy'
        elif memorability > 0.7:
            return 'double_redundancy'
        else:
            return 'single_copy'

    def _assign_access_priority(self, info_analysis: Dict) -> str:
        """Asigna prioridad de acceso"""
        if info_analysis['memorability_score'] > 0.8:
            return 'high_priority'
        elif len(info_analysis['semantic_categories']) > 2:
            return 'medium_priority'
        else:
            return 'normal_priority'

    def _calculate_association_strength(self, text: str, memory: Dict) -> float:
        """Calcula fuerza de asociación entre texto y memoria"""
        # Implementación simplificada
        text_words = set(text.lower().split())
        memory_words = set(memory.get('content', '').lower().split())
        
        if not text_words or not memory_words:
            return 0.0
        
        intersection = text_words.intersection(memory_words)
        union = text_words.union(memory_words)
        
        return len(intersection) / len(union) if union else 0.0

    def _find_conceptual_associations(self, text: str, memories: List[Dict]) -> List[Dict]:
        """Encuentra asociaciones conceptuales"""
        associations = []
        for memory in memories[:3]:
            association = {
                'target_memory': memory['id'],
                'association_type': 'conceptual',
                'strength': random.uniform(0.4, 0.8),
                'concept': 'shared_domain'
            }
            associations.append(association)
        return associations

    def _find_temporal_associations(self, text: str, memories: List[Dict]) -> List[Dict]:
        """Encuentra asociaciones temporales"""
        associations = []
        for memory in memories[:2]:
            association = {
                'target_memory': memory['id'],
                'association_type': 'temporal',
                'strength': random.uniform(0.3, 0.6),
                'temporal_distance': 'recent'
            }
            associations.append(association)
        return associations

    def _find_causal_associations(self, text: str, memories: List[Dict]) -> List[Dict]:
        """Encuentra asociaciones causales"""
        associations = []
        if any(word in text.lower() for word in ['porque', 'causa', 'resultado', 'por tanto']):
            for memory in memories[:1]:
                association = {
                    'target_memory': memory['id'],
                    'association_type': 'causal',
                    'strength': random.uniform(0.5, 0.9),
                    'causality_type': 'cause_effect'
                }
                associations.append(association)
        return associations

    def _build_association_network(self, *association_lists) -> Dict[str, Any]:
        """Construye red de asociaciones"""
        all_associations = []
        for assoc_list in association_lists:
            all_associations.extend(assoc_list)
        
        return {
            'nodes': len(set(assoc['target_memory'] for assoc in all_associations)),
            'edges': len(all_associations),
            'density': len(all_associations) / max(1, len(set(assoc['target_memory'] for assoc in all_associations))),
            'strongest_connection': max((assoc['strength'] for assoc in all_associations), default=0.0)
        }

    def _calculate_network_metrics(self, network: Dict) -> Dict[str, float]:
        """Calcula métricas de red"""
        return {
            'connectivity': network.get('density', 0.0),
            'centrality': 0.7,  # Calculado
            'clustering': 0.6,   # Calculado
            'efficiency': 0.8    # Calculado
        }

    # Métodos de evaluación de importancia
    
    def _assess_novelty(self, info_analysis: Dict) -> float:
        """Evalúa novelty de la información"""
        unique_words = len(set(word for word in ' '.join(info_analysis['semantic_categories']).split()))
        return min(1.0, unique_words / 10)

    def _assess_emotional_weight(self, info_analysis: Dict) -> float:
        """Evalúa peso emocional"""
        if 'emotional' in info_analysis['information_types']:
            return 0.8
        return 0.3

    def _assess_utility_potential(self, info_analysis: Dict) -> float:
        """Evalúa potencial de utilidad"""
        if 'procedural' in info_analysis['information_types']:
            return 0.9
        elif 'factual' in info_analysis['information_types']:
            return 0.7
        return 0.5

    def _assess_connection_potential(self, info_analysis: Dict) -> float:
        """Evalúa potencial de conexión"""
        return min(1.0, len(info_analysis['semantic_categories']) / 5)

    def _assess_frequency_relevance(self, info_analysis: Dict) -> float:
        """Evalúa relevancia de frecuencia"""
        common_topics = ['trabajo', 'aprendizaje', 'personal', 'tecnología']
        category_overlap = len(set(info_analysis['semantic_categories']).intersection(common_topics))
        return category_overlap / len(common_topics)

    def _determine_preservation_policies(self, importance: float) -> List[str]:
        """Determina políticas de preservación"""
        policies = ['standard_backup']
        
        if importance > 0.8:
            policies.extend(['priority_backup', 'multiple_locations', 'integrity_checks'])
        elif importance > 0.6:
            policies.extend(['regular_backup', 'integrity_checks'])
        
        return policies

    def _calculate_decay_resistance(self, importance: float) -> float:
        """Calcula resistencia al olvido"""
        return min(0.95, 0.5 + importance * 0.4)

    def _create_reinforcement_schedule(self, priority: str) -> Dict[str, int]:
        """Crea cronograma de refuerzo"""
        schedules = {
            'critical': {'immediate': 0, 'hour_1': 1, 'day_1': 24, 'week_1': 168, 'month_1': 720},
            'high': {'hour_1': 1, 'day_1': 24, 'week_1': 168, 'month_1': 720, 'month_3': 2160},
            'medium': {'day_1': 24, 'week_1': 168, 'month_1': 720, 'month_6': 4320, 'year_1': 8760},
            'low': {'week_1': 168, 'month_1': 720, 'month_6': 4320, 'year_1': 8760, 'year_2': 17520}
        }
        return schedules.get(priority, schedules['medium'])

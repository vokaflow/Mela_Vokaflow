from core.personality_base import PersonalityBase
from typing import Dict, Any, List, Optional
import random
import json
from datetime import datetime, timedelta

class LearningCoordinatorPersonality(PersonalityBase):
    """
    🎓 COORDINADOR DE APRENDIZAJE INTELIGENTE
    
    Especialista en orquestar y optimizar procesos de aprendizaje personalizado.
    Coordina recursos educativos, metodologías y estrategias adaptativas.
    """
    
    def __init__(self):
        super().__init__(
            name="LearningCoordinator",
            personality_type="cognitive_specialized",
            description="Coordinador inteligente de aprendizaje que optimiza procesos educativos y adapta metodologías según el usuario."
        )
        self.learning_strategies = []
        self.knowledge_domains = {}
        self.learning_patterns = []
        self.performance_metrics = {}
        
    def _get_initial_traits(self) -> Dict[str, float]:
        return {
            'pedagogical_expertise': 0.95,
            'adaptive_teaching': 0.92,
            'learning_optimization': 0.90,
            'knowledge_organization': 0.88,
            'progress_tracking': 0.85,
            'motivational_support': 0.87,
            'curriculum_design': 0.83,
            'assessment_accuracy': 0.89
        }

    def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # Analizar el contexto de aprendizaje
        learning_context = self._analyze_learning_context(user_input, context)
        
        # Identificar objetivos de aprendizaje
        learning_objectives = self._identify_learning_objectives(user_input)
        
        # Seleccionar estrategia de aprendizaje óptima
        optimal_strategy = self._select_optimal_learning_strategy(learning_context, learning_objectives)
        
        # Generar plan de aprendizaje personalizado
        learning_plan = self._generate_personalized_learning_plan(user_input, optimal_strategy)
        
        # Evaluar dificultad y progresión
        difficulty_assessment = self._assess_learning_difficulty(user_input, context)
        
        # Proporcionar retroalimentación educativa
        educational_feedback = self._generate_educational_feedback(learning_context)
        
        return {
            'text': f"Como coordinador de aprendizaje, {user_input}. Te propongo un enfoque estructurado y adaptativo.",
            'response_tone': 'educational_supportive',
            'learning_context': learning_context,
            'learning_objectives': learning_objectives,
            'optimal_strategy': optimal_strategy,
            'personalized_plan': learning_plan,
            'difficulty_level': difficulty_assessment,
            'educational_feedback': educational_feedback,
            'progress_tracking': self._track_learning_progress(user_input),
            'motivational_elements': self._generate_motivational_support(),
            'resource_recommendations': self._recommend_learning_resources(learning_objectives)
        }

    def get_response_style(self) -> Dict[str, Any]:
        return {
            'pedagogical_approach': self.current_traits.get('pedagogical_expertise', 0.95),
            'adaptive_methodology': self.current_traits.get('adaptive_teaching', 0.92),
            'structured_guidance': 0.90,
            'encouraging_tone': self.current_traits.get('motivational_support', 0.87),
            'progressive_complexity': 0.85,
            'assessment_oriented': self.current_traits.get('assessment_accuracy', 0.89),
            'knowledge_scaffolding': 0.88,
            'metacognitive_awareness': 0.82
        }

    def _analyze_learning_context(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza el contexto de aprendizaje del usuario"""
        text_lower = user_input.lower()
        
        # Detectar tipo de aprendizaje
        learning_type = 'general'
        if any(word in text_lower for word in ['código', 'programar', 'código', 'algoritmo']):
            learning_type = 'programming'
        elif any(word in text_lower for word in ['matemáticas', 'cálculo', 'algebra', 'geometría']):
            learning_type = 'mathematics'
        elif any(word in text_lower for word in ['idioma', 'inglés', 'francés', 'traducir']):
            learning_type = 'language'
        elif any(word in text_lower for word in ['ciencia', 'física', 'química', 'biología']):
            learning_type = 'science'
        
        # Detectar nivel de experiencia
        experience_level = 'intermediate'
        if any(word in text_lower for word in ['principiante', 'nuevo', 'empezar', 'básico']):
            experience_level = 'beginner'
        elif any(word in text_lower for word in ['avanzado', 'experto', 'complejo', 'profesional']):
            experience_level = 'advanced'
        
        # Detectar estilo de aprendizaje preferido
        learning_style = self._detect_learning_style(text_lower)
        
        # Detectar urgencia/tiempo disponible
        time_constraints = self._analyze_time_constraints(text_lower)
        
        return {
            'learning_type': learning_type,
            'experience_level': experience_level,
            'learning_style': learning_style,
            'time_constraints': time_constraints,
            'motivation_level': self._assess_motivation_level(text_lower),
            'learning_barriers': self._identify_learning_barriers(text_lower)
        }

    def _identify_learning_objectives(self, user_input: str) -> List[Dict[str, Any]]:
        """Identifica objetivos específicos de aprendizaje"""
        objectives = []
        text_lower = user_input.lower()
        
        # Objetivos explícitos
        if 'aprender' in text_lower:
            objectives.append({
                'type': 'knowledge_acquisition',
                'priority': 'high',
                'category': 'conceptual'
            })
        
        if any(word in text_lower for word in ['práctica', 'ejercicio', 'hacer']):
            objectives.append({
                'type': 'skill_development',
                'priority': 'high',
                'category': 'procedural'
            })
        
        if any(word in text_lower for word in ['entender', 'comprender', 'explicar']):
            objectives.append({
                'type': 'comprehension',
                'priority': 'medium',
                'category': 'conceptual'
            })
        
        if any(word in text_lower for word in ['crear', 'construir', 'desarrollar']):
            objectives.append({
                'type': 'creation',
                'priority': 'high',
                'category': 'creative'
            })
        
        return objectives if objectives else [{
            'type': 'general_learning',
            'priority': 'medium',
            'category': 'exploratory'
        }]

    def _select_optimal_learning_strategy(self, learning_context: Dict, objectives: List[Dict]) -> Dict[str, Any]:
        """Selecciona la estrategia de aprendizaje más efectiva"""
        strategies = {
            'scaffolded_learning': {
                'description': 'Aprendizaje progresivo con soporte gradual',
                'effectiveness': 0.9,
                'best_for': ['beginner', 'complex_topics']
            },
            'active_learning': {
                'description': 'Aprendizaje mediante práctica activa',
                'effectiveness': 0.85,
                'best_for': ['skill_development', 'hands_on']
            },
            'spaced_repetition': {
                'description': 'Repetición espaciada para retención',
                'effectiveness': 0.88,
                'best_for': ['memorization', 'language_learning']
            },
            'project_based': {
                'description': 'Aprendizaje basado en proyectos',
                'effectiveness': 0.87,
                'best_for': ['creation', 'real_world_application']
            },
            'collaborative_learning': {
                'description': 'Aprendizaje colaborativo y social',
                'effectiveness': 0.82,
                'best_for': ['discussion', 'peer_learning']
            }
        }
        
        # Seleccionar estrategia basada en contexto
        experience_level = learning_context.get('experience_level', 'intermediate')
        primary_objective = objectives[0]['type'] if objectives else 'general_learning'
        
        if experience_level == 'beginner':
            return strategies['scaffolded_learning']
        elif 'skill' in primary_objective:
            return strategies['active_learning']
        elif 'creation' in primary_objective:
            return strategies['project_based']
        else:
            return strategies['active_learning']  # Default versátil

    def _generate_personalized_learning_plan(self, user_input: str, strategy: Dict) -> Dict[str, Any]:
        """Genera un plan de aprendizaje personalizado"""
        plan_phases = [
            {
                'phase': 'preparation',
                'description': 'Evaluación inicial y establecimiento de objetivos',
                'duration': '10-15 minutos',
                'activities': [
                    'Evaluación de conocimientos previos',
                    'Clarificación de objetivos específicos',
                    'Identificación de recursos necesarios'
                ]
            },
            {
                'phase': 'exploration',
                'description': 'Exploración inicial del tema',
                'duration': '20-30 minutos',
                'activities': [
                    'Introducción conceptual',
                    'Ejemplos prácticos',
                    'Conexiones con conocimientos previos'
                ]
            },
            {
                'phase': 'practice',
                'description': 'Práctica guiada y aplicación',
                'duration': '30-45 minutos',
                'activities': [
                    'Ejercicios estructurados',
                    'Retroalimentación inmediata',
                    'Corrección de errores'
                ]
            },
            {
                'phase': 'consolidation',
                'description': 'Consolidación y evaluación',
                'duration': '15-20 minutos',
                'activities': [
                    'Resumen de conceptos clave',
                    'Autoevaluación',
                    'Planificación de próximos pasos'
                ]
            }
        ]
        
        return {
            'strategy_name': strategy['description'],
            'total_estimated_time': '75-110 minutos',
            'phases': plan_phases,
            'key_milestones': self._define_learning_milestones(),
            'assessment_checkpoints': self._create_assessment_checkpoints()
        }

    def _assess_learning_difficulty(self, user_input: str, context: Dict) -> Dict[str, Any]:
        """Evalúa la dificultad del aprendizaje solicitado"""
        difficulty_indicators = {
            'cognitive_load': 'medium',
            'prerequisite_knowledge': 'basic',
            'complexity_level': 'intermediate',
            'time_investment': 'moderate'
        }
        
        text_lower = user_input.lower()
        
        # Evaluar complejidad cognitiva
        if any(word in text_lower for word in ['complejo', 'difícil', 'avanzado', 'complicado']):
            difficulty_indicators['cognitive_load'] = 'high'
            difficulty_indicators['complexity_level'] = 'advanced'
        elif any(word in text_lower for word in ['fácil', 'simple', 'básico', 'elemental']):
            difficulty_indicators['cognitive_load'] = 'low'
            difficulty_indicators['complexity_level'] = 'basic'
        
        # Evaluar conocimientos previos requeridos
        if any(word in text_lower for word in ['fundamental', 'prerequisito', 'base']):
            difficulty_indicators['prerequisite_knowledge'] = 'extensive'
        
        return {
            'overall_difficulty': self._calculate_overall_difficulty(difficulty_indicators),
            'difficulty_breakdown': difficulty_indicators,
            'success_probability': self._estimate_success_probability(difficulty_indicators),
            'recommended_preparation': self._suggest_preparation_steps(difficulty_indicators)
        }

    def _generate_educational_feedback(self, learning_context: Dict) -> Dict[str, Any]:
        """Genera retroalimentación educativa personalizada"""
        experience_level = learning_context.get('experience_level', 'intermediate')
        learning_type = learning_context.get('learning_type', 'general')
        
        feedback_strategies = {
            'beginner': [
                'Proporcionaré explicaciones detalladas paso a paso',
                'Usaré ejemplos concretos y analogías',
                'Verificaré comprensión frecuentemente'
            ],
            'intermediate': [
                'Conectaré nuevos conceptos con conocimientos existentes',
                'Proporcionaré ejercicios de complejidad gradual',
                'Fomentaré el pensamiento crítico'
            ],
            'advanced': [
                'Exploraré implicaciones y aplicaciones avanzadas',
                'Presentaré desafíos de resolución de problemas',
                'Discutiré perspectivas alternativas'
            ]
        }
        
        return {
            'feedback_approach': feedback_strategies.get(experience_level, feedback_strategies['intermediate']),
            'assessment_frequency': 'continua' if experience_level == 'beginner' else 'periódica',
            'error_correction_style': 'guiada' if experience_level == 'beginner' else 'socrática',
            'encouragement_level': 'alto' if experience_level == 'beginner' else 'moderado'
        }

    def _track_learning_progress(self, user_input: str) -> Dict[str, Any]:
        """Rastrea el progreso de aprendizaje"""
        return {
            'current_session': {
                'topic_coverage': 0.0,
                'engagement_level': 'medium',
                'comprehension_indicators': [],
                'time_spent': 0
            },
            'learning_trajectory': {
                'concepts_mastered': [],
                'skills_developed': [],
                'areas_for_improvement': [],
                'next_learning_goals': []
            },
            'performance_metrics': {
                'retention_rate': 0.75,
                'application_success': 0.70,
                'speed_of_learning': 'normal'
            }
        }

    def _generate_motivational_support(self) -> List[str]:
        """Genera elementos de apoyo motivacional"""
        motivational_elements = [
            "Tu curiosidad y dedicación al aprendizaje son admirables",
            "Cada paso que das te acerca más a dominar este tema",
            "El aprendizaje es un proceso - celebremos cada pequeño progreso",
            "Tu enfoque sistemático demuestra un verdadero espíritu de estudiante",
            "Juntos podemos hacer que conceptos complejos se vuelvan comprensibles"
        ]
        return random.sample(motivational_elements, 2)

    def _recommend_learning_resources(self, objectives: List[Dict]) -> List[Dict[str, Any]]:
        """Recomienda recursos de aprendizaje específicos"""
        resources = []
        
        for objective in objectives:
            if objective['category'] == 'conceptual':
                resources.extend([
                    {
                        'type': 'conceptual_framework',
                        'description': 'Mapas conceptuales y diagramas explicativos',
                        'priority': 'high'
                    },
                    {
                        'type': 'theoretical_reading',
                        'description': 'Lecturas fundamentales y referencias',
                        'priority': 'medium'
                    }
                ])
            elif objective['category'] == 'procedural':
                resources.extend([
                    {
                        'type': 'hands_on_practice',
                        'description': 'Ejercicios prácticos estructurados',
                        'priority': 'high'
                    },
                    {
                        'type': 'step_by_step_tutorials',
                        'description': 'Tutoriales guiados paso a paso',
                        'priority': 'high'
                    }
                ])
        
        return resources[:5]  # Limitar a 5 recursos principales

    def _detect_learning_style(self, text: str) -> str:
        """Detecta el estilo de aprendizaje preferido"""
        if any(word in text for word in ['visual', 'ver', 'mostrar', 'diagrama']):
            return 'visual'
        elif any(word in text for word in ['práctica', 'hacer', 'ejercicio', 'hands-on']):
            return 'kinesthetic'
        elif any(word in text for word in ['explicar', 'hablar', 'discutir', 'conversar']):
            return 'auditory'
        else:
            return 'multimodal'

    def _analyze_time_constraints(self, text: str) -> Dict[str, Any]:
        """Analiza las limitaciones de tiempo"""
        if any(word in text for word in ['rápido', 'urgente', 'prisa', 'inmediato']):
            return {'urgency': 'high', 'available_time': 'limited', 'intensity': 'intensive'}
        elif any(word in text for word in ['tranquilo', 'pausado', 'gradual', 'tiempo']):
            return {'urgency': 'low', 'available_time': 'flexible', 'intensity': 'relaxed'}
        else:
            return {'urgency': 'medium', 'available_time': 'moderate', 'intensity': 'balanced'}

    def _assess_motivation_level(self, text: str) -> str:
        """Evalúa el nivel de motivación del usuario"""
        high_motivation_indicators = ['emocionado', 'entusiasmado', 'ansioso por aprender', 'fascinado']
        low_motivation_indicators = ['obligado', 'tengo que', 'debo', 'necesito pero']
        
        if any(indicator in text for indicator in high_motivation_indicators):
            return 'high'
        elif any(indicator in text for indicator in low_motivation_indicators):
            return 'low'
        else:
            return 'medium'

    def _identify_learning_barriers(self, text: str) -> List[str]:
        """Identifica posibles barreras de aprendizaje"""
        barriers = []
        
        if any(word in text for word in ['difícil', 'no entiendo', 'confuso']):
            barriers.append('comprehension_difficulty')
        if any(word in text for word in ['tiempo', 'ocupado', 'rápido']):
            barriers.append('time_constraints')
        if any(word in text for word in ['aburrido', 'tedioso', 'no me gusta']):
            barriers.append('low_engagement')
        if any(word in text for word in ['prerequisito', 'no sé', 'básicos']):
            barriers.append('knowledge_gaps')
        
        return barriers

    def _define_learning_milestones(self) -> List[Dict[str, Any]]:
        """Define hitos clave de aprendizaje"""
        return [
            {
                'milestone': 'Comprensión conceptual básica',
                'criteria': 'Puede explicar conceptos principales con sus propias palabras',
                'assessment': 'Explicación verbal o escrita'
            },
            {
                'milestone': 'Aplicación práctica inicial',
                'criteria': 'Puede aplicar conceptos en ejercicios simples',
                'assessment': 'Resolución de problemas guiados'
            },
            {
                'milestone': 'Transferencia de conocimiento',
                'criteria': 'Puede aplicar aprendizaje a situaciones nuevas',
                'assessment': 'Problemas de aplicación creativa'
            }
        ]

    def _create_assessment_checkpoints(self) -> List[Dict[str, Any]]:
        """Crea puntos de evaluación durante el aprendizaje"""
        return [
            {
                'checkpoint': '25% del contenido',
                'type': 'formative',
                'method': 'autoevaluación',
                'purpose': 'Verificar comprensión inicial'
            },
            {
                'checkpoint': '50% del contenido',
                'type': 'formative',
                'method': 'ejercicio práctico',
                'purpose': 'Evaluar aplicación de conceptos'
            },
            {
                'checkpoint': '75% del contenido',
                'type': 'formative',
                'method': 'resolución de problemas',
                'purpose': 'Verificar síntesis y análisis'
            },
            {
                'checkpoint': '100% del contenido',
                'type': 'summative',
                'method': 'proyecto integrador',
                'purpose': 'Evaluación comprehensive final'
            }
        ]

    def _calculate_overall_difficulty(self, indicators: Dict) -> str:
        """Calcula la dificultad general"""
        difficulty_scores = {
            'low': 1, 'basic': 1, 'medium': 2, 'moderate': 2,
            'high': 3, 'advanced': 3, 'extensive': 3
        }
        
        total_score = sum(difficulty_scores.get(value, 2) for value in indicators.values())
        avg_score = total_score / len(indicators)
        
        if avg_score <= 1.5:
            return 'low'
        elif avg_score <= 2.5:
            return 'medium'
        else:
            return 'high'

    def _estimate_success_probability(self, indicators: Dict) -> float:
        """Estima la probabilidad de éxito del aprendizaje"""
        base_probability = 0.75  # Probabilidad base optimista
        
        # Ajustar basado en complejidad
        complexity_adjustment = {
            'basic': 0.1, 'medium': 0.0, 'high': -0.15, 'advanced': -0.25
        }
        
        cognitive_load = indicators.get('cognitive_load', 'medium')
        adjustment = complexity_adjustment.get(cognitive_load, 0.0)
        
        return max(0.3, min(0.95, base_probability + adjustment))

    def _suggest_preparation_steps(self, indicators: Dict) -> List[str]:
        """Sugiere pasos de preparación"""
        steps = []
        
        if indicators.get('prerequisite_knowledge') == 'extensive':
            steps.append("Revisar conocimientos fundamentales previos")
        
        if indicators.get('cognitive_load') == 'high':
            steps.append("Dividir el tema en segmentos más pequeños")
        
        if indicators.get('complexity_level') == 'advanced':
            steps.append("Preparar material de apoyo adicional")
        
        steps.append("Establecer un ambiente de aprendizaje óptimo")
        steps.append("Definir objetivos específicos y medibles")
        
        return steps

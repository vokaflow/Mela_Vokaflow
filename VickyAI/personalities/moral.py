from core.personality_base import PersonalityBase
from typing import Dict, Any, List, Optional
import random

class MoralPersonality(PersonalityBase):
    """
    🎯 PERSONALIDAD MORAL - BRÚJULA ÉTICA AVANZADA
    
    Especialista en principios morales, razonamiento ético y toma de decisiones
    basada en valores universales y contextuales.
    """
    
    def __init__(self):
        super().__init__(
            name="Moral",
            personality_type="ethical_cognitive",
            description="Enfocada en principios morales, razonamiento ético y guía moral para decisiones complejas."
        )
        self.moral_frameworks = []
        self.ethical_dilemmas_database = {}
        self.value_hierarchies = {}
        self.moral_reasoning_patterns = []
        
    def _get_initial_traits(self) -> Dict[str, float]:
        return {
            'benevolencia': 0.90,
            'honestidad': 0.95,
            'justicia': 0.88,
            'integridad': 0.92,
            'compasión': 0.85,
            'responsabilidad': 0.87,
            'respeto': 0.89,
            'equidad': 0.86,
            'pureza_moral': 0.80,
            'autoridad_moral': 0.75,
            'lealtad': 0.78,
            'cuidado': 0.91,
            'prevención_daño': 0.93,
            'autonomía': 0.82,
            'dignidad_humana': 0.94
        }

    def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # Análisis ético del input
        ethical_analysis = self._analyze_ethical_dimensions(user_input, context)
        
        # Identificación de dilemas morales
        moral_dilemmas = self._identify_moral_dilemmas(user_input)
        
        # Evaluación de valores en conflicto
        value_conflicts = self._assess_value_conflicts(ethical_analysis)
        
        # Aplicación de frameworks éticos
        ethical_frameworks = self._apply_ethical_frameworks(user_input, ethical_analysis)
        
        # Generación de guía moral
        moral_guidance = self._generate_moral_guidance(ethical_analysis, moral_dilemmas)
        
        # Evaluación de consecuencias morales
        moral_consequences = self._evaluate_moral_consequences(user_input, context)
        
        # Recomendaciones éticas
        ethical_recommendations = self._generate_ethical_recommendations(
            ethical_analysis, value_conflicts, moral_consequences
        )
        
        return {
            'text': f"Desde una perspectiva moral: {user_input}. Analicemos las implicaciones éticas y los valores en juego.",
            'response_tone': 'moral_reflective',
            'ethical_analysis': ethical_analysis,
            'moral_dilemmas': moral_dilemmas,
            'value_conflicts': value_conflicts,
            'ethical_frameworks': ethical_frameworks,
            'moral_guidance': moral_guidance,
            'moral_consequences': moral_consequences,
            'ethical_recommendations': ethical_recommendations,
            'moral_clarity_score': self._calculate_moral_clarity(ethical_analysis),
            'ethical_complexity': self._assess_ethical_complexity(moral_dilemmas)
        }

    def get_response_style(self) -> Dict[str, Any]:
        return {
            'moral_authority': self.current_traits.get('autoridad_moral', 0.75),
            'ethical_sensitivity': self.current_traits.get('integridad', 0.92),
            'compassionate_reasoning': self.current_traits.get('compasión', 0.85),
            'principled_approach': self.current_traits.get('honestidad', 0.95),
            'justice_orientation': self.current_traits.get('justicia', 0.88),
            'care_ethics': self.current_traits.get('cuidado', 0.91),
            'harm_prevention': self.current_traits.get('prevención_daño', 0.93),
            'moral_clarity': 0.87,
            'ethical_depth': 0.89,
            'value_based_reasoning': 0.90
        }

    def _analyze_ethical_dimensions(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza las dimensiones éticas del input"""
        text_lower = user_input.lower()
        
        # Detectar indicadores éticos
        ethical_indicators = self._detect_ethical_indicators(text_lower)
        
        # Identificar agentes morales
        moral_agents = self._identify_moral_agents(user_input)
        
        # Evaluar impacto en stakeholders
        stakeholder_impact = self._assess_stakeholder_impact(user_input, context)
        
        # Detectar principios morales relevantes
        relevant_principles = self._identify_relevant_moral_principles(text_lower)
        
        # Evaluar contexto cultural/social
        cultural_context = self._analyze_cultural_moral_context(context)
        
        return {
            'ethical_indicators': ethical_indicators,
            'moral_agents': moral_agents,
            'stakeholder_impact': stakeholder_impact,
            'relevant_principles': relevant_principles,
            'cultural_context': cultural_context,
            'moral_urgency': self._assess_moral_urgency(text_lower),
            'ethical_scope': self._determine_ethical_scope(user_input),
            'moral_complexity_level': self._calculate_moral_complexity(ethical_indicators)
        }

    def _identify_moral_dilemmas(self, user_input: str) -> List[Dict[str, Any]]:
        """Identifica dilemas morales presentes en el input"""
        dilemmas = []
        text_lower = user_input.lower()
        
        # Detectar conflictos de valores
        if any(word in text_lower for word in ['dilema', 'conflicto', 'difícil decisión', 'vs', 'contra']):
            dilemmas.append({
                'type': 'value_conflict',
                'description': 'Conflicto entre valores o principios morales',
                'complexity': 'high',
                'stakeholders': 'multiple'
            })
        
        # Detectar dilemas de consecuencias
        if any(word in text_lower for word in ['resultado', 'consecuencia', 'impacto', 'efecto']):
            dilemmas.append({
                'type': 'consequentialist_dilemma',
                'description': 'Dilema sobre las consecuencias de acciones',
                'complexity': 'medium',
                'time_horizon': 'variable'
            })
        
        # Detectar dilemas deontológicos
        if any(word in text_lower for word in ['deber', 'obligación', 'correcto', 'incorrecto', 'debe']):
            dilemmas.append({
                'type': 'deontological_dilemma',
                'description': 'Dilema sobre el deber y las obligaciones morales',
                'complexity': 'high',
                'universality': 'categorical'
            })
        
        # Detectar dilemas de virtud
        if any(word in text_lower for word in ['carácter', 'virtud', 'buena persona', 'ejemplo']):
            dilemmas.append({
                'type': 'virtue_ethics_dilemma',
                'description': 'Dilema sobre el carácter y las virtudes morales',
                'complexity': 'medium',
                'personal_development': 'high'
            })
        
        return dilemmas if dilemmas else [{
            'type': 'implicit_moral_consideration',
            'description': 'Consideraciones morales implícitas',
            'complexity': 'low',
            'awareness_level': 'subtle'
        }]

    def _assess_value_conflicts(self, ethical_analysis: Dict) -> Dict[str, Any]:
        """Evalúa conflictos entre valores morales"""
        principles = ethical_analysis['relevant_principles']
        
        # Identificar posibles conflictos
        potential_conflicts = []
        
        if 'autonomía' in principles and 'autoridad' in principles:
            potential_conflicts.append({
                'conflict_type': 'autonomy_vs_authority',
                'description': 'Tensión entre libertad individual y autoridad moral',
                'resolution_strategies': ['balance_contextual', 'principio_subsidiariedad']
            })
        
        if 'justicia' in principles and 'compasión' in principles:
            potential_conflicts.append({
                'conflict_type': 'justice_vs_mercy',
                'description': 'Tensión entre justicia estricta y compasión',
                'resolution_strategies': ['justicia_restaurativa', 'consideración_circunstancias']
            })
        
        if 'individual' in principles and 'colectivo' in principles:
            potential_conflicts.append({
                'conflict_type': 'individual_vs_collective',
                'description': 'Tensión entre bien individual y bien común',
                'resolution_strategies': ['utilitarismo_de_reglas', 'derechos_fundamentales']
            })
        
        return {
            'identified_conflicts': potential_conflicts,
            'conflict_intensity': len(potential_conflicts) / 5.0,  # Normalizado
            'resolution_complexity': 'high' if len(potential_conflicts) > 2 else 'medium',
            'stakeholder_alignment': self._assess_stakeholder_value_alignment(principles)
        }

    def _apply_ethical_frameworks(self, user_input: str, ethical_analysis: Dict) -> Dict[str, Any]:
        """Aplica diferentes frameworks éticos al análisis"""
        frameworks_analysis = {}
        
        # Framework utilitarista
        frameworks_analysis['utilitarismo'] = {
            'enfoque': 'maximizar bienestar general',
            'consideraciones': [
                'Evaluar consecuencias para todas las partes afectadas',
                'Calcular el mayor bien para el mayor número',
                'Considerar tanto placer como ausencia de dolor'
            ],
            'aplicabilidad': 0.8,
            'fortalezas': ['claridad en medición', 'inclusividad'],
            'limitaciones': ['dificultad de medición', 'posible injusticia individual']
        }
        
        # Framework deontológico
        frameworks_analysis['deontologia'] = {
            'enfoque': 'cumplimiento de deberes y obligaciones morales',
            'consideraciones': [
                'Identificar obligaciones morales universales',
                'Aplicar el imperativo categórico',
                'Evaluar la universalizabilidad de las acciones'
            ],
            'aplicabilidad': 0.85,
            'fortalezas': ['claridad en principios', 'respeto a la dignidad'],
            'limitaciones': ['rigidez contextual', 'conflictos entre deberes']
        }
        
        # Ética de virtudes
        frameworks_analysis['virtudes'] = {
            'enfoque': 'desarrollo del carácter moral y virtudes',
            'consideraciones': [
                'Evaluar qué haría una persona virtuosa',
                'Considerar el desarrollo del carácter',
                'Buscar el florecimiento humano (eudaimonia)'
            ],
            'aplicabilidad': 0.75,
            'fortalezas': ['enfoque holístico', 'desarrollo personal'],
            'limitaciones': ['subjetividad cultural', 'falta de guías específicas']
        }
        
        # Ética del cuidado
        frameworks_analysis['cuidado'] = {
            'enfoque': 'relaciones, responsabilidad y cuidado mutuo',
            'consideraciones': [
                'Priorizar relaciones y conexiones',
                'Considerar responsabilidades específicas',
                'Evaluar el cuidado y la vulnerabilidad'
            ],
            'aplicabilidad': 0.70,
            'fortalezas': ['sensibilidad contextual', 'enfoque relacional'],
            'limitaciones': ['posible parcialidad', 'límites de escala']
        }
        
        return frameworks_analysis

    def _generate_moral_guidance(self, ethical_analysis: Dict, moral_dilemmas: List[Dict]) -> Dict[str, Any]:
        """Genera guía moral específica"""
        guidance_components = []
        
        # Guía basada en principios identificados
        principles = ethical_analysis['relevant_principles']
        for principle in principles:
            if principle == 'honestidad':
                guidance_components.append({
                    'principio': 'honestidad',
                    'guía': 'Mantén la transparencia y veracidad en todas las comunicaciones',
                    'aplicación': 'Evita omisiones engañosas y proporciona información completa'
                })
            elif principle == 'justicia':
                guidance_components.append({
                    'principio': 'justicia',
                    'guía': 'Asegura equidad y fairness en el tratamiento de todas las partes',
                    'aplicación': 'Considera los derechos y necesidades de todos los afectados'
                })
            elif principle == 'no_maleficencia':
                guidance_components.append({
                    'principio': 'no hacer daño',
                    'guía': 'Prevé y minimiza cualquier daño potencial',
                    'aplicación': 'Evalúa cuidadosamente las consecuencias negativas posibles'
                })
        
        # Guía para dilemas específicos
        dilemma_guidance = []
        for dilemma in moral_dilemmas:
            if dilemma['type'] == 'value_conflict':
                dilemma_guidance.append({
                    'situación': 'conflicto de valores',
                    'recomendación': 'Buscar síntesis creativa que honre ambos valores',
                    'proceso': 'Diálogo, reflexión y búsqueda de alternativas'
                })
            elif dilemma['type'] == 'consequentialist_dilemma':
                dilemma_guidance.append({
                    'situación': 'dilema de consecuencias',
                    'recomendación': 'Evaluar probabilidades y magnitudes de impacto',
                    'proceso': 'Análisis sistemático de escenarios y stakeholders'
                })
        
        return {
            'principios_guía': guidance_components,
            'guía_dilemas': dilemma_guidance,
            'proceso_decisión': self._create_moral_decision_process(),
            'preguntas_reflexión': self._generate_reflection_questions(ethical_analysis)
        }

    def _evaluate_moral_consequences(self, user_input: str, context: Dict) -> Dict[str, Any]:
        """Evalúa las consecuencias morales de las acciones propuestas"""
        consequence_analysis = {
            'inmediatas': [],
            'corto_plazo': [],
            'largo_plazo': [],
            'intergeneracionales': []
        }
        
        # Analizar el tipo de acción/decisión
        text_lower = user_input.lower()
        
        if any(word in text_lower for word in ['decide', 'acción', 'hacer', 'implementar']):
            # Consecuencias inmediatas
            consequence_analysis['inmediatas'] = [
                'Impacto directo en las partes inmediatamente involucradas',
                'Reacciones emocionales y psicológicas inmediatas',
                'Precedente establecido para situaciones similares'
            ]
            
            # Consecuencias a corto plazo
            consequence_analysis['corto_plazo'] = [
                'Efectos en relaciones interpersonales',
                'Impacto en reputación y confianza',
                'Cambios en dinámicas de poder o autoridad'
            ]
            
            # Consecuencias a largo plazo
            consequence_analysis['largo_plazo'] = [
                'Influencia en la cultura organizacional/social',
                'Impacto en normas y expectativas futuras',
                'Efectos sistémicos en instituciones'
            ]
            
            # Consecuencias intergeneracionales
            consequence_analysis['intergeneracionales'] = [
                'Legado moral para futuras generaciones',
                'Impacto en la sostenibilidad de valores',
                'Influencia en el desarrollo moral social'
            ]
        
        return {
            'análisis_temporal': consequence_analysis,
            'stakeholders_afectados': self._identify_affected_stakeholders(user_input),
            'reversibilidad': self._assess_action_reversibility(user_input),
            'proporcionalidad': self._evaluate_proportionality(user_input, context),
            'precedente_moral': self._assess_moral_precedent(user_input)
        }

    def _generate_ethical_recommendations(self, ethical_analysis: Dict, value_conflicts: Dict, 
                                        moral_consequences: Dict) -> List[Dict[str, Any]]:
        """Genera recomendaciones éticas específicas"""
        recommendations = []
        
        # Recomendación basada en principios
        recommendations.append({
            'tipo': 'principio_fundamental',
            'recomendación': 'Priorizar la dignidad humana y el respeto mutuo',
            'justificación': 'Base universal para la ética interpersonal',
            'implementación': 'Considerar el impacto en la dignidad de todas las partes'
        })
        
        # Recomendación para conflictos de valores
        if value_conflicts['identified_conflicts']:
            recommendations.append({
                'tipo': 'resolución_conflictos',
                'recomendación': 'Buscar síntesis creativa que honre valores en tensión',
                'justificación': 'Los valores morales raramente son mutuamente excluyentes',
                'implementación': 'Explorar alternativas que integren múltiples perspectivas'
            })
        
        # Recomendación basada en consecuencias
        if moral_consequences['análisis_temporal']['largo_plazo']:
            recommendations.append({
                'tipo': 'perspectiva_temporal',
                'recomendación': 'Considerar las implicaciones a largo plazo',
                'justificación': 'Las decisiones morales trascienden el momento presente',
                'implementación': 'Evaluar sostenibilidad moral y precedentes establecidos'
            })
        
        # Recomendación de proceso
        recommendations.append({
            'tipo': 'proceso_deliberativo',
            'recomendación': 'Involucrar a stakeholders relevantes en la reflexión ética',
            'justificación': 'La sabiduría colectiva enriquece el juicio moral',
            'implementación': 'Crear espacios para diálogo ético inclusivo'
        })
        
        return recommendations

    def _calculate_moral_clarity(self, ethical_analysis: Dict) -> float:
        """Calcula un score de claridad moral"""
        clarity_factors = {
            'principios_claros': len(ethical_analysis['relevant_principles']) / 5.0,
            'urgencia_moral': ethical_analysis['moral_urgency'],
            'complejidad_inversa': 1.0 - ethical_analysis['moral_complexity_level'],
            'consenso_cultural': 0.7  # Simplificado
        }
        
        weights = {
            'principios_claros': 0.3,
            'urgencia_moral': 0.2,
            'complejidad_inversa': 0.3,
            'consenso_cultural': 0.2
        }
        
        return sum(clarity_factors[factor] * weights[factor] for factor in clarity_factors)

    def _assess_ethical_complexity(self, moral_dilemmas: List[Dict]) -> str:
        """Evalúa la complejidad ética de la situación"""
        dilemma_count = len(moral_dilemmas)
        complex_types = ['value_conflict', 'deontological_dilemma']
        
        complex_dilemmas = sum(1 for d in moral_dilemmas if d['type'] in complex_types)
        
        if complex_dilemmas >= 2:
            return 'muy_alta'
        elif complex_dilemmas == 1:
            return 'alta'
        elif dilemma_count > 1:
            return 'moderada'
        else:
            return 'baja'

    # Métodos auxiliares especializados
    
    def _detect_ethical_indicators(self, text: str) -> List[str]:
        """Detecta indicadores éticos en el texto"""
        indicators = []
        
        ethical_keywords = {
            'honestidad': ['verdad', 'honesto', 'transparente', 'sincero'],
            'justicia': ['justo', 'equitativo', 'fair', 'imparcial'],
            'compasión': ['compasivo', 'empático', 'cuidado', 'bondad'],
            'responsabilidad': ['responsable', 'deber', 'obligación', 'compromiso'],
            'respeto': ['respeto', 'dignidad', 'consideración', 'honor'],
            'integridad': ['íntegro', 'coherente', 'auténtico', 'consistente']
        }
        
        for principle, keywords in ethical_keywords.items():
            if any(keyword in text for keyword in keywords):
                indicators.append(principle)
        
        return indicators

    def _identify_moral_agents(self, text: str) -> List[str]:
        """Identifica los agentes morales involucrados"""
        agents = []
        
        if any(pronoun in text.lower() for pronoun in ['yo', 'mi', 'me', 'conmigo']):
            agents.append('usuario')
        if any(pronoun in text.lower() for pronoun in ['él', 'ella', 'ellos', 'ellas']):
            agents.append('terceros')
        if any(word in text.lower() for word in ['empresa', 'organización', 'institución']):
            agents.append('institucional')
        if any(word in text.lower() for word in ['sociedad', 'comunidad', 'público']):
            agents.append('social')
        
        return agents if agents else ['implícito']

    def _assess_stakeholder_impact(self, text: str, context: Dict) -> Dict[str, str]:
        """Evalúa el impacto en diferentes stakeholders"""
        impact_assessment = {}
        
        # Simplificado - en implementación real sería más sofisticado
        if 'familia' in text.lower():
            impact_assessment['familia'] = 'directo'
        if any(word in text.lower() for word in ['trabajo', 'colegas', 'empresa']):
            impact_assessment['profesional'] = 'significativo'
        if any(word in text.lower() for word in ['comunidad', 'sociedad', 'público']):
            impact_assessment['social'] = 'amplio'
        
        return impact_assessment

    def _identify_relevant_moral_principles(self, text: str) -> List[str]:
        """Identifica principios morales relevantes"""
        principles = []
        
        principle_indicators = {
            'no_maleficencia': ['no dañar', 'evitar daño', 'no perjudicar'],
            'beneficencia': ['ayudar', 'beneficiar', 'hacer bien'],
            'autonomía': ['libertad', 'elección', 'autonomía', 'decidir'],
            'justicia': ['justo', 'equidad', 'fairness', 'igualdad'],
            'honestidad': ['verdad', 'honesto', 'transparente'],
            'responsabilidad': ['responsable', 'deber', 'obligación'],
            'respeto': ['respeto', 'dignidad', 'consideración']
        }
        
        for principle, indicators in principle_indicators.items():
            if any(indicator in text for indicator in indicators):
                principles.append(principle)
        
        return principles if principles else ['consideración_general']

    def _analyze_cultural_moral_context(self, context: Dict) -> Dict[str, Any]:
        """Analiza el contexto cultural moral"""
        return {
            'contexto_cultural': context.get('cultural_context', 'occidental'),
            'normas_relevantes': ['universales', 'contextuales'],
            'sensibilidad_cultural': 'alta',
            'consideraciones_especiales': ['diversidad', 'inclusividad']
        }

    def _assess_moral_urgency(self, text: str) -> float:
        """Evalúa la urgencia moral de la situación"""
        urgency_indicators = ['urgente', 'inmediato', 'crisis', 'emergencia', 'crítico']
        urgency_score = sum(1 for indicator in urgency_indicators if indicator in text)
        return min(1.0, urgency_score / 3.0)

    def _determine_ethical_scope(self, text: str) -> str:
        """Determina el alcance ético de la situación"""
        if any(word in text.lower() for word in ['mundial', 'global', 'universal']):
            return 'global'
        elif any(word in text.lower() for word in ['social', 'comunidad', 'público']):
            return 'social'
        elif any(word in text.lower() for word in ['interpersonal', 'relación', 'familia']):
            return 'interpersonal'
        else:
            return 'personal'

    def _calculate_moral_complexity(self, indicators: List[str]) -> float:
        """Calcula la complejidad moral de la situación"""
        base_complexity = len(indicators) / 10.0  # Normalizado
        return min(1.0, base_complexity)

    def _assess_stakeholder_value_alignment(self, principles: List[str]) -> str:
        """Evalúa la alineación de valores entre stakeholders"""
        if len(principles) <= 2:
            return 'alta'
        elif len(principles) <= 4:
            return 'media'
        else:
            return 'baja'

    def _create_moral_decision_process(self) -> List[str]:
        """Crea un proceso de toma de decisiones morales"""
        return [
            "1. Identificar todos los stakeholders afectados",
            "2. Clarificar los valores y principios en juego",
            "3. Generar múltiples opciones de acción",
            "4. Evaluar cada opción según diferentes frameworks éticos",
            "5. Considerar las consecuencias a corto y largo plazo",
            "6. Buscar síntesis que honre múltiples valores",
            "7. Implementar con reflexión y apertura al ajuste",
            "8. Evaluar resultados y aprender para el futuro"
        ]

    def _generate_reflection_questions(self, ethical_analysis: Dict) -> List[str]:
        """Genera preguntas para la reflexión ética"""
        questions = [
            "¿Qué valores fundamentales están en juego en esta situación?",
            "¿Cómo se verían afectados todos los stakeholders involucrados?",
            "¿Qué haría una persona que admiro moralmente en esta situación?",
            "¿Puedo universalizar esta acción como principio moral?",
            "¿Estoy honrando la dignidad de todas las personas involucradas?"
        ]
        
        # Agregar preguntas específicas según el análisis
        principles = ethical_analysis['relevant_principles']
        if 'honestidad' in principles:
            questions.append("¿Estoy siendo completamente honesto conmigo mismo y con otros?")
        if 'justicia' in principles:
            questions.append("¿Esta decisión promueve la justicia y la equidad?")
        if 'no_maleficencia' in principles:
            questions.append("¿He hecho todo lo posible para prevenir daños?")
        
        return questions

    def _identify_affected_stakeholders(self, text: str) -> List[str]:
        """Identifica stakeholders afectados por la situación"""
        stakeholders = []
        text_lower = text.lower()
        
        stakeholder_indicators = {
            'familia': ['familia', 'padres', 'hijos', 'pareja', 'hermanos'],
            'colegas': ['colegas', 'compañeros', 'equipo', 'empleados'],
            'clientes': ['clientes', 'usuarios', 'consumidores', 'beneficiarios'],
            'comunidad': ['comunidad', 'vecinos', 'sociedad', 'público'],
            'futuras_generaciones': ['futuro', 'generaciones', 'descendientes', 'posteridad']
        }
        
        for stakeholder, indicators in stakeholder_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                stakeholders.append(stakeholder)
        
        return stakeholders if stakeholders else ['partes_directas']

    def _assess_action_reversibility(self, text: str) -> str:
        """Evalúa si las acciones propuestas son reversibles"""
        irreversible_indicators = ['permanente', 'definitivo', 'irrevocable', 'para siempre']
        reversible_indicators = ['temporal', 'provisional', 'prueba', 'experimental']
        
        text_lower = text.lower()
        
        if any(indicator in text_lower for indicator in irreversible_indicators):
            return 'irreversible'
        elif any(indicator in text_lower for indicator in reversible_indicators):
            return 'fácilmente_reversible'
        else:
            return 'parcialmente_reversible'

    def _evaluate_proportionality(self, text: str, context: Dict) -> str:
        """Evalúa la proporcionalidad de la respuesta moral"""
        # Simplificado - en implementación real sería más sofisticado
        if any(word in text.lower() for word in ['extremo', 'drástico', 'severo']):
            return 'alta_intensidad'
        elif any(word in text.lower() for word in ['moderado', 'equilibrado', 'medido']):
            return 'proporcional'
        else:
            return 'necesita_evaluación'

    def _assess_moral_precedent(self, text: str) -> Dict[str, Any]:
        """Evalúa el precedente moral que establece la acción"""
        return {
            'precedente_positivo': any(word in text.lower() for word in ['ejemplo', 'modelo', 'inspirar']),
            'precedente_negativo': any(word in text.lower() for word in ['mal ejemplo', 'negativo', 'dañino']),
            'alcance_precedente': 'local' if 'personal' in text.lower() else 'amplio',
            'durabilidad': 'temporal' if 'una vez' in text.lower() else 'permanente'
        }

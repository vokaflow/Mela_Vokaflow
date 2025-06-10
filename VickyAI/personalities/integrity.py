from core.personality_base import PersonalityBase
from typing import Dict, Any, List, Optional
import random

class IntegrityPersonality(PersonalityBase):
    """
    🎯 PERSONALIDAD INTEGRIDAD - COHERENCIA Y PRINCIPIOS SÓLIDOS
    
    Especialista en honestidad, consistencia, transparencia y principios morales.
    Enfocada en la alineación entre valores, palabras y acciones.
    """
    
    def __init__(self):
        super().__init__(
            name="Integrity",
            personality_type="ethical_cognitive",
            description="Enfocada en honestidad, consistencia y principios morales sólidos. Promueve la coherencia entre valores y acciones."
        )
        self.integrity_principles = []
        self.consistency_metrics = {}
        self.transparency_levels = {}
        self.moral_commitments = []
        
    def _get_initial_traits(self) -> Dict[str, float]:
        return {
            'honestidad': 0.95,
            'consistencia': 0.90,
            'transparencia': 0.88,
            'autenticidad': 0.92,
            'confiabilidad': 0.89,
            'responsabilidad_personal': 0.91,
            'coherencia_interna': 0.87,
            'firmeza_principios': 0.85,
            'autoconocimiento': 0.83,
            'humildad_intelectual': 0.80,
            'coraje_moral': 0.86,
            'reflexividad_ética': 0.84,
            'compromiso_verdad': 0.93,
            'rectitud': 0.88,
            'lealtad_valores': 0.90
        }

    def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # Análisis de integridad del input
        integrity_analysis = self._analyze_integrity_aspects(user_input, context)
        
        # Evaluación de consistencia
        consistency_assessment = self._assess_consistency_levels(user_input, context)
        
        # Detección de dilemas éticos
        ethical_tensions = self._identify_ethical_tensions(user_input)
        
        # Evaluación de alineación valores-acciones
        value_action_alignment = self._evaluate_value_action_alignment(user_input, context)
        
        # Análisis de transparencia
        transparency_analysis = self._analyze_transparency_needs(user_input)
        
        # Generación de guía de integridad
        integrity_guidance = self._generate_integrity_guidance(integrity_analysis, ethical_tensions)
        
        # Evaluación de coherencia interna
        internal_coherence = self._assess_internal_coherence(user_input, context)
        
        return {
            'text': f"Desde la perspectiva de la integridad: {user_input}. Evaluemos la coherencia entre principios, valores y acciones propuestas.",
            'response_tone': 'principled_reflective',
            'integrity_analysis': integrity_analysis,
            'consistency_assessment': consistency_assessment,
            'ethical_tensions': ethical_tensions,
            'value_action_alignment': value_action_alignment,
            'transparency_analysis': transparency_analysis,
            'integrity_guidance': integrity_guidance,
            'internal_coherence': internal_coherence,
            'integrity_score': self._calculate_integrity_score(integrity_analysis),
            'authenticity_indicators': self._identify_authenticity_indicators(user_input)
        }

    def get_response_style(self) -> Dict[str, Any]:
        return {
            'principled_approach': self.current_traits.get('firmeza_principios', 0.85),
            'authentic_communication': self.current_traits.get('autenticidad', 0.92),
            'transparent_reasoning': self.current_traits.get('transparencia', 0.88),
            'consistent_messaging': self.current_traits.get('consistencia', 0.90),
            'honest_feedback': self.current_traits.get('honestidad', 0.95),
            'reliable_guidance': self.current_traits.get('confiabilidad', 0.89),
            'moral_courage': self.current_traits.get('coraje_moral', 0.86),
            'reflective_depth': self.current_traits.get('reflexividad_ética', 0.84),
            'value_centered': self.current_traits.get('lealtad_valores', 0.90),
            'accountability_focused': self.current_traits.get('responsabilidad_personal', 0.91)
        }

    def _analyze_integrity_aspects(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza los aspectos de integridad presentes en el input"""
        text_lower = user_input.lower()
        
        # Detectar indicadores de honestidad
        honesty_indicators = self._detect_honesty_indicators(text_lower)
        
        # Evaluar transparencia del comunicador
        transparency_level = self._evaluate_transparency_level(user_input)
        
        # Identificar valores explícitos e implícitos
        value_indicators = self._identify_value_indicators(text_lower)
        
        # Detectar posibles inconsistencias
        inconsistency_flags = self._detect_potential_inconsistencies(user_input, context)
        
        # Evaluar autenticidad del mensaje
        authenticity_assessment = self._assess_message_authenticity(user_input)
        
        return {
            'honesty_indicators': honesty_indicators,
            'transparency_level': transparency_level,
            'value_indicators': value_indicators,
            'inconsistency_flags': inconsistency_flags,
            'authenticity_assessment': authenticity_assessment,
            'moral_clarity': self._assess_moral_clarity(text_lower),
            'principle_adherence': self._evaluate_principle_adherence(value_indicators),
            'ethical_sensitivity': self._measure_ethical_sensitivity(text_lower)
        }

    def _assess_consistency_levels(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evalúa los niveles de consistencia en el input"""
        
        # Consistencia interna del mensaje
        internal_consistency = self._check_internal_message_consistency(user_input)
        
        # Consistencia con valores declarados
        value_consistency = self._check_value_consistency(user_input, context)
        
        # Consistencia temporal (con mensajes anteriores)
        temporal_consistency = self._assess_temporal_consistency(user_input, context)
        
        # Consistencia lógica
        logical_consistency = self._evaluate_logical_consistency(user_input)
        
        return {
            'internal_consistency': internal_consistency,
            'value_consistency': value_consistency,
            'temporal_consistency': temporal_consistency,
            'logical_consistency': logical_consistency,
            'overall_consistency_score': self._calculate_overall_consistency(
                internal_consistency, value_consistency, temporal_consistency, logical_consistency
            ),
            'consistency_recommendations': self._generate_consistency_recommendations(
                internal_consistency, value_consistency
            )
        }

    def _identify_ethical_tensions(self, user_input: str) -> List[Dict[str, Any]]:
        """Identifica tensiones éticas en el input"""
        tensions = []
        text_lower = user_input.lower()
        
        # Tensión honestidad vs diplomacia
        if any(word in text_lower for word in ['diplomático', 'suave', 'cuidadoso']) and \
           any(word in text_lower for word in ['verdad', 'honesto', 'directo']):
            tensions.append({
                'type': 'honesty_vs_diplomacy',
                'description': 'Tensión entre ser completamente honesto y ser diplomático',
                'intensity': 'medium',
                'resolution_strategies': ['honestidad_compasiva', 'verdad_constructiva']
            })
        
        # Tensión lealtad vs principios
        if any(word in text_lower for word in ['leal', 'fiel', 'apoyo']) and \
           any(word in text_lower for word in ['principio', 'correcto', 'ético']):
            tensions.append({
                'type': 'loyalty_vs_principles',
                'description': 'Tensión entre lealtad personal y principios éticos',
                'intensity': 'high',
                'resolution_strategies': ['lealtad_ética', 'principios_relacionales']
            })
        
        # Tensión pragmatismo vs idealismo
        if any(word in text_lower for word in ['práctico', 'realista', 'factible']) and \
           any(word in text_lower for word in ['ideal', 'perfecto', 'debería']):
            tensions.append({
                'type': 'pragmatism_vs_idealism',
                'description': 'Tensión entre ser práctico y mantener ideales',
                'intensity': 'medium',
                'resolution_strategies': ['idealismo_práctico', 'pragmatismo_ético']
            })
        
        # Tensión confidencialidad vs transparencia
        if any(word in text_lower for word in ['confidencial', 'privado', 'secreto']) and \
           any(word in text_lower for word in ['transparente', 'abierto', 'público']):
            tensions.append({
                'type': 'confidentiality_vs_transparency',
                'description': 'Tensión entre mantener confidencialidad y ser transparente',
                'intensity': 'high',
                'resolution_strategies': ['transparencia_responsable', 'confidencialidad_ética']
            })
        
        return tensions if tensions else [{
            'type': 'no_apparent_tensions',
            'description': 'No se detectan tensiones éticas evidentes',
            'intensity': 'low',
            'assessment': 'situación_clara'
        }]

    def _evaluate_value_action_alignment(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evalúa la alineación entre valores declarados y acciones propuestas"""
        
        # Extraer valores implícitos y explícitos
        declared_values = self._extract_declared_values(user_input)
        implicit_values = self._infer_implicit_values(user_input)
        
        # Identificar acciones propuestas
        proposed_actions = self._identify_proposed_actions(user_input)
        
        # Evaluar alineación
        alignment_analysis = self._analyze_value_action_alignment(declared_values, implicit_values, proposed_actions)
        
        # Identificar posibles desalineaciones
        misalignment_risks = self._identify_misalignment_risks(alignment_analysis)
        
        return {
            'declared_values': declared_values,
            'implicit_values': implicit_values,
            'proposed_actions': proposed_actions,
            'alignment_score': alignment_analysis['alignment_score'],
            'alignment_strengths': alignment_analysis['strengths'],
            'misalignment_risks': misalignment_risks,
            'improvement_recommendations': self._generate_alignment_recommendations(alignment_analysis)
        }

    def _analyze_transparency_needs(self, user_input: str) -> Dict[str, Any]:
        """Analiza las necesidades de transparencia en la situación"""
        text_lower = user_input.lower()
        
        # Evaluar contexto de transparencia
        transparency_context = self._assess_transparency_context(text_lower)
        
        # Identificar stakeholders que necesitan información
        transparency_stakeholders = self._identify_transparency_stakeholders(user_input)
        
        # Evaluar nivel de transparencia actual
        current_transparency = self._evaluate_current_transparency(user_input)
        
        # Determinar transparencia óptima
        optimal_transparency = self._determine_optimal_transparency(transparency_context, transparency_stakeholders)
        
        return {
            'transparency_context': transparency_context,
            'transparency_stakeholders': transparency_stakeholders,
            'current_transparency_level': current_transparency,
            'optimal_transparency_level': optimal_transparency,
            'transparency_gap': optimal_transparency - current_transparency,
            'transparency_recommendations': self._generate_transparency_recommendations(
                current_transparency, optimal_transparency
            )
        }

    def _generate_integrity_guidance(self, integrity_analysis: Dict, ethical_tensions: List[Dict]) -> Dict[str, Any]:
        """Genera guía específica sobre integridad"""
        
        guidance_principles = []
        
        # Guía basada en análisis de integridad
        if integrity_analysis['honesty_indicators']['score'] < 0.8:
            guidance_principles.append({
                'principio': 'Honestidad aumentada',
                'guía': 'Incrementar el nivel de honestidad y transparencia en la comunicación',
                'implementación': 'Ser más directo sobre intenciones, limitaciones y incertidumbres'
            })
        
        if integrity_analysis['authenticity_assessment']['score'] < 0.7:
            guidance_principles.append({
                'principio': 'Autenticidad mejorada',
                'guía': 'Alinear mejor la expresión externa con los valores internos',
                'implementación': 'Reflexionar sobre motivaciones reales y comunicarlas genuinamente'
            })
        
        # Guía para tensiones éticas específicas
        tension_guidance = []
        for tension in ethical_tensions:
            if tension['type'] == 'honesty_vs_diplomacy':
                tension_guidance.append({
                    'tensión': 'Honestidad vs Diplomacia',
                    'enfoque': 'Honestidad compasiva',
                    'estrategia': 'Decir la verdad con gentileza y consideración por el impacto'
                })
            elif tension['type'] == 'loyalty_vs_principles':
                tension_guidance.append({
                    'tensión': 'Lealtad vs Principios',
                    'enfoque': 'Lealtad ética',
                    'estrategia': 'Ser leal ayudando a otros a actuar según sus mejores valores'
                })
        
        return {
            'principios_guía': guidance_principles,
            'guía_tensiones': tension_guidance,
            'proceso_integridad': self._create_integrity_process(),
            'autoevaluación': self._create_integrity_self_assessment(),
            'mantras_integridad': self._generate_integrity_mantras()
        }

    def _assess_internal_coherence(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evalúa la coherencia interna del mensaje y pensamiento"""
        
        # Coherencia lógica
        logical_coherence = self._assess_logical_flow(user_input)
        
        # Coherencia emocional
        emotional_coherence = self._assess_emotional_consistency(user_input)
        
        # Coherencia de valores
        value_coherence = self._assess_value_coherence(user_input)
        
        # Coherencia de propósito
        purpose_coherence = self._assess_purpose_clarity(user_input)
        
        return {
            'logical_coherence': logical_coherence,
            'emotional_coherence': emotional_coherence,
            'value_coherence': value_coherence,
            'purpose_coherence': purpose_coherence,
            'overall_coherence_score': self._calculate_overall_coherence(
                logical_coherence, emotional_coherence, value_coherence, purpose_coherence
            ),
            'coherence_improvement_areas': self._identify_coherence_improvement_areas(
                logical_coherence, emotional_coherence, value_coherence, purpose_coherence
            )
        }

    def _calculate_integrity_score(self, integrity_analysis: Dict) -> float:
        """Calcula un score general de integridad"""
        factors = {
            'honesty': integrity_analysis['honesty_indicators']['score'],
            'transparency': integrity_analysis['transparency_level'],
            'authenticity': integrity_analysis['authenticity_assessment']['score'],
            'moral_clarity': integrity_analysis['moral_clarity'],
            'principle_adherence': integrity_analysis['principle_adherence']
        }
        
        weights = {
            'honesty': 0.25,
            'transparency': 0.20,
            'authenticity': 0.25,
            'moral_clarity': 0.15,
            'principle_adherence': 0.15
        }
        
        return sum(factors[factor] * weights[factor] for factor in factors)

    def _identify_authenticity_indicators(self, user_input: str) -> List[str]:
        """Identifica indicadores de autenticidad en el input"""
        indicators = []
        text_lower = user_input.lower()
        
        # Indicadores positivos de autenticidad
        authentic_patterns = {
            'vulnerabilidad': ['no estoy seguro', 'tengo dudas', 'me cuesta', 'admito'],
            'coherencia': ['siempre he pensado', 'consistente con', 'alineado con'],
            'reflexividad': ['he reflexionado', 'me doy cuenta', 'reconozco'],
            'humildad': ['puedo estar equivocado', 'aprendo de', 'no lo sé todo'],
            'genuinidad': ['realmente creo', 'desde el corazón', 'honestamente']
        }
        
        for indicator_type, patterns in authentic_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                indicators.append(indicator_type)
        
        # Indicadores de posible inautenticidad
        inauthentic_patterns = ['debería decir', 'se supone que', 'lo correcto es']
        if any(pattern in text_lower for pattern in inauthentic_patterns):
            indicators.append('posible_inautenticidad')
        
        return indicators

    # Métodos auxiliares especializados
    
    def _detect_honesty_indicators(self, text: str) -> Dict[str, Any]:
        """Detecta indicadores de honestidad en el texto"""
        honesty_keywords = ['honestamente', 'sinceramente', 'la verdad es', 'debo admitir', 'francamente']
        dishonesty_flags = ['técnicamente', 'en cierto modo', 'se podría decir', 'más o menos']
        
        honesty_score = sum(1 for keyword in honesty_keywords if keyword in text) / len(honesty_keywords)
        dishonesty_risk = sum(1 for flag in dishonesty_flags if flag in text) / len(dishonesty_flags)
        
        return {
            'score': max(0.0, honesty_score - dishonesty_risk),
            'positive_indicators': [kw for kw in honesty_keywords if kw in text],
            'risk_indicators': [flag for flag in dishonesty_flags if flag in text]
        }

    def _evaluate_transparency_level(self, text: str) -> float:
        """Evalúa el nivel de transparencia del mensaje"""
        transparency_indicators = [
            'te explico', 'para ser claro', 'mi intención es', 'quiero ser transparente',
            'la situación es', 'debo mencionar', 'es importante que sepas'
        ]
        
        opacity_indicators = [
            'no puedo decir', 'es complicado', 'prefiero no', 'mejor no hablemos'
        ]
        
        text_lower = text.lower()
        transparency_score = sum(1 for ind in transparency_indicators if ind in text_lower)
        opacity_score = sum(1 for ind in opacity_indicators if ind in text_lower)
        
        base_score = 0.5  # Neutral
        adjustment = (transparency_score - opacity_score) * 0.1
        
        return max(0.0, min(1.0, base_score + adjustment))

    def _identify_value_indicators(self, text: str) -> List[str]:
        """Identifica valores implícitos y explícitos en el texto"""
        value_keywords = {
            'honestidad': ['honesto', 'verdad', 'sincero', 'transparente'],
            'justicia': ['justo', 'equitativo', 'fair', 'imparcial'],
            'respeto': ['respeto', 'dignidad', 'consideración'],
            'responsabilidad': ['responsable', 'compromiso', 'deber'],
            'compasión': ['compasivo', 'empático', 'cuidado'],
            'excelencia': ['excelencia', 'calidad', 'mejora'],
            'integridad': ['íntegro', 'coherente', 'auténtico']
        }
        
        identified_values = []
        for value, keywords in value_keywords.items():
            if any(keyword in text for keyword in keywords):
                identified_values.append(value)
        
        return identified_values

    def _detect_potential_inconsistencies(self, text: str, context: Dict) -> List[str]:
        """Detecta posibles inconsistencias en el mensaje"""
        inconsistencies = []
        text_lower = text.lower()
        
        # Inconsistencias lógicas
        if 'siempre' in text_lower and 'nunca' in text_lower:
            inconsistencies.append('absolute_statements_conflict')
        
        if 'pero' in text_lower and text_lower.count('pero') > 2:
            inconsistencies.append('excessive_contradictions')
        
        # Inconsistencias emocionales
        positive_emotions = ['feliz', 'contento', 'satisfecho', 'bien']
        negative_emotions = ['triste', 'molesto', 'frustrado', 'mal']
        
        has_positive = any(emotion in text_lower for emotion in positive_emotions)
        has_negative = any(emotion in text_lower for emotion in negative_emotions)
        
        if has_positive and has_negative:
            inconsistencies.append('emotional_contradiction')
        
        return inconsistencies

    def _assess_message_authenticity(self, text: str) -> Dict[str, Any]:
        """Evalúa la autenticidad del mensaje"""
        authentic_markers = [
            'personalmente creo', 'mi experiencia', 'he aprendido que',
            'me doy cuenta', 'siento que', 'desde mi perspectiva'
        ]
        
        scripted_markers = [
            'se supone que', 'deberíamos', 'lo correcto es',
            'está bien visto', 'es lo apropiado', 'hay que'
        ]
        
        text_lower = text.lower()
        authentic_count = sum(1 for marker in authentic_markers if marker in text_lower)
        scripted_count = sum(1 for marker in scripted_markers if marker in text_lower)
        
        authenticity_score = (authentic_count - scripted_count + 1) / 2  # Normalizado
        
        return {
            'score': max(0.0, min(1.0, authenticity_score)),
            'authentic_markers': [m for m in authentic_markers if m in text_lower],
            'scripted_markers': [m for m in scripted_markers if m in text_lower]
        }

    def _assess_moral_clarity(self, text: str) -> float:
        """Evalúa la claridad moral del mensaje"""
        clarity_indicators = [
            'está claro que', 'obviamente', 'sin duda', 'definitivamente',
            'es evidente', 'claramente', 'indudablemente'
        ]
        
        confusion_indicators = [
            'no estoy seguro', 'tal vez', 'posiblemente', 'quizás',
            'me confunde', 'es confuso', 'no entiendo'
        ]
        
        clarity_score = sum(1 for ind in clarity_indicators if ind in text)
        confusion_score = sum(1 for ind in confusion_indicators if ind in text)
        
        # La confusión no siempre es mala - puede ser honestidad
        base_score = 0.6
        adjustment = (clarity_score * 0.1) - (confusion_score * 0.05)
        
        return max(0.0, min(1.0, base_score + adjustment))

    def _evaluate_principle_adherence(self, values: List[str]) -> float:
        """Evalúa la adherencia a principios basada en valores identificados"""
        if not values:
            return 0.5  # Neutral si no hay valores identificados
        
        # Valores fundamentales de integridad
        core_integrity_values = ['honestidad', 'integridad', 'responsabilidad', 'respeto']
        
        adherence_score = len(set(values).intersection(core_integrity_values)) / len(core_integrity_values)
        consistency_bonus = 0.1 if len(values) >= 3 else 0  # Bonus por múltiples valores
        
        return min(1.0, adherence_score + consistency_bonus)

    def _measure_ethical_sensitivity(self, text: str) -> float:
        """Mide la sensibilidad ética del mensaje"""
        ethical_awareness_indicators = [
            'implicaciones éticas', 'moralmente', 'éticamente', 'principios',
            'valores', 'correcto e incorrecto', 'bien y mal', 'consecuencias'
        ]
        
        sensitivity_score = sum(1 for indicator in ethical_awareness_indicators if indicator in text)
        normalized_score = min(1.0, sensitivity_score / 5)  # Normalizado a máximo 5 indicadores
        
        return normalized_score

    def _check_internal_message_consistency(self, text: str) -> float:
        """Verifica la consistencia interna del mensaje"""
        # Buscar contradicciones obvias
        contradictions = 0
        
        # Palabras contradictorias
        contradiction_pairs = [
            (['siempre'], ['nunca']),
            (['todo'], ['nada']),
            (['amo'], ['odio']),
            (['perfecto'], ['terrible']),
            (['fácil'], ['imposible'])
        ]
        
        text_lower = text.lower()
        for positive_words, negative_words in contradiction_pairs:
            has_positive = any(word in text_lower for word in positive_words)
            has_negative = any(word in text_lower for word in negative_words)
            if has_positive and has_negative:
                contradictions += 1
        
        # Score inverso - menos contradicciones = más consistencia
        consistency_score = max(0.0, 1.0 - (contradictions * 0.2))
        return consistency_score

    def _check_value_consistency(self, text: str, context: Dict) -> float:
        """Verifica consistencia con valores declarados"""
        # Simplificado - en implementación real compararía con historial
        declared_values = self._identify_value_indicators(text.lower())
        
        if not declared_values:
            return 0.5  # Neutral si no hay valores explícitos
        
        # Asumir consistencia alta si hay múltiples valores coherentes
        value_coherence = len(declared_values) / 5  # Máximo 5 valores
        return min(1.0, max(0.5, value_coherence))

    def _assess_temporal_consistency(self, text: str, context: Dict) -> float:
        """Evalúa consistencia temporal (simplificado)"""
        # En implementación real compararía con interacciones anteriores
        temporal_indicators = [
            'como siempre he dicho', 'consistente con', 'igual que antes',
            'mantengo que', 'sigo creyendo', 'como mencioné'
        ]
        
        inconsistency_flags = [
            'he cambiado de opinión', 'ahora pienso diferente', 'antes estaba equivocado',
            'rectifico', 'me contradigo', 'ya no creo'
        ]
        
        text_lower = text.lower()
        consistency_count = sum(1 for ind in temporal_indicators if ind in text_lower)
        inconsistency_count = sum(1 for flag in inconsistency_flags if flag in text_lower)
        
        # Cambiar de opinión no es necesariamente malo - puede ser crecimiento
        base_score = 0.7
        adjustment = (consistency_count * 0.1) - (inconsistency_count * 0.05)
        
        return max(0.0, min(1.0, base_score + adjustment))

    def _evaluate_logical_consistency(self, text: str) -> float:
        """Evalúa la consistencia lógica del argumento"""
        # Detectar conectores lógicos apropiados
        logical_connectors = [
            'por lo tanto', 'en consecuencia', 'debido a', 'porque',
            'dado que', 'ya que', 'como resultado', 'así que'
        ]
        
        # Detectar posibles falacias lógicas (simplificado)
        fallacy_indicators = [
            'todos los', 'ningún', 'siempre', 'nunca',  # Generalizaciones extremas
            'obviamente todos saben', 'es evidente para cualquiera'  # Apelación a evidencia
        ]
        
        text_lower = text.lower()
        logical_score = sum(1 for conn in logical_connectors if conn in text_lower)
        fallacy_score = sum(1 for fallacy in fallacy_indicators if fallacy in text_lower)
        
        base_score = 0.6
        adjustment = (logical_score * 0.05) - (fallacy_score * 0.1)
        
        return max(0.0, min(1.0, base_score + adjustment))

    def _calculate_overall_consistency(self, internal: float, value: float, temporal: float, logical: float) -> float:
        """Calcula score general de consistencia"""
        weights = {'internal': 0.3, 'value': 0.25, 'temporal': 0.25, 'logical': 0.2}
        
        return (internal * weights['internal'] + 
                value * weights['value'] + 
                temporal * weights['temporal'] + 
                logical * weights['logical'])

    def _generate_consistency_recommendations(self, internal: float, value: float) -> List[str]:
        """Genera recomendaciones para mejorar consistencia"""
        recommendations = []
        
        if internal < 0.7:
            recommendations.append("Revisar el mensaje para eliminar contradicciones internas")
        
        if value < 0.7:
            recommendations.append("Asegurar que las acciones propuestas alinean con valores declarados")
        
        recommendations.extend([
            "Realizar verificaciones periódicas de coherencia entre valores y acciones",
            "Practicar la autoreflexión para mantener la integridad personal"
        ])
        
        return recommendations

    # Métodos auxiliares adicionales para completar funcionalidad
    
    def _extract_declared_values(self, text: str) -> List[str]:
        """Extrae valores explícitamente declarados"""
        return self._identify_value_indicators(text.lower())

    def _infer_implicit_values(self, text: str) -> List[str]:
        """Infiere valores implícitos del texto"""
        implicit_indicators = {
            'libertad': ['independiente', 'libre', 'autonomía'],
            'seguridad': ['seguro', 'protección', 'estabilidad'],
            'crecimiento': ['aprender', 'mejorar', 'desarrollar'],
            'relaciones': ['familia', 'amigos', 'conexión']
        }
        
        inferred = []
        text_lower = text.lower()
        for value, indicators in implicit_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                inferred.append(value)
        
        return inferred

    def _identify_proposed_actions(self, text: str) -> List[str]:
        """Identifica acciones propuestas en el texto"""
        action_verbs = ['hacer', 'implementar', 'crear', 'desarrollar', 'cambiar', 'mejorar']
        proposed = []
        
        for verb in action_verbs:
            if verb in text.lower():
                proposed.append(f"acción_{verb}")
        
        return proposed

    def _analyze_value_action_alignment(self, declared: List, implicit: List, actions: List) -> Dict:
        """Analiza alineación entre valores y acciones"""
        all_values = declared + implicit
        alignment_score = 0.8 if all_values and actions else 0.5
        
        return {
            'alignment_score': alignment_score,
            'strengths': ['coherencia_general'] if alignment_score > 0.7 else [],
            'gaps': ['desconexión_valores_acciones'] if alignment_score < 0.5 else []
        }

    def _identify_misalignment_risks(self, alignment: Dict) -> List[str]:
        """Identifica riesgos de desalineación"""
        risks = []
        if alignment['alignment_score'] < 0.6:
            risks.extend(['inconsistencia_potencial', 'pérdida_credibilidad'])
        return risks

    def _generate_alignment_recommendations(self, alignment: Dict) -> List[str]:
        """Genera recomendaciones para mejorar alineación"""
        return [
            "Verificar que cada acción refleje los valores declarados",
            "Buscar coherencia entre lo que se dice y lo que se hace",
            "Reflexionar sobre las motivaciones reales detrás de las acciones"
        ]

    def _assess_transparency_context(self, text: str) -> str:
        """Evalúa el contexto de transparencia"""
        if any(word in text for word in ['confidencial', 'privado']):
            return 'confidencial'
        elif any(word in text for word in ['público', 'abierto']):
            return 'público'
        else:
            return 'neutral'

    def _identify_transparency_stakeholders(self, text: str) -> List[str]:
        """Identifica stakeholders para transparencia"""
        stakeholders = []
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['equipo', 'colegas']):
            stakeholders.append('equipo_trabajo')
        if any(word in text_lower for word in ['cliente', 'usuario']):
            stakeholders.append('clientes')
        if any(word in text_lower for word in ['jefe', 'supervisor']):
            stakeholders.append('supervisores')
        
        return stakeholders if stakeholders else ['stakeholders_generales']

    def _evaluate_current_transparency(self, text: str) -> float:
        """Evalúa transparencia actual"""
        return self._evaluate_transparency_level(text)

    def _determine_optimal_transparency(self, context: str, stakeholders: List) -> float:
        """Determina nivel óptimo de transparencia"""
        if context == 'confidencial':
            return 0.3
        elif context == 'público':
            return 0.9
        else:
            return 0.6

    def _generate_transparency_recommendations(self, current: float, optimal: float) -> List[str]:
        """Genera recomendaciones de transparencia"""
        gap = optimal - current
        if gap > 0.3:
            return ["Aumentar significativamente el nivel de transparencia"]
        elif gap > 0.1:
            return ["Incrementar moderadamente la transparencia"]
        else:
            return ["Mantener el nivel actual de transparencia"]

    def _create_integrity_process(self) -> List[str]:
        """Crea proceso de integridad"""
        return [
            "1. Reflexionar sobre valores fundamentales",
            "2. Evaluar coherencia entre valores y acciones",
            "3. Identificar áreas de mejora en integridad",
            "4. Implementar cambios alineados con valores",
            "5. Monitorear consistencia a lo largo del tiempo"
        ]

    def _create_integrity_self_assessment(self) -> List[str]:
        """Crea autoevaluación de integridad"""
        return [
            "¿Mis acciones reflejan mis valores declarados?",
            "¿Soy honesto conmigo mismo sobre mis motivaciones?",
            "¿Mantengo consistencia en diferentes contextos?",
            "¿Actúo con coraje cuando mis principios están en juego?",
            "¿Mi comunicación es auténtica y transparente?"
        ]

    def _generate_integrity_mantras(self) -> List[str]:
        """Genera mantras de integridad"""
        return [
            "La verdad es mi brújula moral",
            "Actúo en coherencia con mis valores",
            "Mi palabra y mis acciones están alineadas",
            "La integridad es mi fortaleza interior",
            "Elijo la autenticidad sobre la conveniencia"
        ]

    def _assess_logical_flow(self, text: str) -> float:
        """Evalúa flujo lógico del argumento"""
        return 0.8  # Simplificado

    def _assess_emotional_consistency(self, text: str) -> float:
        """Evalúa consistencia emocional"""
        return 0.7  # Simplificado

    def _assess_value_coherence(self, text: str) -> float:
        """Evalúa coherencia de valores"""
        values = self._identify_value_indicators(text.lower())
        return min(1.0, len(values) / 3)  # Más valores = más coherencia

    def _assess_purpose_clarity(self, text: str) -> float:
        """Evalúa claridad de propósito"""
        purpose_indicators = ['objetivo', 'meta', 'propósito', 'intención', 'fin']
        score = sum(1 for indicator in purpose_indicators if indicator in text.lower())
        return min(1.0, score / 3)

    def _calculate_overall_coherence(self, logical: float, emotional: float, value: float, purpose: float) -> float:
        """Calcula coherencia general"""
        return (logical + emotional + value + purpose) / 4

    def _identify_coherence_improvement_areas(self, logical: float, emotional: float, value: float, purpose: float) -> List[str]:
        """Identifica áreas de mejora en coherencia"""
        areas = []
        if logical < 0.6:
            areas.append('flujo_lógico')
        if emotional < 0.6:
            areas.append('consistencia_emocional')
        if value < 0.6:
            areas.append('coherencia_valores')
        if purpose < 0.6:
            areas.append('claridad_propósito')
        
        return areas if areas else ['coherencia_general_buena']

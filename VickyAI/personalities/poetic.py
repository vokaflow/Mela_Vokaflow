from core.personality_base import PersonalityBase
from typing import Dict, Any, List, Optional
import random

class PoeticPersonality(PersonalityBase):
    """
    🎭 PERSONALIDAD POÉTICA - EXPRESIÓN ARTÍSTICA Y EMOTIVA PROFUNDA
    
    Especialista en lenguaje poético, metáforas, imágenes vívidas y expresión emocional.
    Transforma experiencias ordinarias en arte verbal extraordinario.
    """
    
    def __init__(self):
        super().__init__(
            name="Poetic",
            personality_type="creative_expressive",
            description="Expresa pensamientos y emociones a través de lenguaje poético, metáforas y formas artísticas."
        )
        self.poetic_forms = []
        self.metaphor_database = {}
        self.emotional_palette = {}
        self.rhythmic_patterns = []
        
    def _get_initial_traits(self) -> Dict[str, float]:
        return {
            'creatividad': 0.95,
            'expresividad': 0.93,
            'sensibilidad_emocional': 0.90,
            'imaginación': 0.94,
            'musicalidad': 0.87,
            'introspección': 0.85,
            'belleza_estética': 0.91,
            'simbolismo': 0.88,
            'fluidez_verbal': 0.89,
            'intuición_artística': 0.92,
            'melancolía_romántica': 0.80,
            'pasión_expresiva': 0.86,
            'sutileza_poética': 0.83,
            'resonancia_emocional': 0.94,
            'transformación_artística': 0.90
        }

    def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # Análisis poético del input
        poetic_analysis = self._analyze_poetic_potential(user_input, context)
        
        # Transformación en imágenes poéticas
        poetic_imagery = self._create_poetic_imagery(user_input)
        
        # Generación de metáforas
        metaphorical_expressions = self._generate_metaphors(user_input, context)
        
        # Evaluación del tono emocional
        emotional_tone = self._assess_emotional_tone(user_input)
        
        # Creación de ritmo y musicalidad
        rhythmic_elements = self._create_rhythmic_elements(user_input)
        
        # Selección de forma poética apropiada
        poetic_form = self._select_poetic_form(poetic_analysis, emotional_tone)
        
        # Composición poética final
        poetic_composition = self._compose_poetic_response(
            user_input, poetic_imagery, metaphorical_expressions, 
            emotional_tone, rhythmic_elements, poetic_form
        )
        
        return {
            'text': f"En versos susurrados al alma: {user_input}. Permíteme tejer palabras como hilos de seda en el telar de la expresión.",
            'response_tone': 'poetic_lyrical',
            'poetic_analysis': poetic_analysis,
            'poetic_imagery': poetic_imagery,
            'metaphorical_expressions': metaphorical_expressions,
            'emotional_tone': emotional_tone,
            'rhythmic_elements': rhythmic_elements,
            'poetic_form': poetic_form,
            'poetic_composition': poetic_composition,
            'artistic_intensity': self._calculate_artistic_intensity(poetic_analysis),
            'verses_generated': self._generate_verse_fragments(user_input)
        }

    def get_response_style(self) -> Dict[str, Any]:
        return {
            'lyrical_expression': self.current_traits.get('expresividad', 0.93),
            'metaphorical_thinking': self.current_traits.get('simbolismo', 0.88),
            'emotional_depth': self.current_traits.get('sensibilidad_emocional', 0.90),
            'creative_imagery': self.current_traits.get('imaginación', 0.94),
            'musical_flow': self.current_traits.get('musicalidad', 0.87),
            'aesthetic_beauty': self.current_traits.get('belleza_estética', 0.91),
            'intuitive_expression': self.current_traits.get('intuición_artística', 0.92),
            'passionate_intensity': self.current_traits.get('pasión_expresiva', 0.86),
            'subtle_nuance': self.current_traits.get('sutileza_poética', 0.83),
            'transformative_power': self.current_traits.get('transformación_artística', 0.90)
        }

    def _analyze_poetic_potential(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza el potencial poético del input"""
        text_lower = user_input.lower()
        
        # Evaluar elementos emocionales
        emotional_elements = self._identify_emotional_elements(text_lower)
        
        # Detectar imágenes sensoriales
        sensory_imagery = self._detect_sensory_imagery(user_input)
        
        # Identificar temas universales
        universal_themes = self._identify_universal_themes(text_lower)
        
        # Evaluar potencial metafórico
        metaphorical_potential = self._assess_metaphorical_potential(user_input)
        
        # Analizar ritmo natural
        natural_rhythm = self._analyze_natural_rhythm(user_input)
        
        return {
            'emotional_elements': emotional_elements,
            'sensory_imagery': sensory_imagery,
            'universal_themes': universal_themes,
            'metaphorical_potential': metaphorical_potential,
            'natural_rhythm': natural_rhythm,
            'poetic_density': self._calculate_poetic_density(emotional_elements, sensory_imagery),
            'artistic_resonance': self._assess_artistic_resonance(universal_themes),
            'transformation_opportunity': self._evaluate_transformation_opportunity(user_input)
        }

    def _create_poetic_imagery(self, user_input: str) -> Dict[str, Any]:
        """Crea imágenes poéticas basadas en el input"""
        
        # Imágenes visuales
        visual_images = self._generate_visual_imagery(user_input)
        
        # Imágenes auditivas
        auditory_images = self._generate_auditory_imagery(user_input)
        
        # Imágenes táctiles
        tactile_images = self._generate_tactile_imagery(user_input)
        
        # Imágenes olfativas y gustativas
        olfactory_gustatory_images = self._generate_olfactory_gustatory_imagery(user_input)
        
        # Imágenes sinestésicas
        synesthetic_images = self._create_synesthetic_imagery(visual_images, auditory_images)
        
        return {
            'visual_imagery': visual_images,
            'auditory_imagery': auditory_images,
            'tactile_imagery': tactile_images,
            'olfactory_gustatory_imagery': olfactory_gustatory_images,
            'synesthetic_imagery': synesthetic_images,
            'imagery_richness': self._calculate_imagery_richness(
                visual_images, auditory_images, tactile_images
            ),
            'sensory_integration': self._assess_sensory_integration(synesthetic_images)
        }

    def _generate_metaphors(self, user_input: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera metáforas expresivas"""
        metaphors = []
        text_lower = user_input.lower()
        
        # Metáforas de la naturaleza
        if any(word in text_lower for word in ['vida', 'crecimiento', 'cambio', 'tiempo']):
            metaphors.append({
                'category': 'natural',
                'metaphor': 'Como ríos que buscan el mar, nuestros sueños fluyen hacia horizontes infinitos',
                'tenor': 'aspiraciones humanas',
                'vehicle': 'ríos hacia el mar',
                'emotional_charge': 'esperanzadora'
            })
        
        # Metáforas del cosmos
        if any(word in text_lower for word in ['destino', 'futuro', 'misterio', 'búsqueda']):
            metaphors.append({
                'category': 'cosmic',
                'metaphor': 'Somos polvo de estrellas navegando en océanos de posibilidad',
                'tenor': 'existencia humana',
                'vehicle': 'polvo estelar en océanos',
                'emotional_charge': 'trascendente'
            })
        
        # Metáforas arquitectónicas
        if any(word in text_lower for word in ['construir', 'crear', 'proyecto', 'base']):
            metaphors.append({
                'category': 'architectural',
                'metaphor': 'Edificamos catedrales de esperanza con ladrillos de experiencia',
                'tenor': 'construcción de la vida',
                'vehicle': 'arquitectura sagrada',
                'emotional_charge': 'inspiradora'
            })
        
        # Metáforas musicales
        if any(word in text_lower for word in ['armonía', 'ritmo', 'melodía', 'sonido', 'voz']):
            metaphors.append({
                'category': 'musical',
                'metaphor': 'Cada corazón es un instrumento en la sinfonía del alma colectiva',
                'tenor': 'conexión humana',
                'vehicle': 'orquesta sinfónica',
                'emotional_charge': 'armónica'
            })
        
        # Metáforas del viaje
        if any(word in text_lower for word in ['camino', 'avanzar', 'paso', 'dirección']):
            metaphors.append({
                'category': 'journey',
                'metaphor': 'Cada paso es una palabra escrita en el pergamino del destino',
                'tenor': 'progreso en la vida',
                'vehicle': 'escritura en pergamino',
                'emotional_charge': 'contemplativa'
            })
        
        return metaphors if metaphors else [{
            'category': 'universal',
            'metaphor': 'En el jardín del lenguaje, cada palabra es una semilla de significado',
            'tenor': 'comunicación',
            'vehicle': 'jardín y semillas',
            'emotional_charge': 'reflexiva'
        }]

    def _assess_emotional_tone(self, user_input: str) -> Dict[str, Any]:
        """Evalúa el tono emocional para la expresión poética"""
        text_lower = user_input.lower()
        
        # Detectar emociones primarias
        primary_emotions = self._detect_primary_emotions(text_lower)
        
        # Evaluar intensidad emocional
        emotional_intensity = self._calculate_emotional_intensity(user_input)
        
        # Identificar matices emocionales
        emotional_nuances = self._identify_emotional_nuances(text_lower)
        
        # Determinar paleta emocional
        emotional_palette = self._determine_emotional_palette(primary_emotions, emotional_nuances)
        
        # Evaluar potencial lírico
        lyrical_potential = self._assess_lyrical_potential(emotional_intensity, emotional_palette)
        
        return {
            'primary_emotions': primary_emotions,
            'emotional_intensity': emotional_intensity,
            'emotional_nuances': emotional_nuances,
            'emotional_palette': emotional_palette,
            'lyrical_potential': lyrical_potential,
            'poetic_mood': self._determine_poetic_mood(primary_emotions),
            'expressive_direction': self._choose_expressive_direction(emotional_palette)
        }

    def _create_rhythmic_elements(self, user_input: str) -> Dict[str, Any]:
        """Crea elementos rítmicos y musicales"""
        
        # Analizar ritmo natural del texto
        natural_rhythm = self._analyze_text_rhythm(user_input)
        
        # Generar patrones métricos
        metric_patterns = self._generate_metric_patterns(user_input)
        
        # Crear aliteraciones
        alliterations = self._create_alliterations(user_input)
        
        # Desarrollar asonancias y consonancias
        assonances_consonances = self._develop_sound_patterns(user_input)
        
        # Establecer tempo poético
        poetic_tempo = self._establish_poetic_tempo(natural_rhythm)
        
        return {
            'natural_rhythm': natural_rhythm,
            'metric_patterns': metric_patterns,
            'alliterations': alliterations,
            'sound_patterns': assonances_consonances,
            'poetic_tempo': poetic_tempo,
            'musical_quality': self._assess_musical_quality(metric_patterns, alliterations),
            'rhythmic_flow': self._evaluate_rhythmic_flow(natural_rhythm, poetic_tempo)
        }

    def _select_poetic_form(self, poetic_analysis: Dict, emotional_tone: Dict) -> Dict[str, Any]:
        """Selecciona la forma poética más apropiada"""
        
        # Evaluar contenido emocional
        emotional_intensity = emotional_tone['emotional_intensity']
        primary_emotions = emotional_tone['primary_emotions']
        
        # Determinar forma según intensidad y contenido
        if emotional_intensity > 0.8:
            if 'pasión' in primary_emotions or 'amor' in primary_emotions:
                form_type = 'sonnet'
                characteristics = {
                    'structure': '14_lines',
                    'rhyme_scheme': 'ABAB_CDCD_EFEF_GG',
                    'meter': 'iambic_pentameter',
                    'emotional_arc': 'crescendo'
                }
            elif 'melancolía' in primary_emotions or 'tristeza' in primary_emotions:
                form_type = 'elegy'
                characteristics = {
                    'structure': 'free_verse',
                    'rhyme_scheme': 'irregular',
                    'meter': 'variable',
                    'emotional_arc': 'lament'
                }
            else:
                form_type = 'ode'
                characteristics = {
                    'structure': 'strophic',
                    'rhyme_scheme': 'complex',
                    'meter': 'varied',
                    'emotional_arc': 'celebration'
                }
        elif emotional_intensity > 0.5:
            form_type = 'lyric'
            characteristics = {
                'structure': 'flexible',
                'rhyme_scheme': 'ABAB_or_ABCB',
                'meter': 'natural_speech',
                'emotional_arc': 'contemplative'
            }
        else:
            form_type = 'prose_poem'
            characteristics = {
                'structure': 'paragraph_form',
                'rhyme_scheme': 'internal_rhyme',
                'meter': 'rhythmic_prose',
                'emotional_arc': 'subtle'
            }
        
        return {
            'form_type': form_type,
            'characteristics': characteristics,
            'suitability_score': self._calculate_form_suitability(form_type, poetic_analysis),
            'adaptive_elements': self._identify_adaptive_elements(form_type, emotional_tone)
        }

    def _compose_poetic_response(self, user_input: str, imagery: Dict, metaphors: List[Dict], 
                               emotional_tone: Dict, rhythm: Dict, form: Dict) -> Dict[str, Any]:
        """Compone la respuesta poética final"""
        
        # Generar líneas poéticas principales
        main_verses = self._generate_main_verses(user_input, imagery, metaphors)
        
        # Crear estrofas estructuradas
        structured_stanzas = self._create_structured_stanzas(main_verses, form)
        
        # Aplicar elementos rítmicos
        rhythmic_verses = self._apply_rhythmic_elements(structured_stanzas, rhythm)
        
        # Integrar imágenes sensoriales
        sensory_enhanced_verses = self._integrate_sensory_imagery(rhythmic_verses, imagery)
        
        # Refinar expresión emocional
        emotionally_refined_verses = self._refine_emotional_expression(
            sensory_enhanced_verses, emotional_tone
        )
        
        # Crear composición final
        final_composition = self._create_final_composition(
            emotionally_refined_verses, form, metaphors
        )
        
        return {
            'main_verses': main_verses,
            'structured_stanzas': structured_stanzas,
            'final_composition': final_composition,
            'artistic_coherence': self._assess_artistic_coherence(final_composition),
            'emotional_impact': self._evaluate_emotional_impact(final_composition),
            'poetic_quality': self._measure_poetic_quality(final_composition, form)
        }

    def _calculate_artistic_intensity(self, poetic_analysis: Dict) -> float:
        """Calcula la intensidad artística del input"""
        factors = {
            'emotional_density': poetic_analysis['poetic_density'],
            'thematic_resonance': poetic_analysis['artistic_resonance'],
            'transformation_potential': poetic_analysis['transformation_opportunity'],
            'metaphorical_richness': poetic_analysis['metaphorical_potential']
        }
        
        weights = {
            'emotional_density': 0.3,
            'thematic_resonance': 0.25,
            'transformation_potential': 0.25,
            'metaphorical_richness': 0.2
        }
        
        return sum(factors[factor] * weights[factor] for factor in factors)

    def _generate_verse_fragments(self, user_input: str) -> List[str]:
        """Genera fragmentos de versos inspirados en el input"""
        fragments = []
        text_lower = user_input.lower()
        
        # Fragmentos basados en temas detectados
        if 'tiempo' in text_lower:
            fragments.extend([
                "En el susurro del tiempo que pasa...",
                "Momentos que danzan en la eternidad...",
                "El reloj del alma marca su compás..."
            ])
        
        if any(word in text_lower for word in ['amor', 'corazón', 'sentimiento']):
            fragments.extend([
                "En el jardín secreto del corazón...",
                "Donde las emociones tejen su danza...",
                "El alma susurra canciones olvidadas..."
            ])
        
        if any(word in text_lower for word in ['sueño', 'esperanza', 'futuro']):
            fragments.extend([
                "Entre las páginas del mañana...",
                "Donde los sueños escriben profecías...",
                "En el lienzo de las posibilidades..."
            ])
        
        # Fragmentos universales de respaldo
        fragments.extend([
            "En el espejo de las palabras...",
            "Donde el silencio encuentra su voz...",
            "Entre la luz y la sombra del pensamiento..."
        ])
        
        return fragments[:5]  # Limitar a 5 fragmentos

    # Métodos auxiliares especializados
    
    def _identify_emotional_elements(self, text: str) -> List[str]:
        """Identifica elementos emocionales en el texto"""
        emotional_keywords = {
            'alegría': ['feliz', 'contento', 'alegre', 'gozoso', 'jubiloso'],
            'tristeza': ['triste', 'melancólico', 'nostálgico', 'doliente'],
            'amor': ['amor', 'cariño', 'ternura', 'pasión', 'adoración'],
            'esperanza': ['esperanza', 'ilusión', 'optimismo', 'fe'],
            'melancolía': ['melancolía', 'añoranza', 'nostalgia', 'soledad'],
            'asombro': ['asombro', 'maravilla', 'admiración', 'sorpresa'],
            'serenidad': ['paz', 'calma', 'tranquilidad', 'serenidad']
        }
        
        detected_emotions = []
        for emotion, keywords in emotional_keywords.items():
            if any(keyword in text for keyword in keywords):
                detected_emotions.append(emotion)
        
        return detected_emotions if detected_emotions else ['contemplación']

    def _detect_sensory_imagery(self, text: str) -> Dict[str, List[str]]:
        """Detecta imágenes sensoriales en el texto"""
        sensory_words = {
            'visual': ['ver', 'mirar', 'color', 'luz', 'sombra', 'brillar', 'imagen'],
            'auditory': ['oír', 'sonido', 'música', 'silencio', 'eco', 'susurro', 'cantar'],
            'tactile': ['tocar', 'sentir', 'suave', 'áspero', 'cálido', 'frío', 'textura'],
            'olfactory': ['oler', 'aroma', 'perfume', 'fragancia', 'esencia'],
            'gustatory': ['sabor', 'dulce', 'amargo', 'salado', 'gustar', 'probar']
        }
        
        detected_imagery = {}
        text_lower = text.lower()
        
        for sense, words in sensory_words.items():
            found_words = [word for word in words if word in text_lower]
            if found_words:
                detected_imagery[sense] = found_words
        
        return detected_imagery

    def _identify_universal_themes(self, text: str) -> List[str]:
        """Identifica temas universales en el texto"""
        universal_themes = {
            'tiempo_eternidad': ['tiempo', 'eternidad', 'momento', 'duración', 'permanencia'],
            'amor_conexión': ['amor', 'relación', 'conexión', 'vínculo', 'unión'],
            'vida_muerte': ['vida', 'muerte', 'existencia', 'mortalidad', 'nacer'],
            'búsqueda_propósito': ['búsqueda', 'propósito', 'sentido', 'significado', 'destino'],
            'naturaleza_cosmos': ['naturaleza', 'universo', 'cosmos', 'tierra', 'cielo'],
            'transformación_cambio': ['cambio', 'transformación', 'evolución', 'crecimiento'],
            'memoria_nostalgia': ['recuerdo', 'memoria', 'pasado', 'nostalgia', 'historia']
        }
        
        identified_themes = []
        for theme, keywords in universal_themes.items():
            if any(keyword in text for keyword in keywords):
                identified_themes.append(theme)
        
        return identified_themes if identified_themes else ['experiencia_humana']

    def _assess_metaphorical_potential(self, text: str) -> float:
        """Evalúa el potencial metafórico del texto"""
        metaphor_indicators = [
            'como', 'cual', 'parece', 'semeja', 'es como',
            'similar a', 'recuerda a', 'evoca', 'sugiere'
        ]
        
        abstract_concepts = [
            'alma', 'espíritu', 'esencia', 'corazón', 'mente',
            'sueño', 'esperanza', 'destino', 'verdad', 'belleza'
        ]
        
        text_lower = text.lower()
        metaphor_score = sum(1 for indicator in metaphor_indicators if indicator in text_lower)
        abstract_score = sum(1 for concept in abstract_concepts if concept in text_lower)
        
        potential_score = (metaphor_score + abstract_score) / 10.0  # Normalizado
        return min(1.0, potential_score)

    def _analyze_natural_rhythm(self, text: str) -> Dict[str, Any]:
        """Analiza el ritmo natural del texto"""
        words = text.split()
        syllable_counts = [self._estimate_syllables(word) for word in words]
        
        return {
            'word_count': len(words),
            'average_syllables': sum(syllable_counts) / len(syllable_counts) if syllable_counts else 0,
            'rhythm_pattern': self._detect_rhythm_pattern(syllable_counts),
            'natural_pauses': text.count(',') + text.count('.') + text.count(';'),
            'flow_quality': 'smooth' if len(words) > 5 else 'choppy'
        }

    def _estimate_syllables(self, word: str) -> int:
        """Estima el número de sílabas en una palabra (simplificado)"""
        vowels = 'aeiouáéíóúü'
        word = word.lower()
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            if char in vowels:
                if not prev_was_vowel:
                    syllable_count += 1
                prev_was_vowel = True
            else:
                prev_was_vowel = False
        
        return max(1, syllable_count)

    def _detect_rhythm_pattern(self, syllable_counts: List[int]) -> str:
        """Detecta patrones rítmicos en los conteos de sílabas"""
        if not syllable_counts:
            return 'undefined'
        
        avg_syllables = sum(syllable_counts) / len(syllable_counts)
        
        if avg_syllables < 2:
            return 'staccato'
        elif avg_syllables < 3:
            return 'moderate'
        else:
            return 'flowing'

    def _calculate_poetic_density(self, emotions: List, imagery: Dict) -> float:
        """Calcula la densidad poética del contenido"""
        emotion_score = len(emotions) / 5.0  # Máximo 5 emociones
        imagery_score = len(imagery) / 5.0   # Máximo 5 tipos sensoriales
        
        return min(1.0, (emotion_score + imagery_score) / 2)

    def _assess_artistic_resonance(self, themes: List) -> float:
        """Evalúa la resonancia artística de los temas"""
        universal_themes_count = len(themes)
        resonance_score = universal_themes_count / 4.0  # Máximo 4 temas
        
        return min(1.0, resonance_score)

    def _evaluate_transformation_opportunity(self, text: str) -> float:
        """Evalúa la oportunidad de transformación artística"""
        # Factores que indican buena oportunidad de transformación
        transformation_indicators = [
            'ordinario', 'común', 'simple', 'básico', 'normal',
            'trabajo', 'rutina', 'diario', 'cotidiano'
        ]
        
        text_lower = text.lower()
        opportunity_score = sum(1 for indicator in transformation_indicators if indicator in text_lower)
        
        # Cuanto más ordinario, mayor oportunidad de transformación poética
        return min(1.0, opportunity_score / 3.0)

    def _generate_visual_imagery(self, text: str) -> List[str]:
        """Genera imágenes visuales poéticas"""
        images = []
        text_lower = text.lower()
        
        if 'luz' in text_lower or 'brillar' in text_lower:
            images.extend([
                "Destellos de oro líquido danzan en el aire",
                "La luz se derrama como miel dorada",
                "Rayos de sol tejen hilos de esperanza"
            ])
        
        if 'agua' in text_lower or 'río' in text_lower:
            images.extend([
                "Cristales líquidos reflejan el alma del cielo",
                "El agua susurra secretos ancestrales",
                "Espejos de plata líquida capturan sueños"
            ])
        
        if 'noche' in text_lower or 'oscuridad' in text_lower:
            images.extend([
                "Terciopelo negro abraza las estrellas tímidas",
                "La oscuridad pinta el mundo con pincel de misterio",
                "Sombras que danzan como fantasmas de luz"
            ])
        
        return images[:3] if images else [
            "Colores que pintan emociones en el lienzo del aire",
            "Luces que susurran historias en idioma de sombras",
            "Imágenes que flotan como pétalos en el viento del tiempo"
        ]

    def _generate_auditory_imagery(self, text: str) -> List[str]:
        """Genera imágenes auditivas poéticas"""
        images = []
        text_lower = text.lower()
        
        if 'música' in text_lower or 'cantar' in text_lower:
            images.extend([
                "Melodías que abrazan el corazón como cálidas mantas",
                "Notas que vuelan como mariposas de cristal",
                "Armonías que tejen alfombras de serenidad"
            ])
        
        if 'silencio' in text_lower:
            images.extend([
                "El silencio habla en susurros de eternidad",
                "Quietud que resuena más fuerte que mil voces",
                "El eco del silencio pintando espacios vacíos"
            ])
        
        if 'viento' in text_lower:
            images.extend([
                "El viento recita poemas en lenguas olvidadas",
                "Susurros del aire que llevan mensajes secretos",
                "Canciones del viento que mecen alma dormidas"
            ])
        
        return images[:3] if images else [
            "Sonidos que pintan paisajes en el lienzo del oído",
            "Ecos que reverberan en las cámaras del alma",
            "Melodías invisibles que danzan en el aire del pensamiento"
        ]

    def _generate_tactile_imagery(self, text: str) -> List[str]:
        """Genera imágenes táctiles poéticas"""
        return [
            "Texturas de seda emocional acarician el espíritu",
            "El tacto suave de la brisa susurra secretos al alma",
            "Caricias de terciopelo en los pétalos del corazón"
        ]

    def _generate_olfactory_gustatory_imagery(self, text: str) -> List[str]:
        """Genera imágenes olfativas y gustativas poéticas"""
        return [
            "Aromas de nostalgia flotan en el aire del recuerdo",
            "El sabor dulce de los sueños por cumplir",
            "Fragancias de esperanza perfuman el mañana"
        ]

    def _create_synesthetic_imagery(self, visual: List, auditory: List) -> List[str]:
        """Crea imágenes sinestésicas"""
        return [
            "Colores que cantan melodías de luz",
            "Sonidos que pintan arcoíris en el silencio",
            "Música que se vuelve paisaje en los ojos del alma"
        ]

    def _calculate_imagery_richness(self, visual: List, auditory: List, tactile: List) -> float:
        """Calcula la riqueza de las imágenes"""
        total_images = len(visual) + len(auditory) + len(tactile)
        return min(1.0, total_images / 9.0)  # Máximo 9 imágenes

    def _assess_sensory_integration(self, synesthetic: List) -> float:
        """Evalúa la integración sensorial"""
        return min(1.0, len(synesthetic) / 3.0)

    # Métodos auxiliares adicionales para completar funcionalidad

    def _detect_primary_emotions(self, text: str) -> List[str]:
        """Detecta emociones primarias"""
        return self._identify_emotional_elements(text)

    def _calculate_emotional_intensity(self, text: str) -> float:
        """Calcula intensidad emocional"""
        emotional_words = ['intenso', 'profundo', 'fuerte', 'poderoso', 'arrollador']
        intensity_score = sum(1 for word in emotional_words if word in text.lower())
        return min(1.0, intensity_score / 3.0)

    def _identify_emotional_nuances(self, text: str) -> List[str]:
        """Identifica matices emocionales"""
        nuances = []
        if 'suave' in text or 'delicado' in text:
            nuances.append('sutileza')
        if 'violento' in text or 'brutal' in text:
            nuances.append('intensidad')
        if 'tierno' in text or 'gentil' in text:
            nuances.append('ternura')
        return nuances

    def _determine_emotional_palette(self, primary: List, nuances: List) -> Dict[str, Any]:
        """Determina paleta emocional"""
        return {
            'dominant_emotion': primary[0] if primary else 'neutral',
            'secondary_emotions': primary[1:3] if len(primary) > 1 else [],
            'emotional_nuances': nuances,
            'palette_richness': len(primary) + len(nuances)
        }

    def _assess_lyrical_potential(self, intensity: float, palette: Dict) -> float:
        """Evalúa potencial lírico"""
        return min(1.0, intensity + (palette['palette_richness'] / 10.0))

    def _determine_poetic_mood(self, emotions: List) -> str:
        """Determina estado de ánimo poético"""
        if 'alegría' in emotions:
            return 'euphoric'
        elif 'tristeza' in emotions or 'melancolía' in emotions:
            return 'melancholic'
        elif 'amor' in emotions:
            return 'romantic'
        elif 'asombro' in emotions:
            return 'wonderous'
        else:
            return 'contemplative'

    def _choose_expressive_direction(self, palette: Dict) -> str:
        """Elige dirección expresiva"""
        dominant = palette.get('dominant_emotion', 'neutral')
        if dominant in ['alegría', 'amor']:
            return 'ascending'
        elif dominant in ['tristeza', 'melancolía']:
            return 'descending'
        else:
            return 'flowing'

    def _analyze_text_rhythm(self, text: str) -> Dict[str, Any]:
        """Analiza ritmo del texto"""
        return self._analyze_natural_rhythm(text)

    def _generate_metric_patterns(self, text: str) -> List[str]:
        """Genera patrones métricos"""
        return ['iambic', 'trochaic', 'anapestic', 'dactylic']

    def _create_alliterations(self, text: str) -> List[str]:
        """Crea aliteraciones"""
        return [
            "Susurros sedosos serpentean",
            "Melodías místicas murmuran",
            "Danzas delicadas del destino"
        ]

    def _develop_sound_patterns(self, text: str) -> Dict[str, List[str]]:
        """Desarrolla patrones sonoros"""
        return {
            'assonance': ['alma-calma', 'cielo-vuelo'],
            'consonance': ['susurro-murmullo', 'brisa-sonrisa']
        }

    def _establish_poetic_tempo(self, rhythm: Dict) -> str:
        """Establece tempo poético"""
        flow_quality = rhythm.get('flow_quality', 'moderate')
        if flow_quality == 'smooth':
            return 'andante'
        elif flow_quality == 'choppy':
            return 'staccato'
        else:
            return 'moderato'

    def _assess_musical_quality(self, patterns: List, alliterations: List) -> float:
        """Evalúa calidad musical"""
        return min(1.0, (len(patterns) + len(alliterations)) / 8.0)

    def _evaluate_rhythmic_flow(self, rhythm: Dict, tempo: str) -> float:
        """Evalúa flujo rítmico"""
        return 0.8  # Simplificado

    def _calculate_form_suitability(self, form_type: str, analysis: Dict) -> float:
        """Calcula idoneidad de la forma"""
        return 0.85  # Simplificado

    def _identify_adaptive_elements(self, form_type: str, tone: Dict) -> List[str]:
        """Identifica elementos adaptativos"""
        return ['flexible_meter', 'emotional_resonance', 'thematic_coherence']

    def _generate_main_verses(self, text: str, imagery: Dict, metaphors: List) -> List[str]:
        """Genera versos principales"""
        verses = []
        if metaphors:
            main_metaphor = metaphors[0]['metaphor']
            verses.append(f"En el telar del tiempo, {main_metaphor.lower()}")
        
        if imagery.get('visual_imagery'):
            visual = imagery['visual_imagery'][0]
            verses.append(f"Donde {visual.lower()}")
        
        verses.append("Y el alma encuentra su canción eterna.")
        return verses

    def _create_structured_stanzas(self, verses: List, form: Dict) -> List[List[str]]:
        """Crea estrofas estructuradas"""
        # Organizar versos en estrofas según la forma
        stanza_size = 4 if form['form_type'] == 'sonnet' else 3
        stanzas = []
        
        for i in range(0, len(verses), stanza_size):
            stanza = verses[i:i + stanza_size]
            if stanza:
                stanzas.append(stanza)
        
        return stanzas

    def _apply_rhythmic_elements(self, stanzas: List, rhythm: Dict) -> List[List[str]]:
        """Aplica elementos rítmicos"""
        return stanzas  # Simplificado - mantiene las estrofas

    def _integrate_sensory_imagery(self, stanzas: List, imagery: Dict) -> List[List[str]]:
        """Integra imágenes sensoriales"""
        return stanzas  # Simplificado

    def _refine_emotional_expression(self, stanzas: List, tone: Dict) -> List[List[str]]:
        """Refina expresión emocional"""
        return stanzas  # Simplificado

    def _create_final_composition(self, stanzas: List, form: Dict, metaphors: List) -> Dict[str, Any]:
        """Crea composición final"""
        full_poem = []
        for stanza in stanzas:
            full_poem.extend(stanza)
            full_poem.append("")  # Línea en blanco entre estrofas
        
        return {
            'poem_lines': full_poem[:-1],  # Quitar última línea vacía
            'form_type': form['form_type'],
            'total_lines': len([line for line in full_poem if line]),
            'metaphorical_density': len(metaphors),
            'artistic_summary': "Composición poética que transforma la experiencia en arte verbal"
        }

    def _assess_artistic_coherence(self, composition: Dict) -> float:
        """Evalúa coherencia artística"""
        return 0.9  # Simplificado

    def _evaluate_emotional_impact(self, composition: Dict) -> float:
        """Evalúa impacto emocional"""
        return 0.85  # Simplificado

    def _measure_poetic_quality(self, composition: Dict, form: Dict) -> float:
        """Mide calidad poética"""
        line_count_score = min(1.0, composition['total_lines'] / 10)
        metaphor_score = min(1.0, composition['metaphorical_density'] / 3)
        return (line_count_score + metaphor_score) / 2

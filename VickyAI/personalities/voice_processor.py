from core.personality_base import PersonalityBase
from typing import Dict, Any, List
import re
import time
# import json # Not used directly in this snippet
from datetime import datetime

class VoiceProcessorPersonality(PersonalityBase):
    def __init__(self):
        super().__init__(
            name="VoiceProcessor",
            personality_type="technical_autonomous", # Assumed
            description="Procesamiento de voz y audio" # Assumed
        )
        # self.traits is initialized by PersonalityBase
        self.specializations = [
            'voice_analysis',
            'speech_processing',
            'audio_enhancement',
            'vocal_pattern_recognition',
            'communication_optimization'
        ]
        self.voice_parameters = ['pitch', 'tone', 'pace', 'volume', 'clarity']
        self.voice_profiles = {}
        self.audio_settings = {
            'sample_rate': 44100,
            'bit_depth': 16,
            'channels': 2,
            'format': 'wav'
        }
        self.speech_synthesis_engines = ['neural_tts', 'concatenative', 'parametric']
        self.voice_models = {
            'female_neutral': {'pitch': 220, 'speed': 1.0, 'emotion': 'neutral'},
            'male_neutral': {'pitch': 120, 'speed': 1.0, 'emotion': 'neutral'},
            'child_friendly': {'pitch': 280, 'speed': 0.9, 'emotion': 'cheerful'},
            'professional': {'pitch': 180, 'speed': 1.1, 'emotion': 'confident'}
        }
        self.audio_processing_history = []
        
    def _get_initial_traits(self) -> Dict[str, float]:
        return {
            'síntesis_voz': 0.95,
            'reconocimiento_voz': 0.93,
            'procesamiento_audio': 0.91,
            'análisis_emocional': 0.89,
            'optimización_calidad': 0.90,
            'adaptación_contexto': 0.88,
            'personalización_voz': 0.87,
            'reducción_ruido': 0.86
        }
    
    def process_input(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]: # Added type hints
        # Assuming user_input is text for synthesis, or context contains audio data
        text_for_synthesis = user_input 
        audio_characteristics_from_context = self._analyze_audio_context(context)

        synthesis_analysis = self._analyze_for_speech_synthesis(text_for_synthesis)
        synthesis_parameters = self._generate_synthesis_parameters(text_for_synthesis, audio_characteristics_from_context)
        device_optimizations = self._optimize_for_devices(synthesis_parameters)
        emotional_processing = self._process_emotional_content(text_for_synthesis)
        voice_recommendations = self._recommend_voice_settings(text_for_synthesis, context if context else {})
        pronunciation_guide = self._generate_pronunciation_guide(text_for_synthesis)
        
        self._record_audio_processing(text_for_synthesis, synthesis_parameters, audio_characteristics_from_context)
        
        return {
            'synthesis_analysis': synthesis_analysis,
            'synthesis_parameters': synthesis_parameters,
            'device_optimizations': device_optimizations,
            'emotional_processing': emotional_processing,
            'voice_recommendations': voice_recommendations,
            'pronunciation_guide': pronunciation_guide,
            'audio_quality_assessment': self._assess_audio_quality(synthesis_parameters)
        }
    
    def get_response_style(self) -> Dict[str, Any]:
        return {
            'tone': 'technical_supportive',
            'structure': 'analytical_systematic',
            'detail_level': 'precise_technical',
            'visualization': 'audio_waveform_concepts'
        }
    
    # ... (rest of the methods from the provided snippet, ensure they have type hints)
    # Make sure all helper methods like _analyze_voice_patterns, _generate_processing_suggestions etc.
    # are correctly defined or adapted if the process_input logic has changed.
    # The original process_input had different calls. I've updated it to reflect a synthesis scenario.

    def _analyze_voice_patterns(self, user_input: str) -> Dict[str, Any]: # Placeholder if needed
        # This method was in the original process_input, adapt if it's for voice input analysis
        return {"pattern": "example"}

    def _generate_processing_suggestions(self, voice_analysis: Dict[str, Any]) -> List[str]: # Placeholder
        return ["suggestion1"]

    def _suggest_enhancements(self, user_input: str) -> List[str]: # Placeholder
        return ["enhancement1"]

    def _optimize_communication(self, user_input: str) -> Dict[str, Any]: # Placeholder
        return {"optimized": True}

    def _generate_technical_specs(self, user_input: str) -> Dict[str, Any]: # Placeholder
        return {"specs": "example"}

    def _analyze_for_speech_synthesis(self, text: str) -> Dict[str, Any]:
        analysis = {
            'text_length': len(text),
            'word_count': len(text.split()),
            'sentence_count': len(re.split(r'[.!?]+', text)),
            'complexity_score': self._calculate_text_complexity(text),
            'punctuation_analysis': self._analyze_punctuation(text),
            'special_characters': self._identify_special_characters(text),
            'pronunciation_challenges': self._identify_pronunciation_challenges(text),
            'estimated_duration': self._estimate_speech_duration(text)
        }
        return analysis

    def _analyze_audio_context(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        if not context or 'audio' not in context:
            return {
                'audio_available': False,
                'default_characteristics': {
                    'speaker_type': 'unknown',
                    'environment': 'neutral',
                    'quality': 'standard'
                }
            }
        audio_context_data = context.get('audio', {})
        characteristics = {
            'audio_available': True,
            'speaker_characteristics': self._analyze_speaker_characteristics(audio_context_data),
            'environment_analysis': self._analyze_audio_environment(audio_context_data),
            'quality_metrics': self._assess_input_audio_quality(audio_context_data),
            'noise_analysis': self._analyze_background_noise(audio_context_data),
            'emotional_indicators': self._detect_emotional_audio_cues(audio_context_data)
        }
        return characteristics

    def _generate_synthesis_parameters(self, text: str, audio_characteristics: Dict[str, Any]) -> Dict[str, Any]:
        base_voice = self._select_base_voice_model(text, audio_characteristics)
        content_adjustments = self._adjust_for_content(text)
        # personalization = self._apply_voice_personalization(audio_characteristics) # personalization not used further
        synthesis_params = {
            'voice_model': base_voice,
            'pitch': self._calculate_optimal_pitch(base_voice, content_adjustments),
            'speed': self._calculate_optimal_speed(text, content_adjustments),
            'volume': self._calculate_optimal_volume(audio_characteristics),
            'emotion': self._determine_emotional_tone(text),
            'emphasis_points': self._identify_emphasis_points(text),
            'pause_patterns': self._generate_pause_patterns(text),
            'intonation_curve': self._generate_intonation_curve(text),
            'breathing_patterns': self._generate_breathing_patterns(text)
        }
        return synthesis_params

    def _optimize_for_devices(self, synthesis_parameters: Dict[str, Any]) -> Dict[str, Any]:
        device_profiles = {
            'smartphone': {'sample_rate': 22050, 'compression': 'high', 'eq_profile': 'mobile_optimized', 'volume_normalization': True},
            'desktop': {'sample_rate': 44100, 'compression': 'low', 'eq_profile': 'full_range', 'volume_normalization': False},
            'smart_speaker': {'sample_rate': 16000, 'compression': 'medium', 'eq_profile': 'voice_optimized', 'volume_normalization': True},
            'headphones': {'sample_rate': 48000, 'compression': 'minimal', 'eq_profile': 'audiophile', 'volume_normalization': False}
        }
        optimizations = {}
        for device, profile in device_profiles.items():
            optimized_params = synthesis_parameters.copy()
            optimized_params.update({
                'device_profile': profile,
                'optimized_for': device,
                'quality_level': self._determine_quality_level(device),
                'latency_optimization': self._optimize_latency(device)
            })
            optimizations[device] = optimized_params
        return optimizations

    def _process_emotional_content(self, text: str) -> Dict[str, Any]:
        emotional_indicators = {
            'joy': ['feliz', 'alegre', 'contento', 'genial', 'fantástico', 'excelente'],
            'sadness': ['triste', 'melancólico', 'deprimido', 'lamentable', 'desafortunado'],
            'anger': ['enojado', 'furioso', 'molesto', 'irritado', 'indignado'],
            'fear': ['miedo', 'temor', 'asustado', 'nervioso', 'preocupado'],
            'surprise': ['sorpresa', 'asombro', 'increíble', 'inesperado', 'wow'],
            'excitement': ['emocionado', 'entusiasmado', 'ansioso', 'expectante']
        }
        detected_emotions = {}
        text_lower = text.lower()
        for emotion, indicators in emotional_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            if score > 0:
                detected_emotions[emotion] = score / len(indicators)
        dominant_emotion = max(detected_emotions, key=detected_emotions.get) if detected_emotions else 'neutral'
        emotional_synthesis = {
            'dominant_emotion': dominant_emotion,
            'emotion_intensity': detected_emotions.get(dominant_emotion, 0.5),
            'emotional_modulations': self._generate_emotional_modulations(dominant_emotion),
            'prosodic_adjustments': self._generate_prosodic_adjustments(dominant_emotion),
            'voice_quality_changes': self._generate_voice_quality_changes(dominant_emotion)
        }
        return emotional_synthesis

    def _recommend_voice_settings(self, text: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        recommendations = []
        content_type = self._classify_content_type(text)
        if content_type == 'educational':
            recommendations.append({'setting': 'educational_voice', 'description': 'Voz clara y pausada para contenido educativo', 'parameters': {'speed': 0.9, 'clarity': 'high', 'emphasis': 'moderate'}})
        elif content_type == 'entertainment':
            recommendations.append({'setting': 'expressive_voice', 'description': 'Voz expresiva y dinámica para entretenimiento', 'parameters': {'expressiveness': 'high', 'variation': 'dynamic', 'energy': 'elevated'}})
        elif content_type == 'professional':
            recommendations.append({'setting': 'professional_voice', 'description': 'Voz profesional y confiable', 'parameters': {'formality': 'high', 'confidence': 'strong', 'pace': 'measured'}})
        
        if context and 'environment' in context: # Check if context is not None
            environment = context.get('environment', 'unknown') # Use .get for safety
            if environment == 'noisy':
                recommendations.append({'setting': 'noise_resistant', 'description': 'Optimizado para ambientes ruidosos', 'parameters': {'volume': 'elevated', 'clarity': 'maximum', 'frequency_emphasis': 'mid_range'}})
        return recommendations

    def _generate_pronunciation_guide(self, text: str) -> Dict[str, Any]:
        difficult_words = self._identify_difficult_pronunciations(text)
        phonetic_transcriptions = self._generate_phonetic_transcriptions(difficult_words)
        stress_patterns = self._identify_stress_patterns(text)
        pronunciation_guide = {
            'difficult_words': difficult_words,
            'phonetic_transcriptions': phonetic_transcriptions,
            'stress_patterns': stress_patterns,
            'pronunciation_tips': self._generate_pronunciation_tips(difficult_words),
            'alternative_pronunciations': self._suggest_alternative_pronunciations(difficult_words)
        }
        return pronunciation_guide

    def _record_audio_processing(self, text: str, synthesis_params: Dict[str, Any], audio_characteristics: Dict[str, Any]):
        processing_record = {
            'timestamp': datetime.now().isoformat(),
            'text_length': len(text),
            'processing_type': 'speech_synthesis',
            'voice_model_used': synthesis_params.get('voice_model', 'default'),
            'emotional_content': synthesis_params.get('emotion', 'neutral'),
            'audio_quality': audio_characteristics.get('quality_metrics', {}),
            'processing_duration': time.time() # Simulated, consider actual timing
        }
        self.audio_processing_history.append(processing_record)
        if len(self.audio_processing_history) > 50:
            self.audio_processing_history = self.audio_processing_history[-50:]

    def _assess_audio_quality(self, synthesis_parameters: Dict[str, Any]) -> Dict[str, Any]:
        quality_metrics = {
            'clarity_score': 0.9, 'naturalness_score': 0.85, 'expressiveness_score': 0.8,
            'intelligibility_score': 0.95, 'overall_quality': 'high',
            'quality_factors': {
                'voice_model_quality': synthesis_parameters.get('voice_model', 'standard'),
                'emotional_accuracy': synthesis_parameters.get('emotion', 'neutral'),
                'prosodic_quality': 'good', 'audio_fidelity': 'high'
            }
        }
        return quality_metrics

    def _calculate_text_complexity(self, text: str) -> float:
        words = text.split()
        if not words: return 0.0
        avg_word_length = sum(len(word) for word in words) / len(words)
        long_words = sum(1 for word in words if len(word) > 6)
        complex_punctuation = len(re.findall(r'[;:()[\]{}"]', text))
        complexity = (avg_word_length / 10) + (long_words / len(words)) + (complex_punctuation / (len(text) if len(text) > 0 else 1))
        return min(1.0, complexity)

    def _analyze_punctuation(self, text: str) -> Dict[str, int]:
        return {'periods': text.count('.'), 'commas': text.count(','), 'questions': text.count('?'), 'exclamations': text.count('!'), 'semicolons': text.count(';'), 'colons': text.count(':')}

    def _identify_special_characters(self, text: str) -> List[str]:
        special_chars = []
        if re.search(r'\d+', text): special_chars.append('numbers')
        if re.search(r'\b[A-Z]{2,}\b', text): special_chars.append('abbreviations')
        if re.search(r'http[s]?://\S+', text): special_chars.append('urls')
        if re.search(r'\S+@\S+\.\S+', text): special_chars.append('emails')
        return special_chars

    def _identify_pronunciation_challenges(self, text: str) -> List[str]:
        challenges = []
        if re.search(r'\b\w*[bcdfghjklmnpqrstvwxyz]{3,}\w*\b', text, re.IGNORECASE): challenges.append('consonant_clusters')
        foreign_patterns = [r'\b\w*sch\w*\b', r'\b\w*tch\w*\b', r'\b\w*ght\w*\b']
        for pattern in foreign_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                challenges.append('foreign_words'); break
        return challenges

    def _estimate_speech_duration(self, text: str) -> float:
        words = len(text.split())
        duration_minutes = words / 150
        return duration_minutes * 60

    def _analyze_speaker_characteristics(self, audio_context: Dict[str, Any]) -> Dict[str, Any]:
        return {'estimated_age': audio_context.get('age', 'adult'), 'estimated_gender': audio_context.get('gender', 'neutral'), 'accent_detected': audio_context.get('accent', 'neutral'), 'speaking_rate': audio_context.get('rate', 'normal'), 'voice_quality': audio_context.get('quality', 'clear')}

    def _analyze_audio_environment(self, audio_context: Dict[str, Any]) -> Dict[str, Any]:
        return {'noise_level': audio_context.get('noise_level', 'low'), 'reverb_detected': audio_context.get('reverb', False), 'echo_present': audio_context.get('echo', False), 'environment_type': audio_context.get('environment', 'indoor')}

    def _assess_input_audio_quality(self, audio_context: Dict[str, Any]) -> Dict[str, float]:
        return {'clarity': audio_context.get('clarity', 0.8), 'signal_to_noise': audio_context.get('snr', 0.7), 'frequency_response': audio_context.get('freq_response', 0.8), 'dynamic_range': audio_context.get('dynamic_range', 0.75)}

    def _analyze_background_noise(self, audio_context: Dict[str, Any]) -> Dict[str, Any]:
        return {'noise_type': audio_context.get('noise_type', 'ambient'), 'noise_level_db': audio_context.get('noise_db', 30), 'noise_frequency': audio_context.get('noise_freq', 'broadband'), 'noise_consistency': audio_context.get('noise_consistency', 'steady')}

    def _detect_emotional_audio_cues(self, audio_context: Dict[str, Any]) -> Dict[str, float]:
        return {'pitch_variation': audio_context.get('pitch_var', 0.5), 'energy_level': audio_context.get('energy', 0.6), 'speaking_rate_emotion': audio_context.get('rate_emotion', 0.5), 'voice_tension': audio_context.get('tension', 0.3)}

    def _select_base_voice_model(self, text: str, audio_characteristics: Dict[str, Any]) -> str:
        content_type = self._classify_content_type(text)
        if content_type == 'professional': return 'professional'
        elif content_type == 'educational': return 'female_neutral'
        elif content_type == 'entertainment': return 'male_neutral'
        else: return 'female_neutral'

    def _adjust_for_content(self, text: str) -> Dict[str, float]:
        adjustments = {'speed_modifier': 1.0, 'pitch_modifier': 1.0, 'emphasis_modifier': 1.0}
        word_count = len(text.split())
        if word_count > 100: adjustments['speed_modifier'] = 0.95
        complexity = self._calculate_text_complexity(text)
        if complexity > 0.7:
            adjustments['speed_modifier'] *= 0.9
            adjustments['emphasis_modifier'] = 1.2
        return adjustments

    def _apply_voice_personalization(self, audio_characteristics: Dict[str, Any]) -> Dict[str, Any]:
        if not audio_characteristics.get('audio_available', False): return {'personalization': 'none'}
        speaker_chars = audio_characteristics.get('speaker_characteristics', {})
        personalization = {'pitch_adaptation': self._adapt_pitch(speaker_chars), 'speed_adaptation': self._adapt_speed(speaker_chars), 'style_adaptation': self._adapt_style(speaker_chars)}
        return personalization

    def _calculate_optimal_pitch(self, base_voice: str, adjustments: Dict[str, float]) -> float:
        base_pitch = self.voice_models[base_voice]['pitch']
        modifier = adjustments.get('pitch_modifier', 1.0)
        return base_pitch * modifier

    def _calculate_optimal_speed(self, text: str, adjustments: Dict[str, float]) -> float:
        base_speed = 1.0
        modifier = adjustments.get('speed_modifier', 1.0)
        return base_speed * modifier

    def _calculate_optimal_volume(self, audio_characteristics: Dict[str, Any]) -> float:
        if audio_characteristics.get('audio_available', False):
            noise_level = audio_characteristics.get('environment_analysis', {}).get('noise_level', 'low')
            if noise_level == 'high': return 0.9
            elif noise_level == 'medium': return 0.7
        return 0.6

    def _determine_emotional_tone(self, text: str) -> str:
        emotional_content = self._process_emotional_content(text)
        return emotional_content.get('dominant_emotion', 'neutral')

    def _identify_emphasis_points(self, text: str) -> Dict[str, Any]: # Changed return type
        emphasis_indicators = ['!', '?', 'muy', 'realmente', 'absolutamente']
        emphasis_count = sum(1 for indicator in emphasis_indicators if indicator in text.lower())
        return {'emphasis_level': 'high' if emphasis_count > 3 else 'moderate' if emphasis_count > 1 else 'low', 'emphasis_points': emphasis_count, 'suggested_vocal_stress': self._suggest_vocal_stress(emphasis_count)}

    def _suggest_vocal_stress(self, emphasis_count: int) -> str: # Added helper
        if emphasis_count > 3: return "strong"
        if emphasis_count > 1: return "moderate"
        return "normal"

    def _generate_pause_patterns(self, text: str) -> List[Dict[str, Any]]:
        pauses = []
        punctuation_pauses = {'.': 0.5, ',': 0.2, ';': 0.3, ':': 0.3, '!': 0.4, '?': 0.4}
        for punct, duration in punctuation_pauses.items():
            positions = [m.start() for m in re.finditer(re.escape(punct), text)]
            for pos in positions:
                pauses.append({'position': pos, 'duration': duration, 'type': f'punctuation_{punct}'})
        return pauses

    def _generate_intonation_curve(self, text: str) -> Dict[str, Any]:
        return {'pattern': 'declarative', 'rise_points': [], 'fall_points': [], 'peak_intensity': 0.8}

    def _generate_breathing_patterns(self, text: str) -> List[Dict[str, Any]]:
        breathing_points = []
        sentences = re.split(r'[.!?]+', text)
        current_pos = 0
        for sentence in sentences:
            if sentence.strip():
                current_pos += len(sentence) + 1 # Account for separator
                breathing_points.append({'position': current_pos, 'type': 'natural_break', 'duration': 0.3})
        return breathing_points

    def _classify_content_type(self, text: str) -> str:
        educational_keywords = ['aprender', 'enseñar', 'explicar', 'estudiar', 'lección']
        professional_keywords = ['empresa', 'negocio', 'proyecto', 'reunión', 'informe']
        entertainment_keywords = ['divertido', 'gracioso', 'entretenido', 'juego', 'historia']
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in educational_keywords): return 'educational'
        elif any(keyword in text_lower for keyword in professional_keywords): return 'professional'
        elif any(keyword in text_lower for keyword in entertainment_keywords): return 'entertainment'
        else: return 'general'

    def _generate_emotional_modulations(self, emotion: str) -> Dict[str, float]:
        modulations = {'joy': {'pitch_variation': 1.2, 'speed_variation': 1.1, 'energy': 1.3}, 'sadness': {'pitch_variation': 0.8, 'speed_variation': 0.9, 'energy': 0.7}, 'anger': {'pitch_variation': 1.1, 'speed_variation': 1.2, 'energy': 1.4}, 'fear': {'pitch_variation': 1.3, 'speed_variation': 1.1, 'energy': 0.9}, 'neutral': {'pitch_variation': 1.0, 'speed_variation': 1.0, 'energy': 1.0}}
        return modulations.get(emotion, modulations['neutral'])

    def _generate_prosodic_adjustments(self, emotion: str) -> Dict[str, Any]:
        return {'stress_pattern': 'normal', 'rhythm_adjustment': 1.0, 'intonation_range': 'normal'}

    def _generate_voice_quality_changes(self, emotion: str) -> Dict[str, Any]:
        return {'breathiness': 0.0, 'roughness': 0.0, 'tension': 0.0}

    def _determine_quality_level(self, device: str) -> str:
        quality_map = {'smartphone': 'medium', 'desktop': 'high', 'smart_speaker': 'medium', 'headphones': 'highest'}
        return quality_map.get(device, 'medium')

    def _optimize_latency(self, device: str) -> Dict[str, Any]:
        return {'buffer_size': 'optimal', 'processing_priority': 'high', 'streaming_enabled': True}

    def _identify_difficult_pronunciations(self, text: str) -> List[str]:
        difficult_patterns = [r'\b\w*rr\w*\b', r'\b\w*[bcdfghjklmnpqrstvwxyz]{3,}\w*\b', r'\b[A-Z]{2,}\b']
        difficult_words = []
        for pattern in difficult_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            difficult_words.extend(matches)
        return list(set(difficult_words))

    def _generate_phonetic_transcriptions(self, words: List[str]) -> Dict[str, str]:
        transcriptions = {}
        for word in words:
            transcriptions[word] = f"[{word.lower()}]"
        return transcriptions

    def _identify_stress_patterns(self, text: str) -> List[Dict[str, Any]]:
        stress_patterns = []
        accented_words = re.findall(r'\b\w*[áéíóúü]\w*\b', text, re.IGNORECASE)
        for word in accented_words:
            stress_patterns.append({'word': word, 'stress_type': 'graphic_accent', 'syllable_stress': 'marked'})
        return stress_patterns

    def _generate_pronunciation_tips(self, words: List[str]) -> List[str]:
        tips = []
        for word in words:
            if 'rr' in word.lower(): tips.append(f"Para '{word}': vibrar la lengua en la RR")
            elif len(word) > 8: tips.append(f"Para '{word}': dividir en sílabas para mejor pronunciación")
        return tips

    def _suggest_alternative_pronunciations(self, words: List[str]) -> Dict[str, List[str]]:
        alternatives = {}
        for word in words:
            alternatives[word] = [f"{word}_alt1", f"{word}_alt2"]
        return alternatives

    def _adapt_pitch(self, speaker_characteristics: Dict[str, Any]) -> float:
        gender = speaker_characteristics.get('estimated_gender', 'neutral')
        if gender == 'male': return 0.8
        elif gender == 'female': return 1.2
        return 1.0

    def _adapt_speed(self, speaker_characteristics: Dict[str, Any]) -> float:
        rate = speaker_characteristics.get('speaking_rate', 'normal')
        if rate == 'fast': return 1.1
        elif rate == 'slow': return 0.9
        return 1.0

    def _adapt_style(self, speaker_characteristics: Dict[str, Any]) -> str:
        quality = speaker_characteristics.get('voice_quality', 'clear')
        if quality == 'rough': return 'casual'
        elif quality == 'smooth': return 'professional'
        return 'neutral'

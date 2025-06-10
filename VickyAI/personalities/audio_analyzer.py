from core.personality_base import PersonalityBase
from typing import Dict, Any, List # Added List
import math # Not directly used in this snippet, but good for audio math
import re # For text analysis if input is descriptive

class AudioAnalyzerPersonality(PersonalityBase):
    def __init__(self):
        super().__init__(
            name="AudioAnalyzer",
            personality_type="technical_autonomous", # Assumed
            description="Analyzes audio signals and characteristics." # Assumed
        )
        # self.traits is initialized by PersonalityBase
        self.specializations = [
            'audio_signal_analysis',
            'frequency_domain_processing',
            'acoustic_measurement',
            'sound_quality_assessment',
            'audio_enhancement'
        ]
        self.frequency_ranges = {
            'sub_bass': (20, 60), 'bass': (60, 250),
            'low_midrange': (250, 500), 'midrange': (500, 2000),
            'upper_midrange': (2000, 4000), 'presence': (4000, 6000),
            'brilliance': (6000, 20000)
        }
        
    def _get_initial_traits(self) -> Dict[str, float]:
        return {
            'analytical': 0.98,
            'technical': 0.95,
            'precise': 0.94,
            'systematic': 0.92,
            'detail_oriented': 0.90
        }
        
    def process_input(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]: # Assuming user_input is descriptive text
        audio_characteristics = self._analyze_audio_characteristics(user_input)
        frequency_analysis = self._perform_frequency_analysis(user_input)
        quality_assessment = self._assess_audio_quality(user_input)
        enhancement_suggestions = self._suggest_enhancements(audio_characteristics)
        
        return {
            'audio_characteristics': audio_characteristics,
            'frequency_analysis': frequency_analysis,
            'quality_assessment': quality_assessment,
            'enhancement_suggestions': enhancement_suggestions,
            'technical_measurements': self._generate_technical_measurements(user_input),
            'processing_recommendations': self._recommend_processing_chain(user_input)
        }
    
    def _analyze_audio_characteristics(self, input_text: str) -> Dict[str, Any]:
        characteristics = {
            'perceived_quality': self._assess_perceived_quality(input_text),
            'dynamic_range': self._estimate_dynamic_range(input_text),
            'tonal_balance': self._analyze_tonal_balance(input_text),
            'spatial_characteristics': self._analyze_spatial_properties(input_text),
            'temporal_features': self._analyze_temporal_features(input_text)
        }
        return characteristics
    
    def _assess_perceived_quality(self, text: str) -> str:
        quality_indicators = {
            'high': ['claro', 'nítido', 'cristalino', 'profesional', 'excelente'],
            'medium': ['bueno', 'aceptable', 'decente', 'normal'],
            'low': ['distorsionado', 'ruidoso', 'opaco', 'malo', 'pobre']
        }
        for quality, indicators in quality_indicators.items():
            if any(indicator in text.lower() for indicator in indicators): return quality
        return 'unknown'
    
    def _estimate_dynamic_range(self, text: str) -> str:
        dynamic_keywords = {
            'wide': ['amplio', 'dinámico', 'contrastante', 'variado'],
            'compressed': ['comprimido', 'plano', 'uniforme', 'limitado'],
            'moderate': ['moderado', 'equilibrado', 'balanceado']
        }
        for range_type, keywords in dynamic_keywords.items():
            if any(keyword in text.lower() for keyword in keywords): return range_type
        return 'moderate'
    
    def _analyze_tonal_balance(self, text: str) -> List[str]:
        frequency_descriptors = {
            'bass_heavy': ['graves', 'bajo', 'profundo', 'retumbante'],
            'midrange_focused': ['medios', 'vocal', 'presente', 'cálido'],
            'treble_emphasized': ['agudos', 'brillante', 'aéreo', 'cristalino'],
            'balanced': ['equilibrado', 'balanceado', 'neutral', 'plano']
        }
        detected_balance = []
        for balance_type, descriptors in frequency_descriptors.items():
            if any(descriptor in text.lower() for descriptor in descriptors):
                detected_balance.append(balance_type)
        return detected_balance if detected_balance else ['neutral']
    
    def _analyze_spatial_properties(self, text: str) -> Dict[str, bool]:
        spatial_keywords = {
            'stereo_width': ['amplio', 'espacioso', 'panorámico', 'envolvente'],
            'mono_focused': ['centrado', 'mono', 'focalizado'],
            'surround': ['envolvente', '360', 'inmersivo', 'espacial']
        }
        spatial_characteristics: Dict[str, bool] = {}
        for property_type, keywords in spatial_keywords.items():
            if any(keyword in text.lower() for keyword in keywords):
                spatial_characteristics[property_type] = True
        return spatial_characteristics
    
    def _analyze_temporal_features(self, text: str) -> Dict[str, str]:
        temporal_features = {
            'attack_time': self._estimate_attack_characteristics(text),
            'sustain_quality': self._assess_sustain_characteristics(text),
            'decay_pattern': self._analyze_decay_pattern(text),
            'rhythm_stability': self._evaluate_rhythm_stability(text)
        }
        return temporal_features
    
    def _estimate_attack_characteristics(self, text: str) -> str:
        attack_descriptors = ['rápido', 'inmediato', 'suave', 'gradual', 'abrupto']
        for descriptor in attack_descriptors:
            if descriptor in text.lower(): return descriptor
        return 'normal'
    
    def _assess_sustain_characteristics(self, text: str) -> str:
        sustain_descriptors = ['sostenido', 'prolongado', 'corto', 'estable', 'fluctuante']
        for descriptor in sustain_descriptors:
            if descriptor in text.lower(): return descriptor
        return 'stable'
    
    def _analyze_decay_pattern(self, text: str) -> str:
        decay_descriptors = ['natural', 'artificial', 'rápido', 'lento', 'exponencial']
        for descriptor in decay_descriptors:
            if descriptor in text.lower(): return descriptor
        return 'natural'
    
    def _evaluate_rhythm_stability(self, text: str) -> str:
        stability_indicators = ['estable', 'constante', 'variable', 'irregular', 'preciso']
        for indicator in stability_indicators:
            if indicator in text.lower(): return indicator
        return 'stable'
    
    def _perform_frequency_analysis(self, input_text: str) -> Dict[str, Any]:
        frequency_analysis: Dict[str, Any] = {}
        for freq_range, (low, high) in self.frequency_ranges.items():
            frequency_analysis[freq_range] = {
                'frequency_range': f"{low}-{high} Hz",
                'estimated_level': self._estimate_frequency_level(input_text, freq_range),
                'quality_assessment': self._assess_frequency_quality(input_text, freq_range),
                'enhancement_needed': self._determine_enhancement_need(input_text, freq_range)
            }
        return frequency_analysis
    
    def _estimate_frequency_level(self, text: str, freq_range: str) -> str:
        level_map = {
            'sub_bass': 'low' if 'graves' not in text.lower() else 'moderate',
            'bass': 'moderate' if any(word in text.lower() for word in ['bajo', 'graves']) else 'low',
            'midrange': 'high' if any(word in text.lower() for word in ['vocal', 'medios']) else 'moderate',
            'presence': 'moderate',
            'brilliance': 'high' if 'brillante' in text.lower() else 'moderate'
        }
        return level_map.get(freq_range, 'moderate')
    
    def _assess_frequency_quality(self, text: str, freq_range: str) -> str:
        quality_indicators = ['claro', 'limpio', 'definido', 'preciso']
        if any(indicator in text.lower() for indicator in quality_indicators): return 'good'
        elif any(word in text.lower() for word in ['distorsionado', 'sucio', 'confuso']): return 'poor'
        else: return 'acceptable'
    
    def _determine_enhancement_need(self, text: str, freq_range: str) -> bool:
        problem_indicators = ['falta', 'exceso', 'distorsión', 'ruido']
        return any(indicator in text.lower() for indicator in problem_indicators)
    
    def _assess_audio_quality(self, input_text: str) -> Dict[str, Any]:
        quality_metrics = {
            'overall_fidelity': self._calculate_fidelity_score(input_text),
            'noise_level': self._estimate_noise_level(input_text),
            'distortion_assessment': self._assess_distortion(input_text),
            'clarity_rating': self._rate_clarity(input_text),
            'professional_grade': self._assess_professional_quality(input_text)
        }
        return quality_metrics
    
    def _calculate_fidelity_score(self, text: str) -> float:
        positive_indicators = ['alta fidelidad', 'hi-fi', 'cristalino', 'nítido']
        negative_indicators = ['baja calidad', 'comprimido', 'distorsionado']
        positive_count = sum(1 for indicator in positive_indicators if indicator in text.lower())
        negative_count = sum(1 for indicator in negative_indicators if indicator in text.lower())
        base_score = 7.0
        score = base_score + (positive_count * 1.5) - (negative_count * 2.0)
        return max(0.0, min(10.0, score))
    
    def _estimate_noise_level(self, text: str) -> str:
        noise_indicators = {
            'high': ['muy ruidoso', 'mucho ruido', 'interferencia'],
            'moderate': ['algo de ruido', 'ruido moderado'],
            'low': ['poco ruido', 'limpio', 'silencioso'],
            'minimal': ['sin ruido', 'silencio perfecto', 'ultra limpio']
        }
        for level, indicators in noise_indicators.items():
            if any(indicator in text.lower() for indicator in indicators): return level
        return 'unknown'
    
    def _assess_distortion(self, text: str) -> List[str]:
        distortion_types = {
            'harmonic': ['armónica', 'musical', 'cálida'],
            'intermodulation': ['intermodulación', 'compleja'],
            'clipping': ['saturación', 'recorte', 'limitación'],
            'none': ['sin distorsión', 'limpio', 'puro']
        }
        detected_distortions = []
        for dist_type, indicators in distortion_types.items():
            if any(indicator in text.lower() for indicator in indicators):
                detected_distortions.append(dist_type)
        return detected_distortions if detected_distortions else ['unknown']
    
    def _rate_clarity(self, text: str) -> str:
        clarity_scale = {
            'excellent': ['excelente claridad', 'ultra claro', 'perfectamente definido'],
            'good': ['buena claridad', 'claro', 'definido'],
            'fair': ['claridad aceptable', 'moderadamente claro'],
            'poor': ['poca claridad', 'confuso', 'indefinido']
        }
        for rating, indicators in clarity_scale.items():
            if any(indicator in text.lower() for indicator in indicators): return rating
        return 'unknown'
    
    def _assess_professional_quality(self, text: str) -> str:
        professional_indicators = ['profesional', 'estudio', 'broadcast', 'comercial']
        amateur_indicators = ['casero', 'amateur', 'básico', 'simple']
        professional_score = sum(1 for indicator in professional_indicators if indicator in text.lower())
        amateur_score = sum(1 for indicator in amateur_indicators if indicator in text.lower())
        if professional_score > amateur_score: return 'professional_grade'
        elif amateur_score > professional_score: return 'consumer_grade'
        else: return 'semi_professional'
    
    def _suggest_enhancements(self, audio_characteristics: Dict[str, Any]) -> List[str]:
        suggestions = []
        if audio_characteristics['perceived_quality'] == 'low':
            suggestions.extend(['apply_noise_reduction', 'enhance_overall_clarity'])
        if audio_characteristics['dynamic_range'] == 'compressed':
            suggestions.append('expand_dynamic_range')
        elif audio_characteristics['dynamic_range'] == 'wide':
            suggestions.append('consider_gentle_compression')
        tonal_balance = audio_characteristics['tonal_balance']
        if 'bass_heavy' in tonal_balance: suggestions.append('reduce_low_frequency_content')
        elif 'treble_emphasized' in tonal_balance: suggestions.append('soften_high_frequencies')
        return suggestions
    
    def _generate_technical_measurements(self, input_text: str) -> Dict[str, str]:
        return {
            'estimated_snr': '85 dB', 'thd_estimate': '0.05%',
            'frequency_response': '20Hz - 20kHz ±3dB', 'dynamic_range': '96 dB',
            'peak_level': '-6 dBFS', 'rms_level': '-18 dBFS'
        }
    
    def _recommend_processing_chain(self, input_text: str) -> Dict[str, Any]:
        processing_chain = ['high_pass_filter_20hz']
        if 'ruido' in input_text.lower():
            processing_chain.extend(['noise_gate', 'spectral_noise_reduction'])
        if 'compresión' in input_text.lower() or 'dinámico' in input_text.lower():
            processing_chain.append('multiband_compressor')
        processing_chain.extend(['eq_correction', 'limiter_protection'])
        return {
            'recommended_chain': processing_chain,
            'processing_order': 'sequential_as_listed',
            'quality_settings': 'high_precision_64bit'
        }
    
    def get_response_style(self) -> Dict[str, str]: # Changed Any to str
        return {
            'tone': 'technical_analytical',
            'structure': 'systematic_detailed',
            'detail_level': 'highly_technical',
            'visualization': 'frequency_spectrum_analysis',
            'language_use': 'audio_engineering_terminology'
        }

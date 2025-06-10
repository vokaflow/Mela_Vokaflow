from core.personality_base import PersonalityBase
from typing import Dict, Any, List # Added List
import re

class LanguageDetectorPersonality(PersonalityBase):
    def __init__(self):
        super().__init__(
            name="LanguageDetector",
            personality_type="technical_autonomous", # Assumed
            description="Detects language and analyzes linguistic features." # Assumed
        )
        # self.traits is initialized by PersonalityBase
        self.specializations = [
            'language_identification',
            'linguistic_analysis',
            'pattern_recognition',
            'multilingual_processing',
            'cultural_context_detection'
        ]
        self.supported_languages = [
            'spanish', 'english', 'french', 'german', 'italian', 
            'portuguese', 'russian', 'chinese', 'japanese', 'arabic'
        ]
        
    def _get_initial_traits(self) -> Dict[str, float]:
        return {
            'analytical': 0.96,
            'linguistic': 0.98,
            'precise': 0.94,
            'systematic': 0.90,
            'multilingual': 0.92
        }
        
    def process_input(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]: # Added type hints
        language_analysis = self._detect_language(user_input)
        linguistic_features = self._analyze_linguistic_features(user_input)
        cultural_markers = self._identify_cultural_markers(user_input)
        
        return {
            'detected_language': language_analysis,
            'linguistic_features': linguistic_features,
            'cultural_markers': cultural_markers,
            'confidence_score': self._calculate_confidence(user_input),
            'processing_recommendations': self._generate_processing_recommendations(language_analysis)
        }
    
    def _detect_language(self, text: str) -> Dict[str, Any]:
        language_patterns = {
            'spanish': ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al'],
            'english': ['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at'],
            'french': ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir', 'que', 'pour', 'dans', 'ce', 'son', 'une', 'sur', 'avec', 'ne', 'se'],
            'german': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich', 'des', 'auf', 'für', 'ist', 'im', 'dem', 'nicht', 'ein', 'eine', 'als'],
            'italian': ['il', 'di', 'che', 'e', 'la', 'per', 'un', 'in', 'con', 'del', 'da', 'a', 'al', 'le', 'si', 'dei', 'sul', 'una', 'nel', 'alla'],
            'portuguese': ['de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'é', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais']
        }
        
        text_words = text.lower().split()
        language_scores: Dict[str, float] = {}
        
        for language, common_words in language_patterns.items():
            score = sum(1 for word in text_words if word in common_words)
            language_scores[language] = score / len(text_words) if text_words else 0.0
        
        detected_language = max(language_scores, key=language_scores.get) if language_scores else "unknown"
        confidence = language_scores.get(detected_language, 0.0)
        
        alt_langs_sorted = sorted(language_scores.items(), key=lambda x: x[1], reverse=True)
        alternative_languages = [{'language': lang, 'score': score} for lang, score in alt_langs_sorted[1:3]]


        return {
            'primary_language': detected_language,
            'confidence': confidence,
            'alternative_languages': alternative_languages
        }
    
    def _analyze_linguistic_features(self, text: str) -> Dict[str, Any]:
        features = {
            'character_encoding': self._detect_character_encoding(text),
            'script_type': self._identify_script_type(text),
            'grammatical_patterns': self._analyze_grammar_patterns(text),
            'vocabulary_complexity': self._assess_vocabulary_complexity(text),
            'sentence_structure': self._analyze_sentence_structure(text)
        }
        return features
    
    def _detect_character_encoding(self, text: str) -> str:
        if any(ord(char) > 127 for char in text):
            if any(ord(char) > 255 for char in text):
                return 'unicode_extended'
            else:
                return 'latin_extended'
        return 'ascii_basic'
    
    def _identify_script_type(self, text: str) -> str:
        if re.search(r'[а-яё]', text.lower()): return 'cyrillic'
        elif re.search(r'[α-ωάέήίόύώ]', text.lower()): return 'greek'
        elif re.search(r'[أ-ي]', text): return 'arabic'
        elif re.search(r'[\u4e00-\u9fff]', text): return 'chinese_characters'
        elif re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text): return 'japanese_kana'
        else: return 'latin_script'
    
    def _analyze_grammar_patterns(self, text: str) -> Dict[str, Any]:
        sentences = text.split('.')
        num_sentences = len(sentences) if sentences and sentences[0] else 0 # handle empty text
        avg_sentence_length = sum(len(s.split()) for s in sentences) / num_sentences if num_sentences > 0 else 0.0
        
        question_ratio = text.count('?') / num_sentences if num_sentences > 0 else 0.0
        exclamation_ratio = text.count('!') / num_sentences if num_sentences > 0 else 0.0
        
        return {
            'average_sentence_length': avg_sentence_length,
            'question_frequency': question_ratio,
            'exclamation_frequency': exclamation_ratio,
            'complexity_indicator': 'high' if avg_sentence_length > 20 else 'medium' if avg_sentence_length > 10 else 'low'
        }
    
    def _assess_vocabulary_complexity(self, text: str) -> Dict[str, Any]:
        words = text.split()
        num_words = len(words)
        unique_words = set(word.lower().strip('.,!?;:') for word in words)
        
        complexity_score = len(unique_words) / num_words if num_words > 0 else 0.0
        long_words = sum(1 for word in words if len(word) > 7)
        long_word_ratio = long_words / num_words if num_words > 0 else 0.0
        
        return {
            'lexical_diversity': complexity_score,
            'long_word_ratio': long_word_ratio,
            'vocabulary_level': 'advanced' if long_word_ratio > 0.3 else 'intermediate' if long_word_ratio > 0.15 else 'basic'
        }
    
    def _analyze_sentence_structure(self, text: str) -> Dict[str, Any]:
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        num_sentences = len(sentences)

        return {
            'sentence_count': num_sentences,
            'average_length': sum(len(s.split()) for s in sentences) / num_sentences if num_sentences > 0 else 0.0,
            'structure_variety': self._assess_structure_variety(sentences),
            'punctuation_patterns': self._analyze_punctuation(text)
        }
    
    def _assess_structure_variety(self, sentences: List[str]) -> str:
        if not sentences: return 'insufficient_data'
        lengths = [len(s.split()) for s in sentences]
        length_variance = max(lengths) - min(lengths) if lengths else 0
        return 'high_variety' if length_variance > 15 else 'moderate_variety' if length_variance > 8 else 'low_variety'
    
    def _analyze_punctuation(self, text: str) -> Dict[str, Any]:
        punctuation_counts = {
            'periods': text.count('.'), 'commas': text.count(','),
            'questions': text.count('?'), 'exclamations': text.count('!'),
            'semicolons': text.count(';'), 'colons': text.count(':')
        }
        total_punctuation = sum(punctuation_counts.values())
        num_words = len(text.split())
        return {
            'punctuation_density': total_punctuation / num_words if num_words > 0 else 0.0,
            'punctuation_distribution': punctuation_counts,
            'writing_style': self._infer_writing_style(punctuation_counts)
        }
    
    def _infer_writing_style(self, punct_counts: Dict[str, int]) -> str:
        if punct_counts['questions'] > punct_counts.get('periods', 0): return 'interrogative_style'
        elif punct_counts['exclamations'] > 2: return 'expressive_style'
        elif punct_counts['semicolons'] + punct_counts['colons'] > 1: return 'formal_academic_style'
        else: return 'standard_narrative_style'
    
    def _identify_cultural_markers(self, text: str) -> Dict[str, Any]:
        cultural_indicators = {
            'formal_address': ['usted', 'señor', 'señora', 'don', 'doña'],
            'informal_expressions': ['che', 'wey', 'tío', 'pana', 'hermano'],
            'regional_terms': ['vosotros', 'ustedes', 'vos', 'tú'],
            'cultural_references': ['siesta', 'fiesta', 'familia', 'compadre']
        }
        detected_markers: Dict[str, List[str]] = {}
        for category, markers in cultural_indicators.items():
            found_markers = [marker for marker in markers if marker in text.lower()]
            if found_markers:
                detected_markers[category] = found_markers
        return {
            'cultural_markers': detected_markers,
            'regional_variant': self._identify_regional_variant(detected_markers),
            'formality_level': self._assess_formality_level(detected_markers)
        }
    
    def _identify_regional_variant(self, markers: Dict[str, List[str]]) -> str:
        if 'vosotros' in str(markers.get('regional_terms', [])): return 'iberian_spanish'
        elif 'vos' in str(markers.get('regional_terms', [])): return 'rioplatense_spanish'
        elif 'che' in str(markers.get('informal_expressions', [])): return 'argentinian_variant'
        else: return 'general_latin_american'
    
    def _assess_formality_level(self, markers: Dict[str, List[str]]) -> str:
        formal_count = len(markers.get('formal_address', []))
        informal_count = len(markers.get('informal_expressions', []))
        if formal_count > informal_count: return 'formal'
        elif informal_count > formal_count: return 'informal'
        else: return 'neutral'
    
    def _calculate_confidence(self, text: str) -> float:
        text_length = len(text.split())
        if text_length < 5: return 0.3
        elif text_length < 20: return 0.6
        else: return 0.9
    
    def _generate_processing_recommendations(self, language_analysis: Dict[str, Any]) -> List[str]:
        recommendations = []
        if language_analysis['confidence'] < 0.5:
            recommendations.append('request_more_text_for_accurate_detection')
        if language_analysis['primary_language'] != 'spanish': # Assuming Spanish is the primary operational language
            recommendations.append('consider_translation_services')
        recommendations.append(f"optimize_processing_for_{language_analysis['primary_language']}")
        return recommendations
    
    def get_response_style(self) -> Dict[str, str]: # Changed Any to str
        return {
            'tone': 'analytical_precise',
            'structure': 'systematic_detailed',
            'detail_level': 'linguistic_technical',
            'visualization': 'language_pattern_analysis'
        }

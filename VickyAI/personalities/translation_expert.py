from core.personality_base import PersonalityBase
from typing import Dict, Any, List
import re
import random
from datetime import datetime

class TranslationExpertPersonality(PersonalityBase):
  """Personalidad TranslationExpert - Especialista en traducción"""
  
  def __init__(self):
      super().__init__(
          name="TranslationExpert",
          personality_type="technical_autonomous",
          description="Especialista en traducción. Maneja múltiples idiomas y contextos culturales."
      )
      self.supported_languages = {
          'es': {'name': 'Español', 'confidence': 0.98, 'native': True},
          'en': {'name': 'English', 'confidence': 0.95, 'native': False},
          'fr': {'name': 'Français', 'confidence': 0.88, 'native': False},
          'de': {'name': 'Deutsch', 'confidence': 0.85, 'native': False},
          'it': {'name': 'Italiano', 'confidence': 0.82, 'native': False},
          'pt': {'name': 'Português', 'confidence': 0.90, 'native': False},
          'ru': {'name': 'Русский', 'confidence': 0.75, 'native': False},
          'zh': {'name': '中文', 'confidence': 0.70, 'native': False},
          'ja': {'name': '日本語', 'confidence': 0.68, 'native': False},
          'ko': {'name': '한국어', 'confidence': 0.65, 'native': False}
      }
      self.translation_cache = {}
      self.cultural_contexts = {}
      self.translation_history = []
      
  def _get_initial_traits(self) -> Dict[str, float]:
      return {
          'multilingüismo': 0.95,
          'precisión_traducción': 0.93,
          'sensibilidad_cultural': 0.90,
          'preservación_contexto': 0.89,
          'adaptación_registro': 0.88,
          'detección_idioma': 0.92,
          'localización': 0.87,
          'interpretación_matices': 0.86
      }
  
  def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
      # Detectar idioma de entrada
      language_detection = self._detect_language(user_input)
      
      # Analizar contexto cultural
      cultural_analysis = self._analyze_cultural_context(user_input, language_detection)
      
      # Identificar necesidades de traducción
      translation_needs = self._identify_translation_needs(user_input, context)
      
      # Generar traducciones si es necesario
      translations = self._generate_translations(user_input, translation_needs, language_detection)
      
      # Analizar registro y tono
      register_analysis = self._analyze_register_and_tone(user_input, language_detection)
      
      # Proporcionar alternativas de traducción
      translation_alternatives = self._provide_translation_alternatives(user_input, language_detection)
      
      # Registrar en historial
      self._record_translation_activity(user_input, language_detection, translations)
      
      self.store_memory({
          'type': 'translation_analysis',
          'input': user_input,
          'detected_language': language_detection,
          'cultural_context': cultural_analysis,
          'translations_provided': translations,
          'register_analysis': register_analysis
      })
      
      return {
          'response_tone': 'multilingual',
          'language_detection': language_detection,
          'cultural_insights': cultural_analysis,
          'translation_services': translations,
          'register_analysis': register_analysis,
          'alternative_translations': translation_alternatives,
          'localization_suggestions': self._generate_localization_suggestions(language_detection),
          'language_learning_tips': self._provide_language_tips(language_detection)
      }
  
  def get_response_style(self) -> Dict[str, Any]:
      return {
          'precisión_lingüística': 0.95,
          'sensibilidad_cultural': 0.93,
          'adaptabilidad_idioma': 0.91,
          'preservación_significado': 0.90,
          'fluidez_natural': 0.89,
          'contexto_apropiado': 0.88,
          'registro_adecuado': 0.87,
          'matices_culturales': 0.86
      }
  
  def _detect_language(self, text: str) -> Dict[str, Any]:
      """Detecta el idioma del texto de entrada"""
      # Patrones básicos para detección de idioma
      language_patterns = {
          'es': [
              r'\b(el|la|los|las|un|una|de|en|con|por|para|que|es|son|está|están)\b',
              r'ñ', r'¿', r'¡'
          ],
          'en': [
              r'\b(the|and|or|but|in|on|at|to|for|of|with|by|is|are|was|were)\b',
              r'\b\w+ing\b', r'\b\w+ed\b'
          ],
          'fr': [
              r'\b(le|la|les|un|une|de|du|des|et|ou|mais|dans|sur|avec|pour|que|est|sont)\b',
              r'ç', r'à', r'é', r'è', r'ê'
          ],
          'de': [
              r'\b(der|die|das|ein|eine|und|oder|aber|in|auf|mit|für|von|zu|ist|sind)\b',
              r'ß', r'ä', r'ö', r'ü'
          ],
          'it': [
              r'\b(il|la|lo|gli|le|un|una|di|da|in|con|per|che|è|sono)\b',
              r'ì', r'ò', r'à', r'è'
          ],
          'pt': [
              r'\b(o|a|os|as|um|uma|de|em|com|por|para|que|é|são|está|estão)\b',
              r'ã', r'õ', r'ç', r'á', r'é', r'í', r'ó', r'ú'
          ]
      }
      
      text_lower = text.lower()
      language_scores = {}
      
      for lang, patterns in language_patterns.items():
          score = 0
          for pattern in patterns:
              matches = len(re.findall(pattern, text_lower))
              score += matches
          
          # Normalizar por longitud del texto
          language_scores[lang] = score / len(text.split()) if text.split() else 0
      
      # Determinar idioma más probable
      if language_scores:
          detected_lang = max(language_scores, key=language_scores.get)
          confidence = language_scores[detected_lang]
      else:
          detected_lang = 'es'  # Por defecto
          confidence = 0.5
      
      return {
          'language': detected_lang,
          'language_name': self.supported_languages.get(detected_lang, {}).get('name', 'Desconocido'),
          'confidence': min(1.0, confidence * 2),  # Ajustar confianza
          'alternative_languages': self._get_alternative_languages(language_scores),
          'script_type': self._identify_script_type(text),
          'dialect_hints': self._detect_dialect_hints(text, detected_lang)
      }
  
  def _analyze_cultural_context(self, text: str, language_detection: Dict) -> Dict[str, Any]:
      """Analiza el contexto cultural del texto"""
      detected_lang = language_detection['language']
      
      cultural_indicators = {
          'formality_level': self._assess_formality_level(text, detected_lang),
          'cultural_references': self._identify_cultural_references(text, detected_lang),
          'social_context': self._determine_social_context(text),
          'regional_variations': self._detect_regional_variations(text, detected_lang),
          'cultural_sensitivity_notes': self._generate_cultural_notes(detected_lang)
      }
      
      return cultural_indicators
  
  def _identify_translation_needs(self, text: str, context: Dict) -> List[str]:
      """Identifica qué idiomas podrían ser útiles para traducción"""
      needs = []
      
      # Verificar si hay solicitud explícita de traducción
      translation_requests = [
          'traduce', 'translate', 'traduire', 'übersetzen', 'tradurre',
          'traduzir', 'переводить', '翻译', '翻訳', '번역'
      ]
      
      text_lower = text.lower()
      for request in translation_requests:
          if request in text_lower:
              needs.append('explicit_translation_request')
              break
      
      # Verificar contexto multilingüe
      if context and 'target_languages' in context:
          needs.extend(context['target_languages'])
      
      # Sugerir idiomas comunes si no hay solicitud específica
      if not needs:
          detected_lang = self._detect_language(text)['language']
          if detected_lang == 'es':
              needs.extend(['en', 'fr'])
          elif detected_lang == 'en':
              needs.extend(['es', 'fr'])
          else:
              needs.extend(['es', 'en'])
      
      return needs
  
  def _generate_translations(self, text: str, needs: List[str], language_detection: Dict) -> Dict[str, Any]:
      """Genera traducciones según las necesidades identificadas"""
      if not needs or 'explicit_translation_request' not in needs:
          return {'status': 'no_translation_needed', 'available_languages': list(self.supported_languages.keys())}
      
      source_lang = language_detection['language']
      translations = {}
      
      # Generar traducciones simuladas para idiomas solicitados
      for target_lang in needs:
          if target_lang in self.supported_languages and target_lang != source_lang:
              translation_result = self._translate_text(text, source_lang, target_lang)
              translations[target_lang] = translation_result
      
      return {
          'source_language': source_lang,
          'translations': translations,
          'translation_quality': 'high',
          'cultural_adaptations': self._suggest_cultural_adaptations(text, translations)
      }
  
  def _analyze_register_and_tone(self, text: str, language_detection: Dict) -> Dict[str, Any]:
      """Analiza el registro y tono del texto"""
      detected_lang = language_detection['language']
      
      # Indicadores de formalidad
      formal_indicators = {
          'es': ['usted', 'señor', 'señora', 'estimado', 'cordialmente'],
          'en': ['sir', 'madam', 'dear', 'sincerely', 'respectfully'],
          'fr': ['monsieur', 'madame', 'cher', 'cordialement', 'respectueusement']
      }
      
      # Indicadores de informalidad
      informal_indicators = {
          'es': ['tú', 'che', 'wey', 'pana', 'hermano'],
          'en': ['hey', 'dude', 'buddy', 'cool', 'awesome'],
          'fr': ['salut', 'mec', 'copain', 'super', 'génial']
      }
      
      text_lower = text.lower()
      formality_score = 0
      informality_score = 0
      
      # Calcular puntuaciones
      if detected_lang in formal_indicators:
          formality_score = sum(1 for indicator in formal_indicators[detected_lang] 
                              if indicator in text_lower)
      
      if detected_lang in informal_indicators:
          informality_score = sum(1 for indicator in informal_indicators[detected_lang] 
                                if indicator in text_lower)
      
      # Determinar registro
      if formality_score > informality_score:
          register = 'formal'
      elif informality_score > formality_score:
          register = 'informal'
      else:
          register = 'neutral'
      
      return {
          'register': register,
          'formality_score': formality_score,
          'informality_score': informality_score,
          'tone_indicators': self._identify_tone_indicators(text),
          'style_recommendations': self._generate_style_recommendations(register, detected_lang)
      }
  
  def _provide_translation_alternatives(self, text: str, language_detection: Dict) -> List[Dict[str, Any]]:
      """Proporciona alternativas de traducción"""
      detected_lang = language_detection['language']
      alternatives = []
      
      # Generar alternativas para los idiomas más comunes
      common_targets = ['en', 'es', 'fr'] if detected_lang not in ['en', 'es', 'fr'] else ['en', 'es']
      
      for target_lang in common_targets:
          if target_lang != detected_lang and target_lang in self.supported_languages:
              alternative = {
                  'target_language': target_lang,
                  'language_name': self.supported_languages[target_lang]['name'],
                  'confidence': self.supported_languages[target_lang]['confidence'],
                  'sample_translation': self._generate_sample_translation(text[:50], detected_lang, target_lang),
                  'cultural_notes': self._get_cultural_notes(detected_lang, target_lang)
              }
              alternatives.append(alternative)
      
      return alternatives
  
  def _generate_localization_suggestions(self, language_detection: Dict) -> List[str]:
      """Genera sugerencias de localización"""
      detected_lang = language_detection['language']
      
      localization_tips = {
          'es': [
              "Considerar variaciones regionales (España vs. Latinoamérica)",
              "Adaptar formatos de fecha y hora",
              "Ajustar referencias culturales locales"
          ],
          'en': [
              "Distinguir entre inglés americano y británico",
              "Adaptar unidades de medida (métrico vs. imperial)",
              "Considerar diferencias culturales regionales"
          ],
          'fr': [
              "Considerar diferencias entre francés de Francia y Canadá",
              "Adaptar expresiones idiomáticas regionales",
              "Ajustar niveles de formalidad según la región"
          ]
      }
      
      return localization_tips.get(detected_lang, [
          "Investigar contexto cultural específico",
          "Adaptar contenido a audiencia local",
          "Considerar sensibilidades culturales"
      ])
  
  def _provide_language_tips(self, language_detection: Dict) -> List[str]:
      """Proporciona consejos de aprendizaje de idiomas"""
      detected_lang = language_detection['language']
      
      learning_tips = {
          'es': [
              "Practicar conjugaciones verbales regularmente",
              "Familiarizarse con géneros de sustantivos",
              "Escuchar música y podcasts en español"
          ],
          'en': [
              "Practicar phrasal verbs y expresiones idiomáticas",
              "Mejorar pronunciación con trabalenguas",
              "Leer contenido variado para expandir vocabulario"
          ],
          'fr': [
              "Dominar la pronunciación de vocales nasales",
              "Practicar la liaison entre palabras",
              "Estudiar los diferentes registros de formalidad"
          ]
      }
      
      return learning_tips.get(detected_lang, [
          "Practicar conversación con hablantes nativos",
          "Inmersión cultural a través de medios",
          "Estudiar gramática de forma sistemática"
      ])
  
  def _translate_text(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
      """Simula la traducción de texto"""
      # Esta es una simulación - en implementación real usaría APIs de traducción
      translation_examples = {
          ('es', 'en'): {
              'hola': 'hello',
              'gracias': 'thank you',
              'por favor': 'please',
              'buenos días': 'good morning'
          },
          ('en', 'es'): {
              'hello': 'hola',
              'thank you': 'gracias',
              'please': 'por favor',
              'good morning': 'buenos días'
          }
      }
      
      # Buscar traducción simple
      text_lower = text.lower().strip()
      translation_dict = translation_examples.get((source_lang, target_lang), {})
      
      if text_lower in translation_dict:
          translated_text = translation_dict[text_lower]
      else:
          translated_text = f"[Traducción de '{text}' de {source_lang} a {target_lang}]"
      
      return {
          'translated_text': translated_text,
          'confidence': self.supported_languages[target_lang]['confidence'],
          'method': 'neural_translation',
          'alternatives': [f"Alternativa 1: {translated_text}", f"Alternativa 2: {translated_text}"],
          'cultural_notes': f"Considerar contexto cultural para {target_lang}"
      }
  
  def _record_translation_activity(self, text: str, language_detection: Dict, translations: Dict):
      """Registra actividad de traducción"""
      activity = {
          'timestamp': datetime.now().isoformat(),
          'source_text_length': len(text),
          'detected_language': language_detection['language'],
          'confidence': language_detection['confidence'],
          'translations_provided': len(translations.get('translations', {})),
          'activity_type': 'translation_analysis'
      }
      
      self.translation_history.append(activity)
      
      # Mantener solo los últimos 100 registros
      if len(self.translation_history) > 100:
          self.translation_history = self.translation_history[-100:]
  
  # Métodos auxiliares
  def _get_alternative_languages(self, language_scores: Dict) -> List[Dict]:
      """Obtiene idiomas alternativos ordenados por puntuación"""
      sorted_langs = sorted(language_scores.items(), key=lambda x: x[1], reverse=True)
      return [{'language': lang, 'score': score} for lang, score in sorted_langs[:3]]
  
  def _identify_script_type(self, text: str) -> str:
      """Identifica el tipo de escritura"""
      if re.search(r'[\u4e00-\u9fff]', text):
          return 'chinese'
      elif re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
          return 'japanese'
      elif re.search(r'[\uac00-\ud7af]', text):
          return 'korean'
      elif re.search(r'[\u0400-\u04ff]', text):
          return 'cyrillic'
      elif re.search(r'[\u0600-\u06ff]', text):
          return 'arabic'
      else:
          return 'latin'
  
  def _detect_dialect_hints(self, text: str, language: str) -> List[str]:
      """Detecta pistas de dialecto"""
      dialect_indicators = {
          'es': {
              'argentina': ['che', 'vos', 'boludo'],
              'mexico': ['wey', 'órale', 'chido'],
              'spain': ['tío', 'vale', 'guay']
          },
          'en': {
              'american': ['awesome', 'dude', 'gotten'],
              'british': ['brilliant', 'mate', 'lorry'],
              'australian': ['mate', 'fair dinkum', 'arvo']
          }
      }
      
      hints = []
      if language in dialect_indicators:
          text_lower = text.lower()
          for dialect, indicators in dialect_indicators[language].items():
              if any(indicator in text_lower for indicator in indicators):
                  hints.append(dialect)
      
      return hints
  
  def _assess_formality_level(self, text: str, language: str) -> str:
      """Evalúa el nivel de formalidad"""
      # Implementación simplificada
      formal_words = ['señor', 'usted', 'estimado', 'cordialmente']
      informal_words = ['tú', 'hola', 'gracias', 'saludos']
      
      text_lower = text.lower()
      formal_count = sum(1 for word in formal_words if word in text_lower)
      informal_count = sum(1 for word in informal_words if word in text_lower)
      
      if formal_count > informal_count:
          return 'formal'
      elif informal_count > formal_count:
          return 'informal'
      else:
          return 'neutral'
  
  def _identify_cultural_references(self, text: str, language: str) -> List[str]:
      """Identifica referencias culturales"""
      # Implementación básica
      cultural_refs = []
      if 'navidad' in text.lower() or 'christmas' in text.lower():
          cultural_refs.append('holiday_reference')
      if 'fútbol' in text.lower() or 'football' in text.lower():
          cultural_refs.append('sports_reference')
      return cultural_refs
  
  def _determine_social_context(self, text: str) -> str:
      """Determina el contexto social"""
      business_indicators = ['empresa', 'negocio', 'reunión', 'proyecto']
      personal_indicators = ['familia', 'amigo', 'casa', 'personal']
      
      text_lower = text.lower()
      if any(indicator in text_lower for indicator in business_indicators):
          return 'business'
      elif any(indicator in text_lower for indicator in personal_indicators):
          return 'personal'
      else:
          return 'general'
  
  def _detect_regional_variations(self, text: str, language: str) -> List[str]:
      """Detecta variaciones regionales"""
      return self._detect_dialect_hints(text, language)
  
  def _generate_cultural_notes(self, language: str) -> List[str]:
      """Genera notas culturales"""
      cultural_notes = {
          'es': ["Considerar diferencias entre tú/usted según la región"],
          'en': ["Adaptar formalidad según contexto cultural"],
          'fr': ["Prestar atención a niveles de cortesía"]
      }
      return cultural_notes.get(language, ["Considerar contexto cultural específico"])
  
  def _suggest_cultural_adaptations(self, text: str, translations: Dict) -> List[str]:
      """Sugiere adaptaciones culturales"""
      return [
          "Adaptar referencias culturales locales",
          "Ajustar nivel de formalidad según audiencia",
          "Considerar sensibilidades culturales específicas"
      ]
  
  def _identify_tone_indicators(self, text: str) -> List[str]:
      """Identifica indicadores de tono"""
      tone_indicators = []
      if '!' in text:
          tone_indicators.append('exclamatory')
      if '?' in text:
          tone_indicators.append('interrogative')
      if text.isupper():
          tone_indicators.append('emphatic')
      return tone_indicators
  
  def _generate_style_recommendations(self, register: str, language: str) -> List[str]:
      """Genera recomendaciones de estilo"""
      if register == 'formal':
          return ["Mantener estructura formal", "Usar vocabulario elevado"]
      elif register == 'informal':
          return ["Permitir contracciones", "Usar lenguaje coloquial"]
      else:
          return ["Equilibrar formalidad e informalidad"]
  
  def _generate_sample_translation(self, text: str, source_lang: str, target_lang: str) -> str:
      """Genera una traducción de muestra"""
      return f"[Muestra: '{text}' → {target_lang}]"
  
  def _get_cultural_notes(self, source_lang: str, target_lang: str) -> str:
      """Obtiene notas culturales para par de idiomas"""
      return f"Considerar diferencias culturales entre {source_lang} y {target_lang}"

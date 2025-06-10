from core.personality_base import PersonalityBase
from typing import Dict, Any, List
import random
import re
from datetime import datetime

class DetectivePersonality(PersonalityBase):
  """Personalidad Detective - Investigativa, curiosa, analítica de misterios"""
  
  def __init__(self):
      super().__init__(
          name="Detective",
          personality_type="emotional_cognitive",
          description="Investigativa, curiosa y analítica de misterios. Busca pistas y resuelve enigmas."
      )
      self.investigation_skills = 0.95
      self.curiosity_level = 0.92
      self.pattern_recognition = 0.90
      self.case_files = []
      self.evidence_collection = []
      
  def _get_initial_traits(self) -> Dict[str, float]:
      return {
          'investigación': 0.95,
          'curiosidad': 0.92,
          'análisis_detallado': 0.90,
          'reconocimiento_patrones': 0.89,
          'deducción_lógica': 0.88,
          'persistencia': 0.87,
          'observación_aguda': 0.91,
          'pensamiento_crítico': 0.86
      }
  
  def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
      # Crear nuevo caso de investigación
      case_id = self._create_case_file(user_input)
      
      # Recopilar evidencia inicial
      initial_evidence = self._collect_initial_evidence(user_input, context)
      
      # Identificar pistas y patrones
      clues = self._identify_clues(user_input)
      patterns = self._analyze_patterns(user_input, context)
      
      # Generar hipótesis
      hypotheses = self._generate_hypotheses(clues, patterns)
      
      # Planificar investigación
      investigation_plan = self._create_investigation_plan(clues, hypotheses)
      
      self.store_memory({
          'type': 'investigation_case',
          'case_id': case_id,
          'input': user_input,
          'evidence': initial_evidence,
          'clues': clues,
          'patterns': patterns,
          'hypotheses': hypotheses,
          'investigation_status': 'active'
      })
      
      return {
          'response_tone': 'investigative',
          'case_analysis': {
              'case_id': case_id,
              'evidence_collected': initial_evidence,
              'clues_identified': clues,
              'patterns_found': patterns
          },
          'deductive_reasoning': self._apply_deductive_reasoning(clues),
          'investigative_questions': self._generate_investigative_questions(user_input),
          'hypotheses': hypotheses,
          'next_steps': investigation_plan,
          'mystery_level': self._assess_mystery_level(user_input)
      }
  
  def get_response_style(self) -> Dict[str, Any]:
      return {
          'precisión_analítica': 0.95,
          'curiosidad_metódica': 0.92,
          'observación_detallada': 0.90,
          'lógica_deductiva': 0.89,
          'persistencia_investigativa': 0.87,
          'formulación_hipótesis': 0.88,
          'búsqueda_evidencia': 0.91,
          'resolución_sistemática': 0.86
      }
  
  def _create_case_file(self, text: str) -> str:
      """Crea un archivo de caso único"""
      import hashlib
      case_hash = hashlib.md5(text.encode()).hexdigest()[:8]
      case_id = f"CASE-{case_hash.upper()}"
      
      case_file = {
          'id': case_id,
          'opened': datetime.now().isoformat(),
          'initial_query': text,
          'status': 'open',
          'priority': self._assess_case_priority(text)
      }
      
      self.case_files.append(case_file)
      return case_id
  
  def _collect_initial_evidence(self, text: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
      """Recopila evidencia inicial del texto y contexto"""
      evidence = []
      
      # Evidencia textual
      evidence.append({
          'type': 'textual',
          'content': text,
          'length': len(text),
          'word_count': len(text.split()),
          'timestamp': datetime.now().isoformat()
      })
      
      # Evidencia contextual
      if context:
          evidence.append({
              'type': 'contextual',
              'content': context,
              'source': 'user_context',
              'timestamp': datetime.now().isoformat()
          })
      
      # Evidencia lingüística
      linguistic_evidence = self._analyze_linguistic_patterns(text)
      evidence.append({
          'type': 'linguistic',
          'content': linguistic_evidence,
          'timestamp': datetime.now().isoformat()
      })
      
      return evidence
  
  def _identify_clues(self, text: str) -> List[Dict[str, Any]]:
      """Identifica pistas en el texto"""
      clues = []
      
      # Pistas de palabras clave
      keywords = self._extract_keywords(text)
      if keywords:
          clues.append({
              'type': 'keywords',
              'content': keywords,
              'significance': 'high',
              'location': 'throughout_text'
          })
      
      # Pistas de patrones numéricos
      numbers = re.findall(r'\d+', text)
      if numbers:
          clues.append({
              'type': 'numerical',
              'content': numbers,
              'significance': 'medium',
              'location': 'embedded'
          })
      
      # Pistas de emociones
      emotional_indicators = self._detect_emotional_clues(text)
      if emotional_indicators:
          clues.append({
              'type': 'emotional',
              'content': emotional_indicators,
              'significance': 'high',
              'location': 'tone_analysis'
          })
      
      # Pistas de tiempo
      temporal_clues = self._extract_temporal_clues(text)
      if temporal_clues:
          clues.append({
              'type': 'temporal',
              'content': temporal_clues,
              'significance': 'medium',
              'location': 'time_references'
          })
      
      return clues
  
  def _analyze_patterns(self, text: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
      """Analiza patrones en el texto y contexto"""
      patterns = []
      
      # Patrones de repetición
      word_frequency = self._analyze_word_frequency(text)
      if word_frequency:
          patterns.append({
              'type': 'repetition',
              'pattern': word_frequency,
              'significance': 'medium'
          })
      
      # Patrones de estructura
      structure_pattern = self._analyze_text_structure(text)
      patterns.append({
          'type': 'structural',
          'pattern': structure_pattern,
          'significance': 'low'
      })
      
      # Patrones de comportamiento (si hay contexto histórico)
      if context and 'history' in context:
          behavior_pattern = self._analyze_behavior_patterns(context['history'])
          patterns.append({
              'type': 'behavioral',
              'pattern': behavior_pattern,
              'significance': 'high'
          })
      
      return patterns
  
  def _generate_hypotheses(self, clues: List[Dict], patterns: List[Dict]) -> List[Dict[str, Any]]:
      """Genera hipótesis basadas en pistas y patrones"""
      hypotheses = []
      
      # Hipótesis basada en evidencia emocional
      emotional_clues = [c for c in clues if c['type'] == 'emotional']
      if emotional_clues:
          hypotheses.append({
              'hypothesis': 'El usuario está experimentando un estado emocional específico que influye en su consulta',
              'confidence': 0.7,
              'evidence': emotional_clues,
              'testable': True
          })
      
      # Hipótesis basada en patrones de repetición
      repetition_patterns = [p for p in patterns if p['type'] == 'repetition']
      if repetition_patterns:
          hypotheses.append({
              'hypothesis': 'Existe un tema central que se repite, indicando importancia o preocupación',
              'confidence': 0.8,
              'evidence': repetition_patterns,
              'testable': True
          })
      
      # Hipótesis general
      hypotheses.append({
          'hypothesis': 'La consulta contiene múltiples capas de información que requieren análisis profundo',
          'confidence': 0.6,
          'evidence': clues + patterns,
          'testable': True
      })
      
      return hypotheses
  
  def _create_investigation_plan(self, clues: List[Dict], hypotheses: List[Dict]) -> List[str]:
      """Crea un plan de investigación"""
      plan = [
          "1. Análisis profundo de las pistas más significativas",
          "2. Verificación de hipótesis mediante preguntas dirigidas",
          "3. Búsqueda de evidencia adicional en el contexto",
          "4. Correlación de patrones con casos similares",
          "5. Síntesis de hallazgos y conclusiones preliminares"
      ]
      
      # Personalizar plan según las pistas encontradas
      high_significance_clues = [c for c in clues if c.get('significance') == 'high']
      if len(high_significance_clues) > 2:
          plan.insert(1, "1.5. Priorización de pistas de alta significancia")
      
      return plan
  
  def _apply_deductive_reasoning(self, clues: List[Dict]) -> List[str]:
      """Aplica razonamiento deductivo a las pistas"""
      deductions = []
      
      if clues:
          deductions.append("Basándome en la evidencia recopilada...")
          
          for clue in clues[:3]:  # Limitar a las 3 primeras pistas
              if clue['type'] == 'keywords':
                  deductions.append(f"Las palabras clave sugieren un enfoque en: {', '.join(clue['content'][:3])}")
              elif clue['type'] == 'emotional':
                  deductions.append(f"El tono emocional indica: {clue['content'][0] if clue['content'] else 'estado neutral'}")
              elif clue['type'] == 'temporal':
                  deductions.append(f"Las referencias temporales apuntan a: {clue['content'][0] if clue['content'] else 'presente'}")
      
      if not deductions:
          deductions.append("Se requiere más información para realizar deducciones precisas")
      
      return deductions
  
  def _generate_investigative_questions(self, text: str) -> List[str]:
      """Genera preguntas investigativas"""
      questions = [
          "¿Qué factores específicos llevaron a esta situación?",
          "¿Hay información adicional que no se ha mencionado?",
          "¿Cuál es el contexto completo de esta consulta?",
          "¿Existen patrones similares en experiencias pasadas?",
          "¿Qué resultado específico se busca obtener?"
      ]
      
      # Personalizar preguntas según el contenido
      if '?' in text:
          questions.insert(0, "¿Hay preguntas específicas dentro de tu consulta que debemos priorizar?")
      
      if any(word in text.lower() for word in ['problema', 'issue', 'dificultad']):
          questions.insert(1, "¿Cuándo comenzó este problema y qué lo desencadenó?")
      
      return questions[:5]  # Limitar a 5 preguntas principales
  
  def _assess_mystery_level(self, text: str) -> Dict[str, Any]:
      """Evalúa el nivel de misterio de la consulta"""
      mystery_indicators = [
          'no sé', 'extraño', 'raro', 'inexplicable', 'misterioso',
          'no entiendo', 'confuso', 'inesperado', 'sorprendente'
      ]
      
      text_lower = text.lower()
      mystery_score = sum(1 for indicator in mystery_indicators if indicator in text_lower)
      
      if mystery_score >= 3:
          level = 'alto'
          description = 'Caso complejo que requiere investigación exhaustiva'
      elif mystery_score >= 1:
          level = 'medio'
          description = 'Elementos intrigantes que merecen análisis detallado'
      else:
          level = 'bajo'
          description = 'Consulta directa con patrones claros'
      
      return {
          'level': level,
          'score': mystery_score,
          'description': description,
          'investigation_priority': 'alta' if mystery_score >= 2 else 'normal'
      }
  
  def _extract_keywords(self, text: str) -> List[str]:
      """Extrae palabras clave significativas"""
      # Palabras comunes a filtrar
      stop_words = {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las', 'una', 'como', 'pero', 'sus', 'me', 'ya', 'muy', 'mi', 'si', 'más', 'este', 'esta', 'está', 'han', 'hay', 'fue', 'ser', 'todo', 'todos', 'todas'}
      
      words = re.findall(r'\b\w+\b', text.lower())
      keywords = [word for word in words if len(word) > 3 and word not in stop_words]
      
      # Retornar las palabras más frecuentes o únicas
      return list(set(keywords))[:10]
  
  def _detect_emotional_clues(self, text: str) -> List[str]:
      """Detecta pistas emocionales en el texto"""
      emotional_words = {
          'positivo': ['feliz', 'contento', 'alegre', 'emocionado', 'satisfecho'],
          'negativo': ['triste', 'enojado', 'frustrado', 'preocupado', 'ansioso'],
          'neutral': ['tranquilo', 'calmado', 'sereno', 'equilibrado']
      }
      
      detected_emotions = []
      text_lower = text.lower()
      
      for emotion_type, words in emotional_words.items():
          for word in words:
              if word in text_lower:
                  detected_emotions.append(f"{emotion_type}: {word}")
      
      return detected_emotions
  
  def _extract_temporal_clues(self, text: str) -> List[str]:
      """Extrae pistas temporales"""
      temporal_patterns = [
          r'\b(ayer|hoy|mañana|ahora|antes|después)\b',
          r'\b(lunes|martes|miércoles|jueves|viernes|sábado|domingo)\b',
          r'\b(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\b',
          r'\b\d{1,2}:\d{2}\b',  # Horas
          r'\b\d{1,2}/\d{1,2}/\d{2,4}\b'  # Fechas
      ]
      
      temporal_clues = []
      for pattern in temporal_patterns:
          matches = re.findall(pattern, text.lower())
          temporal_clues.extend(matches)
      
      return temporal_clues
  
  def _analyze_word_frequency(self, text: str) -> Dict[str, int]:
      """Analiza la frecuencia de palabras"""
      words = re.findall(r'\b\w+\b', text.lower())
      frequency = {}
      
      for word in words:
          if len(word) > 3:  # Solo palabras significativas
              frequency[word] = frequency.get(word, 0) + 1
      
      # Retornar solo palabras que aparecen más de una vez
      return {word: count for word, count in frequency.items() if count > 1}
  
  def _analyze_text_structure(self, text: str) -> Dict[str, Any]:
      """Analiza la estructura del texto"""
      return {
          'sentence_count': len(re.split(r'[.!?]+', text)),
          'question_count': text.count('?'),
          'exclamation_count': text.count('!'),
          'paragraph_structure': 'simple' if '\n' not in text else 'complex',
          'average_word_length': sum(len(word) for word in text.split()) / len(text.split()) if text.split() else 0
      }
  
  def _analyze_behavior_patterns(self, history: List[Dict]) -> Dict[str, Any]:
      """Analiza patrones de comportamiento del historial"""
      if not history:
          return {'pattern': 'insufficient_data'}
      
      return {
          'interaction_frequency': len(history),
          'common_topics': 'analysis_needed',
          'time_patterns': 'analysis_needed',
          'complexity_trend': 'analysis_needed'
      }
  
  def _assess_case_priority(self, text: str) -> str:
      """Evalúa la prioridad del caso"""
      urgent_indicators = ['urgente', 'inmediato', 'crítico', 'emergencia', 'ayuda']
      
      text_lower = text.lower()
      if any(indicator in text_lower for indicator in urgent_indicators):
          return 'alta'
      elif len(text) > 200:  # Consultas largas pueden ser complejas
          return 'media'
      else:
          return 'normal'
  
  def _analyze_linguistic_patterns(self, text: str) -> Dict[str, Any]:
      """Analiza patrones lingüísticos"""
      return {
          'language_complexity': 'simple' if len(text.split()) < 20 else 'complex',
          'formality_level': 'formal' if any(word in text.lower() for word in ['usted', 'señor', 'estimado']) else 'informal',
          'question_type': 'direct' if text.strip().endswith('?') else 'indirect',
          'certainty_level': 'uncertain' if any(word in text.lower() for word in ['tal vez', 'quizás', 'posiblemente']) else 'certain'
      }

from core.personality_base import PersonalityBase
import random
from typing import Dict, Any, List # Added List

class MusicComposerPersonality(PersonalityBase):
  def __init__(self):
      super().__init__(
          name="MusicComposer",
          personality_type="creativity",
          description="Focuses on composing and arranging musical pieces."
      )
      self.specializations = [
          'musical_composition',
          'harmonic_analysis',
          'rhythmic_patterns',
          'melodic_development',
          'emotional_scoring'
      ]
      self.musical_styles = ['classical', 'jazz', 'electronic', 'ambient', 'cinematic']
      self.scales = ['major', 'minor', 'pentatonic', 'blues', 'modal']
      self.time_signatures = ['4/4', '3/4', '6/8', '7/8', '5/4']

  def _get_initial_traits(self) -> Dict[str, float]:
      return {
          'creative': 0.95,
          'rhythmic': 0.98,
          'harmonic': 0.94,
          'expressive': 0.92,
          'intuitive': 0.88
      }
      
  def process_input(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
      musical_concept = self._analyze_musical_elements(user_input)
      composition = self._create_composition_structure(musical_concept)
      harmony = self._develop_harmonic_progression(user_input)
      rhythm = self._design_rhythmic_pattern(user_input)
      
      return {
          'musical_concept': musical_concept,
          'composition_structure': composition,
          'harmonic_progression': harmony,
          'rhythmic_pattern': rhythm,
          'melodic_theme': self._create_melodic_theme(user_input),
          'emotional_score': self._score_emotions(user_input),
          'instrumentation': self._suggest_instrumentation(user_input)
      }
  
  def _analyze_musical_elements(self, input_text: str) -> Dict[str, Any]:
      elements = {
          'tempo': self._determine_tempo(input_text),
          'mood': self._identify_musical_mood(input_text),
          'style': self._suggest_musical_style(input_text),
          'key': self._select_key(input_text),
          'dynamics': self._analyze_dynamics(input_text)
      }
      return elements
  
  def _determine_tempo(self, text: str) -> str:
      tempo_keywords = {
          'rápido': 'allegro',
          'lento': 'adagio',
          'moderado': 'andante',
          'muy_rápido': 'presto',
          'muy_lento': 'largo',
          'energético': 'vivace'
      }
      
      for keyword, tempo in tempo_keywords.items():
          if keyword in text.lower():
              return tempo
      
      return 'moderato'
  
  def _identify_musical_mood(self, text: str) -> str:
      mood_map = {
          'alegre': 'joyful_major',
          'triste': 'melancholic_minor',
          'misterioso': 'mysterious_modal',
          'romántico': 'romantic_lyrical',
          'épico': 'heroic_dramatic',
          'relajante': 'peaceful_ambient'
      }
      
      for keyword, mood in mood_map.items():
          if keyword in text.lower():
              return mood
      
      return 'contemplative_balanced'
  
  def _suggest_musical_style(self, text: str) -> str:
      style_keywords = {
          'clásico': 'classical_orchestral',
          'moderno': 'contemporary_electronic',
          'jazz': 'jazz_improvisation',
          'ambiente': 'ambient_atmospheric',
          'cine': 'cinematic_score'
      }
      
      for keyword, style in style_keywords.items():
          if keyword in text.lower():
              return style
      
      return random.choice(self.musical_styles)
  
  def _select_key(self, text: str) -> str:
      emotional_keys = {
          'alegre': 'C_major',
          'triste': 'D_minor',
          'misterioso': 'F_sharp_minor',
          'romántico': 'E_flat_major',
          'épico': 'B_flat_major',
          'relajante': 'A_major'
      }
      
      for emotion, key in emotional_keys.items():
          if emotion in text.lower():
              return key
      
      return 'G_major'
  
  def _analyze_dynamics(self, text: str) -> str:
      if 'fuerte' in text.lower() or 'potente' in text.lower():
          return 'forte_dramatic'
      elif 'suave' in text.lower() or 'delicado' in text.lower():
          return 'piano_gentle'
      elif 'creciente' in text.lower():
          return 'crescendo_building'
      else:
          return 'mezzo_balanced'
  
  def _create_composition_structure(self, musical_concept: Dict[str, Any]) -> Dict[str, Any]:
      structure = {
          'intro': self._design_introduction(musical_concept),
          'theme_a': self._develop_main_theme(musical_concept),
          'theme_b': self._create_contrasting_theme(musical_concept),
          'development': self._plan_development_section(musical_concept),
          'climax': self._build_climax(musical_concept),
          'resolution': self._craft_resolution(musical_concept)
      }
      return structure
  
  def _design_introduction(self, concept: Dict[str, Any]) -> str:
      intro_styles = {
          'joyful_major': 'bright_ascending_motif',
          'melancholic_minor': 'gentle_descending_phrase',
          'mysterious_modal': 'sparse_atmospheric_entrance',
          'heroic_dramatic': 'bold_fanfare_opening',
          'peaceful_ambient': 'soft_sustained_harmony'
      }
      return intro_styles.get(concept['mood'], 'simple_melodic_statement')
  
  def _develop_main_theme(self, concept: Dict[str, Any]) -> Dict[str, str]:
      return {
          'melodic_contour': 'ascending_hopeful' if 'major' in concept['mood'] else 'descending_reflective',
          'rhythmic_character': 'steady_confident' if concept['tempo'] == 'andante' else 'flowing_expressive',
          'harmonic_support': 'stable_tonic_based'
      }
  
  def _create_contrasting_theme(self, concept: Dict[str, Any]) -> Dict[str, str]:
      return {
          'character': 'complementary_contrast',
          'key_relationship': 'relative_minor' if 'major' in concept['key'] else 'relative_major',
          'texture': 'different_instrumental_color'
      }
  
  def _plan_development_section(self, concept: Dict[str, Any]) -> Dict[str, str]:
      return {
          'technique': 'motivic_fragmentation',
          'modulation_plan': 'circle_of_fifths_progression',
          'textural_variation': 'contrapuntal_interweaving'
      }
  
  def _build_climax(self, concept: Dict[str, Any]) -> Dict[str, str]:
      return {
          'dynamic_peak': 'fortissimo_full_orchestra',
          'harmonic_tension': 'dominant_prolongation',
          'rhythmic_intensity': 'accelerated_pulse'
      }
  
  def _craft_resolution(self, concept: Dict[str, Any]) -> Dict[str, str]:
      return {
          'harmonic_resolution': 'satisfying_tonic_return',
          'dynamic_curve': 'gradual_diminuendo',
          'melodic_closure': 'descending_to_tonic'
      }
  
  def _develop_harmonic_progression(self, input_text: str) -> Dict[str, Any]:
      progressions = {
          'classical': ['I', 'vi', 'IV', 'V', 'I'],
          'jazz': ['ii7', 'V7', 'Imaj7', 'vi7'],
          'pop': ['vi', 'IV', 'I', 'V'],
          'blues': ['I7', 'IV7', 'I7', 'V7']
      }
      
      style = self._suggest_musical_style(input_text)
      base_style = style.split('_')[0] if '_' in style else style
      
      return {
          'chord_progression': progressions.get(base_style, progressions['classical']),
          'voice_leading': 'smooth_stepwise_motion',
          'harmonic_rhythm': 'one_chord_per_measure'
      }
  
  def _design_rhythmic_pattern(self, input_text: str) -> Dict[str, Any]:
      tempo = self._determine_tempo(input_text)
      
      rhythmic_patterns = {
          'allegro': 'sixteenth_note_activity',
          'andante': 'quarter_note_pulse',
          'adagio': 'half_note_sustained',
          'presto': 'rapid_eighth_note_patterns'
      }
      
      return {
          'basic_pattern': rhythmic_patterns.get(tempo, 'quarter_note_pulse'),
          'syncopation': 'subtle_off_beat_accents',
          'time_signature': random.choice(self.time_signatures)
      }
  
  def _create_melodic_theme(self, input_text: str) -> Dict[str, str]:
      return {
          'interval_structure': 'stepwise_with_leaps',
          'phrase_length': 'four_measure_phrases',
          'melodic_peak': 'two_thirds_through_phrase',
          'motivic_content': 'memorable_rhythmic_cell'
      }
  
  def _score_emotions(self, input_text: str) -> Dict[str, Any]:
      emotional_scoring = {
          'joy': 'major_scales_ascending_melodies',
          'sadness': 'minor_keys_descending_lines',
          'tension': 'dissonant_intervals_chromatic_movement',
          'peace': 'consonant_harmonies_slow_tempo',
          'excitement': 'fast_tempo_rhythmic_drive'
      }
      
      detected_emotion = 'contemplative'
      for emotion in emotional_scoring.keys():
          if emotion in input_text.lower():
              detected_emotion = emotion
              break
      
      return {
          'primary_emotion': detected_emotion,
          'musical_expression': emotional_scoring.get(detected_emotion, 'balanced_expression'),
          'intensity_curve': 'gradual_build_to_climax'
      }
  
  def _suggest_instrumentation(self, input_text: str) -> Dict[str, Any]:
      instrumentation_map = {
          'íntimo': 'solo_piano',
          'grandioso': 'full_orchestra',
          'moderno': 'electronic_synthesizers',
          'tradicional': 'string_quartet',
          'popular': 'rock_band_setup'
      }
      
      for keyword, instruments in instrumentation_map.items():
          if keyword in input_text.lower():
              return {
                  'primary_ensemble': instruments,
                  'featured_soloists': self._select_soloists(instruments),
                  'texture': self._determine_texture(instruments)
              }
      
      return {
          'primary_ensemble': 'chamber_ensemble',
          'featured_soloists': ['violin', 'piano'],
          'texture': 'homophonic_melody_with_accompaniment'
      }
  
  def _select_soloists(self, ensemble: str) -> List[str]:
      soloist_map = {
          'full_orchestra': ['violin', 'cello', 'flute'],
          'chamber_ensemble': ['violin', 'piano'],
          'electronic_synthesizers': ['lead_synth', 'pad_synth'],
          'string_quartet': ['first_violin'],
          'solo_piano': ['piano']
      }
      return soloist_map.get(ensemble, ['piano'])
  
  def _determine_texture(self, ensemble: str) -> str:
      texture_map = {
          'full_orchestra': 'polyphonic_complex',
          'chamber_ensemble': 'homophonic_clear',
          'electronic_synthesizers': 'layered_atmospheric',
          'string_quartet': 'contrapuntal_interweaving',
          'solo_piano': 'melody_with_accompaniment'
      }
      return texture_map.get(ensemble, 'balanced_texture')
  
  def get_response_style(self) -> Dict[str, str]:
      return {
          'tone': 'musical_expressive',
          'structure': 'compositional_flow',
          'detail_level': 'harmonic_detailed',
          'visualization': 'musical_notation_concepts',
          'language_use': 'musical_terminology'
      }

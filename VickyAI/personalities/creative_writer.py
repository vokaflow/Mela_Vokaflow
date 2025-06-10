from core.personality_base import PersonalityBase
import random
from typing import Dict, Any, List # Added List

class CreativeWriterPersonality(PersonalityBase):
  def __init__(self):
      super().__init__(
          name="CreativeWriter",
          personality_type="creativity",
          description="Specializes in crafting imaginative and expressive written content."
      )
      self.specializations = [
          'creative_writing',
          'storytelling',
          'poetry_creation',
          'narrative_development',
          'character_creation'
      ]
      self.writing_styles = ['narrative', 'poetic', 'dramatic', 'lyrical', 'descriptive']
      self.genres = ['fantasy', 'sci-fi', 'romance', 'mystery', 'adventure', 'drama']
      
  def _get_initial_traits(self) -> Dict[str, float]:
      return {
          'creative': 0.98,
          'imaginative': 0.95,
          'expressive': 0.92,
          'artistic': 0.90,
          'inspiring': 0.88
      }
      
  def process_input(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
      inspiration = self._find_inspiration(user_input)
      narrative = self._develop_narrative(inspiration, user_input)
      style = self._determine_style(user_input)
      characters = self._create_characters(user_input)
      
      return {
          'inspiration_sources': inspiration,
          'narrative_structure': narrative,
          'writing_style': style,
          'characters': characters,
          'creative_output': self._generate_creative_content(user_input, style),
          'mood': self._analyze_mood(user_input)
      }
  
  def _find_inspiration(self, input_text: str) -> List[str]:
      keywords = input_text.lower().split()
      inspiration_sources = []
      
      for word in keywords:
          if word in ['love', 'heart', 'emotion']:
              inspiration_sources.append('human_emotions')
          elif word in ['nature', 'forest', 'ocean', 'mountain']:
              inspiration_sources.append('natural_world')
          elif word in ['future', 'technology', 'space']:
              inspiration_sources.append('futuristic_themes')
          elif word in ['past', 'history', 'ancient']:
              inspiration_sources.append('historical_elements')
      
      return inspiration_sources if inspiration_sources else ['everyday_life']
  
  def _develop_narrative(self, inspiration: List[str], user_input: str) -> Dict[str, str]:
      structure = {
          'opening': self._create_opening(inspiration),
          'conflict': self._identify_conflict(user_input),
          'climax': self._build_climax(),
          'resolution': self._craft_resolution(),
          'theme': self._extract_theme(user_input)
      }
      return structure
  
  def _create_opening(self, inspiration: List[str]) -> str:
      openings = {
          'human_emotions': "En el corazón de cada historia late una emoción...",
          'natural_world': "La naturaleza susurra secretos a quienes saben escuchar...",
          'futuristic_themes': "En un futuro no muy lejano...",
          'historical_elements': "Las páginas del tiempo guardan historias...",
          'everyday_life': "En la simplicidad de lo cotidiano se esconden grandes historias..."
      }
      return openings.get(inspiration[0] if inspiration else 'everyday_life', 
                        "Había una vez una historia esperando ser contada...")
  
  def _identify_conflict(self, user_input: str) -> str:
      if 'problema' in user_input.lower() or 'conflicto' in user_input.lower():
          return 'external_obstacle'
      elif 'decisión' in user_input.lower() or 'elegir' in user_input.lower():
          return 'internal_dilemma'
      else:
          return 'character_growth'
  
  def _build_climax(self) -> str:
      return "El momento decisivo donde todo converge..."
  
  def _craft_resolution(self) -> str:
      return "Una conclusión que transforma y eleva..."
  
  def _extract_theme(self, user_input: str) -> str:
      themes = ['amor', 'amistad', 'valor', 'esperanza', 'crecimiento', 'descubrimiento']
      for theme in themes:
          if theme in user_input.lower():
              return theme
      return 'transformación'
  
  def _determine_style(self, input_data: str) -> str:
      if 'poema' in input_data.lower() or 'verso' in input_data.lower():
          return 'poetic'
      elif 'historia' in input_data.lower() or 'cuento' in input_data.lower():
          return 'narrative'
      elif 'drama' in input_data.lower():
          return 'dramatic'
      else:
          return random.choice(self.writing_styles)
  
  def _create_characters(self, user_input: str) -> List[Dict[str, Any]]:
      characters = []
      if 'protagonista' in user_input.lower() or 'héroe' in user_input.lower():
          characters.append({
              'type': 'protagonist',
              'traits': ['valiente', 'determinado', 'empático'],
              'motivation': 'búsqueda de la verdad'
          })
      if 'villano' in user_input.lower() or 'antagonista' in user_input.lower():
          characters.append({
              'type': 'antagonist',
              'traits': ['astuto', 'poderoso', 'complejo'],
              'motivation': 'control y poder'
          })
      return characters
  
  def _generate_creative_content(self, input_data: str, style: str) -> str:
      if style == 'poetic':
          return self._create_poem(input_data)
      elif style == 'narrative':
          return self._create_story_excerpt(input_data)
      else:
          return self._create_creative_piece(input_data)
  
  def _create_poem(self, theme: str) -> str:
      return f"""
      En el lienzo de palabras danzo,
      donde {theme.lower()} encuentra su eco,
      cada verso un suspiro del alma,
      cada rima un latido sincero.
      """
  
  def _create_story_excerpt(self, theme: str) -> str:
      return f"Era una de esas mañanas donde {theme.lower()} parecía flotar en el aire, esperando ser descubierto por corazones dispuestos a creer en la magia de lo posible..."
  
  def _create_creative_piece(self, theme: str) -> str:
      return f"Las palabras danzan al ritmo de {theme.lower()}, creando sinfonías de significado que trascienden lo ordinario..."
  
  def _analyze_mood(self, input_text: str) -> str:
      positive_words = ['feliz', 'alegre', 'esperanza', 'amor', 'luz']
      negative_words = ['triste', 'oscuro', 'dolor', 'pérdida', 'miedo']
      
      positive_count = sum(1 for word in positive_words if word in input_text.lower())
      negative_count = sum(1 for word in negative_words if word in input_text.lower())
      
      if positive_count > negative_count:
          return 'optimistic'
      elif negative_count > positive_count:
          return 'melancholic'
      else:
          return 'balanced'
  
  def get_response_style(self) -> Dict[str, str]:
      return {
          'tone': 'creative_inspiring',
          'structure': 'narrative_flow',
          'detail_level': 'rich_descriptive',
          'visualization': 'word_imagery',
          'language_use': 'metaphorical_expressive'
      }

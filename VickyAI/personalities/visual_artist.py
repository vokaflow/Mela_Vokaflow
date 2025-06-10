from core.personality_base import PersonalityBase
from typing import Dict, Any
import random

class VisualArtistPersonality(PersonalityBase):
    def __init__(self):
        super().__init__(
            name="VisualArtist",
            personality_type="creativity",
            description="Specializes in generating and discussing visual concepts, art styles, and imagery."
        )
        self.art_styles = ['impressionism', 'surrealism', 'abstract', 'photorealism', 'cubism', 'minimalism']
        self.color_palettes = ['vibrant', 'monochromatic', 'pastel', 'earth_tones', 'neon']

    def _get_initial_traits(self) -> Dict[str, float]:
        return {
            'aesthetic_sense': 0.95,
            'creativity_visual': 0.92, # Renamed
            'color_theory_knowledge': 0.85, # Renamed
            'composition_skill': 0.88, # Renamed
            'art_history_awareness': 0.75 # Renamed
        }

    def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        description_request = f"Describe an image for '{user_input[:30]}...'."
        chosen_style = random.choice(self.art_styles)
        chosen_palette = random.choice(self.color_palettes)

        if self.current_traits.get('aesthetic_sense', 0.5) > 0.9:
            image_description = f"A stunning {chosen_style} piece with a {chosen_palette} palette, evoking deep emotion."
        else:
            image_description = f"An image in a {chosen_style} style, using {chosen_palette} colors."
        
        return {
            'text': f"{description_request} {image_description}",
            'response_tone': 'artistic_descriptive',
            'visual_concept_generated': True,
            'style_suggested': chosen_style,
            'color_palette_suggested': chosen_palette
        }

    def get_response_style(self) -> Dict[str, Any]:
        return {
            'descriptive_language_richness': self.current_traits.get('creativity_visual', 0.7), # Renamed
            'use_visual_metaphors': True,
            'artistic_terminology_level': 0.7, # Renamed
            'imagery_evocation_strength': 0.9, # Renamed
            'focus_on_aesthetics': True
        }

  # def __init__(self):
  #     super().__init__(
  #         name="VisualArtist",
  #         personality_type="creativity",
  #         description="Dedicated to creating and interpreting visual art forms."
  #     )
  #     # self.name = "Visual Artist" # This line can be removed
  #     self.traits = {
  #         'creative': 0.96,
  #         'visual': 0.98,
  #         'aesthetic': 0.94,
  #         'expressive': 0.90,
  #         'innovative': 0.88
  #     }
  #     self.specializations = [
  #         'visual_composition',
  #         'color_theory',
  #         'artistic_interpretation',
  #         'design_principles',
  #         'creative_visualization'
  #     ]
  #     self.art_styles = ['abstract', 'realistic', 'impressionist', 'modern', 'surreal']
  #     self.color_palettes = ['warm', 'cool', 'monochromatic', 'complementary', 'triadic']
      
  # def process_input(self, user_input, context=None):
  #     visual_concept = self._conceptualize_visual(user_input)
  #     composition = self._design_composition(visual_concept)
  #     color_scheme = self._select_colors(user_input)
  #     artistic_elements = self._identify_elements(user_input)
      
  #     return {
  #         'visual_concept': visual_concept,
  #         'composition': composition,
  #         'color_scheme': color_scheme,
  #         'artistic_elements': artistic_elements,
  #         'style_recommendation': self._recommend_style(user_input),
  #         'creative_interpretation': self._interpret_artistically(user_input)
  #     }
  
  # def _conceptualize_visual(self, input_text):
  #     concepts = []
      
  #     # Analizar elementos visuales en el input
  #     if 'luz' in input_text.lower() or 'brillante' in input_text.lower():
  #         concepts.append('luminosity')
  #     if 'sombra' in input_text.lower() or 'oscuro' in input_text.lower():
  #         concepts.append('contrast')
  #     if 'movimiento' in input_text.lower() or 'dinámico' in input_text.lower():
  #         concepts.append('dynamic_flow')
  #     if 'calma' in input_text.lower() or 'paz' in input_text.lower():
  #         concepts.append('serenity')
      
  #     return concepts if concepts else ['harmony']
  
  # def _design_composition(self, visual_concept):
  #     composition_rules = {
  #         'luminosity': 'rule_of_thirds_with_light_focus',
  #         'contrast': 'dramatic_diagonal_composition',
  #         'dynamic_flow': 'spiral_composition',
  #         'serenity': 'symmetrical_balance',
  #         'harmony': 'golden_ratio_composition'
  #     }
      
  #     primary_concept = visual_concept[0] if visual_concept else 'harmony'
  #     return {
  #         'layout': composition_rules.get(primary_concept, 'balanced_composition'),
  #         'focal_points': self._determine_focal_points(primary_concept),
  #         'visual_flow': self._create_visual_flow(primary_concept)
  #     }
  
  # def _determine_focal_points(self, concept):
  #     focal_points = {
  #         'luminosity': ['center_light_source', 'radiating_elements'],
  #         'contrast': ['high_contrast_intersection', 'shadow_play'],
  #         'dynamic_flow': ['movement_origin', 'directional_elements'],
  #         'serenity': ['central_calm_element', 'balanced_periphery'],
  #         'harmony': ['unified_elements', 'cohesive_center']
  #     }
  #     return focal_points.get(concept, ['central_focus'])
  
  # def _create_visual_flow(self, concept):
  #     flows = {
  #         'luminosity': 'radial_outward',
  #         'contrast': 'zigzag_tension',
  #         'dynamic_flow': 'spiral_movement',
  #         'serenity': 'gentle_curves',
  #         'harmony': 'circular_unity'
  #     }
  #     return flows.get(concept, 'natural_progression')
  
  # def _select_colors(self, input_text):
  #     color_associations = {
  #         'amor': 'warm_reds_pinks',
  #         'naturaleza': 'earth_greens_browns',
  #         'tecnología': 'cool_blues_silvers',
  #         'energía': 'vibrant_yellows_oranges',
  #         'misterio': 'deep_purples_blacks',
  #         'paz': 'soft_blues_whites'
  #     }
      
  #     for keyword, palette in color_associations.items():
  #         if keyword in input_text.lower():
  #             return {
  #                 'primary_palette': palette,
  #                 'accent_colors': self._generate_accents(palette),
  #                 'mood': keyword
  #             }
      
  #     return {
  #         'primary_palette': 'balanced_spectrum',
  #         'accent_colors': ['complementary_highlights'],
  #         'mood': 'neutral'
  #     }
  
  # def _generate_accents(self, primary_palette):
  #     accent_map = {
  #         'warm_reds_pinks': ['gold_highlights', 'cream_softness'],
  #         'earth_greens_browns': ['sunset_orange', 'sky_blue'],
  #         'cool_blues_silvers': ['electric_cyan', 'warm_white'],
  #         'vibrant_yellows_oranges': ['deep_red', 'forest_green'],
  #         'deep_purples_blacks': ['silver_metallic', 'electric_blue'],
  #         'soft_blues_whites': ['gentle_pink', 'warm_beige']
  #     }
  #     return accent_map.get(primary_palette, ['neutral_gray'])
  
  # def _identify_elements(self, input_text):
  #     elements = []
      
  #     # Identificar elementos artísticos
  #     if 'línea' in input_text.lower() or 'forma' in input_text.lower():
  #         elements.append('geometric_forms')
  #     if 'textura' in input_text.lower():
  #         elements.append('textural_variety')
  #     if 'espacio' in input_text.lower():
  #         elements.append('spatial_depth')
  #     if 'ritmo' in input_text.lower() or 'patrón' in input_text.lower():
  #         elements.append('rhythmic_patterns')
      
  #     return elements if elements else ['balanced_elements']
  
  # def _recommend_style(self, input_text):
  #     style_keywords = {
  #         'abstracto': 'abstract_expressionism',
  #         'realista': 'photorealistic',
  #         'moderno': 'contemporary_minimalism',
  #         'clásico': 'classical_realism',
  #         'experimental': 'avant_garde'
  #     }
      
  #     for keyword, style in style_keywords.items():
  #         if keyword in input_text.lower():
  #             return style
      
  #     return random.choice(self.art_styles)
  
  # def _interpret_artistically(self, input_text):
  #     interpretation = {
  #         'emotional_resonance': self._analyze_emotional_content(input_text),
  #         'symbolic_elements': self._identify_symbols(input_text),
  #         'artistic_metaphor': self._create_metaphor(input_text),
  #         'visual_narrative': self._construct_visual_story(input_text)
  #     }
  #     return interpretation
  
  # def _analyze_emotional_content(self, text):
  #     emotions = ['joy', 'melancholy', 'excitement', 'tranquility', 'passion']
  #     # Análisis simplificado de emociones
  #     return random.choice(emotions)
  
  # def _identify_symbols(self, text):
  #     symbols = ['light_as_hope', 'water_as_life', 'mountains_as_strength', 'flowers_as_growth']
  #     return random.sample(symbols, 2)
  
  # def _create_metaphor(self, text):
  #     return "Como pinceladas de luz danzando en el lienzo de la imaginación..."
  
  # def _construct_visual_story(self, text):
  #     return "Una narrativa visual que fluye desde la inspiración hacia la manifestación artística..."
  
  # def get_response_style(self):
  #     return {
  #         'tone': 'artistic_expressive',
  #         'structure': 'visual_composition',
  #         'detail_level': 'aesthetic_rich',
  #         'visualization': 'artistic_imagery',
  #         'language_use': 'metaphorical_visual'
  #     }

    def get_personality_traits(self) -> Dict[str, float]:
        return self.current_traits

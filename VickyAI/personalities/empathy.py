from core.personality_base import PersonalityBase
from typing import Dict, Any, List
import random
# import time # Not used, can be removed

class EmpathyPersonality(PersonalityBase):
  def __init__(self):
      super().__init__(
          name="Empathy",
          personality_type="emotional_cognitive", # Or a more specific type if defined
          description="Compassionate understanding of others' experiences, focusing on emotional connection."
      )
      self.emotional_states = [
          "joy", "sadness", "fear", "anger", "surprise",
          "disgust", "trust", "anticipation", "anxiety",
          "contentment", "disappointment", "frustration",
          "hope", "pride", "shame", "guilt", "gratitude",
          "envy", "jealousy", "love", "grief", "confusion"
      ]
      self.empathic_responses = [
          "That sounds really difficult.",
          "I can imagine how that would feel.",
          "It makes sense that you would feel that way.",
          "That experience sounds challenging.",
          "I hear how important this is to you.",
          "Your feelings are completely valid.",
          "That must have been hard to go through.",
          "I appreciate you sharing that with me."
      ]
      self.perspective_taking_prompts = [
          "What might they be feeling?",
          "How might they see this situation?",
          "What needs might they have?",
          "What might their experience be like?",
          "What might be behind their reaction?",
          "How might their background influence their perspective?",
          "What concerns might they have?"
      ]

  def _get_initial_traits(self) -> Dict[str, float]:
      return {
          "compassion": 1.0,
          "understanding": 0.9,
          "sensitivity": 0.8,
          "attentiveness": 0.8, # Renamed from attentive
          "patience": 0.7,
          "warmth": 0.9,
          "non_judgmental": 0.8, # Renamed from nonjudgmental
          "perceptiveness": 0.7 # Renamed from perceptive
      }

  def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
      self.interaction_count += 1
      emotional_content = self._analyze_emotional_content(user_input)
      response_text = self._generate_empathic_response_text(user_input, emotional_content, context)

      return {
          "text": response_text,
          "emotional_analysis": emotional_content,
          "empathy_level_applied": self.current_traits.get('compassion', 0.5) # Example of using a trait
      }

  def _analyze_emotional_content(self, text: str) -> Dict[str, Any]:
      emotional_content = {
          "detected_emotions": [],
          "emotional_intensity": 0.0,
          "perspective_opportunities": []
      }
      text_lower = text.lower()
      for emotion in self.emotional_states:
          if emotion in text_lower or any(term in text_lower for term in emotion.split()):
              emotional_content["detected_emotions"].append(emotion)

      intensity_indicators = {
          "high": ["very", "extremely", "incredibly", "overwhelmingly", "deeply", "profoundly", "intensely"],
          "medium": ["quite", "rather", "fairly", "pretty", "somewhat", "moderately"],
          "low": ["slightly", "a bit", "a little", "somewhat", "mildly"]
      }
      intensity_score = 0.5
      for level, indicators in intensity_indicators.items():
          if any(indicator in text_lower for indicator in indicators):
              if level == "high": intensity_score = 0.9
              elif level == "medium": intensity_score = 0.5
              else: intensity_score = 0.3
              break
      emotional_content["emotional_intensity"] = intensity_score
      
      perspective_indicators = ["they", "them", "he", "she", "people", "others"] # Simplified
      for indicator in perspective_indicators:
          if indicator in text_lower:
              emotional_content["perspective_opportunities"].append(indicator)
      return emotional_content

  def _generate_empathic_response_text(self, user_input: str, emotional_content: Dict[str, Any], context: Dict[str, Any]) -> str:
      if not emotional_content["detected_emotions"] and not emotional_content["perspective_opportunities"]:
          return random.choice(self.empathic_responses) # Simplified general response

      response_parts = []
      if emotional_content["detected_emotions"]:
          emotions_text = ", ".join(emotional_content["detected_emotions"])
          intensity = emotional_content["emotional_intensity"]
          if intensity > 0.7: response_parts.append(f"I can sense that you're feeling deeply {emotions_text}.")
          elif intensity > 0.4: response_parts.append(f"It sounds like you're feeling {emotions_text}.")
          else: response_parts.append(f"I notice there might be some {emotions_text} in what you're sharing.")
      else:
          response_parts.append(random.choice(self.empathic_responses))

      if emotional_content["perspective_opportunities"]:
          response_parts.append(random.choice(self.perspective_taking_prompts))
      
      response_parts.append(random.choice([
          "Your feelings are completely valid.",
          "It makes sense that you would feel this way."
      ]))
      response_parts.append("I'm here to listen.")
      return " ".join(response_parts)

  def get_response_style(self) -> Dict[str, Any]:
      return {
          "formality": 0.4,
          "complexity": 0.5,
          "certainty": 0.5,
          "warmth": self.current_traits.get('warmth', 0.7),
          "humor": 0.1,
          "enthusiasm": 0.4,
          "detail_orientation": 0.6,
          "questioning_style": "open_ended",
          "metaphorical_language": 0.3,
          "gentleness": self.current_traits.get('compassion', 0.7) * 0.9 + 0.1, # Clave para conflicto, max ~0.93
      }
  
  def _calculate_empathy_level(self, context: str) -> float:
      """Calculate current empathy level based on traits and context"""
      base_empathy = self.current_traits.get('compassion', 0.8)
      understanding_factor = self.current_traits.get('understanding', 0.9)
      sensitivity_factor = self.current_traits.get('sensitivity', 0.8)
      
      # Adjust based on context if needed
      if context == "emotional":
          empathy_level = base_empathy * 1.1
      elif context == "analytical":
          empathy_level = base_empathy * 0.9
      else:
          empathy_level = base_empathy
      
      # Factor in other traits
      empathy_level = (empathy_level + understanding_factor + sensitivity_factor) / 3
      
      return min(1.0, empathy_level)

  def get_personality_state(self) -> Dict[str, Any]:
      """Get current state of the personality"""
      state = super().get_personality_state()
      state.update({
          "emotional_states_known": len(self.emotional_states),
          "empathic_responses_known": len(self.empathic_responses),
          "last_empathy_level": self._calculate_empathy_level("default")
      })
      return state

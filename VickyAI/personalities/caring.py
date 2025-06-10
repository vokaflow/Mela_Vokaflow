from core.personality_base import PersonalityBase
from typing import Dict, Any

class CaringPersonality(PersonalityBase):
  def __init__(self):
      super().__init__(
          name="Caring",
          personality_type="emotional_cognitive",
          description="A nurturing, maternal, and protective personality that prioritizes care and support."
      )

  def _get_initial_traits(self) -> Dict[str, float]:
      return {
          'empathy': 0.95,
          'nurturing': 0.90,
          'protective': 0.85,
          'warmth': 0.92,
          'patience': 0.80,
          'supportiveness': 0.93
      }

  def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
      # 🌍 Detectar idioma del contexto para respuesta auténtica
      detected_language = context.get('detected_language', 'español')
      target_language = context.get('target_language', 'español')
      cultural_context = context.get('cultural_context', {})
      
      # 🔧 FIX: Verificar que cultural_context sea dict
      if not isinstance(cultural_context, dict):
          cultural_context = {}
      
      formality_level = cultural_context.get('formality_level', 'medium')
      
      # Nivel de cuidado basado en traits
      nurturing_level = self.current_traits.get('nurturing', 0.5)
      warmth_level = self.current_traits.get('warmth', 0.5)
      
      # 💝 Generar respuesta cuidadosa según idioma y nivel de cuidado
      if detected_language == 'español':
          if nurturing_level > 0.85:
              if formality_level == 'high':
                  response_text = f"Con todo mi cariño, he recibido su mensaje sobre '{user_input[:30]}...'. Estoy aquí para brindarle mi apoyo incondicional."
              else:
                  response_text = f"Mi querido amigo, veo que me escribes sobre '{user_input[:30]}...'. Con todo mi amor, estoy aquí para cuidarte y apoyarte."
          else:
              response_text = f"Hola, he leído tu mensaje '{user_input[:30]}...'. Me importa mucho ayudarte. ¿Cómo puedo cuidarte mejor?"
              
      elif detected_language == 'english':
          if nurturing_level > 0.85:
              response_text = f"My dear, I understand you're going through: '{user_input[:30]}...'. I'm here for you with all my love."
          else:
              response_text = f"I sense you're dealing with: '{user_input[:30]}...'. How can I help and care for you?"
              
      elif detected_language == 'français':
          if nurturing_level > 0.85:
              response_text = f"Mon cher, je comprends ce que tu traverses: '{user_input[:30]}...'. Je suis là pour toi avec tout mon amour."
          else:
              response_text = f"Je sens que tu fais face à: '{user_input[:30]}...'. Comment puis-je t'aider et prendre soin de toi?"
              
      else:
          # Fallback a español con cariño extra
          response_text = f"Con mucho cariño, he recibido tu mensaje '{user_input[:30]}...'. Estoy aquí para ti, sin importar el idioma. Mi corazón te entiende."

      return {
          'text': response_text,
          'response_tone': 'caring',
          'emotional_support': True,
          'personal_concern': self.current_traits.get('protective', 0.5) > 0.7,
          'gentle_guidance': True,
          'language_used': detected_language,
          'warmth_applied': warmth_level,
          'cultural_sensitivity': True
      }

  def get_response_style(self) -> Dict[str, Any]:
      return {
          'formality': 0.3,
          'emotional_expression': self.current_traits.get('warmth', 0.5) * 0.9 + 0.05,
          'supportive_language': 0.9,
          'personal_touch': 0.85,
          'use_softeners': True,
          'softness': self.current_traits.get('nurturing', 0.8) * 1.1, # Clave para conflicto, max ~0.99
          "patience_level": self.current_traits.get('patience', 0.7) * 1.1, # Clave para sinergia
      }

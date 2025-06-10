from typing import Dict, List, Any, Optional
import json
import logging
import time
import re 
import copy
import uuid

from core.personality_base import PersonalityBase
# ... (importaciones de otras personalidades)
from personalities.analytic import AnalyticPersonality
from personalities.caring import CaringPersonality
from personalities.romantic import RomanticPersonality
from personalities.direct import DirectPersonality
from personalities.playful import PlayfulPersonality
from personalities.professional import ProfessionalPersonality
from personalities.empathy import EmpathyPersonality 
from personalities.creative_main import CreativeMainPersonality 
from personalities.philosophical import PhilosophicalPersonality
from personalities.rebellious import RebelliousPersonality
from personalities.warrior import WarriorPersonality
from personalities.mystic import MysticPersonality
from personalities.mentor import MentorPersonality
from personalities.detective import DetectivePersonality
from personalities.adventurous import AdventurousPersonality
from personalities.guardian import GuardianPersonality
from personalities.system_master import SystemMasterPersonality
from personalities.security_guardian import SecurityGuardianPersonality
from personalities.performance_optimizer import PerformanceOptimizerPersonality
from personalities.update_manager import UpdateManagerPersonality
from personalities.translation_expert import TranslationExpertPersonality
from personalities.voice_processor import VoiceProcessorPersonality
from personalities.language_detector import LanguageDetectorPersonality
from personalities.audio_analyzer import AudioAnalyzerPersonality
from personalities.data_scientist import DataScientistPersonality
from personalities.learning_coordinator import LearningCoordinatorPersonality 
from personalities.memory_manager import MemoryManagerPersonality
from personalities.algorithm_optimizer import AlgorithmOptimizerPersonality
from personalities.creative_writer import CreativeWriterPersonality
from personalities.visual_artist import VisualArtistPersonality
from personalities.music_composer import MusicComposerPersonality
from personalities.ethics import EthicsPersonality
from personalities.moral import MoralPersonality
from personalities.integrity import IntegrityPersonality
from personalities.wisdom import WisdomPersonality
from personalities.poetic import PoeticPersonality
from personalities.neural_architect import NeuralArchitectPersonality
from personalities.pattern_recognizer import PatternRecognizerPersonality
from personalities.meta_cognitive_analyst import MetaCognitiveAnalystPersonality
from personalities.negotiator import NegotiatorPersonality

logger = logging.getLogger(__name__)

LEARNING_RATE_KEYWORD_POSITIVE = 0.15
LEARNING_RATE_KEYWORD_NEGATIVE = 0.075
SUGGESTION_THRESHOLD = 0.3
MAX_KEYWORDS_PER_INPUT = 10


def extract_keywords(text: str, max_keywords: int = MAX_KEYWORDS_PER_INPUT) -> List[str]:
  words = re.findall(r'\b\w{3,15}\b', text.lower())
  return list(set(words[:max_keywords]))


class PersonalityManager:
  def __init__(self):
      self.personalities: Dict[str, PersonalityBase] = {}
      self.active_personalities: List[PersonalityBase] = []
      self.personality_weights: Dict[str, float] = {}
      self.interaction_history: List[Dict[str, Any]] = []
      self.keyword_personality_scores: Dict[str, Dict[str, float]] = {}
      self.learning_data: Dict[str, Any] = {} 
      
      self.last_conflict_resolution_info: Optional[Dict[str, Any]] = None
      self.last_synergy_applied_info: Optional[Dict[str, Any]] = None
      self.last_processed_interaction_summary: Optional[Dict[str, Any]] = None

      self._initialize_influence_rules() 
      self._initialize_conflict_style_rules()
      self._initialize_synergy_rules()
      self._initialize_personalities()

  def _initialize_synergy_rules(self):
      self.synergy_rules: List[Dict[str, Any]] = [
          {
              "personalities": ["Analytic", "Creative"], "min_activation_threshold": 0.5,
              "rule_name": "AnalyticCreativeInnovation",
              "effects": {
                  "individual_style_boost": {"Analytic": {"innovative_thinking": +0.2}, "Creative": {"analytical_rigor": +0.15}},
                  "base_response_enhancers": {"Analytic": {"prefix": "Desde un análisis creativo, ", "suffix": " ... explorando nuevas soluciones."}, "Creative": {"prefix": "Con una base analítica para esta idea, ", "suffix": " ... asegurando su viabilidad."}}
              }
          },
          {
              "personalities": ["Mentor", "Caring"], "min_activation_threshold": 0.4,
              "rule_name": "EmpatheticGuidance",
              "effects": {
                  "individual_style_boost": {"Mentor": {"empathetic_guidance": +0.2}, "Caring": {"structured_support": +0.15}},
                  "base_response_enhancers": {"ANY": {"prefix": "Con paciencia y cuidado, permíteme guiarte: "}}
              }
          },
          {
              "personalities": ["Negotiator", "Analytic"], "min_activation_threshold": 0.4,
              "rule_name": "DataDrivenNegotiation",
              "effects": {
                  "individual_style_boost": {
                      "Negotiator": {"data_informed_options": +0.2}, 
                      "Analytic": {"solution_oriented_analysis": +0.15} 
                  },
                  "base_response_enhancers": {
                      "Negotiator": {"prefix": "Considerando los datos y las opciones de forma estructurada, ", "suffix": " ... para una decisión bien informada."},
                      "Analytic": {"prefix": "Analizando las implicaciones de cada alternativa, ", "suffix": " ... para facilitar la negociación."}
                  }
              }
          },
          { # Nueva regla de sinergia
              "personalities": ["Ethics", "Negotiator"],
              "min_activation_threshold": 0.4,
              "rule_name": "EthicalDecisionGuidance",
              "effects": {
                  "individual_style_boost": {
                      "Negotiator": {"ethical_awareness_in_options": +0.25}, 
                      "Ethics": {"solution_oriented_ethics": +0.20}      
                  },
                  "base_response_enhancers": {
                      "ANY": { # Se aplicará al dominante si es Ethics o Negotiator y el otro está en sinergia
                          "prefix": "Considerando las implicaciones éticas junto con las opciones prácticas, "
                      }
                  }
              }
          }
      ]
      logger.info(f"Initialized {len(self.synergy_rules)} synergy rules.")
      self.last_synergy_applied_info = None

  def _initialize_conflict_style_rules(self):
      self.conflict_style_rules: List[Dict[str, Any]] = [
          {
              "pair": ("Direct", "Empathy"), "p1_name": "Direct", "p2_name": "Empathy",
              "rule_name": "DirectEmpathyBalance",
              "style_key_p1": "directness", "style_key_p2": "gentleness", "check_type": "inverse_sum", "threshold": 1.4,
              "moderator_is_p2": True, 
              "moderation_effects": {"style_adjustments": {"directness": -0.2}, "response_text_modifiers": {"prefix": "Entiendo la necesidad de ser claros, pero consideremos también cómo se recibe el mensaje. "}}
          },
          {
              "pair": ("Warrior", "Caring"), "p1_name": "Warrior", "p2_name": "Caring",
              "rule_name": "WarriorCaringIntensity",
              "style_key_p1": "intensity", "style_key_p2": "softness", "check_type": "inverse_sum", "threshold": 1.3,
              "moderator_is_p2": True,
              "moderation_effects": {"style_adjustments": {"intensity": -0.15, "aggressiveness": -0.15}, "response_text_modifiers": {"prefix": "Con la fuerza necesaria, pero siempre desde el cuidado, "}}
          },
          {
              "pair": ("Professional", "Playful"), "p1_name": "Professional", "p2_name": "Playful",
              "rule_name": "ProfessionalPlayfulFormality",
              "style_key_p1": "formality", "style_key_p2": "formality", "check_type": "direct_difference", "threshold": 0.6,
              "moderator_is_p1": True, # Professional modera a Playful
              "moderation_effects": {
                  "style_adjustments": {"formality": +0.2}, # Aumenta la formalidad de Playful
                  "response_text_modifiers": {"prefix": "Aportando un enfoque creativo, pero dentro de un marco profesional, "} # Prefijo para la respuesta de Playful
              }
          }
      ]
      logger.info(f"Initialized {len(self.conflict_style_rules)} conflict style rules with refined logic.")
      self.last_conflict_resolution_info = None
      
  def _initialize_influence_rules(self):
      self.influence_rules: Dict[tuple[str, str], Dict[str, Any]] = {
          ("Caring", "Warrior"): {"style_adjustments": { "tono_determinado": -0.1, "motivación_intensa": -0.05,},"response_text_modifiers": { "prefix": "Con empatía y determinación, ",}},
          ("Professional", "Playful"): {"style_adjustments": { "formality": +0.15, "playful_tone": -0.15 }},
          ("Empathy", "Direct"): {"style_adjustments": {"directness": -0.1, "emotional_expression": +0.1},"response_text_modifiers": {"prefix": "Entendiendo tu perspectiva y siendo claros, ",}},
          ("Negotiator", "Empathy"): { 
            "style_adjustments": {"diplomacy": +0.1, "emotional_consideration": +0.15}, 
            "response_text_modifiers": {"prefix": "Considerando tus sentimientos y buscando un camino, "}
          }
      }
      logger.info(f"Initialized {len(self.influence_rules)} mutual influence rules.")

  def _initialize_personalities(self):
      all_personality_classes = [
          AnalyticPersonality, CaringPersonality, RomanticPersonality, DirectPersonality,
          PlayfulPersonality, ProfessionalPersonality, EmpathyPersonality, CreativeMainPersonality, 
          PhilosophicalPersonality, RebelliousPersonality, WarriorPersonality, MysticPersonality, 
          MentorPersonality, DetectivePersonality, AdventurousPersonality, GuardianPersonality,
          SystemMasterPersonality, SecurityGuardianPersonality, PerformanceOptimizerPersonality,
          UpdateManagerPersonality, TranslationExpertPersonality, VoiceProcessorPersonality,
          LanguageDetectorPersonality, AudioAnalyzerPersonality, DataScientistPersonality,
          LearningCoordinatorPersonality, MemoryManagerPersonality,
          AlgorithmOptimizerPersonality, NeuralArchitectPersonality, PatternRecognizerPersonality,
          CreativeWriterPersonality, VisualArtistPersonality, MusicComposerPersonality, PoeticPersonality,
          EthicsPersonality, MoralPersonality, IntegrityPersonality, WisdomPersonality,
          MetaCognitiveAnalystPersonality, NegotiatorPersonality
      ]
      for personality_class in all_personality_classes:
          try:
              personality = personality_class()
              if personality.name in self.personalities: logger.warning(f"Duplicate personality name '{personality.name}' found. Overwriting.")
              self.personalities[personality.name] = personality
              self.personality_weights[personality.name] = 0.0
          except NameError as e: logger.error(f"Failed to initialize personality: {e}. Class might be missing or not imported.")
          except Exception as e: logger.error(f"Error initializing personality {personality_class.__name__}: {e}")
      logger.info(f"Initialized {len(self.personalities)} personalities")

  def _prepare_system_snapshot_for_metacognition(self) -> Dict[str, Any]:
      active_p_details = []
      for p_instance in self.active_personalities:
          if p_instance.activation_level > 0:
            active_p_details.append({
                "name": p_instance.name, "activation_level": p_instance.activation_level,
                "current_traits_summary": {k: round(v,2) for k,v in p_instance.current_traits.items()}
            })
      return {
          "active_personalities_details": active_p_details,
          "personality_weights_preferences": copy.deepcopy(self.personality_weights),
          "last_interaction_summary": self.last_processed_interaction_summary,
          "recent_conflict_resolution_info": self.last_conflict_resolution_info,
          "recent_synergy_applied_info": self.last_synergy_applied_info,
          "total_interactions_logged": len(self.interaction_history),
          "manager_mode": "normal" 
      }

  def process_input(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
      self.last_conflict_resolution_info = None 
      self.last_synergy_applied_info = None
      original_context = copy.deepcopy(context)
      
      suggested_personalities = self._suggest_personalities(user_input, original_context)
      
      current_active_instances = [p for p in self.personalities.values() if p.activation_level > 0]
      current_active_names = {p.name for p in current_active_instances}
      suggested_names = set(suggested_personalities.keys())
      
      for p_instance in current_active_instances:
          if p_instance.name not in suggested_names and self.personality_weights.get(p_instance.name, 0.0) < SUGGESTION_THRESHOLD / 2:
              p_instance.deactivate()
      
      self.active_personalities.clear()
      activated_now_log = []
      active_p_data = {} 

      for personality_name, suggested_weight in suggested_personalities.items():
          p_instance = self.personalities[personality_name]
          effective_weight = max(suggested_weight, self.personality_weights.get(personality_name, 0.0))
          if effective_weight > 0:
            p_instance.activate(effective_weight) 
            if p_instance.activation_level > SUGGESTION_THRESHOLD / 2:
                active_p_data[personality_name] = p_instance.activation_level
                if suggested_weight > 0: activated_now_log.append(f"{personality_name}({suggested_weight:.2f}, pref:{self.personality_weights.get(personality_name, 0.0):.2f})")
      
      self.active_personalities = [p for p_name, p in self.personalities.items() if p.activation_level > SUGGESTION_THRESHOLD / 2]

      if activated_now_log: logger.info(f"Suggested/Weighted personalities for input: {', '.join(activated_now_log)}")
      else: logger.info("No personalities strongly suggested or preferred for this input.")

      personality_responses = {}
      for p_name_active in active_p_data.keys():
          personality = self.personalities[p_name_active]
          current_personality_context = copy.deepcopy(original_context)
          if personality.name == 'MetaCognitiveAnalyst':
              current_personality_context["system_snapshot"] = self._prepare_system_snapshot_for_metacognition()
          response_data = personality.process_input(user_input, current_personality_context)
          personality_responses[p_name_active] = {
              'response': response_data, 'weight': active_p_data[p_name_active], 
              'style': personality.get_response_style()
          }
      
      processed_responses = personality_responses
      if processed_responses:
          processed_responses_after_conflict = self._detect_and_resolve_style_conflicts(processed_responses)
          if processed_responses_after_conflict != processed_responses:
              logger.debug(f"Responses after conflict resolution: {json.dumps(processed_responses_after_conflict, indent=2, default=str)}")
              processed_responses = processed_responses_after_conflict
          
          processed_responses_after_influence = self._apply_mutual_influences(processed_responses)
          if processed_responses_after_influence != processed_responses:
              logger.debug(f"Responses after general mutual influence: {json.dumps(processed_responses_after_influence, indent=2, default=str)}")
              processed_responses = processed_responses_after_influence

          dominant_name_before_synergy = max(processed_responses, key=lambda p: processed_responses[p]['weight']) if processed_responses else None
          processed_responses_after_synergy = self._apply_synergy_effects(processed_responses, dominant_name_before_synergy)
          if processed_responses_after_synergy != processed_responses:
              logger.debug(f"Responses after synergy effects: {json.dumps(processed_responses_after_synergy, indent=2, default=str)}")
              processed_responses = processed_responses_after_synergy
              
          combined_response = self._combine_responses(processed_responses)
      else:
          combined_response = self._combine_responses({}) 
      
      self.last_processed_interaction_summary = {
          'user_input': user_input, 'primary_personality': combined_response.get('primary_personality'),
          'active_personalities': combined_response.get('active_personalities', []),
          'reasoning_notes': "Keyword matches, context, and personality weights."
      }
      interaction_id = self._store_interaction(user_input, original_context, combined_response, suggested_personalities)
      combined_response['interaction_id'] = interaction_id
      return combined_response

  def _apply_synergy_effects(self, current_responses: Dict[str, Dict], dominant_name: Optional[str]) -> Dict[str, Dict]:
      synergized_responses = copy.deepcopy(current_responses)
      applied_synergy_this_turn = False
      for rule in self.synergy_rules:
          synergy_personalities_in_rule = set(rule["personalities"])
          min_activation = rule.get("min_activation_threshold", SUGGESTION_THRESHOLD / 2)
          active_synergy_members = [p_name for p_name in synergy_personalities_in_rule if p_name in synergized_responses and synergized_responses[p_name].get('weight', 0) >= min_activation]
          
          if len(active_synergy_members) == len(synergy_personalities_in_rule):
              logger.info(f"Synergy rule '{rule.get('rule_name', 'UnnamedSynergy')}' triggered for: {', '.join(active_synergy_members)}")
              applied_synergy_this_turn = True
              self.last_synergy_applied_info = {
                  "rule_name": rule.get('rule_name', 'UnnamedSynergy'),
                  "rule_personalities": list(synergy_personalities_in_rule), 
                  "active_members": active_synergy_members, 
                  "effects_applied_summary": rule["effects"] # Simplificado
              }
              effects = rule["effects"]
              if "individual_style_boost" in effects:
                  for p_name_to_boost, style_boosts in effects["individual_style_boost"].items():
                      if p_name_to_boost in synergized_responses and p_name_to_boost in active_synergy_members : # Asegurar que el boost es para un miembro activo de la sinergia
                          target_style = synergized_responses[p_name_to_boost]['style']
                          for style_key, boost_value in style_boosts.items():
                              original_value = target_style.get(style_key, 0.0) # Asumir 0 si no existe para adición
                              new_value = min(max(original_value + boost_value, 0.0), 1.0)
                              target_style[style_key] = new_value
                              logger.debug(f"Synergy boost: {p_name_to_boost} style '{style_key}' from {original_value:.2f} to {new_value:.2f}")
              
              if "base_response_enhancers" in effects:
                  enhancers = effects["base_response_enhancers"]
                  target_for_enhancement = None
                  # Prioridad: El dominante general si está en la sinergia Y tiene enhancer específico
                  if dominant_name and dominant_name in active_synergy_members and dominant_name in enhancers:
                      target_for_enhancement = dominant_name
                  # Siguiente: El dominante general si está en la sinergia Y hay un enhancer "ANY"
                  elif dominant_name and dominant_name in active_synergy_members and "ANY" in enhancers:
                      target_for_enhancement = dominant_name
                  # Fallback: El primer miembro de la sinergia si hay enhancer "ANY" (si el dominante no está en la sinergia o no tiene enhancer)
                  elif "ANY" in enhancers and active_synergy_members:
                      target_for_enhancement = active_synergy_members[0] # O alguna otra lógica para elegir dentro de los miembros de la sinergia

                  if target_for_enhancement and target_for_enhancement in synergized_responses:
                      p_enhancers = enhancers.get(target_for_enhancement, enhancers.get("ANY"))
                      if p_enhancers:
                          response_data = synergized_responses[target_for_enhancement]['response']
                          original_text = response_data.get('text', "")
                          prefix = p_enhancers.get("prefix", "")
                          suffix = p_enhancers.get("suffix", "")
                          modified_text = prefix + original_text + suffix
                          if modified_text != original_text:
                              response_data['text'] = modified_text
                              logger.debug(f"Synergy enhancer for {target_for_enhancement}: added prefix='{prefix}', suffix='{suffix}'")
      if not applied_synergy_this_turn: self.last_synergy_applied_info = None # Reset si ninguna sinergia se aplicó
      return synergized_responses

  def _detect_and_resolve_style_conflicts(self, current_responses: Dict[str, Dict]) -> Dict[str, Dict]:
      resolved_responses = copy.deepcopy(current_responses)
      conflict_resolved_this_turn = False
      for rule in self.conflict_style_rules:
          p1_name, p2_name = rule["p1_name"], rule["p2_name"]
          if p1_name in resolved_responses and p2_name in resolved_responses:
              style1, style2 = resolved_responses[p1_name].get('style', {}), resolved_responses[p2_name].get('style', {})
              val1, val2 = style1.get(rule["style_key_p1"], 0.0), style2.get(rule["style_key_p2"], 0.0)
              conflict_detected = False
              if rule.get("check_type") == "inverse_sum" and (val1 + val2) > rule["threshold"]: conflict_detected = True
              elif rule.get("check_type") == "direct_difference" and abs(val1 - val2) > rule["threshold"]: conflict_detected = True
              
              if conflict_detected:
                  logger.info(f"Conflict rule '{rule.get('rule_name', 'UnnamedConflict')}' triggered between {p1_name} ({rule['style_key_p1']}:{val1:.2f}) and {p2_name} ({rule['style_key_p2']}:{val2:.2f}).")
                  conflict_resolved_this_turn = True
                  
                  moderator_name = p2_name if rule.get("moderator_is_p2", False) else p1_name
                  target_name = p1_name if rule.get("moderator_is_p2", False) else p2_name
                  
                  # Si la regla especifica que el moderador es P1, entonces P1 modera a P2.
                  # Si la regla especifica que el moderador es P2, entonces P2 modera a P1.
                  # El "target" de la moderación es la personalidad que NO es el moderador.
                  if rule.get("moderator_is_p1", False): # P1 modera a P2
                      moderator_name, target_name = p1_name, p2_name
                  elif rule.get("moderator_is_p2", False): # P2 modera a P1
                      moderator_name, target_name = p2_name, p1_name
                  else: # Default o si no está claro, P1 modera a P2 (o alguna otra lógica)
                       moderator_name, target_name = p1_name, p2_name
                       logger.warning(f"Conflict rule '{rule.get('rule_name')}' for {p1_name}/{p2_name} does not specify moderator clearly. Defaulting to {p1_name} moderating {p2_name}.")


                  self.last_conflict_resolution_info = {
                      "rule_name": rule.get('rule_name', 'UnnamedConflict'),
                      "conflicting_pair": (p1_name, p2_name),
                      "moderator": moderator_name,
                      "moderated_personality": target_name,
                      "details": f"{rule['style_key_p1']}:{val1:.2f} vs {rule['style_key_p2']}:{val2:.2f}",
                      "effects_applied_summary": rule["moderation_effects"]
                  }
                  effects = rule["moderation_effects"]
                  if "style_adjustments" in effects and target_name in resolved_responses:
                      target_style_dict = resolved_responses[target_name]['style']
                      for style_key, adj_val in effects["style_adjustments"].items():
                          original_val = target_style_dict.get(style_key, 0.5) # Default si no existe
                          new_val = min(max(original_val + adj_val, 0.0), 1.0)
                          target_style_dict[style_key] = new_val
                          logger.debug(f"Conflict moderation: {target_name} style '{style_key}' from {original_val:.2f} to {new_val:.2f}")
                  
                  if "response_text_modifiers" in effects and target_name in resolved_responses: # Modificador de texto se aplica a la respuesta del TARGET
                      target_response_data = resolved_responses[target_name]['response']
                      original_text = target_response_data.get('text', "")
                      prefix = effects["response_text_modifiers"].get("prefix", "")
                      suffix = effects["response_text_modifiers"].get("suffix", "")
                      modified_text = prefix + original_text + suffix
                      if modified_text != original_text:
                          target_response_data['text'] = modified_text
                          logger.debug(f"Conflict moderation for {target_name}: added prefix='{prefix}', suffix='{suffix}'")
      if not conflict_resolved_this_turn: self.last_conflict_resolution_info = None
      return resolved_responses

  def _apply_mutual_influences(self, personality_responses: Dict[str, Dict]) -> Dict[str, Dict]:
      if not self.influence_rules: return personality_responses
      influenced_responses = copy.deepcopy(personality_responses)
      active_influencers = set(influenced_responses.keys())
      for (influencer_name, influenced_name), rule in self.influence_rules.items():
          if influencer_name in active_influencers and influenced_name in active_influencers and influenced_name in influenced_responses:
              logger.debug(f"Applying mutual influence from {influencer_name} to {influenced_name}")
              if "style_adjustments" in rule:
                  target_style = influenced_responses[influenced_name].get('style', {})
                  for style_key, adjustment in rule["style_adjustments"].items():
                      original_value = target_style.get(style_key, 0.5) 
                      new_value = min(max(original_value + adjustment, 0.0), 1.0)
                      target_style[style_key] = new_value
                      logger.debug(f"  Influence: {influenced_name} style '{style_key}' from {original_value:.2f} to {new_value:.2f}")
                  influenced_responses[influenced_name]['style'] = target_style
              if "response_text_modifiers" in rule:
                  target_response_data = influenced_responses[influenced_name].get('response', {})
                  original_text = target_response_data.get('text', "")
                  prefix = rule.get("response_text_modifiers",{}).get("prefix","")
                  suffix = rule.get("response_text_modifiers",{}).get("suffix","")
                  modified_text = prefix + original_text + suffix
                  if modified_text != original_text:
                      target_response_data['text'] = modified_text
                      logger.debug(f"  Influence on {influenced_name} text: added prefix='{prefix}', suffix='{suffix}'")
                  influenced_responses[influenced_name]['response'] = target_response_data
      return influenced_responses

  def _suggest_personalities(self, user_input: str, context: Dict[str, Any]) -> Dict[str, float]:
      suggestions: Dict[str, float] = {}
      input_lower = user_input.lower()
      
      meta_kws = ["why did you", "explain your reasoning", "your state", "how do you work", "system status", "meta-analysis", "self-reflect", "personality choice"]
      if any(kw in input_lower for kw in meta_kws):
          suggestions['MetaCognitiveAnalyst'] = suggestions.get('MetaCognitiveAnalyst', 0) + 0.95
          for p_name in list(suggestions.keys()):
              if p_name != 'MetaCognitiveAnalyst': suggestions[p_name] = suggestions.get(p_name,0) * 0.3
      
      negotiation_kws = ["decidir", "dilema", "opciones", "pros y contras", "ventajas y desventajas", "negociar", "compromiso", "mediar", "ayúdame a elegir", "estoy entre", "sopesar"]
      ethics_kws_for_negotiation = ["ético", "moral", "valores", "integridad", "dilema moral", "conducta"] # Para potenciar Negotiator si hay temas éticos
      
      is_negotiation_context = any(kw in input_lower for kw in negotiation_kws)
      is_ethics_context_for_negotiation = any(kw in input_lower for kw in ethics_kws_for_negotiation)

      if is_negotiation_context and not suggestions.get('MetaCognitiveAnalyst'):
          suggestions['Negotiator'] = suggestions.get('Negotiator', 0) + 0.9
          if 'Analytic' in self.personalities: suggestions['Analytic'] = suggestions.get('Analytic', 0) + 0.3
          if 'Empathy' in self.personalities: suggestions['Empathy'] = suggestions.get('Empathy', 0) + 0.2
          if is_ethics_context_for_negotiation and 'Ethics' in self.personalities: # Si es negociación Y hay palabras éticas
              suggestions['Ethics'] = suggestions.get('Ethics', 0) + 0.7 # Activar Ethics también
              suggestions['Negotiator'] += 0.1 # Potenciar un poco más a Negotiator

      # Sugerencias para Ethics fuera de un contexto de negociación directa
      general_ethics_kws = ["ética", "moralidad", "principios éticos", "es correcto", "debería"]
      if any(kw in input_lower for kw in general_ethics_kws) and not suggestions.get('MetaCognitiveAnalyst') and not is_negotiation_context:
          suggestions['Ethics'] = suggestions.get('Ethics', 0) + 0.85
          if 'Philosophical' in self.personalities: suggestions['Philosophical'] = suggestions.get('Philosophical', 0) + 0.2
          if 'Wisdom' in self.personalities: suggestions['Wisdom'] = suggestions.get('Wisdom', 0) + 0.2


      technical_kws = ['code', 'python', 'javascript', 'debug', 'algorithm', 'data', 'system', 'technical', 'software', 'error', 'optimizar', 'rendimiento']
      if any(kw in input_lower for kw in technical_kws) and not suggestions.get('MetaCognitiveAnalyst') and not suggestions.get('Negotiator'):
          suggestions['Analytic'] = suggestions.get('Analytic', 0) + 0.6
          suggestions['SystemMaster'] = suggestions.get('SystemMaster', 0) + 0.5
          if any(kw in input_lower for kw in ['algorithm', 'optimizar', 'rendimiento']):
              suggestions['AlgorithmOptimizer'] = suggestions.get('AlgorithmOptimizer', 0) + 0.7
              suggestions['PerformanceOptimizer'] = suggestions.get('PerformanceOptimizer', 0) + 0.7


      # ... (resto de la lógica de _suggest_personalities para otras personalidades) ...
      # Ejemplo para Caring
      caring_kws = ["triste", "preocupado", "mal", "ayuda emocional", "siento", "estresado"]
      if any(kw in input_lower for kw in caring_kws) and not suggestions.get('MetaCognitiveAnalyst'):
          suggestions['Caring'] = suggestions.get('Caring', 0) + 0.8
          suggestions['Empathy'] = suggestions.get('Empathy', 0) + 0.5
      
      # Ejemplo para CreativeWriter
      creative_writing_kws = ["escribe una historia", "poema", "cuento", "narrativa", "ficción"]
      if any(kw in input_lower for kw in creative_writing_kws) and not suggestions.get('MetaCognitiveAnalyst'):
          suggestions['CreativeWriter'] = suggestions.get('CreativeWriter', 0) + 0.9
          suggestions['CreativeMain'] = suggestions.get('CreativeMain', 0) + 0.7 # Activar la principal también

      # Ejemplo para Mentor
      mentor_kws = ["cómo aprendo", "enséñame", "guíame para", "explicación paso a paso", "tutorial"]
      if any(kw in input_lower for kw in mentor_kws) and not suggestions.get('MetaCognitiveAnalyst'):
          suggestions['Mentor'] = suggestions.get('Mentor', 0) + 0.85
          if 'Analytic' in self.personalities: suggestions['Analytic'] = suggestions.get('Analytic', 0) + 0.2 # Para explicaciones estructuradas

      # Ejemplo para Philosophical
      philosophical_kws = ["sentido de la vida", "existencia", "realidad", "consciencia", "por qué estamos aquí"]
      if any(kw in input_lower for kw in philosophical_kws) and not suggestions.get('MetaCognitiveAnalyst'):
          suggestions['Philosophical'] = suggestions.get('Philosophical', 0) + 0.9
          if 'Wisdom' in self.personalities: suggestions['Wisdom'] = suggestions.get('Wisdom', 0) + 0.3
      
      # Ejemplo para TranslationExpert
      translation_kws = ["traduce esto", "en inglés", "al español", "translate to", "qué significa en"]
      if any(kw in input_lower for kw in translation_kws) and not suggestions.get('MetaCognitiveAnalyst'):
          suggestions['TranslationExpert'] = suggestions.get('TranslationExpert', 0) + 0.95


      input_keywords = extract_keywords(input_lower)
      for keyword in input_keywords:
          if keyword in self.keyword_personality_scores:
              for p_name, score in self.keyword_personality_scores[keyword].items():
                  is_meta_strong = 'MetaCognitiveAnalyst' in suggestions and suggestions['MetaCognitiveAnalyst'] > 0.7
                  is_negotiator_strong = 'Negotiator' in suggestions and suggestions['Negotiator'] > 0.7
                  if p_name in self.personalities and not (p_name != 'MetaCognitiveAnalyst' and is_meta_strong) and not (p_name != 'Negotiator' and is_negotiator_strong):
                      learned_influence = score * 0.5 
                      suggestions[p_name] = suggestions.get(p_name, 0) + learned_influence
      
      final_suggestions = {
          name: min(weight, 1.0) for name, weight in suggestions.items() if weight >= SUGGESTION_THRESHOLD
      }
      if not final_suggestions:
          if 'MetaCognitiveAnalyst' in suggestions and suggestions['MetaCognitiveAnalyst'] > 0:
              final_suggestions['MetaCognitiveAnalyst'] = suggestions['MetaCognitiveAnalyst']
          elif 'Negotiator' in suggestions and suggestions['Negotiator'] > 0:
              final_suggestions['Negotiator'] = suggestions['Negotiator']
          # Podríamos añadir un fallback a una personalidad general si ninguna otra se activa
          elif not self.personalities.get("DefaultResponder"): # Si no hay una personalidad por defecto
              if "Caring" in self.personalities: final_suggestions["Caring"] = SUGGESTION_THRESHOLD # Fallback muy genérico
              elif "Professional" in self.personalities: final_suggestions["Professional"] = SUGGESTION_THRESHOLD
              
      return final_suggestions

  def _update_learned_suggestions(self, keywords: List[str], primary_personality_name: str, rating_modifier: float):
      if not primary_personality_name: return
      for keyword in keywords:
          if keyword not in self.keyword_personality_scores: self.keyword_personality_scores[keyword] = {}
          current_score = self.keyword_personality_scores[keyword].get(primary_personality_name, 0.0)
          if rating_modifier > 0: new_score = current_score + LEARNING_RATE_KEYWORD_POSITIVE * rating_modifier * (1.0 - current_score)
          else: new_score = current_score + LEARNING_RATE_KEYWORD_NEGATIVE * rating_modifier * current_score
          self.keyword_personality_scores[keyword][primary_personality_name] = min(max(new_score, 0.0), 1.0)

  def _combine_responses(self, personality_responses: Dict[str, Dict]) -> Dict[str, Any]:
      if not personality_responses: return {'primary_personality': None, 'response_characteristics': {}, 'base_response': {'text': 'No tengo una respuesta específica en este momento.'}, 'personality_weights': {}} # Texto por defecto mejorado
      valid_responses = {k: v for k, v in personality_responses.items() if v.get('weight',0) > 1e-6 and v.get('response',{}).get('text','').strip()} # Asegurar que haya texto
      if not valid_responses: return {'primary_personality': None, 'response_characteristics': {}, 'base_response': {'text': 'Aunque varias ideas surgieron, ninguna parece completamente adecuada ahora.'}, 'personality_weights': {}}
      
      total_weight = sum(resp['weight'] for resp in valid_responses.values())
      if total_weight == 0: return {'primary_personality': None, 'response_characteristics': {}, 'base_response': {'text': 'No hay un enfoque claro para esta consulta en este momento.'}, 'personality_weights': {}}
      
      dominant_personality_name = max(valid_responses, key=lambda p_name: valid_responses[p_name]['weight'])
      base_response_content = valid_responses[dominant_personality_name]['response']
      combined_style: Dict[str, float] = {}
      
      for p_name, resp_data in valid_responses.items():
          style, weight_ratio = resp_data.get('style',{}), resp_data['weight'] / total_weight if total_weight > 0 else 0
          for characteristic, value in style.items():
              if isinstance(value, (int, float)): combined_style[characteristic] = combined_style.get(characteristic, 0.0) + (value * weight_ratio)
      return {
          'primary_personality': dominant_personality_name,
          'active_personalities': list(valid_responses.keys()),
          'response_characteristics': combined_style,
          'base_response': base_response_content,
          'personality_weights': {name: data['weight'] for name, data in valid_responses.items()}
      }

  def _store_interaction(self, user_input: str, context: Dict[str, Any], combined_response: Dict[str, Any], suggested_personalities: Dict[str, float]) -> str:
      interaction_id = uuid.uuid4().hex 
      timestamp = time.time()
      interaction = {
          'interaction_id': interaction_id, 
          'timestamp': timestamp, 'user_input': user_input, 'context': context,
          'combined_response': combined_response, 
          'suggested_personalities_weights': suggested_personalities,
          'active_personalities_at_response': [p.name for p in self.active_personalities if p.activation_level > 0]
      }
      self.interaction_history.append(interaction)
      if len(self.interaction_history) > 1000: self.interaction_history = self.interaction_history[-1000:]
      primary_personality_name = combined_response.get('primary_personality')
      
      if primary_personality_name and primary_personality_name not in ['MetaCognitiveAnalyst', 'Negotiator']: # Y quizás 'Ethics' si su aprendizaje es muy específico
          if primary_personality_name in self.personalities:
              personality_instance = self.personalities[primary_personality_name]
              feedback_for_personality = {'is_primary_responder': True, 'user_rating': None} # Simula un "éxito" general
              response_generated_by_personality = combined_response.get('base_response', {})
              personality_instance.learn_from_interaction(
                 feedback_for_personality, user_input, response_generated_by_personality, specific_rating=None # rating=1.0 implícito
              )
              keywords = extract_keywords(user_input.lower())
              # Usar un rating_modifier positivo pero moderado para el aprendizaje automático de keywords
              self._update_learned_suggestions(keywords, primary_personality_name, rating_modifier=0.5) # Reducido de 1.0
      return interaction_id

  def process_specific_feedback(self, interaction_id: str, feedback_details: Dict[str, int]):
      logger.info(f"Processing specific feedback for interaction ID: {interaction_id}")
      original_interaction = next((inter for inter in reversed(self.interaction_history) if inter.get('interaction_id') == interaction_id), None)
      if not original_interaction:
          logger.warning(f"Could not find interaction ID '{interaction_id}' for specific feedback.")
          return
      user_input_original = original_interaction['user_input']
      keywords_original = extract_keywords(user_input_original.lower())
      for p_name, rating in feedback_details.items(): # rating es -1, 0, o 1
          if p_name not in self.personalities: continue
          personality_instance = self.personalities[p_name]
          
          # Ajustar keyword_personality_scores basado en el rating explícito
          # Un rating de 1 (positivo) refuerza, -1 (negativo) penaliza.
          keyword_rating_modifier = float(rating) # Convertir -1, 0, 1 a float
          if keyword_rating_modifier != 0.0:
              self._update_learned_suggestions(keywords_original, p_name, rating_modifier=keyword_rating_modifier)
          
          # Pasar el rating específico a la personalidad para su aprendizaje interno
          mock_response_by_self = original_interaction['combined_response']['base_response'] 
          feedback_for_instance = {'is_primary_responder': (p_name == original_interaction['combined_response'].get('primary_personality'))}
          
          logger.debug(f"Applying specific feedback (rating: {rating}) to '{p_name}' for input: '{user_input_original}'")
          personality_instance.learn_from_interaction(
              feedback=feedback_for_instance, user_input=user_input_original,
              response_generated_by_self=mock_response_by_self, specific_rating=rating # Pasar el rating -1, 0, 1
          )
      logger.info(f"Specific feedback processed for interaction {interaction_id}.")
      
  def get_current_personality_profile(self) -> Dict[str, float]:
      return copy.deepcopy(self.personality_weights)

  def apply_personality_profile(self, profile: Dict[str, float]):
      for p_name in self.personality_weights: self.personality_weights[p_name] = 0.0
      for personality_name, weight in profile.items(): self.set_personality_weight(personality_name, weight)

  def set_personality_weight(self, personality_name: str, weight: float):
      if personality_name in self.personalities:
          clamped_weight = min(max(0.0, weight), 1.0)
          self.personality_weights[personality_name] = clamped_weight
          logger.info(f"Set preference weight for '{personality_name}' to {clamped_weight:.2f}")
      else: logger.warning(f"Cannot set weight for non-existent personality: {personality_name}")
          
  def get_personality_status(self) -> Dict[str, Any]:
      status = {}
      for name, personality_obj in self.personalities.items(): status[name] = personality_obj.get_personality_state() 
      return {
          'personalities_status': status,
          'manager_active_personalities': [p.name for p in self.active_personalities if p.activation_level > 0],
          'total_interactions_logged': len(self.interaction_history),
          'learned_keyword_associations_count': len(self.keyword_personality_scores),
          'last_conflict_info': self.last_conflict_resolution_info, # Para inspección
          'last_synergy_info': self.last_synergy_applied_info      # Para inspección
      }

  def save_state(self, filepath: str):
      personalities_full_state = {}
      for name, p_instance in self.personalities.items():
          p_state = p_instance.get_personality_state()
          # Guardar memorias explícitamente si es necesario (ya se hace en get_personality_state si está implementado)
          # p_state['short_term_memory_content'] = p_instance.get_short_term_memories()
          # p_state['long_term_memory_content'] = p_instance.get_long_term_memories()
          personalities_full_state[name] = p_state
      state = {
          'interaction_history': self.interaction_history[-200:], # Limitar historial guardado
          'keyword_personality_scores': self.keyword_personality_scores,
          'general_learning_data': self.learning_data, 
          'personalities_full_state': personalities_full_state,
          'personality_weights': self.personality_weights # Guardar preferencias de usuario
      }
      try:
          with open(filepath, 'w') as f: json.dump(state, f, indent=2, default=str) # default=str para objetos no serializables
          logger.info(f"PersonalityManager state saved to {filepath}")
      except IOError as e: logger.error(f"Error saving state to {filepath}: {e}")
      except TypeError as e: logger.error(f"TypeError during state saving: {e}")


  def load_state(self, filepath: str):
      try:
          with open(filepath, 'r') as f: state = json.load(f)
          self.interaction_history = state.get('interaction_history', [])
          self.keyword_personality_scores = state.get('keyword_personality_scores', {})
          self.learning_data = state.get('general_learning_data', {}) 
          self.personality_weights = state.get('personality_weights', self.personality_weights) # Cargar preferencias
          
          loaded_p_states = state.get('personalities_full_state', {})
          if loaded_p_states:
              for p_name, p_state_data in loaded_p_states.items():
                  if p_name in self.personalities: 
                      self.personalities[p_name].set_state_from_dict(p_state_data) 
                  else: logger.warning(f"State for unknown personality '{p_name}' during load.")
          else: logger.info("No full personality states in state file.")
          logger.info(f"PersonalityManager state loaded from {filepath}. Learned keyword associations: {len(self.keyword_personality_scores)}")
      except FileNotFoundError: logger.warning(f"State file {filepath} not found. Initializing with default state.")
      except json.JSONDecodeError: logger.error(f"Could not decode JSON from state file {filepath}.")
      except IOError as e: logger.error(f"Error loading state from {filepath}: {e}")

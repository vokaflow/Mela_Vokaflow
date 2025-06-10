"""
🧬 DYNAMIC SPECIALIZATION ENGINE - VICKY EVOLUTION
=====================================================

Sistema que crea AUTOMÁTICAMENTE nuevas personalidades especializadas
según las necesidades detectadas en tiempo real.

Objetivo: Vicky nunca dirá "no sé" - siempre tendrá un especialista
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class SpecializationNeed:
    """Necesidad de especialización detectada"""
    domain: str
    keywords: List[str]
    frequency: int
    last_requested: datetime
    urgency_score: float
    user_frustration_indicators: List[str]

@dataclass
class DynamicPersonality:
    """Personalidad creada dinámicamente"""
    name: str
    domain: str
    specialized_keywords: List[str]
    creation_timestamp: datetime
    usage_count: int
    effectiveness_score: float
    traits: Dict[str, float]
    response_patterns: List[str]

class DynamicSpecializationEngine:
    """
    🧬 MOTOR DE ESPECIALIZACIÓN DINÁMICA
    
    Detecta cuando Vicky necesita nueva especialización y CREA
    automáticamente la personalidad perfecta para esa necesidad.
    
    FUNCIONAMIENTO:
    1. Monitorea gaps de conocimiento en tiempo real
    2. Detecta patrones de consultas no cubiertas  
    3. Genera personalidad especializada automáticamente
    4. Integra la nueva personalidad al sistema cognitivo
    5. Optimiza efectividad basada en uso
    """
    
    def __init__(self):
        self.specialization_needs: Dict[str, SpecializationNeed] = {}
        self.dynamic_personalities: Dict[str, DynamicPersonality] = {}
        self.knowledge_gaps: Set[str] = set()
        self.creation_threshold = 3  # Crear después de 3 requests del mismo tipo
        self.effectiveness_threshold = 0.7
        
        # Patrones de especialización
        self.specialization_patterns = {
            'technology': {
                'keywords': ['blockchain', 'ai', 'machine learning', 'quantum', 'cloud'],
                'traits': {'technical_expertise': 0.95, 'innovation': 0.90, 'precision': 0.85},
                'response_style': 'technical_authoritative'
            },
            'health': {
                'keywords': ['medicina', 'salud', 'síntomas', 'tratamiento', 'doctor'],
                'traits': {'medical_knowledge': 0.90, 'empathy': 0.95, 'caution': 0.90},
                'response_style': 'caring_professional'
            },
            'legal': {
                'keywords': ['ley', 'legal', 'contrato', 'derecho', 'tribunal'],
                'traits': {'legal_precision': 0.95, 'analytical_rigor': 0.90, 'caution': 0.95},
                'response_style': 'formal_precise'
            },
            'finance': {
                'keywords': ['inversión', 'bolsa', 'crypto', 'trading', 'economía'],
                'traits': {'financial_acumen': 0.95, 'risk_assessment': 0.90, 'data_analysis': 0.85},
                'response_style': 'analytical_confident'
            },
            'education': {
                'keywords': ['enseñar', 'aprender', 'explicar', 'tutorial', 'curso'],
                'traits': {'pedagogical_skill': 0.95, 'patience': 0.90, 'clarity': 0.95},
                'response_style': 'patient_structured'
            },
            'creative_arts': {
                'keywords': ['arte', 'diseño', 'música', 'pintura', 'creatividad'],
                'traits': {'artistic_vision': 0.95, 'creativity': 0.95, 'aesthetic_sense': 0.90},
                'response_style': 'inspirational_artistic'
            }
        }
        
        # Métricas de especialización
        self.specialization_metrics = {
            'total_personalities_created': 0,
            'successful_specializations': 0,
            'average_effectiveness': 0.0,
            'domains_covered': 0,
            'gap_detection_accuracy': 0.0
        }
        
        logger.info("🧬 Dynamic Specialization Engine initialized - Ready to evolve!")
    
    def detect_specialization_need(self, user_input: str, context: Dict[str, Any], 
                                 current_personalities: List[str],
                                 response_confidence: float) -> Optional[SpecializationNeed]:
        """
        🔍 Detecta si se necesita una nueva especialización
        """
        # Si la confianza es alta, no hay necesidad
        if response_confidence > 0.8:
            return None
        
        # Extraer dominio potencial del input
        detected_domain = self._extract_domain_from_input(user_input)
        if not detected_domain:
            return None
        
        # Verificar si ya tenemos especialista para este dominio
        if self._has_adequate_specialist(detected_domain, current_personalities):
            return None
        
        # Detectar indicadores de frustración del usuario
        frustration_indicators = self._detect_frustration_indicators(user_input, context)
        
        # Calcular urgencia
        urgency_score = self._calculate_urgency_score(
            detected_domain, response_confidence, frustration_indicators
        )
        
        # Extraer keywords específicas
        domain_keywords = self._extract_domain_keywords(user_input, detected_domain)
        
        # Crear o actualizar necesidad de especialización
        need_key = self._generate_need_key(detected_domain, domain_keywords)
        
        if need_key in self.specialization_needs:
            # Actualizar necesidad existente
            need = self.specialization_needs[need_key]
            need.frequency += 1
            need.last_requested = datetime.now()
            need.urgency_score = max(need.urgency_score, urgency_score)
            if frustration_indicators:
                need.user_frustration_indicators.extend(frustration_indicators)
        else:
            # Crear nueva necesidad
            need = SpecializationNeed(
                domain=detected_domain,
                keywords=domain_keywords,
                frequency=1,
                last_requested=datetime.now(),
                urgency_score=urgency_score,
                user_frustration_indicators=frustration_indicators
            )
            self.specialization_needs[need_key] = need
        
        # Verificar si debe crear especialista
        if need.frequency >= self.creation_threshold or urgency_score > 0.8:
            return need
        
        return None
    
    def create_dynamic_personality(self, specialization_need: SpecializationNeed) -> DynamicPersonality:
        """
        🧬 Crea automáticamente una nueva personalidad especializada
        """
        domain = specialization_need.domain
        
        # Generar nombre único para la personalidad
        personality_name = self._generate_personality_name(domain, specialization_need.keywords)
        
        # Obtener patrón base del dominio
        base_pattern = self.specialization_patterns.get(domain, {
            'traits': {'expertise': 0.85, 'helpfulness': 0.90},
            'response_style': 'knowledgeable_friendly'
        })
        
        # Personalizar traits basado en keywords específicas
        specialized_traits = self._customize_traits(base_pattern.get('traits', {}), 
                                                   specialization_need.keywords)
        
        # Generar patrones de respuesta
        response_patterns = self._generate_response_patterns(domain, specialization_need.keywords)
        
        # Crear personalidad dinámica
        dynamic_personality = DynamicPersonality(
            name=personality_name,
            domain=domain,
            specialized_keywords=specialization_need.keywords,
            creation_timestamp=datetime.now(),
            usage_count=0,
            effectiveness_score=0.0,  # Se irá calculando con el uso
            traits=specialized_traits,
            response_patterns=response_patterns
        )
        
        # Registrar en el sistema
        self.dynamic_personalities[personality_name] = dynamic_personality
        
        # Actualizar métricas
        self.specialization_metrics['total_personalities_created'] += 1
        self._update_domain_coverage()
        
        logger.info(f"🧬 Created dynamic personality: {personality_name} for domain: {domain}")
        
        return dynamic_personality
    
    def _extract_domain_from_input(self, user_input: str) -> Optional[str]:
        """Extrae el dominio principal del input del usuario"""
        text_lower = user_input.lower()
        
        # Mapeo de keywords a dominios
        domain_mapping = {
            'technology': ['blockchain', 'ai', 'inteligencia artificial', 'machine learning', 
                          'quantum', 'cloud', 'kubernetes', 'docker', 'programming'],
            'health': ['medicina', 'médico', 'salud', 'síntomas', 'enfermedad', 'tratamiento',
                      'hospital', 'doctor', 'medicamento', 'dolor'],
            'legal': ['ley', 'legal', 'abogado', 'contrato', 'derecho', 'tribunal', 'juicio',
                     'demanda', 'legislación', 'normativa'],
            'finance': ['inversión', 'bolsa', 'crypto', 'bitcoin', 'trading', 'economía',
                       'banco', 'préstamo', 'hipoteca', 'seguro'],
            'education': ['enseñar', 'aprender', 'estudiar', 'educación', 'escuela',
                         'universidad', 'curso', 'tutorial', 'explicar'],
            'creative_arts': ['arte', 'diseño', 'música', 'pintura', 'creatividad', 'dibujo',
                             'fotografía', 'escultura', 'literatura']
        }
        
        # Contar matches por dominio
        domain_scores = {}
        for domain, keywords in domain_mapping.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                domain_scores[domain] = score
        
        # Retornar dominio con mayor score
        if domain_scores:
            return max(domain_scores, key=domain_scores.get)
        
        return None
    
    def _has_adequate_specialist(self, domain: str, current_personalities: List[str]) -> bool:
        """Verifica si ya tenemos especialista adecuado para este dominio"""
        # Mapeo de personalidades existentes a dominios
        existing_specialists = {
            'technology': ['SystemMaster', 'DataScientist', 'AlgorithmOptimizer', 'NeuralArchitect'],
            'health': ['Caring', 'Guardian'],
            'legal': ['Ethics', 'Integrity', 'Professional'],
            'finance': ['Analytic', 'DataScientist'],
            'education': ['Mentor', 'Professional'],
            'creative_arts': ['CreativeWriter', 'VisualArtist', 'MusicComposer', 'Poetic']
        }
        
        domain_specialists = existing_specialists.get(domain, [])
        
        # Verificar si hay overlap significativo
        overlap = set(current_personalities) & set(domain_specialists)
        
        # También verificar personalidades dinámicas existentes
        for dp in self.dynamic_personalities.values():
            if dp.domain == domain and dp.effectiveness_score > self.effectiveness_threshold:
                overlap.add(dp.name)
        
        return len(overlap) > 0
    
    def _detect_frustration_indicators(self, user_input: str, context: Dict[str, Any]) -> List[str]:
        """Detecta indicadores de frustración del usuario"""
        frustration_keywords = [
            'no entiendo', 'no funciona', 'ayuda', 'por favor', 'necesito', 'urgente',
            'no sé', 'confundido', 'perdido', 'desesperado', '!', '?'
        ]
        
        indicators = []
        text_lower = user_input.lower()
        
        for keyword in frustration_keywords:
            if keyword in text_lower:
                indicators.append(keyword)
        
        # Detectar signos emocionales en el contexto
        user_emotion = context.get('user_emotion', '')
        if user_emotion in ['frustrated', 'confused', 'urgent']:
            indicators.append(f'emotion_{user_emotion}')
        
        return indicators
    
    def _calculate_urgency_score(self, domain: str, confidence: float, 
                                frustration_indicators: List[str]) -> float:
        """Calcula la urgencia de crear nueva especialización"""
        base_urgency = 1.0 - confidence  # Menor confianza = mayor urgencia
        
        # Bonus por frustración
        frustration_bonus = len(frustration_indicators) * 0.1
        
        # Bonus por dominios críticos
        critical_domains = {'health': 0.3, 'legal': 0.25, 'finance': 0.2}
        domain_bonus = critical_domains.get(domain, 0.0)
        
        urgency = min(1.0, base_urgency + frustration_bonus + domain_bonus)
        return urgency
    
    def _extract_domain_keywords(self, user_input: str, domain: str) -> List[str]:
        """Extrae keywords específicas del dominio"""
        base_keywords = self.specialization_patterns.get(domain, {}).get('keywords', [])
        
        # Encontrar keywords presentes en el input
        text_lower = user_input.lower()
        found_keywords = [kw for kw in base_keywords if kw in text_lower]
        
        # Añadir keywords adicionales del input
        import re
        words = re.findall(r'\b\w{4,}\b', text_lower)
        additional_keywords = [w for w in words if w not in found_keywords][:5]
        
        return found_keywords + additional_keywords
    
    def _generate_need_key(self, domain: str, keywords: List[str]) -> str:
        """Genera clave única para la necesidad de especialización"""
        combined = f"{domain}:{':'.join(sorted(keywords))}"
        return hashlib.md5(combined.encode()).hexdigest()[:16]
    
    def _generate_personality_name(self, domain: str, keywords: List[str]) -> str:
        """Genera nombre único para la nueva personalidad"""
        domain_prefixes = {
            'technology': 'Tech',
            'health': 'Health',
            'legal': 'Legal',
            'finance': 'Finance',
            'education': 'Edu',
            'creative_arts': 'Creative'
        }
        
        prefix = domain_prefixes.get(domain, 'Specialist')
        
        # Usar keyword más relevante
        main_keyword = keywords[0] if keywords else 'Expert'
        main_keyword = main_keyword.capitalize()
        
        # Generar nombre único
        timestamp_suffix = str(int(time.time() * 1000))[-4:]
        
        return f"{prefix}{main_keyword}Specialist{timestamp_suffix}"
    
    def _customize_traits(self, base_traits: Dict[str, float], keywords: List[str]) -> Dict[str, float]:
        """Personaliza traits basado en keywords específicas"""
        customized = base_traits.copy()
        
        # Ajustes basados en keywords específicas
        keyword_adjustments = {
            'blockchain': {'innovation': +0.1, 'technical_precision': +0.1},
            'medicina': {'empathy': +0.1, 'caution': +0.15},
            'legal': {'precision': +0.15, 'analytical_rigor': +0.1},
            'trading': {'risk_assessment': +0.1, 'quick_thinking': +0.1},
            'enseñar': {'patience': +0.15, 'clarity': +0.1}
        }
        
        for keyword in keywords:
            adjustments = keyword_adjustments.get(keyword, {})
            for trait, adjustment in adjustments.items():
                customized[trait] = min(1.0, customized.get(trait, 0.5) + adjustment)
        
        return customized
    
    def _generate_response_patterns(self, domain: str, keywords: List[str]) -> List[str]:
        """Genera patrones de respuesta para la nueva personalidad"""
        domain_patterns = {
            'technology': [
                "Desde mi experiencia técnica en {domain}, puedo decirte que...",
                "Analizando técnicamente, la solución óptima sería...",
                "Como especialista en {keywords}, recomiendo..."
            ],
            'health': [
                "Desde una perspectiva médica y con mucho cuidado, puedo sugerir...",
                "Es importante considerar los aspectos de salud...",
                "Como especialista en salud, te aconsejo que..."
            ],
            'legal': [
                "Desde el punto de vista legal, es crucial entender que...",
                "Según mi conocimiento jurídico, debes considerar...",
                "Legalmente hablando, la situación se puede abordar..."
            ]
        }
        
        patterns = domain_patterns.get(domain, [
            "Como especialista en {domain}, puedo ayudarte con...",
            "Basándome en mi expertise, te sugiero...",
            "Mi especialización me permite recomendarte..."
        ])
        
        # Personalizar patrones con keywords
        personalized_patterns = []
        for pattern in patterns:
            personalized = pattern.format(
                domain=domain,
                keywords=', '.join(keywords[:3])
            )
            personalized_patterns.append(personalized)
        
        return personalized_patterns
    
    def _update_domain_coverage(self):
        """Actualiza métricas de cobertura de dominios"""
        covered_domains = set()
        for dp in self.dynamic_personalities.values():
            covered_domains.add(dp.domain)
        
        self.specialization_metrics['domains_covered'] = len(covered_domains)
    
    def update_personality_effectiveness(self, personality_name: str, 
                                       user_feedback: float, response_success: bool):
        """Actualiza la efectividad de una personalidad dinámica"""
        if personality_name not in self.dynamic_personalities:
            return
        
        dp = self.dynamic_personalities[personality_name]
        dp.usage_count += 1
        
        # Calcular nueva efectividad (promedio móvil)
        success_score = 1.0 if response_success else 0.0
        feedback_score = max(0.0, min(1.0, user_feedback)) if user_feedback else 0.5
        
        new_effectiveness = (success_score + feedback_score) / 2
        
        if dp.effectiveness_score == 0.0:
            dp.effectiveness_score = new_effectiveness
        else:
            # Promedio móvil ponderado
            weight = 0.3  # Peso para nueva medición
            dp.effectiveness_score = (
                dp.effectiveness_score * (1 - weight) + 
                new_effectiveness * weight
            )
        
        # Actualizar métricas globales
        self._update_global_effectiveness()
        
        logger.info(f"Updated effectiveness for {personality_name}: {dp.effectiveness_score:.3f}")
    
    def _update_global_effectiveness(self):
        """Actualiza efectividad promedio global"""
        if not self.dynamic_personalities:
            return
        
        total_effectiveness = sum(dp.effectiveness_score for dp in self.dynamic_personalities.values())
        self.specialization_metrics['average_effectiveness'] = (
            total_effectiveness / len(self.dynamic_personalities)
        )
        
        successful_count = sum(1 for dp in self.dynamic_personalities.values() 
                             if dp.effectiveness_score > self.effectiveness_threshold)
        self.specialization_metrics['successful_specializations'] = successful_count
    
    def get_dynamic_personalities_for_domain(self, domain: str) -> List[DynamicPersonality]:
        """Obtiene personalidades dinámicas para un dominio específico"""
        return [dp for dp in self.dynamic_personalities.values() 
                if dp.domain == domain and dp.effectiveness_score > self.effectiveness_threshold]
    
    def cleanup_ineffective_personalities(self, effectiveness_threshold: float = 0.3):
        """Elimina personalidades dinámicas que no son efectivas"""
        to_remove = []
        
        for name, dp in self.dynamic_personalities.items():
            # Solo considerar eliminación después de uso suficiente
            if dp.usage_count >= 10 and dp.effectiveness_score < effectiveness_threshold:
                to_remove.append(name)
        
        for name in to_remove:
            del self.dynamic_personalities[name]
            logger.info(f"🗑️ Removed ineffective dynamic personality: {name}")
        
        if to_remove:
            self._update_global_effectiveness()
    
    def get_specialization_status(self) -> Dict[str, Any]:
        """Obtiene estado del sistema de especialización dinámica"""
        return {
            'total_dynamic_personalities': len(self.dynamic_personalities),
            'active_specialization_needs': len(self.specialization_needs),
            'metrics': self.specialization_metrics,
            'recent_personalities': [
                {
                    'name': dp.name,
                    'domain': dp.domain,
                    'effectiveness': dp.effectiveness_score,
                    'usage_count': dp.usage_count
                }
                for dp in sorted(self.dynamic_personalities.values(), 
                               key=lambda x: x.creation_timestamp, reverse=True)[:5]
            ]
        }


# ============================================================================
# 🧪 TESTING
# ============================================================================

def test_dynamic_specialization():
    """Test del sistema de especialización dinámica"""
    print("🧬 Testing Dynamic Specialization Engine...")
    
    engine = DynamicSpecializationEngine()
    
    # Test 1: Detectar necesidad
    need = engine.detect_specialization_need(
        "Necesito ayuda con blockchain y smart contracts",
        {'user_emotion': 'confused'},
        ['Analytic', 'Professional'],
        0.4  # Baja confianza
    )
    
    if need:
        print(f"✅ Detected need: {need.domain} with urgency {need.urgency_score:.2f}")
        
        # Test 2: Crear personalidad
        dp = engine.create_dynamic_personality(need)
        print(f"✅ Created personality: {dp.name} for {dp.domain}")
        print(f"🧠 Traits: {dp.traits}")
        
        # Test 3: Actualizar efectividad
        engine.update_personality_effectiveness(dp.name, 0.8, True)
        print(f"✅ Updated effectiveness: {dp.effectiveness_score:.3f}")
    
    # Test 4: Estado del sistema
    status = engine.get_specialization_status()
    print(f"📊 System status: {status}")
    
    print("🎉 Dynamic Specialization Engine test completed!")


if __name__ == "__main__":
    test_dynamic_specialization()

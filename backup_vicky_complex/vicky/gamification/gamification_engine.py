"""
Sistema de Gamificación para VokaFlow

Este módulo implementa un sistema completo de gamificación que incluye:
- Sistema de puntos y experiencia
- Logros y badges
- Niveles de progreso
- Desafíos y misiones
- Recompensas y beneficios
- Estadísticas y rankings
- Mecánicas de engagement
"""

import os
import time
import json
import logging
import math
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import random
import uuid

# Configuración de logging
logger = logging.getLogger("vicky.gamification")

class AchievementType(Enum):
    """Tipos de logros."""
    USAGE = "usage"
    LEARNING = "learning"
    EFFICIENCY = "efficiency"
    EXPLORATION = "exploration"
    SOCIAL = "social"
    MILESTONE = "milestone"
    SPECIAL = "special"

class AchievementRarity(Enum):
    """Rareza de logros."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class ChallengeType(Enum):
    """Tipos de desafíos."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SPECIAL_EVENT = "special_event"
    PERSONAL = "personal"

class RewardType(Enum):
    """Tipos de recompensas."""
    POINTS = "points"
    BADGE = "badge"
    TITLE = "title"
    FEATURE_UNLOCK = "feature_unlock"
    CUSTOMIZATION = "customization"
    SPECIAL_ACCESS = "special_access"

@dataclass
class Achievement:
    """Definición de un logro."""
    id: str
    name: str
    description: str
    type: AchievementType
    rarity: AchievementRarity
    points: int
    requirements: Dict[str, Any]
    icon: str
    unlock_message: str
    hidden: bool = False
    prerequisites: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserAchievement:
    """Logro desbloqueado por un usuario."""
    achievement_id: str
    user_id: str
    unlocked_at: float
    progress: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Challenge:
    """Definición de un desafío."""
    id: str
    name: str
    description: str
    type: ChallengeType
    start_time: float
    end_time: float
    requirements: Dict[str, Any]
    rewards: List[Dict[str, Any]]
    difficulty: str  # easy, medium, hard, expert
    max_participants: Optional[int] = None
    current_participants: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserChallenge:
    """Participación de usuario en un desafío."""
    challenge_id: str
    user_id: str
    joined_at: float
    progress: float = 0.0
    completed: bool = False
    completed_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserProfile:
    """Perfil de gamificación del usuario."""
    user_id: str
    level: int = 1
    experience: int = 0
    total_points: int = 0
    achievements_unlocked: List[str] = field(default_factory=list)
    active_challenges: List[str] = field(default_factory=list)
    titles: List[str] = field(default_factory=list)
    active_title: Optional[str] = None
    customizations: Dict[str, Any] = field(default_factory=dict)
    statistics: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)

class PointsCalculator:
    """Calculadora de puntos para diferentes actividades."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_points = config.get("base_points", {
            "message_sent": 10,
            "translation_used": 15,
            "voice_interaction": 20,
            "problem_solved": 50,
            "feature_discovered": 25,
            "daily_login": 5,
            "consecutive_days": 10,
            "feedback_given": 30,
            "help_request": 5,
            "advanced_feature": 40
        })
        
        self.multipliers = config.get("multipliers", {
            "streak_bonus": 1.5,
            "weekend_bonus": 1.2,
            "night_owl_bonus": 1.1,
            "efficiency_bonus": 2.0,
            "exploration_bonus": 1.3
        })
    
    def calculate_points(self, activity: str, context: Dict[str, Any] = None) -> int:
        """Calcula puntos para una actividad específica."""
        context = context or {}
        base = self.base_points.get(activity, 10)
        
        # Aplicar multiplicadores
        multiplier = 1.0
        
        # Bonus por racha
        if context.get("consecutive_days", 0) > 7:
            multiplier *= self.multipliers["streak_bonus"]
        
        # Bonus de fin de semana
        if datetime.now().weekday() >= 5:  # Sábado o domingo
            multiplier *= self.multipliers["weekend_bonus"]
        
        # Bonus nocturno (22:00 - 06:00)
        current_hour = datetime.now().hour
        if current_hour >= 22 or current_hour <= 6:
            multiplier *= self.multipliers["night_owl_bonus"]
        
        # Bonus por eficiencia
        if context.get("efficiency_score", 0) > 0.8:
            multiplier *= self.multipliers["efficiency_bonus"]
        
        # Bonus por exploración
        if context.get("new_feature_used", False):
            multiplier *= self.multipliers["exploration_bonus"]
        
        return int(base * multiplier)

class AchievementManager:
    """Gestor de logros y badges."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.achievements = {}
        self._load_achievements()
    
    def _load_achievements(self) -> None:
        """Carga las definiciones de logros."""
        # Logros de uso básico
        self.achievements.update({
            "first_message": Achievement(
                id="first_message",
                name="Primer Contacto",
                description="Envía tu primer mensaje a Vicky",
                type=AchievementType.MILESTONE,
                rarity=AchievementRarity.COMMON,
                points=50,
                requirements={"messages_sent": 1},
                icon="💬",
                unlock_message="¡Bienvenido a VokaFlow! Has dado tu primer paso."
            ),
            "chatterbox": Achievement(
                id="chatterbox",
                name="Conversador",
                description="Envía 100 mensajes",
                type=AchievementType.USAGE,
                rarity=AchievementRarity.UNCOMMON,
                points=200,
                requirements={"messages_sent": 100},
                icon="🗣️",
                unlock_message="¡Eres todo un conversador! Sigues explorando las capacidades de Vicky."
            ),
            "translator": Achievement(
                id="translator",
                name="Políglota",
                description="Usa la función de traducción 50 veces",
                type=AchievementType.USAGE,
                rarity=AchievementRarity.UNCOMMON,
                points=300,
                requirements={"translations_used": 50},
                icon="🌍",
                unlock_message="¡Dominas los idiomas! Eres un verdadero políglota digital."
            ),
            "voice_master": Achievement(
                id="voice_master",
                name="Maestro de Voz",
                description="Usa interacciones de voz 25 veces",
                type=AchievementType.USAGE,
                rarity=AchievementRarity.RARE,
                points=400,
                requirements={"voice_interactions": 25},
                icon="🎤",
                unlock_message="¡Tu voz es tu poder! Has dominado la comunicación vocal."
            ),
            "problem_solver": Achievement(
                id="problem_solver",
                name="Solucionador",
                description="Resuelve 10 problemas técnicos con ayuda de Vicky",
                type=AchievementType.EFFICIENCY,
                rarity=AchievementRarity.RARE,
                points=500,
                requirements={"problems_solved": 10},
                icon="🔧",
                unlock_message="¡Eres un solucionador nato! Los problemas no son rival para ti."
            ),
            "explorer": Achievement(
                id="explorer",
                name="Explorador",
                description="Descubre 15 características diferentes de VokaFlow",
                type=AchievementType.EXPLORATION,
                rarity=AchievementRarity.UNCOMMON,
                points=350,
                requirements={"features_discovered": 15},
                icon="🧭",
                unlock_message="¡Espíritu aventurero! Has explorado los rincones de VokaFlow."
            ),
            "streak_warrior": Achievement(
                id="streak_warrior",
                name="Guerrero de Rachas",
                description="Mantén una racha de 30 días consecutivos",
                type=AchievementType.MILESTONE,
                rarity=AchievementRarity.EPIC,
                points=1000,
                requirements={"consecutive_days": 30},
                icon="🔥",
                unlock_message="¡Imparable! Tu dedicación es legendaria."
            ),
            "efficiency_expert": Achievement(
                id="efficiency_expert",
                name="Experto en Eficiencia",
                description="Mantén una puntuación de eficiencia superior al 90% durante 7 días",
                type=AchievementType.EFFICIENCY,
                rarity=AchievementRarity.EPIC,
                points=800,
                requirements={"efficiency_streak": 7, "min_efficiency": 0.9},
                icon="⚡",
                unlock_message="¡Eficiencia máxima! Eres un maestro de la productividad."
            ),
            "night_owl": Achievement(
                id="night_owl",
                name="Búho Nocturno",
                description="Usa VokaFlow después de medianoche 20 veces",
                type=AchievementType.SPECIAL,
                rarity=AchievementRarity.RARE,
                points=300,
                requirements={"night_sessions": 20},
                icon="🦉",
                unlock_message="¡La noche es tuya! Trabajas cuando otros duermen."
            ),
            "feedback_champion": Achievement(
                id="feedback_champion",
                name="Campeón del Feedback",
                description="Proporciona feedback valioso 10 veces",
                type=AchievementType.SOCIAL,
                rarity=AchievementRarity.RARE,
                points=600,
                requirements={"feedback_given": 10},
                icon="💡",
                unlock_message="¡Tu opinión cuenta! Ayudas a mejorar VokaFlow."
            ),
            "legend": Achievement(
                id="legend",
                name="Leyenda de VokaFlow",
                description="Alcanza el nivel 50",
                type=AchievementType.MILESTONE,
                rarity=AchievementRarity.LEGENDARY,
                points=5000,
                requirements={"level": 50},
                icon="👑",
                unlock_message="¡LEYENDA! Has alcanzado la cima de VokaFlow.",
                hidden=True
            )
        })
    
    def check_achievements(self, user_profile: UserProfile, activity_data: Dict[str, Any]) -> List[Achievement]:
        """Verifica qué logros ha desbloqueado el usuario."""
        newly_unlocked = []
        
        for achievement_id, achievement in self.achievements.items():
            # Saltar si ya está desbloqueado
            if achievement_id in user_profile.achievements_unlocked:
                continue
            
            # Verificar prerrequisitos
            if achievement.prerequisites:
                if not all(prereq in user_profile.achievements_unlocked for prereq in achievement.prerequisites):
                    continue
            
            # Verificar requisitos
            if self._check_requirements(achievement.requirements, user_profile, activity_data):
                newly_unlocked.append(achievement)
                user_profile.achievements_unlocked.append(achievement_id)
                user_profile.total_points += achievement.points
                
                logger.info(f"Usuario {user_profile.user_id} desbloqueó logro: {achievement.name}")
        
        return newly_unlocked
    
    def _check_requirements(self, requirements: Dict[str, Any], 
                          user_profile: UserProfile, activity_data: Dict[str, Any]) -> bool:
        """Verifica si se cumplen los requisitos de un logro."""
        for req_key, req_value in requirements.items():
            # Verificar en estadísticas del usuario
            user_value = user_profile.statistics.get(req_key, 0)
            
            # Verificar en datos de actividad actual
            if req_key in activity_data:
                user_value = max(user_value, activity_data[req_key])
            
            # Verificar requisitos especiales
            if req_key == "level":
                user_value = user_profile.level
            elif req_key == "consecutive_days":
                user_value = self._calculate_consecutive_days(user_profile)
            elif req_key == "efficiency_streak":
                user_value = self._calculate_efficiency_streak(user_profile, requirements.get("min_efficiency", 0.8))
            
            # Comparar valores
            if user_value < req_value:
                return False
        
        return True
    
    def _calculate_consecutive_days(self, user_profile: UserProfile) -> int:
        """Calcula días consecutivos de uso."""
        # Implementación simplificada
        # En producción, esto consultaría el historial de actividad
        return user_profile.statistics.get("consecutive_days", 0)
    
    def _calculate_efficiency_streak(self, user_profile: UserProfile, min_efficiency: float) -> int:
        """Calcula racha de eficiencia."""
        # Implementación simplificada
        return user_profile.statistics.get("efficiency_streak", 0)

class ChallengeManager:
    """Gestor de desafíos y misiones."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.active_challenges = {}
        self._generate_daily_challenges()
    
    def _generate_daily_challenges(self) -> None:
        """Genera desafíos diarios automáticamente."""
        today = datetime.now().date()
        challenge_date = today.strftime("%Y-%m-%d")
        
        daily_challenges = [
            Challenge(
                id=f"daily_messages_{challenge_date}",
                name="Conversador Diario",
                description="Envía 20 mensajes hoy",
                type=ChallengeType.DAILY,
                start_time=time.mktime(today.timetuple()),
                end_time=time.mktime((today + timedelta(days=1)).timetuple()),
                requirements={"messages_sent": 20},
                rewards=[{"type": "points", "value": 100}, {"type": "badge", "value": "daily_chatter"}],
                difficulty="easy"
            ),
            Challenge(
                id=f"daily_translation_{challenge_date}",
                name="Traductor del Día",
                description="Realiza 10 traducciones hoy",
                type=ChallengeType.DAILY,
                start_time=time.mktime(today.timetuple()),
                end_time=time.mktime((today + timedelta(days=1)).timetuple()),
                requirements={"translations_used": 10},
                rewards=[{"type": "points", "value": 150}, {"type": "badge", "value": "daily_translator"}],
                difficulty="medium"
            ),
            Challenge(
                id=f"daily_efficiency_{challenge_date}",
                name="Eficiencia Máxima",
                description="Mantén una eficiencia del 85% durante todo el día",
                type=ChallengeType.DAILY,
                start_time=time.mktime(today.timetuple()),
                end_time=time.mktime((today + timedelta(days=1)).timetuple()),
                requirements={"min_efficiency": 0.85, "min_interactions": 5},
                rewards=[{"type": "points", "value": 200}, {"type": "title", "value": "Eficiente"}],
                difficulty="hard"
            )
        ]
        
        for challenge in daily_challenges:
            self.active_challenges[challenge.id] = challenge
    
    def get_available_challenges(self, user_profile: UserProfile) -> List[Challenge]:
        """Obtiene desafíos disponibles para un usuario."""
        current_time = time.time()
        available = []
        
        for challenge in self.active_challenges.values():
            # Verificar si está activo
            if challenge.start_time <= current_time <= challenge.end_time:
                # Verificar si el usuario ya participa
                if challenge.id not in user_profile.active_challenges:
                    # Verificar límite de participantes
                    if challenge.max_participants is None or challenge.current_participants < challenge.max_participants:
                        available.append(challenge)
        
        return available
    
    def join_challenge(self, user_profile: UserProfile, challenge_id: str) -> bool:
        """Permite a un usuario unirse a un desafío."""
        if challenge_id not in self.active_challenges:
            return False
        
        challenge = self.active_challenges[challenge_id]
        
        # Verificar si ya participa
        if challenge_id in user_profile.active_challenges:
            return False
        
        # Verificar límite de participantes
        if challenge.max_participants and challenge.current_participants >= challenge.max_participants:
            return False
        
        # Unir al usuario
        user_profile.active_challenges.append(challenge_id)
        challenge.current_participants += 1
        
        logger.info(f"Usuario {user_profile.user_id} se unió al desafío: {challenge.name}")
        return True
    
    def update_challenge_progress(self, user_profile: UserProfile, activity_data: Dict[str, Any]) -> List[Challenge]:
        """Actualiza el progreso de desafíos activos."""
        completed_challenges = []
        
        for challenge_id in user_profile.active_challenges.copy():
            if challenge_id not in self.active_challenges:
                user_profile.active_challenges.remove(challenge_id)
                continue
            
            challenge = self.active_challenges[challenge_id]
            
            # Verificar si el desafío ha expirado
            if time.time() > challenge.end_time:
                user_profile.active_challenges.remove(challenge_id)
                continue
            
            # Calcular progreso
            progress = self._calculate_challenge_progress(challenge, user_profile, activity_data)
            
            # Verificar si está completado
            if progress >= 1.0:
                completed_challenges.append(challenge)
                user_profile.active_challenges.remove(challenge_id)
                
                # Otorgar recompensas
                self._grant_challenge_rewards(user_profile, challenge)
                
                logger.info(f"Usuario {user_profile.user_id} completó desafío: {challenge.name}")
        
        return completed_challenges
    
    def _calculate_challenge_progress(self, challenge: Challenge, user_profile: UserProfile, 
                                    activity_data: Dict[str, Any]) -> float:
        """Calcula el progreso de un desafío."""
        total_progress = 0.0
        requirement_count = len(challenge.requirements)
        
        for req_key, req_value in challenge.requirements.items():
            user_value = user_profile.statistics.get(req_key, 0)
            
            # Considerar actividad del día actual
            if req_key in activity_data:
                user_value = activity_data[req_key]
            
            # Calcular progreso de este requisito
            req_progress = min(1.0, user_value / req_value)
            total_progress += req_progress
        
        return total_progress / requirement_count if requirement_count > 0 else 0.0
    
    def _grant_challenge_rewards(self, user_profile: UserProfile, challenge: Challenge) -> None:
        """Otorga recompensas por completar un desafío."""
        for reward in challenge.rewards:
            reward_type = reward.get("type")
            reward_value = reward.get("value")
            
            if reward_type == "points":
                user_profile.total_points += reward_value
            elif reward_type == "badge":
                if reward_value not in user_profile.achievements_unlocked:
                    user_profile.achievements_unlocked.append(reward_value)
            elif reward_type == "title":
                if reward_value not in user_profile.titles:
                    user_profile.titles.append(reward_value)

class LevelSystem:
    """Sistema de niveles y experiencia."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_exp = config.get("base_exp", 100)
        self.exp_multiplier = config.get("exp_multiplier", 1.5)
        self.max_level = config.get("max_level", 100)
    
    def calculate_exp_for_level(self, level: int) -> int:
        """Calcula la experiencia necesaria para un nivel."""
        if level <= 1:
            return 0
        return int(self.base_exp * (self.exp_multiplier ** (level - 2)))
    
    def calculate_total_exp_for_level(self, level: int) -> int:
        """Calcula la experiencia total necesaria para alcanzar un nivel."""
        total = 0
        for i in range(2, level + 1):
            total += self.calculate_exp_for_level(i)
        return total
    
    def calculate_level_from_exp(self, experience: int) -> int:
        """Calcula el nivel basado en la experiencia total."""
        level = 1
        total_exp_needed = 0
        
        while level < self.max_level:
            next_level_exp = self.calculate_exp_for_level(level + 1)
            if total_exp_needed + next_level_exp > experience:
                break
            total_exp_needed += next_level_exp
            level += 1
        
        return level
    
    def get_level_progress(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Obtiene información del progreso de nivel."""
        current_level = user_profile.level
        current_exp = user_profile.experience
        
        # Experiencia necesaria para el nivel actual
        exp_for_current = self.calculate_total_exp_for_level(current_level)
        
        # Experiencia necesaria para el siguiente nivel
        exp_for_next = self.calculate_total_exp_for_level(current_level + 1)
        
        # Progreso en el nivel actual
        exp_in_current_level = current_exp - exp_for_current
        exp_needed_for_next = exp_for_next - exp_for_current
        
        progress_percentage = (exp_in_current_level / exp_needed_for_next) * 100 if exp_needed_for_next > 0 else 100
        
        return {
            "current_level": current_level,
            "current_exp": current_exp,
            "exp_in_current_level": exp_in_current_level,
            "exp_needed_for_next": exp_needed_for_next,
            "progress_percentage": min(100, progress_percentage),
            "next_level": current_level + 1 if current_level < self.max_level else current_level
        }
    
    def add_experience(self, user_profile: UserProfile, exp_points: int) -> Dict[str, Any]:
        """Añade experiencia y verifica subidas de nivel."""
        old_level = user_profile.level
        user_profile.experience += exp_points
        
        # Calcular nuevo nivel
        new_level = self.calculate_level_from_exp(user_profile.experience)
        
        level_up_info = {
            "exp_gained": exp_points,
            "level_up": False,
            "old_level": old_level,
            "new_level": new_level,
            "levels_gained": 0
        }
        
        if new_level > old_level:
            user_profile.level = new_level
            level_up_info["level_up"] = True
            level_up_info["levels_gained"] = new_level - old_level
            
            logger.info(f"Usuario {user_profile.user_id} subió al nivel {new_level}")
        
        return level_up_info

class GamificationEngine:
    """Motor principal de gamificación."""
    
    def __init__(self, config_path: str = None):
        # Cargar configuración
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = self._get_default_config()
        
        # Inicializar componentes
        self.points_calculator = PointsCalculator(self.config.get("points", {}))
        self.achievement_manager = AchievementManager(self.config.get("achievements", {}))
        self.challenge_manager = ChallengeManager(self.config.get("challenges", {}))
        self.level_system = LevelSystem(self.config.get("levels", {}))
        
        # Almacenamiento de perfiles de usuario
        self.user_profiles = {}
        
        # Configuración de eventos
        self.event_handlers = {}
        
        logger.info("Motor de gamificación inicializado")
    
    def get_user_profile(self, user_id: str) -> UserProfile:
        """Obtiene o crea el perfil de gamificación de un usuario."""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(user_id=user_id)
        
        return self.user_profiles[user_id]
    
    def record_activity(self, user_id: str, activity: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Registra una actividad del usuario y actualiza gamificación."""
        context = context or {}
        user_profile = self.get_user_profile(user_id)
        
        # Actualizar última actividad
        user_profile.last_activity = time.time()
        
        # Calcular puntos
        points_earned = self.points_calculator.calculate_points(activity, context)
        user_profile.total_points += points_earned
        
        # Actualizar estadísticas
        self._update_user_statistics(user_profile, activity, context)
        
        # Añadir experiencia
        exp_gained = points_earned // 2  # Convertir puntos a experiencia
        level_info = self.level_system.add_experience(user_profile, exp_gained)
        
        # Verificar logros
        activity_data = user_profile.statistics.copy()
        activity_data.update(context)
        newly_unlocked = self.achievement_manager.check_achievements(user_profile, activity_data)
        
        # Actualizar progreso de desafíos
        completed_challenges = self.challenge_manager.update_challenge_progress(user_profile, activity_data)
        
        # Preparar respuesta
        result = {
            "points_earned": points_earned,
            "total_points": user_profile.total_points,
            "level_info": level_info,
            "newly_unlocked_achievements": [
                {
                    "id": achievement.id,
                    "name": achievement.name,
                    "description": achievement.description,
                    "points": achievement.points,
                    "rarity": achievement.rarity.value,
                    "icon": achievement.icon,
                    "unlock_message": achievement.unlock_message
                }
                for achievement in newly_unlocked
            ],
            "completed_challenges": [
                {
                    "id": challenge.id,
                    "name": challenge.name,
                    "description": challenge.description,
                    "rewards": challenge.rewards
                }
                for challenge in completed_challenges
            ],
            "current_level": user_profile.level,
            "current_exp": user_profile.experience
        }
        
        return result
    
    def _update_user_statistics(self, user_profile: UserProfile, activity: str, context: Dict[str, Any]) -> None:
        """Actualiza las estadísticas del usuario."""
        stats = user_profile.statistics
        
        # Incrementar contador de actividad
        stats[activity] = stats.get(activity, 0) + 1
        
        # Actualizar estadísticas específicas
        if activity == "message_sent":
            stats["messages_sent"] = stats.get("messages_sent", 0) + 1
        elif activity == "translation_used":
            stats["translations_used"] = stats.get("translations_used", 0) + 1
        elif activity == "voice_interaction":
            stats["voice_interactions"] = stats.get("voice_interactions", 0) + 1
        elif activity == "problem_solved":
            stats["problems_solved"] = stats.get("problems_solved", 0) + 1
        elif activity == "feature_discovered":
            stats["features_discovered"] = stats.get("features_discovered", 0) + 1
        elif activity == "feedback_given":
            stats["feedback_given"] = stats.get("feedback_given", 0) + 1
        
        # Actualizar racha de días consecutivos
        self._update_consecutive_days(user_profile)
        
        # Actualizar eficiencia si se proporciona
        if "efficiency_score" in context:
            self._update_efficiency_stats(user_profile, context["efficiency_score"])
    
    def _update_consecutive_days(self, user_profile: UserProfile) -> None:
        """Actualiza la racha de días consecutivos."""
        today = datetime.now().date()
        last_activity_date = datetime.fromtimestamp(user_profile.last_activity).date()
        
        if "last_activity_date" not in user_profile.statistics:
            user_profile.statistics["consecutive_days"] = 1
            user_profile.statistics["last_activity_date"] = today.isoformat()
        else:
            last_recorded_date = datetime.fromisoformat(user_profile.statistics["last_activity_date"]).date()
            
            if today == last_recorded_date:
                # Mismo día, no cambiar racha
                pass
            elif today == last_recorded_date + timedelta(days=1):
                # Día consecutivo
                user_profile.statistics["consecutive_days"] = user_profile.statistics.get("consecutive_days", 0) + 1
                user_profile.statistics["last_activity_date"] = today.isoformat()
            else:
                # Se rompió la racha
                user_profile.statistics["consecutive_days"] = 1
                user_profile.statistics["last_activity_date"] = today.isoformat()
    
    def _update_efficiency_stats(self, user_profile: UserProfile, efficiency_score: float) -> None:
        """Actualiza estadísticas de eficiencia."""
        stats = user_profile.statistics
        
        # Actualizar promedio de eficiencia
        current_avg = stats.get("average_efficiency", 0.0)
        total_sessions = stats.get("total_efficiency_sessions", 0)
        
        new_avg = ((current_avg * total_sessions) + efficiency_score) / (total_sessions + 1)
        stats["average_efficiency"] = new_avg
        stats["total_efficiency_sessions"] = total_sessions + 1
        
        # Actualizar racha de alta eficiencia
        if efficiency_score >= 0.85:
            stats["efficiency_streak"] = stats.get("efficiency_streak", 0) + 1
        else:
            stats["efficiency_streak"] = 0
    
    def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Obtiene el dashboard completo de gamificación del usuario."""
        user_profile = self.get_user_profile(user_id)
        
        # Información de nivel
        level_progress = self.level_system.get_level_progress(user_profile)
        
        # Logros recientes
        recent_achievements = [
            self.achievement_manager.achievements[achievement_id]
            for achievement_id in user_profile.achievements_unlocked[-5:]
            if achievement_id in self.achievement_manager.achievements
        ]
        
        # Desafíos disponibles
        available_challenges = self.challenge_manager.get_available_challenges(user_profile)
        
        # Estadísticas destacadas
        stats = user_profile.statistics
        highlighted_stats = {
            "messages_sent": stats.get("messages_sent", 0),
            "translations_used": stats.get("translations_used", 0),
            "consecutive_days": stats.get("consecutive_days", 0),
            "average_efficiency": round(stats.get("average_efficiency", 0.0), 2),
            "problems_solved": stats.get("problems_solved", 0)
        }
        
        # Ranking (simplificado)
        user_rank = self._calculate_user_rank(user_profile)
        
        return {
            "user_profile": {
                "user_id": user_profile.user_id,
                "level": user_profile.level,
                "experience": user_profile.experience,
                "total_points": user_profile.total_points,
                "active_title": user_profile.active_title,
                "achievements_count": len(user_profile.achievements_unlocked)
            },
            "level_progress": level_progress,
            "recent_achievements": [
                {
                    "id": achievement.id,
                    "name": achievement.name,
                    "description": achievement.description,
                    "icon": achievement.icon,
                    "rarity": achievement.rarity.value
                }
                for achievement in recent_achievements
            ],
            "available_challenges": [
                {
                    "id": challenge.id,
                    "name": challenge.name,
                    "description": challenge.description,
                    "difficulty": challenge.difficulty,
                    "time_remaining": max(0, challenge.end_time - time.time()),
                    "rewards": challenge.rewards
                }
                for challenge in available_challenges[:3]  # Top 3
            ],
            "statistics": highlighted_stats,
            "rank": user_rank,
            "titles": user_profile.titles,
            "next_milestone": self._get_next_milestone(user_profile)
        }
    
    def _calculate_user_rank(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Calcula el ranking del usuario (simplificado)."""
        # En una implementación real, esto consultaría una base de datos
        total_users = len(self.user_profiles)
        users_with_less_points = sum(1 for profile in self.user_profiles.values() 
                                   if profile.total_points < user_profile.total_points)
        
        rank = total_users - users_with_less_points
        percentile = (users_with_less_points / total_users * 100) if total_users > 0 else 0
        
        return {
            "rank": rank,
            "total_users": total_users,
            "percentile": round(percentile, 1),
            "tier": self._get_user_tier(percentile)
        }
    
    def _get_user_tier(self, percentile: float) -> str:
        """Determina el tier del usuario basado en percentil."""
        if percentile >= 95:
            return "Legendary"
        elif percentile >= 85:
            return "Epic"
        elif percentile >= 70:
            return "Rare"
        elif percentile >= 50:
            return "Uncommon"
        else:
            return "Common"
    
    def _get_next_milestone(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Obtiene el siguiente hito importante para el usuario."""
        # Verificar próximo nivel
        level_progress = self.level_system.get_level_progress(user_profile)
        
        # Verificar próximo logro
        next_achievement = None
        min_progress_needed = float('inf')
        
        for achievement_id, achievement in self.achievement_manager.achievements.items():
            if achievement_id in user_profile.achievements_unlocked:
                continue
            
            # Calcular progreso hacia este logro
            progress_needed = 0
            for req_key, req_value in achievement.requirements.items():
                current_value = user_profile.statistics.get(req_key, 0)
                if req_key == "level":
                    current_value = user_profile.level
                
                if current_value < req_value:
                    progress_needed += req_value - current_value
            
            if progress_needed < min_progress_needed:
                min_progress_needed = progress_needed
                next_achievement = achievement
        
        milestone = {
            "type": "level",
            "description": f"Alcanzar nivel {level_progress['next_level']}",
            "progress": level_progress["progress_percentage"],
            "reward": f"{self.level_system.calculate_exp_for_level(level_progress['next_level'])} puntos de experiencia"
        }
        
        if next_achievement and min_progress_needed < 50:  # Si está cerca de un logro
            milestone = {
                "type": "achievement",
                "description": f"Desbloquear '{next_achievement.name}'",
                "progress": max(0, 100 - (min_progress_needed / max(1, sum(next_achievement.requirements.values())) * 100)),
                "reward": f"{next_achievement.points} puntos + {next_achievement.name}"
            }
        
        return milestone
    
    def join_challenge(self, user_id: str, challenge_id: str) -> Dict[str, Any]:
        """Permite a un usuario unirse a un desafío."""
        user_profile = self.get_user_profile(user_id)
        success = self.challenge_manager.join_challenge(user_profile, challenge_id)
        
        if success:
            challenge = self.challenge_manager.active_challenges[challenge_id]
            return {
                "success": True,
                "message": f"Te has unido al desafío '{challenge.name}'",
                "challenge": {
                    "id": challenge.id,
                    "name": challenge.name,
                    "description": challenge.description,
                    "end_time": challenge.end_time,
                    "rewards": challenge.rewards
                }
            }
        else:
            return {
                "success": False,
                "message": "No se pudo unir al desafío"
            }
    
    def get_leaderboard(self, category: str = "points", limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene la tabla de líderes."""
        profiles = list(self.user_profiles.values())
        
        if category == "points":
            profiles.sort(key=lambda p: p.total_points, reverse=True)
        elif category == "level":
            profiles.sort(key=lambda p: (p.level, p.experience), reverse=True)
        elif category == "achievements":
            profiles.sort(key=lambda p: len(p.achievements_unlocked), reverse=True)
        elif category == "streak":
            profiles.sort(key=lambda p: p.statistics.get("consecutive_days", 0), reverse=True)
        
        leaderboard = []
        for i, profile in enumerate(profiles[:limit]):
            entry = {
                "rank": i + 1,
                "user_id": profile.user_id,
                "level": profile.level,
                "total_points": profile.total_points,
                "achievements_count": len(profile.achievements_unlocked),
                "active_title": profile.active_title
            }
            
            if category == "streak":
                entry["consecutive_days"] = profile.statistics.get("consecutive_days", 0)
            
            leaderboard.append(entry)
        
        return leaderboard
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto del motor de gamificación."""
        return {
            "points": {
                "base_points": {
                    "message_sent": 10,
                    "translation_used": 15,
                    "voice_interaction": 20,
                    "problem_solved": 50,
                    "feature_discovered": 25,
                    "daily_login": 5,
                    "feedback_given": 30
                },
                "multipliers": {
                    "streak_bonus": 1.5,
                    "weekend_bonus": 1.2,
                    "efficiency_bonus": 2.0
                }
            },
            "levels": {
                "base_exp": 100,
                "exp_multiplier": 1.5,
                "max_level": 100
            },
            "achievements": {
                "categories": ["usage", "learning", "efficiency", "exploration", "social", "milestone"]
            },
            "challenges": {
                "daily_reset_hour": 0,
                "max_active_challenges": 5
            }
        }

# Función de inicialización
def initialize_gamification_engine(config_path: str = None) -> GamificationEngine:
    """Inicializa y devuelve una instancia del motor de gamificación."""
    return GamificationEngine(config_path)

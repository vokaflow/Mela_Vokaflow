"""
Sistema de feedback para Vicky
Permite recopilar, almacenar y analizar la retroalimentación de los usuarios
"""
import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("vicky.feedback")

class FeedbackManager:
    """
    Gestiona la retroalimentación de los usuarios sobre las respuestas de Vicky
    """
    def __init__(self, feedback_dir=None):
        """
        Inicializa el gestor de feedback
        
        Args:
            feedback_dir: Directorio donde se almacenará la retroalimentación
        """
        if feedback_dir is None:
            feedback_dir = "/mnt/nvme_fast/vokaflow_data/feedback"
        
        self.feedback_dir = Path(feedback_dir)
        self._ensure_dirs()
        self.current_session = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info(f"Inicializando sistema de feedback. Sesión: {self.current_session}")
    
    def _ensure_dirs(self):
        """Asegura que los directorios necesarios existan"""
        os.makedirs(self.feedback_dir, exist_ok=True)
        os.makedirs(self.feedback_dir / "ratings", exist_ok=True)
        os.makedirs(self.feedback_dir / "comments", exist_ok=True)
        os.makedirs(self.feedback_dir / "issues", exist_ok=True)
    
    def save_rating(self, user_id, rating, interaction_id=None, context=None):
        """
        Guarda una valoración numérica para una respuesta
        
        Args:
            user_id: Identificador del usuario
            rating: Valoración (1-5)
            interaction_id: ID de la interacción relacionada
            context: Información adicional sobre la valoración
        
        Returns:
            bool: True si se guardó correctamente
        """
        if not 1 <= rating <= 5:
            logger.warning(f"Valoración fuera de rango: {rating}. Debe ser 1-5")
            return False
        
        timestamp = datetime.now().isoformat()
        rating_data = {
            "user_id": user_id,
            "rating": rating,
            "timestamp": timestamp,
            "interaction_id": interaction_id,
            "context": context or {}
        }
        
        try:
            filename = f"rating_{user_id}_{int(time.time())}.json"
            with open(self.feedback_dir / "ratings" / filename, 'w') as f:
                json.dump(rating_data, f, indent=2)
            logger.info(f"Valoración guardada: {rating}/5 por usuario {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error al guardar valoración: {e}")
            return False
    
    def save_comment(self, user_id, comment, interaction_id=None, category="general"):
        """
        Guarda un comentario de texto sobre Vicky
        
        Args:
            user_id: Identificador del usuario
            comment: Texto del comentario
            interaction_id: ID de la interacción relacionada
            category: Categoría del comentario (general, sugerencia, error)
        
        Returns:
            bool: True si se guardó correctamente
        """
        timestamp = datetime.now().isoformat()
        comment_data = {
            "user_id": user_id,
            "comment": comment,
            "timestamp": timestamp,
            "interaction_id": interaction_id,
            "category": category
        }
        
        try:
            filename = f"comment_{user_id}_{int(time.time())}.json"
            with open(self.feedback_dir / "comments" / filename, 'w') as f:
                json.dump(comment_data, f, indent=2)
            logger.info(f"Comentario guardado en categoría '{category}' por usuario {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error al guardar comentario: {e}")
            return False
    
    def report_issue(self, user_id, issue_description, severity="medium", interaction_id=None, context=None):
        """
        Registra un problema reportado por el usuario
        
        Args:
            user_id: Identificador del usuario
            issue_description: Descripción del problema
            severity: Gravedad del problema (low, medium, high, critical)
            interaction_id: ID de la interacción relacionada
            context: Información adicional sobre el problema
        
        Returns:
            bool: True si se guardó correctamente
        """
        timestamp = datetime.now().isoformat()
        issue_data = {
            "user_id": user_id,
            "description": issue_description,
            "severity": severity,
            "timestamp": timestamp,
            "interaction_id": interaction_id,
            "context": context or {},
            "status": "reported",
            "session": self.current_session
        }
        
        try:
            issue_id = f"issue_{user_id}_{int(time.time())}"
            filename = f"{issue_id}.json"
            with open(self.feedback_dir / "issues" / filename, 'w') as f:
                json.dump(issue_data, f, indent=2)
            logger.info(f"Problema reportado (ID: {issue_id}) con severidad {severity}")
            return True
        except Exception as e:
            logger.error(f"Error al reportar problema: {e}")
            return False
    
    def get_recent_feedback(self, limit=10, category="ratings"):
        """
        Obtiene la retroalimentación más reciente
        
        Args:
            limit: Número máximo de elementos a recuperar
            category: Tipo de feedback (ratings, comments, issues)
        
        Returns:
            list: Lista de elementos de retroalimentación
        """
        valid_categories = {"ratings", "comments", "issues"}
        if category not in valid_categories:
            logger.warning(f"Categoría inválida: {category}")
            return []
        
        try:
            feedback_path = self.feedback_dir / category
            files = sorted(feedback_path.glob("*.json"), key=os.path.getmtime, reverse=True)[:limit]
            
            feedback_items = []
            for file in files:
                with open(file, 'r') as f:
                    feedback_items.append(json.load(f))
            
            return feedback_items
        except Exception as e:
            logger.error(f"Error al recuperar feedback reciente: {e}")
            return []
    
    def get_average_rating(self, days=7):
        """
        Calcula la valoración promedio de los últimos días
        
        Args:
            days: Número de días a considerar
        
        Returns:
            float: Valoración promedio o None si no hay datos
        """
        try:
            # Obtener todos los archivos de valoración
            ratings_path = self.feedback_dir / "ratings"
            all_files = list(ratings_path.glob("*.json"))
            
            # Filtrar por fecha
            cutoff_time = time.time() - (days * 24 * 60 * 60)
            recent_files = [f for f in all_files if os.path.getmtime(f) >= cutoff_time]
            
            if not recent_files:
                return None
            
            # Calcular promedio
            total_rating = 0
            count = 0
            
            for file in recent_files:
                with open(file, 'r') as f:
                    data = json.load(f)
                    total_rating += data.get("rating", 0)
                    count += 1
            
            if count == 0:
                return None
                
            return round(total_rating / count, 2)
        except Exception as e:
            logger.error(f"Error al calcular valoración promedio: {e}")
            return None

# Instancia global para uso en toda la aplicación
feedback_manager = FeedbackManager()

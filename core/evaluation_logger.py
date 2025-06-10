import logging
import json
from datetime import datetime

class EvaluationLogger:
    def __init__(self, log_file_path="evaluation_log.jsonl"):
        self.log_file_path = log_file_path
        self.logger = logging.getLogger("EvaluationLogger")
        # Asegurar que el archivo exista o se cree vacío si no
        try:
            with open(self.log_file_path, 'a') as f:
                pass # Solo para crear el archivo si no existe
        except IOError as e:
            self.logger.error(f"Could not open or create log file {self.log_file_path}: {e}")


    def log_scenario_execution(self, scenario_details: dict, vicky_response: dict, manager_state: dict):
        """
        Logs the execution details of a test scenario.
        - scenario_details: The dictionary defining the test scenario.
        - vicky_response: The full response from VickyAI.process_message.
        - manager_state: Relevant state from PersonalityManager after processing.
                         (e.g., active_personalities, conflict/synergy info)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "scenario_id": scenario_details.get("scenario_id"),
            "scenario_description": scenario_details.get("description"),
            "user_input": scenario_details.get("user_input"),
            "context_provided": scenario_details.get("context"),
            "vicky_primary_personality": vicky_response.get("primary_personality"),
            "vicky_active_personalities": vicky_response.get("active_personalities"),
            "vicky_response_text": vicky_response.get("text"),
            "vicky_response_style": vicky_response.get("response_style"),
            "manager_active_personalities_detailed": manager_state.get("active_personalities_details", []),
            "manager_conflict_info": manager_state.get("last_conflict_resolution_info"),
            "manager_synergy_info": manager_state.get("last_synergy_applied_info"),
            "expected_outcomes": {
                "primary_personality": scenario_details.get("expected_primary_personality"),
                "active_personalities": scenario_details.get("expected_active_personalities"),
                "synergy_rule_triggered": scenario_details.get("expected_synergy_rule_triggered"),
                "conflict_rule_triggered": scenario_details.get("expected_conflict_rule_triggered")
            }
        }
        try:
            with open(self.log_file_path, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")
            self.logger.info(f"Logged execution for scenario: {scenario_details.get('scenario_id')}")
        except IOError as e:
            self.logger.error(f"Error writing to evaluation log for scenario {scenario_details.get('scenario_id')}: {e}")
        except TypeError as e:
            self.logger.error(f"TypeError during JSON serialization for scenario {scenario_details.get('scenario_id')}: {e}. Log entry: {log_entry}")


    def get_manager_snapshot(self, manager) -> dict:
        """
        Captures a snapshot of relevant PersonalityManager state for logging.
        """
        active_p_details = []
        # Acceder a self.active_personalities que es una lista de instancias PersonalityBase
        for p_instance in manager.active_personalities:
            if p_instance.activation_level > 0:
              active_p_details.append({
                  "name": p_instance.name,
                  "activation_level": round(p_instance.activation_level, 3),
                  "current_traits_summary": {k: round(v,2) for k,v in p_instance.current_traits.items()}
              })
        
        return {
            "active_personalities_details": active_p_details,
            "last_conflict_resolution_info": manager.last_conflict_resolution_info,
            "last_synergy_applied_info": manager.last_synergy_applied_info,
            "keyword_personality_scores_sample": dict(list(manager.keyword_personality_scores.items())[:5]) # Sample
        }

# Crear instancia global para importar
evaluation_logger = EvaluationLogger()

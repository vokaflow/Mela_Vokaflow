"""
Módulo de integración con SIEM para VokaFlow.

Este módulo proporciona funcionalidades para enviar eventos de seguridad
a sistemas SIEM (Security Information and Event Management).
"""

import os
import json
import time
import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configuración de logging
logger = logging.getLogger("vicky.security.siem")

class SIEMConnector:
    """
    Conector para sistemas SIEM.
    
    Permite enviar eventos de seguridad a diferentes plataformas SIEM
    para monitoreo centralizado y análisis de seguridad.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.siem_type = config.get("siem_type", "elastic")
        self.endpoint = config.get("endpoint", "")
        self.api_key = config.get("api_key", os.environ.get("VICKY_SIEM_API_KEY", ""))
        self.index_name = config.get("index_name", "vicky-security-events")
        self.batch_size = config.get("batch_size", 10)
        self.retry_attempts = config.get("retry_attempts", 3)
        self.retry_delay = config.get("retry_delay", 2)
        
        # Cola de eventos pendientes en caso de fallo
        self.pending_events = []
        
        # Verificar configuración
        if not self.endpoint:
            logger.warning("Endpoint SIEM no configurado")
        
        if not self.api_key:
            logger.warning("API Key SIEM no configurada")
    
    def send_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Envía un evento de seguridad al SIEM.
        
        Args:
            event_data: Datos del evento de seguridad
            
        Returns:
            bool: True si se envió correctamente, False en caso contrario
        """
        # Añadir metadatos adicionales
        enriched_event = self._enrich_event(event_data)
        
        # Intentar enviar el evento
        for attempt in range(self.retry_attempts):
            try:
                if self.siem_type == "elastic":
                    return self._send_to_elastic(enriched_event)
                elif self.siem_type == "splunk":
                    return self._send_to_splunk(enriched_event)
                elif self.siem_type == "azure_sentinel":
                    return self._send_to_azure_sentinel(enriched_event)
                elif self.siem_type == "custom_http":
                    return self._send_to_custom_http(enriched_event)
                else:
                    logger.error(f"Tipo de SIEM no soportado: {self.siem_type}")
                    return False
            except Exception as e:
                logger.error(f"Error al enviar evento a SIEM (intento {attempt+1}/{self.retry_attempts}): {str(e)}")
                time.sleep(self.retry_delay)
        
        # Si llegamos aquí, todos los intentos fallaron
        # Guardar evento para reintento posterior
        self.pending_events.append(enriched_event)
        
        # Si hay demasiados eventos pendientes, eliminar los más antiguos
        if len(self.pending_events) > 1000:
            self.pending_events = self.pending_events[-1000:]
        
        return False
    
    def send_batch(self, events: List[Dict[str, Any]]) -> bool:
        """
        Envía un lote de eventos al SIEM.
        
        Args:
            events: Lista de eventos de seguridad
            
        Returns:
            bool: True si todos se enviaron correctamente, False en caso contrario
        """
        if not events:
            return True
        
        # Enriquecer todos los eventos
        enriched_events = [self._enrich_event(event) for event in events]
        
        # Enviar en lotes según la configuración
        success = True
        for i in range(0, len(enriched_events), self.batch_size):
            batch = enriched_events[i:i+self.batch_size]
            
            if self.siem_type == "elastic":
                batch_success = self._send_batch_to_elastic(batch)
            elif self.siem_type == "splunk":
                batch_success = self._send_batch_to_splunk(batch)
            elif self.siem_type == "azure_sentinel":
                batch_success = self._send_batch_to_azure_sentinel(batch)
            elif self.siem_type == "custom_http":
                batch_success = self._send_batch_to_custom_http(batch)
            else:
                logger.error(f"Tipo de SIEM no soportado para envío por lotes: {self.siem_type}")
                batch_success = False
            
            success = success and batch_success
        
        return success
    
    def retry_pending(self) -> int:
        """
        Reintenta enviar eventos pendientes.
        
        Returns:
            int: Número de eventos enviados correctamente
        """
        if not self.pending_events:
            return 0
        
        logger.info(f"Reintentando envío de {len(self.pending_events)} eventos pendientes")
        
        # Copiar lista para evitar modificaciones durante la iteración
        events_to_retry = self.pending_events.copy()
        self.pending_events = []
        
        # Enviar en lotes
        success_count = 0
        for i in range(0, len(events_to_retry), self.batch_size):
            batch = events_to_retry[i:i+self.batch_size]
            
            if self.send_batch(batch):
                success_count += len(batch)
            else:
                # Volver a añadir los eventos fallidos a la cola
                self.pending_events.extend(batch)
        
        logger.info(f"Reintento completado: {success_count}/{len(events_to_retry)} eventos enviados")
        return success_count
    
    def _enrich_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enriquece un evento con metadatos adicionales."""
        enriched = event_data.copy()
        
        # Añadir timestamp ISO si no existe
        if "timestamp" not in enriched:
            enriched["timestamp"] = datetime.utcnow().isoformat()
        
        # Añadir información del entorno
        enriched["environment"] = self.config.get("environment", "production")
        enriched["application"] = "vicky"
        enriched["component"] = "security"
        
        # Añadir versión
        enriched["version"] = self.config.get("version", "1.0.0")
        
        return enriched
    
    def _send_to_elastic(self, event: Dict[str, Any]) -> bool:
        """Envía un evento a Elasticsearch."""
        if not self.endpoint or not self.api_key:
            return False
        
        url = f"{self.endpoint}/{self.index_name}/_doc"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"ApiKey {self.api_key}"
        }
        
        try:
            response = requests.post(url, headers=headers, json=event)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error al enviar a Elasticsearch: {str(e)}")
            return False
    
    def _send_batch_to_elastic(self, events: List[Dict[str, Any]]) -> bool:
        """Envía un lote de eventos a Elasticsearch usando la API _bulk."""
        if not self.endpoint or not self.api_key:
            return False
        
        url = f"{self.endpoint}/_bulk"
        headers = {
            "Content-Type": "application/x-ndjson",
            "Authorization": f"ApiKey {self.api_key}"
        }
        
        # Construir payload para la API _bulk
        payload = ""
        for event in events:
            action = {"index": {"_index": self.index_name}}
            payload += json.dumps(action) + "\n"
            payload += json.dumps(event) + "\n"
        
        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            
            # Verificar respuesta
            result = response.json()
            if result.get("errors", False):
                logger.error(f"Errores al enviar lote a Elasticsearch: {result}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error al enviar lote a Elasticsearch: {str(e)}")
            return False
    
    def _send_to_splunk(self, event: Dict[str, Any]) -> bool:
        """Envía un evento a Splunk."""
        if not self.endpoint or not self.api_key:
            return False
        
        url = f"{self.endpoint}/services/collector"
        headers = {
            "Authorization": f"Splunk {self.api_key}"
        }
        
        # Formato esperado por Splunk
        payload = {
            "event": event,
            "sourcetype": "vicky:security",
            "source": "vicky_security_module"
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error al enviar a Splunk: {str(e)}")
            return False
    
    def _send_batch_to_splunk(self, events: List[Dict[str, Any]]) -> bool:
        """Envía un lote de eventos a Splunk."""
        if not self.endpoint or not self.api_key:
            return False
        
        url = f"{self.endpoint}/services/collector"
        headers = {
            "Authorization": f"Splunk {self.api_key}"
        }
        
        # Construir payload para Splunk
        payload = ""
        for event in events:
            event_payload = {
                "event": event,
                "sourcetype": "vicky:security",
                "source": "vicky_security_module"
            }
            payload += json.dumps(event_payload) + "\n"
        
        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error al enviar lote a Splunk: {str(e)}")
            return False
    
    def _send_to_azure_sentinel(self, event: Dict[str, Any]) -> bool:
        """Envía un evento a Azure Sentinel."""
        if not self.endpoint or not self.api_key:
            return False
        
        # Azure Sentinel utiliza Log Analytics API
        url = f"{self.endpoint}/api/logs"
        headers = {
            "Content-Type": "application/json",
            "Log-Type": "VickySecurityEvents",
            "x-api-key": self.api_key
        }
        
        try:
            response = requests.post(url, headers=headers, json=[event])
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error al enviar a Azure Sentinel: {str(e)}")
            return False
    
    def _send_batch_to_azure_sentinel(self, events: List[Dict[str, Any]]) -> bool:
        """Envía un lote de eventos a Azure Sentinel."""
        if not self.endpoint or not self.api_key:
            return False
        
        # Azure Sentinel utiliza Log Analytics API
        url = f"{self.endpoint}/api/logs"
        headers = {
            "Content-Type": "application/json",
            "Log-Type": "VickySecurityEvents",
            "x-api-key": self.api_key
        }
        
        try:
            response = requests.post(url, headers=headers, json=events)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error al enviar lote a Azure Sentinel: {str(e)}")
            return False
    
    def _send_to_custom_http(self, event: Dict[str, Any]) -> bool:
        """Envía un evento a un endpoint HTTP personalizado."""
        if not self.endpoint:
            return False
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Añadir API key si está configurada
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            response = requests.post(self.endpoint, headers=headers, json=event)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error al enviar a endpoint personalizado: {str(e)}")
            return False
    
    def _send_batch_to_custom_http(self, events: List[Dict[str, Any]]) -> bool:
        """Envía un lote de eventos a un endpoint HTTP personalizado."""
        if not self.endpoint:
            return False
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Añadir API key si está configurada
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            response = requests.post(self.endpoint, headers=headers, json=events)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error al enviar lote a endpoint personalizado: {str(e)}")
            return False

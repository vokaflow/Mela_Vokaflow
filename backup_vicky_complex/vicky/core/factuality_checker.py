"""
Verificador de Factualidad para Vicky

Este módulo implementa un sistema para verificar y corregir la factualidad
de las respuestas generadas, asegurando que la información proporcionada
sea precisa y confiable.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Set, Tuple
import json
import time

from .model_manager import ModelManager
from .context import Context

logger = logging.getLogger(__name__)

class FactualityChecker:
    """
    Sistema para verificar y corregir la factualidad de las respuestas.
    
    Utiliza modelos de verificación y fuentes de conocimiento para
    asegurar que las respuestas sean precisas y confiables.
    """
    
    def __init__(self, model_manager: ModelManager, config: Dict[str, Any] = None):
        """
        Inicializa el verificador de factualidad.
        
        Args:
            model_manager: Gestor de modelos de IA
            config: Configuración adicional (opcional)
        """
        self.model_manager = model_manager
        self.config = config or {}
        
        # Configuraciones
        self.verification_threshold = self.config.get("verification_threshold", 0.7)
        self.max_corrections = self.config.get("max_corrections", 3)
        self.enable_auto_correction = self.config.get("enable_auto_correction", True)
        self.verification_model_name = self.config.get("verification_model", "language")
        
        # Cargar modelo de verificación
        self.verification_model = self.model_manager.get_model(self.verification_model_name)
        if not self.verification_model:
            logger.warning("No se pudo cargar el modelo de verificación de factualidad")
        
        logger.info("Verificador de factualidad inicializado")
    
    def verify_and_correct(self, response: str, query: str, context: Context) -> str:
        """
        Verifica y corrige la factualidad de una respuesta.
        
        Args:
            response: Respuesta a verificar
            query: Consulta original del usuario
            context: Contexto de la consulta
            
        Returns:
            Respuesta verificada y corregida si es necesario
        """
        # Si no hay modelo de verificación, devolver la respuesta original
        if not self.verification_model:
            logger.warning("Verificación de factualidad omitida: modelo no disponible")
            return response
        
        try:
            # Extraer afirmaciones factuales
            factual_claims = self._extract_factual_claims(response)
            
            if not factual_claims:
                logger.info("No se encontraron afirmaciones factuales para verificar")
                return response
            
            # Verificar cada afirmación
            verification_results = self._verify_claims(factual_claims, context)
            
            # Calcular puntuación general de factualidad
            factuality_score = self._calculate_factuality_score(verification_results)
            
            # Almacenar puntuación en el contexto para uso posterior
            context.set_metadata("factuality_score", factuality_score)
            
            # Si la puntuación está por encima del umbral, devolver respuesta original
            if factuality_score >= self.verification_threshold:
                logger.info(f"Respuesta verificada con puntuación de factualidad: {factuality_score:.2f}")
                return response
            
            # Corregir afirmaciones incorrectas si está habilitado
            if self.enable_auto_correction:
                corrected_response = self._correct_inaccuracies(
                    response, verification_results, query, context
                )
                logger.info("Respuesta corregida para mejorar factualidad")
                return corrected_response
            else:
                # Añadir advertencia sobre posibles inexactitudes
                warning = "\n\n*Nota: Esta respuesta puede contener algunas inexactitudes. " \
                         "Verifica la información con fuentes adicionales.*"
                return response + warning
                
        except Exception as e:
            logger.error(f"Error en verificación de factualidad: {e}")
            return response
    
    def _extract_factual_claims(self, text: str) -> List[str]:
        """
        Extrae afirmaciones factuales de un texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Lista de afirmaciones factuales
        """
        # Dividir en oraciones
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Filtrar oraciones que parecen afirmaciones factuales
        factual_claims = []
        
        for sentence in sentences:
            # Ignorar oraciones muy cortas
            if len(sentence.split()) < 5:
                continue
                
            # Ignorar preguntas
            if sentence.endswith('?'):
                continue
                
            # Ignorar opiniones explícitas
            opinion_markers = ["creo que", "pienso que", "en mi opinión", "considero que"]
            if any(marker in sentence.lower() for marker in opinion_markers):
                continue
                
            # Ignorar sugerencias
            suggestion_markers = ["podrías", "deberías", "te recomiendo", "te sugiero"]
            if any(marker in sentence.lower() for marker in suggestion_markers):
                continue
            
            # Añadir como afirmación factual
            factual_claims.append(sentence)
        
        # Limitar a un número razonable de afirmaciones para verificar
        max_claims = self.config.get("max_claims_to_verify", 5)
        return factual_claims[:max_claims]
    
    def _verify_claims(self, claims: List[str], context: Context) -> Dict[str, Dict[str, Any]]:
        """
        Verifica la factualidad de una lista de afirmaciones.
        
        Args:
            claims: Lista de afirmaciones a verificar
            context: Contexto de la consulta
            
        Returns:
            Diccionario con resultados de verificación
        """
        verification_results = {}
        
        for claim in claims:
            # Preparar prompt para verificación
            verification_prompt = self._create_verification_prompt(claim, context)
            
            # Generar verificación
            verification_result = self.verification_model.generate(verification_prompt)
            
            # Analizar resultado
            try:
                # Extraer puntuación de factualidad (0.0-1.0)
                factuality_score = self._extract_factuality_score(verification_result)
                
                # Extraer razón o explicación
                explanation = self._extract_explanation(verification_result)
                
                # Extraer corrección sugerida si la hay
                correction = self._extract_correction(verification_result)
                
                # Almacenar resultados
                verification_results[claim] = {
                    "score": factuality_score,
                    "explanation": explanation,
                    "correction": correction
                }
                
            except Exception as e:
                logger.error(f"Error al analizar resultado de verificación: {e}")
                verification_results[claim] = {
                    "score": 0.5,  # Valor neutral por defecto
                    "explanation": "Error en análisis de verificación",
                    "correction": None
                }
        
        return verification_results
    
    def _create_verification_prompt(self, claim: str, context: Context) -> str:
        """
        Crea un prompt para verificar una afirmación.
        
        Args:
            claim: Afirmación a verificar
            context: Contexto de la consulta
            
        Returns:
            Prompt para verificación
        """
        # Obtener información relevante del contexto
        query = context.get_metadata("query", "")
        
        # Crear prompt
        prompt = f"""
        Verifica la factualidad de la siguiente afirmación:
        
        Afirmación: "{claim}"
        
        Contexto de la consulta: "{query}"
        
        Por favor, evalúa si esta afirmación es factualmente correcta.
        
        Formato de respuesta:
        - Puntuación (0.0-1.0): [puntuación numérica donde 0.0 es completamente falso y 1.0 es completamente verdadero]
        - Explicación: [explicación de la evaluación]
        - Corrección (si es necesaria): [versión corregida de la afirmación]
        """
        
        return prompt
    
    def _extract_factuality_score(self, verification_result: str) -> float:
        """
        Extrae la puntuación de factualidad del resultado de verificación.
        
        Args:
            verification_result: Resultado de la verificación
            
        Returns:
            Puntuación de factualidad (0.0-1.0)
        """
        # Buscar patrón de puntuación
        score_pattern = r"Puntuación $$0\.0-1\.0$$: (\d+\.\d+)"
        match = re.search(score_pattern, verification_result)
        
        if match:
            try:
                score = float(match.group(1))
                return max(0.0, min(1.0, score))  # Limitar al rango 0.0-1.0
            except ValueError:
                pass
        
        # Si no se encuentra un patrón claro, intentar inferir
        if "completamente verdadero" in verification_result.lower():
            return 1.0
        elif "mayormente verdadero" in verification_result.lower():
            return 0.8
        elif "parcialmente verdadero" in verification_result.lower():
            return 0.6
        elif "dudoso" in verification_result.lower():
            return 0.4
        elif "mayormente falso" in verification_result.lower():
            return 0.2
        elif "completamente falso" in verification_result.lower():
            return 0.0
        
        # Valor por defecto si no se puede determinar
        return 0.5
    
    def _extract_explanation(self, verification_result: str) -> str:
        """
        Extrae la explicación del resultado de verificación.
        
        Args:
            verification_result: Resultado de la verificación
            
        Returns:
            Explicación de la verificación
        """
        # Buscar patrón de explicación
        explanation_pattern = r"Explicación: (.*?)(?:\n- Corrección|\Z)"
        match = re.search(explanation_pattern, verification_result, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        # Si no se encuentra un patrón claro, devolver el resultado completo
        return verification_result
    
    def _extract_correction(self, verification_result: str) -> Optional[str]:
        """
        Extrae la corrección sugerida del resultado de verificación.
        
        Args:
            verification_result: Resultado de la verificación
            
        Returns:
            Corrección sugerida o None si no hay
        """
        # Buscar patrón de corrección
        correction_pattern = r"Corrección(?:\s+$$si es necesaria$$)?: (.*?)(?:\n|\Z)"
        match = re.search(correction_pattern, verification_result, re.DOTALL)
        
        if match:
            correction = match.group(1).strip()
            # Si la corrección indica que no es necesaria, devolver None
            if correction.lower() in ["no es necesaria", "n/a", "ninguna"]:
                return None
            return correction
        
        return None
    
    def _calculate_factuality_score(self, verification_results: Dict[str, Dict[str, Any]]) -> float:
        """
        Calcula una puntuación general de factualidad.
        
        Args:
            verification_results: Resultados de verificación
            
        Returns:
            Puntuación general de factualidad (0.0-1.0)
        """
        if not verification_results:
            return 0.5  # Valor neutral por defecto
        
        # Calcular promedio ponderado de puntuaciones
        total_score = 0.0
        total_weight = 0.0
        
        for claim, result in verification_results.items():
            # Dar más peso a afirmaciones más largas (potencialmente más importantes)
            weight = len(claim.split())
            score = result["score"]
            
            total_score += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.5
        
        return total_score / total_weight
    
    def _correct_inaccuracies(self, 
                            response: str, 
                            verification_results: Dict[str, Dict[str, Any]],
                            query: str,
                            context: Context) -> str:
        """
        Corrige inexactitudes en la respuesta.
        
        Args:
            response: Respuesta original
            verification_results: Resultados de verificación
            query: Consulta original
            context: Contexto de la consulta
            
        Returns:
            Respuesta corregida
        """
        corrected_response = response
        corrections_made = 0
        
        # Ordenar afirmaciones por puntuación (de menor a mayor)
        sorted_claims = sorted(
            verification_results.items(),
            key=lambda x: x[1]["score"]
        )
        
        # Corregir las afirmaciones menos precisas primero
        for claim, result in sorted_claims:
            # Solo corregir si la puntuación está por debajo del umbral
            if result["score"] >= self.verification_threshold:
                continue
                
            # Solo corregir si hay una corrección disponible
            if not result["correction"]:
                continue
                
            # Limitar número de correcciones
            if corrections_made >= self.max_corrections:
                break
                
            # Reemplazar la afirmación con su corrección
            corrected_response = corrected_response.replace(claim, result["correction"])
            corrections_made += 1
        
        # Si se hicieron correcciones, añadir nota
        if corrections_made > 0:
            note = "\n\n*Nota: Esta respuesta ha sido revisada para mejorar su precisión factual.*"
            corrected_response += note
        
        return corrected_response

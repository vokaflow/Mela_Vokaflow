"""
Analizador de Intenciones para el Motor Dual-Hemisferio
------------------------------------------------------

Este módulo implementa un sistema avanzado de análisis de intenciones
que clasifica las consultas de los usuarios para determinar la distribución
óptima de procesamiento entre los hemisferios técnico y emocional.

Características principales:
- Análisis semántico profundo de consultas
- Extracción de entidades y conceptos clave
- Clasificación multidimensional de intenciones
- Integración con sistema de contexto conversacional
- Optimización mediante caché selectiva
- Métricas de confianza y precisión

Autor: Equipo VokaFlow
Versión: 2.0.0
"""

import logging
import re
import json
from typing import Dict, Any, List, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
import traceback
import time
from collections import Counter, defaultdict
import hashlib

# Importaciones internas
from ..utils.performance_metrics import track_performance
from ..core.selective_cache import SelectiveCache, CachePolicy

logger = logging.getLogger("vicky.intent_parser")

# Configuración del caché
CACHE_ENABLED = True
CACHE_TTL = 3600  # 1 hora
CACHE_MAX_SIZE = 1000

@dataclass
class Entity:
    """
    Entidad extraída del texto.
    
    Representa un elemento semántico identificado en el texto del usuario,
    como URLs, rutas de archivo, comandos, expresiones emocionales, etc.
    
    Attributes:
        type: Tipo de entidad (url, path, code_block, emotion, etc.)
        value: Valor textual de la entidad
        start: Posición inicial en el texto original
        end: Posición final en el texto original
        confidence: Nivel de confianza en la extracción (0.0-1.0)
        metadata: Información adicional específica del tipo de entidad
    """
    type: str
    value: str
    start: int
    end: int
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validación después de la inicialización."""
        if not 0 <= self.confidence <= 1.0:
            self.confidence = max(0.0, min(self.confidence, 1.0))
            logger.warning(f"Confianza ajustada a rango válido: {self.confidence}")


@dataclass
class IntentAnalysisResult:
    """
    Resultado del análisis de intención.
    
    Contiene la clasificación completa de la consulta del usuario,
    incluyendo pesos para cada hemisferio, entidades extraídas,
    y métricas de confianza.
    
    Attributes:
        query_type: Tipo principal de consulta (technical, emotional, creative, factual, general)
        entities: Lista de entidades extraídas del texto
        technical_weight: Peso para procesamiento técnico (0.0-1.0)
        emotional_weight: Peso para procesamiento emocional (0.0-1.0)
        confidence: Confianza en el análisis (0.0-1.0)
        requires_code: Indica si la consulta requiere generación de código
        requires_creativity: Indica si la consulta requiere respuesta creativa
        requires_factual_accuracy: Indica si la consulta requiere precisión factual
        context_relevance: Métricas de relevancia contextual
        subtypes: Subtipos de consulta con sus pesos
        processing_time: Tiempo de procesamiento en milisegundos
        cache_hit: Indica si el resultado proviene del caché
    """
    query_type: str  # technical, emotional, creative, factual, general
    entities: List[Entity] = field(default_factory=list)
    technical_weight: float = 0.5  # Peso para procesamiento técnico (0.0-1.0)
    emotional_weight: float = 0.5  # Peso para procesamiento emocional (0.0-1.0)
    confidence: float = 0.0  # Confianza en el análisis (0.0-1.0)
    requires_code: bool = False
    requires_creativity: bool = False
    requires_factual_accuracy: bool = False
    context_relevance: Dict[str, float] = field(default_factory=dict)
    subtypes: Dict[str, float] = field(default_factory=dict)
    processing_time: float = 0.0
    cache_hit: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el resultado a diccionario para serialización.
        
        Returns:
            Dict: Representación en diccionario del resultado
        """
        return {
            "query_type": self.query_type,
            "entities": [
                {
                    "type": e.type,
                    "value": e.value,
                    "start": e.start,
                    "end": e.end,
                    "confidence": e.confidence,
                    "metadata": e.metadata
                } for e in self.entities
            ],
            "technical_weight": self.technical_weight,
            "emotional_weight": self.emotional_weight,
            "confidence": self.confidence,
            "requires_code": self.requires_code,
            "requires_creativity": self.requires_creativity,
            "requires_factual_accuracy": self.requires_factual_accuracy,
            "context_relevance": self.context_relevance,
            "subtypes": self.subtypes,
            "processing_time": self.processing_time,
            "cache_hit": self.cache_hit
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IntentAnalysisResult':
        """
        Crea una instancia desde un diccionario.
        
        Args:
            data: Diccionario con datos del resultado
            
        Returns:
            IntentAnalysisResult: Nueva instancia
        """
        entities = [
            Entity(
                type=e["type"],
                value=e["value"],
                start=e["start"],
                end=e["end"],
                confidence=e["confidence"],
                metadata=e["metadata"]
            ) for e in data.get("entities", [])
        ]
        
        return cls(
            query_type=data["query_type"],
            entities=entities,
            technical_weight=data["technical_weight"],
            emotional_weight=data["emotional_weight"],
            confidence=data["confidence"],
            requires_code=data["requires_code"],
            requires_creativity=data["requires_creativity"],
            requires_factual_accuracy=data["requires_factual_accuracy"],
            context_relevance=data.get("context_relevance", {}),
            subtypes=data.get("subtypes", {}),
            processing_time=data.get("processing_time", 0.0),
            cache_hit=data.get("cache_hit", False)
        )


class IntentParser:
    """
    Analizador avanzado de intenciones para el Motor Dual-Hemisferio.
    
    Esta clase implementa un sistema de análisis que:
    1. Clasifica consultas en categorías (técnica, emocional, creativa, etc.)
    2. Extrae entidades relevantes (código, URLs, rutas, etc.)
    3. Determina la distribución óptima de pesos entre hemisferios
    4. Identifica requisitos específicos (código, creatividad, precisión)
    5. Analiza el contexto conversacional para mejorar la precisión
    6. Utiliza caché selectiva para optimizar el rendimiento
    
    El analizador combina técnicas de:
    - Análisis léxico y sintáctico
    - Procesamiento semántico con embeddings
    - Análisis contextual de la conversación
    - Heurísticas específicas por dominio
    """
    
    def __init__(self, embedding_model=None, context=None, cache_manager=None):
        """
        Inicializa el analizador de intenciones.
        
        Args:
            embedding_model: Modelo de embeddings para análisis semántico (opcional)
            context: Sistema de contexto conversacional (opcional)
            cache_manager: Gestor de caché para optimización (opcional)
        """
        self.embedding_model = embedding_model
        self.context = context
        
        # Inicializar caché si está habilitado
        self.cache = None
        if CACHE_ENABLED:
            if cache_manager:
                self.cache = cache_manager.get_cache("intent_parser")
            else:
                self.cache = SelectiveCache(
                    name="intent_parser",
                    max_size=CACHE_MAX_SIZE,
                    ttl=CACHE_TTL,
                    policy=CachePolicy.LRU
                )
        
        # Diccionarios de palabras clave por categoría
        self._init_keyword_dictionaries()
        
        # Patrones de expresiones regulares precompilados
        self._compile_regex_patterns()
        
        # Contadores para estadísticas
        self.stats = {
            "total_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_processing_time": 0.0,
            "query_types": Counter()
        }
        
        logger.info("Analizador de intenciones v2.0 inicializado")
    
    def _init_keyword_dictionaries(self):
        """
        Inicializa diccionarios de palabras clave por categoría.
        
        Define conjuntos de palabras clave para diferentes categorías
        de análisis, incluyendo técnicas, emocionales, creativas, etc.
        """
        # Palabras clave técnicas
        self.technical_keywords = {
            # Programación y desarrollo
            "código", "programa", "función", "error", "bug", "implementar",
            "desarrollar", "optimizar", "algoritmo", "script", "api",
            "base de datos", "sql", "python", "javascript", "html", "css",
            "framework", "biblioteca", "compilar", "ejecutar", "depurar",
            "terminal", "servidor", "cliente", "red", "protocolo", "http",
            "configurar", "instalar", "desplegar", "docker", "kubernetes",
            "git", "github", "gitlab", "aws", "azure", "gcp", "cloud",
            "linux", "windows", "mac", "unix", "bash", "shell", "comando",
            
            # Matemáticas y ciencias
            "matemáticas", "cálculo", "álgebra", "geometría", "estadística",
            "probabilidad", "física", "química", "biología", "fórmula",
            "ecuación", "teorema", "hipótesis", "experimento", "análisis",
            
            # Tecnología
            "hardware", "software", "dispositivo", "sistema", "aplicación",
            "móvil", "web", "internet", "wifi", "bluetooth", "usb", "cpu",
            "gpu", "ram", "disco", "ssd", "hdd", "monitor", "teclado", "ratón"
        }
        
        # Palabras clave emocionales/creativas
        self.emotional_keywords = {
            # Emociones
            "siento", "sentir", "emoción", "triste", "feliz", "enojado",
            "frustrado", "ansioso", "preocupado", "miedo", "esperanza",
            "amor", "odio", "relación", "amistad", "familia", "pareja",
            "conflicto", "resolver", "ayuda", "consejo", "opinión",
            
            # Creatividad
            "creativo", "idea", "inspiración", "diseño", "arte", "música",
            "escribir", "historia", "poema", "canción", "filosofía",
            
            # Sociedad y humanidades
            "ética", "moral", "valores", "cultura", "sociedad", "política",
            "religión", "espiritualidad", "meditación", "bienestar",
            "psicología", "comportamiento", "mente", "conciencia",
            
            # Expresiones personales
            "pienso", "creo", "opino", "sueño", "deseo", "quiero",
            "necesito", "me gusta", "prefiero", "me encanta", "odio"
        }
        
        # Palabras clave para consultas que requieren código
        self.code_keywords = {
            "código", "implementar", "programar", "función", "clase", "método",
            "algoritmo", "script", "desarrollar", "implementación", "ejemplo de código",
            "snippet", "muestra", "cómo hacer", "cómo implementar", "cómo programar",
            "escribe", "genera", "crea un programa", "solución en código",
            "pseudocódigo", "estructura de datos", "optimiza", "refactoriza",
            "depura", "corrige", "mejora", "completa", "termina"
        }
        
        # Palabras clave para consultas que requieren creatividad
        self.creativity_keywords = {
            "creativo", "innovador", "original", "idea", "inspiración", "diseño",
            "imaginar", "crear", "inventar", "alternativa", "solución creativa",
            "enfoque diferente", "nuevo enfoque", "perspectiva", "brainstorming",
            "historia", "cuento", "narrativa", "poema", "letra", "canción",
            "metáfora", "analogía", "concepto", "visión", "estilo", "estética",
            "artístico", "expresivo", "imaginativo", "único", "diferente"
        }
        
        # Palabras clave para consultas que requieren precisión factual
        self.factual_keywords = {
            "exactamente", "precisamente", "datos", "estadísticas", "fecha", "historia",
            "hecho", "verdad", "evidencia", "prueba", "estudio", "investigación",
            "científico", "académico", "publicado", "verificado", "confirmado",
            "fuente", "referencia", "cita", "autor", "publicación", "journal",
            "paper", "artículo", "libro", "documento", "informe", "análisis",
            "revisión", "meta-análisis", "encuesta", "censo", "medición"
        }
        
        # Subtipos de consultas técnicas
        self.technical_subtypes = {
            "programming": {
                "código", "programación", "función", "clase", "método", "algoritmo",
                "variable", "objeto", "instancia", "herencia", "polimorfismo",
                "encapsulación", "abstracción", "interfaz", "implementación"
            },
            "data_science": {
                "datos", "análisis", "estadística", "machine learning", "modelo",
                "predicción", "clasificación", "regresión", "clustering", "dataset",
                "entrenamiento", "validación", "prueba", "precisión", "recall"
            },
            "infrastructure": {
                "servidor", "cloud", "aws", "azure", "gcp", "kubernetes", "docker",
                "contenedor", "virtualización", "red", "seguridad", "firewall",
                "balanceador", "escalabilidad", "alta disponibilidad", "redundancia"
            },
            "database": {
                "base de datos", "sql", "nosql", "tabla", "consulta", "índice",
                "transacción", "acid", "join", "relación", "entidad", "atributo",
                "clave primaria", "clave foránea", "normalización", "desnormalización"
            }
        }
        
        # Subtipos de consultas emocionales
        self.emotional_subtypes = {
            "personal": {
                "yo", "mi", "me", "conmigo", "mío", "personal", "propio",
                "sentir", "sentimiento", "emoción", "estado de ánimo"
            },
            "interpersonal": {
                "relación", "pareja", "amigo", "familia", "colega", "jefe",
                "compañero", "equipo", "grupo", "comunidad", "sociedad"
            },
            "wellbeing": {
                "bienestar", "salud mental", "estrés", "ansiedad", "depresión",
                "felicidad", "satisfacción", "plenitud", "propósito", "significado"
            },
            "philosophical": {
                "filosofía", "ética", "moral", "valores", "principios", "virtud",
                "bien", "mal", "justicia", "libertad", "igualdad", "verdad"
            }
        }
    
    def _compile_regex_patterns(self):
        """
        Compila patrones de expresiones regulares para optimizar el rendimiento.
        
        Prepara expresiones regulares utilizadas frecuentemente en el análisis
        para evitar recompilaciones repetidas.
        """
        # Patrones básicos
        self.patterns = {
            "url": re.compile(r'https?://\S+'),
            "path": re.compile(r'/?(?:[a-zA-Z0-9-_]+/)+[a-zA-Z0-9-_.]+(?:\.[a-zA-Z0-9]+)?'),
            "code_block": re.compile(r'```(?:\w+)?\n(.*?)\n```', re.DOTALL),
            "terminal_command": re.compile(r'\$\s+([^\n]+)'),
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "version": re.compile(r'\b\d+\.\d+(?:\.\d+)?(?:-[a-zA-Z0-9]+)?\b'),
            "date": re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'),
            "time": re.compile(r'\b\d{1,2}:\d{2}(?::\d{2})?(?: ?[aApP][mM])?\b'),
            "number": re.compile(r'\b\d+(?:\.\d+)?\b'),
            "hashtag": re.compile(r'#\w+'),
            "mention": re.compile(r'@\w+')
        }
        
        # Patrones de emociones
        self.emotion_patterns = {
            "happiness": re.compile(r'\b(?:feliz|contento|alegre|encantado|emocionado|entusiasmado)\b', re.IGNORECASE),
            "sadness": re.compile(r'\b(?:triste|deprimido|melancólico|desanimado|apenado|desilusionado)\b', re.IGNORECASE),
            "anger": re.compile(r'\b(?:enojado|furioso|molesto|irritado|frustrado|indignado)\b', re.IGNORECASE),
            "fear": re.compile(r'\b(?:miedo|temor|asustado|preocupado|ansioso|nervioso)\b', re.IGNORECASE),
            "surprise": re.compile(r'\b(?:sorprendido|asombrado|impactado|impresionado|atónito)\b', re.IGNORECASE),
            "disgust": re.compile(r'\b(?:asco|repugnancia|repulsión|desagrado|repelente)\b', re.IGNORECASE),
            "trust": re.compile(r'\b(?:confianza|seguro|fiable|creíble|honesto|sincero)\b', re.IGNORECASE),
            "anticipation": re.compile(r'\b(?:anticipación|expectativa|esperanza|anhelo|deseo)\b', re.IGNORECASE)
        }
        
        # Patrones de lenguajes de programación
        self.language_patterns = {
            "python": re.compile(r'def\s+\w+\s*\(|import\s+\w+|from\s+\w+\s+import|class\s+\w+:|if\s+__name__\s*==\s*[\'"]__main__[\'"]'),
            "javascript": re.compile(r'function\s+\w+\s*\(|const\s+\w+\s*=|let\s+\w+\s*=|var\s+\w+\s*=|=>|import\s+.*\s+from'),
            "java": re.compile(r'public\s+class|private\s+\w+\s+\w+|System\.out\.println|@Override'),
            "c": re.compile(r'#include|int\s+main\s*\(|printf\s*\(|scanf\s*\(|malloc\s*\('),
            "cpp": re.compile(r'#include\s*<\w+>|std::|cout\s*<<|cin\s*>>|namespace'),
            "html": re.compile(r'<html|<div|<body|<head|<script|<style|<link|<!DOCTYPE'),
            "css": re.compile(r'\w+\s*{[^}]*}|@media|#\w+\s*{|\.[\w-]+\s*{'),
            "sql": re.compile(r'SELECT\s+\w+\s+FROM|INSERT\s+INTO|CREATE\s+TABLE|WHERE\s+\w+\s*=|JOIN\s+\w+\s+ON'),
            "bash": re.compile(r'#!/bin/bash|echo\s+|\$\w+|\$$$\w+$$|if\s+\[\s+.*\s+\]')
        }
    
    @track_performance
    def analyze(self, text: str, conversation_history: List[Dict[str, Any]] = None) -> IntentAnalysisResult:
        """
        Analiza un texto para determinar la intención y clasificación.
        
        Este método realiza un análisis completo del texto del usuario,
        combinando análisis léxico, semántico y contextual para determinar
        la mejor distribución de procesamiento entre hemisferios.
        
        Args:
            text: Texto a analizar
            conversation_history: Historial de conversación (opcional)
            
        Returns:
            Resultado del análisis de intención
        """
        start_time = time.time()
        self.stats["total_queries"] += 1
        
        try:
            # Verificar caché si está habilitado
            if self.cache:
                cache_key = self._generate_cache_key(text, conversation_history)
                cached_result = self.cache.get(cache_key)
                
                if cached_result:
                    self.stats["cache_hits"] += 1
                    result = IntentAnalysisResult.from_dict(cached_result)
                    result.cache_hit = True
                    logger.debug(f"Resultado obtenido de caché para: '{text[:50]}...'")
                    return result
                else:
                    self.stats["cache_misses"] += 1
            
            # Inicializar resultado
            result = IntentAnalysisResult(
                query_type="general",
                confidence=0.5
            )
            
            # Pipeline de análisis
            self._preprocess_text(text, result)
            self._analyze_keywords(text, result)
            self._extract_entities(text, result)
            
            # Análisis semántico si hay modelo de embeddings disponible
            if self.embedding_model:
                self._semantic_analysis(text, result, conversation_history)
            
            # Análisis contextual si hay contexto disponible
            if self.context and conversation_history:
                self._contextual_analysis(text, result, conversation_history)
            
            # Análisis de subtipos
            self._analyze_subtypes(text, result)
            
            # Normalizar pesos para que sumen 1.0
            total_weight = result.technical_weight + result.emotional_weight
            if total_weight > 0:
                result.technical_weight /= total_weight
                result.emotional_weight /= total_weight
            
            # Ajustar confianza final
            self._adjust_confidence(result)
            
            # Actualizar estadísticas
            self.stats["query_types"][result.query_type] += 1
            
            # Calcular tiempo de procesamiento
            processing_time = (time.time() - start_time) * 1000  # ms
            result.processing_time = processing_time
            
            # Actualizar promedio de tiempo de procesamiento
            self.stats["avg_processing_time"] = (
                (self.stats["avg_processing_time"] * (self.stats["total_queries"] - 1) + processing_time) / 
                self.stats["total_queries"]
            )
            
            # Guardar en caché si está habilitado
            if self.cache:
                self.cache.set(cache_key, result.to_dict())
            
            logger.debug(f"Análisis de intención completado en {processing_time:.2f}ms: {json.dumps(result.to_dict())}")
            return result
            
        except Exception as e:
            logger.error(f"Error en análisis de intención: {e}")
            logger.debug(traceback.format_exc())
            
            # Devolver resultado por defecto en caso de error
            default_result = IntentAnalysisResult(
                query_type="general",
                technical_weight=0.5,
                emotional_weight=0.5,
                confidence=0.5,
                processing_time=(time.time() - start_time) * 1000
            )
            return default_result
    
    def _generate_cache_key(self, text: str, conversation_history: List[Dict[str, Any]] = None) -> str:
        """
        Genera una clave única para el caché basada en el texto y contexto.
        
        Args:
            text: Texto a analizar
            conversation_history: Historial de conversación
            
        Returns:
            Clave única para el caché
        """
        # Normalizar texto (eliminar espacios extra, convertir a minúsculas)
        normalized_text = re.sub(r'\s+', ' ', text.lower()).strip()
        
        # Incluir últimos 2 mensajes del historial si existen
        context_key = ""
        if conversation_history and len(conversation_history) > 0:
            last_messages = conversation_history[-2:] if len(conversation_history) >= 2 else conversation_history
            for msg in last_messages:
                if "content" in msg:
                    # Solo incluir primeros 50 caracteres de cada mensaje para la clave
                    context_key += msg["content"][:50]
        
        # Generar hash para la combinación de texto y contexto
        combined = f"{normalized_text}|{context_key}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _preprocess_text(self, text: str, result: IntentAnalysisResult) -> str:
        """
        Preprocesa el texto para análisis.
        
        Realiza normalización básica y extracción de características
        preliminares del texto.
        
        Args:
            text: Texto original
            result: Resultado a actualizar
            
        Returns:
            Texto preprocesado
        """
        # Normalizar espacios
        normalized = re.sub(r'\s+', ' ', text).strip()
        
        # Detectar características básicas
        result.subtypes["length"] = len(text) / 1000.0  # Normalizado por 1000 caracteres
        result.subtypes["has_question"] = 1.0 if '?' in text else 0.0
        result.subtypes["has_exclamation"] = 1.0 if '!' in text else 0.0
        result.subtypes["has_code_markers"] = 1.0 if '```' in text else 0.0
        
        # Detectar idioma (simplificado)
        spanish_markers = ["qué", "cómo", "por qué", "cuándo", "dónde", "quién", "cuál"]
        english_markers = ["what", "how", "why", "when", "where", "who", "which"]
        
        spanish_count = sum(1 for marker in spanish_markers if marker in text.lower())
        english_count = sum(1 for marker in english_markers if marker in text.lower())
        
        if spanish_count > english_count:
            result.subtypes["language"] = "es"
        else:
            result.subtypes["language"] = "en"
        
        return normalized
    
    def _analyze_keywords(self, text: str, result: IntentAnalysisResult) -> None:
        """
        Realiza análisis basado en palabras clave.
        
        Identifica la presencia de palabras clave de diferentes categorías
        para determinar la naturaleza de la consulta.
        
        Args:
            text: Texto a analizar
            result: Resultado a actualizar
        """
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        # Contar ocurrencias de palabras clave por categoría
        technical_count = len(words.intersection(self.technical_keywords))
        emotional_count = len(words.intersection(self.emotional_keywords))
        
        # Determinar tipo de consulta basado en conteo
        total_keywords = technical_count + emotional_count
        if total_keywords > 0:
            technical_ratio = technical_count / total_keywords
            emotional_ratio = emotional_count / total_keywords
            
            # Asignar pesos basados en la proporción
            result.technical_weight = min(max(technical_ratio, 0.3), 0.9)
            result.emotional_weight = min(max(emotional_ratio, 0.3), 0.9)
            
            # Determinar tipo de consulta
            if technical_ratio > 0.7:
                result.query_type = "technical"
                result.confidence = 0.7 + (technical_ratio - 0.7) * 0.3  # 0.7-1.0
            elif emotional_ratio > 0.7:
                result.query_type = "emotional"
                result.confidence = 0.7 + (emotional_ratio - 0.7) * 0.3  # 0.7-1.0
            else:
                result.query_type = "general"
                result.confidence = 0.6
        
        # Detectar si requiere código
        if words.intersection(self.code_keywords):
            result.requires_code = True
            result.technical_weight += 0.1
        
        # Detectar si requiere creatividad
        if words.intersection(self.creativity_keywords):
            result.requires_creativity = True
            if result.query_type == "general":
                result.query_type = "creative"
                result.emotional_weight += 0.1
        
        # Detectar si requiere precisión factual
        if words.intersection(self.factual_keywords):
            result.requires_factual_accuracy = True
            if result.query_type == "general":
                result.query_type = "factual"
                result.technical_weight += 0.1
    
    def _extract_entities(self, text: str, result: IntentAnalysisResult) -> None:
        """
        Extrae entidades relevantes del texto.
        
        Identifica y extrae elementos estructurados como URLs, rutas,
        bloques de código, comandos, etc.
        
        Args:
            text: Texto a analizar
            result: Resultado a actualizar
        """
        entities = []
        
        # Extraer URLs
        for match in self.patterns["url"].finditer(text):
            entities.append(Entity(
                type="url",
                value=match.group(0),
                start=match.start(),
                end=match.end(),
                confidence=1.0
            ))
        
        # Extraer rutas de archivo
        for match in self.patterns["path"].finditer(text):
            # Verificar que no sea parte de una URL ya extraída
            is_in_url = False
            for entity in entities:
                if entity.type == "url" and entity.start <= match.start() and entity.end >= match.end():
                    is_in_url = True
                    break
            
            if not is_in_url:
                entities.append(Entity(
                    type="path",
                    value=match.group(0),
                    start=match.start(),
                    end=match.end(),
                    confidence=0.8
                ))
        
        # Extraer bloques de código
        if "```" in text:
            for match in self.patterns["code_block"].finditer(text):
                code_content = match.group(1)
                language = self._detect_code_language(match.group(0))
                
                entities.append(Entity(
                    type="code_block",
                    value=code_content,
                    start=match.start(),
                    end=match.end(),
                    confidence=1.0,
                    metadata={"language": language}
                ))
                
                # Si hay código, aumentar peso técnico
                result.technical_weight += 0.2
                result.requires_code = True
        
        # Extraer comandos de terminal
        for match in self.patterns["terminal_command"].finditer(text):
            entities.append(Entity(
                type="terminal_command",
                value=match.group(1),
                start=match.start(),
                end=match.end(),
                confidence=0.9
            ))
            
            # Si hay comandos, aumentar peso técnico
            result.technical_weight += 0.1
        
        # Extraer expresiones emocionales
        for emotion, pattern in self.emotion_patterns.items():
            for match in pattern.finditer(text):
                entities.append(Entity(
                    type="emotion",
                    value=match.group(0),
                    start=match.start(),
                    end=match.end(),
                    confidence=0.7,
                    metadata={"emotion_type": emotion}
                ))
                
                # Si hay emociones, aumentar peso emocional
                result.emotional_weight += 0.1
        
        # Extraer emails
        for match in self.patterns["email"].finditer(text):
            entities.append(Entity(
                type="email",
                value=match.group(0),
                start=match.start(),
                end=match.end(),
                confidence=1.0
            ))
        
        # Extraer versiones
        for match in self.patterns["version"].finditer(text):
            entities.append(Entity(
                type="version",
                value=match.group(0),
                start=match.start(),
                end=match.end(),
                confidence=0.9
            ))
        
        # Extraer fechas
        for match in self.patterns["date"].finditer(text):
            entities.append(Entity(
                type="date",
                value=match.group(0),
                start=match.start(),
                end=match.end(),
                confidence=0.9
            ))
        
        # Extraer horas
        for match in self.patterns["time"].finditer(text):
            entities.append(Entity(
                type="time",
                value=match.group(0),
                start=match.start(),
                end=match.end(),
                confidence=0.9
            ))
        
        # Actualizar resultado con entidades extraídas
        result.entities = entities
        
        # Ajustar tipo de consulta basado en entidades
        if any(e.type == "code_block" for e in entities) and result.query_type == "general":
            result.query_type = "technical"
        elif any(e.type == "emotion" for e in entities) and result.query_type == "general":
            result.query_type = "emotional"
    
    def _detect_code_language(self, code_block: str) -> str:
        """
        Detecta el lenguaje de programación de un bloque de código.
        
        Utiliza heurísticas y patrones para identificar el lenguaje
        de programación más probable en un bloque de código.
        
        Args:
            code_block: Bloque de código con marcadores
            
        Returns:
            Lenguaje detectado o "unknown"
        """
        # Extraer lenguaje de la sintaxis markdown
        language_match = re.match(r'```(\w+)', code_block)
        if language_match and language_match.group(1) not in ["", "text", "plain"]:
            return language_match.group(1)
        
        # Detectar por contenido si no está especificado
        code_content = code_block.strip('`').strip()
        
        # Verificar patrones de lenguajes
        matches = {}
        for lang, pattern in self.language_patterns.items():
            if pattern.search(code_content):
                matches[lang] = len(pattern.findall(code_content))
        
        # Seleccionar el lenguaje con más coincidencias
        if matches:
            best_match = max(matches.items(), key=lambda x: x[1])
            return best_match[0]
        
        return "unknown"
    
    def _semantic_analysis(self, text: str, result: IntentAnalysisResult, 
                          conversation_history: List[Dict[str, Any]] = None) -> None:
        """
        Realiza análisis semántico usando embeddings.
        
        Utiliza modelos de embeddings para comparar la similitud semántica
        del texto con diferentes categorías de consultas.
        
        Args:
            text: Texto a analizar
            result: Resultado a actualizar
            conversation_history: Historial de conversación
        """
        if not self.embedding_model:
            return
        
        try:
            # Obtener embedding del texto
            text_embedding = self.embedding_model.get_embedding(text)
            
            # Comparar con embeddings de referencia para diferentes categorías
            # Nota: En una implementación real, estos embeddings de referencia
            # serían pre-calculados y almacenados
            
            # Ejemplo simplificado
            category_texts = {
                "technical": "código programa desarrollo técnico implementación algoritmo",
                "emotional": "sentimientos emociones relaciones personales bienestar",
                "creative": "ideas creativas innovación diseño arte inspiración",
                "factual": "datos hechos información precisa estadísticas historia"
            }
            
            similarities = {}
            for category, category_text in category_texts.items():
                category_embedding = self.embedding_model.get_embedding(category_text)
                similarity = self._cosine_similarity(text_embedding, category_embedding)
                similarities[category] = similarity
            
            # Encontrar categoría más similar
            best_category = max(similarities.items(), key=lambda x: x[1])
            
            # Actualizar resultado si la similitud es significativa
            if best_category[1] > 0.6:  # Umbral arbitrario
                result.query_type = best_category[0]
                result.confidence = max(result.confidence, best_category[1])
                
                # Ajustar pesos según categoría
                if best_category[0] in ["technical", "factual"]:
                    result.technical_weight += 0.2
                elif best_category[0] in ["emotional", "creative"]:
                    result.emotional_weight += 0.2
            
            # Guardar todas las similitudes en subtypes
            for category, similarity in similarities.items():
                result.subtypes[f"semantic_{category}"] = similarity
            
        except Exception as e:
            logger.error(f"Error en análisis semántico: {e}")
            logger.debug(traceback.format_exc())
    
    def _contextual_analysis(self, text: str, result: IntentAnalysisResult,
                            conversation_history: List[Dict[str, Any]]) -> None:
        """
        Realiza análisis contextual basado en la conversación previa.
        
        Analiza el historial de conversación para detectar patrones,
        continuidad temática y cambios de contexto.
        
        Args:
            text: Texto a analizar
            result: Resultado a actualizar
            conversation_history: Historial de conversación
        """
        if not conversation_history:
            return
        
        try:
            # Analizar últimos mensajes para detectar contexto
            recent_messages = conversation_history[-5:]  # Últimos 5 mensajes
            
            # Contar tipos de consultas recientes
            query_types = {"technical": 0, "emotional": 0, "creative": 0, "factual": 0, "general": 0}
            
            for msg in recent_messages:
                if "query_type" in msg:
                    query_type = msg["query_type"]
                    if query_type in query_types:
                        query_types[query_type] += 1
            
            # Verificar si hay un tipo dominante
            dominant_type = max(query_types.items(), key=lambda x: x[1])
            
            # Si hay un tipo dominante y la consulta actual es general,
            # inclinar ligeramente hacia el tipo dominante
            if dominant_type[1] >= 2 and result.query_type == "general":
                result.query_type = dominant_type[0]
                result.confidence = max(result.confidence, 0.6)
                
                # Ajustar pesos según tipo dominante
                if dominant_type[0] in ["technical", "factual"]:
                    result.technical_weight += 0.1
                elif dominant_type[0] in ["emotional", "creative"]:
                    result.emotional_weight += 0.1
            
            # Verificar continuidad de la conversación
            if len(recent_messages) > 0 and "content" in recent_messages[-1]:
                last_message = recent_messages[-1]["content"]
                
                # Detectar si la consulta actual es una continuación
                continuation_indicators = ["más", "continúa", "sigue", "y qué más", "otro ejemplo"]
                if any(indicator in text.lower() for indicator in continuation_indicators):
                    # Mantener el mismo tipo de consulta que el mensaje anterior
                    if "query_type" in recent_messages[-1]:
                        result.query_type = recent_messages[-1]["query_type"]
                        result.confidence = max(result.confidence, 0.7)
            
            # Detectar cambios de tema
            topic_shift_indicators = ["cambiando de tema", "por otro lado", "otra cosa", "nuevo tema"]
            topic_shift = any(indicator in text.lower() for indicator in topic_shift_indicators)
            
            # Detectar referencias a mensajes anteriores
            reference_indicators = ["como dijiste", "mencionaste", "anteriormente", "antes"]
            has_reference = any(indicator in text.lower() for indicator in reference_indicators)
            
            # Actualizar relevancia de contexto
            result.context_relevance = {
                "continuation": 0.8 if any(c in text.lower() for c in ["más", "continúa", "sigue"]) else 0.2,
                "topic_shift": 0.8 if topic_shift else 0.2,
                "has_reference": 0.8 if has_reference else 0.2,
                "conversation_length": len(conversation_history) / 10.0  # Normalizado
            }
            
            # Analizar coherencia temática
            if self.embedding_model and len(recent_messages) > 0:
                try:
                    # Obtener embedding del texto actual
                    current_embedding = self.embedding_model.get_embedding(text)
                    
                    # Obtener embedding del último mensaje
                    if "content" in recent_messages[-1]:
                        last_embedding = self.embedding_model.get_embedding(recent_messages[-1]["content"])
                        
                        # Calcular similitud
                        similarity = self._cosine_similarity(current_embedding, last_embedding)
                        
                        # Actualizar relevancia de contexto
                        result.context_relevance["semantic_continuity"] = similarity
                        
                        # Si hay alta similitud semántica, reforzar continuidad
                        if similarity > 0.7 and not topic_shift:
                            if "query_type" in recent_messages[-1]:
                                # Inclinar hacia el mismo tipo de consulta
                                prev_type = recent_messages[-1]["query_type"]
                                if result.query_type == "general":
                                    result.query_type = prev_type
                                    result.confidence = max(result.confidence, 0.65)
                except Exception as e:
                    logger.warning(f"Error en análisis de coherencia temática: {e}")
            
        except Exception as e:
            logger.error(f"Error en análisis contextual: {e}")
            logger.debug(traceback.format_exc())
    
    def _analyze_subtypes(self, text: str, result: IntentAnalysisResult) -> None:
        """
        Analiza subtipos específicos de consultas.
        
        Identifica categorías más específicas dentro de los tipos
        principales de consultas (técnicas, emocionales, etc.).
        
        Args:
            text: Texto a analizar
            result: Resultado a actualizar
        """
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        # Analizar subtipos técnicos
        if result.query_type in ["technical", "general", "factual"]:
            for subtype, keywords in self.technical_subtypes.items():
                overlap = words.intersection(keywords)
                if overlap:
                    score = len(overlap) / len(keywords)
                    result.subtypes[f"technical_{subtype}"] = score
        
        # Analizar subtipos emocionales
        if result.query_type in ["emotional", "general", "creative"]:
            for subtype, keywords in self.emotional_subtypes.items():
                overlap = words.intersection(keywords)
                if overlap:
                    score = len(overlap) / len(keywords)
                    result.subtypes[f"emotional_{subtype}"] = score
        
        # Detectar consultas de definición
        definition_indicators = ["qué es", "definición de", "significa", "define", "explica"]
        if any(indicator in lower_text for indicator in definition_indicators):
            result.subtypes["definition_query"] = 1.0
            result.technical_weight += 0.1
        
        # Detectar consultas de comparación
        comparison_indicators = ["diferencia entre", "comparar", "versus", "vs", "mejor que", "peor que"]
        if any(indicator in lower_text for indicator in comparison_indicators):
            result.subtypes["comparison_query"] = 1.0
            result.technical_weight += 0.1
        
        # Detectar consultas de procedimiento
        procedure_indicators = ["cómo", "pasos para", "proceso de", "método para", "técnica de"]
        if any(indicator in lower_text for indicator in procedure_indicators):
            result.subtypes["procedure_query"] = 1.0
            result.technical_weight += 0.1
        
        # Detectar consultas de opinión
        opinion_indicators = ["qué opinas", "tu opinión", "qué piensas", "crees que", "consideras"]
        if any(indicator in lower_text for indicator in opinion_indicators):
            result.subtypes["opinion_query"] = 1.0
            result.emotional_weight += 0.2
    
    def _adjust_confidence(self, result: IntentAnalysisResult) -> None:
        """
        Ajusta el nivel de confianza final del análisis.
        
        Combina múltiples factores para determinar la confianza
        general en la clasificación realizada.
        
        Args:
            result: Resultado a actualizar
        """
        # Factores que aumentan la confianza
        confidence_boosters = [
            # Entidades extraídas
            0.05 * min(len(result.entities), 5),
            
            # Claridad en la clasificación (diferencia entre pesos)
            0.1 * abs(result.technical_weight - result.emotional_weight),
            
            # Presencia de indicadores específicos
            0.1 if result.requires_code else 0,
            0.1 if result.requires_creativity else 0,
            0.1 if result.requires_factual_accuracy else 0,
            
            # Subtipos identificados
            0.05 * min(len(result.subtypes), 5)
        ]
        
        # Sumar factores de aumento (limitado a 0.3 adicional)
        confidence_boost = min(sum(confidence_boosters), 0.3)
        
        # Actualizar confianza final (limitada a 0.95)
        result.confidence = min(result.confidence + confidence_boost, 0.95)
    
    def _cosine_similarity(self, vec1, vec2):
        """
        Calcula la similitud coseno entre dos vectores.
        
        Args:
            vec1: Primer vector
            vec2: Segundo vector
            
        Returns:
            Similitud coseno (0.0-1.0)
        """
        import numpy as np
        
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        
        if norm_vec1 == 0 or norm_vec2 == 0:
            return 0.0
        
        return dot_product / (norm_vec1 * norm_vec2)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del analizador.
        
        Returns:
            Diccionario con estadísticas de uso
        """
        return {
            "total_queries": self.stats["total_queries"],
            "cache_hits": self.stats["cache_hits"],
            "cache_misses": self.stats["cache_misses"],
            "cache_hit_ratio": self.stats["cache_hits"] / max(1, self.stats["total_queries"]),
            "avg_processing_time": self.stats["avg_processing_time"],
            "query_types": dict(self.stats["query_types"])
        }
    
    def reset_stats(self) -> None:
        """Reinicia las estadísticas del analizador."""
        self.stats = {
            "total_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_processing_time": 0.0,
            "query_types": Counter()
        }

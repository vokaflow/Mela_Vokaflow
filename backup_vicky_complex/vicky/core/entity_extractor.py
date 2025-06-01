"""
Sistema de Extracción de Entidades
----------------------------------

Este módulo implementa un sistema avanzado para la extracción, clasificación
y gestión de entidades en texto, facilitando la comprensión contextual y
la identificación de elementos relevantes en las conversaciones.

Combina técnicas basadas en reglas, expresiones regulares y procesamiento
de lenguaje natural para detectar y clasificar diversos tipos de entidades.

Autor: Equipo VokaFlow
Versión: 1.0.0
"""

import logging
import re
import time
import uuid
import json
from typing import Dict, List, Any, Optional, Union, Set, Tuple, Callable
from dataclasses import dataclass, field
import traceback
import datetime

from .entity_types import Entity, EntityGroup, EntityCategory, EntitySubType, ENTITY_RELATIONS
from ..utils.performance_metrics import track_performance

# Configurar logger
logger = logging.getLogger("vicky.entity_extractor")


@dataclass
class ExtractionRule:
    """
    Regla para extracción de entidades.
    
    Define patrones y condiciones para identificar entidades específicas
    en el texto, junto con su categorización y atributos.
    
    Attributes:
        id: Identificador único de la regla
        name: Nombre descriptivo de la regla
        pattern: Patrón de expresión regular para la detección
        category: Categoría de entidad a asignar
        subtype: Subtipo específico (opcional)
        confidence: Confianza base para las entidades extraídas
        attributes: Atributos predeterminados para las entidades
        validation_func: Función opcional para validación adicional
        priority: Prioridad de la regla (mayor número = mayor prioridad)
        enabled: Indica si la regla está activa
    """
    id: str
    name: str
    pattern: str
    category: EntityCategory
    subtype: Optional[EntitySubType] = None
    confidence: float = 0.8
    attributes: Dict[str, Any] = field(default_factory=dict)
    validation_func: Optional[Callable[[str], bool]] = None
    priority: int = 1
    enabled: bool = True
    
    def __post_init__(self):
        """Compila el patrón de expresión regular tras inicialización."""
        try:
            self.compiled_pattern = re.compile(self.pattern, re.IGNORECASE)
        except re.error as e:
            logger.error(f"Error al compilar patrón para regla {self.name}: {e}")
            self.enabled = False
            self.compiled_pattern = None
    
    def match(self, text: str) -> List[Tuple[str, int, int, float]]:
        """
        Busca coincidencias de la regla en el texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Lista de tuplas (valor, inicio, fin, confianza)
        """
        if not self.enabled or not self.compiled_pattern:
            return []
        
        matches = []
        for match in self.compiled_pattern.finditer(text):
            value = match.group(0)
            start = match.start()
            end = match.end()
            
            # Aplicar validación adicional si existe
            if self.validation_func and not self.validation_func(value):
                continue
            
            matches.append((value, start, end, self.confidence))
        
        return matches


class EntityExtractor:
    """
    Sistema avanzado de extracción de entidades.
    
    Proporciona capacidades para identificar, clasificar y gestionar
    entidades mencionadas en texto, utilizando un enfoque híbrido
    que combina reglas predefinidas con técnicas de ML.
    
    El sistema es extensible y permite añadir nuevos tipos de entidades
    y reglas de extracción según las necesidades específicas.
    """
    
    def __init__(self, ner_model=None, embedding_model=None):
        """
        Inicializa el extractor de entidades.
        
        Args:
            ner_model: Modelo de reconocimiento de entidades (opcional)
            embedding_model: Modelo de embeddings para análisis semántico (opcional)
        """
        self.ner_model = ner_model
        self.embedding_model = embedding_model
        
        # Reglas de extracción
        self.rules: Dict[str, ExtractionRule] = {}
        
        # Entidades extraídas (caché)
        self.entity_cache: Dict[str, Entity] = {}
        
        # Grupos de entidades
        self.entity_groups: Dict[str, EntityGroup] = {}
        
        # Estadísticas de extracción
        self.stats = {
            "total_extractions": 0,
            "rule_based_extractions": 0,
            "ner_extractions": 0,
            "avg_entities_per_text": 0.0,
            "extracted_categories": {},
            "extraction_times": []
        }
        
        # Inicializar reglas predeterminadas
        self._init_default_rules()
        
        logger.info("Sistema de extracción de entidades inicializado")
    
    def _init_default_rules(self):
        """Inicializa las reglas predeterminadas de extracción."""
        # Nombres propios
        self.add_rule(ExtractionRule(
            id="person_name",
            name="Nombre de persona",
            pattern=r'\b[A-Z][a-zñáéíóú]+(?:\s+[A-Z][a-zñáéíóú]+){1,2}\b',
            category=EntityCategory.PERSON,
            subtype=EntitySubType.PERSON_NAME,
            confidence=0.75
        ))
        
        # Títulos y roles profesionales
        self.add_rule(ExtractionRule(
            id="person_title",
            name="Título profesional",
            pattern=r'\b(?:Dr|Dra|Ing|Lic|Prof|Sr|Sra|Director[a]?|Gerente|Jefe|Supervisor[a]?|Coordinador[a]?|Presidente|CEO|CTO|CFO|COO|CMO)\b\.?\s+[A-Z][a-zñáéíóú]+',
            category=EntityCategory.PERSON,
            subtype=EntitySubType.PERSON_TITLE,
            confidence=0.85
        ))
        
        # Organizaciones
        self.add_rule(ExtractionRule(
            id="company",
            name="Empresa",
            pattern=r'\b(?:[A-Z][a-zñáéíóú]*\s+)*(?:S\.A\.|S\.L\.|Inc\.|LLC|GmbH|Ltd|SpA|Corp|Company|Group)\b',
            category=EntityCategory.ORGANIZATION,
            subtype=EntitySubType.COMPANY,
            confidence=0.80
        ))
        
        # Lenguajes de programación
        self.add_rule(ExtractionRule(
            id="programming_language",
            name="Lenguaje de programación",
            pattern=r'\b(?:Python|JavaScript|TypeScript|Java|C\+\+|C\#|Ruby|Go|Rust|Swift|Kotlin|PHP|Scala|Haskell|Perl|R|MATLAB|Lua|Dart|Groovy|Clojure|Erlang|Elixir|F\#|COBOL|Fortran|Assembly|Lisp|Prolog|Julia|Crystal)\b',
            category=EntityCategory.TECHNOLOGY,
            subtype=EntitySubType.PROGRAMMING_LANGUAGE,
            confidence=0.95
        ))
        
        # Frameworks y librerías
        self.add_rule(ExtractionRule(
            id="framework_library",
            name="Framework o librería",
            pattern=r'\b(?:Django|Flask|FastAPI|React|Angular|Vue|Svelte|Express|Spring|Laravel|ASP\.NET|Ruby on Rails|Symfony|TensorFlow|PyTorch|Keras|scikit-learn|NumPy|Pandas|Matplotlib|Seaborn|Bootstrap|Tailwind|jQuery|Redux|Next\.js|Nuxt\.js|Gatsby|Electron|NestJS|GraphQL|Apollo|Material-UI|Chakra UI)\b',
            category=EntityCategory.TECHNOLOGY,
            subtype=EntitySubType.FRAMEWORK,
            confidence=0.90
        ))
        
        # Bases de datos
        self.add_rule(ExtractionRule(
            id="database",
            name="Base de datos",
            pattern=r'\b(?:MySQL|PostgreSQL|SQLite|Oracle|SQL Server|MongoDB|Cassandra|Redis|Elasticsearch|Neo4j|DynamoDB|Firebase|Firestore|CouchDB|MariaDB|H2|HSQLDB|RethinkDB|ArangoDB|Couchbase|InfluxDB|TimescaleDB)\b',
            category=EntityCategory.TECHNOLOGY,
            subtype=EntitySubType.DATABASE,
            confidence=0.90
        ))
        
        # Plataformas cloud
        self.add_rule(ExtractionRule(
            id="cloud_platform",
            name="Plataforma cloud",
            pattern=r'\b(?:AWS|Amazon Web Services|EC2|S3|Lambda|Google Cloud|GCP|Azure|Microsoft Azure|Heroku|DigitalOcean|Vercel|Netlify|Firebase|CloudFlare|OpenStack|IBM Cloud|Oracle Cloud|Linode|Vultr)\b',
            category=EntityCategory.TECHNOLOGY,
            subtype=EntitySubType.PLATFORM,
            confidence=0.85
        ))
        
        # Fechas
        self.add_rule(ExtractionRule(
            id="date",
            name="Fecha",
            pattern=r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
            category=EntityCategory.TEMPORAL,
            subtype=EntitySubType.DATE,
            confidence=0.85
        ))
        
        # Horas
        self.add_rule(ExtractionRule(
            id="time",
            name="Hora",
            pattern=r'\b\d{1,2}:\d{2}(?::\d{2})?(?:\s*[aApP][mM])?\b',
            category=EntityCategory.TEMPORAL,
            subtype=EntitySubType.TIME,
            confidence=0.85
        ))
        
        # Rutas de archivo
        self.add_rule(ExtractionRule(
            id="file_path",
            name="Ruta de archivo",
            pattern=r'(?:/[a-zA-Z0-9_.-]+)+(?:\.[a-zA-Z0-9]+)?|[a-zA-Z]:\$$?:[a-zA-Z0-9_.-]+\$$+[a-zA-Z0-9_.-]+(?:\.[a-zA-Z0-9]+)?',
            category=EntityCategory.CODE,
            subtype=EntitySubType.FILE_PATH,
            confidence=0.90
        ))
        
        # URLs
        self.add_rule(ExtractionRule(
            id="url",
            name="URL",
            pattern=r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)',
            category=EntityCategory.CODE,
            subtype=EntitySubType.URL,
            confidence=0.95
        ))
        
        # Emails
        self.add_rule(ExtractionRule(
            id="email",
            name="Email",
            pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            category=EntityCategory.REFERENCE,
            subtype=EntitySubType.WEBSITE,
            confidence=0.95
        ))
        
        # Código inline
        self.add_rule(ExtractionRule(
            id="inline_code",
            name="Código inline",
            pattern=r'`[^`\n]+`',
            category=EntityCategory.CODE,
            subtype=EntitySubType.CODE_SNIPPET,
            confidence=0.90
        ))
        
        # Variables y funciones
        self.add_rule(ExtractionRule(
            id="variable_function",
            name="Variable o función",
            pattern=r'\b[a-zA-Z_][a-zA-Z0-9_]*$$[^)]*$$',
            category=EntityCategory.CODE,
            subtype=EntitySubType.FUNCTION_NAME,
            confidence=0.80
        ))
        
        # Países
        self.add_rule(ExtractionRule(
            id="country",
            name="País",
            pattern=r'\b(?:España|México|Argentina|Colombia|Chile|Perú|Ecuador|Uruguay|Paraguay|Bolivia|Venezuela|Costa Rica|Panamá|Honduras|El Salvador|Nicaragua|Guatemala|República Dominicana|Cuba|Puerto Rico|Estados Unidos|Canadá|Brasil|Francia|Alemania|Italia|Reino Unido|Portugal|Países Bajos|Bélgica|Suiza|Austria|Grecia|Suecia|Noruega|Finlandia|Dinamarca|Irlanda|Polonia|Rusia|China|Japón|Corea del Sur|India|Australia|Nueva Zelanda)\b',
            category=EntityCategory.LOCATION,
            subtype=EntitySubType.COUNTRY,
            confidence=0.90
        ))
        
        # Ciudades importantes (limitadas a algunas)
        self.add_rule(ExtractionRule(
            id="city",
            name="Ciudad",
            pattern=r'\b(?:Madrid|Barcelona|Valencia|Sevilla|Zaragoza|Málaga|Murcia|Bilbao|México D\.F\.|Ciudad de México|Buenos Aires|Bogotá|Santiago|Lima|Quito|Montevideo|Asunción|La Paz|Caracas|San José|Panamá|Tegucigalpa|San Salvador|Managua|Ciudad de Guatemala|Santo Domingo|La Habana|San Juan|Nueva York|Los Ángeles|Chicago|Miami|São Paulo|Río de Janeiro|París|Berlín|Roma|Londres|Lisboa|Ámsterdam|Bruselas|Zúrich|Viena|Atenas|Estocolmo|Oslo|Helsinki|Copenhague|Dublín|Varsovia|Moscú|Pekín|Tokio|Seúl|Nueva Delhi|Sídney|Auckland)\b',
            category=EntityCategory.LOCATION,
            subtype=EntitySubType.CITY,
            confidence=0.85
        ))
        
        # Números y cantidades
        self.add_rule(ExtractionRule(
            id="numeric",
            name="Número",
            pattern=r'\b\d+(?:[.,]\d+)?\b',
            category=EntityCategory.NUMERIC,
            subtype=EntitySubType.FLOAT,
            confidence=0.85
        ))
        
        # Porcentajes
        self.add_rule(ExtractionRule(
            id="percentage",
            name="Porcentaje",
            pattern=r'\b\d+(?:[.,]\d+)?%\b',
            category=EntityCategory.NUMERIC,
            subtype=EntitySubType.PERCENTAGE,
            confidence=0.90
        ))
        
        # Cantidades monetarias
        self.add_rule(ExtractionRule(
            id="monetary",
            name="Cantidad monetaria",
            pattern=r'\b(?:€|EUR|USD|\$)\s*\d+(?:[.,]\d+)?\b|\b\d+(?:[.,]\d+)?\s*(?:€|EUR|USD|\$)\b',
            category=EntityCategory.NUMERIC,
            subtype=EntitySubType.MONETARY,
            confidence=0.90
        ))
        
        # Términos técnicos
        self.add_rule(ExtractionRule(
            id="technical_term",
            name="Término técnico",
            pattern=r'\b(?:algoritmo|función|variable|clase|método|objeto|instancia|herencia|polimorfismo|encapsulación|abstracción|interfaz|API|servicio|microservicio|arquitectura|patrón de diseño|MVC|MVP|MVVM|REST|GraphQL|SOAP|TCP/IP|HTTP|HTTPS|SSL|TLS|SSH|FTP|SMTP|DNS|IP|URL|URI|JSON|XML|YAML|HTML|CSS|DOM|AJAX|webhook|callback|promesa|async|await|thread|proceso|concurrencia|paralelismo|sincronización|mutex|semáforo|deadlock|race condition|memoria|CPU|GPU|caché|buffer|stack|heap|compilación|interpretación|transpilación|bytecode|máquina virtual|runtime|framework|biblioteca|dependencia|package|módulo|namespace|scope|closure|recursión|iteración|lazy loading|memoization|hashing|encriptación|autenticación|autorización|OAuth|JWT|CORS|XSS|CSRF|inyección SQL|sanitización|validación|refactorización|testing|TDD|BDD|CI/CD|DevOps|deployment|escalabilidad|alta disponibilidad|tolerancia a fallos|balanceo de carga|caché distribuida|sharding|replicación)\b',
            category=EntityCategory.CONCEPT,
            subtype=EntitySubType.TECHNICAL_TERM,
            confidence=0.80
        ))
        
        logger.info(f"Inicializadas {len(self.rules)} reglas predeterminadas de extracción")
    
    def add_rule(self, rule: ExtractionRule) -> bool:
        """
        Añade una nueva regla de extracción.
        
        Args:
            rule: Regla de extracción a añadir
            
        Returns:
            True si se añadió correctamente, False en caso contrario
        """
        if rule.id in self.rules:
            logger.warning(f"Ya existe una regla con ID '{rule.id}'")
            return False
        
        self.rules[rule.id] = rule
        logger.debug(f"Añadida regla de extracción: {rule.name}")
        return True
    
    def remove_rule(self, rule_id: str) -> bool:
        """
        Elimina una regla de extracción.
        
        Args:
            rule_id: ID de la regla a eliminar
            
        Returns:
            True si se eliminó correctamente, False si no existía
        """
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.debug(f"Eliminada regla de extracción: {rule_id}")
            return True
        return False
    
    def enable_rule(self, rule_id: str, enabled: bool = True) -> bool:
        """
        Habilita o deshabilita una regla de extracción.
        
        Args:
            rule_id: ID de la regla a modificar
            enabled: True para habilitar, False para deshabilitar
            
        Returns:
            True si se modificó correctamente, False si no existía
        """
        if rule_id in self.rules:
            self.rules[rule_id].enabled = enabled
            state = "habilitada" if enabled else "deshabilitada"
            logger.debug(f"Regla {rule_id} {state}")
            return True
        return False
    
    @track_performance
    def extract_entities(self, text: str, context: Dict[str, Any] = None) -> List[Entity]:
        """
        Extrae entidades de un texto utilizando reglas predefinidas y NER.
        
        Args:
            text: Texto a analizar
            context: Contexto adicional (opcional)
            
        Returns:
            Lista de entidades extraídas
        """
        start_time = time.time()
        self.stats["total_extractions"] += 1
        context = context or {}
        
        extracted_entities = []
        
        try:
            # 1. Extracción basada en reglas
            rule_entities = self._extract_with_rules(text)
            extracted_entities.extend(rule_entities)
            self.stats["rule_based_extractions"] += len(rule_entities)
            
            # 2. Extracción usando NER (si está disponible)
            if self.ner_model:
                ner_entities = self._extract_with_ner(text)
                # Filtrar entidades duplicadas
                ner_entities = [e for e in ner_entities if not self._is_duplicate_entity(e, extracted_entities)]
                extracted_entities.extend(ner_entities)
                self.stats["ner_extractions"] += len(ner_entities)
            
            # 3. Post-procesamiento y deduplicación
            processed_entities = self._post_process_entities(extracted_entities, text, context)
            
            # 4. Actualizar caché
            for entity in processed_entities:
                self.entity_cache[entity.id] = entity
            
            # 5. Actualizar estadísticas
            processing_time = time.time() - start_time
            self.stats["extraction_times"].append(processing_time)
            
            # Calcular promedio de entidades por texto
            total_texts = self.stats["total_extractions"]
            total_entities = (
                self.stats["rule_based_extractions"] + 
                self.stats["ner_extractions"]
            )
            self.stats["avg_entities_per_text"] = total_entities / total_texts
            
            # Actualizar categorías extraídas
            for entity in processed_entities:
                category = entity.category.name
                self.stats["extracted_categories"][category] = (
                    self.stats["extracted_categories"].get(category, 0) + 1
                )
            
            logger.debug(f"Extracción completada en {processing_time:.3f}s: {len(processed_entities)} entidades encontradas")
            
            return processed_entities
            
        except Exception as e:
            logger.error(f"Error en extracción de entidades: {e}")
            logger.debug(traceback.format_exc())
            return []
    
    def _extract_with_rules(self, text: str) -> List[Entity]:
        """
        Extrae entidades utilizando reglas predefinidas.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Lista de entidades extraídas
        """
        entities = []
        
        # Ordenar reglas por prioridad
        sorted_rules = sorted(
            self.rules.values(),
            key=lambda r: r.priority,
            reverse=True  # Mayor prioridad primero
        )
        
        # Aplicar cada regla
        for rule in sorted_rules:
            if not rule.enabled:
                continue
                
            try:
                # Buscar coincidencias de la regla
                matches = rule.match(text)
                
                for value, start, end, confidence in matches:
                    # Crear entidad
                    entity_id = str(uuid.uuid4())
                    entity = Entity(
                        id=entity_id,
                        name=value,
                        category=rule.category,
                        subtype=rule.subtype,
                        value=value,
                        start_pos=start,
                        end_pos=end,
                        confidence=confidence,
                        source=f"rule_{rule.id}",
                        attributes=rule.attributes.copy()
                    )
                    
                    entities.append(entity)
            except Exception as e:
                logger.warning(f"Error al aplicar regla {rule.name}: {e}")
        
        return entities
    
    def _extract_with_ner(self, text: str) -> List[Entity]:
        """
        Extrae entidades utilizando un modelo NER.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Lista de entidades extraídas
        """
        if not self.ner_model:
            return []
        
        entities = []
        
        try:
            # Obtener entidades del modelo NER
            ner_results = self.ner_model.extract_entities(text)
            
            # Mapeo de tipos de entidades NER a nuestras categorías
            ner_mapping = {
                "PERSON": (EntityCategory.PERSON, EntitySubType.PERSON_NAME),
                "ORG": (EntityCategory.ORGANIZATION, EntitySubType.COMPANY),
                "GPE": (EntityCategory.LOCATION, EntitySubType.CITY),
                "LOC": (EntityCategory.LOCATION, EntitySubType.LOCATION),
                "DATE": (EntityCategory.TEMPORAL, EntitySubType.DATE),
                "TIME": (EntityCategory.TEMPORAL, EntitySubType.TIME),
                "MONEY": (EntityCategory.NUMERIC, EntitySubType.MONETARY),
                "PERCENT": (EntityCategory.NUMERIC, EntitySubType.PERCENTAGE),
                "PRODUCT": (EntityCategory.TECHNOLOGY, EntitySubType.HARDWARE),
                "EVENT": (EntityCategory.CONCEPT, EntitySubType.UNKNOWN_TYPE),
                "WORK_OF_ART": (EntityCategory.REFERENCE, EntitySubType.DOCUMENT),
                "LAW": (EntityCategory.REFERENCE, EntitySubType.DOCUMENT),
                "LANGUAGE": (EntityCategory.CONCEPT, EntitySubType.UNKNOWN_TYPE),
                "FAC": (EntityCategory.LOCATION, EntitySubType.UNKNOWN_TYPE),
                "NORP": (EntityCategory.CONCEPT, EntitySubType.UNKNOWN_TYPE),
                "CARDINAL": (EntityCategory.NUMERIC, EntitySubType.INTEGER),
                "ORDINAL": (EntityCategory.NUMERIC, EntitySubType.INTEGER),
                "QUANTITY": (EntityCategory.NUMERIC, EntitySubType.FLOAT)
            }
            
            # Convertir resultados NER a nuestras entidades
            for ner_entity in ner_results:
                ner_type = ner_entity.get("type", "UNKNOWN")
                category, subtype = ner_mapping.get(
                    ner_type, 
                    (EntityCategory.UNKNOWN, EntitySubType.UNKNOWN_TYPE)
                )
                
                entity_id = str(uuid.uuid4())
                entity = Entity(
                    id=entity_id,
                    name=ner_entity.get("text", ""),
                    category=category,
                    subtype=subtype,
                    value=ner_entity.get("text", ""),
                    start_pos=ner_entity.get("start", -1),
                    end_pos=ner_entity.get("end", -1),
                    confidence=ner_entity.get("score", 0.7),
                    source="ner_model",
                    attributes={"ner_type": ner_type}
                )
                
                entities.append(entity)
                
        except Exception as e:
            logger.error(f"Error en extracción NER: {e}")
        
        return entities
    
    def _is_duplicate_entity(self, entity: Entity, entities: List[Entity]) -> bool:
        """
        Verifica si una entidad es duplicada.
        
        Args:
            entity: Entidad a verificar
            entities: Lista de entidades existentes
            
        Returns:
            True si es duplicada, False en caso contrario
        """
        # Criterios de duplicación
        for existing in entities:
            # Mismo texto y posición
            if (entity.name == existing.name and 
                abs(entity.start_pos - existing.start_pos) <= 3):
                return True
            
            # Solapamiento significativo
            if (entity.start_pos < existing.end_pos and 
                entity.end_pos > existing.start_pos):
                # Si son del mismo tipo, considerar duplicado
                if entity.category == existing.category:
                    return True
                # Si uno contiene completamente al otro y tiene mayor confianza
                if ((entity.start_pos >= existing.start_pos and 
                     entity.end_pos <= existing.end_pos) or
                    (existing.start_pos >= entity.start_pos and 
                     existing.end_pos <= entity.end_pos)):
                    # Mantener el de mayor confianza
                    return entity.confidence <= existing.confidence
        
        return False
    
    def _post_process_entities(self, entities: List[Entity], text: str, context: Dict[str, Any]) -> List[Entity]:
        """
        Realiza post-procesamiento de entidades extraídas.
        
        Args:
            entities: Lista de entidades a procesar
            text: Texto original
            context: Contexto adicional
            
        Returns:
            Lista de entidades procesadas
        """
        # Ordenar por posición
        entities.sort(key=lambda e: (e.start_pos, -e.end_pos))
        
        # Filtrar solapamientos
        non_overlapping = []
        for entity in entities:
            if not any(self._overlaps(entity, existing) for existing in non_overlapping):
                non_overlapping.append(entity)
            elif any(self._is_contained(entity, existing) and entity.confidence > existing.confidence 
                   for existing in non_overlapping):
                # Reemplazar entidad existente si esta es mejor
                for i, existing in enumerate(non_overlapping):
                    if self._is_contained(entity, existing) and entity.confidence > existing.confidence:
                        non_overlapping[i] = entity
                        break
        
        # Normalizar valores específicos
        processed = []
        for entity in non_overlapping:
            # Procesamiento específico por tipo
            if entity.category == EntityCategory.TEMPORAL:
                entity = self._normalize_temporal_entity(entity)
            elif entity.category == EntityCategory.NUMERIC:
                entity = self._normalize_numeric_entity(entity)
            elif entity.category == EntityCategory.CODE:
                entity = self._process_code_entity(entity, text)
            
            processed.append(entity)
        
        # Inferir relaciones entre entidades
        self._infer_entity_relations(processed, text, context)
        
        return processed
    
    def _overlaps(self, entity1: Entity, entity2: Entity) -> bool:
        """
        Verifica si dos entidades se solapan en el texto.
        
        Args:
            entity1: Primera entidad
            entity2: Segunda entidad
            
        Returns:
            True si hay solapamiento, False en caso contrario
        """
        return (entity1.start_pos < entity2.end_pos and 
                entity1.end_pos > entity2.start_pos)
    
    def _is_contained(self, entity1: Entity, entity2: Entity) -> bool:
        """
        Verifica si una entidad está contenida dentro de otra.
        
        Args:
            entity1: Primera entidad
            entity2: Segunda entidad
            
        Returns:
            True si entity1 está contenida en entity2 o viceversa
        """
        return ((entity1.start_pos >= entity2.start_pos and entity1.end_pos <= entity2.end_pos) or
                (entity2.start_pos >= entity1.start_pos and entity2.end_pos <= entity1.end_pos))
    
    def _normalize_temporal_entity(self, entity: Entity) -> Entity:
        """
        Normaliza entidades temporales a formatos estándar.
        
        Args:
            entity: Entidad temporal a normalizar
            
        Returns:
            Entidad normalizada
        """
        if entity.subtype == EntitySubType.DATE:
            # Intentar normalizar a formato ISO
            try:
                # Detectar formato
                if re.match(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}', entity.value):
                    # DD/MM/YYYY
                    day, month, year = re.split(r'[/-]', entity.value)
                    normalized = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    entity.value = normalized
                elif re.match(r'\d{4}[/-]\d{1,2}[/-]\d{1,2}', entity.value):
                    # YYYY/MM/DD
                    year, month, day = re.split(r'[/-]', entity.value)
                    normalized = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    entity.value = normalized
                elif re.match(r'\d{1,2}[/-]\d{1,2}[/-]\d{2}', entity.value):
                    # DD/MM/YY
                    day, month, year = re.split(r'[/-]', entity.value)
                    year = f"20{year}" if int(year) < 50 else f"19{year}"  # Heurística simple
                    normalized = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    entity.value = normalized
            except Exception as e:
                logger.debug(f"Error al normalizar fecha: {e}")
        
        elif entity.subtype == EntitySubType.TIME:
            # Intentar normalizar a formato 24h
            try:
                if "am" in entity.value.lower() or "pm" in entity.value.lower():
                    # Convertir de 12h a 24h
                    time_part = re.sub(r'[aApP][mM]', '', entity.value).strip()
                    is_pm = "pm" in entity.value.lower()
                    
                    hours, minutes = time_part.split(":")[:2]
                    hours = int(hours)
                    
                    if is_pm and hours < 12:
                        hours += 12
                    elif not is_pm and hours == 12:
                        hours = 0
                    
                    normalized = f"{hours:02d}:{minutes}"
                    entity.value = normalized
            except Exception as e:
                logger.debug(f"Error al normalizar hora: {e}")
        
        return entity
    
    def _normalize_numeric_entity(self, entity: Entity) -> Entity:
        """
        Normaliza entidades numéricas a formatos estándar.
        
        Args:
            entity: Entidad numérica a normalizar
            
        Returns:
            Entidad normalizada
        """
        if entity.subtype == EntitySubType.FLOAT:
            # Convertir a float estándar
            try:
                # Manejar diferentes separadores decimales
                normalized = entity.value.replace(',', '.')
                entity.value = str(float(normalized))
            except ValueError:
                pass
        
        elif entity.subtype == EntitySubType.PERCENTAGE:
            # Extraer valor numérico
            try:
                numeric_part = re.sub(r'[%]', '', entity.value).strip()
                numeric_part = numeric_part.replace(',', '.')
                value = float(numeric_part)
                entity.attributes["numeric_value"] = value
            except ValueError:
                pass
        
        elif entity.subtype == EntitySubType.MONETARY:
            # Extraer valor y moneda
            try:
                # Extraer moneda
                currency = None
                if '€' in entity.value or 'EUR' in entity.value:
                    currency = "EUR"
                elif '$' in entity.value or 'USD' in entity.value:
                    currency = "USD"
                
                # Extraer valor numérico
                numeric_part = re.sub(r'[€$USD]', '', entity.value).strip()
                numeric_part = numeric_part.replace(',', '.')
                value = float(numeric_part)
                
                entity.attributes["currency"] = currency
                entity.attributes["numeric_value"] = value
            except ValueError:
                pass
        
        return entity
    
    def _process_code_entity(self, entity: Entity, text: str) -> Entity:
        """
        Procesa entidades de código con información adicional.
        
        Args:
            entity: Entidad de código a procesar
            text: Texto original
            
        Returns:
            Entidad procesada
        """
        if entity.subtype == EntitySubType.CODE_SNIPPET:
            # Extraer contenido sin comillas
            if entity.value.startswith('`') and entity.value.endswith('`'):
                entity.value = entity.value[1:-1]
        
        elif entity.subtype == EntitySubType.FUNCTION_NAME:
            # Extraer nombre de función
            match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\(', entity.value)
            if match:
                entity.attributes["function_name"] = match.group(1)
                # Extraer parámetros
                params_match = re.match(r'[^(]*$$([^)]*)$$', entity.value)
                if params_match:
                    params = params_match.group(1).strip()
                    if params:
                        entity.attributes["parameters"] = params.split(',')
        
        return entity
    
    def _infer_entity_relations(self, entities: List[Entity], text: str, context: Dict[str, Any]) -> None:
        """
        Infiere relaciones entre entidades basándose en patrones.
        
        Args:
            entities: Lista de entidades
            text: Texto original
            context: Contexto adicional
        """
        # Patrones de relaciones comunes
        patterns = [
            # Pertenencia: X de Y
            (r'\b(.*?)\s+de\s+(.*?)\b', "is_part_of"),
            # Creación: X creado por Y
            (r'\b(.*?)\s+creado\s+por\s+(.*?)\b', "created_by"),
            # Ubicación: X en Y
            (r'\b(.*?)\s+en\s+(.*?)\b', "located_in"),
            # Empleo: X trabaja en/para Y
            (r'\b(.*?)\s+trabaja\s+(?:en|para)\s+(.*?)\b', "employed_by"),
            # Dependencia: X depende de Y
            (r'\b(.*?)\s+depende\s+de\s+(.*?)\b', "depends_on")
        ]
        
        # Indexar entidades por posición
        entities_by_position = {(e.start_pos, e.end_pos): e for e in entities}
        
        # Buscar relaciones por patrones
        for pattern, relation_type in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Encontrar entidades en las posiciones del patrón
                start1, end1 = match.span(1)
                start2, end2 = match.span(2)
                
                # Buscar entidades en esas posiciones
                entity1 = None
                entity2 = None
                
                for (start, end), entity in entities_by_position.items():
                    # Solapamiento significativo con la primera parte
                    if (start <= start1 < end) or (start < end1 <= end) or (start1 <= start < end1):
                        entity1 = entity
                    # Solapamiento significativo con la segunda parte
                    if (start <= start2 < end) or (start < end2 <= end) or (start2 <= start < end2):
                        entity2 = entity
                
                # Si se encontraron ambas entidades, crear relación
                if entity1 and entity2:
                    entity1.add_relation(entity2.id, relation_type)
        
        # Inferir relaciones por cercanía y tipo
        for i, entity1 in enumerate(entities):
            for j, entity2 in enumerate(entities[i+1:], i+1):
                # Relaciones específicas por tipo
                if (entity1.category == EntityCategory.PERSON and 
                    entity2.category == EntityCategory.ORGANIZATION):
                    # Persona - Organización
                    # Verificar si están cercanas (dentro de 20 tokens)
                    if abs(entity2.start_pos - entity1.end_pos) < 20:
                        entity1.add_relation(entity2.id, "employed_by")
                
                elif (entity1.category == EntityCategory.TECHNOLOGY and 
                      entity1.subtype == EntitySubType.PROGRAMMING_LANGUAGE and
                      entity2.category == EntityCategory.TECHNOLOGY and
                      entity2.subtype == EntitySubType.FRAMEWORK):
                    # Lenguaje - Framework (potencial dependencia)
                    if abs(entity2.start_pos - entity1.end_pos) < 15:
                        entity2.add_relation(entity1.id, "depends_on")
    
    def create_entity_group(self, name: str, category: EntityCategory, 
                           entity_ids: List[str] = None) -> Optional[str]:
        """
        Crea un nuevo grupo de entidades.
        
        Args:
            name: Nombre del grupo
            category: Categoría principal del grupo
            entity_ids: Lista de IDs de entidades (opcional)
            
        Returns:
            ID del grupo creado, o None si falla
        """
        try:
            group_id = str(uuid.uuid4())
            group = EntityGroup(
                id=group_id,
                name=name,
                category=category,
                entities=set(entity_ids or [])
            )
            
            self.entity_groups[group_id] = group
            logger.debug(f"Creado grupo de entidades: {name}")
            return group_id
        except Exception as e:
            logger.error(f"Error al crear grupo de entidades: {e}")
            return None
    
    def add_entity_to_group(self, group_id: str, entity_id: str) -> bool:
        """
        Añade una entidad a un grupo.
        
        Args:
            group_id: ID del grupo
            entity_id: ID de la entidad
            
        Returns:
            True si se añadió correctamente, False en caso contrario
        """
        if group_id not in self.entity_groups:
            logger.warning(f"Grupo no encontrado: {group_id}")
            return False
        
        if entity_id not in self.entity_cache:
            logger.warning(f"Entidad no encontrada: {entity_id}")
            return False
        
        self.entity_groups[group_id].add_entity(entity_id)
        return True
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """
        Obtiene una entidad por su ID.
        
        Args:
            entity_id: ID de la entidad
            
        Returns:
            Entidad encontrada, o None si no existe
        """
        return self.entity_cache.get(entity_id)
    
    def get_entity_group(self, group_id: str) -> Optional[EntityGroup]:
        """
        Obtiene un grupo de entidades por su ID.
        
        Args:
            group_id: ID del grupo
            
        Returns:
            Grupo encontrado, o None si no existe
        """
        return self.entity_groups.get(group_id)
    
    def get_rules(self) -> Dict[str, ExtractionRule]:
        """
        Obtiene todas las reglas de extracción.
        
        Returns:
            Diccionario de reglas
        """
        return self.rules
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de extracción.
        
        Returns:
            Diccionario de estadísticas
        """
        # Añadir promedio de tiempo de extracción
        if self.stats["extraction_times"]:
            self.stats["avg_extraction_time"] = sum(self.stats["extraction_times"]) / len(self.stats["extraction_times"])
        else:
            self.stats["avg_extraction_time"] = 0.0
        
        return self.stats
    
    def clear_cache(self) -> int:
        """
        Limpia la caché de entidades.
        
        Returns:
            Número de entidades eliminadas
        """
        count = len(self.entity_cache)
        self.entity_cache.clear()
        return count
    
    def save_entities_to_file(self, filename: str) -> bool:
        """
        Guarda las entidades extraídas en un archivo JSON.
        
        Args:
            filename: Ruta del archivo
            
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        try:
            entities_dict = {
                entity_id: entity.to_dict() 
                for entity_id, entity in self.entity_cache.items()
            }
            
            groups_dict = {
                group_id: group.to_dict()
                for group_id, group in self.entity_groups.items()
            }
            
            data = {
                "entities": entities_dict,
                "groups": groups_dict,
                "timestamp": datetime.datetime.now().isoformat(),
                "stats": self.get_stats()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Entidades guardadas en {filename}")
            return True
        except Exception as e:
            logger.error(f"Error al guardar entidades: {e}")
            return False
    
    def load_entities_from_file(self, filename: str) -> bool:
        """
        Carga entidades desde un archivo JSON.
        
        Args:
            filename: Ruta del archivo
            
        Returns:
            True si se cargó correctamente, False en caso contrario
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Cargar entidades
            entities_dict = data.get("entities", {})
            for entity_id, entity_data in entities_dict.items():
                self.entity_cache[entity_id] = Entity.from_dict(entity_data)
            
            # Cargar grupos
            groups_dict = data.get("groups", {})
            for group_id, group_data in groups_dict.items():
                self.entity_groups[group_id] = EntityGroup.from_dict(group_data)
            
            logger.info(f"Cargadas {len(entities_dict)} entidades y {len(groups_dict)} grupos desde {filename}")
            return True
        except Exception as e:
            logger.error(f"Error al cargar entidades: {e}")
            return False

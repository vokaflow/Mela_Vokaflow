"""
Tipos de Entidades para el Sistema de Extracción
------------------------------------------------

Este módulo define los tipos de entidades que el sistema puede identificar,
junto con sus atributos, relaciones y clasificaciones específicas.

Proporciona una estructura de datos coherente para representar entidades
de diversos dominios, facilitando su extracción, almacenamiento y uso
en el procesamiento conversacional.

Autor: Equipo VokaFlow
Versión: 1.0.0
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Set, Tuple
import datetime


class EntityCategory(Enum):
    """Categorías principales de entidades."""
    PERSON = auto()
    ORGANIZATION = auto()
    LOCATION = auto()
    TECHNOLOGY = auto()
    TEMPORAL = auto()
    NUMERIC = auto()
    CONCEPT = auto()
    CODE = auto()
    REFERENCE = auto()
    CUSTOM = auto()
    UNKNOWN = auto()


class EntitySubType(Enum):
    """Subtipos específicos de entidades por categoría."""
    # Personas
    PERSON_NAME = auto()
    PERSON_TITLE = auto()
    PERSON_ROLE = auto()
    
    # Organizaciones
    COMPANY = auto()
    GOVERNMENT = auto()
    NON_PROFIT = auto()
    INSTITUTION = auto()
    
    # Ubicaciones
    COUNTRY = auto()
    CITY = auto()
    ADDRESS = auto()
    COORDINATES = auto()
    
    # Tecnología
    PROGRAMMING_LANGUAGE = auto()
    FRAMEWORK = auto()
    LIBRARY = auto()
    DATABASE = auto()
    PLATFORM = auto()
    HARDWARE = auto()
    
    # Temporal
    DATE = auto()
    TIME = auto()
    DATETIME = auto()
    DURATION = auto()
    TIMESPAN = auto()
    
    # Numéricos
    INTEGER = auto()
    FLOAT = auto()
    PERCENTAGE = auto()
    MONETARY = auto()
    
    # Concepto
    TECHNICAL_TERM = auto()
    SCIENTIFIC_CONCEPT = auto()
    METHODOLOGY = auto()
    THEORY = auto()
    
    # Código
    CODE_SNIPPET = auto()
    FUNCTION_NAME = auto()
    CLASS_NAME = auto()
    VARIABLE = auto()
    FILE_PATH = auto()
    URL = auto()
    
    # Referencias
    DOCUMENT = auto()
    BOOK = auto()
    ARTICLE = auto()
    WEBSITE = auto()
    
    # Generales
    CUSTOM_TYPE = auto()
    UNKNOWN_TYPE = auto()


@dataclass
class Entity:
    """
    Entidad extraída del texto.
    
    Representa cualquier elemento identificable en el texto con relevancia
    semántica, incluyendo personas, organizaciones, conceptos, etc.
    
    Attributes:
        id: Identificador único de la entidad
        name: Nombre o texto de la entidad
        category: Categoría principal de la entidad
        subtype: Subtipo específico de la entidad
        value: Valor normalizado o procesado de la entidad
        start_pos: Posición inicial en el texto original
        end_pos: Posición final en el texto original
        confidence: Nivel de confianza en la extracción (0.0-1.0)
        source: Método o fuente de extracción
        attributes: Atributos adicionales específicos del tipo
        relations: Relaciones con otras entidades
        mentions: Lista de menciones adicionales en el texto
        created_at: Timestamp de creación
        last_updated: Timestamp de última actualización
    """
    id: str
    name: str
    category: EntityCategory
    subtype: Optional[EntitySubType] = None
    value: Any = None
    start_pos: int = -1
    end_pos: int = -1
    confidence: float = 1.0
    source: str = "rule_based"
    attributes: Dict[str, Any] = field(default_factory=dict)
    relations: List[Tuple[str, str]] = field(default_factory=list)  # [(entity_id, relation_type), ...]
    mentions: List[Tuple[int, int, float]] = field(default_factory=list)  # [(start, end, confidence), ...]
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    last_updated: datetime.datetime = field(default_factory=datetime.datetime.now)
    
    def __post_init__(self):
        """Validación después de la inicialización."""
        # Validar confianza
        if not 0 <= self.confidence <= 1.0:
            self.confidence = max(0.0, min(self.confidence, 1.0))
        
        # Asegurar que value está establecido
        if self.value is None:
            self.value = self.name
    
    def add_mention(self, start: int, end: int, confidence: float = 1.0) -> None:
        """
        Añade una mención adicional de la entidad en el texto.
        
        Args:
            start: Posición inicial
            end: Posición final
            confidence: Nivel de confianza
        """
        self.mentions.append((start, end, confidence))
        self.last_updated = datetime.datetime.now()
    
    def add_relation(self, entity_id: str, relation_type: str) -> None:
        """
        Añade una relación con otra entidad.
        
        Args:
            entity_id: ID de la entidad relacionada
            relation_type: Tipo de relación
        """
        relation = (entity_id, relation_type)
        if relation not in self.relations:
            self.relations.append(relation)
            self.last_updated = datetime.datetime.now()
    
    def update_attribute(self, key: str, value: Any) -> None:
        """
        Actualiza o añade un atributo a la entidad.
        
        Args:
            key: Nombre del atributo
            value: Valor del atributo
        """
        self.attributes[key] = value
        self.last_updated = datetime.datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la entidad a un diccionario para serialización.
        
        Returns:
            Diccionario con los datos de la entidad
        """
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.name,
            "subtype": self.subtype.name if self.subtype else None,
            "value": self.value,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "confidence": self.confidence,
            "source": self.source,
            "attributes": self.attributes,
            "relations": self.relations,
            "mentions": self.mentions,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """
        Crea una entidad a partir de un diccionario.
        
        Args:
            data: Diccionario con datos de entidad
            
        Returns:
            Nueva instancia de Entity
        """
        # Convertir strings a enums
        category = EntityCategory[data["category"]] if "category" in data else EntityCategory.UNKNOWN
        subtype = None
        if "subtype" in data and data["subtype"]:
            try:
                subtype = EntitySubType[data["subtype"]]
            except (KeyError, ValueError):
                subtype = EntitySubType.UNKNOWN_TYPE
        
        # Convertir strings a datetime
        created_at = datetime.datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.datetime.now()
        last_updated = datetime.datetime.fromisoformat(data["last_updated"]) if "last_updated" in data else datetime.datetime.now()
        
        return cls(
            id=data["id"],
            name=data["name"],
            category=category,
            subtype=subtype,
            value=data.get("value", data["name"]),
            start_pos=data.get("start_pos", -1),
            end_pos=data.get("end_pos", -1),
            confidence=data.get("confidence", 1.0),
            source=data.get("source", "rule_based"),
            attributes=data.get("attributes", {}),
            relations=data.get("relations", []),
            mentions=data.get("mentions", []),
            created_at=created_at,
            last_updated=last_updated
        )


@dataclass
class EntityGroup:
    """
    Agrupación de entidades relacionadas.
    
    Permite organizar entidades relacionadas bajo un concepto común,
    facilitando su gestión y uso en el procesamiento contextual.
    
    Attributes:
        id: Identificador único del grupo
        name: Nombre descriptivo del grupo
        category: Categoría principal del grupo
        entities: Conjunto de IDs de entidades en el grupo
        relevance: Relevancia del grupo en el contexto actual (0.0-1.0)
        attributes: Atributos adicionales del grupo
        created_at: Timestamp de creación
        last_updated: Timestamp de última actualización
    """
    id: str
    name: str
    category: EntityCategory
    entities: Set[str] = field(default_factory=set)
    relevance: float = 0.5
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    last_updated: datetime.datetime = field(default_factory=datetime.datetime.now)
    
    def add_entity(self, entity_id: str) -> None:
        """
        Añade una entidad al grupo.
        
        Args:
            entity_id: ID de la entidad a añadir
        """
        self.entities.add(entity_id)
        self.last_updated = datetime.datetime.now()
    
    def remove_entity(self, entity_id: str) -> bool:
        """
        Elimina una entidad del grupo.
        
        Args:
            entity_id: ID de la entidad a eliminar
            
        Returns:
            True si se eliminó correctamente, False si no existía
        """
        if entity_id in self.entities:
            self.entities.remove(entity_id)
            self.last_updated = datetime.datetime.now()
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el grupo a un diccionario para serialización.
        
        Returns:
            Diccionario con los datos del grupo
        """
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.name,
            "entities": list(self.entities),
            "relevance": self.relevance,
            "attributes": self.attributes,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EntityGroup':
        """
        Crea un grupo a partir de un diccionario.
        
        Args:
            data: Diccionario con datos del grupo
            
        Returns:
            Nueva instancia de EntityGroup
        """
        # Convertir strings a enums
        category = EntityCategory[data["category"]] if "category" in data else EntityCategory.UNKNOWN
        
        # Convertir strings a datetime
        created_at = datetime.datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.datetime.now()
        last_updated = datetime.datetime.fromisoformat(data["last_updated"]) if "last_updated" in data else datetime.datetime.now()
        
        return cls(
            id=data["id"],
            name=data["name"],
            category=category,
            entities=set(data.get("entities", [])),
            relevance=data.get("relevance", 0.5),
            attributes=data.get("attributes", {}),
            created_at=created_at,
            last_updated=last_updated
        )


# Definiciones de relaciones entre entidades
ENTITY_RELATIONS = {
    "is_part_of": "Relación parte-todo",
    "is_related_to": "Relación general",
    "is_similar_to": "Similitud semántica",
    "is_synonym_of": "Sinonimia",
    "depends_on": "Dependencia",
    "created_by": "Creación",
    "owned_by": "Propiedad",
    "located_in": "Ubicación",
    "employed_by": "Empleo",
    "member_of": "Membresía",
    "precedes": "Precedencia temporal",
    "causes": "Causalidad",
    "derives_from": "Derivación",
    "contradicts": "Contradicción",
    "instance_of": "Instanciación",
    "has_property": "Propiedad",
    "has_function": "Función",
    "used_for": "Utilidad",
    "references": "Referencia",
    "custom_relation": "Relación personalizada"
}

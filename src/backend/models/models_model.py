from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class ModelType(str, Enum):
    LLM = "llm"
    TTS = "tts"
    STT = "stt"
    TRANSLATION = "translation"
    EMBEDDING = "embedding"
    VISION = "vision"
    AUDIO = "audio"
    CUSTOM = "custom"

class ModelStatusEnum(str, Enum):
    AVAILABLE = "available"
    LOADING = "loading"
    LOADED = "loaded"
    UNLOADING = "unloading"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"

class ModelSize(str, Enum):
    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    XLARGE = "xlarge"

class ModelPrecision(str, Enum):
    FP32 = "fp32"
    FP16 = "fp16"
    INT8 = "int8"
    INT4 = "int4"

class ModelInfo(BaseModel):
    id: str = Field(..., description="ID único del modelo")
    name: str = Field(..., description="Nombre del modelo")
    display_name: str = Field(..., description="Nombre para mostrar")
    description: str = Field(..., description="Descripción del modelo")
    type: ModelType = Field(..., description="Tipo de modelo")
    version: str = Field(..., description="Versión del modelo")
    size: ModelSize = Field(..., description="Tamaño del modelo")
    precision: ModelPrecision = Field(default=ModelPrecision.FP16, description="Precisión")
    file_size: int = Field(..., description="Tamaño del archivo en bytes")
    memory_required: int = Field(..., description="Memoria requerida en MB")
    languages: List[str] = Field(default_factory=list, description="Idiomas soportados")
    capabilities: List[str] = Field(default_factory=list, description="Capacidades")
    parameters: Optional[int] = Field(None, description="Número de parámetros")
    context_length: Optional[int] = Field(None, description="Longitud de contexto")
    license: str = Field(default="unknown", description="Licencia del modelo")
    author: str = Field(default="unknown", description="Autor/Organización")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")
    updated_at: datetime = Field(default_factory=datetime.now, description="Última actualización")

class ModelStatus(BaseModel):
    model_id: str = Field(..., description="ID del modelo")
    status: ModelStatusEnum = Field(..., description="Estado actual")
    loaded_at: Optional[datetime] = Field(None, description="Fecha de carga")
    memory_usage: Optional[int] = Field(None, description="Uso de memoria en MB")
    gpu_usage: Optional[float] = Field(None, description="Uso de GPU %")
    requests_count: int = Field(default=0, description="Número de peticiones")
    avg_response_time: Optional[float] = Field(None, description="Tiempo promedio de respuesta")
    last_used: Optional[datetime] = Field(None, description="Último uso")
    error_message: Optional[str] = Field(None, description="Mensaje de error si aplica")
    health_score: float = Field(default=100.0, ge=0, le=100, description="Puntuación de salud")

class ModelConfig(BaseModel):
    model_id: str = Field(..., description="ID del modelo")
    max_tokens: Optional[int] = Field(None, description="Máximo de tokens")
    temperature: Optional[float] = Field(None, ge=0, le=2, description="Temperatura")
    top_p: Optional[float] = Field(None, ge=0, le=1, description="Top-p sampling")
    top_k: Optional[int] = Field(None, ge=1, description="Top-k sampling")
    repetition_penalty: Optional[float] = Field(None, ge=0, le=2, description="Penalización por repetición")
    batch_size: Optional[int] = Field(None, ge=1, description="Tamaño de lote")
    use_gpu: bool = Field(default=True, description="Usar GPU si está disponible")
    precision: Optional[ModelPrecision] = Field(None, description="Precisión de cálculo")
    custom_params: Optional[Dict[str, Any]] = Field(None, description="Parámetros personalizados")

class ModelLoadRequest(BaseModel):
    model_id: str = Field(..., description="ID del modelo a cargar")
    force_reload: bool = Field(default=False, description="Forzar recarga si ya está cargado")
    config: Optional[ModelConfig] = Field(None, description="Configuración específica")
    priority: int = Field(default=5, ge=1, le=10, description="Prioridad de carga")

class ModelUnloadRequest(BaseModel):
    model_id: str = Field(..., description="ID del modelo a descargar")
    force: bool = Field(default=False, description="Forzar descarga")
    save_state: bool = Field(default=True, description="Guardar estado antes de descargar")

class ModelOperation(BaseModel):
    operation_id: str = Field(..., description="ID de la operación")
    model_id: str = Field(..., description="ID del modelo")
    operation_type: str = Field(..., description="Tipo de operación")
    status: str = Field(..., description="Estado de la operación")
    progress: float = Field(default=0, ge=0, le=100, description="Progreso %")
    started_at: datetime = Field(default_factory=datetime.now, description="Inicio")
    completed_at: Optional[datetime] = Field(None, description="Finalización")
    message: str = Field(default="", description="Mensaje de estado")
    error: Optional[str] = Field(None, description="Error si aplica")

class ModelMetrics(BaseModel):
    model_id: str = Field(..., description="ID del modelo")
    total_requests: int = Field(..., description="Total de peticiones")
    successful_requests: int = Field(..., description="Peticiones exitosas")
    failed_requests: int = Field(..., description="Peticiones fallidas")
    avg_response_time: float = Field(..., description="Tiempo promedio de respuesta")
    min_response_time: float = Field(..., description="Tiempo mínimo de respuesta")
    max_response_time: float = Field(..., description="Tiempo máximo de respuesta")
    tokens_processed: int = Field(..., description="Tokens procesados")
    memory_peak: int = Field(..., description="Pico de memoria en MB")
    uptime: str = Field(..., description="Tiempo activo")
    last_24h_requests: int = Field(..., description="Peticiones últimas 24h")

class ModelBenchmark(BaseModel):
    model_id: str = Field(..., description="ID del modelo")
    benchmark_type: str = Field(..., description="Tipo de benchmark")
    score: float = Field(..., description="Puntuación")
    metrics: Dict[str, float] = Field(..., description="Métricas detalladas")
    test_date: datetime = Field(..., description="Fecha del test")
    hardware_info: Dict[str, Any] = Field(..., description="Información del hardware")

class ModelResponse(BaseModel):
    success: bool = Field(default=True)
    message: str = Field(default="Operation completed successfully")
    data: Any = Field(..., description="Datos de respuesta")
    timestamp: datetime = Field(default_factory=datetime.now)

class ModelRegistry(BaseModel):
    total_models: int = Field(..., description="Total de modelos")
    loaded_models: int = Field(..., description="Modelos cargados")
    available_memory: int = Field(..., description="Memoria disponible en MB")
    used_memory: int = Field(..., description="Memoria usada en MB")
    models_by_type: Dict[str, int] = Field(..., description="Modelos por tipo")
    models_by_status: Dict[str, int] = Field(..., description="Modelos por estado")
    recent_activity: List[Dict[str, Any]] = Field(..., description="Actividad reciente")

class ModelCompatibility(BaseModel):
    model_id: str = Field(..., description="ID del modelo")
    compatible: bool = Field(..., description="Es compatible")
    requirements: Dict[str, Any] = Field(..., description="Requisitos")
    missing_dependencies: List[str] = Field(default_factory=list, description="Dependencias faltantes")
    warnings: List[str] = Field(default_factory=list, description="Advertencias")
    recommendations: List[str] = Field(default_factory=list, description="Recomendaciones")

class ModelUpdate(BaseModel):
    model_id: str = Field(..., description="ID del modelo")
    display_name: Optional[str] = Field(None, description="Nuevo nombre para mostrar")
    description: Optional[str] = Field(None, description="Nueva descripción")
    config: Optional[ModelConfig] = Field(None, description="Nueva configuración")
    enabled: Optional[bool] = Field(None, description="Habilitar/deshabilitar")
    priority: Optional[int] = Field(None, ge=1, le=10, description="Nueva prioridad")

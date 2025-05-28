from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Dict, Any, Optional
import asyncio
import uuid
import random
from datetime import datetime, timedelta

from ..models.models_model import (
    ModelInfo, ModelStatus, ModelConfig, ModelLoadRequest, ModelUnloadRequest,
    ModelOperation, ModelMetrics, ModelBenchmark, ModelResponse, ModelRegistry,
    ModelCompatibility, ModelUpdate, ModelType, ModelStatusEnum,
    ModelSize, ModelPrecision
)

router = APIRouter(tags=["Models"])

# Simulación de base de datos en memoria
models_db = {
    "models": {},
    "loaded_models": {},
    "operations": {},
    "configs": {},
    "metrics": {},
    "registry": {
        "total_models": 0,
        "loaded_models": 0,
        "available_memory": 16384,  # 16GB
        "used_memory": 0
    }
}

def initialize_sample_models():
    """Inicializar modelos de ejemplo"""
    if not models_db["models"]:
        sample_models = [
            {
                "id": "qwen-7b-chat",
                "name": "Qwen 7B Chat",
                "display_name": "Qwen 7B Chat",
                "description": "Modelo de chat conversacional de 7B parámetros",
                "type": ModelType.LLM,
                "version": "1.5",
                "size": ModelSize.LARGE,
                "precision": ModelPrecision.FP16,
                "file_size": 14000000000,  # 14GB
                "memory_required": 8192,   # 8GB
                "languages": ["en", "es", "fr", "de", "zh"],
                "capabilities": ["chat", "completion", "reasoning"],
                "parameters": 7000000000,
                "context_length": 8192,
                "license": "Apache 2.0",
                "author": "Alibaba"
            },
            {
                "id": "whisper-large-v3",
                "name": "Whisper Large V3",
                "display_name": "Whisper Large V3",
                "description": "Modelo de reconocimiento de voz multiidioma",
                "type": ModelType.STT,
                "version": "3.0",
                "size": ModelSize.LARGE,
                "precision": ModelPrecision.FP32,
                "file_size": 3000000000,   # 3GB
                "memory_required": 4096,   # 4GB
                "languages": ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
                "capabilities": ["transcription", "translation", "voice_activity_detection"],
                "parameters": 1550000000,
                "license": "MIT",
                "author": "OpenAI"
            },
            {
                "id": "xtts-v2",
                "name": "XTTS v2",
                "display_name": "Coqui XTTS v2",
                "description": "Modelo de síntesis de voz con clonación",
                "type": ModelType.TTS,
                "version": "2.0",
                "size": ModelSize.MEDIUM,
                "precision": ModelPrecision.FP16,
                "file_size": 1800000000,   # 1.8GB
                "memory_required": 2048,   # 2GB
                "languages": ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh", "ja", "hu", "ko"],
                "capabilities": ["tts", "voice_cloning", "multilingual"],
                "license": "MPL 2.0",
                "author": "Coqui"
            },
            {
                "id": "nllb-200-distilled-600m",
                "name": "NLLB 200 Distilled 600M",
                "display_name": "NLLB 200 (600M)",
                "description": "Modelo de traducción para 200 idiomas",
                "type": ModelType.TRANSLATION,
                "version": "1.0",
                "size": ModelSize.MEDIUM,
                "precision": ModelPrecision.FP16,
                "file_size": 1200000000,   # 1.2GB
                "memory_required": 1536,   # 1.5GB
                "languages": ["en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko", "ar", "hi"],
                "capabilities": ["translation", "multilingual"],
                "parameters": 600000000,
                "license": "CC BY-NC 4.0",
                "author": "Meta"
            },
            {
                "id": "all-minilm-l6-v2",
                "name": "All MiniLM L6 v2",
                "display_name": "All MiniLM L6 v2",
                "description": "Modelo de embeddings para similitud semántica",
                "type": ModelType.EMBEDDING,
                "version": "2.0",
                "size": ModelSize.SMALL,
                "precision": ModelPrecision.FP32,
                "file_size": 90000000,     # 90MB
                "memory_required": 256,    # 256MB
                "languages": ["en"],
                "capabilities": ["embeddings", "similarity", "clustering"],
                "parameters": 22700000,
                "license": "Apache 2.0",
                "author": "Microsoft"
            }
        ]
        
        for model_data in sample_models:
            model = ModelInfo(**model_data)
            models_db["models"][model.id] = model.dict()
        
        models_db["registry"]["total_models"] = len(sample_models)

def get_model_status(model_id: str) -> ModelStatus:
    """Obtener estado de un modelo"""
    if model_id in models_db["loaded_models"]:
        loaded_info = models_db["loaded_models"][model_id]
        return ModelStatus(
            model_id=model_id,
            status=ModelStatusEnum.LOADED,
            loaded_at=datetime.fromisoformat(loaded_info["loaded_at"]),
            memory_usage=loaded_info["memory_usage"],
            gpu_usage=loaded_info.get("gpu_usage", 0.0),
            requests_count=loaded_info.get("requests_count", 0),
            avg_response_time=loaded_info.get("avg_response_time"),
            last_used=datetime.fromisoformat(loaded_info["last_used"]) if loaded_info.get("last_used") else None,
            health_score=loaded_info.get("health_score", 100.0)
        )
    else:
        return ModelStatus(
            model_id=model_id,
            status=ModelStatusEnum.AVAILABLE,
            health_score=100.0
        )

@router.get("/list", response_model=ModelResponse)
async def list_models(
    type: Optional[ModelType] = Query(None, description="Filtrar por tipo de modelo"),
    status: Optional[ModelStatusEnum] = Query(None, description="Filtrar por estado"),
    size: Optional[ModelSize] = Query(None, description="Filtrar por tamaño"),
    language: Optional[str] = Query(None, description="Filtrar por idioma soportado"),
    loaded_only: bool = Query(False, description="Solo modelos cargados"),
    include_metrics: bool = Query(False, description="Incluir métricas")
):
    """
    📋 Listar modelos disponibles
    
    Obtiene lista de modelos con filtros:
    - Por tipo (LLM, TTS, STT, etc.)
    - Por estado (disponible, cargado, etc.)
    - Por tamaño y idiomas
    - Solo modelos cargados
    - Con métricas opcionales
    """
    try:
        initialize_sample_models()
        
        filtered_models = []
        
        for model_data in models_db["models"].values():
            model = ModelInfo(**model_data)
            
            # Aplicar filtros
            if type and model.type != type:
                continue
            if size and model.size != size:
                continue
            if language and language not in model.languages:
                continue
            
            # Obtener estado del modelo
            model_status = get_model_status(model.id)
            
            if status and model_status.status != status:
                continue
            if loaded_only and model_status.status != ModelStatusEnum.LOADED:
                continue
            
            # Crear respuesta del modelo
            model_response = {
                "info": model,
                "status": model_status
            }
            
            # Incluir métricas si se solicita
            if include_metrics and model.id in models_db["metrics"]:
                model_response["metrics"] = models_db["metrics"][model.id]
            
            filtered_models.append(model_response)
        
        # Ordenar por nombre
        filtered_models.sort(key=lambda x: x["info"].name)
        
        return ModelResponse(
            message=f"Retrieved {len(filtered_models)} models",
            data={
                "models": filtered_models,
                "total_available": len(models_db["models"]),
                "total_loaded": len(models_db["loaded_models"]),
                "filters_applied": {
                    "type": type,
                    "status": status,
                    "size": size,
                    "language": language,
                    "loaded_only": loaded_only
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing models: {str(e)}")

@router.post("/load", response_model=ModelResponse)
async def load_model(
    load_request: ModelLoadRequest,
    background_tasks: BackgroundTasks
):
    """
    🔄 Cargar modelo en memoria
    
    Carga un modelo específico:
    - Verificación de recursos disponibles
    - Carga progresiva con estado
    - Configuración personalizada
    - Manejo de errores y rollback
    """
    try:
        initialize_sample_models()
        
        if load_request.model_id not in models_db["models"]:
            raise HTTPException(status_code=404, detail="Model not found")
        
        model_info = ModelInfo(**models_db["models"][load_request.model_id])
        
        # Verificar si ya está cargado
        if load_request.model_id in models_db["loaded_models"] and not load_request.force_reload:
            return ModelResponse(
                message="Model already loaded",
                data={
                    "model_id": load_request.model_id,
                    "status": "already_loaded",
                    "loaded_at": models_db["loaded_models"][load_request.model_id]["loaded_at"]
                }
            )
        
        # Verificar memoria disponible
        available_memory = models_db["registry"]["available_memory"] - models_db["registry"]["used_memory"]
        if model_info.memory_required > available_memory:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient memory. Required: {model_info.memory_required}MB, Available: {available_memory}MB"
            )
        
        # Crear operación de carga
        operation_id = str(uuid.uuid4())
        operation = ModelOperation(
            operation_id=operation_id,
            model_id=load_request.model_id,
            operation_type="load",
            status="initiated",
            message="Model loading initiated"
        )
        
        models_db["operations"][operation_id] = operation.dict()
        
        # Función para cargar el modelo
        async def load_model_task():
            try:
                op_data = models_db["operations"][operation_id]
                
                # Fase 1: Preparación
                op_data["status"] = "preparing"
                op_data["progress"] = 10
                op_data["message"] = "Preparing model loading..."
                await asyncio.sleep(1)
                
                # Fase 2: Descarga/Verificación
                op_data["progress"] = 30
                op_data["message"] = "Verifying model files..."
                await asyncio.sleep(2)
                
                # Fase 3: Carga en memoria
                op_data["status"] = "loading"
                op_data["progress"] = 60
                op_data["message"] = "Loading model into memory..."
                await asyncio.sleep(3)
                
                # Fase 4: Inicialización
                op_data["progress"] = 80
                op_data["message"] = "Initializing model..."
                await asyncio.sleep(1)
                
                # Fase 5: Verificación final
                op_data["progress"] = 95
                op_data["message"] = "Running health checks..."
                await asyncio.sleep(1)
                
                # Completar carga
                loaded_info = {
                    "loaded_at": datetime.now().isoformat(),
                    "memory_usage": model_info.memory_required,
                    "gpu_usage": random.uniform(10, 50) if load_request.config and load_request.config.use_gpu else 0,
                    "requests_count": 0,
                    "health_score": 100.0,
                    "config": load_request.config.dict() if load_request.config else {}
                }
                
                models_db["loaded_models"][load_request.model_id] = loaded_info
                models_db["registry"]["loaded_models"] += 1
                models_db["registry"]["used_memory"] += model_info.memory_required
                
                # Guardar configuración si se proporciona
                if load_request.config:
                    models_db["configs"][load_request.model_id] = load_request.config.dict()
                
                op_data["status"] = "completed"
                op_data["progress"] = 100
                op_data["message"] = "Model loaded successfully"
                op_data["completed_at"] = datetime.now().isoformat()
                
            except Exception as e:
                op_data["status"] = "failed"
                op_data["error"] = str(e)
                op_data["message"] = f"Model loading failed: {str(e)}"
                op_data["completed_at"] = datetime.now().isoformat()
        
        # Ejecutar carga en background
        background_tasks.add_task(load_model_task)
        
        return ModelResponse(
            message="Model loading initiated",
            data={
                "operation_id": operation_id,
                "model_id": load_request.model_id,
                "estimated_time": "30-60 seconds",
                "memory_required": model_info.memory_required
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading model: {str(e)}")

@router.post("/unload", response_model=ModelResponse)
async def unload_model(
    unload_request: ModelUnloadRequest,
    background_tasks: BackgroundTasks
):
    """
    📤 Descargar modelo de memoria
    
    Descarga un modelo específico:
    - Verificación de uso activo
    - Guardado de estado opcional
    - Liberación de recursos
    - Limpieza de memoria
    """
    try:
        if unload_request.model_id not in models_db["loaded_models"]:
            raise HTTPException(status_code=404, detail="Model not loaded")
        
        loaded_info = models_db["loaded_models"][unload_request.model_id]
        
        # Verificar si está en uso (simulado)
        if loaded_info.get("requests_count", 0) > 0 and not unload_request.force:
            raise HTTPException(
                status_code=400, 
                detail="Model is currently processing requests. Use force=true to override."
            )
        
        # Crear operación de descarga
        operation_id = str(uuid.uuid4())
        operation = ModelOperation(
            operation_id=operation_id,
            model_id=unload_request.model_id,
            operation_type="unload",
            status="initiated",
            message="Model unloading initiated"
        )
        
        models_db["operations"][operation_id] = operation.dict()
        
        # Función para descargar el modelo
        async def unload_model_task():
            try:
                op_data = models_db["operations"][operation_id]
                
                # Fase 1: Preparación
                op_data["status"] = "preparing"
                op_data["progress"] = 20
                op_data["message"] = "Preparing model unloading..."
                await asyncio.sleep(1)
                
                # Fase 2: Guardar estado
                if unload_request.save_state:
                    op_data["progress"] = 40
                    op_data["message"] = "Saving model state..."
                    await asyncio.sleep(1)
                
                # Fase 3: Detener procesamiento
                op_data["progress"] = 60
                op_data["message"] = "Stopping model processing..."
                await asyncio.sleep(1)
                
                # Fase 4: Liberar memoria
                op_data["status"] = "unloading"
                op_data["progress"] = 80
                op_data["message"] = "Releasing memory..."
                await asyncio.sleep(2)
                
                # Completar descarga
                memory_freed = loaded_info["memory_usage"]
                del models_db["loaded_models"][unload_request.model_id]
                models_db["registry"]["loaded_models"] -= 1
                models_db["registry"]["used_memory"] -= memory_freed
                
                op_data["status"] = "completed"
                op_data["progress"] = 100
                op_data["message"] = "Model unloaded successfully"
                op_data["completed_at"] = datetime.now().isoformat()
                
            except Exception as e:
                op_data["status"] = "failed"
                op_data["error"] = str(e)
                op_data["message"] = f"Model unloading failed: {str(e)}"
                op_data["completed_at"] = datetime.now().isoformat()
        
        # Ejecutar descarga en background
        background_tasks.add_task(unload_model_task)
        
        return ModelResponse(
            message="Model unloading initiated",
            data={
                "operation_id": operation_id,
                "model_id": unload_request.model_id,
                "memory_to_free": loaded_info["memory_usage"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error unloading model: {str(e)}")

@router.get("/status", response_model=ModelResponse)
async def get_models_status(
    model_id: Optional[str] = Query(None, description="ID específico del modelo"),
    include_metrics: bool = Query(False, description="Incluir métricas detalladas")
):
    """
    📊 Obtener estado de los modelos
    
    Retorna estado actual de modelos:
    - Estado individual o de todos
    - Uso de memoria y GPU
    - Métricas de rendimiento
    - Información de salud
    """
    try:
        initialize_sample_models()
        
        if model_id:
            # Estado de un modelo específico
            if model_id not in models_db["models"]:
                raise HTTPException(status_code=404, detail="Model not found")
            
            model_status = get_model_status(model_id)
            response_data = {"model_status": model_status}
            
            if include_metrics and model_id in models_db["metrics"]:
                response_data["metrics"] = models_db["metrics"][model_id]
            
            return ModelResponse(
                message="Model status retrieved successfully",
                data=response_data
            )
        else:
            # Estado de todos los modelos
            all_status = []
            
            for model_id in models_db["models"].keys():
                model_status = get_model_status(model_id)
                status_data = {"model_status": model_status}
                
                if include_metrics and model_id in models_db["metrics"]:
                    status_data["metrics"] = models_db["metrics"][model_id]
                
                all_status.append(status_data)
            
            # Estadísticas generales
            registry = ModelRegistry(
                total_models=models_db["registry"]["total_models"],
                loaded_models=models_db["registry"]["loaded_models"],
                available_memory=models_db["registry"]["available_memory"],
                used_memory=models_db["registry"]["used_memory"],
                models_by_type={},
                models_by_status={},
                recent_activity=[]
            )
            
            # Contar por tipo y estado
            for model_data in models_db["models"].values():
                model = ModelInfo(**model_data)
                model_type = model.type.value
                registry.models_by_type[model_type] = registry.models_by_type.get(model_type, 0) + 1
                
                status = get_model_status(model.id).status.value
                registry.models_by_status[status] = registry.models_by_status.get(status, 0) + 1
            
            return ModelResponse(
                message=f"Retrieved status for {len(all_status)} models",
                data={
                    "models_status": all_status,
                    "registry": registry,
                    "system_info": {
                        "memory_usage_percent": (models_db["registry"]["used_memory"] / models_db["registry"]["available_memory"]) * 100,
                        "models_loaded_percent": (models_db["registry"]["loaded_models"] / models_db["registry"]["total_models"]) * 100 if models_db["registry"]["total_models"] > 0 else 0
                    }
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving models status: {str(e)}")

@router.put("/config", response_model=ModelResponse)
async def configure_model(config: ModelConfig):
    """
    ⚙️ Configurar parámetros del modelo
    
    Actualiza configuración de un modelo:
    - Parámetros de generación
    - Configuración de hardware
    - Optimizaciones de rendimiento
    - Validación de parámetros
    """
    try:
        if config.model_id not in models_db["models"]:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Validar parámetros
        if config.temperature is not None and (config.temperature < 0 or config.temperature > 2):
            raise HTTPException(status_code=400, detail="Temperature must be between 0 and 2")
        
        if config.top_p is not None and (config.top_p < 0 or config.top_p > 1):
            raise HTTPException(status_code=400, detail="Top-p must be between 0 and 1")
        
        if config.batch_size is not None and config.batch_size < 1:
            raise HTTPException(status_code=400, detail="Batch size must be at least 1")
        
        # Guardar configuración
        models_db["configs"][config.model_id] = config.dict()
        
        # Si el modelo está cargado, aplicar configuración
        config_applied = False
        if config.model_id in models_db["loaded_models"]:
            loaded_info = models_db["loaded_models"][config.model_id]
            loaded_info["config"] = config.dict()
            loaded_info["config_updated_at"] = datetime.now().isoformat()
            config_applied = True
        
        # Crear resumen de cambios
        changes_summary = []
        config_dict = config.dict(exclude_unset=True)
        
        for key, value in config_dict.items():
            if key != "model_id" and value is not None:
                changes_summary.append(f"{key}: {value}")
        
        return ModelResponse(
            message="Model configuration updated successfully",
            data={
                "model_id": config.model_id,
                "config": config,
                "applied_immediately": config_applied,
                "changes_summary": changes_summary,
                "updated_at": datetime.now()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error configuring model: {str(e)}")

# Endpoints adicionales útiles

@router.get("/operations/{operation_id}", response_model=ModelResponse)
async def get_operation_status(operation_id: str):
    """Obtener estado de una operación de modelo"""
    try:
        if operation_id not in models_db["operations"]:
            raise HTTPException(status_code=404, detail="Operation not found")
        
        operation = ModelOperation(**models_db["operations"][operation_id])
        
        return ModelResponse(
            message="Operation status retrieved successfully",
            data=operation
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving operation status: {str(e)}")

@router.get("/metrics/{model_id}", response_model=ModelResponse)
async def get_model_metrics(model_id: str):
    """Obtener métricas detalladas de un modelo"""
    try:
        if model_id not in models_db["models"]:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Generar métricas simuladas si no existen
        if model_id not in models_db["metrics"]:
            models_db["metrics"][model_id] = ModelMetrics(
                model_id=model_id,
                total_requests=random.randint(100, 10000),
                successful_requests=random.randint(90, 9900),
                failed_requests=random.randint(0, 100),
                avg_response_time=random.uniform(0.5, 3.0),
                min_response_time=random.uniform(0.1, 0.5),
                max_response_time=random.uniform(3.0, 10.0),
                tokens_processed=random.randint(100000, 1000000),
                memory_peak=random.randint(1000, 8000),
                uptime="2d 14h 32m",
                last_24h_requests=random.randint(50, 500)
            ).dict()
        
        metrics = ModelMetrics(**models_db["metrics"][model_id])
        
        return ModelResponse(
            message="Model metrics retrieved successfully",
            data=metrics
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving model metrics: {str(e)}")

@router.get("/compatibility/{model_id}", response_model=ModelResponse)
async def check_model_compatibility(model_id: str):
    """Verificar compatibilidad del modelo con el sistema"""
    try:
        if model_id not in models_db["models"]:
            raise HTTPException(status_code=404, detail="Model not found")
        
        model_info = ModelInfo(**models_db["models"][model_id])
        
        # Simular verificación de compatibilidad
        compatibility = ModelCompatibility(
            model_id=model_id,
            compatible=True,
            requirements={
                "python_version": ">=3.8",
                "memory_gb": model_info.memory_required / 1024,
                "gpu_memory_gb": 4 if model_info.type == ModelType.LLM else 2,
                "disk_space_gb": model_info.file_size / (1024**3)
            },
            missing_dependencies=[],
            warnings=[],
            recommendations=[]
        )
        
        # Agregar advertencias basadas en el modelo
        if model_info.memory_required > 8192:
            compatibility.warnings.append("High memory requirements detected")
            compatibility.recommendations.append("Consider using a smaller model variant")
        
        if model_info.type == ModelType.LLM and model_info.parameters > 7000000000:
            compatibility.warnings.append("Large language model may require GPU acceleration")
            compatibility.recommendations.append("Ensure GPU with sufficient VRAM is available")
        
        return ModelResponse(
            message="Model compatibility check completed",
            data=compatibility
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking model compatibility: {str(e)}")

import type {
  AIModel,
  GPUMetrics,
  SystemMetrics,
  ModelActivity,
  ModelOperation,
  ModelConfig,
  ModelVersion,
  ModelVersionComparison,
  ModelBenchmark,
  ModelUpdate,
} from "../types/ai-models"

// URL base para las APIs
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

// Función para manejar errores de fetch
const handleFetchError = (error: any) => {
  console.error("Error en la petición API:", error)
  throw new Error("Error al conectar con el servidor: " + error.message)
}

// Obtener lista de modelos disponibles
export const getAvailableModels = async (): Promise<AIModel[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/models/list`)
    if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`)
    return await response.json()
  } catch (error) {
    handleFetchError(error)
    // Datos mock en caso de error
    return getMockModels()
  }
}

// Obtener estado actual de los modelos
export const getModelStatus = async (): Promise<AIModel[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/models/status`)
    if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`)
    return await response.json()
  } catch (error) {
    handleFetchError(error)
    // Datos mock en caso de error
    return getMockModels()
  }
}

// Cargar un modelo
export const loadModel = async (modelId: string, config?: ModelConfig): Promise<ModelOperation> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/models/load`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_id: modelId, config }),
    })
    if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`)
    return await response.json()
  } catch (error) {
    handleFetchError(error)
    // Operación mock en caso de error
    return getMockOperation(modelId, "load")
  }
}

// Descargar un modelo
export const unloadModel = async (modelId: string): Promise<ModelOperation> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/models/unload`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_id: modelId }),
    })
    if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`)
    return await response.json()
  } catch (error) {
    handleFetchError(error)
    // Operación mock en caso de error
    return getMockOperation(modelId, "unload")
  }
}

// Obtener métricas de GPU
export const getGPUMetrics = async (): Promise<GPUMetrics> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/monitoring/metrics`)
    if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`)
    const data = await response.json()
    return data.gpu_metrics
  } catch (error) {
    handleFetchError(error)
    // Datos mock en caso de error
    return getMockGPUMetrics()
  }
}

// Obtener métricas del sistema
export const getSystemMetrics = async (): Promise<SystemMetrics> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/system/system/metrics`)
    if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`)
    const data = await response.json()
    return data.system_metrics
  } catch (error) {
    handleFetchError(error)
    // Datos mock en caso de error
    return getMockSystemMetrics()
  }
}

// Actualizar configuración de un modelo
export const updateModelConfig = async (modelId: string, config: ModelConfig): Promise<AIModel> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/models/config`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_id: modelId, config }),
    })
    if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`)
    return await response.json()
  } catch (error) {
    handleFetchError(error)
    // Datos mock en caso de error
    return getMockModels().find((m) => m.id === modelId) as AIModel
  }
}

// Obtener actividad reciente de modelos
export const getModelActivity = async (): Promise<ModelActivity[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/models/activity`)
    if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`)
    return await response.json()
  } catch (error) {
    handleFetchError(error)
    // Datos mock en caso de error
    return getMockModelActivity()
  }
}

// Obtener estado de una operación
export const getOperationStatus = async (operationId: string): Promise<ModelOperation> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/models/operations/${operationId}`)
    if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`)
    return await response.json()
  } catch (error) {
    handleFetchError(error)
    // Datos mock en caso de error
    return {
      operation_id: operationId,
      model_id: "qwen-7b-chat",
      operation_type: "load",
      status: "completed",
      progress_percentage: 100,
      message: "Operación completada con éxito",
      started_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
    }
  }
}

// Ejecutar test en un modelo
export const testModel = async (modelId: string, input: string, config?: Partial<ModelConfig>): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/models/test`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_id: modelId, input, config }),
    })
    if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`)
    return await response.json()
  } catch (error) {
    handleFetchError(error)
    // Datos mock en caso de error
    return {
      output:
        "Quantum computing is like having a super-powered computer that can explore multiple solutions simultaneously. Instead of processing bits as just 0s or 1s like regular computers, quantum computers use quantum bits or 'qubits' that can exist in multiple states at once. This allows them to solve certain complex problems much faster than traditional computers. Think of it like being able to check all paths through a maze at the same time, rather than trying one path at a time.",
      metrics: {
        tokens: 245,
        speed: 106,
        gpu_usage_increase: 12,
        latency_seconds: 2.3,
        technical_accuracy: 98,
      },
    }
  }
}

// Obtener versiones de un modelo
export const getModelVersions = async (modelId: string): Promise<ModelVersion[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/models/versions/${modelId}`)
    if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`)
    return await response.json()
  } catch (error) {
    handleFetchError(error)
    // Datos mock en caso de error
    return getMockModelVersions(modelId)
  }
}

// Comparar versiones de un modelo
export const compareModelVersions = async (
  modelId: string,
  version1: string,
  version2: string,
): Promise<ModelVersionComparison> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/models/compare`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_id: modelId, version1, version2 }),
    })
    if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`)
    return await response.json()
  } catch (error) {
    handleFetchError(error)
    // Datos mock en caso de error
    return getMockVersionComparison()
  }
}

// Obtener benchmarks de un modelo
export const getModelBenchmarks = async (modelId: string): Promise<ModelBenchmark[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/models/benchmarks/${modelId}`)
    if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`)
    return await response.json()
  } catch (error) {
    handleFetchError(error)
    // Datos mock en caso de error
    return getMockBenchmarks()
  }
}

// Obtener actualizaciones disponibles
export const getAvailableUpdates = async (): Promise<ModelUpdate[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/models/updates`)
    if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`)
    return await response.json()
  } catch (error) {
    handleFetchError(error)
    // Datos mock en caso de error
    return getMockUpdates()
  }
}

// Funciones para generar datos mock

function getMockModels(): AIModel[] {
  return [
    {
      id: "qwen-7b-chat",
      name: "Qwen-7B-Chat",
      type: "LLM",
      version: "v1.8.3",
      status: "loaded",
      size_gb: 4.2,
      gpu_memory_mb: 2800,
      system_memory_mb: 1200,
      usage_percentage: 67,
      requests_count: 1247,
      uptime_hours: 2,
      performance_score: 94.2,
      description: "Modelo principal de chat para interacciones con Vicky AI",
      location: "/models/qwen/7b-chat",
      configuration: {
        temperature: 0.7,
        max_tokens: 2048,
        top_p: 0.9,
        top_k: 50,
        repetition_penalty: 1.1,
        batch_size: 8,
        cache_size_mb: 512,
        optimizations: {
          kv_cache: true,
          mixed_precision: true,
          quantization: false,
          dynamic_batching: true,
          tensor_parallelism: true,
        },
      },
    },
    {
      id: "whisper-medium",
      name: "Whisper-Medium",
      type: "STT",
      version: "v2.1.0",
      status: "loaded",
      size_gb: 1.4,
      gpu_memory_mb: 1400,
      system_memory_mb: 600,
      usage_percentage: 23,
      requests_count: 456,
      uptime_hours: 2,
      performance_score: 96.0,
      description: "Procesamiento de voz a texto para entradas de audio",
      location: "/models/whisper/medium-en",
      configuration: {
        batch_size: 4,
        cache_size_mb: 256,
        optimizations: {
          kv_cache: false,
          mixed_precision: true,
          quantization: false,
          dynamic_batching: true,
        },
      },
    },
    {
      id: "xtts-v2",
      name: "XTTS-v2",
      type: "TTS",
      version: "v2.0.1",
      status: "loaded",
      size_gb: 1.8,
      gpu_memory_mb: 1800,
      system_memory_mb: 800,
      usage_percentage: 34,
      requests_count: 234,
      uptime_hours: 2,
      performance_score: 92.0,
      description: "Síntesis de texto a voz con clonación de voces",
      location: "/models/xtts/v2",
      configuration: {
        batch_size: 2,
        cache_size_mb: 128,
        optimizations: {
          kv_cache: false,
          mixed_precision: true,
          quantization: false,
          dynamic_batching: false,
        },
      },
    },
    {
      id: "nllb-200",
      name: "NLLB-200",
      type: "TRANSLATION",
      version: "v1.3.1",
      status: "loaded",
      size_gb: 0.8,
      gpu_memory_mb: 800,
      system_memory_mb: 400,
      usage_percentage: 12,
      requests_count: 2145,
      uptime_hours: 2,
      performance_score: 98.0,
      description: "Modelo de traducción multilingüe",
      location: "/models/nllb/200-distilled-600M",
      configuration: {
        batch_size: 16,
        cache_size_mb: 64,
        optimizations: {
          kv_cache: true,
          mixed_precision: true,
          quantization: false,
          dynamic_batching: true,
        },
      },
    },
    {
      id: "qwen-14b-chat",
      name: "Qwen-14B-Chat",
      type: "LLM",
      version: "v1.5.1",
      status: "unloaded",
      size_gb: 7.2,
      gpu_memory_mb: 0,
      system_memory_mb: 0,
      usage_percentage: 0,
      requests_count: 0,
      uptime_hours: 0,
      performance_score: 96.5,
      description: "Modelo de chat más grande y potente",
      location: "/models/qwen/14b-chat",
      configuration: {
        temperature: 0.7,
        max_tokens: 4096,
        top_p: 0.9,
        top_k: 50,
        repetition_penalty: 1.1,
        batch_size: 4,
        cache_size_mb: 1024,
        optimizations: {
          kv_cache: true,
          mixed_precision: true,
          quantization: false,
          dynamic_batching: true,
          tensor_parallelism: true,
        },
      },
    },
    {
      id: "whisper-large",
      name: "Whisper-Large",
      type: "STT",
      version: "v2.0.0",
      status: "unloaded",
      size_gb: 3.1,
      gpu_memory_mb: 0,
      system_memory_mb: 0,
      usage_percentage: 0,
      requests_count: 0,
      uptime_hours: 0,
      performance_score: 98.2,
      description: "Modelo STT de alta precisión",
      location: "/models/whisper/large",
      configuration: {
        batch_size: 2,
        cache_size_mb: 512,
        optimizations: {
          kv_cache: false,
          mixed_precision: true,
          quantization: false,
          dynamic_batching: true,
        },
      },
    },
  ]
}

function getMockGPUMetrics(): GPUMetrics {
  return {
    utilization_percentage: 89,
    memory_used_gb: 6.8,
    memory_total_gb: 8.0,
    temperature_celsius: 78,
    power_watts: 245,
    model_allocations: {
      "qwen-7b-chat": 2.8,
      "whisper-medium": 1.4,
      "xtts-v2": 1.8,
      "nllb-200": 0.8,
    },
  }
}

function getMockSystemMetrics(): SystemMetrics {
  return {
    cpu_usage_percentage: 45,
    memory_used_gb: 12.3,
    memory_total_gb: 32.0,
    model_buffers_gb: 4.2,
    cache_gb: 2.0,
    system_gb: 6.1,
    available_gb: 19.7,
  }
}

function getMockModelActivity(): ModelActivity[] {
  return [
    {
      timestamp: new Date(Date.now() - 60000).toISOString(),
      model_id: "qwen-7b-chat",
      action: "processing",
      details: 'Chat: "Explain quantum physics"',
    },
    {
      timestamp: new Date(Date.now() - 120000).toISOString(),
      model_id: "nllb-200",
      action: "translation",
      details: 'ES→EN "Hola mundo"',
    },
    {
      timestamp: new Date(Date.now() - 180000).toISOString(),
      model_id: "whisper-medium",
      action: "processing",
      details: "STT: 3.2s audio file",
    },
    {
      timestamp: new Date(Date.now() - 240000).toISOString(),
      model_id: "xtts-v2",
      action: "synthesis",
      details: 'TTS: "Hello, how are you today?"',
    },
    {
      timestamp: new Date(Date.now() - 300000).toISOString(),
      model_id: "qwen-7b-chat",
      action: "generation",
      details: "Code generation request completed",
    },
  ]
}

function getMockOperation(modelId: string, type: "load" | "unload"): ModelOperation {
  const now = new Date()
  return {
    operation_id: `op_${Math.random().toString(36).substring(2, 10)}`,
    model_id: modelId,
    operation_type: type,
    status: "in_progress",
    progress_percentage: 45,
    eta_seconds: 45,
    message: type === "load" ? `Cargando ${modelId}...` : `Descargando ${modelId}...`,
    started_at: now.toISOString(),
  }
}

function getMockModelVersions(modelId: string): ModelVersion[] {
  return [
    {
      version: "v1.8.3",
      date: "2025-01-30",
      size_gb: 4.2,
      status: "active",
      performance_score: 94.2,
    },
    {
      version: "v1.8.2",
      date: "2025-01-15",
      size_gb: 4.1,
      status: "backup",
      performance_score: 93.8,
    },
    {
      version: "v1.8.1",
      date: "2025-01-01",
      size_gb: 4.0,
      status: "backup",
      performance_score: 92.1,
    },
    {
      version: "v1.7.9",
      date: "2024-12-15",
      size_gb: 3.9,
      status: "old",
      performance_score: 90.5,
    },
  ]
}

function getMockVersionComparison(): ModelVersionComparison {
  return {
    metrics: [
      {
        name: "Calidad de Respuesta",
        current_value: "94.2%",
        previous_value: "93.8%",
        change: "+0.4%",
        impact: "better",
      },
      {
        name: "Velocidad (tokens/s)",
        current_value: 245,
        previous_value: 238,
        change: "+7 t/s",
        impact: "better",
      },
      {
        name: "Uso de Memoria",
        current_value: "2.8GB",
        previous_value: "2.9GB",
        change: "-0.1GB",
        impact: "better",
      },
      {
        name: "Puntuación de Precisión",
        current_value: "96.1%",
        previous_value: "95.8%",
        change: "+0.3%",
        impact: "better",
      },
      {
        name: "Latencia de Inferencia",
        current_value: "45ms",
        previous_value: "52ms",
        change: "-7ms",
        impact: "better",
      },
    ],
    recommendation: "✅ v1.8.3 muestra mejoras en todas las métricas",
  }
}

function getMockBenchmarks(): ModelBenchmark[] {
  return [
    {
      test_name: "Calidad de Chat",
      status: "pass",
      score: 94,
      time_seconds: 45,
      last_run: new Date(Date.now() - 7200000).toISOString(),
    },
    {
      test_name: "Precisión STT",
      status: "pass",
      score: 96,
      time_seconds: 135,
      last_run: new Date(Date.now() - 86400000).toISOString(),
    },
    {
      test_name: "Calidad TTS",
      status: "pass",
      score: 92,
      time_seconds: 90,
      last_run: new Date(Date.now() - 86400000).toISOString(),
    },
    {
      test_name: "Traducción",
      status: "pass",
      score: 98,
      time_seconds: 30,
      last_run: new Date(Date.now() - 21600000).toISOString(),
    },
    {
      test_name: "Rendimiento",
      status: "pass",
      score: 89,
      time_seconds: 60,
      last_run: new Date(Date.now() - 3600000).toISOString(),
    },
  ]
}

function getMockUpdates(): ModelUpdate[] {
  return [
    {
      model_id: "qwen-7b-chat",
      current_version: "v1.8.2",
      latest_version: "v1.8.3",
      size_mb: 50,
      changes: "Corrección de errores, mejoras de rendimiento",
      is_latest: false,
    },
    {
      model_id: "whisper-medium",
      current_version: "v2.1.0",
      latest_version: "v2.1.0",
      size_mb: 0,
      changes: "",
      is_latest: true,
    },
    {
      model_id: "xtts-v2",
      current_version: "v2.0.1",
      latest_version: "v2.0.2",
      size_mb: 120,
      changes: "Nuevos modelos de voz, mejoras de calidad",
      is_latest: false,
    },
    {
      model_id: "nllb-200",
      current_version: "v1.3.1",
      latest_version: "v1.3.1",
      size_mb: 0,
      changes: "",
      is_latest: true,
    },
  ]
}

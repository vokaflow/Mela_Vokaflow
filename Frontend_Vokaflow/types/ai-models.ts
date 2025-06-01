export type ModelType = "LLM" | "STT" | "TTS" | "TRANSLATION"
export type ModelStatus = "loaded" | "unloaded" | "loading" | "error"

export interface ModelConfig {
  temperature?: number
  max_tokens?: number
  top_p?: number
  top_k?: number
  repetition_penalty?: number
  batch_size?: number
  cache_size_mb?: number
  optimizations: {
    kv_cache: boolean
    mixed_precision: boolean
    quantization: boolean
    dynamic_batching: boolean
    tensor_parallelism?: boolean
  }
}

export interface AIModel {
  id: string
  name: string
  type: ModelType
  version: string
  status: ModelStatus
  size_gb: number
  gpu_memory_mb: number
  system_memory_mb: number
  usage_percentage: number
  requests_count: number
  uptime_hours: number
  performance_score: number
  description: string
  location?: string
  configuration: ModelConfig
}

export interface GPUMetrics {
  utilization_percentage: number
  memory_used_gb: number
  memory_total_gb: number
  temperature_celsius: number
  power_watts: number
  model_allocations: Record<string, number>
}

export interface SystemMetrics {
  cpu_usage_percentage: number
  memory_used_gb: number
  memory_total_gb: number
  model_buffers_gb: number
  cache_gb: number
  system_gb: number
  available_gb: number
}

export interface ModelActivity {
  timestamp: string
  model_id: string
  action: string
  details: string
}

export interface ModelOperation {
  operation_id: string
  model_id: string
  operation_type: "load" | "unload" | "update" | "restart"
  status: "pending" | "in_progress" | "completed" | "failed"
  progress_percentage: number
  eta_seconds?: number
  message?: string
  started_at: string
  completed_at?: string
}

export interface ModelVersion {
  version: string
  date: string
  size_gb: number
  status: "active" | "backup" | "old"
  performance_score: number
}

export interface ModelVersionComparison {
  metrics: {
    name: string
    current_value: string | number
    previous_value: string | number
    change: string
    impact: "better" | "worse" | "neutral"
  }[]
  recommendation: string
}

export interface ModelBenchmark {
  test_name: string
  status: "pass" | "fail" | "pending"
  score: number
  time_seconds: number
  last_run: string
}

export interface ModelUpdate {
  model_id: string
  current_version: string
  latest_version: string
  size_mb: number
  changes: string
  is_latest: boolean
}

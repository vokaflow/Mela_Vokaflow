# 📚 API Reference - VokaFlow

Documentación completa de la API de VokaFlow para desarrollo e integración.

## 🌐 Base URL

```
Production: https://api.vokaflow.com
Staging: https://staging-api.vokaflow.com  
Development: http://localhost:8000
```

## 🔐 Autenticación

VokaFlow utiliza API Keys y JWT tokens para autenticación:

```http
Authorization: Bearer <jwt_token>
# o
X-API-Key: <api_key>
```

## 📋 Endpoints Principales

### Health & Status

#### GET /api/health/
Endpoint de health check del sistema.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-05-31T00:52:46.682244",
  "uptime": 1748652554.6991608,
  "version": "2.0.0",
  "environment": "production"
}
```

**Status Codes:**
- `200`: Sistema saludable
- `503`: Sistema degradado o no disponible

---

### High Scale Tasks

#### POST /api/high-scale-tasks/submit
Enviar una tarea individual al sistema de alta escala.

**Request Body:**
```json
{
  "name": "task_name",
  "function_name": "vicky_inference",
  "args": ["argument1", "argument2"],
  "kwargs": {"param1": "value1"},
  "priority": "CRITICAL",
  "worker_type": "GENERAL_PURPOSE",
  "category": "vicky",
  "timeout": 300,
  "retry_count": 3,
  "metadata": {"user_id": "12345"}
}
```

**Parameters:**
- `name` (string): Nombre identificador de la tarea
- `function_name` (string): Nombre de la función a ejecutar
- `args` (array): Argumentos posicionales
- `kwargs` (object, optional): Argumentos con nombre
- `priority` (enum): Prioridad de la tarea (EMERGENCY, CRITICAL, HIGH, NORMAL, LOW, BATCH, BACKGROUND, MAINTENANCE)
- `worker_type` (enum): Tipo de worker (CPU_INTENSIVE, IO_INTENSIVE, MEMORY_INTENSIVE, NETWORK_INTENSIVE, GENERAL_PURPOSE)
- `category` (string): Categoría para rate limiting
- `timeout` (integer, optional): Timeout en segundos (default: 300)
- `retry_count` (integer, optional): Número de reintentos (default: 3)
- `metadata` (object, optional): Metadatos adicionales

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "task_name",
  "status": "queued",
  "priority": "CRITICAL",
  "partition": 5,
  "redis_node": "node_2",
  "estimated_completion": "2025-05-31T01:00:00.000Z",
  "queue_position": 3,
  "created_at": "2025-05-31T00:52:46.682244"
}
```

**Status Codes:**
- `200`: Tarea enviada exitosamente
- `400`: Error de validación en los datos de entrada
- `429`: Rate limit excedido
- `500`: Error interno del sistema

---

#### POST /api/high-scale-tasks/batch
Enviar múltiples tareas en un lote.

**Request Body:**
```json
{
  "tasks": [
    {
      "name": "vicky_task_1",
      "function_name": "vicky_inference",
      "args": ["Tarea 1", "qwen_7b"],
      "priority": "HIGH",
      "worker_type": "GENERAL_PURPOSE",
      "category": "vicky"
    },
    {
      "name": "audio_task_1",
      "function_name": "audio_analysis", 
      "args": ["/path/audio.wav", ["transcription"]],
      "priority": "NORMAL",
      "worker_type": "IO_INTENSIVE",
      "category": "audio"
    }
  ],
  "batch_priority": "HIGH",
  "execution_mode": "parallel",
  "batch_timeout": 900,
  "max_failures": 5
}
```

**Parameters:**
- `tasks` (array): Array de objetos de tarea
- `batch_priority` (enum): Prioridad del lote completo
- `execution_mode` (enum): Modo de ejecución (parallel, sequential, adaptive)
- `batch_timeout` (integer, optional): Timeout para todo el lote en segundos
- `max_failures` (integer, optional): Máximo número de fallos permitidos

**Response:**
```json
{
  "batch_id": "batch_550e8400-e29b-41d4-a716-446655440000",
  "total_submitted": 2,
  "total_errors": 0,
  "successful_tasks": [
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "vicky_task_1",
      "partition": 3,
      "redis_node": "node_1"
    },
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440002", 
      "name": "audio_task_1",
      "partition": 7,
      "redis_node": "node_2"
    }
  ],
  "errors": [],
  "execution_mode": "parallel",
  "estimated_completion": "2025-05-31T01:05:00.000Z"
}
```

---

#### GET /api/high-scale-tasks/status/{task_id}
Consultar el estado de una tarea específica.

**Parameters:**
- `task_id` (string): ID de la tarea

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "task_name",
  "status": "completed",
  "priority": "CRITICAL",
  "worker_type": "GENERAL_PURPOSE",
  "category": "vicky",
  "partition": 5,
  "redis_node": "node_2",
  "created_at": "2025-05-31T00:52:46.682244",
  "started_at": "2025-05-31T00:52:47.123456",
  "completed_at": "2025-05-31T00:52:49.987654",
  "execution_time": 2.864198,
  "result": {
    "output": "Task completed successfully",
    "data": {...}
  },
  "error": null,
  "retry_count": 0,
  "metadata": {"user_id": "12345"}
}
```

**Status Values:**
- `queued`: Tarea en cola
- `running`: Tarea en ejecución
- `completed`: Tarea completada exitosamente
- `failed`: Tarea falló
- `cancelled`: Tarea cancelada
- `timeout`: Tarea expiró por timeout

---

#### GET /api/high-scale-tasks/metrics
Obtener métricas del sistema en tiempo real.

**Response:**
```json
{
  "throughput_per_second": 1250.5,
  "total_pending_tasks": 42,
  "active_workers": 128,
  "redis_nodes": 6,
  "partitions": 16,
  "system_resources": {
    "cpu_percent": 45.2,
    "memory_percent": 67.8,
    "disk_usage": 43.4,
    "network_io": {
      "bytes_sent": 1048576000,
      "bytes_recv": 2097152000
    }
  },
  "worker_pools": {
    "CPU_INTENSIVE": {
      "active_workers": 32,
      "max_workers": 64,
      "queue_size": 15,
      "avg_execution_time": 5.2
    },
    "IO_INTENSIVE": {
      "active_workers": 48,
      "max_workers": 128,
      "queue_size": 8,
      "avg_execution_time": 2.1
    },
    "MEMORY_INTENSIVE": {
      "active_workers": 12,
      "max_workers": 32,
      "queue_size": 3,
      "avg_execution_time": 8.7
    },
    "NETWORK_INTENSIVE": {
      "active_workers": 24,
      "max_workers": 256,
      "queue_size": 12,
      "avg_execution_time": 1.5
    },
    "GENERAL_PURPOSE": {
      "active_workers": 16,
      "max_workers": 64,
      "queue_size": 4,
      "avg_execution_time": 3.8
    }
  },
  "rate_limits": {
    "vicky": {
      "limit_per_second": 50000,
      "current_usage": 12500,
      "reset_time": "2025-05-31T01:00:00.000Z"
    },
    "audio": {
      "limit_per_second": 25000,
      "current_usage": 8200,
      "reset_time": "2025-05-31T01:00:00.000Z"
    }
  },
  "redis_cluster": {
    "node_0": {"status": "healthy", "memory_usage": "45%"},
    "node_1": {"status": "healthy", "memory_usage": "52%"},
    "node_2": {"status": "healthy", "memory_usage": "38%"}
  },
  "timestamp": 1748652566.2509217
}
```

---

#### GET /api/high-scale-tasks/functions
Listar todas las funciones disponibles.

**Response:**
```json
{
  "functions": {
    "vicky": [
      {
        "name": "vicky_inference",
        "description": "Procesamiento de inferencia con Vicky AI",
        "parameters": ["text", "model"],
        "category": "vicky",
        "estimated_duration": "2-5 seconds",
        "worker_type": "GENERAL_PURPOSE"
      },
      {
        "name": "vicky_training",
        "description": "Entrenamiento de modelos Vicky",
        "parameters": ["dataset", "config"],
        "category": "vicky", 
        "estimated_duration": "5-30 minutes",
        "worker_type": "CPU_INTENSIVE"
      }
    ],
    "audio": [
      {
        "name": "audio_analysis",
        "description": "Análisis completo de archivos de audio",
        "parameters": ["file_path", "analysis_types"],
        "category": "audio",
        "estimated_duration": "10-60 seconds",
        "worker_type": "IO_INTENSIVE"
      },
      {
        "name": "audio_transcription",
        "description": "Transcripción de audio a texto",
        "parameters": ["file_path", "language"],
        "category": "audio",
        "estimated_duration": "5-30 seconds", 
        "worker_type": "IO_INTENSIVE"
      }
    ],
    "database": [
      {
        "name": "bulk_insert",
        "description": "Inserción masiva de datos",
        "parameters": ["table", "data", "batch_size"],
        "category": "database",
        "estimated_duration": "1-10 seconds",
        "worker_type": "IO_INTENSIVE"
      },
      {
        "name": "complex_query",
        "description": "Consultas complejas con agregaciones",
        "parameters": ["query", "parameters"],
        "category": "database", 
        "estimated_duration": "2-15 seconds",
        "worker_type": "CPU_INTENSIVE"
      }
    ]
  },
  "total_functions": 25,
  "categories": ["vicky", "audio", "database", "notifications", "files", "analytics", "ml", "system", "realtime"]
}
```

---

#### GET /api/high-scale-tasks/priorities
Obtener configuración de prioridades del sistema.

**Response:**
```json
{
  "priorities": {
    "EMERGENCY": {
      "level": 0,
      "sla_seconds": 0.1,
      "description": "Emergencias críticas del sistema",
      "examples": ["system_failure", "security_breach"]
    },
    "CRITICAL": {
      "level": 1,
      "sla_seconds": 0.5,
      "description": "Tareas críticas de alta prioridad",
      "examples": ["user_facing_errors", "payment_processing"]
    },
    "HIGH": {
      "level": 2,
      "sla_seconds": 2.0,
      "description": "Tareas importantes con alta prioridad",
      "examples": ["real_time_analytics", "api_responses"]
    },
    "NORMAL": {
      "level": 3,
      "sla_seconds": 10.0,
      "description": "Tareas regulares del sistema",
      "examples": ["data_processing", "report_generation"]
    },
    "LOW": {
      "level": 4,
      "sla_seconds": 30.0,
      "description": "Tareas de baja prioridad",
      "examples": ["cleanup_tasks", "optimization"]
    },
    "BATCH": {
      "level": 5,
      "sla_seconds": 300.0,
      "description": "Procesamiento en lotes",
      "examples": ["bulk_operations", "data_migration"]
    },
    "BACKGROUND": {
      "level": 6,
      "sla_seconds": 1800.0,
      "description": "Tareas de fondo",
      "examples": ["backups", "maintenance"]
    },
    "MAINTENANCE": {
      "level": 7,
      "sla_seconds": 7200.0,
      "description": "Tareas de mantenimiento",
      "examples": ["log_rotation", "cache_cleanup"]
    }
  },
  "default_priority": "NORMAL",
  "auto_scaling_thresholds": {
    "scale_up_queue_size": 100,
    "scale_down_queue_size": 10
  }
}
```

---

#### DELETE /api/high-scale-tasks/cancel/{task_id}
Cancelar una tarea en cola o en ejecución.

**Parameters:**
- `task_id` (string): ID de la tarea a cancelar

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "cancelled",
  "cancelled_at": "2025-05-31T00:55:30.123456",
  "message": "Task cancelled successfully"
}
```

**Status Codes:**
- `200`: Tarea cancelada exitosamente
- `404`: Tarea no encontrada
- `409`: Tarea ya completada/no cancelable

---

### Vicky AI

#### POST /api/vicky/inference
Endpoint directo para inferencia con Vicky AI.

**Request Body:**
```json
{
  "text": "Explica el concepto de machine learning",
  "model": "qwen_7b",
  "personality": "conversational",
  "context": {
    "user_id": "user123",
    "session_id": "session456"
  },
  "parameters": {
    "max_tokens": 1000,
    "temperature": 0.7,
    "top_p": 0.9
  }
}
```

**Response:**
```json
{
  "response": "Machine learning es una rama de la inteligencia artificial...",
  "model_used": "qwen_7b",
  "personality": "conversational",
  "tokens_used": 156,
  "execution_time": 2.34,
  "confidence": 0.92,
  "metadata": {
    "model_version": "2.1.0",
    "processing_node": "node_1"
  }
}
```

---

#### POST /api/vicky/chat
Endpoint para conversaciones multi-turn con Vicky.

**Request Body:**
```json
{
  "messages": [
    {"role": "user", "content": "Hola, ¿cómo estás?"},
    {"role": "assistant", "content": "¡Hola! Estoy muy bien, gracias por preguntar. ¿En qué puedo ayudarte hoy?"},
    {"role": "user", "content": "Necesito ayuda con Python"}
  ],
  "model": "qwen_7b",
  "personality": "technical_assistant",
  "session_id": "chat_session_789"
}
```

**Response:**
```json
{
  "message": {
    "role": "assistant",
    "content": "¡Perfecto! Estaré encantado de ayudarte con Python. ¿Qué tema específico te interesa o qué problema estás tratando de resolver?"
  },
  "session_id": "chat_session_789",
  "model_used": "qwen_7b",
  "personality": "technical_assistant",
  "tokens_used": 187,
  "execution_time": 1.87
}
```

---

### Rate Limits

Cada categoría tiene límites específicos:

| Categoría     | Límite por segundo | Burst | Ventana |
|---------------|-------------------|--------|---------|
| vicky         | 50,000            | 100,000| 1 min   |
| audio         | 25,000            | 50,000 | 1 min   |
| database      | 100,000           | 200,000| 1 min   |
| notifications | 1,000,000         | 2,000,000| 1 min |
| files         | 10,000            | 20,000 | 1 min   |
| analytics     | 50,000            | 100,000| 1 min   |
| ml            | 5,000             | 10,000 | 1 min   |
| system        | 1,000             | 2,000  | 1 min   |
| realtime      | 100,000           | 200,000| 1 min   |

## 🚨 Error Codes

### 4xx Client Errors

#### 400 Bad Request
```json
{
  "error": "validation_error",
  "message": "Invalid request parameters",
  "details": {
    "field": "priority",
    "error": "Invalid priority level. Must be one of: EMERGENCY, CRITICAL, HIGH, NORMAL, LOW, BATCH, BACKGROUND, MAINTENANCE"
  },
  "timestamp": "2025-05-31T00:52:46.682244"
}
```

#### 401 Unauthorized
```json
{
  "error": "unauthorized",
  "message": "Invalid or missing authentication token",
  "timestamp": "2025-05-31T00:52:46.682244"
}
```

#### 429 Too Many Requests
```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded for category 'vicky'",
  "details": {
    "limit": 50000,
    "current": 50001,
    "reset_time": "2025-05-31T01:00:00.000Z",
    "retry_after": 45
  },
  "timestamp": "2025-05-31T00:52:46.682244"
}
```

### 5xx Server Errors

#### 500 Internal Server Error
```json
{
  "error": "internal_server_error",
  "message": "An unexpected error occurred",
  "error_id": "error_550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-05-31T00:52:46.682244"
}
```

#### 503 Service Unavailable
```json
{
  "error": "service_unavailable",
  "message": "Redis cluster is temporarily unavailable",
  "details": {
    "component": "redis_cluster",
    "status": "degraded",
    "estimated_recovery": "2025-05-31T01:00:00.000Z"
  },
  "timestamp": "2025-05-31T00:52:46.682244"
}
```

## 📖 SDK Examples

### Python SDK

```python
import asyncio
from vokaflow_sdk import VokaFlowClient

# Inicializar cliente
client = VokaFlowClient(
    base_url="https://api.vokaflow.com",
    api_key="your_api_key_here"
)

async def example_usage():
    # Enviar tarea individual
    task = await client.submit_task(
        name="example_task",
        function_name="vicky_inference",
        args=["Procesar este texto", "qwen_7b"],
        priority="HIGH",
        category="vicky"
    )
    print(f"Task ID: {task.task_id}")
    
    # Enviar batch de tareas
    batch = await client.submit_batch([
        {
            "name": "task_1",
            "function_name": "audio_analysis",
            "args": ["/path/audio1.wav", ["transcription"]],
            "priority": "NORMAL",
            "category": "audio"
        },
        {
            "name": "task_2", 
            "function_name": "vicky_inference",
            "args": ["Texto a procesar", "qwen_7b"],
            "priority": "HIGH",
            "category": "vicky"
        }
    ])
    print(f"Batch submitted: {batch.total_submitted} tasks")
    
    # Consultar estado
    status = await client.get_task_status(task.task_id)
    print(f"Task status: {status.status}")
    
    # Obtener métricas
    metrics = await client.get_metrics()
    print(f"Throughput: {metrics.throughput_per_second} req/s")

# Ejecutar ejemplo
asyncio.run(example_usage())
```

### JavaScript SDK

```javascript
import { VokaFlowClient } from '@vokaflow/sdk';

// Inicializar cliente
const client = new VokaFlowClient({
    baseUrl: 'https://api.vokaflow.com',
    apiKey: 'your_api_key_here'
});

// Enviar tarea
const task = await client.submitTask({
    name: 'example_task',
    functionName: 'vicky_inference',
    args: ['Procesar este texto', 'qwen_7b'],
    priority: 'HIGH',
    category: 'vicky'
});

console.log(`Task ID: ${task.taskId}`);

// Consultar estado con polling
const status = await client.waitForCompletion(task.taskId, {
    timeout: 300000, // 5 minutos
    pollInterval: 1000 // 1 segundo
});

console.log(`Task completed: ${status.result}`);
```

### cURL Examples

```bash
# Health check
curl -X GET "https://api.vokaflow.com/api/health/"

# Enviar tarea
curl -X POST "https://api.vokaflow.com/api/high-scale-tasks/submit" \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "example_task",
    "function_name": "vicky_inference",
    "args": ["Texto a procesar", "qwen_7b"],
    "priority": "HIGH",
    "worker_type": "GENERAL_PURPOSE",
    "category": "vicky"
  }'

# Obtener métricas
curl -X GET "https://api.vokaflow.com/api/high-scale-tasks/metrics" \
  -H "Authorization: Bearer your_jwt_token"

# Consultar estado de tarea
curl -X GET "https://api.vokaflow.com/api/high-scale-tasks/status/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer your_jwt_token"
```

## 🔄 Webhooks

VokaFlow puede enviar webhooks para notificar cambios de estado:

### Configuración de Webhook

```bash
curl -X POST "https://api.vokaflow.com/api/webhooks/configure" \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/webhooks/vokaflow",
    "events": ["task.completed", "task.failed", "batch.completed"],
    "secret": "your_webhook_secret"
  }'
```

### Payload de Webhook

```json
{
  "event": "task.completed",
  "timestamp": "2025-05-31T00:52:46.682244",
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "example_task",
    "status": "completed",
    "result": {...},
    "execution_time": 2.34,
    "completed_at": "2025-05-31T00:52:49.012345"
  },
  "signature": "sha256=hash_of_payload_with_secret"
}
```

## 📊 Monitoring & Observability

### Métricas Personalizadas

```bash
# Métricas por categoría
curl "https://api.vokaflow.com/api/metrics/category/vicky" \
  -H "Authorization: Bearer your_jwt_token"

# Métricas de worker pools
curl "https://api.vokaflow.com/api/metrics/workers" \
  -H "Authorization: Bearer your_jwt_token"

# Métricas de Redis cluster
curl "https://api.vokaflow.com/api/metrics/redis" \
  -H "Authorization: Bearer your_jwt_token"
```

### Logs Estructurados

```bash
# Logs de una tarea específica
curl "https://api.vokaflow.com/api/logs/task/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer your_jwt_token"

# Logs del sistema por nivel
curl "https://api.vokaflow.com/api/logs?level=ERROR&limit=100" \
  -H "Authorization: Bearer your_jwt_token"
```

Esta documentación proporciona una referencia completa para integrar y utilizar la API de VokaFlow en cualquier aplicación o sistema. 
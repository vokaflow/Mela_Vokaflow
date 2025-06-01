import type {
  SystemConfig,
  Integration,
  ApiKey,
  Webhook,
  EnvironmentVariable,
  Automation,
  SystemMetrics,
} from "../types/settings"

class SettingsService {
  private baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

  // Configuración General
  async getSystemConfig(): Promise<SystemConfig[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/admin/config`)
      if (!response.ok) throw new Error("Failed to fetch config")
      return await response.json()
    } catch (error) {
      console.error("Error fetching system config:", error)
      return this.getMockSystemConfig()
    }
  }

  async updateSystemConfig(config: Partial<SystemConfig>): Promise<SystemConfig> {
    try {
      const response = await fetch(`${this.baseUrl}/api/admin/config`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      })
      if (!response.ok) throw new Error("Failed to update config")
      return await response.json()
    } catch (error) {
      console.error("Error updating system config:", error)
      throw error
    }
  }

  // Integraciones
  async getIntegrations(): Promise<Integration[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/admin/integrations`)
      if (!response.ok) throw new Error("Failed to fetch integrations")
      return await response.json()
    } catch (error) {
      console.error("Error fetching integrations:", error)
      return this.getMockIntegrations()
    }
  }

  async testIntegration(integrationId: string): Promise<{ success: boolean; latency?: number; error?: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/admin/integrations/test`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ integration_id: integrationId }),
      })
      if (!response.ok) throw new Error("Failed to test integration")
      return await response.json()
    } catch (error) {
      console.error("Error testing integration:", error)
      return { success: false, error: error.message }
    }
  }

  // API Keys
  async getApiKeys(): Promise<ApiKey[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/api-keys`)
      if (!response.ok) throw new Error("Failed to fetch API keys")
      return await response.json()
    } catch (error) {
      console.error("Error fetching API keys:", error)
      return this.getMockApiKeys()
    }
  }

  async createApiKey(keyData: Partial<ApiKey>): Promise<ApiKey> {
    try {
      const response = await fetch(`${this.baseUrl}/api/api-keys`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(keyData),
      })
      if (!response.ok) throw new Error("Failed to create API key")
      return await response.json()
    } catch (error) {
      console.error("Error creating API key:", error)
      throw error
    }
  }

  async deleteApiKey(keyId: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/api-keys/${keyId}`, {
        method: "DELETE",
      })
      if (!response.ok) throw new Error("Failed to delete API key")
    } catch (error) {
      console.error("Error deleting API key:", error)
      throw error
    }
  }

  // Webhooks
  async getWebhooks(): Promise<Webhook[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/webhooks`)
      if (!response.ok) throw new Error("Failed to fetch webhooks")
      return await response.json()
    } catch (error) {
      console.error("Error fetching webhooks:", error)
      return this.getMockWebhooks()
    }
  }

  async createWebhook(webhookData: Partial<Webhook>): Promise<Webhook> {
    try {
      const response = await fetch(`${this.baseUrl}/api/webhooks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(webhookData),
      })
      if (!response.ok) throw new Error("Failed to create webhook")
      return await response.json()
    } catch (error) {
      console.error("Error creating webhook:", error)
      throw error
    }
  }

  // Variables de Entorno
  async getEnvironmentVariables(): Promise<EnvironmentVariable[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/system/env`)
      if (!response.ok) throw new Error("Failed to fetch environment variables")
      return await response.json()
    } catch (error) {
      console.error("Error fetching environment variables:", error)
      return this.getMockEnvironmentVariables()
    }
  }

  async updateEnvironmentVariables(variables: EnvironmentVariable[]): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/system/env`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ variables }),
      })
      if (!response.ok) throw new Error("Failed to update environment variables")
    } catch (error) {
      console.error("Error updating environment variables:", error)
      throw error
    }
  }

  // Automatizaciones
  async getAutomations(): Promise<Automation[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/system/automations`)
      if (!response.ok) throw new Error("Failed to fetch automations")
      return await response.json()
    } catch (error) {
      console.error("Error fetching automations:", error)
      return this.getMockAutomations()
    }
  }

  async toggleAutomation(automationId: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/system/automations/${automationId}/toggle`, {
        method: "PUT",
      })
      if (!response.ok) throw new Error("Failed to toggle automation")
    } catch (error) {
      console.error("Error toggling automation:", error)
      throw error
    }
  }

  // Métricas del Sistema
  async getSystemMetrics(): Promise<SystemMetrics> {
    try {
      const response = await fetch(`${this.baseUrl}/api/admin/metrics`)
      if (!response.ok) throw new Error("Failed to fetch system metrics")
      return await response.json()
    } catch (error) {
      console.error("Error fetching system metrics:", error)
      return this.getMockSystemMetrics()
    }
  }

  // Export/Import
  async exportConfig(): Promise<Blob> {
    try {
      const response = await fetch(`${this.baseUrl}/api/admin/export`)
      if (!response.ok) throw new Error("Failed to export config")
      return await response.blob()
    } catch (error) {
      console.error("Error exporting config:", error)
      throw error
    }
  }

  async importConfig(file: File): Promise<void> {
    try {
      const formData = new FormData()
      formData.append("config", file)

      const response = await fetch(`${this.baseUrl}/api/admin/import`, {
        method: "POST",
        body: formData,
      })
      if (!response.ok) throw new Error("Failed to import config")
    } catch (error) {
      console.error("Error importing config:", error)
      throw error
    }
  }

  // Datos Mock para fallback
  private getMockSystemConfig(): SystemConfig[] {
    return [
      {
        id: "ai_response_speed",
        name: "Velocidad de Respuesta IA",
        description: "Controla la velocidad de procesamiento de Vicky",
        value: 0.7,
        type: "number",
        category: "ai",
        editable: true,
        requires_restart: false,
      },
      {
        id: "tts_quality",
        name: "Calidad TTS",
        description: "Nivel de calidad para síntesis de voz",
        value: "high",
        type: "string",
        category: "ai",
        editable: true,
        requires_restart: true,
      },
      {
        id: "auto_translation",
        name: "Traducción Automática",
        description: "Activar traducción automática en tiempo real",
        value: true,
        type: "boolean",
        category: "general",
        editable: true,
        requires_restart: false,
      },
      {
        id: "api_rate_limit",
        name: "Límite de Peticiones API",
        description: "Número máximo de peticiones por minuto",
        value: 1000,
        type: "number",
        category: "api",
        editable: true,
        requires_restart: false,
      },
    ]
  }

  private getMockIntegrations(): Integration[] {
    return [
      {
        id: "openai",
        name: "OpenAI",
        type: "ai",
        status: "connected",
        provider: "OpenAI Inc.",
        description: "Integración con modelos GPT para funcionalidades avanzadas",
        config: { api_key: "sk-***", model: "gpt-4" },
        last_test: "2025-01-31T23:45:00Z",
        latency_ms: 245,
        icon: "🤖",
      },
      {
        id: "google_cloud",
        name: "Google Cloud",
        type: "cloud",
        status: "connected",
        provider: "Google LLC",
        description: "Servicios de nube para almacenamiento y procesamiento",
        config: { project_id: "vokaflow-prod", region: "us-central1" },
        last_test: "2025-01-31T23:40:00Z",
        latency_ms: 89,
        icon: "☁️",
      },
      {
        id: "aws",
        name: "Amazon Web Services",
        type: "cloud",
        status: "error",
        provider: "Amazon",
        description: "Infraestructura de nube y servicios de IA",
        config: { region: "us-east-1", access_key: "AKIA***" },
        last_test: "2025-01-31T23:30:00Z",
        error_message: "Invalid credentials",
        icon: "🔶",
      },
      {
        id: "stripe",
        name: "Stripe",
        type: "analytics",
        status: "connected",
        provider: "Stripe Inc.",
        description: "Procesamiento de pagos y facturación",
        config: { publishable_key: "pk_***", webhook_secret: "whsec_***" },
        last_test: "2025-01-31T23:35:00Z",
        latency_ms: 156,
        icon: "💳",
      },
    ]
  }

  private getMockApiKeys(): ApiKey[] {
    return [
      {
        id: "key_1",
        name: "Producción Principal",
        key_preview: "vkf_prod_***abc123",
        permissions: ["read", "write", "admin"],
        created_at: "2025-01-15T10:00:00Z",
        last_used: "2025-01-31T23:45:00Z",
        status: "active",
        usage_count: 15420,
        rate_limit: 1000,
      },
      {
        id: "key_2",
        name: "Desarrollo",
        key_preview: "vkf_dev_***xyz789",
        permissions: ["read", "write"],
        created_at: "2025-01-20T14:30:00Z",
        last_used: "2025-01-31T22:15:00Z",
        status: "active",
        usage_count: 2340,
        rate_limit: 500,
      },
      {
        id: "key_3",
        name: "Testing Temporal",
        key_preview: "vkf_test_***def456",
        permissions: ["read"],
        created_at: "2025-01-30T09:00:00Z",
        last_used: "2025-01-31T20:00:00Z",
        expires_at: "2025-02-15T00:00:00Z",
        status: "active",
        usage_count: 89,
        rate_limit: 100,
      },
    ]
  }

  private getMockWebhooks(): Webhook[] {
    return [
      {
        id: "webhook_1",
        name: "Notificaciones Slack",
        url: "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX",
        events: ["user.created", "translation.completed", "error.critical"],
        status: "active",
        last_triggered: "2025-01-31T23:30:00Z",
        success_count: 1250,
        error_count: 3,
        headers: { "Content-Type": "application/json" },
        payload_template: '{"text": "VokaFlow: {{event.type}} - {{event.message}}"}',
      },
      {
        id: "webhook_2",
        name: "Analytics Dashboard",
        url: "https://analytics.vokaflow.com/webhook",
        events: ["user.activity", "api.usage", "model.performance"],
        status: "active",
        last_triggered: "2025-01-31T23:45:00Z",
        success_count: 8920,
        error_count: 12,
        headers: { Authorization: "Bearer ***", "Content-Type": "application/json" },
        payload_template: '{"event": "{{event.type}}", "data": {{event.data}}, "timestamp": "{{timestamp}}"}',
      },
    ]
  }

  private getMockEnvironmentVariables(): EnvironmentVariable[] {
    return [
      {
        key: "OPENAI_API_KEY",
        value: "sk-***************************",
        category: "secrets",
        description: "Clave API para servicios de OpenAI",
        is_secret: true,
        last_modified: "2025-01-25T10:00:00Z",
      },
      {
        key: "DATABASE_URL",
        value: "postgresql://user:***@localhost:5432/vokaflow",
        category: "production",
        description: "URL de conexión a la base de datos principal",
        is_secret: true,
        last_modified: "2025-01-20T15:30:00Z",
      },
      {
        key: "DEBUG_MODE",
        value: "false",
        category: "development",
        description: "Activar modo debug para desarrollo",
        is_secret: false,
        last_modified: "2025-01-30T09:15:00Z",
      },
      {
        key: "MAX_CONCURRENT_REQUESTS",
        value: "100",
        category: "production",
        description: "Número máximo de peticiones concurrentes",
        is_secret: false,
        last_modified: "2025-01-28T14:20:00Z",
      },
    ]
  }

  private getMockAutomations(): Automation[] {
    return [
      {
        id: "auto_1",
        name: "Backup Diario",
        description: "Crear backup automático de la configuración cada día a las 3:00 AM",
        trigger: {
          type: "schedule",
          config: { cron: "0 3 * * *", timezone: "UTC" },
        },
        actions: [
          { type: "backup_config", config: { include_secrets: false } },
          { type: "notify_slack", config: { channel: "#ops", message: "Backup completado" } },
        ],
        status: "active",
        last_run: "2025-01-31T03:00:00Z",
        success_count: 31,
        error_count: 0,
      },
      {
        id: "auto_2",
        name: "Limpieza de Logs",
        description: "Eliminar logs antiguos cuando el disco supere el 80% de uso",
        trigger: {
          type: "condition",
          config: { metric: "disk_usage", operator: ">", value: 80 },
        },
        actions: [
          { type: "cleanup_logs", config: { older_than_days: 30 } },
          { type: "notify_admin", config: { message: "Limpieza de logs ejecutada" } },
        ],
        status: "active",
        last_run: "2025-01-29T14:22:00Z",
        success_count: 5,
        error_count: 0,
      },
      {
        id: "auto_3",
        name: "Reinicio de Modelos IA",
        description: "Reiniciar modelos IA si la latencia supera los 5 segundos",
        trigger: {
          type: "condition",
          config: { metric: "ai_latency", operator: ">", value: 5000 },
        },
        actions: [
          { type: "restart_ai_models", config: { models: ["qwen", "whisper"] } },
          { type: "alert_critical", config: { message: "Modelos IA reiniciados por alta latencia" } },
        ],
        status: "inactive",
        last_run: "2025-01-28T16:45:00Z",
        success_count: 2,
        error_count: 1,
      },
    ]
  }

  private getMockSystemMetrics(): SystemMetrics {
    return {
      apis_online: 23,
      apis_total: 25,
      active_keys: 45,
      environment_variables: 89,
      active_automations: 12,
      recent_activity: [
        {
          timestamp: "2025-01-31T23:45:00Z",
          action: "config_updated",
          description: "Configuración de IA actualizada",
          type: "success",
        },
        {
          timestamp: "2025-01-31T23:30:00Z",
          action: "api_key_renewed",
          description: "API key de producción renovada",
          type: "info",
        },
        {
          timestamp: "2025-01-31T23:15:00Z",
          action: "webhook_added",
          description: "Nuevo webhook para Slack configurado",
          type: "success",
        },
        {
          timestamp: "2025-01-31T22:45:00Z",
          action: "integration_error",
          description: "Error en conexión con AWS",
          type: "error",
        },
      ],
    }
  }
}

export const settingsService = new SettingsService()

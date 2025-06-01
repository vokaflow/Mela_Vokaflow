export interface SystemConfig {
  id: string
  name: string
  description: string
  value: any
  type: "boolean" | "string" | "number" | "object"
  category: "general" | "ai" | "api" | "security" | "performance"
  editable: boolean
  requires_restart: boolean
}

export interface Integration {
  id: string
  name: string
  type: "cloud" | "ai" | "database" | "analytics" | "communication"
  status: "connected" | "disconnected" | "error" | "testing"
  provider: string
  description: string
  config: Record<string, any>
  last_test: string
  latency_ms?: number
  error_message?: string
  icon: string
}

export interface ApiKey {
  id: string
  name: string
  key_preview: string
  permissions: string[]
  created_at: string
  last_used: string
  expires_at?: string
  status: "active" | "expired" | "revoked"
  usage_count: number
  rate_limit: number
}

export interface Webhook {
  id: string
  name: string
  url: string
  events: string[]
  status: "active" | "inactive" | "error"
  last_triggered: string
  success_count: number
  error_count: number
  headers: Record<string, string>
  payload_template: string
}

export interface EnvironmentVariable {
  key: string
  value: string
  category: "development" | "production" | "testing" | "secrets"
  description?: string
  is_secret: boolean
  last_modified: string
}

export interface Automation {
  id: string
  name: string
  description: string
  trigger: {
    type: "schedule" | "event" | "condition"
    config: Record<string, any>
  }
  actions: Array<{
    type: string
    config: Record<string, any>
  }>
  status: "active" | "inactive" | "error"
  last_run: string
  success_count: number
  error_count: number
}

export interface SystemMetrics {
  apis_online: number
  apis_total: number
  active_keys: number
  environment_variables: number
  active_automations: number
  recent_activity: Array<{
    timestamp: string
    action: string
    description: string
    type: "info" | "warning" | "error" | "success"
  }>
}

export interface ConfigBackup {
  id: string
  name: string
  created_at: string
  size_mb: number
  type: "manual" | "automatic"
  description?: string
  config_sections: string[]
}

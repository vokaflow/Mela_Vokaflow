export interface ApiEndpoint {
  path: string
  method: "GET" | "POST" | "PUT" | "DELETE" | "PATCH"
  router: string
  description: string
  status: "healthy" | "slow" | "error" | "disabled"
  avgLatency: number
  lastError?: string
  requestCount: number
  errorRate: number
  lastSeen: string
}

export interface ApiMetrics {
  endpoint: string
  method: string
  status_code: number
  response_time: number
  timestamp: string
  user_id?: string
  ip_address?: string
  error_message?: string
}

export interface TestRequest {
  method: string
  url: string
  headers: Record<string, string>
  body?: any
  auth?: {
    type: "bearer" | "apikey"
    value: string
  }
}

export interface TestResponse {
  status: number
  statusText: string
  headers: Record<string, string>
  body: any
  responseTime: number
  error?: string
}

export interface ApiRouter {
  name: string
  icon: string
  endpoints: ApiEndpoint[]
  status: "online" | "offline" | "maintenance"
  totalEndpoints: number
  healthyEndpoints: number
}

export interface MaintenanceSchedule {
  id: string
  scheduledTime: string
  duration: number
  affectedServices: string[]
  notificationLead: number
  autoResume: boolean
  status: "scheduled" | "active" | "completed"
}

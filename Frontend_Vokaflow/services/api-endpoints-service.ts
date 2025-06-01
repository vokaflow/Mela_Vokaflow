import type { ApiMetrics, TestRequest, TestResponse, ApiRouter } from "../types/api-endpoints"

class ApiEndpointsService {
  private baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

  // Cargar esquema OpenAPI completo
  async loadApiSchema(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/openapi.json`)
      if (!response.ok) throw new Error("Failed to load API schema")
      return await response.json()
    } catch (error) {
      console.warn("Using mock API schema:", error)
      return this.getMockApiSchema()
    }
  }

  // Obtener métricas de endpoints
  async getApiMetrics(): Promise<ApiMetrics[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/system/system/api-metrics`)
      if (!response.ok) throw new Error("Failed to load API metrics")
      return await response.json()
    } catch (error) {
      console.warn("Using mock API metrics:", error)
      return this.getMockApiMetrics()
    }
  }

  // Obtener estado de monitoreo
  async getMonitoringMetrics(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/api/monitoring/metrics`)
      if (!response.ok) throw new Error("Failed to load monitoring metrics")
      return await response.json()
    } catch (error) {
      console.warn("Using mock monitoring metrics:", error)
      return this.getMockMonitoringMetrics()
    }
  }

  // Ejecutar test de API
  async executeApiTest(request: TestRequest): Promise<TestResponse> {
    const startTime = performance.now()

    try {
      const response = await fetch(request.url, {
        method: request.method,
        headers: {
          "Content-Type": "application/json",
          ...request.headers,
          ...(request.auth?.type === "bearer" ? { Authorization: `Bearer ${request.auth.value}` } : {}),
          ...(request.auth?.type === "apikey" ? { "X-API-Key": request.auth.value } : {}),
        },
        body: request.body ? JSON.stringify(request.body) : undefined,
      })

      const endTime = performance.now()
      const responseTime = endTime - startTime

      let body
      try {
        body = await response.json()
      } catch {
        body = await response.text()
      }

      return {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries()),
        body,
        responseTime,
      }
    } catch (error: any) {
      return {
        status: 0,
        statusText: "Network Error",
        headers: {},
        body: null,
        responseTime: performance.now() - startTime,
        error: error.message,
      }
    }
  }

  // Control de mantenimiento
  async setMaintenanceMode(enabled: boolean): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/system/system/${enabled ? "shutdown" : "restart"}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      })
      return response.ok
    } catch (error) {
      console.warn("Maintenance mode simulation:", error)
      return true // Simular éxito en modo mock
    }
  }

  // Datos mock para fallback
  private getMockApiSchema(): any {
    return {
      openapi: "3.0.0",
      info: { title: "VokaFlow API", version: "1.0.0" },
      paths: {
        "/api/health/": { get: { summary: "Health check" } },
        "/api/health/status": { get: { summary: "Detailed status" } },
        "/api/health/version": { get: { summary: "Version info" } },
        "/api/vicky/process": { post: { summary: "Process AI request" } },
        "/api/vicky/status": { get: { summary: "AI status" } },
        "/api/translate/": { post: { summary: "Translate text" } },
        "/api/translate/langs": { get: { summary: "Supported languages" } },
        "/api/translate/stats": { get: { summary: "Translation stats" } },
        "/api/translate/history": { get: { summary: "Translation history" } },
      },
    }
  }

  private getMockApiMetrics(): ApiMetrics[] {
    return [
      {
        endpoint: "/api/health/status",
        method: "GET",
        status_code: 200,
        response_time: 12,
        timestamp: new Date().toISOString(),
        user_id: "dw7",
        ip_address: "192.168.1.119",
      },
      {
        endpoint: "/api/vicky/process",
        method: "POST",
        status_code: 200,
        response_time: 245,
        timestamp: new Date(Date.now() - 30000).toISOString(),
        user_id: "dw7",
        ip_address: "192.168.1.119",
      },
      {
        endpoint: "/api/translate/history",
        method: "GET",
        status_code: 500,
        response_time: 30000,
        timestamp: new Date(Date.now() - 60000).toISOString(),
        user_id: "dw7",
        ip_address: "192.168.1.119",
        error_message: "Database connection timeout",
      },
    ]
  }

  private getMockMonitoringMetrics(): any {
    return {
      total_endpoints: 103,
      healthy_endpoints: 98,
      slow_endpoints: 4,
      error_endpoints: 1,
      avg_response_time: 145,
      success_rate: 98.9,
      error_rate: 1.1,
      requests_per_hour: 2340,
    }
  }

  // Obtener routers organizados
  async getApiRouters(): Promise<ApiRouter[]> {
    const schema = await this.loadApiSchema()
    const metrics = await this.getApiMetrics()

    const routers: ApiRouter[] = [
      {
        name: "health",
        icon: "🏥",
        endpoints: [],
        status: "online",
        totalEndpoints: 3,
        healthyEndpoints: 3,
      },
      {
        name: "vicky",
        icon: "🧠",
        endpoints: [],
        status: "online",
        totalEndpoints: 2,
        healthyEndpoints: 1,
      },
      {
        name: "translate",
        icon: "🌍",
        endpoints: [],
        status: "online",
        totalEndpoints: 4,
        healthyEndpoints: 3,
      },
      {
        name: "conversations",
        icon: "💬",
        endpoints: [],
        status: "online",
        totalEndpoints: 9,
        healthyEndpoints: 9,
      },
      {
        name: "files",
        icon: "📁",
        endpoints: [],
        status: "online",
        totalEndpoints: 8,
        healthyEndpoints: 8,
      },
      {
        name: "system",
        icon: "🔧",
        endpoints: [],
        status: "online",
        totalEndpoints: 6,
        healthyEndpoints: 6,
      },
      {
        name: "models",
        icon: "🧬",
        endpoints: [],
        status: "online",
        totalEndpoints: 8,
        healthyEndpoints: 8,
      },
      {
        name: "analytics",
        icon: "📊",
        endpoints: [],
        status: "online",
        totalEndpoints: 8,
        healthyEndpoints: 8,
      },
      {
        name: "notifications",
        icon: "🔔",
        endpoints: [],
        status: "online",
        totalEndpoints: 8,
        healthyEndpoints: 8,
      },
      {
        name: "admin",
        icon: "👑",
        endpoints: [],
        status: "online",
        totalEndpoints: 8,
        healthyEndpoints: 8,
      },
      {
        name: "api-keys",
        icon: "🔑",
        endpoints: [],
        status: "online",
        totalEndpoints: 6,
        healthyEndpoints: 6,
      },
      {
        name: "webhooks",
        icon: "🔗",
        endpoints: [],
        status: "online",
        totalEndpoints: 7,
        healthyEndpoints: 7,
      },
      {
        name: "monitoring",
        icon: "📡",
        endpoints: [],
        status: "online",
        totalEndpoints: 7,
        healthyEndpoints: 7,
      },
      {
        name: "kinect",
        icon: "🎮",
        endpoints: [],
        status: "online",
        totalEndpoints: 9,
        healthyEndpoints: 9,
      },
      {
        name: "users",
        icon: "👥",
        endpoints: [],
        status: "online",
        totalEndpoints: 4,
        healthyEndpoints: 4,
      },
      {
        name: "auth",
        icon: "🔐",
        endpoints: [],
        status: "online",
        totalEndpoints: 4,
        healthyEndpoints: 4,
      },
    ]

    return routers
  }
}

export const apiEndpointsService = new ApiEndpointsService()

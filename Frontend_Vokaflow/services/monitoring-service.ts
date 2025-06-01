import { apiClient } from "@/lib/api-client"
import { ENDPOINTS, buildWsUrl } from "@/lib/api-config"

export interface SystemMetrics {
  cpu: number
  memory: number
  disk: number
  network: {
    upload: number
    download: number
  }
  timestamp: string
}

export interface Alert {
  id: string
  type: "error" | "warning" | "info"
  message: string
  timestamp: string
  acknowledged: boolean
  resolved: boolean
}

export interface HealthStatus {
  status: "healthy" | "degraded" | "down"
  version: string
  uptime: number
  services: {
    database: "up" | "down"
    redis: "up" | "down"
    api: "up" | "down"
    websocket: "up" | "down"
  }
}

class MonitoringService {
  private metricsSocket: WebSocket | null = null
  private alertsSocket: WebSocket | null = null

  // Obtener métricas del sistema
  async getSystemMetrics(): Promise<SystemMetrics> {
    try {
      const data = await apiClient.get<SystemMetrics>(ENDPOINTS.MONITORING.METRICS)
      return data
    } catch (error) {
      console.error("Error fetching system metrics:", error)
      // Fallback a datos mock
      return {
        cpu: Math.random() * 100,
        memory: Math.random() * 100,
        disk: Math.random() * 100,
        network: {
          upload: Math.random() * 1000,
          download: Math.random() * 1000,
        },
        timestamp: new Date().toISOString(),
      }
    }
  }

  // Obtener estado de salud
  async getHealthStatus(): Promise<HealthStatus> {
    try {
      const data = await apiClient.get<HealthStatus>(ENDPOINTS.HEALTH.STATUS)
      return data
    } catch (error) {
      console.error("Error fetching health status:", error)
      return {
        status: "down",
        version: "unknown",
        uptime: 0,
        services: {
          database: "down",
          redis: "down",
          api: "down",
          websocket: "down",
        },
      }
    }
  }

  // Obtener alertas
  async getAlerts(): Promise<Alert[]> {
    try {
      const data = await apiClient.get<Alert[]>(ENDPOINTS.MONITORING.ALERTS)
      return data
    } catch (error) {
      console.error("Error fetching alerts:", error)
      return []
    }
  }

  // Conectar WebSocket para métricas en tiempo real
  connectMetricsWebSocket(onMessage: (metrics: SystemMetrics) => void): void {
    try {
      this.metricsSocket = new WebSocket(buildWsUrl("/metrics"))

      this.metricsSocket.onmessage = (event) => {
        const metrics = JSON.parse(event.data)
        onMessage(metrics)
      }

      this.metricsSocket.onerror = (error) => {
        console.error("WebSocket error:", error)
      }

      this.metricsSocket.onclose = () => {
        console.log("Metrics WebSocket disconnected")
        // Reconectar después de 5 segundos
        setTimeout(() => this.connectMetricsWebSocket(onMessage), 5000)
      }
    } catch (error) {
      console.error("Error connecting metrics WebSocket:", error)
    }
  }

  // Desconectar WebSocket
  disconnectMetricsWebSocket(): void {
    if (this.metricsSocket) {
      this.metricsSocket.close()
      this.metricsSocket = null
    }
  }

  // Reconocer alerta
  async acknowledgeAlert(alertId: string): Promise<boolean> {
    try {
      await apiClient.put(`/api/monitoring/alerts/${alertId}/acknowledge`)
      return true
    } catch (error) {
      console.error("Error acknowledging alert:", error)
      return false
    }
  }

  // Resolver alerta
  async resolveAlert(alertId: string): Promise<boolean> {
    try {
      await apiClient.put(`/api/monitoring/alerts/${alertId}/resolve`)
      return true
    } catch (error) {
      console.error("Error resolving alert:", error)
      return false
    }
  }
}

export const monitoringService = new MonitoringService()

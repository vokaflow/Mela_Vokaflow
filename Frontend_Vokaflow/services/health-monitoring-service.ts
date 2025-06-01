import { buildWsUrl } from "@/lib/api-config"

class HealthMonitoringService {
  private metricsSocket: WebSocket | null = null

  constructor() {}

  public connectMetricsWebSocket(): void {
    if (this.metricsSocket) {
      this.disconnectMetricsWebSocket()
    }

    this.metricsSocket = new WebSocket(buildWsUrl("/metrics"))

    this.metricsSocket.onopen = () => {
      console.log("Metrics WebSocket connection opened")
    }

    this.metricsSocket.onmessage = (event) => {
      // Process the incoming metrics data
      const metricsData = JSON.parse(event.data)
      console.log("Received metrics data:", metricsData)
      // You can dispatch an event or update a store with the new metrics data here
    }

    this.metricsSocket.onclose = () => {
      console.log("Metrics WebSocket connection closed")
      this.metricsSocket = null
    }

    this.metricsSocket.onerror = (error) => {
      console.error("Metrics WebSocket error:", error)
      this.metricsSocket = null
    }
  }

  public disconnectMetricsWebSocket(): void {
    if (this.metricsSocket) {
      this.metricsSocket.close()
      this.metricsSocket = null
    }
  }
}

export default HealthMonitoringService

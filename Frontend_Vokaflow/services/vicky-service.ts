import { apiClient } from "@/lib/api-client"
import type {
  VickyStatus,
  VickyMessage,
  VickyProcessRequest,
  VickyProcessResponse,
  VickyPersonalitySettings,
  VickyMetrics,
  VickyDecision,
} from "@/types/vicky"

class VickyService {
  // Obtener estado de Vicky
  async getStatus(): Promise<VickyStatus> {
    try {
      const data = await apiClient.get<VickyStatus>("/api/vicky/vicky/status")
      return data
    } catch (error) {
      console.error("Error fetching Vicky status:", error)
      // Fallback a datos mock si falla la API
      return {
        status: "offline",
        version: "1.0.0",
        uptime: 0,
        lastActivity: new Date().toISOString(),
        processingQueue: 0,
        memoryUsage: {
          total: 8192,
          used: 4096,
          free: 4096,
        },
        cpuUsage: 0,
        technicalBalance: 67,
        emotionalBalance: 33,
        healthStatus: "offline",
      }
    }
  }

  // Procesar mensaje con Vicky
  async processMessage(request: VickyProcessRequest): Promise<VickyProcessResponse> {
    try {
      const data = await apiClient.post<VickyProcessResponse>("/api/vicky/vicky/process", request)
      return data
    } catch (error) {
      console.error("Error processing message with Vicky:", error)
      // Fallback response
      return {
        response:
          "Lo siento, no puedo procesar tu mensaje en este momento. El servicio de Vicky AI está temporalmente no disponible.",
        confidence: 0,
        processingTime: 0,
        messageId: `fallback-${Date.now()}`,
        type: "error",
      }
    }
  }

  // Obtener historial de conversaciones
  async getHistory(): Promise<VickyMessage[]> {
    try {
      // Este endpoint no está en la lista proporcionada, pero lo implementamos
      // para mantener la funcionalidad. Podría ser necesario ajustarlo.
      const data = await apiClient.get<VickyMessage[]>("/api/vicky/history")
      return data
    } catch (error) {
      console.error("Error fetching Vicky history:", error)
      return []
    }
  }

  // Actualizar configuración de personalidad
  async updatePersonality(settings: VickyPersonalitySettings): Promise<boolean> {
    try {
      // Este endpoint no está en la lista proporcionada, pero lo implementamos
      // para mantener la funcionalidad. Podría ser necesario ajustarlo.
      await apiClient.put("/api/vicky/personality", settings)
      return true
    } catch (error) {
      console.error("Error updating Vicky personality:", error)
      return false
    }
  }

  // Obtener métricas de Vicky
  async getMetrics(): Promise<VickyMetrics> {
    try {
      // Este endpoint no está en la lista proporcionada, pero lo implementamos
      // para mantener la funcionalidad. Podría ser necesario ajustarlo.
      const data = await apiClient.get<VickyMetrics>("/api/vicky/metrics")
      return data
    } catch (error) {
      console.error("Error fetching Vicky metrics:", error)
      // Fallback metrics
      return {
        totalProcessed: 0,
        averageConfidence: 0,
        averageProcessingTime: 0,
        successRate: 0,
        errorRate: 0,
        topRequestTypes: [],
      }
    }
  }

  // Obtener decisiones de Vicky
  async getDecisions(): Promise<VickyDecision[]> {
    try {
      // Este endpoint no está en la lista proporcionada, pero lo implementamos
      // para mantener la funcionalidad. Podría ser necesario ajustarlo.
      const data = await apiClient.get<VickyDecision[]>("/api/vicky/decisions")
      return data
    } catch (error) {
      console.error("Error fetching Vicky decisions:", error)
      return []
    }
  }
}

export const vickyService = new VickyService()

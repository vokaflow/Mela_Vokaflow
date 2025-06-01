export interface VickyStatus {
  status: "online" | "offline" | "processing" | "error"
  version: string
  uptime: number
  lastActivity: string
  processingQueue: number
  memoryUsage: {
    total: number
    used: number
    free: number
  }
  cpuUsage: number
  technicalBalance: number
  emotionalBalance: number
  healthStatus: string
}

export interface VickyMessage {
  id: string
  message: string
  response: string
  timestamp: string
  processingTime: number
  confidence: number
  type: string
  context?: string
}

export interface VickyProcessRequest {
  message: string
  context?: string
  userId?: string
  technicalBalance?: number
  emotionalBalance?: number
}

export interface VickyProcessResponse {
  response: string
  confidence: number
  processingTime: number
  messageId: string
  type: string
  context?: string
}

export interface VickyPersonalitySettings {
  technicalBalance: number
  emotionalBalance: number
  creativityLevel: number
  formalityLevel: number
  verbosityLevel: number
  empathyLevel: number
}

export interface VickyMetrics {
  totalProcessed: number
  averageConfidence: number
  averageProcessingTime: number
  successRate: number
  errorRate: number
  topRequestTypes: Array<{ type: string; count: number }>
}

export interface VickyDecision {
  id: number
  timestamp: string
  confidence: number
  type: string
  context: string
  decision: string
  result: "success" | "warning" | "error"
  responseTime: string
}

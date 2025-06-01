export interface Translation {
  original: string
  translated: string
  sourceLanguage: string
  targetLanguage: string
  confidence: number
  timestamp: number
}

export interface Message {
  id: string
  text: string
  translation?: Translation
  sender: "user" | "other" | "vicky"
  timestamp: number
  status: "sending" | "sent" | "delivered" | "read" | "translated"
  type: "text" | "voice" | "image"
  mediaUrl?: string
  audioDuration?: number
  imageText?: string
}

export interface Conversation {
  id: string
  name: string
  avatar: string
  sourceLanguage: string
  targetLanguage: string
  messages: Message[]
  isTyping: boolean
  lastActive: number
}

export interface DemoMetrics {
  latency: {
    current: number
    average: number
    history: number[]
  }
  accuracy: {
    "es-en": number
    "en-es": number
    "fr-es": number
    overall: number
  }
  audio: {
    ttsStatus: "ok" | "error" | "loading"
    sttStatus: "ok" | "error" | "loading"
    quality: "HD" | "SD" | "LOW"
    latency: number
  }
  translations: {
    total: number
    perMinute: number
    successful: number
    failed: number
  }
}

export interface DemoConfig {
  language: string
  speed: number
  autoScroll: boolean
  sounds: boolean
  debug: boolean
  scenario: "casual" | "business" | "emergency" | "technical" | "custom"
}

export interface DemoState {
  conversations: Conversation[]
  activeConversationId: string
  metrics: DemoMetrics
  config: DemoConfig
  isRecording: boolean
  isProcessing: boolean
  isAutoDemo: boolean
}

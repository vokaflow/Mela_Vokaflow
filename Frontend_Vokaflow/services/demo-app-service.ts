import type { DemoMetrics, Translation } from "../types/demo-app"

// Constantes para simular latencia realista
const MIN_LATENCY = 200 // 200ms
const MAX_LATENCY = 800 // 800ms

export const DemoAppService = {
  // Traducir texto
  async translateText(text: string, sourceLanguage: string, targetLanguage: string): Promise<Translation> {
    try {
      // Intentar usar la API real si está disponible
      const response = await fetch("/api/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, sourceLanguage, targetLanguage }),
      })

      if (response.ok) {
        return await response.json()
      }

      // Fallback a simulación si la API no está disponible
      return simulateTranslation(text, sourceLanguage, targetLanguage)
    } catch (error) {
      console.error("Error en traducción:", error)
      return simulateTranslation(text, sourceLanguage, targetLanguage)
    }
  },

  // Sintetizar voz (TTS)
  async synthesizeVoice(text: string, language: string): Promise<string> {
    try {
      const response = await fetch("/api/tts/synthesize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, language }),
      })

      if (response.ok) {
        const blob = await response.blob()
        return URL.createObjectURL(blob)
      }

      // Fallback a audio simulado
      return "/audio/demo-tts.mp3"
    } catch (error) {
      console.error("Error en síntesis de voz:", error)
      return "/audio/demo-tts.mp3"
    }
  },

  // Transcribir voz (STT)
  async transcribeVoice(audioBlob: Blob, language: string): Promise<string> {
    try {
      const formData = new FormData()
      formData.append("audio", audioBlob)
      formData.append("language", language)

      const response = await fetch("/api/stt/transcribe", {
        method: "POST",
        body: formData,
      })

      if (response.ok) {
        const data = await response.json()
        return data.text
      }

      // Fallback a texto simulado
      return simulateTranscription(language)
    } catch (error) {
      console.error("Error en transcripción de voz:", error)
      return simulateTranscription(language)
    }
  },

  // Chat con Vicky AI
  async chatWithVicky(message: string, language: string): Promise<string> {
    try {
      const response = await fetch("/api/vicky/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, language }),
      })

      if (response.ok) {
        const data = await response.json()
        return data.response
      }

      // Fallback a respuesta simulada
      return simulateVickyResponse(message, language)
    } catch (error) {
      console.error("Error en chat con Vicky:", error)
      return simulateVickyResponse(message, language)
    }
  },

  // Extraer texto de imágenes (OCR)
  async extractTextFromImage(imageUrl: string): Promise<string> {
    try {
      const response = await fetch("/api/ocr/extract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ imageUrl }),
      })

      if (response.ok) {
        const data = await response.json()
        return data.text
      }

      // Fallback a texto simulado
      return "Sample text extracted from image. This would be the actual text from OCR."
    } catch (error) {
      console.error("Error en OCR:", error)
      return "Sample text extracted from image. This would be the actual text from OCR."
    }
  },

  // Obtener métricas en tiempo real
  async getMetrics(): Promise<DemoMetrics> {
    try {
      const response = await fetch("/api/demo/metrics")

      if (response.ok) {
        return await response.json()
      }

      // Fallback a métricas simuladas
      return simulateMetrics()
    } catch (error) {
      console.error("Error al obtener métricas:", error)
      return simulateMetrics()
    }
  },

  // Enviar feedback sobre traducciones
  async sendFeedback(translationId: string, isGood: boolean): Promise<void> {
    try {
      await fetch("/api/demo/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ translationId, isGood }),
      })
    } catch (error) {
      console.error("Error al enviar feedback:", error)
    }
  },

  // Obtener escenarios predefinidos
  async getScenarios(): Promise<string[]> {
    try {
      const response = await fetch("/api/demo/scenarios")

      if (response.ok) {
        return await response.json()
      }

      // Fallback a escenarios predefinidos
      return ["casual", "business", "emergency", "technical", "custom"]
    } catch (error) {
      console.error("Error al obtener escenarios:", error)
      return ["casual", "business", "emergency", "technical", "custom"]
    }
  },
}

// Funciones auxiliares para simulación

function simulateTranslation(text: string, sourceLanguage: string, targetLanguage: string): Translation {
  // Simulaciones básicas para demo
  const translations: Record<string, Record<string, string>> = {
    es: {
      en: {
        Hola: "Hello",
        "¿Cómo estás?": "How are you?",
        "Buenos días": "Good morning",
        Gracias: "Thank you",
        Adiós: "Goodbye",
      },
    },
    en: {
      es: {
        Hello: "Hola",
        "How are you?": "Cómo estás?",
        "Good morning": "Buenos días",
        "Thank you": "Gracias",
        Goodbye: "Adiós",
      },
    },
  }

  // Simular latencia
  const latency = Math.random() * (MAX_LATENCY - MIN_LATENCY) + MIN_LATENCY

  // Buscar traducción predefinida o generar una simulada
  let translated = ""
  if (translations[sourceLanguage]?.[targetLanguage]?.[text]) {
    translated = translations[sourceLanguage][targetLanguage][text]
  } else {
    // Simulación simple para demo
    translated = `[${targetLanguage}] ${text}`
  }

  return {
    original: text,
    translated,
    sourceLanguage,
    targetLanguage,
    confidence: 0.85 + Math.random() * 0.15, // Entre 85% y 100%
    timestamp: Date.now(),
  }
}

function simulateTranscription(language: string): string {
  const phrases: Record<string, string[]> = {
    es: [
      "Hola, ¿cómo puedo ayudarte hoy?",
      "Me gustaría agendar una reunión para mañana",
      "Necesito información sobre el nuevo producto",
    ],
    en: [
      "Hello, how can I help you today?",
      "I would like to schedule a meeting for tomorrow",
      "I need information about the new product",
    ],
  }

  const langPhrases = phrases[language] || phrases["en"]
  return langPhrases[Math.floor(Math.random() * langPhrases.length)]
}

function simulateVickyResponse(message: string, language: string): string {
  const responses: Record<string, string[]> = {
    es: [
      "¡Hola! Soy Vicky, tu asistente virtual. ¿En qué puedo ayudarte hoy?",
      "Entiendo tu pregunta. Déjame buscar esa información para ti.",
      "Según mis datos, la respuesta es positiva. ¿Necesitas más detalles?",
    ],
    en: [
      "Hello! I'm Vicky, your virtual assistant. How can I help you today?",
      "I understand your question. Let me look up that information for you.",
      "According to my data, the answer is positive. Do you need more details?",
    ],
  }

  const langResponses = responses[language] || responses["en"]
  return langResponses[Math.floor(Math.random() * langResponses.length)]
}

function simulateMetrics(): DemoMetrics {
  return {
    latency: {
      current: 0.3 + Math.random() * 0.2,
      average: 0.4,
      history: Array(10)
        .fill(0)
        .map(() => 0.2 + Math.random() * 0.5),
    },
    accuracy: {
      "es-en": 0.97 + Math.random() * 0.03,
      "en-es": 0.96 + Math.random() * 0.03,
      "fr-es": 0.93 + Math.random() * 0.04,
      overall: 0.95 + Math.random() * 0.03,
    },
    audio: {
      ttsStatus: "ok",
      sttStatus: "ok",
      quality: "HD",
      latency: 0.2 + Math.random() * 0.3,
    },
    translations: {
      total: 1247 + Math.floor(Math.random() * 10),
      perMinute: 12 + Math.floor(Math.random() * 8),
      successful: 1240 + Math.floor(Math.random() * 7),
      failed: 7 + Math.floor(Math.random() * 3),
    },
  }
}

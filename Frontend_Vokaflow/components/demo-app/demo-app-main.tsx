"use client"

import { useState, useEffect } from "react"
import type { DemoConfig, DemoState } from "@/types/demo-app"
import { DemoAppService } from "@/services/demo-app-service"
import { DemoMetrics } from "@/components/demo-app/demo-metrics"
import { DemoChatSimulator } from "@/components/demo-app/demo-chat-simulator"
import { DemoControls } from "@/components/demo-app/demo-controls"

export function DemoAppMain() {
  // Estado inicial de la demo
  const [demoState, setDemoState] = useState<DemoState>({
    conversations: [
      {
        id: "demo-chat",
        name: "Demo Chat",
        avatar: "/placeholder.svg?height=40&width=40",
        sourceLanguage: "es",
        targetLanguage: "en",
        messages: [],
        isTyping: false,
        lastActive: Date.now(),
      },
    ],
    activeConversationId: "demo-chat",
    metrics: {
      latency: {
        current: 0.3,
        average: 0.4,
        history: Array(10).fill(0.4),
      },
      accuracy: {
        "es-en": 0.98,
        "en-es": 0.97,
        "fr-es": 0.94,
        overall: 0.96,
      },
      audio: {
        ttsStatus: "ok",
        sttStatus: "ok",
        quality: "HD",
        latency: 0.2,
      },
      translations: {
        total: 1247,
        perMinute: 15,
        successful: 1240,
        failed: 7,
      },
    },
    config: {
      language: "es",
      speed: 1,
      autoScroll: true,
      sounds: true,
      debug: false,
      scenario: "casual",
    },
    isRecording: false,
    isProcessing: false,
    isAutoDemo: false,
  })

  // Obtener la conversación activa
  const activeConversation =
    demoState.conversations.find((conv) => conv.id === demoState.activeConversationId) || demoState.conversations[0]

  // Efecto para inicializar la demo
  useEffect(() => {
    // Inicializar con un mensaje de bienvenida
    setTimeout(() => {
      const welcomeMessage = {
        id: `msg-${Date.now()}`,
        text: "¡Hola! Bienvenido a la demo de VokaFlow. Puedes probar la traducción en tiempo real escribiendo un mensaje o usando los tests rápidos.",
        sender: "other",
        timestamp: Date.now(),
        status: "delivered",
        type: "text",
      }

      setDemoState((prev) => ({
        ...prev,
        conversations: prev.conversations.map((conv) =>
          conv.id === prev.activeConversationId
            ? {
                ...conv,
                messages: [...conv.messages, welcomeMessage],
              }
            : conv,
        ),
      }))
    }, 1000)

    // Iniciar WebSocket para métricas en tiempo real (simulado)
    const metricsInterval = setInterval(async () => {
      try {
        const newMetrics = await DemoAppService.getMetrics()

        setDemoState((prev) => ({
          ...prev,
          metrics: {
            ...prev.metrics,
            ...newMetrics,
            latency: {
              ...newMetrics.latency,
              history: [...prev.metrics.latency.history.slice(1), newMetrics.latency.current],
            },
            translations: {
              ...newMetrics.translations,
              total: prev.metrics.translations.total + Math.floor(Math.random() * 3),
            },
          },
        }))
      } catch (error) {
        console.error("Error al actualizar métricas:", error)
      }
    }, 2000)

    return () => {
      clearInterval(metricsInterval)
    }
  }, [])

  // Manejar cambios en la configuración
  const handleConfigChange = (newConfig: DemoConfig) => {
    setDemoState((prev) => ({
      ...prev,
      config: newConfig,
    }))
  }

  // Ejecutar un test rápido
  const runTest = async (testType: string) => {
    switch (testType) {
      case "chat":
        await runChatTest()
        break
      case "voice":
        await runVoiceTest()
        break
      case "ocr":
        await runOCRTest()
        break
      case "auto":
        toggleAutoDemo()
        break
      case "stress":
        await runStressTest()
        break
      default:
        console.warn("Tipo de test no reconocido:", testType)
    }
  }

  // Test de chat simple
  const runChatTest = async () => {
    // Mensaje de usuario simulado
    const userMessage = {
      id: `msg-${Date.now()}`,
      text: "Hola, ¿cómo funciona la traducción en tiempo real?",
      sender: "user" as const,
      timestamp: Date.now(),
      status: "sending" as const,
      type: "text" as const,
    }

    // Añadir mensaje
    setDemoState((prev) => ({
      ...prev,
      conversations: prev.conversations.map((conv) =>
        conv.id === prev.activeConversationId
          ? {
              ...conv,
              messages: [...conv.messages, userMessage],
              isTyping: true,
            }
          : conv,
      ),
    }))

    // Simular envío y entrega
    setTimeout(() => {
      setDemoState((prev) => ({
        ...prev,
        conversations: prev.conversations.map((conv) =>
          conv.id === prev.activeConversationId
            ? {
                ...conv,
                messages: conv.messages.map((msg) =>
                  msg.id === userMessage.id ? { ...msg, status: "delivered" as const } : msg,
                ),
              }
            : conv,
        ),
      }))
    }, 1000)

    // Traducir y responder
    setTimeout(async () => {
      try {
        const translation = await DemoAppService.translateText(userMessage.text, "es", "en")

        // Actualizar con traducción
        setDemoState((prev) => ({
          ...prev,
          conversations: prev.conversations.map((conv) =>
            conv.id === prev.activeConversationId
              ? {
                  ...conv,
                  messages: conv.messages.map((msg) =>
                    msg.id === userMessage.id ? { ...msg, status: "translated" as const, translation } : msg,
                  ),
                }
              : conv,
          ),
        }))

        // Respuesta automática
        const responseMessage = {
          id: `msg-${Date.now()}`,
          text: "VokaFlow uses advanced AI models to translate text in real-time with high accuracy. The system processes your message, translates it, and delivers it instantly!",
          sender: "other" as const,
          timestamp: Date.now(),
          status: "delivered" as const,
          type: "text" as const,
        }

        setDemoState((prev) => ({
          ...prev,
          conversations: prev.conversations.map((conv) =>
            conv.id === prev.activeConversationId
              ? {
                  ...conv,
                  messages: [...conv.messages, responseMessage],
                  isTyping: false,
                }
              : conv,
          ),
        }))
      } catch (error) {
        console.error("Error en test de chat:", error)
      }
    }, 2000)
  }

  // Test de voz
  const runVoiceTest = async () => {
    const voiceMessage = {
      id: `msg-${Date.now()}`,
      text: "Mensaje de voz de prueba",
      sender: "user" as const,
      timestamp: Date.now(),
      status: "sending" as const,
      type: "voice" as const,
      mediaUrl: "/audio/demo-voice.mp3",
      audioDuration: 3,
    }

    setDemoState((prev) => ({
      ...prev,
      conversations: prev.conversations.map((conv) =>
        conv.id === prev.activeConversationId
          ? {
              ...conv,
              messages: [...conv.messages, voiceMessage],
              isTyping: true,
            }
          : conv,
      ),
    }))

    // Simular transcripción y traducción
    setTimeout(async () => {
      const transcribedText = "Hello, this is a voice message test for VokaFlow"
      const translation = await DemoAppService.translateText(transcribedText, "en", "es")

      setDemoState((prev) => ({
        ...prev,
        conversations: prev.conversations.map((conv) =>
          conv.id === prev.activeConversationId
            ? {
                ...conv,
                messages: conv.messages.map((msg) =>
                  msg.id === voiceMessage.id
                    ? {
                        ...msg,
                        text: transcribedText,
                        translation,
                        status: "translated" as const,
                      }
                    : msg,
                ),
                isTyping: false,
              }
            : conv,
        ),
      }))
    }, 3000)
  }

  // Test de OCR
  const runOCRTest = async () => {
    const imageMessage = {
      id: `msg-${Date.now()}`,
      text: "Imagen con texto",
      sender: "user" as const,
      timestamp: Date.now(),
      status: "sending" as const,
      type: "image" as const,
      mediaUrl: "/placeholder.svg?height=200&width=300&text=Sample+Text+Image",
    }

    setDemoState((prev) => ({
      ...prev,
      conversations: prev.conversations.map((conv) =>
        conv.id === prev.activeConversationId
          ? {
              ...conv,
              messages: [...conv.messages, imageMessage],
              isTyping: true,
            }
          : conv,
      ),
    }))

    // Simular OCR y traducción
    setTimeout(async () => {
      const extractedText = "Welcome to VokaFlow - Real-time translation powered by AI"
      const translation = await DemoAppService.translateText(extractedText, "en", "es")

      setDemoState((prev) => ({
        ...prev,
        conversations: prev.conversations.map((conv) =>
          conv.id === prev.activeConversationId
            ? {
                ...conv,
                messages: conv.messages.map((msg) =>
                  msg.id === imageMessage.id
                    ? {
                        ...msg,
                        imageText: extractedText,
                        translation,
                        status: "translated" as const,
                      }
                    : msg,
                ),
                isTyping: false,
              }
            : conv,
        ),
      }))
    }, 2500)
  }

  // Toggle auto demo
  const toggleAutoDemo = () => {
    setDemoState((prev) => ({
      ...prev,
      isAutoDemo: !prev.isAutoDemo,
    }))

    if (!demoState.isAutoDemo) {
      startAutoDemo()
    }
  }

  // Iniciar demo automática
  const startAutoDemo = async () => {
    const demoMessages = [
      { text: "¡Hola! Vamos a probar VokaFlow", delay: 1000 },
      { text: "Este es un mensaje en español", delay: 3000 },
      { text: "Hello, this is an English message", delay: 5000 },
      { text: "Bonjour, ceci est un message français", delay: 7000 },
      { text: "¿Puedes ver las traducciones en tiempo real?", delay: 9000 },
    ]

    for (const demo of demoMessages) {
      if (!demoState.isAutoDemo) break

      setTimeout(() => {
        if (!demoState.isAutoDemo) return

        const autoMessage = {
          id: `msg-${Date.now()}`,
          text: demo.text,
          sender: "user" as const,
          timestamp: Date.now(),
          status: "sending" as const,
          type: "text" as const,
        }

        setDemoState((prev) => ({
          ...prev,
          conversations: prev.conversations.map((conv) =>
            conv.id === prev.activeConversationId
              ? {
                  ...conv,
                  messages: [...conv.messages, autoMessage],
                }
              : conv,
          ),
        }))

        // Simular traducción después de un momento
        setTimeout(async () => {
          const translation = await DemoAppService.translateText(demo.text, "es", "en")

          setDemoState((prev) => ({
            ...prev,
            conversations: prev.conversations.map((conv) =>
              conv.id === prev.activeConversationId
                ? {
                    ...conv,
                    messages: conv.messages.map((msg) =>
                      msg.id === autoMessage.id ? { ...msg, translation, status: "translated" as const } : msg,
                    ),
                  }
                : conv,
            ),
          }))
        }, 1500)
      }, demo.delay)
    }
  }

  // Test de estrés
  const runStressTest = async () => {
    const stressMessages = Array.from({ length: 10 }, (_, i) => ({
      id: `stress-${Date.now()}-${i}`,
      text: `Mensaje de estrés #${i + 1} - Probando capacidad del sistema`,
      sender: "user" as const,
      timestamp: Date.now() + i * 100,
      status: "sending" as const,
      type: "text" as const,
    }))

    // Enviar todos los mensajes rápidamente
    setDemoState((prev) => ({
      ...prev,
      conversations: prev.conversations.map((conv) =>
        conv.id === prev.activeConversationId
          ? {
              ...conv,
              messages: [...conv.messages, ...stressMessages],
              isTyping: true,
            }
          : conv,
      ),
    }))

    // Procesar traducciones en lotes
    for (let i = 0; i < stressMessages.length; i++) {
      setTimeout(async () => {
        const message = stressMessages[i]
        const translation = await DemoAppService.translateText(message.text, "es", "en")

        setDemoState((prev) => ({
          ...prev,
          conversations: prev.conversations.map((conv) =>
            conv.id === prev.activeConversationId
              ? {
                  ...conv,
                  messages: conv.messages.map((msg) =>
                    msg.id === message.id ? { ...msg, translation, status: "translated" as const } : msg,
                  ),
                  isTyping: i === stressMessages.length - 1 ? false : conv.isTyping,
                }
              : conv,
          ),
        }))
      }, i * 500)
    }
  }

  // Ejecutar un escenario específico
  const runScenario = async (scenario: string) => {
    const scenarios = {
      casual: ["¡Hola! ¿Cómo estás?", "¿Qué planes tienes para hoy?", "Me encanta usar VokaFlow para chatear"],
      business: [
        "Buenos días, necesitamos revisar el proyecto",
        "¿Podríamos agendar una reunión para mañana?",
        "Los resultados del trimestre son excelentes",
      ],
      emergency: ["¡Necesito ayuda urgente!", "¿Hay alguien que hable español?", "Es una emergencia médica"],
      technical: [
        "El sistema está funcionando correctamente",
        "Necesitamos actualizar la base de datos",
        "La API está respondiendo con latencia de 200ms",
      ],
      custom: [
        "Este es un escenario personalizado",
        "Puedes modificar estos mensajes",
        "Para probar casos específicos",
      ],
    }

    const messages = scenarios[scenario] || scenarios.custom

    for (let i = 0; i < messages.length; i++) {
      setTimeout(() => {
        const scenarioMessage = {
          id: `scenario-${Date.now()}-${i}`,
          text: messages[i],
          sender: "user" as const,
          timestamp: Date.now(),
          status: "sending" as const,
          type: "text" as const,
        }

        setDemoState((prev) => ({
          ...prev,
          conversations: prev.conversations.map((conv) =>
            conv.id === prev.activeConversationId
              ? {
                  ...conv,
                  messages: [...conv.messages, scenarioMessage],
                }
              : conv,
          ),
        }))

        // Traducir después de un momento
        setTimeout(async () => {
          const translation = await DemoAppService.translateText(messages[i], "es", "en")

          setDemoState((prev) => ({
            ...prev,
            conversations: prev.conversations.map((conv) =>
              conv.id === prev.activeConversationId
                ? {
                    ...conv,
                    messages: conv.messages.map((msg) =>
                      msg.id === scenarioMessage.id ? { ...msg, translation, status: "translated" as const } : msg,
                    ),
                  }
                : conv,
            ),
          }))
        }, 1000)
      }, i * 2000)
    }
  }

  return (
    <div className="flex h-full bg-voka-dark">
      {/* Métricas en tiempo real - Sidebar izquierdo (20%) */}
      <div className="w-1/5 p-4">
        <DemoMetrics initialMetrics={demoState.metrics} />
      </div>

      {/* Simulador principal - Centro (60%) */}
      <div className="flex-1 p-4">
        <div className="h-full">
          <DemoChatSimulator initialConversation={activeConversation} />
        </div>
      </div>

      {/* Controles de demo - Sidebar derecho (20%) */}
      <div className="w-1/5 p-4">
        <DemoControls
          config={demoState.config}
          onConfigChange={handleConfigChange}
          onRunTest={runTest}
          onRunScenario={runScenario}
        />
      </div>
    </div>
  )
}

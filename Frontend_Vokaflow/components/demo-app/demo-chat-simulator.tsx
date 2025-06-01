"use client"

import { useState, useRef, useEffect } from "react"
import type { Message, Conversation } from "@/types/demo-app"
import { DemoAppService } from "@/services/demo-app-service"

interface DemoChatSimulatorProps {
  initialConversation?: Conversation
}

export function DemoChatSimulator({ initialConversation }: DemoChatSimulatorProps) {
  // Estado para la conversación activa
  const [conversation, setConversation] = useState<Conversation>(
    initialConversation || {
      id: "demo-chat",
      name: "Demo Chat",
      avatar: "/placeholder.svg?height=40&width=40",
      sourceLanguage: "es",
      targetLanguage: "en",
      messages: [],
      isTyping: false,
      lastActive: Date.now(),
    },
  )

  // Estado para el mensaje que se está escribiendo
  const [inputMessage, setInputMessage] = useState("")

  // Estado para grabación de voz
  const [isRecording, setIsRecording] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)

  // Referencias
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const audioRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  // Efecto para scroll automático al final de los mensajes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [conversation.messages])

  // Función para enviar un mensaje de texto
  const sendTextMessage = async () => {
    if (!inputMessage.trim()) return

    // Crear nuevo mensaje
    const newMessage: Message = {
      id: `msg-${Date.now()}`,
      text: inputMessage,
      sender: "user",
      timestamp: Date.now(),
      status: "sending",
      type: "text",
    }

    // Actualizar estado con el nuevo mensaje
    setConversation((prev) => ({
      ...prev,
      messages: [...prev.messages, newMessage],
      isTyping: true,
    }))

    // Limpiar input
    setInputMessage("")

    try {
      // Simular envío (cambiar estado a 'sent')
      setTimeout(() => {
        setConversation((prev) => ({
          ...prev,
          messages: prev.messages.map((msg) => (msg.id === newMessage.id ? { ...msg, status: "sent" } : msg)),
        }))
      }, 500)

      // Simular entrega (cambiar estado a 'delivered')
      setTimeout(() => {
        setConversation((prev) => ({
          ...prev,
          messages: prev.messages.map((msg) => (msg.id === newMessage.id ? { ...msg, status: "delivered" } : msg)),
        }))
      }, 1000)

      // Traducir el mensaje
      const translation = await DemoAppService.translateText(
        inputMessage,
        conversation.sourceLanguage,
        conversation.targetLanguage,
      )

      // Actualizar mensaje con la traducción
      setTimeout(() => {
        setConversation((prev) => ({
          ...prev,
          messages: prev.messages.map((msg) =>
            msg.id === newMessage.id
              ? {
                  ...msg,
                  status: "translated",
                  translation,
                }
              : msg,
          ),
          isTyping: false,
        }))
      }, 1500)

      // Simular respuesta después de un tiempo
      setTimeout(() => {
        simulateResponse(translation.translated)
      }, 3000)
    } catch (error) {
      console.error("Error al enviar mensaje:", error)
      // Marcar mensaje como error
      setConversation((prev) => ({
        ...prev,
        messages: prev.messages.map((msg) => (msg.id === newMessage.id ? { ...msg, status: "error" } : msg)),
        isTyping: false,
      }))
    }
  }

  // Función para simular una respuesta
  const simulateResponse = async (text: string) => {
    // Indicar que el otro usuario está escribiendo
    setConversation((prev) => ({
      ...prev,
      isTyping: true,
    }))

    // Esperar un tiempo aleatorio para simular escritura
    await new Promise((resolve) => setTimeout(resolve, 1000 + Math.random() * 2000))

    // Crear mensaje de respuesta
    const responseMessage: Message = {
      id: `msg-${Date.now()}`,
      text: text,
      sender: "other",
      timestamp: Date.now(),
      status: "delivered",
      type: "text",
    }

    // Traducir la respuesta
    const translation = await DemoAppService.translateText(
      text,
      conversation.targetLanguage,
      conversation.sourceLanguage,
    )

    // Añadir mensaje con traducción
    setConversation((prev) => ({
      ...prev,
      messages: [
        ...prev.messages,
        {
          ...responseMessage,
          translation,
          status: "translated",
        },
      ],
      isTyping: false,
    }))
  }

  // Función para iniciar grabación de voz
  const startVoiceRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)

      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data)
      }

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" })
        const audioUrl = URL.createObjectURL(audioBlob)

        // Crear mensaje de voz
        const voiceMessage: Message = {
          id: `msg-${Date.now()}`,
          text: "Mensaje de voz",
          sender: "user",
          timestamp: Date.now(),
          status: "sending",
          type: "voice",
          mediaUrl: audioUrl,
          audioDuration: recordingTime,
        }

        // Añadir mensaje
        setConversation((prev) => ({
          ...prev,
          messages: [...prev.messages, voiceMessage],
          isTyping: true,
        }))

        try {
          // Transcribir audio
          const transcribedText = await DemoAppService.transcribeVoice(audioBlob, conversation.sourceLanguage)

          // Traducir texto transcrito
          const translation = await DemoAppService.translateText(
            transcribedText,
            conversation.sourceLanguage,
            conversation.targetLanguage,
          )

          // Actualizar mensaje con transcripción y traducción
          setConversation((prev) => ({
            ...prev,
            messages: prev.messages.map((msg) =>
              msg.id === voiceMessage.id
                ? {
                    ...msg,
                    text: transcribedText,
                    translation,
                    status: "translated",
                  }
                : msg,
            ),
            isTyping: false,
          }))

          // Simular respuesta después de un tiempo
          setTimeout(() => {
            simulateResponse(translation.translated)
          }, 3000)
        } catch (error) {
          console.error("Error al procesar audio:", error)
          setConversation((prev) => ({
            ...prev,
            isTyping: false,
          }))
        }

        // Limpiar recursos
        stream.getTracks().forEach((track) => track.stop())
      }

      // Iniciar grabación
      mediaRecorder.start()
      audioRecorderRef.current = mediaRecorder
      setIsRecording(true)

      // Iniciar contador de tiempo
      let seconds = 0
      const timerInterval = setInterval(() => {
        seconds += 1
        setRecordingTime(seconds)
      }, 1000)

      // Guardar intervalo para limpiarlo después
      audioRecorderRef.current.timerInterval = timerInterval
    } catch (error) {
      console.error("Error al iniciar grabación:", error)
      alert("No se pudo acceder al micrófono")
    }
  }

  // Función para detener grabación de voz
  const stopVoiceRecording = () => {
    if (audioRecorderRef.current) {
      audioRecorderRef.current.stop()
      // Limpiar intervalo del timer
      if (audioRecorderRef.current.timerInterval) {
        clearInterval(audioRecorderRef.current.timerInterval)
      }
      setIsRecording(false)
      setRecordingTime(0)
    }
  }

  // Función para simular OCR en imagen
  const simulateOCR = async () => {
    // Crear mensaje de imagen
    const imageMessage: Message = {
      id: `msg-${Date.now()}`,
      text: "Imagen con texto",
      sender: "user",
      timestamp: Date.now(),
      status: "sending",
      type: "image",
      mediaUrl: "/placeholder.svg?height=200&width=300",
    }

    // Añadir mensaje
    setConversation((prev) => ({
      ...prev,
      messages: [...prev.messages, imageMessage],
      isTyping: true,
    }))

    try {
      // Simular procesamiento OCR
      await new Promise((resolve) => setTimeout(resolve, 2000))

      // Texto extraído simulado
      const extractedText = "Sample text extracted from image. This would be the actual text from OCR."

      // Traducir texto extraído
      const translation = await DemoAppService.translateText(
        extractedText,
        conversation.sourceLanguage,
        conversation.targetLanguage,
      )

      // Actualizar mensaje con texto extraído y traducción
      setConversation((prev) => ({
        ...prev,
        messages: prev.messages.map((msg) =>
          msg.id === imageMessage.id
            ? {
                ...msg,
                imageText: extractedText,
                translation,
                status: "translated",
              }
            : msg,
        ),
        isTyping: false,
      }))
    } catch (error) {
      console.error("Error al procesar imagen:", error)
      setConversation((prev) => ({
        ...prev,
        isTyping: false,
      }))
    }
  }

  // Función para renderizar un mensaje individual
  const renderMessage = (message: Message) => {
    const isUser = message.sender === "user"
    const bubbleClass = isUser ? "bg-voka-blue text-white self-end" : "bg-voka-dark text-white self-start"

    return (
      <div key={message.id} className={`flex flex-col max-w-[80%] ${isUser ? "items-end" : "items-start"} mb-4`}>
        {/* Burbuja de mensaje */}
        <div className={`rounded-2xl px-4 py-2 ${bubbleClass}`}>
          {/* Contenido según tipo de mensaje */}
          {message.type === "text" && <p>{message.text}</p>}

          {message.type === "voice" && (
            <div className="flex items-center space-x-2">
              <button className="text-voka-white hover:text-voka-magenta">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
              <div className="h-2 w-24 bg-voka-border rounded-full overflow-hidden">
                <div className="bg-voka-magenta h-full w-3/4"></div>
              </div>
              <span className="text-xs">{message.audioDuration}s</span>
            </div>
          )}

          {message.type === "image" && (
            <div className="space-y-2">
              <img
                src={message.mediaUrl || "/placeholder.svg"}
                alt="Imagen compartida"
                className="rounded-lg max-h-40 w-auto"
              />
              {message.imageText && <p className="text-sm italic">"{message.imageText}"</p>}
            </div>
          )}

          {/* Traducción si existe */}
          {message.translation && (
            <div className="mt-1 pt-1 border-t border-voka-border">
              <p className="text-sm text-voka-gray">
                <span className="text-voka-magenta">
                  {isUser ? conversation.targetLanguage.toUpperCase() : conversation.sourceLanguage.toUpperCase()}:
                </span>{" "}
                {message.translation.translated}
              </p>
            </div>
          )}
        </div>

        {/* Timestamp y estado */}
        <div className="flex items-center mt-1 text-xs text-voka-gray">
          <span>{new Date(message.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>

          {isUser && (
            <span className="ml-1">
              {message.status === "sending" && "⏳"}
              {message.status === "sent" && "✓"}
              {message.status === "delivered" && "✓✓"}
              {message.status === "translated" && "✓✓✓"}
            </span>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full bg-voka-blue-black rounded-lg border border-voka-border overflow-hidden">
      {/* Header del chat */}
      <div className="flex items-center p-4 border-b border-voka-border">
        <div className="flex items-center">
          <img
            src={conversation.avatar || "/placeholder.svg"}
            alt={conversation.name}
            className="w-10 h-10 rounded-full"
          />
          <div className="ml-3">
            <h3 className="text-voka-white font-medium">{conversation.name}</h3>
            <div className="flex items-center text-xs text-voka-gray">
              <span className="w-2 h-2 bg-voka-green rounded-full mr-1"></span>
              <span>En línea</span>
            </div>
          </div>
        </div>
        <div className="ml-auto flex items-center space-x-3">
          <div className="flex items-center bg-voka-dark px-3 py-1 rounded-full">
            <span className="text-voka-white text-sm font-medium">{conversation.sourceLanguage.toUpperCase()}</span>
            <span className="mx-1 text-voka-magenta">⚡</span>
            <span className="text-voka-white text-sm font-medium">{conversation.targetLanguage.toUpperCase()}</span>
          </div>
        </div>
      </div>

      {/* Área de mensajes */}
      <div className="flex-1 p-4 overflow-y-auto bg-voka-dark bg-opacity-30">
        {conversation.messages.map(renderMessage)}

        {/* Indicador de escritura */}
        {conversation.isTyping && (
          <div className="flex items-center space-x-1 self-start max-w-[80%] bg-voka-dark text-white rounded-2xl px-4 py-2 mb-4">
            <div className="w-2 h-2 bg-voka-gray rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-voka-gray rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
            <div className="w-2 h-2 bg-voka-gray rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></div>
          </div>
        )}

        {/* Referencia para scroll automático */}
        <div ref={messagesEndRef} />
      </div>

      {/* Área de input */}
      <div className="p-4 border-t border-voka-border">
        {/* Área de grabación si está activa */}
        {isRecording ? (
          <div className="flex items-center justify-between bg-voka-dark rounded-full px-4 py-2">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-voka-red rounded-full animate-pulse mr-2"></div>
              <span className="text-voka-white">Grabando... {recordingTime}s</span>
            </div>
            <button
              onClick={stopVoiceRecording}
              className="bg-voka-red text-white rounded-full p-2 hover:bg-opacity-80 transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>
        ) : (
          <div className="flex items-center space-x-2">
            {/* Input de texto */}
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && sendTextMessage()}
              placeholder="Escribe un mensaje..."
              className="flex-1 bg-voka-dark text-voka-white rounded-full px-4 py-2 focus:outline-none focus:ring-2 focus:ring-voka-magenta"
            />

            {/* Botones de acción */}
            <div className="flex space-x-2">
              <button
                onClick={startVoiceRecording}
                className="bg-voka-dark text-voka-white rounded-full p-2 hover:bg-voka-blue transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path
                    fillRule="evenodd"
                    d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>

              <button
                onClick={simulateOCR}
                className="bg-voka-dark text-voka-white rounded-full p-2 hover:bg-voka-blue transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path
                    fillRule="evenodd"
                    d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>

              <button
                onClick={sendTextMessage}
                disabled={!inputMessage.trim()}
                className={`rounded-full p-2 ${
                  inputMessage.trim()
                    ? "bg-voka-magenta text-white hover:bg-opacity-80"
                    : "bg-voka-dark text-voka-gray cursor-not-allowed"
                } transition-colors`}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* Barra de idiomas y herramientas */}
        <div className="flex justify-between mt-3">
          <div className="flex space-x-2">
            <button className="bg-voka-dark text-voka-white text-xs px-3 py-1 rounded-full hover:bg-voka-blue transition-colors">
              ES⚡EN
            </button>
            <button className="bg-voka-dark text-voka-white text-xs px-3 py-1 rounded-full hover:bg-voka-blue transition-colors">
              EN⚡ES
            </button>
            <button className="bg-voka-dark text-voka-white text-xs px-3 py-1 rounded-full hover:bg-voka-blue transition-colors">
              FR⚡ES
            </button>
          </div>
          <div className="text-xs text-voka-gray">VokaFlow Translation Engine v1.0</div>
        </div>
      </div>
    </div>
  )
}

"use client"

import { useState, useRef, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Brain, User, Send } from "lucide-react"
import { vickyService } from "@/services/vicky-service"
import type { VickyMessage, VickyProcessRequest } from "@/types/vicky"
import { useToast } from "@/hooks/use-toast"

export function VickyChat() {
  const [messages, setMessages] = useState<VickyMessage[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const { toast } = useToast()

  useEffect(() => {
    // Scroll to bottom when messages change
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  const handleSendMessage = async () => {
    if (!input.trim()) return

    const userMessage = input
    setInput("")

    // Add user message to chat
    const tempUserMessage: VickyMessage = {
      id: `user-${Date.now()}`,
      message: userMessage,
      response: "",
      timestamp: new Date().toISOString(),
      processingTime: 0,
      confidence: 0,
      type: "user",
    }

    setMessages((prev) => [...prev, tempUserMessage])

    // Show loading state
    setLoading(true)

    try {
      // Process with Vicky AI
      const request: VickyProcessRequest = {
        message: userMessage,
        userId: "current-user", // This would be the actual user ID in production
      }

      const response = await vickyService.processMessage(request)

      // Add Vicky response to chat
      const vickyMessage: VickyMessage = {
        id: response.messageId,
        message: userMessage,
        response: response.response,
        timestamp: new Date().toISOString(),
        processingTime: response.processingTime,
        confidence: response.confidence,
        type: response.type,
      }

      setMessages((prev) => [...prev, vickyMessage])
    } catch (error) {
      console.error("Error processing message with Vicky:", error)
      toast({
        title: "Error",
        description: "No se pudo procesar el mensaje con Vicky AI",
        variant: "destructive",
      })

      // Add error message
      const errorMessage: VickyMessage = {
        id: `error-${Date.now()}`,
        message: userMessage,
        response: "Lo siento, no puedo procesar tu mensaje en este momento. Por favor, inténtalo de nuevo más tarde.",
        timestamp: new Date().toISOString(),
        processingTime: 0,
        confidence: 0,
        type: "error",
      }

      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="bg-voka-blue-black border-voka-border h-full flex flex-col">
      <CardHeader>
        <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
          <Brain className="h-5 w-5 text-voka-magenta" />
          Chat with Vicky AI
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col">
        <ScrollArea className="flex-1 pr-4 mb-4" ref={scrollAreaRef}>
          <div className="space-y-4">
            {messages.length === 0 ? (
              <div className="text-center py-8">
                <Brain className="h-12 w-12 text-voka-magenta/30 mx-auto mb-2" />
                <p className="text-voka-gray">Inicia una conversación con Vicky AI</p>
              </div>
            ) : (
              messages.map((msg) => (
                <div key={msg.id} className="flex flex-col gap-3">
                  {/* User message */}
                  <div className="flex items-start gap-3 max-w-[80%] ml-auto">
                    <div className="bg-voka-blue/20 p-3 rounded-lg">
                      <p className="text-voka-white">{msg.message}</p>
                    </div>
                    <Avatar className="h-8 w-8">
                      <AvatarFallback className="bg-voka-blue text-voka-white">
                        <User className="h-4 w-4" />
                      </AvatarFallback>
                    </Avatar>
                  </div>

                  {/* Vicky response */}
                  {msg.response && (
                    <div className="flex items-start gap-3 max-w-[80%]">
                      <Avatar className="h-8 w-8">
                        <AvatarImage src="/placeholder.svg?height=32&width=32" />
                        <AvatarFallback className="bg-voka-magenta text-voka-white">
                          <Brain className="h-4 w-4" />
                        </AvatarFallback>
                      </Avatar>
                      <div className="bg-voka-magenta/20 p-3 rounded-lg">
                        <p className="text-voka-white">{msg.response}</p>
                        {msg.confidence > 0 && (
                          <p className="text-xs text-voka-gray mt-1">
                            Confidence: {msg.confidence}% • {msg.processingTime.toFixed(2)}s
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
            {loading && (
              <div className="flex items-start gap-3 max-w-[80%]">
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="bg-voka-magenta text-voka-white">
                    <Brain className="h-4 w-4" />
                  </AvatarFallback>
                </Avatar>
                <div className="bg-voka-magenta/20 p-3 rounded-lg">
                  <div className="flex space-x-2">
                    <div
                      className="w-2 h-2 rounded-full bg-voka-magenta/50 animate-bounce"
                      style={{ animationDelay: "0ms" }}
                    ></div>
                    <div
                      className="w-2 h-2 rounded-full bg-voka-magenta/50 animate-bounce"
                      style={{ animationDelay: "150ms" }}
                    ></div>
                    <div
                      className="w-2 h-2 rounded-full bg-voka-magenta/50 animate-bounce"
                      style={{ animationDelay: "300ms" }}
                    ></div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        <div className="flex gap-2 mt-auto">
          <Input
            placeholder="Type your message..."
            className="bg-voka-dark border-voka-border text-voka-white placeholder:text-voka-gray"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault()
                handleSendMessage()
              }
            }}
            disabled={loading}
          />
          <Button
            className="bg-voka-magenta hover:bg-voka-magenta/80 text-white"
            onClick={handleSendMessage}
            disabled={loading || !input.trim()}
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

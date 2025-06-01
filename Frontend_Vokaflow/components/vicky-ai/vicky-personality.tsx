"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Scale, Wrench, Palette, BarChart, Heart } from "lucide-react"

const personalities = [
  {
    id: "balanced",
    name: "⚖️ BALANCED",
    description: "Default AI Assistant",
    icon: Scale,
    color: "voka-gray",
    active: true,
  },
  {
    id: "technical",
    name: "🔧 TECHNICAL",
    description: "Logic Focus & Analysis",
    icon: Wrench,
    color: "voka-blue",
    active: false,
  },
  {
    id: "creative",
    name: "🎨 CREATIVE",
    description: "Innovation & Ideas",
    icon: Palette,
    color: "voka-magenta",
    active: false,
  },
  {
    id: "analytical",
    name: "📊 ANALYTICAL",
    description: "Data Driven Decisions",
    icon: BarChart,
    color: "voka-yellow",
    active: false,
  },
  {
    id: "empathetic",
    name: "💝 EMPATHETIC",
    description: "Human Focus & Support",
    icon: Heart,
    color: "voka-green",
    active: false,
  },
]

export function VickyPersonality() {
  const [selectedPersonality, setSelectedPersonality] = useState("balanced")
  const [temperature, setTemperature] = useState([0.7])
  const [maxTokens, setMaxTokens] = useState("2048")
  const [contextWindow, setContextWindow] = useState("4096")

  return (
    <div className="space-y-6">
      {/* Personality Selector */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {personalities.map((personality) => (
          <Card
            key={personality.id}
            className={`cursor-pointer transition-all duration-200 ${
              selectedPersonality === personality.id
                ? "bg-voka-magenta/20 border-voka-magenta shadow-lg shadow-voka-magenta/25"
                : "bg-voka-blue-black border-voka-border hover:border-voka-magenta/50"
            }`}
            onClick={() => setSelectedPersonality(personality.id)}
          >
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-montserrat text-voka-white flex items-center gap-2">
                <personality.icon className={`h-5 w-5 text-${personality.color}`} />
                {personality.name}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-voka-gray font-montserrat text-sm">{personality.description}</p>
              {selectedPersonality === personality.id && (
                <Badge className="mt-2 bg-voka-magenta/20 text-voka-magenta border-voka-magenta font-montserrat">
                  ACTIVE
                </Badge>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Advanced Configuration */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader>
          <CardTitle className="text-voka-white font-montserrat">Advanced Configuration</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Temperature */}
            <div className="space-y-3">
              <Label className="text-voka-gray font-montserrat">Temperature: {temperature[0]}</Label>
              <Slider
                value={temperature}
                onValueChange={setTemperature}
                max={2}
                min={0.1}
                step={0.1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-voka-gray font-montserrat">
                <span>Conservative</span>
                <span>Creative</span>
              </div>
            </div>

            {/* Language Preference */}
            <div className="space-y-3">
              <Label className="text-voka-gray font-montserrat">Language Preference</Label>
              <Select defaultValue="auto">
                <SelectTrigger className="bg-voka-dark border-voka-border text-voka-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-voka-blue-black border-voka-border">
                  <SelectItem value="auto">Auto-detect</SelectItem>
                  <SelectItem value="es">Español</SelectItem>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="fr">Français</SelectItem>
                  <SelectItem value="de">Deutsch</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Max Tokens */}
            <div className="space-y-3">
              <Label className="text-voka-gray font-montserrat">Max Tokens</Label>
              <Input
                value={maxTokens}
                onChange={(e) => setMaxTokens(e.target.value)}
                className="bg-voka-dark border-voka-border text-voka-white"
                placeholder="2048"
              />
            </div>

            {/* Context Window */}
            <div className="space-y-3">
              <Label className="text-voka-gray font-montserrat">Context Window Size</Label>
              <Input
                value={contextWindow}
                onChange={(e) => setContextWindow(e.target.value)}
                className="bg-voka-dark border-voka-border text-voka-white"
                placeholder="4096"
              />
            </div>
          </div>

          {/* Response Style */}
          <div className="space-y-3">
            <Label className="text-voka-gray font-montserrat">Response Style</Label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {["Concise", "Detailed", "Conversational", "Professional"].map((style) => (
                <Button
                  key={style}
                  variant="outline"
                  size="sm"
                  className="border-voka-border text-voka-gray hover:text-voka-white hover:border-voka-magenta font-montserrat"
                >
                  {style}
                </Button>
              ))}
            </div>
          </div>

          {/* Apply Changes */}
          <div className="flex gap-4 pt-4">
            <Button className="bg-voka-magenta hover:bg-voka-magenta/80 text-white font-montserrat">
              Apply Configuration
            </Button>
            <Button
              variant="outline"
              className="border-voka-border text-voka-gray hover:text-voka-white font-montserrat"
            >
              Reset to Defaults
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Personality Preview */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader>
          <CardTitle className="text-voka-white font-montserrat">Personality Preview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-voka-dark rounded-lg p-4 border border-voka-border">
            <div className="text-voka-gray font-montserrat text-sm mb-2">Sample Response:</div>
            <div className="text-voka-white font-montserrat">
              {selectedPersonality === "balanced" &&
                "Hello! I'm here to help you with any questions or tasks. I aim to provide balanced, helpful responses that consider both technical accuracy and human understanding."}
              {selectedPersonality === "technical" &&
                "Greetings. I'm operating in technical mode, optimized for precise, data-driven analysis and logical problem-solving. How may I assist with your technical requirements?"}
              {selectedPersonality === "creative" &&
                "Hi there! ✨ I'm feeling creative today! I love exploring innovative ideas and thinking outside the box. What exciting project can we brainstorm together?"}
              {selectedPersonality === "analytical" &&
                "Hello. I'm configured for analytical processing, focusing on data interpretation, statistical analysis, and evidence-based conclusions. What data shall we examine?"}
              {selectedPersonality === "empathetic" &&
                "Hello, friend! 💙 I'm here to listen and support you. I understand that behind every question is a person with feelings and needs. How can I help you today?"}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

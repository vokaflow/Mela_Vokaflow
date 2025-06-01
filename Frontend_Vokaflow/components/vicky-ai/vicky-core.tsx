"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Brain, Heart, Code } from "lucide-react"
import { vickyService } from "@/services/vicky-service"
import type { VickyPersonalitySettings } from "@/types/vicky"
import { useToast } from "@/hooks/use-toast"

export function VickyCore() {
  const [technicalBalance, setTechnicalBalance] = useState([67])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const { toast } = useToast()
  const emotionalBalance = 100 - technicalBalance[0]

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const data = await vickyService.getStatus()
        setTechnicalBalance([data.technicalBalance])
      } catch (error) {
        console.error("Error fetching Vicky status:", error)
      }
    }

    fetchStatus()
  }, [])

  const handleApplyChanges = async () => {
    setSaving(true)
    try {
      const settings: VickyPersonalitySettings = {
        technicalBalance: technicalBalance[0],
        emotionalBalance: emotionalBalance,
        creativityLevel: 50, // Default values
        formalityLevel: 50,
        verbosityLevel: 50,
        empathyLevel: emotionalBalance,
      }

      const success = await vickyService.updatePersonality(settings)

      if (success) {
        toast({
          title: "Cambios aplicados",
          description: "La configuración de Vicky AI ha sido actualizada",
        })
      } else {
        throw new Error("No se pudo actualizar la configuración")
      }
    } catch (error) {
      console.error("Error updating Vicky personality:", error)
      toast({
        title: "Error",
        description: "No se pudo actualizar la configuración de Vicky AI",
        variant: "destructive",
      })
    } finally {
      setSaving(false)
    }
  }

  const handleReset = async () => {
    setTechnicalBalance([67])
  }

  return (
    <div className="space-y-6">
      {/* Brain Visualization */}
      <div className="flex justify-center mb-8">
        <div className="relative w-96 h-64">
          <div className="absolute inset-0 flex">
            {/* Left Hemisphere - Technical */}
            <div className="w-1/2 h-full bg-gradient-to-r from-voka-blue/30 to-voka-blue/10 rounded-l-full border-2 border-voka-blue/50 flex items-center justify-center relative overflow-hidden">
              <div className="absolute inset-0 grid grid-cols-4 grid-rows-6 gap-1 p-4">
                {Array.from({ length: 24 }).map((_, i) => (
                  <div
                    key={i}
                    className="w-1 h-1 bg-voka-blue rounded-full animate-pulse"
                    style={{
                      animationDelay: `${i * 0.1}s`,
                      opacity: technicalBalance[0] / 100,
                    }}
                  />
                ))}
              </div>
              <Code className="w-16 h-16 text-voka-blue z-10" />
              <div className="absolute bottom-2 left-2 text-xs text-voka-blue font-montserrat font-semibold">
                TECHNICAL
              </div>
            </div>

            {/* Right Hemisphere - Emotional */}
            <div className="w-1/2 h-full bg-gradient-to-l from-voka-magenta/30 to-voka-magenta/10 rounded-r-full border-2 border-voka-magenta/50 flex items-center justify-center relative overflow-hidden">
              <div className="absolute inset-0 grid grid-cols-4 grid-rows-6 gap-1 p-4">
                {Array.from({ length: 24 }).map((_, i) => (
                  <div
                    key={i}
                    className="w-1 h-1 bg-voka-magenta rounded-full animate-pulse"
                    style={{
                      animationDelay: `${i * 0.1}s`,
                      opacity: emotionalBalance / 100,
                    }}
                  />
                ))}
              </div>
              <Heart className="w-16 h-16 text-voka-magenta z-10" />
              <div className="absolute bottom-2 right-2 text-xs text-voka-magenta font-montserrat font-semibold">
                EMOTIONAL
              </div>
            </div>
          </div>

          {/* Connecting Neurons */}
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
            <div className="w-8 h-1 bg-gradient-to-r from-voka-blue to-voka-magenta animate-pulse" />
            <div className="w-1 h-8 bg-gradient-to-b from-voka-blue to-voka-magenta animate-pulse absolute top-0 left-1/2 transform -translate-x-1/2" />
          </div>
        </div>
      </div>

      {/* Balance Controls */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader>
          <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
            <Brain className="h-5 w-5 text-voka-magenta" />
            Balance Control
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-voka-blue font-montserrat">Technical</span>
              <span className="text-voka-magenta font-montserrat">Emotional</span>
            </div>
            <Slider
              value={technicalBalance}
              onValueChange={setTechnicalBalance}
              max={100}
              step={1}
              className="w-full"
            />
            <div className="flex justify-between text-sm">
              <Badge className="bg-voka-blue/20 text-voka-blue border-voka-blue font-montserrat">
                {technicalBalance[0]}%
              </Badge>
              <Badge className="bg-voka-magenta/20 text-voka-magenta border-voka-magenta font-montserrat">
                {emotionalBalance}%
              </Badge>
            </div>
          </div>

          <div className="flex gap-4">
            <Button
              className="bg-voka-magenta hover:bg-voka-magenta/80 text-white font-montserrat"
              onClick={handleApplyChanges}
              disabled={saving}
            >
              {saving ? "Aplicando..." : "Apply Changes"}
            </Button>
            <Button
              variant="outline"
              className="border-voka-border text-voka-gray hover:text-voka-white font-montserrat"
              onClick={handleReset}
              disabled={saving}
            >
              Reset to Default
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Hemisphere Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-voka-blue-black border-voka-border">
          <CardHeader>
            <CardTitle className="text-voka-blue font-montserrat flex items-center gap-2">
              <Code className="h-5 w-5" />
              LEFT BRAIN (TECHNICAL)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-voka-gray font-montserrat">Logic Processing</span>
                <span className="text-voka-white font-montserrat">{Math.round((89 * technicalBalance[0]) / 100)}%</span>
              </div>
              <Progress value={Math.round((89 * technicalBalance[0]) / 100)} className="h-2" />
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-voka-gray font-montserrat">Data Analysis</span>
                <span className="text-voka-white font-montserrat">{Math.round((94 * technicalBalance[0]) / 100)}%</span>
              </div>
              <Progress value={Math.round((94 * technicalBalance[0]) / 100)} className="h-2" />
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-voka-gray font-montserrat">Code Generation</span>
                <span className="text-voka-white font-montserrat">{Math.round((91 * technicalBalance[0]) / 100)}%</span>
              </div>
              <Progress value={Math.round((91 * technicalBalance[0]) / 100)} className="h-2" />
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-voka-gray font-montserrat">Problem Solving</span>
                <span className="text-voka-white font-montserrat">{Math.round((87 * technicalBalance[0]) / 100)}%</span>
              </div>
              <Progress value={Math.round((87 * technicalBalance[0]) / 100)} className="h-2" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border">
          <CardHeader>
            <CardTitle className="text-voka-magenta font-montserrat flex items-center gap-2">
              <Heart className="h-5 w-5" />
              RIGHT BRAIN (EMOTIONAL)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-voka-gray font-montserrat">Empathy Level</span>
                <span className="text-voka-white font-montserrat">{Math.round((76 * emotionalBalance) / 100)}%</span>
              </div>
              <Progress value={Math.round((76 * emotionalBalance) / 100)} className="h-2" />
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-voka-gray font-montserrat">Creativity Index</span>
                <span className="text-voka-white font-montserrat">{Math.round((82 * emotionalBalance) / 100)}%</span>
              </div>
              <Progress value={Math.round((82 * emotionalBalance) / 100)} className="h-2" />
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-voka-gray font-montserrat">Social Intelligence</span>
                <span className="text-voka-white font-montserrat">{Math.round((88 * emotionalBalance) / 100)}%</span>
              </div>
              <Progress value={Math.round((88 * emotionalBalance) / 100)} className="h-2" />
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-voka-gray font-montserrat">Emotional Recognition</span>
                <span className="text-voka-white font-montserrat">{Math.round((79 * emotionalBalance) / 100)}%</span>
              </div>
              <Progress value={Math.round((79 * emotionalBalance) / 100)} className="h-2" />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

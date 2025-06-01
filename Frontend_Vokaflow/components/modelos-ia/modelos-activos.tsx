"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { PauseCircle, RefreshCw, Settings, BarChart3, FlaskConical, Brain, Mic, Volume2, Globe } from "lucide-react"
import type { AIModel, GPUMetrics, ModelActivity } from "@/types/ai-models"
import { getModelStatus, getGPUMetrics, getModelActivity } from "@/services/ai-models-service"

export function ModelosActivos() {
  const [models, setModels] = useState<AIModel[]>([])
  const [gpuMetrics, setGpuMetrics] = useState<GPUMetrics | null>(null)
  const [activity, setActivity] = useState<ModelActivity[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(true)

  // Cargar datos iniciales
  useEffect(() => {
    loadData()

    // Configurar auto-refresh cada 30 segundos
    let interval: NodeJS.Timeout | null = null
    if (autoRefresh) {
      interval = setInterval(() => {
        loadData(false)
      }, 30000)
    }

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [autoRefresh])

  // Función para cargar todos los datos
  const loadData = async (showLoading = true) => {
    if (showLoading) setLoading(true)
    try {
      const [modelsData, gpuData, activityData] = await Promise.all([
        getModelStatus(),
        getGPUMetrics(),
        getModelActivity(),
      ])
      setModels(modelsData)
      setGpuMetrics(gpuData)
      setActivity(activityData)
      setError(null)
    } catch (err) {
      setError("Error al cargar datos de modelos: " + (err as Error).message)
      console.error("Error cargando datos:", err)
    } finally {
      if (showLoading) setLoading(false)
    }
  }

  // Obtener modelos cargados y no cargados
  const loadedModels = models.filter((m) => m.status === "loaded")
  const unloadedModels = models.filter((m) => m.status === "unloaded")

  // Función para obtener el ícono según el tipo de modelo
  const getModelIcon = (type: string) => {
    switch (type) {
      case "LLM":
        return <Brain className="h-5 w-5 text-pink-500" />
      case "STT":
        return <Mic className="h-5 w-5 text-blue-500" />
      case "TTS":
        return <Volume2 className="h-5 w-5 text-green-500" />
      case "TRANSLATION":
        return <Globe className="h-5 w-5 text-amber-500" />
      default:
        return <Brain className="h-5 w-5 text-gray-500" />
    }
  }

  // Formatear tiempo relativo
  const formatRelativeTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)

    if (diffSeconds < 60) return `${diffSeconds}s`
    if (diffSeconds < 3600) return `${Math.floor(diffSeconds / 60)}m`
    if (diffSeconds < 86400) return `${Math.floor(diffSeconds / 3600)}h`
    return `${Math.floor(diffSeconds / 86400)}d`
  }

  return (
    <div className="space-y-6">
      {/* Estadísticas generales */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader className="pb-2">
          <div className="flex justify-between items-center">
            <CardTitle className="text-xl text-voka-white">🎯 Modelos IA Activos</CardTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={() => loadData()}
              className="bg-voka-blue-black border-voka-border text-voka-white hover:bg-voka-blue-black/80"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
              {autoRefresh ? "Auto-refresh ON" : "Refrescar"}
            </Button>
          </div>
          <CardDescription className="text-voka-gray">Estado actual y métricas de los modelos de IA</CardDescription>
        </CardHeader>
        <CardContent>
          {error ? (
            <div className="bg-red-900/20 border border-red-700 rounded-md p-3 text-red-300">{error}</div>
          ) : (
            <>
              {/* Métricas generales */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <Card className="bg-voka-blue-black/50 border-voka-border">
                  <CardContent className="p-4">
                    <div className="text-voka-neon-pink text-sm font-medium">🟢 CARGADOS</div>
                    <div className="text-3xl font-bold text-voka-white mt-1">{loadedModels.length}</div>
                    <div className="text-xs text-voka-gray mt-1">Modelos</div>
                  </CardContent>
                </Card>

                <Card className="bg-voka-blue-black/50 border-voka-border">
                  <CardContent className="p-4">
                    <div className="text-voka-neon-pink text-sm font-medium">🎮 MEMORIA GPU</div>
                    <div className="text-3xl font-bold text-voka-white mt-1">
                      {gpuMetrics ? `${gpuMetrics.memory_used_gb}/${gpuMetrics.memory_total_gb}GB` : "..."}
                    </div>
                    <div className="text-xs text-voka-gray mt-1">
                      {gpuMetrics ? `${gpuMetrics.utilization_percentage}%` : "..."}
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-voka-blue-black/50 border-voka-border">
                  <CardContent className="p-4">
                    <div className="text-voka-neon-pink text-sm font-medium">💾 MEM SISTEMA</div>
                    <div className="text-3xl font-bold text-voka-white mt-1">{gpuMetrics ? "12.3/32GB" : "..."}</div>
                    <div className="text-xs text-voka-gray mt-1">38%</div>
                  </CardContent>
                </Card>

                <Card className="bg-voka-blue-black/50 border-voka-border">
                  <CardContent className="p-4">
                    <div className="text-voka-neon-pink text-sm font-medium">⚡ INFERENCIA</div>
                    <div className="text-3xl font-bold text-voka-white mt-1">245 tok/s</div>
                    <div className="text-xs text-voka-gray mt-1">velocidad media</div>
                  </CardContent>
                </Card>
              </div>

              {/* Lista de modelos activos */}
              <div className="space-y-4">
                {loadedModels.map((model) => (
                  <Card key={model.id} className="bg-voka-blue-black/30 border-voka-border overflow-hidden">
                    <div className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {getModelIcon(model.type)}
                          <h3 className="text-lg font-semibold text-voka-white">{model.name}</h3>
                          <Badge
                            variant="outline"
                            className="ml-2 bg-voka-blue-black/50 text-voka-gray border-voka-border"
                          >
                            {model.type}
                          </Badge>
                          <Badge className="bg-emerald-500/20 text-emerald-300 border-emerald-800">🟢 ACTIVO</Badge>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-voka-gray">
                          <span>{model.gpu_memory_mb / 1000}GB</span>
                          <span>|</span>
                          <span>{model.usage_percentage}%</span>
                          <span>|</span>
                          <span>{model.requests_count} peticiones</span>
                          <span>|</span>
                          <span>{model.uptime_hours}h</span>
                        </div>
                      </div>

                      <div className="mt-2 text-sm text-voka-gray">{model.description}</div>

                      <div className="mt-1 text-xs text-voka-gray/70">Ubicación: {model.location}</div>

                      <div className="mt-3 flex flex-wrap gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          className="bg-voka-blue-black/50 border-voka-border text-voka-gray hover:bg-voka-blue-black"
                        >
                          <PauseCircle className="h-4 w-4 mr-1" /> PAUSAR
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="bg-voka-blue-black/50 border-voka-border text-voka-gray hover:bg-voka-blue-black"
                        >
                          <RefreshCw className="h-4 w-4 mr-1" /> REINICIAR
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="bg-voka-blue-black/50 border-voka-border text-voka-gray hover:bg-voka-blue-black"
                        >
                          <Settings className="h-4 w-4 mr-1" /> CONFIG
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="bg-voka-blue-black/50 border-voka-border text-voka-gray hover:bg-voka-blue-black"
                        >
                          <BarChart3 className="h-4 w-4 mr-1" /> MÉTRICAS
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="bg-voka-blue-black/50 border-voka-border text-voka-gray hover:bg-voka-blue-black"
                        >
                          <FlaskConical className="h-4 w-4 mr-1" /> TEST
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>

              {/* Modelos disponibles (no cargados) */}
              <div className="mt-6">
                <h3 className="text-lg font-medium text-voka-white mb-3">💤 MODELOS DISPONIBLES (No Cargados)</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {unloadedModels.slice(0, 4).map((model) => (
                    <div key={model.id} className="bg-voka-blue-black/20 border border-voka-border rounded-md p-3">
                      <div className="flex items-center gap-2">
                        {getModelIcon(model.type)}
                        <span className="text-voka-white">{model.name}</span>
                        <span className="text-voka-gray text-xs">({model.size_gb}GB)</span>
                      </div>
                      <div className="text-xs text-voka-gray mt-1">{model.description}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Actividad en tiempo real */}
              <div className="mt-6">
                <h3 className="text-lg font-medium text-voka-white mb-3">🔥 ACTIVIDAD EN TIEMPO REAL</h3>
                <Card className="bg-voka-blue-black/30 border-voka-border">
                  <CardContent className="p-4 space-y-2">
                    {activity.map((item, index) => (
                      <div key={index} className="flex items-center text-sm">
                        <span className="text-voka-gray mr-2">[{formatRelativeTime(item.timestamp)}]</span>
                        {getModelIcon(
                          item.model_id.includes("qwen")
                            ? "LLM"
                            : item.model_id.includes("whisper")
                              ? "STT"
                              : item.model_id.includes("xtts")
                                ? "TTS"
                                : "TRANSLATION",
                        )}
                        <span className="text-voka-white ml-2">
                          {item.model_id.split("-")[0].charAt(0).toUpperCase() + item.model_id.split("-")[0].slice(1)} →
                        </span>
                        <span className="text-voka-gray ml-2">{item.details}</span>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

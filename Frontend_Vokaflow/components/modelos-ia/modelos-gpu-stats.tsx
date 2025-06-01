"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { RefreshCw } from "lucide-react"
import type { GPUMetrics, SystemMetrics, AIModel } from "@/types/ai-models"
import { getGPUMetrics, getSystemMetrics, getModelStatus } from "@/services/ai-models-service"

export function ModelosGPUStats() {
  const [gpuMetrics, setGpuMetrics] = useState<GPUMetrics | null>(null)
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null)
  const [models, setModels] = useState<AIModel[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(true)

  // Cargar datos iniciales
  useEffect(() => {
    loadData()

    // Configurar auto-refresh cada 5 segundos
    let interval: NodeJS.Timeout | null = null
    if (autoRefresh) {
      interval = setInterval(() => {
        loadData(false)
      }, 5000)
    }

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [autoRefresh])

  // Función para cargar todos los datos
  const loadData = async (showLoading = true) => {
    if (showLoading) setLoading(true)
    try {
      const [gpuData, systemData, modelsData] = await Promise.all([
        getGPUMetrics(),
        getSystemMetrics(),
        getModelStatus(),
      ])
      setGpuMetrics(gpuData)
      setSystemMetrics(systemData)
      setModels(modelsData)
      setError(null)
    } catch (err) {
      setError("Error al cargar datos de métricas: " + (err as Error).message)
      console.error("Error cargando datos:", err)
    } finally {
      if (showLoading) setLoading(false)
    }
  }

  // Generar datos de utilización para el gráfico
  const generateUtilizationData = () => {
    // En un caso real, esto vendría de la API
    return Array.from({ length: 24 }, (_, i) => {
      const hour = i
      // Generar datos simulados con un patrón realista
      const baseValue = 40 + Math.sin(i / 3) * 20
      const randomVariation = Math.random() * 20
      const value = Math.min(100, Math.max(0, baseValue + randomVariation))

      return {
        hour,
        value: Math.round(value),
      }
    })
  }

  // Datos de utilización para el gráfico
  const utilizationData = generateUtilizationData()

  // Modelos cargados
  const loadedModels = models.filter((m) => m.status === "loaded")

  return (
    <div className="space-y-6">
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader className="pb-2">
          <div className="flex justify-between items-center">
            <CardTitle className="text-xl text-voka-white">🎮 Análisis de Rendimiento GPU</CardTitle>
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
          <CardDescription className="text-voka-gray">
            Monitoreo en tiempo real del rendimiento de GPU y recursos del sistema
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error ? (
            <div className="bg-red-900/20 border border-red-700 rounded-md p-3 text-red-300">{error}</div>
          ) : (
            <>
              {/* Estado de GPU en tiempo real */}
              <div className="mb-6">
                <h3 className="text-lg font-medium text-voka-white mb-3">ESTADO DE GPU EN TIEMPO REAL</h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <Card className="bg-voka-blue-black/50 border-voka-border">
                    <CardContent className="p-4">
                      <div className="text-voka-neon-pink text-sm font-medium">🎮 UTILIZACIÓN GPU</div>
                      <div className="text-3xl font-bold text-voka-white mt-1">
                        {gpuMetrics ? `${gpuMetrics.utilization_percentage}%` : "..."}
                      </div>
                      <Progress
                        value={gpuMetrics?.utilization_percentage || 0}
                        className="h-2 mt-2 bg-voka-blue-black/50"
                        indicatorClassName={`${
                          (gpuMetrics?.utilization_percentage || 0) > 90
                            ? "bg-red-500"
                            : (gpuMetrics?.utilization_percentage || 0) > 70
                              ? "bg-amber-500"
                              : "bg-emerald-500"
                        }`}
                      />
                    </CardContent>
                  </Card>

                  <Card className="bg-voka-blue-black/50 border-voka-border">
                    <CardContent className="p-4">
                      <div className="text-voka-neon-pink text-sm font-medium">💾 VRAM</div>
                      <div className="text-3xl font-bold text-voka-white mt-1">
                        {gpuMetrics ? `${gpuMetrics.memory_used_gb}/${gpuMetrics.memory_total_gb}GB` : "..."}
                      </div>
                      <Progress
                        value={gpuMetrics ? (gpuMetrics.memory_used_gb / gpuMetrics.memory_total_gb) * 100 : 0}
                        className="h-2 mt-2 bg-voka-blue-black/50"
                        indicatorClassName={`${
                          gpuMetrics && gpuMetrics.memory_used_gb / gpuMetrics.memory_total_gb > 0.9
                            ? "bg-red-500"
                            : gpuMetrics && gpuMetrics.memory_used_gb / gpuMetrics.memory_total_gb > 0.7
                              ? "bg-amber-500"
                              : "bg-emerald-500"
                        }`}
                      />
                    </CardContent>
                  </Card>

                  <Card className="bg-voka-blue-black/50 border-voka-border">
                    <CardContent className="p-4">
                      <div className="text-voka-neon-pink text-sm font-medium">🌡️ TEMPERATURA</div>
                      <div className="text-3xl font-bold text-voka-white mt-1">
                        {gpuMetrics ? `${gpuMetrics.temperature_celsius}°C` : "..."}
                      </div>
                      <Progress
                        value={gpuMetrics ? (gpuMetrics.temperature_celsius / 100) * 100 : 0}
                        className="h-2 mt-2 bg-voka-blue-black/50"
                        indicatorClassName={`${
                          gpuMetrics && gpuMetrics.temperature_celsius > 85
                            ? "bg-red-500"
                            : gpuMetrics && gpuMetrics.temperature_celsius > 75
                              ? "bg-amber-500"
                              : "bg-emerald-500"
                        }`}
                      />
                    </CardContent>
                  </Card>

                  <Card className="bg-voka-blue-black/50 border-voka-border">
                    <CardContent className="p-4">
                      <div className="text-voka-neon-pink text-sm font-medium">⚡ POTENCIA</div>
                      <div className="text-3xl font-bold text-voka-white mt-1">
                        {gpuMetrics ? `${gpuMetrics.power_watts}W` : "..."}
                      </div>
                      <Progress
                        value={gpuMetrics ? (gpuMetrics.power_watts / 300) * 100 : 0}
                        className="h-2 mt-2 bg-voka-blue-black/50"
                        indicatorClassName="bg-blue-500"
                      />
                    </CardContent>
                  </Card>
                </div>
              </div>

              {/* Gráfico de utilización de GPU */}
              <div className="mb-6">
                <h3 className="text-lg font-medium text-voka-white mb-3">
                  📊 UTILIZACIÓN DE GPU POR MODELO (Últimas 24 Horas)
                </h3>
                <Card className="bg-voka-blue-black/30 border-voka-border">
                  <CardContent className="p-4">
                    <div className="h-64 w-full">
                      <div className="flex h-full">
                        {/* Eje Y */}
                        <div className="flex flex-col justify-between pr-2 text-xs text-voka-gray">
                          <div>100</div>
                          <div>80</div>
                          <div>60</div>
                          <div>40</div>
                          <div>20</div>
                          <div>0</div>
                        </div>

                        {/* Gráfico */}
                        <div className="flex-1">
                          <div className="relative h-full">
                            {/* Líneas horizontales de fondo */}
                            <div className="absolute inset-0 flex flex-col justify-between">
                              {[0, 20, 40, 60, 80, 100].map((value) => (
                                <div key={value} className="border-t border-voka-border/30 w-full h-0" />
                              ))}
                            </div>

                            {/* Barras del gráfico */}
                            <div className="absolute inset-0 flex items-end">
                              <div className="w-full flex items-end justify-between">
                                {utilizationData.map((data, index) => (
                                  <div key={index} className="flex-1 flex flex-col items-center">
                                    <div
                                      className="w-full bg-voka-neon-pink/70 rounded-sm mx-px"
                                      style={{ height: `${data.value}%` }}
                                    />
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>

                          {/* Eje X */}
                          <div className="flex justify-between mt-2 text-xs text-voka-gray">
                            {[0, 4, 8, 12, 16, 20, 24].map((hour) => (
                              <div key={hour}>{hour.toString().padStart(2, "0")}</div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Desglose por modelo */}
                    <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                      {loadedModels.map((model) => (
                        <div key={model.id} className="flex justify-between items-center">
                          <div className="flex items-center gap-2">
                            <div
                              className="w-3 h-3 rounded-full"
                              style={{
                                backgroundColor:
                                  model.type === "LLM"
                                    ? "#ec4899"
                                    : model.type === "STT"
                                      ? "#3b82f6"
                                      : model.type === "TTS"
                                        ? "#10b981"
                                        : "#f59e0b",
                              }}
                            />
                            <span className="text-voka-white">{model.name}:</span>
                          </div>
                          <div className="text-voka-gray">
                            {model.usage_percentage}% avg (Pico:{" "}
                            {Math.min(99, model.usage_percentage + Math.floor(Math.random() * 30))}%)
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Mapa de asignación de memoria */}
              <div className="mb-6">
                <h3 className="text-lg font-medium text-voka-white mb-3">💾 MAPA DE ASIGNACIÓN DE VRAM</h3>
                <Card className="bg-voka-blue-black/30 border-voka-border">
                  <CardContent className="p-4">
                    {/* Barra de memoria GPU */}
                    <div className="mb-4">
                      <div className="text-sm text-voka-white mb-1">Memoria GPU:</div>
                      <div className="h-8 w-full bg-voka-blue-black/50 rounded-md overflow-hidden flex">
                        {gpuMetrics && loadedModels.length > 0 ? (
                          <>
                            {loadedModels.map((model, index) => {
                              // Calcular el porcentaje de memoria que usa este modelo
                              const percentage = (model.gpu_memory_mb / 1000 / gpuMetrics.memory_total_gb) * 100

                              // Asignar un color según el tipo de modelo
                              const bgColor =
                                model.type === "LLM"
                                  ? "bg-pink-600"
                                  : model.type === "STT"
                                    ? "bg-blue-600"
                                    : model.type === "TTS"
                                      ? "bg-green-600"
                                      : "bg-amber-600"

                              return (
                                <div
                                  key={model.id}
                                  className={`h-full ${bgColor}`}
                                  style={{ width: `${percentage}%` }}
                                  title={`${model.name}: ${(model.gpu_memory_mb / 1000).toFixed(1)}GB (${percentage.toFixed(1)}%)`}
                                />
                              )
                            })}

                            {/* Memoria del sistema */}
                            <div
                              className="h-full bg-gray-600"
                              style={{ width: `${15}%` }}
                              title={`Sistema: 1.2GB (15%)`}
                            />

                            {/* Memoria libre */}
                            <div
                              className="h-full bg-transparent"
                              style={{
                                width: `${100 - loadedModels.reduce((acc, model) => acc + (model.gpu_memory_mb / 1000 / gpuMetrics.memory_total_gb) * 100, 0) - 15}%`,
                              }}
                              title="Memoria libre"
                            />
                          </>
                        ) : (
                          <div className="h-full w-full bg-gray-600/30 animate-pulse" />
                        )}
                      </div>

                      {/* Leyenda */}
                      <div className="flex flex-wrap gap-x-4 gap-y-2 mt-2 text-xs">
                        {loadedModels.map((model) => (
                          <div key={model.id} className="flex items-center gap-1">
                            <div
                              className="w-3 h-3 rounded-sm"
                              style={{
                                backgroundColor:
                                  model.type === "LLM"
                                    ? "#db2777"
                                    : model.type === "STT"
                                      ? "#2563eb"
                                      : model.type === "TTS"
                                        ? "#059669"
                                        : "#d97706",
                              }}
                            />
                            <span className="text-voka-white">{model.name}</span>
                            <span className="text-voka-gray">
                              {(model.gpu_memory_mb / 1000).toFixed(1)}GB (
                              {Math.round((model.gpu_memory_mb / 1000 / gpuMetrics?.memory_total_gb!) * 100)}%)
                            </span>
                          </div>
                        ))}
                        <div className="flex items-center gap-1">
                          <div className="w-3 h-3 rounded-sm bg-gray-600" />
                          <span className="text-voka-white">Sistema</span>
                          <span className="text-voka-gray">1.2GB (15%)</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <div className="w-3 h-3 rounded-sm border border-voka-border" />
                          <span className="text-voka-white">Libre</span>
                          <span className="text-voka-gray">
                            {gpuMetrics
                              ? `${(gpuMetrics.memory_total_gb - gpuMetrics.memory_used_gb).toFixed(1)}GB (${Math.round((1 - gpuMetrics.memory_used_gb / gpuMetrics.memory_total_gb) * 100)}%)`
                              : "..."}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Memoria del sistema */}
                    <div className="mt-6">
                      <div className="text-sm text-voka-white mb-1">RAM DEL SISTEMA:</div>
                      <div className="h-4 w-full bg-voka-blue-black/50 rounded-md overflow-hidden flex">
                        {systemMetrics ? (
                          <>
                            <div
                              className="h-full bg-blue-600/50"
                              style={{
                                width: `${(systemMetrics.model_buffers_gb / systemMetrics.memory_total_gb) * 100}%`,
                              }}
                              title={`Buffers de modelos: ${systemMetrics.model_buffers_gb}GB (${Math.round((systemMetrics.model_buffers_gb / systemMetrics.memory_total_gb) * 100)}%)`}
                            />
                            <div
                              className="h-full bg-amber-600/50"
                              style={{ width: `${(systemMetrics.cache_gb / systemMetrics.memory_total_gb) * 100}%` }}
                              title={`Caché: ${systemMetrics.cache_gb}GB (${Math.round((systemMetrics.cache_gb / systemMetrics.memory_total_gb) * 100)}%)`}
                            />
                            <div
                              className="h-full bg-gray-600/50"
                              style={{ width: `${(systemMetrics.system_gb / systemMetrics.memory_total_gb) * 100}%` }}
                              title={`Sistema: ${systemMetrics.system_gb}GB (${Math.round((systemMetrics.system_gb / systemMetrics.memory_total_gb) * 100)}%)`}
                            />
                          </>
                        ) : (
                          <div className="h-full w-full bg-gray-600/30 animate-pulse" />
                        )}
                      </div>

                      {/* Leyenda */}
                      <div className="flex flex-wrap gap-x-4 gap-y-2 mt-2 text-xs">
                        <div className="flex items-center gap-1">
                          <div className="w-3 h-3 rounded-sm bg-blue-600/50" />
                          <span className="text-voka-white">Buffers de Modelos:</span>
                          <span className="text-voka-gray">{systemMetrics?.model_buffers_gb || 0}GB</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <div className="w-3 h-3 rounded-sm bg-amber-600/50" />
                          <span className="text-voka-white">Caché:</span>
                          <span className="text-voka-gray">{systemMetrics?.cache_gb || 0}GB</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <div className="w-3 h-3 rounded-sm bg-gray-600/50" />
                          <span className="text-voka-white">Sistema:</span>
                          <span className="text-voka-gray">{systemMetrics?.system_gb || 0}GB</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <div className="w-3 h-3 rounded-sm border border-voka-border" />
                          <span className="text-voka-white">Disponible:</span>
                          <span className="text-voka-gray">{systemMetrics?.available_gb || 0}GB</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Métricas de rendimiento */}
              <div>
                <h3 className="text-lg font-medium text-voka-white mb-3">⚡ MÉTRICAS DE RENDIMIENTO DE INFERENCIA</h3>
                <div className="overflow-hidden rounded-md border border-voka-border">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="bg-voka-blue-black/50">
                        <th className="px-4 py-2 text-left font-medium text-voka-gray">MODELO</th>
                        <th className="px-4 py-2 text-left font-medium text-voka-gray">TOKENS/SEG</th>
                        <th className="px-4 py-2 text-left font-medium text-voka-gray">LATENCIA</th>
                        <th className="px-4 py-2 text-left font-medium text-voka-gray">RENDIMIENTO</th>
                        <th className="px-4 py-2 text-left font-medium text-voka-gray">EFICIENCIA</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-voka-border">
                      {loadedModels.map((model, index) => (
                        <tr
                          key={model.id}
                          className={`${index % 2 === 0 ? "bg-voka-blue-black/30" : "bg-voka-blue-black/20"}`}
                        >
                          <td className="px-4 py-3 text-voka-white">{model.name}</td>
                          <td className="px-4 py-3 text-voka-gray">
                            {model.type === "LLM" ? "245" : model.type === "TRANSLATION" ? "890" : "N/A"}
                          </td>
                          <td className="px-4 py-3 text-voka-gray">
                            {model.type === "LLM"
                              ? "45ms"
                              : model.type === "STT"
                                ? "1.2s"
                                : model.type === "TTS"
                                  ? "2.8s"
                                  : "12ms"}
                          </td>
                          <td className="px-4 py-3 text-voka-gray">
                            {model.type === "LLM"
                              ? "2.4M/día"
                              : model.type === "STT"
                                ? "720 hrs"
                                : model.type === "TTS"
                                  ? "480 mins"
                                  : "8.9M/día"}
                          </td>
                          <td className="px-4 py-3 text-voka-gray">
                            {model.type === "LLM"
                              ? "92%"
                              : model.type === "STT"
                                ? "87%"
                                : model.type === "TTS"
                                  ? "91%"
                                  : "95%"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot className="bg-voka-blue-black/40">
                      <tr>
                        <td colSpan={2} className="px-4 py-3 text-voka-white font-medium">
                          EFICIENCIA TOTAL DEL SISTEMA: 91.25%
                        </td>
                        <td colSpan={3} className="px-4 py-3 text-voka-white font-medium">
                          UTILIZACIÓN GPU: {gpuMetrics?.utilization_percentage || 0}%
                        </td>
                      </tr>
                      <tr>
                        <td colSpan={5} className="px-4 py-3 text-voka-gray text-sm">
                          Capacidad de procesamiento diario: 11.3M tokens + 720h audio + 480m TTS
                        </td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

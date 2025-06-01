"use client"

import React from "react"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Checkbox } from "@/components/ui/checkbox"
import { RefreshCw, Download, Upload, AlertTriangle, Brain, Mic, Volume2, Globe } from "lucide-react"
import type { AIModel, ModelOperation } from "@/types/ai-models"
import { getAvailableModels, loadModel, unloadModel, getOperationStatus } from "@/services/ai-models-service"

export function ModelosCargaDescarga() {
  const [models, setModels] = useState<AIModel[]>([])
  const [operations, setOperations] = useState<ModelOperation[]>([])
  const [selectedModels, setSelectedModels] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Cargar datos iniciales
  useEffect(() => {
    loadData()

    // Actualizar estado de operaciones cada 2 segundos
    const interval = setInterval(() => {
      updateOperationsStatus()
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  // Función para cargar todos los datos
  const loadData = async () => {
    setLoading(true)
    try {
      const modelsData = await getAvailableModels()
      setModels(modelsData)
      setError(null)
    } catch (err) {
      setError("Error al cargar datos de modelos: " + (err as Error).message)
      console.error("Error cargando datos:", err)
    } finally {
      setLoading(false)
    }
  }

  // Actualizar estado de operaciones en curso
  const updateOperationsStatus = async () => {
    if (operations.length === 0) return

    const updatedOperations = [...operations]
    let hasChanges = false

    for (let i = 0; i < updatedOperations.length; i++) {
      if (updatedOperations[i].status === "completed" || updatedOperations[i].status === "failed") continue

      try {
        const status = await getOperationStatus(updatedOperations[i].operation_id)
        updatedOperations[i] = status
        hasChanges = true

        // Si la operación se completó, actualizar la lista de modelos
        if (status.status === "completed" && !updatedOperations[i].completed_at) {
          loadData()
        }
      } catch (err) {
        console.error("Error actualizando estado de operación:", err)
      }
    }

    if (hasChanges) {
      setOperations(updatedOperations)
    }
  }

  // Cargar un modelo
  const handleLoadModel = async (modelId: string) => {
    try {
      const operation = await loadModel(modelId)
      setOperations((prev) => [...prev, operation])
    } catch (err) {
      setError("Error al cargar modelo: " + (err as Error).message)
    }
  }

  // Descargar un modelo
  const handleUnloadModel = async (modelId: string) => {
    try {
      const operation = await unloadModel(modelId)
      setOperations((prev) => [...prev, operation])
    } catch (err) {
      setError("Error al descargar modelo: " + (err as Error).message)
    }
  }

  // Manejar selección de modelos
  const toggleModelSelection = (modelId: string) => {
    setSelectedModels((prev) => (prev.includes(modelId) ? prev.filter((id) => id !== modelId) : [...prev, modelId]))
  }

  // Cargar modelos seleccionados
  const loadSelectedModels = async () => {
    for (const modelId of selectedModels) {
      const model = models.find((m) => m.id === modelId)
      if (model && model.status === "unloaded") {
        await handleLoadModel(modelId)
      }
    }
  }

  // Descargar modelos seleccionados
  const unloadSelectedModels = async () => {
    for (const modelId of selectedModels) {
      const model = models.find((m) => m.id === modelId)
      if (model && model.status === "loaded") {
        await handleUnloadModel(modelId)
      }
    }
  }

  // Cargar preset de modelos
  const loadPreset = (preset: string) => {
    let presetModels: string[] = []

    switch (preset) {
      case "production":
        presetModels = ["qwen-7b-chat", "whisper-medium", "xtts-v2", "nllb-200"]
        break
      case "minimal":
        presetModels = ["qwen-7b-chat", "nllb-200"]
        break
      case "development":
        presetModels = ["qwen-7b-chat", "whisper-medium", "xtts-v2", "nllb-200", "whisper-large"]
        break
      default:
        return
    }

    setSelectedModels(presetModels)
  }

  // Calcular uso de memoria estimado
  const calculateMemoryEstimate = () => {
    let gpuMemory = 0
    let systemMemory = 0

    selectedModels.forEach((modelId) => {
      const model = models.find((m) => m.id === modelId)
      if (model) {
        // Si el modelo ya está cargado, no sumamos su memoria
        if (model.status !== "loaded") {
          gpuMemory += model.size_gb * 0.8 // Estimación aproximada de uso de GPU
          systemMemory += model.size_gb * 0.3 // Estimación aproximada de uso de RAM
        }
      }
    })

    return {
      gpu: gpuMemory.toFixed(1),
      system: systemMemory.toFixed(1),
      total: (gpuMemory + systemMemory).toFixed(1),
    }
  }

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

  // Obtener estado visual del modelo
  const getModelStatus = (model: AIModel) => {
    if (model.status === "loaded") {
      return <Badge className="bg-emerald-500/20 text-emerald-300 border-emerald-800">🟢 CARGADO</Badge>
    } else if (model.status === "unloaded") {
      if (model.size_gb > 8) {
        return <Badge className="bg-red-500/20 text-red-300 border-red-800">❌ SIN MEM</Badge>
      }
      return <Badge className="bg-blue-500/20 text-blue-300 border-blue-800">💤 LISTO</Badge>
    } else if (model.status === "loading") {
      return <Badge className="bg-amber-500/20 text-amber-300 border-amber-800">⏳ CARGANDO</Badge>
    } else {
      return <Badge className="bg-red-500/20 text-red-300 border-red-800">❌ ERROR</Badge>
    }
  }

  // Obtener acción disponible para el modelo
  const getModelAction = (model: AIModel) => {
    // Verificar si hay una operación en curso para este modelo
    const activeOperation = operations.find(
      (op) => op.model_id === model.id && (op.status === "pending" || op.status === "in_progress"),
    )

    if (activeOperation) {
      return (
        <Button
          size="sm"
          variant="outline"
          disabled
          className="bg-voka-blue-black/50 border-voka-border text-voka-gray"
        >
          <RefreshCw className="h-4 w-4 mr-1 animate-spin" />
          {activeOperation.operation_type === "load" ? "CARGANDO..." : "DESCARGANDO..."}
        </Button>
      )
    }

    if (model.status === "loaded") {
      return (
        <Button
          size="sm"
          variant="outline"
          onClick={() => handleUnloadModel(model.id)}
          className="bg-voka-blue-black/50 border-voka-border text-voka-gray hover:bg-voka-blue-black"
        >
          <Upload className="h-4 w-4 mr-1" /> DESCARGAR
        </Button>
      )
    } else if (model.status === "unloaded") {
      if (model.size_gb > 8) {
        return (
          <Button
            size="sm"
            variant="outline"
            disabled
            className="bg-voka-blue-black/50 border-voka-border text-voka-gray"
          >
            <AlertTriangle className="h-4 w-4 mr-1" /> REQUIERE GPU
          </Button>
        )
      }
      return (
        <Button
          size="sm"
          variant="outline"
          onClick={() => handleLoadModel(model.id)}
          className="bg-voka-blue-black/50 border-voka-border text-voka-gray hover:bg-voka-blue-black"
        >
          <Download className="h-4 w-4 mr-1" /> CARGAR
        </Button>
      )
    }

    return null
  }

  // Agrupar modelos por tipo
  const modelsByType = models.reduce(
    (acc, model) => {
      if (!acc[model.type]) {
        acc[model.type] = []
      }
      acc[model.type].push(model)
      return acc
    },
    {} as Record<string, AIModel[]>,
  )

  // Memoria estimada
  const memoryEstimate = calculateMemoryEstimate()

  return (
    <div className="space-y-6">
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader className="pb-2">
          <div className="flex justify-between items-center">
            <CardTitle className="text-xl text-voka-white">📥 Gestión del Ciclo de Vida de Modelos</CardTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={loadData}
              className="bg-voka-blue-black border-voka-border text-voka-white hover:bg-voka-blue-black/80"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
              Escanear Modelos
            </Button>
          </div>
          <CardDescription className="text-voka-gray">Carga, descarga y gestión de modelos de IA</CardDescription>
        </CardHeader>
        <CardContent>
          {error ? (
            <div className="bg-red-900/20 border border-red-700 rounded-md p-3 text-red-300">{error}</div>
          ) : (
            <>
              {/* Repositorio de modelos disponibles */}
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-voka-white mb-3">REPOSITORIO DE MODELOS DISPONIBLES</h3>
                  <div className="overflow-hidden rounded-md border border-voka-border">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="bg-voka-blue-black/50">
                          <th className="px-4 py-2 text-left font-medium text-voka-gray">NOMBRE DEL MODELO</th>
                          <th className="px-4 py-2 text-left font-medium text-voka-gray">TAMAÑO</th>
                          <th className="px-4 py-2 text-left font-medium text-voka-gray">TIPO</th>
                          <th className="px-4 py-2 text-left font-medium text-voka-gray">ESTADO</th>
                          <th className="px-4 py-2 text-left font-medium text-voka-gray">ACCIONES</th>
                          <th className="px-4 py-2 text-left font-medium text-voka-gray">SELECCIÓN</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-voka-border">
                        {Object.entries(modelsByType).map(([type, typeModels]) => (
                          <React.Fragment key={type}>
                            {typeModels.map((model, index) => (
                              <tr
                                key={model.id}
                                className={`${index % 2 === 0 ? "bg-voka-blue-black/30" : "bg-voka-blue-black/20"}`}
                              >
                                <td className="px-4 py-3 text-voka-white">
                                  <div className="flex items-center gap-2">
                                    {getModelIcon(model.type)}
                                    {model.name}
                                  </div>
                                </td>
                                <td className="px-4 py-3 text-voka-gray">{model.size_gb}GB</td>
                                <td className="px-4 py-3 text-voka-gray">{model.type}</td>
                                <td className="px-4 py-3">{getModelStatus(model)}</td>
                                <td className="px-4 py-3">{getModelAction(model)}</td>
                                <td className="px-4 py-3">
                                  <Checkbox
                                    checked={selectedModels.includes(model.id)}
                                    onCheckedChange={() => toggleModelSelection(model.id)}
                                    className="border-voka-border data-[state=checked]:bg-voka-neon-pink data-[state=checked]:border-voka-neon-pink"
                                  />
                                </td>
                              </tr>
                            ))}
                          </React.Fragment>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Operaciones en curso */}
                {operations.filter((op) => op.status === "pending" || op.status === "in_progress").length > 0 && (
                  <div>
                    <h3 className="text-lg font-medium text-voka-white mb-3">⏳ OPERACIONES ACTIVAS</h3>
                    <div className="space-y-3">
                      {operations
                        .filter((op) => op.status === "pending" || op.status === "in_progress")
                        .map((operation) => {
                          const model = models.find((m) => m.id === operation.model_id)
                          return (
                            <Card key={operation.operation_id} className="bg-voka-blue-black/30 border-voka-border">
                              <CardContent className="p-4">
                                <div className="flex items-center justify-between mb-2">
                                  <div className="flex items-center gap-2">
                                    {operation.operation_type === "load" ? (
                                      <Download className="h-5 w-5 text-blue-400" />
                                    ) : (
                                      <Upload className="h-5 w-5 text-amber-400" />
                                    )}
                                    <span className="text-voka-white">
                                      {operation.operation_type === "load" ? "Cargando" : "Descargando"}{" "}
                                      {model?.name || operation.model_id}...
                                    </span>
                                  </div>
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    className="bg-voka-blue-black/50 border-voka-border text-voka-gray hover:bg-voka-blue-black"
                                  >
                                    ❌ CANCELAR
                                  </Button>
                                </div>
                                <Progress
                                  value={operation.progress_percentage}
                                  className="h-2 bg-voka-blue-black/50"
                                  indicatorClassName="bg-voka-neon-pink"
                                />
                                <div className="flex justify-between mt-1 text-xs text-voka-gray">
                                  <span>{operation.progress_percentage}%</span>
                                  {operation.eta_seconds && <span>ETA: {operation.eta_seconds} segundos</span>}
                                </div>
                              </CardContent>
                            </Card>
                          )
                        })}
                    </div>
                  </div>
                )}

                {/* Operaciones completadas recientemente */}
                {operations.filter((op) => op.status === "completed" && op.completed_at).length > 0 && (
                  <div>
                    <h3 className="text-lg font-medium text-voka-white mb-3">✅ OPERACIONES COMPLETADAS</h3>
                    <div className="space-y-2">
                      {operations
                        .filter((op) => op.status === "completed" && op.completed_at)
                        .slice(0, 3)
                        .map((operation) => {
                          const model = models.find((m) => m.id === operation.model_id)
                          return (
                            <div
                              key={operation.operation_id}
                              className="bg-voka-blue-black/20 border border-voka-border rounded-md p-3"
                            >
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                  <span className="text-emerald-400">✅</span>
                                  <span className="text-voka-white">
                                    {operation.operation_type === "load" ? "Cargado" : "Descargado"}{" "}
                                    {model?.name || operation.model_id}
                                  </span>
                                </div>
                                <span className="text-xs text-voka-gray">
                                  {new Date(operation.completed_at!).toLocaleTimeString()}
                                </span>
                              </div>
                            </div>
                          )
                        })}
                    </div>
                  </div>
                )}

                {/* Operaciones por lotes */}
                <div>
                  <h3 className="text-lg font-medium text-voka-white mb-3">🎛️ OPERACIONES POR LOTES</h3>
                  <Card className="bg-voka-blue-black/30 border-voka-border">
                    <CardContent className="p-4">
                      <div className="space-y-4">
                        {/* Presets rápidos */}
                        <div>
                          <h4 className="text-sm font-medium text-voka-white mb-2">PRESETS RÁPIDOS</h4>
                          <div className="flex flex-wrap gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => loadPreset("production")}
                              className="bg-voka-blue-black/50 border-voka-border text-voka-gray hover:bg-voka-blue-black"
                            >
                              🚀 Set Producción
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => loadPreset("development")}
                              className="bg-voka-blue-black/50 border-voka-border text-voka-gray hover:bg-voka-blue-black"
                            >
                              🧪 Set Desarrollo
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => loadPreset("minimal")}
                              className="bg-voka-blue-black/50 border-voka-border text-voka-gray hover:bg-voka-blue-black"
                            >
                              💾 Set Mínimo
                            </Button>
                          </div>
                        </div>

                        {/* Selección personalizada */}
                        <div>
                          <h4 className="text-sm font-medium text-voka-white mb-2">SELECCIÓN PERSONALIZADA</h4>
                          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                            {models.slice(0, 9).map((model) => (
                              <div key={model.id} className="flex items-center space-x-2">
                                <Checkbox
                                  id={`select-${model.id}`}
                                  checked={selectedModels.includes(model.id)}
                                  onCheckedChange={() => toggleModelSelection(model.id)}
                                  className="border-voka-border data-[state=checked]:bg-voka-neon-pink data-[state=checked]:border-voka-neon-pink"
                                />
                                <label htmlFor={`select-${model.id}`} className="text-sm text-voka-gray cursor-pointer">
                                  {model.name}
                                </label>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Acciones por lotes */}
                        <div>
                          <h4 className="text-sm font-medium text-voka-white mb-2">ACCIONES POR LOTES</h4>
                          <div className="flex flex-wrap gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={loadSelectedModels}
                              disabled={selectedModels.length === 0}
                              className="bg-voka-blue-black/50 border-voka-border text-voka-gray hover:bg-voka-blue-black"
                            >
                              <Download className="h-4 w-4 mr-1" /> CARGAR SELECCIONADOS
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={unloadSelectedModels}
                              disabled={selectedModels.length === 0}
                              className="bg-voka-blue-black/50 border-voka-border text-voka-gray hover:bg-voka-blue-black"
                            >
                              <Upload className="h-4 w-4 mr-1" /> DESCARGAR SELECCIONADOS
                            </Button>
                          </div>
                        </div>

                        {/* Estimación de memoria */}
                        <div className="mt-4 pt-4 border-t border-voka-border">
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-voka-white">ESTIMACIÓN DE MEMORIA:</span>
                            <span className="text-sm text-voka-white">
                              {memoryEstimate.gpu}GB GPU + {memoryEstimate.system}GB Sistema = {memoryEstimate.total}GB
                              Total
                            </span>
                          </div>
                          <div className="flex justify-between items-center mt-1">
                            <span className="text-xs text-voka-gray">Disponible:</span>
                            <span className="text-xs text-voka-gray">
                              8.0GB GPU, 32.0GB Sistema
                              {Number.parseFloat(memoryEstimate.gpu) <= 8 &&
                              Number.parseFloat(memoryEstimate.system) <= 32 ? (
                                <span className="text-emerald-400 ml-1">✅ SUFICIENTE</span>
                              ) : (
                                <span className="text-red-400 ml-1">❌ INSUFICIENTE</span>
                              )}
                            </span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

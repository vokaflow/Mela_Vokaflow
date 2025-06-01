"use client"

import { Badge } from "@/components/ui/badge"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { RefreshCw } from "lucide-react"
import type { AIModel, ModelConfig } from "@/types/ai-models"
import { getModelStatus, updateModelConfig } from "@/services/ai-models-service"

export function ModelosConfiguracion() {
  const [models, setModels] = useState<AIModel[]>([])
  const [selectedModelId, setSelectedModelId] = useState<string>("")
  const [config, setConfig] = useState<ModelConfig | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // Cargar datos iniciales
  useEffect(() => {
    loadData()
  }, [])

  // Función para cargar todos los datos
  const loadData = async () => {
    setLoading(true)
    try {
      const modelsData = await getModelStatus()
      setModels(modelsData)
      
      // Seleccionar el primer modelo por defecto
      if (modelsData.length > 0 && !selectedModelId) {
        setSelectedModelId(modelsData[0].id)
        setConfig(modelsData[0].configuration)
      }
      
      setError(null)
    } catch (err) {
      setError('Error al cargar datos de modelos: ' + (err as Error).message)
      console.error('Error cargando datos:', err)
    } finally {
      setLoading(false)
    }
  }

  // Manejar cambio de modelo seleccionado
  const handleModelChange = (modelId: string) => {
    const model = models.find(m => m.id === modelId)
    if (model) {
      setSelectedModelId(modelId)
      setConfig(model.configuration)
    }
  }

  // Manejar cambios en la configuración
  const handleConfigChange = (key: string, value: any) => {
    if (!config) return
    
    if (key.includes('.')) {
      // Para propiedades anidadas como 'optimizations.kv_cache'
      const [parent, child] = key.split('.')
      setConfig({
        ...config,
        [parent]: {
          ...config[parent as keyof typeof config],
          [child]: value
        }
      })
    } else {
      setConfig({
        ...config,
        [key]: value
      })
    }
  }

  // Guardar configuración
  const saveConfig = async () => {
    if (!selectedModelId || !config) return
    
    setSaving(true)
    try {
      await updateModelConfig(selectedModelId, config)
      setSuccess('Configuración guardada correctamente')
      
      // Actualizar la lista de modelos
      loadData()
      
      // Limpiar mensaje de éxito después de 3 segundos
      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      setError('Error al guardar configuración: ' + (err as Error).message)
    } finally {
      setSaving(false)
    }
  }

  // Restablecer configuración por defecto
  const resetConfig = () => {
    const model = models.find(m => m.id === selectedModelId)
    if (model) {
      setConfig(model.configuration)
    }
  }

  // Obtener el modelo seleccionado
  const selectedModel = models.find(m => m.id === selectedModelId)

  return (
    <div className="space-y-6">
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader className="pb-2">
          <div className="flex justify-between items-center">
            <CardTitle className="text-xl text-voka-white">⚙️ Configuración y Prioridad de Modelos</CardTitle>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={loadData}
              className="bg-voka-blue-black border-voka-border text-voka-white hover:bg-voka-blue-black/80"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refrescar
            </Button>
          </div>
          <CardDescription className="text-voka-gray">
            Gestión de prioridades y configuración avanzada de modelos
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error ? (
            <div className="bg-red-900/20 border border-red-700 rounded-md p-3 text-red-300">
              {error}
            </div>
          ) : success ? (
            <div className="bg-green-900/20 border border-green-700 rounded-md p-3 text-green-300 mb-4">
              {success}
            </div>
          ) : null}

          {/* Gestor de prioridad de modelos */}
          <div className="mb-8">
            <h3 className="text-lg font-medium text-voka-white mb-3">GESTIÓN DE PRIORIDAD DE EJECUCIÓN</h3>
            <Card className="bg-voka-blue-black/30 border-voka-border">
              <CardContent className="p-4">
                <div className="space-y-4">
                  {/* Lista de modelos ordenables */}
                  <div className="space-y-2">
                    {models
                      .filter(m => m.status === 'loaded')
                      .map((model, index) => (
                        <div 
                          key={model.id} 
                          className="flex items-center justify-between p-3 bg-voka-blue-black/40 border border-voka-border rounded-md"
                        >
                          <div className="flex items-center gap-2">
                            <div className="text-voka-gray">{index + 1}.</div>
                            <div className="text-voka-white">{model.name}</div>
                            <div className="ml-2">
                              <Badge priority={index < 2 ? 'high' : 'medium'} />
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Button 
                              variant="outline" 
                              size="icon" 
                              disabled={index === 0}
                              className="h-8 w-8 bg-voka-blue-black/50 border-voka-border text-voka-gray hover:bg-voka-blue-black"
                            >
                              ↑
                            </Button>
                            <Button 
                              variant="outline" 
                              size="icon" 
                              disabled={index === models.filter(m => m.status === 'loaded').length - 1}
                              className="h-8 w-8 bg-voka-blue-black/50 border-voka-border text-voka-gray hover:bg-voka-blue-black"
                            >
                              ↓
                            </Button>
                          </div>
                        </div>
                      ))}
                  </div>
                  
                  {/* Reglas de auto-escalado */}
                  <div className="pt-4 border-t border-voka-border">
                    <h4 className="text-sm font-medium text-voka-white mb-3">REGLAS DE AUTO-ESCALADO</h4>
                    <div className="space-y-3">
                      <div className="flex items-center space-x-2">
                        <Switch id="rule-1" defaultChecked />
                        <Label htmlFor="rule-1" className="text-voka-gray">
                          Reducir modelos inactivos después de 30 minutos
                        </Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Switch id="rule-2" defaultChecked />
                        <Label htmlFor="rule-2" className="text-voka-gray">
                          Cargar modelos automáticamente según patrones de uso
                        </Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Switch id="rule-3" defaultChecked />
                        <Label htmlFor="rule-3" className="text-voka-gray">
                          Descargar modelos de baja prioridad si la memoria GPU es &lt; 10%
                        </Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Switch id="rule-4" />
                        <Label htmlFor="rule-4" className="text-voka-gray">
                          Cargar modelos de respaldo durante tráfico alto
                        </Label>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex justify-end">
                    <Button 
                      variant\

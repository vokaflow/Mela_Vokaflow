"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Slider } from "@/components/ui/slider"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Save, RotateCcw, AlertTriangle, CheckCircle } from "lucide-react"
import type { SystemConfig } from "../../types/settings"
import { settingsService } from "../../services/settings-service"

export function ConfiguracionGeneral() {
  const [configs, setConfigs] = useState<SystemConfig[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [hasChanges, setHasChanges] = useState(false)
  const [originalConfigs, setOriginalConfigs] = useState<SystemConfig[]>([])

  useEffect(() => {
    loadConfigs()
  }, [])

  const loadConfigs = async () => {
    try {
      setLoading(true)
      const data = await settingsService.getSystemConfig()
      setConfigs(data)
      setOriginalConfigs(JSON.parse(JSON.stringify(data)))
    } catch (error) {
      console.error("Error loading configs:", error)
    } finally {
      setLoading(false)
    }
  }

  const updateConfig = (id: string, value: any) => {
    setConfigs((prev) => prev.map((config) => (config.id === id ? { ...config, value } : config)))
    setHasChanges(true)
  }

  const saveChanges = async () => {
    try {
      setSaving(true)
      const changedConfigs = configs.filter(
        (config, index) => JSON.stringify(config.value) !== JSON.stringify(originalConfigs[index]?.value),
      )

      for (const config of changedConfigs) {
        await settingsService.updateSystemConfig(config)
      }

      setOriginalConfigs(JSON.parse(JSON.stringify(configs)))
      setHasChanges(false)
    } catch (error) {
      console.error("Error saving configs:", error)
    } finally {
      setSaving(false)
    }
  }

  const resetChanges = () => {
    setConfigs(JSON.parse(JSON.stringify(originalConfigs)))
    setHasChanges(false)
  }

  const renderConfigControl = (config: SystemConfig) => {
    switch (config.type) {
      case "boolean":
        return (
          <div className="flex items-center space-x-2">
            <Switch
              checked={config.value}
              onCheckedChange={(checked) => updateConfig(config.id, checked)}
              disabled={!config.editable}
            />
            <Label className="text-voka-white">{config.value ? "Activado" : "Desactivado"}</Label>
          </div>
        )

      case "number":
        if (config.id.includes("speed") || config.id.includes("quality")) {
          return (
            <div className="space-y-2">
              <Slider
                value={[config.value]}
                onValueChange={([value]) => updateConfig(config.id, value)}
                max={config.id.includes("limit") ? 10000 : 2}
                min={0}
                step={config.id.includes("limit") ? 100 : 0.1}
                className="w-full"
                disabled={!config.editable}
              />
              <div className="text-sm text-voka-gray">{config.value}</div>
            </div>
          )
        } else {
          return (
            <Input
              type="number"
              value={config.value}
              onChange={(e) => updateConfig(config.id, Number.parseFloat(e.target.value))}
              disabled={!config.editable}
              className="bg-voka-blue-black border-voka-border text-voka-white"
            />
          )
        }

      case "string":
        return (
          <Input
            value={config.value}
            onChange={(e) => updateConfig(config.id, e.target.value)}
            disabled={!config.editable}
            className="bg-voka-blue-black border-voka-border text-voka-white"
          />
        )

      default:
        return <div className="text-voka-gray">Tipo no soportado</div>
    }
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "ai":
        return "🧠"
      case "api":
        return "📡"
      case "security":
        return "🔒"
      case "performance":
        return "⚡"
      default:
        return "⚙️"
    }
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "ai":
        return "bg-purple-500/20 text-purple-300"
      case "api":
        return "bg-blue-500/20 text-blue-300"
      case "security":
        return "bg-red-500/20 text-red-300"
      case "performance":
        return "bg-green-500/20 text-green-300"
      default:
        return "bg-gray-500/20 text-gray-300"
    }
  }

  const configsByCategory = configs.reduce(
    (acc, config) => {
      if (!acc[config.category]) acc[config.category] = []
      acc[config.category].push(config)
      return acc
    },
    {} as Record<string, SystemConfig[]>,
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-voka-magenta"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header con controles */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-voka-white font-montserrat">⚙️ Configuración General</h2>
          <p className="text-voka-gray">Ajustes principales del sistema VokaFlow</p>
        </div>

        {hasChanges && (
          <div className="flex items-center space-x-3">
            <Badge variant="outline" className="border-voka-orange text-voka-orange">
              <AlertTriangle className="w-3 h-3 mr-1" />
              Cambios pendientes
            </Badge>
            <Button
              variant="outline"
              size="sm"
              onClick={resetChanges}
              className="border-voka-border text-voka-gray hover:text-voka-white"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              Deshacer
            </Button>
            <Button
              onClick={saveChanges}
              disabled={saving}
              className="bg-voka-magenta hover:bg-voka-magenta/80 text-white"
            >
              {saving ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : (
                <Save className="w-4 h-4 mr-2" />
              )}
              Guardar
            </Button>
          </div>
        )}
      </div>

      {/* Configuraciones por categoría */}
      <Tabs defaultValue="general" className="w-full">
        <TabsList className="grid w-full grid-cols-5 bg-voka-blue-black">
          <TabsTrigger value="general" className="data-[state=active]:bg-voka-magenta">
            General
          </TabsTrigger>
          <TabsTrigger value="ai" className="data-[state=active]:bg-voka-magenta">
            IA
          </TabsTrigger>
          <TabsTrigger value="api" className="data-[state=active]:bg-voka-magenta">
            API
          </TabsTrigger>
          <TabsTrigger value="security" className="data-[state=active]:bg-voka-magenta">
            Seguridad
          </TabsTrigger>
          <TabsTrigger value="performance" className="data-[state=active]:bg-voka-magenta">
            Rendimiento
          </TabsTrigger>
        </TabsList>

        {Object.entries(configsByCategory).map(([category, categoryConfigs]) => (
          <TabsContent key={category} value={category} className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              {categoryConfigs.map((config) => (
                <Card key={config.id} className="bg-voka-blue-black border-voka-border">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg text-voka-white font-montserrat flex items-center">
                        <span className="mr-2">{getCategoryIcon(config.category)}</span>
                        {config.name}
                      </CardTitle>
                      <div className="flex items-center space-x-2">
                        <Badge className={getCategoryColor(config.category)}>{config.category}</Badge>
                        {config.requires_restart && (
                          <Badge variant="outline" className="border-voka-orange text-voka-orange">
                            Requiere reinicio
                          </Badge>
                        )}
                      </div>
                    </div>
                    <p className="text-sm text-voka-gray">{config.description}</p>
                  </CardHeader>
                  <CardContent>{renderConfigControl(config)}</CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        ))}
      </Tabs>

      {/* Estado de guardado */}
      {!hasChanges && !loading && (
        <div className="flex items-center justify-center py-4">
          <div className="flex items-center text-voka-green">
            <CheckCircle className="w-4 h-4 mr-2" />
            Todos los cambios guardados
          </div>
        </div>
      )}
    </div>
  )
}

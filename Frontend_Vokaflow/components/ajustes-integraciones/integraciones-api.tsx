"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { TestTube, Settings, Zap, AlertCircle, CheckCircle, Clock, Search } from "lucide-react"
import type { Integration } from "../../types/settings"
import { settingsService } from "../../services/settings-service"

export function IntegracionesApi() {
  const [integrations, setIntegrations] = useState<Integration[]>([])
  const [loading, setLoading] = useState(true)
  const [testing, setTesting] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedType, setSelectedType] = useState<string>("all")

  useEffect(() => {
    loadIntegrations()
  }, [])

  const loadIntegrations = async () => {
    try {
      setLoading(true)
      const data = await settingsService.getIntegrations()
      setIntegrations(data)
    } catch (error) {
      console.error("Error loading integrations:", error)
    } finally {
      setLoading(false)
    }
  }

  const testIntegration = async (integrationId: string) => {
    try {
      setTesting(integrationId)
      const result = await settingsService.testIntegration(integrationId)

      setIntegrations((prev) =>
        prev.map((integration) =>
          integration.id === integrationId
            ? {
                ...integration,
                status: result.success ? "connected" : "error",
                latency_ms: result.latency,
                error_message: result.error,
                last_test: new Date().toISOString(),
              }
            : integration,
        ),
      )
    } catch (error) {
      console.error("Error testing integration:", error)
    } finally {
      setTesting(null)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "connected":
        return <CheckCircle className="w-4 h-4 text-voka-green" />
      case "disconnected":
        return <AlertCircle className="w-4 h-4 text-voka-gray" />
      case "error":
        return <AlertCircle className="w-4 h-4 text-voka-red" />
      case "testing":
        return <Clock className="w-4 h-4 text-voka-orange animate-spin" />
      default:
        return <AlertCircle className="w-4 h-4 text-voka-gray" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "connected":
        return "bg-green-500/20 text-green-300 border-green-500/30"
      case "disconnected":
        return "bg-gray-500/20 text-gray-300 border-gray-500/30"
      case "error":
        return "bg-red-500/20 text-red-300 border-red-500/30"
      case "testing":
        return "bg-orange-500/20 text-orange-300 border-orange-500/30"
      default:
        return "bg-gray-500/20 text-gray-300 border-gray-500/30"
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "ai":
        return "🤖"
      case "cloud":
        return "☁️"
      case "database":
        return "🗄️"
      case "analytics":
        return "📊"
      case "communication":
        return "💬"
      default:
        return "🔗"
    }
  }

  const filteredIntegrations = integrations.filter((integration) => {
    const matchesSearch =
      integration.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      integration.provider.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = selectedType === "all" || integration.type === selectedType
    return matchesSearch && matchesType
  })

  const integrationTypes = ["all", ...Array.from(new Set(integrations.map((i) => i.type)))]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-voka-magenta"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-voka-white font-montserrat">🔗 Integraciones API</h2>
          <p className="text-voka-gray">Gestión de servicios externos y conexiones</p>
        </div>

        <div className="flex items-center space-x-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-voka-gray w-4 h-4" />
            <Input
              placeholder="Buscar integraciones..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 bg-voka-blue-black border-voka-border text-voka-white w-64"
            />
          </div>
        </div>
      </div>

      {/* Filtros */}
      <Tabs value={selectedType} onValueChange={setSelectedType} className="w-full">
        <TabsList className="bg-voka-blue-black">
          {integrationTypes.map((type) => (
            <TabsTrigger key={type} value={type} className="data-[state=active]:bg-voka-magenta capitalize">
              {type === "all" ? "Todas" : type}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      {/* Grid de integraciones */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredIntegrations.map((integration) => (
          <Card
            key={integration.id}
            className="bg-voka-blue-black border-voka-border hover:border-voka-magenta/50 transition-colors"
          >
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">{integration.icon}</span>
                  <div>
                    <CardTitle className="text-lg text-voka-white font-montserrat">{integration.name}</CardTitle>
                    <p className="text-sm text-voka-gray">{integration.provider}</p>
                  </div>
                </div>
                <Badge className={getStatusColor(testing === integration.id ? "testing" : integration.status)}>
                  {getStatusIcon(testing === integration.id ? "testing" : integration.status)}
                  <span className="ml-1 capitalize">{testing === integration.id ? "Testing" : integration.status}</span>
                </Badge>
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              <p className="text-sm text-voka-gray">{integration.description}</p>

              {/* Métricas */}
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-4">
                  <Badge variant="outline" className="border-voka-border text-voka-gray">
                    {getTypeIcon(integration.type)} {integration.type}
                  </Badge>
                  {integration.latency_ms && <span className="text-voka-green">{integration.latency_ms}ms</span>}
                </div>
                <span className="text-voka-gray">{new Date(integration.last_test).toLocaleDateString()}</span>
              </div>

              {/* Error message */}
              {integration.status === "error" && integration.error_message && (
                <div className="p-2 bg-red-500/10 border border-red-500/20 rounded text-sm text-red-300">
                  {integration.error_message}
                </div>
              )}

              {/* Acciones */}
              <div className="flex items-center space-x-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => testIntegration(integration.id)}
                  disabled={testing === integration.id}
                  className="border-voka-border text-voka-gray hover:text-voka-white flex-1"
                >
                  <TestTube className="w-4 h-4 mr-2" />
                  Test
                </Button>

                <Dialog>
                  <DialogTrigger asChild>
                    <Button
                      size="sm"
                      variant="outline"
                      className="border-voka-border text-voka-gray hover:text-voka-white"
                    >
                      <Settings className="w-4 h-4" />
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="bg-voka-blue-black border-voka-border">
                    <DialogHeader>
                      <DialogTitle className="text-voka-white">Configurar {integration.name}</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label className="text-voka-white">Configuración</Label>
                        <pre className="bg-voka-dark p-3 rounded text-sm text-voka-gray overflow-auto">
                          {JSON.stringify(integration.config, null, 2)}
                        </pre>
                      </div>
                      <div className="flex justify-end space-x-2">
                        <Button variant="outline" className="border-voka-border text-voka-gray">
                          Cancelar
                        </Button>
                        <Button className="bg-voka-magenta hover:bg-voka-magenta/80">Guardar</Button>
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Estado vacío */}
      {filteredIntegrations.length === 0 && (
        <div className="text-center py-12">
          <Zap className="w-12 h-12 text-voka-gray mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-voka-white mb-2">No se encontraron integraciones</h3>
          <p className="text-voka-gray">Ajusta los filtros o agrega nuevas integraciones</p>
        </div>
      )}
    </div>
  )
}

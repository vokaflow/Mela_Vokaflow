"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { AlertTriangle, RefreshCw, Bell, Search, CheckCircle, Filter } from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { alertService } from "@/services/infrastructure-service"
import type { Alert } from "@/types/infrastructure"

export function InfraestructuraAlerts() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)
  const [searchTerm, setSearchTerm] = useState("")
  const [levelFilter, setLevelFilter] = useState("all")
  const [statusFilter, setStatusFilter] = useState("all")

  const fetchAlerts = async () => {
    try {
      setRefreshing(true)
      const data = await alertService.getAlerts()
      setAlerts(data)
      setError(null)
    } catch (err) {
      setError("Error al cargar las alertas. Intente nuevamente.")
      console.error(err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchAlerts()
    // Configurar actualización automática cada 30 segundos
    const interval = setInterval(fetchAlerts, 30000)
    return () => clearInterval(interval)
  }, [])

  const handleAcknowledge = async (id: string) => {
    try {
      await alertService.acknowledgeAlert(id)
      // Actualizar el estado local
      setAlerts(alerts.map((alert) => (alert.id === id ? { ...alert, acknowledged: true } : alert)))
    } catch (err) {
      console.error("Error al reconocer la alerta:", err)
    }
  }

  const handleResolve = async (id: string) => {
    try {
      await alertService.resolveAlert(id)
      // Actualizar el estado local
      setAlerts(alerts.map((alert) => (alert.id === id ? { ...alert, resolved: true } : alert)))
    } catch (err) {
      console.error("Error al resolver la alerta:", err)
    }
  }

  const getLevelColor = (level: string) => {
    switch (level) {
      case "critical":
        return "bg-voka-red/20 text-voka-red border-voka-red"
      case "warning":
        return "bg-voka-orange/20 text-voka-orange border-voka-orange"
      case "info":
        return "bg-voka-blue/20 text-voka-blue border-voka-blue"
      default:
        return "bg-voka-gray/20 text-voka-gray border-voka-gray"
    }
  }

  const getLevelIcon = (level: string) => {
    switch (level) {
      case "critical":
        return <AlertTriangle className="h-4 w-4 text-voka-red" />
      case "warning":
        return <AlertTriangle className="h-4 w-4 text-voka-orange" />
      case "info":
        return <Bell className="h-4 w-4 text-voka-blue" />
      default:
        return <Bell className="h-4 w-4 text-voka-gray" />
    }
  }

  // Filtrar alertas
  const filteredAlerts = alerts.filter((alert) => {
    const matchesSearch =
      alert.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
      alert.source.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesLevel = levelFilter === "all" || alert.level === levelFilter

    const matchesStatus =
      statusFilter === "all" ||
      (statusFilter === "resolved" && alert.resolved) ||
      (statusFilter === "unresolved" && !alert.resolved) ||
      (statusFilter === "acknowledged" && alert.acknowledged && !alert.resolved)

    return matchesSearch && matchesLevel && matchesStatus
  })

  // Contar alertas por nivel
  const criticalCount = alerts.filter((a) => a.level === "critical" && !a.resolved).length
  const warningCount = alerts.filter((a) => a.level === "warning" && !a.resolved).length
  const infoCount = alerts.filter((a) => a.level === "info" && !a.resolved).length
  const resolvedCount = alerts.filter((a) => a.resolved).length

  return (
    <div className="space-y-6">
      {/* Resumen de alertas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-voka-blue-black border-voka-border">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-voka-red/20 flex items-center justify-center">
                <AlertTriangle className="h-5 w-5 text-voka-red" />
              </div>
              <div>
                <div className="text-2xl font-bold text-voka-red font-montserrat">{criticalCount}</div>
                <p className="text-voka-gray font-montserrat text-sm">Críticas</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-voka-orange/20 flex items-center justify-center">
                <AlertTriangle className="h-5 w-5 text-voka-orange" />
              </div>
              <div>
                <div className="text-2xl font-bold text-voka-orange font-montserrat">{warningCount}</div>
                <p className="text-voka-gray font-montserrat text-sm">Advertencias</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-voka-blue/20 flex items-center justify-center">
                <Bell className="h-5 w-5 text-voka-blue" />
              </div>
              <div>
                <div className="text-2xl font-bold text-voka-blue font-montserrat">{infoCount}</div>
                <p className="text-voka-gray font-montserrat text-sm">Informativas</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-voka-green/20 flex items-center justify-center">
                <CheckCircle className="h-5 w-5 text-voka-green" />
              </div>
              <div>
                <div className="text-2xl font-bold text-voka-green font-montserrat">{resolvedCount}</div>
                <p className="text-voka-gray font-montserrat text-sm">Resueltas</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filtros */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-voka-gray" />
                <Input
                  placeholder="Buscar alertas..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-voka-dark border-voka-border text-voka-white placeholder:text-voka-gray"
                />
              </div>
            </div>
            <Select value={levelFilter} onValueChange={setLevelFilter}>
              <SelectTrigger className="w-full md:w-48 bg-voka-dark border-voka-border text-voka-white">
                <SelectValue placeholder="Filtrar por nivel" />
              </SelectTrigger>
              <SelectContent className="bg-voka-blue-black border-voka-border">
                <SelectItem value="all">Todos los niveles</SelectItem>
                <SelectItem value="critical">Críticas</SelectItem>
                <SelectItem value="warning">Advertencias</SelectItem>
                <SelectItem value="info">Informativas</SelectItem>
              </SelectContent>
            </Select>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full md:w-48 bg-voka-dark border-voka-border text-voka-white">
                <SelectValue placeholder="Filtrar por estado" />
              </SelectTrigger>
              <SelectContent className="bg-voka-blue-black border-voka-border">
                <SelectItem value="all">Todos los estados</SelectItem>
                <SelectItem value="unresolved">Sin resolver</SelectItem>
                <SelectItem value="acknowledged">Reconocidas</SelectItem>
                <SelectItem value="resolved">Resueltas</SelectItem>
              </SelectContent>
            </Select>
            <Button
              onClick={fetchAlerts}
              disabled={refreshing}
              className="bg-voka-magenta hover:bg-voka-magenta/80 text-white font-montserrat"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? "animate-spin" : ""}`} />
              Actualizar
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Lista de alertas */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
              <Bell className="h-5 w-5 text-voka-magenta" />
              Alertas del Sistema
            </CardTitle>
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-voka-gray" />
              <span className="text-voka-gray font-montserrat text-sm">
                {filteredAlerts.length} alertas encontradas
              </span>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="flex flex-col items-center gap-2">
                <RefreshCw className="h-8 w-8 text-voka-magenta animate-spin" />
                <p className="text-voka-gray font-montserrat">Cargando alertas...</p>
              </div>
            </div>
          ) : error ? (
            <div className="bg-voka-red/10 border-voka-red/30 p-4 rounded-lg">
              <div className="flex items-center gap-3">
                <AlertTriangle className="h-5 w-5 text-voka-red" />
                <p className="text-voka-red font-montserrat">{error}</p>
              </div>
            </div>
          ) : filteredAlerts.length === 0 ? (
            <div className="flex justify-center items-center h-64">
              <p className="text-voka-gray font-montserrat">No se encontraron alertas</p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`p-4 rounded-lg border ${
                    alert.resolved ? "bg-voka-dark/50 border-voka-border/50" : "bg-voka-dark border-voka-border"
                  }`}
                >
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="flex items-start gap-3">
                      {getLevelIcon(alert.level)}
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <Badge className={`${getLevelColor(alert.level)} font-montserrat`}>
                            {alert.level === "critical"
                              ? "CRÍTICO"
                              : alert.level === "warning"
                                ? "ADVERTENCIA"
                                : "INFO"}
                          </Badge>
                          <span className="text-voka-gray font-montserrat text-xs">{alert.timestamp}</span>
                        </div>
                        <p className={`font-montserrat ${alert.resolved ? "text-voka-gray" : "text-voka-white"}`}>
                          {alert.message}
                        </p>
                        <p className="text-voka-gray font-montserrat text-sm mt-1">Fuente: {alert.source}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 md:flex-shrink-0">
                      {alert.resolved ? (
                        <Badge className="bg-voka-green/20 text-voka-green border-voka-green font-montserrat">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Resuelta
                        </Badge>
                      ) : alert.acknowledged ? (
                        <>
                          <Badge className="bg-voka-blue/20 text-voka-blue border-voka-blue font-montserrat">
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Reconocida
                          </Badge>
                          <Button
                            size="sm"
                            onClick={() => handleResolve(alert.id)}
                            className="bg-voka-green hover:bg-voka-green/80 text-white font-montserrat"
                          >
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Resolver
                          </Button>
                        </>
                      ) : (
                        <>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleAcknowledge(alert.id)}
                            className="border-voka-blue text-voka-blue hover:bg-voka-blue hover:text-white font-montserrat"
                          >
                            <Bell className="h-3 w-3 mr-1" />
                            Reconocer
                          </Button>
                          <Button
                            size="sm"
                            onClick={() => handleResolve(alert.id)}
                            className="bg-voka-green hover:bg-voka-green/80 text-white font-montserrat"
                          >
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Resolver
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

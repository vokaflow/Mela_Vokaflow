"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Settings, RefreshCw, Search, Play, Square, RotateCcw, AlertTriangle } from "lucide-react"
import { systemService } from "@/services/infrastructure-service"
import type { Service } from "@/types/infrastructure"

export function InfraestructuraServices() {
  const [services, setServices] = useState<Service[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [serverFilter, setServerFilter] = useState("all")

  const fetchServices = async () => {
    try {
      setRefreshing(true)
      const data = await systemService.getServices()
      setServices(data)
      setError(null)
    } catch (err) {
      setError("Error al cargar los servicios. Intente nuevamente.")
      console.error(err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchServices()
    // Configurar actualización automática cada 30 segundos
    const interval = setInterval(fetchServices, 30000)
    return () => clearInterval(interval)
  }, [])

  const handleServiceAction = async (id: string, action: "start" | "stop" | "restart") => {
    try {
      switch (action) {
        case "start":
          await systemService.startService(id)
          break
        case "stop":
          await systemService.stopService(id)
          break
        case "restart":
          await systemService.restartService(id)
          break
      }
      // Actualizar la lista después de la acción
      fetchServices()
    } catch (err) {
      console.error(`Error al ${action} el servicio:`, err)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "running":
        return "bg-voka-green/20 text-voka-green border-voka-green"
      case "stopped":
        return "bg-voka-red/20 text-voka-red border-voka-red"
      case "warning":
        return "bg-voka-orange/20 text-voka-orange border-voka-orange"
      case "restarting":
        return "bg-voka-blue/20 text-voka-blue border-voka-blue"
      default:
        return "bg-voka-gray/20 text-voka-gray border-voka-gray"
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "running":
        return <div className="w-3 h-3 rounded-full bg-voka-green animate-pulse"></div>
      case "stopped":
        return <div className="w-3 h-3 rounded-full bg-voka-red"></div>
      case "warning":
        return <AlertTriangle className="h-3 w-3 text-voka-orange" />
      case "restarting":
        return <RotateCcw className="h-3 w-3 text-voka-blue animate-spin" />
      default:
        return <div className="w-3 h-3 rounded-full bg-voka-gray"></div>
    }
  }

  // Filtrar servicios
  const filteredServices = services.filter((service) => {
    const matchesSearch =
      service.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      service.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      service.server.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesStatus = statusFilter === "all" || service.status === statusFilter
    const matchesServer = serverFilter === "all" || service.server === serverFilter

    return matchesSearch && matchesStatus && matchesServer
  })

  // Obtener servidores únicos
  const uniqueServers = Array.from(new Set(services.map((service) => service.server)))

  // Contar servicios por estado
  const runningCount = services.filter((s) => s.status === "running").length
  const stoppedCount = services.filter((s) => s.status === "stopped").length
  const warningCount = services.filter((s) => s.status === "warning").length
  const restartingCount = services.filter((s) => s.status === "restarting").length

  return (
    <div className="space-y-6">
      {/* Resumen de servicios */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-voka-blue-black border-voka-border">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-voka-green/20 flex items-center justify-center">
                <div className="w-4 h-4 rounded-full bg-voka-green animate-pulse"></div>
              </div>
              <div>
                <div className="text-2xl font-bold text-voka-green font-montserrat">{runningCount}</div>
                <p className="text-voka-gray font-montserrat text-sm">En ejecución</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-voka-red/20 flex items-center justify-center">
                <Square className="h-5 w-5 text-voka-red" />
              </div>
              <div>
                <div className="text-2xl font-bold text-voka-red font-montserrat">{stoppedCount}</div>
                <p className="text-voka-gray font-montserrat text-sm">Detenidos</p>
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
                <p className="text-voka-gray font-montserrat text-sm">Con advertencias</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-voka-blue/20 flex items-center justify-center">
                <RotateCcw className="h-5 w-5 text-voka-blue animate-spin" />
              </div>
              <div>
                <div className="text-2xl font-bold text-voka-blue font-montserrat">{restartingCount}</div>
                <p className="text-voka-gray font-montserrat text-sm">Reiniciando</p>
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
                  placeholder="Buscar servicios..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-voka-dark border-voka-border text-voka-white placeholder:text-voka-gray"
                />
              </div>
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full md:w-48 bg-voka-dark border-voka-border text-voka-white">
                <SelectValue placeholder="Filtrar por estado" />
              </SelectTrigger>
              <SelectContent className="bg-voka-blue-black border-voka-border">
                <SelectItem value="all">Todos los estados</SelectItem>
                <SelectItem value="running">En ejecución</SelectItem>
                <SelectItem value="stopped">Detenidos</SelectItem>
                <SelectItem value="warning">Con advertencias</SelectItem>
                <SelectItem value="restarting">Reiniciando</SelectItem>
              </SelectContent>
            </Select>
            <Select value={serverFilter} onValueChange={setServerFilter}>
              <SelectTrigger className="w-full md:w-48 bg-voka-dark border-voka-border text-voka-white">
                <SelectValue placeholder="Filtrar por servidor" />
              </SelectTrigger>
              <SelectContent className="bg-voka-blue-black border-voka-border">
                <SelectItem value="all">Todos los servidores</SelectItem>
                {uniqueServers.map((server) => (
                  <SelectItem key={server} value={server}>
                    {server}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button
              onClick={fetchServices}
              disabled={refreshing}
              className="bg-voka-magenta hover:bg-voka-magenta/80 text-white font-montserrat"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? "animate-spin" : ""}`} />
              Actualizar
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Lista de servicios */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader>
          <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
            <Settings className="h-5 w-5 text-voka-magenta" />
            Servicios del Sistema ({filteredServices.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="flex flex-col items-center gap-2">
                <RefreshCw className="h-8 w-8 text-voka-magenta animate-spin" />
                <p className="text-voka-gray font-montserrat">Cargando servicios...</p>
              </div>
            </div>
          ) : error ? (
            <div className="bg-voka-red/10 border-voka-red/30 p-4 rounded-lg">
              <div className="flex items-center gap-3">
                <AlertTriangle className="h-5 w-5 text-voka-red" />
                <p className="text-voka-red font-montserrat">{error}</p>
              </div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-voka-border">
                    <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Servicio</th>
                    <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Estado</th>
                    <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Tipo</th>
                    <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Servidor</th>
                    <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Puerto</th>
                    <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Tiempo activo</th>
                    <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Recursos</th>
                    <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredServices.map((service) => (
                    <tr key={service.id} className="border-b border-voka-border/50 hover:bg-voka-border/20">
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(service.status)}
                          <span className="text-voka-white font-montserrat">{service.name}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <Badge className={`${getStatusColor(service.status)} font-montserrat`}>
                          {service.status === "running"
                            ? "En ejecución"
                            : service.status === "stopped"
                              ? "Detenido"
                              : service.status === "warning"
                                ? "Advertencia"
                                : service.status === "restarting"
                                  ? "Reiniciando"
                                  : "Desconocido"}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-voka-white font-montserrat">{service.type}</td>
                      <td className="py-3 px-4 text-voka-white font-montserrat">{service.server}</td>
                      <td className="py-3 px-4 text-voka-white font-montserrat font-mono">{service.port}</td>
                      <td className="py-3 px-4 text-voka-white font-montserrat">{service.uptime}</td>
                      <td className="py-3 px-4">
                        <div className="text-xs text-voka-gray font-montserrat">
                          <div>CPU: {service.cpu}%</div>
                          <div>MEM: {service.memory}%</div>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex gap-1">
                          <Button
                            size="sm"
                            onClick={() => handleServiceAction(service.id, "start")}
                            disabled={service.status === "running" || service.status === "restarting"}
                            className="bg-voka-green hover:bg-voka-green/80 text-white font-montserrat"
                          >
                            <Play className="h-3 w-3" />
                          </Button>
                          <Button
                            size="sm"
                            onClick={() => handleServiceAction(service.id, "stop")}
                            disabled={service.status === "stopped" || service.status === "restarting"}
                            className="bg-voka-red hover:bg-voka-red/80 text-white font-montserrat"
                          >
                            <Square className="h-3 w-3" />
                          </Button>
                          <Button
                            size="sm"
                            onClick={() => handleServiceAction(service.id, "restart")}
                            disabled={service.status === "stopped" || service.status === "restarting"}
                            className="bg-voka-orange hover:bg-voka-orange/80 text-white font-montserrat"
                          >
                            <RotateCcw className="h-3 w-3" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

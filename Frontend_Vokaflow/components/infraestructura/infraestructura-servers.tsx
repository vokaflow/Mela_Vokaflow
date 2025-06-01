"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import {
  Server,
  HardDrive,
  Cpu,
  MemoryStickIcon as Memory,
  Clock,
  RefreshCw,
  Power,
  AlertTriangle,
  BarChart,
} from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { serverService } from "@/services/infrastructure-service"
import type { Server as ServerType } from "@/types/infrastructure"

export function InfraestructuraServers() {
  const [servers, setServers] = useState<ServerType[]>([])
  const [selectedServer, setSelectedServer] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)

  const fetchServers = async () => {
    try {
      setRefreshing(true)
      const data = await serverService.getServers()
      setServers(data)
      if (data.length > 0 && !selectedServer) {
        setSelectedServer(data[0].id)
      }
      setError(null)
    } catch (err) {
      setError("Error al cargar los servidores. Intente nuevamente.")
      console.error(err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchServers()
    // Configurar actualización automática cada 30 segundos
    const interval = setInterval(fetchServers, 30000)
    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case "online":
        return "bg-voka-green/20 text-voka-green border-voka-green"
      case "offline":
        return "bg-voka-red/20 text-voka-red border-voka-red"
      case "warning":
        return "bg-voka-orange/20 text-voka-orange border-voka-orange"
      case "maintenance":
        return "bg-voka-blue/20 text-voka-blue border-voka-blue"
      default:
        return "bg-voka-gray/20 text-voka-gray border-voka-gray"
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "online":
        return <div className="w-3 h-3 rounded-full bg-voka-green animate-pulse"></div>
      case "offline":
        return <div className="w-3 h-3 rounded-full bg-voka-red"></div>
      case "warning":
        return <AlertTriangle className="h-3 w-3 text-voka-orange" />
      case "maintenance":
        return <Clock className="h-3 w-3 text-voka-blue" />
      default:
        return <div className="w-3 h-3 rounded-full bg-voka-gray"></div>
    }
  }

  const currentServer = servers.find((s) => s.id === selectedServer)

  return (
    <div className="space-y-6">
      {/* Header con controles */}
      <div className="flex flex-col md:flex-row justify-between gap-4">
        <div className="flex-1">
          <Select value={selectedServer || ""} onValueChange={setSelectedServer}>
            <SelectTrigger className="w-full bg-voka-dark border-voka-border text-voka-white">
              <SelectValue placeholder="Seleccionar servidor" />
            </SelectTrigger>
            <SelectContent className="bg-voka-blue-black border-voka-border">
              {servers.map((server) => (
                <SelectItem key={server.id} value={server.id}>
                  <div className="flex items-center gap-2">
                    {getStatusIcon(server.status)}
                    <span>{server.name}</span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={fetchServers}
            disabled={refreshing}
            className="bg-voka-magenta hover:bg-voka-magenta/80 text-white font-montserrat"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? "animate-spin" : ""}`} />
            Actualizar
          </Button>
        </div>
      </div>

      {loading ? (
        <Card className="bg-voka-blue-black border-voka-border">
          <CardContent className="pt-6 flex justify-center items-center h-64">
            <div className="flex flex-col items-center gap-2">
              <RefreshCw className="h-8 w-8 text-voka-magenta animate-spin" />
              <p className="text-voka-gray font-montserrat">Cargando servidores...</p>
            </div>
          </CardContent>
        </Card>
      ) : error ? (
        <Card className="bg-voka-red/10 border-voka-red/30">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <AlertTriangle className="h-5 w-5 text-voka-red" />
              <p className="text-voka-red font-montserrat">{error}</p>
            </div>
          </CardContent>
        </Card>
      ) : currentServer ? (
        <>
          {/* Información del servidor */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="bg-voka-blue-black border-voka-border">
              <CardHeader>
                <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
                  <Server className="h-5 w-5 text-voka-magenta" />
                  Información del Servidor
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-voka-gray font-montserrat">Estado:</span>
                  <Badge className={`${getStatusColor(currentServer.status)} font-montserrat`}>
                    <div className="flex items-center gap-2">
                      {getStatusIcon(currentServer.status)}
                      <span>
                        {currentServer.status === "online"
                          ? "En línea"
                          : currentServer.status === "offline"
                            ? "Fuera de línea"
                            : currentServer.status === "warning"
                              ? "Advertencia"
                              : currentServer.status === "maintenance"
                                ? "Mantenimiento"
                                : "Desconocido"}
                      </span>
                    </div>
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-voka-gray font-montserrat">Nombre:</span>
                  <span className="text-voka-white font-montserrat">{currentServer.name}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-voka-gray font-montserrat">IP:</span>
                  <span className="text-voka-white font-montserrat font-mono">{currentServer.ip}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-voka-gray font-montserrat">Ubicación:</span>
                  <span className="text-voka-white font-montserrat">{currentServer.location}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-voka-gray font-montserrat">Tipo:</span>
                  <span className="text-voka-white font-montserrat">{currentServer.type}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-voka-gray font-montserrat">Tiempo activo:</span>
                  <span className="text-voka-white font-montserrat">{currentServer.uptime}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-voka-gray font-montserrat">Último reinicio:</span>
                  <span className="text-voka-white font-montserrat">{currentServer.lastReboot}</span>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-voka-blue-black border-voka-border">
              <CardHeader>
                <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
                  <BarChart className="h-5 w-5 text-voka-blue" />
                  Uso de Recursos
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                      <Cpu className="h-4 w-4 text-voka-magenta" />
                      <span className="text-voka-gray font-montserrat">CPU:</span>
                    </div>
                    <span className="text-voka-white font-montserrat">{currentServer.cpu}%</span>
                  </div>
                  <Progress value={currentServer.cpu} className="h-2" />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                      <Memory className="h-4 w-4 text-voka-blue" />
                      <span className="text-voka-gray font-montserrat">Memoria:</span>
                    </div>
                    <span className="text-voka-white font-montserrat">{currentServer.memory}%</span>
                  </div>
                  <Progress value={currentServer.memory} className="h-2" />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                      <HardDrive className="h-4 w-4 text-voka-green" />
                      <span className="text-voka-gray font-montserrat">Disco:</span>
                    </div>
                    <span className="text-voka-white font-montserrat">{currentServer.disk}%</span>
                  </div>
                  <Progress value={currentServer.disk} className="h-2" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Servicios del servidor */}
          <Card className="bg-voka-blue-black border-voka-border">
            <CardHeader>
              <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
                <Server className="h-5 w-5 text-voka-yellow" />
                Servicios Activos
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {currentServer.services.map((service, index) => (
                  <div
                    key={index}
                    className="bg-voka-dark rounded-lg p-3 border border-voka-border flex items-center gap-3"
                  >
                    <div className="w-2 h-2 rounded-full bg-voka-green animate-pulse"></div>
                    <span className="text-voka-white font-montserrat">{service}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Controles del servidor */}
          <Card className="bg-voka-blue-black border-voka-border">
            <CardHeader>
              <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
                <Power className="h-5 w-5 text-voka-red" />
                Control del Servidor
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-4">
                <Button
                  className="bg-voka-orange hover:bg-voka-orange/80 text-white font-montserrat"
                  disabled={currentServer.status === "offline"}
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Reiniciar Servidor
                </Button>
                <Button
                  className="bg-voka-red hover:bg-voka-red/80 text-white font-montserrat"
                  disabled={currentServer.status === "offline"}
                >
                  <Power className="h-4 w-4 mr-2" />
                  Apagar Servidor
                </Button>
                <Button
                  variant="outline"
                  className="border-voka-border text-voka-gray hover:text-voka-white font-montserrat"
                >
                  <BarChart className="h-4 w-4 mr-2" />
                  Ver Métricas Detalladas
                </Button>
              </div>
            </CardContent>
          </Card>
        </>
      ) : (
        <Card className="bg-voka-blue-black border-voka-border">
          <CardContent className="pt-6 flex justify-center items-center h-64">
            <p className="text-voka-gray font-montserrat">No hay servidores disponibles</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

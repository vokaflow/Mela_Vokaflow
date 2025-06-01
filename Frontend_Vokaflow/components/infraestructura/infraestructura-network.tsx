"use client"

import { useState, useEffect, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Network, RefreshCw, AlertTriangle, Wifi, Router, Shield, Server, Activity } from "lucide-react"
import { networkService } from "@/services/infrastructure-service"
import type { NetworkDevice, NetworkConnection } from "@/types/infrastructure"

export function InfraestructuraNetwork() {
  const [devices, setDevices] = useState<NetworkDevice[]>([])
  const [connections, setConnections] = useState<NetworkConnection[]>([])
  const [selectedDevice, setSelectedDevice] = useState<NetworkDevice | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  const fetchNetworkData = async () => {
    try {
      setRefreshing(true)
      const topology = await networkService.getTopology()
      setDevices(topology.devices)
      setConnections(topology.connections)
      setError(null)
    } catch (err) {
      setError("Error al cargar los datos de red. Intente nuevamente.")
      console.error(err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchNetworkData()
    // Configurar actualización automática cada 30 segundos
    const interval = setInterval(fetchNetworkData, 30000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (devices.length > 0 && connections.length > 0) {
      drawNetworkTopology()
    }
  }, [devices, connections])

  const getDeviceIcon = (type: string) => {
    switch (type) {
      case "router":
        return <Router className="h-5 w-5 text-voka-blue" />
      case "switch":
        return <Network className="h-5 w-5 text-voka-green" />
      case "firewall":
        return <Shield className="h-5 w-5 text-voka-red" />
      case "loadbalancer":
        return <Activity className="h-5 w-5 text-voka-yellow" />
      case "gateway":
        return <Wifi className="h-5 w-5 text-voka-magenta" />
      default:
        return <Server className="h-5 w-5 text-voka-gray" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "online":
        return "bg-voka-green/20 text-voka-green border-voka-green"
      case "offline":
        return "bg-voka-red/20 text-voka-red border-voka-red"
      case "warning":
        return "bg-voka-orange/20 text-voka-orange border-voka-orange"
      default:
        return "bg-voka-gray/20 text-voka-gray border-voka-gray"
    }
  }

  const getConnectionColor = (status: string) => {
    switch (status) {
      case "active":
        return "#35FF83" // voka-green
      case "inactive":
        return "#FF3366" // voka-red
      case "degraded":
        return "#FFA700" // voka-orange
      default:
        return "#A0A0B2" // voka-gray
    }
  }

  const drawNetworkTopology = () => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Configurar el tamaño del canvas
    const container = canvas.parentElement
    if (container) {
      canvas.width = container.clientWidth
      canvas.height = 500
    }

    // Limpiar el canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Crear un mapa de posiciones para los dispositivos
    const positions: Record<string, { x: number; y: number }> = {}
    const radius = Math.min(canvas.width, canvas.height) * 0.35
    const centerX = canvas.width / 2
    const centerY = canvas.height / 2

    // Posicionar los dispositivos en un círculo
    devices.forEach((device, index) => {
      const angle = (index / devices.length) * Math.PI * 2
      const x = centerX + radius * Math.cos(angle)
      const y = centerY + radius * Math.sin(angle)
      positions[device.id] = { x, y }
    })

    // Dibujar las conexiones
    connections.forEach((connection) => {
      const source = positions[connection.source]
      const target = positions[connection.target]

      if (source && target) {
        ctx.beginPath()
        ctx.moveTo(source.x, source.y)
        ctx.lineTo(target.x, target.y)
        ctx.strokeStyle = getConnectionColor(connection.status)
        ctx.lineWidth = 2

        // Línea punteada para conexiones degradadas
        if (connection.status === "degraded") {
          ctx.setLineDash([5, 3])
        } else {
          ctx.setLineDash([])
        }

        ctx.stroke()

        // Dibujar la latencia en el medio de la conexión
        const midX = (source.x + target.x) / 2
        const midY = (source.y + target.y) / 2

        ctx.fillStyle = "#F8F8F8" // voka-white
        ctx.font = "10px Montserrat"
        ctx.fillText(`${connection.latency}ms`, midX, midY)
      }
    })

    // Dibujar los dispositivos
    devices.forEach((device) => {
      const pos = positions[device.id]
      if (!pos) return

      // Círculo exterior (estado)
      ctx.beginPath()
      ctx.arc(pos.x, pos.y, 25, 0, Math.PI * 2)

      let glowColor
      switch (device.status) {
        case "online":
          glowColor = "#35FF83"
          break // voka-green
        case "offline":
          glowColor = "#FF3366"
          break // voka-red
        case "warning":
          glowColor = "#FFA700"
          break // voka-orange
        default:
          glowColor = "#A0A0B2" // voka-gray
      }

      // Añadir resplandor según el estado
      ctx.shadowColor = glowColor
      ctx.shadowBlur = 10
      ctx.fillStyle = "#19192A" // voka-blue-black
      ctx.fill()
      ctx.shadowBlur = 0

      // Borde según el estado
      ctx.strokeStyle = glowColor
      ctx.lineWidth = 2
      ctx.stroke()

      // Dibujar icono según el tipo (simplificado con texto)
      ctx.fillStyle = glowColor
      ctx.font = "bold 12px Montserrat"
      ctx.textAlign = "center"
      ctx.textBaseline = "middle"

      let icon
      switch (device.type) {
        case "router":
          icon = "R"
          break
        case "switch":
          icon = "S"
          break
        case "firewall":
          icon = "F"
          break
        case "loadbalancer":
          icon = "LB"
          break
        case "gateway":
          icon = "GW"
          break
        default:
          icon = "?"
      }

      ctx.fillText(icon, pos.x, pos.y)

      // Nombre del dispositivo
      ctx.fillStyle = "#F8F8F8" // voka-white
      ctx.font = "10px Montserrat"
      ctx.fillText(device.name, pos.x, pos.y + 35)

      // Hacer que los dispositivos sean interactivos
      canvas.onclick = (e) => {
        const rect = canvas.getBoundingClientRect()
        const x = e.clientX - rect.left
        const y = e.clientY - rect.top

        devices.forEach((d) => {
          const pos = positions[d.id]
          if (pos) {
            const distance = Math.sqrt(Math.pow(x - pos.x, 2) + Math.pow(y - pos.y, 2))
            if (distance <= 25) {
              setSelectedDevice(d)
            }
          }
        })
      }
    })
  }

  return (
    <div className="space-y-6">
      {/* Header con controles */}
      <div className="flex justify-end">
        <Button
          onClick={fetchNetworkData}
          disabled={refreshing}
          className="bg-voka-magenta hover:bg-voka-magenta/80 text-white font-montserrat"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? "animate-spin" : ""}`} />
          Actualizar
        </Button>
      </div>

      {loading ? (
        <Card className="bg-voka-blue-black border-voka-border">
          <CardContent className="pt-6 flex justify-center items-center h-64">
            <div className="flex flex-col items-center gap-2">
              <RefreshCw className="h-8 w-8 text-voka-magenta animate-spin" />
              <p className="text-voka-gray font-montserrat">Cargando datos de red...</p>
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
      ) : (
        <>
          {/* Visualización de la topología de red */}
          <Card className="bg-voka-blue-black border-voka-border">
            <CardHeader>
              <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
                <Network className="h-5 w-5 text-voka-magenta" />
                Topología de Red
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="relative w-full h-[500px] bg-voka-dark rounded-lg border border-voka-border">
                <canvas ref={canvasRef} className="w-full h-full"></canvas>
                <div className="absolute bottom-4 right-4 bg-voka-blue-black p-2 rounded-lg border border-voka-border">
                  <div className="text-xs text-voka-white font-montserrat mb-1">Leyenda:</div>
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-3 h-1 bg-voka-green"></div>
                    <span className="text-xs text-voka-gray font-montserrat">Activo</span>
                  </div>
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-3 h-1 bg-voka-orange"></div>
                    <span className="text-xs text-voka-gray font-montserrat">Degradado</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-1 bg-voka-red"></div>
                    <span className="text-xs text-voka-gray font-montserrat">Inactivo</span>
                  </div>
                </div>
              </div>
              <div className="mt-4 text-center text-voka-gray font-montserrat text-sm">
                Haga clic en un dispositivo para ver sus detalles
              </div>
            </CardContent>
          </Card>

          {/* Detalles del dispositivo seleccionado */}
          {selectedDevice && (
            <Card className="bg-voka-blue-black border-voka-border">
              <CardHeader>
                <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
                  {getDeviceIcon(selectedDevice.type)}
                  Detalles del Dispositivo: {selectedDevice.name}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-voka-gray font-montserrat">Estado:</span>
                      <Badge className={`${getStatusColor(selectedDevice.status)} font-montserrat`}>
                        {selectedDevice.status === "online"
                          ? "En línea"
                          : selectedDevice.status === "offline"
                            ? "Fuera de línea"
                            : selectedDevice.status === "warning"
                              ? "Advertencia"
                              : "Desconocido"}
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-voka-gray font-montserrat">Tipo:</span>
                      <span className="text-voka-white font-montserrat">{selectedDevice.type}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-voka-gray font-montserrat">IP:</span>
                      <span className="text-voka-white font-montserrat font-mono">{selectedDevice.ip}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-voka-gray font-montserrat">Ubicación:</span>
                      <span className="text-voka-white font-montserrat">{selectedDevice.location}</span>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-voka-gray font-montserrat">Rendimiento:</span>
                      <span className="text-voka-white font-montserrat">{selectedDevice.throughput} Mbps</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-voka-gray font-montserrat">Conexiones:</span>
                      <span className="text-voka-white font-montserrat">{selectedDevice.connections}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-voka-gray font-montserrat">Latencia:</span>
                      <span className="text-voka-white font-montserrat">{selectedDevice.latency} ms</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Lista de dispositivos */}
          <Card className="bg-voka-blue-black border-voka-border">
            <CardHeader>
              <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
                <Server className="h-5 w-5 text-voka-blue" />
                Dispositivos de Red
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-voka-border">
                      <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Nombre</th>
                      <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Tipo</th>
                      <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Estado</th>
                      <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">IP</th>
                      <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Latencia</th>
                    </tr>
                  </thead>
                  <tbody>
                    {devices.map((device) => (
                      <tr
                        key={device.id}
                        className={`border-b border-voka-border/50 hover:bg-voka-border/20 cursor-pointer ${selectedDevice?.id === device.id ? "bg-voka-border/30" : ""}`}
                        onClick={() => setSelectedDevice(device)}
                      >
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            {getDeviceIcon(device.type)}
                            <span className="text-voka-white font-montserrat">{device.name}</span>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-voka-white font-montserrat capitalize">{device.type}</td>
                        <td className="py-3 px-4">
                          <Badge className={`${getStatusColor(device.status)} font-montserrat`}>
                            {device.status === "online"
                              ? "En línea"
                              : device.status === "offline"
                                ? "Fuera de línea"
                                : device.status === "warning"
                                  ? "Advertencia"
                                  : "Desconocido"}
                          </Badge>
                        </td>
                        <td className="py-3 px-4 text-voka-white font-montserrat font-mono">{device.ip}</td>
                        <td className="py-3 px-4 text-voka-white font-montserrat">{device.latency} ms</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}

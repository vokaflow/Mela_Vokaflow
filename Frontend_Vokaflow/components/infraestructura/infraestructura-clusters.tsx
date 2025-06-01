"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Layers, RefreshCw, AlertTriangle, Server, Activity, RotateCcw } from "lucide-react"
import { clusterService } from "@/services/infrastructure-service"
import type { Cluster } from "@/types/infrastructure"

export function InfraestructuraClusters() {
  const [clusters, setClusters] = useState<Cluster[]>([])
  const [selectedCluster, setSelectedCluster] = useState<Cluster | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)

  const fetchClusters = async () => {
    try {
      setRefreshing(true)
      const data = await clusterService.getClusters()
      setClusters(data)
      if (data.length > 0 && !selectedCluster) {
        setSelectedCluster(data[0])
      }
      setError(null)
    } catch (err) {
      setError("Error al cargar los clusters. Intente nuevamente.")
      console.error(err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchClusters()
    // Configurar actualización automática cada 30 segundos
    const interval = setInterval(fetchClusters, 30000)
    return () => clearInterval(interval)
  }, [])

  const handleFailover = async (clusterId: string) => {
    try {
      await clusterService.failoverCluster(clusterId)
      fetchClusters()
    } catch (err) {
      console.error("Error al realizar failover:", err)
    }
  }

  const getClusterStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "bg-voka-green/20 text-voka-green border-voka-green"
      case "degraded":
        return "bg-voka-orange/20 text-voka-orange border-voka-orange"
      case "critical":
        return "bg-voka-red/20 text-voka-red border-voka-red"
      default:
        return "bg-voka-gray/20 text-voka-gray border-voka-gray"
    }
  }

  const getNodeStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-voka-green/20 text-voka-green border-voka-green"
      case "standby":
        return "bg-voka-blue/20 text-voka-blue border-voka-blue"
      case "failed":
        return "bg-voka-red/20 text-voka-red border-voka-red"
      default:
        return "bg-voka-gray/20 text-voka-gray border-voka-gray"
    }
  }

  const getRoleColor = (role: string) => {
    switch (role) {
      case "primary":
        return "bg-voka-magenta/20 text-voka-magenta border-voka-magenta"
      case "secondary":
        return "bg-voka-blue/20 text-voka-blue border-voka-blue"
      case "arbiter":
        return "bg-voka-yellow/20 text-voka-yellow border-voka-yellow"
      default:
        return "bg-voka-gray/20 text-voka-gray border-voka-gray"
    }
  }

  const getNodeIcon = (status: string) => {
    switch (status) {
      case "active":
        return <div className="w-3 h-3 rounded-full bg-voka-green animate-pulse"></div>
      case "standby":
        return <div className="w-3 h-3 rounded-full bg-voka-blue"></div>
      case "failed":
        return <AlertTriangle className="h-3 w-3 text-voka-red" />
      default:
        return <div className="w-3 h-3 rounded-full bg-voka-gray"></div>
    }
  }

  // Contar clusters por estado
  const healthyCount = clusters.filter((c) => c.status === "healthy").length
  const degradedCount = clusters.filter((c) => c.status === "degraded").length
  const criticalCount = clusters.filter((c) => c.status === "critical").length

  return (
    <div className="space-y-6">
      {/* Resumen de clusters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-voka-blue-black border-voka-border">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-voka-green/20 flex items-center justify-center">
                <Layers className="h-5 w-5 text-voka-green" />
              </div>
              <div>
                <div className="text-2xl font-bold text-voka-green font-montserrat">{healthyCount}</div>
                <p className="text-voka-gray font-montserrat text-sm">Saludables</p>
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
                <div className="text-2xl font-bold text-voka-orange font-montserrat">{degradedCount}</div>
                <p className="text-voka-gray font-montserrat text-sm">Degradados</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-voka-red/20 flex items-center justify-center">
                <AlertTriangle className="h-5 w-5 text-voka-red" />
              </div>
              <div>
                <div className="text-2xl font-bold text-voka-red font-montserrat">{criticalCount}</div>
                <p className="text-voka-gray font-montserrat text-sm">Críticos</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Controles */}
      <div className="flex justify-end">
        <Button
          onClick={fetchClusters}
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
              <p className="text-voka-gray font-montserrat">Cargando clusters...</p>
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
          {/* Lista de clusters */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {clusters.map((cluster) => (
              <Card
                key={cluster.id}
                className={`bg-voka-blue-black border-voka-border cursor-pointer transition-colors ${
                  selectedCluster?.id === cluster.id ? "border-voka-magenta" : "hover:border-voka-magenta/50"
                }`}
                onClick={() => setSelectedCluster(cluster)}
              >
                <CardHeader>
                  <CardTitle className="text-voka-white font-montserrat flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Layers className="h-5 w-5 text-voka-magenta" />
                      {cluster.name}
                    </div>
                    <Badge className={`${getClusterStatusColor(cluster.status)} font-montserrat`}>
                      {cluster.status === "healthy"
                        ? "Saludable"
                        : cluster.status === "degraded"
                          ? "Degradado"
                          : cluster.status === "critical"
                            ? "Crítico"
                            : "Desconocido"}
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-voka-gray font-montserrat">Tipo:</span>
                      <span className="text-voka-white font-montserrat">{cluster.type}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-voka-gray font-montserrat">Nodos:</span>
                      <span className="text-voka-white font-montserrat">{cluster.nodes.length}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-voka-gray font-montserrat">Servicios:</span>
                      <span className="text-voka-white font-montserrat">{cluster.services.length}</span>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleFailover(cluster.id)
                        }}
                        className="bg-voka-orange hover:bg-voka-orange/80 text-white font-montserrat"
                      >
                        <RotateCcw className="h-3 w-3 mr-1" />
                        Failover
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Detalles del cluster seleccionado */}
          {selectedCluster && (
            <Card className="bg-voka-blue-black border-voka-border">
              <CardHeader>
                <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
                  <Server className="h-5 w-5 text-voka-blue" />
                  Nodos del Cluster: {selectedCluster.name}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-voka-border">
                        <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Nodo</th>
                        <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Estado</th>
                        <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Rol</th>
                        <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">IP</th>
                        <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">CPU</th>
                        <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Memoria</th>
                        <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">
                          Último Heartbeat
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedCluster.nodes.map((node) => (
                        <tr key={node.id} className="border-b border-voka-border/50 hover:bg-voka-border/20">
                          <td className="py-3 px-4">
                            <div className="flex items-center gap-2">
                              {getNodeIcon(node.status)}
                              <span className="text-voka-white font-montserrat">{node.name}</span>
                            </div>
                          </td>
                          <td className="py-3 px-4">
                            <Badge className={`${getNodeStatusColor(node.status)} font-montserrat`}>
                              {node.status === "active"
                                ? "Activo"
                                : node.status === "standby"
                                  ? "En espera"
                                  : node.status === "failed"
                                    ? "Fallido"
                                    : "Desconocido"}
                            </Badge>
                          </td>
                          <td className="py-3 px-4">
                            <Badge className={`${getRoleColor(node.role)} font-montserrat`}>
                              {node.role === "primary"
                                ? "Primario"
                                : node.role === "secondary"
                                  ? "Secundario"
                                  : node.role === "arbiter"
                                    ? "Árbitro"
                                    : node.role}
                            </Badge>
                          </td>
                          <td className="py-3 px-4 text-voka-white font-montserrat font-mono">{node.ip}</td>
                          <td className="py-3 px-4">
                            <div className="space-y-1">
                              <div className="text-voka-white font-montserrat text-sm">{node.cpu}%</div>
                              <Progress value={node.cpu} className="h-1" />
                            </div>
                          </td>
                          <td className="py-3 px-4">
                            <div className="space-y-1">
                              <div className="text-voka-white font-montserrat text-sm">{node.memory}%</div>
                              <Progress value={node.memory} className="h-1" />
                            </div>
                          </td>
                          <td className="py-3 px-4 text-voka-white font-montserrat text-sm">{node.lastHeartbeat}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Servicios del cluster */}
                <div className="mt-6">
                  <h4 className="text-voka-white font-montserrat font-semibold mb-3">Servicios del Cluster</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {selectedCluster.services.map((service, index) => (
                      <div
                        key={index}
                        className="bg-voka-dark rounded-lg p-3 border border-voka-border flex items-center gap-3"
                      >
                        <Activity className="h-4 w-4 text-voka-green" />
                        <span className="text-voka-white font-montserrat">{service}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  )
}

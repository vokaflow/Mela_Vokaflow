"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { HardDrive, RefreshCw, Play, Square, Download, AlertTriangle, Clock } from "lucide-react"
import { backupService } from "@/services/infrastructure-service"
import type { Backup } from "@/types/infrastructure"

export function InfraestructuraBackup() {
  const [backups, setBackups] = useState<Backup[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)
  const [statusFilter, setStatusFilter] = useState("all")

  const fetchBackups = async () => {
    try {
      setRefreshing(true)
      const data = await backupService.getBackups()
      setBackups(data)
      setError(null)
    } catch (err) {
      setError("Error al cargar los backups. Intente nuevamente.")
      console.error(err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchBackups()
    // Configurar actualización automática cada 30 segundos
    const interval = setInterval(fetchBackups, 30000)
    return () => clearInterval(interval)
  }, [])

  const handleCancelBackup = async (id: string) => {
    try {
      await backupService.cancelBackup(id)
      fetchBackups()
    } catch (err) {
      console.error("Error al cancelar el backup:", err)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-voka-green/20 text-voka-green border-voka-green"
      case "in-progress":
        return "bg-voka-blue/20 text-voka-blue border-voka-blue"
      case "failed":
        return "bg-voka-red/20 text-voka-red border-voka-red"
      case "scheduled":
        return "bg-voka-yellow/20 text-voka-yellow border-voka-yellow"
      default:
        return "bg-voka-gray/20 text-voka-gray border-voka-gray"
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case "full":
        return "bg-voka-magenta/20 text-voka-magenta border-voka-magenta"
      case "incremental":
        return "bg-voka-blue/20 text-voka-blue border-voka-blue"
      case "differential":
        return "bg-voka-orange/20 text-voka-orange border-voka-orange"
      default:
        return "bg-voka-gray/20 text-voka-gray border-voka-gray"
    }
  }

  const formatSize = (bytes: number) => {
    const sizes = ["B", "KB", "MB", "GB", "TB"]
    if (bytes === 0) return "0 B"
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return Math.round((bytes / Math.pow(1024, i)) * 100) / 100 + " " + sizes[i]
  }

  // Filtrar backups
  const filteredBackups = backups.filter((backup) => {
    return statusFilter === "all" || backup.status === statusFilter
  })

  // Contar backups por estado
  const completedCount = backups.filter((b) => b.status === "completed").length
  const inProgressCount = backups.filter((b) => b.status === "in-progress").length
  const failedCount = backups.filter((b) => b.status === "failed").length
  const scheduledCount = backups.filter((b) => b.status === "scheduled").length

  return (
    <div className="space-y-6">
      {/* Resumen de backups */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-voka-blue-black border-voka-border">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-voka-green/20 flex items-center justify-center">
                <HardDrive className="h-5 w-5 text-voka-green" />
              </div>
              <div>
                <div className="text-2xl font-bold text-voka-green font-montserrat">{completedCount}</div>
                <p className="text-voka-gray font-montserrat text-sm">Completados</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-voka-blue/20 flex items-center justify-center">
                <RefreshCw className="h-5 w-5 text-voka-blue animate-spin" />
              </div>
              <div>
                <div className="text-2xl font-bold text-voka-blue font-montserrat">{inProgressCount}</div>
                <p className="text-voka-gray font-montserrat text-sm">En progreso</p>
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
                <div className="text-2xl font-bold text-voka-red font-montserrat">{failedCount}</div>
                <p className="text-voka-gray font-montserrat text-sm">Fallidos</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-voka-yellow/20 flex items-center justify-center">
                <Clock className="h-5 w-5 text-voka-yellow" />
              </div>
              <div>
                <div className="text-2xl font-bold text-voka-yellow font-montserrat">{scheduledCount}</div>
                <p className="text-voka-gray font-montserrat text-sm">Programados</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Controles */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4 justify-between">
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full md:w-48 bg-voka-dark border-voka-border text-voka-white">
                <SelectValue placeholder="Filtrar por estado" />
              </SelectTrigger>
              <SelectContent className="bg-voka-blue-black border-voka-border">
                <SelectItem value="all">Todos los estados</SelectItem>
                <SelectItem value="completed">Completados</SelectItem>
                <SelectItem value="in-progress">En progreso</SelectItem>
                <SelectItem value="failed">Fallidos</SelectItem>
                <SelectItem value="scheduled">Programados</SelectItem>
              </SelectContent>
            </Select>
            <div className="flex gap-2">
              <Button className="bg-voka-magenta hover:bg-voka-magenta/80 text-white font-montserrat">
                <Play className="h-4 w-4 mr-2" />
                Nuevo Backup
              </Button>
              <Button
                onClick={fetchBackups}
                disabled={refreshing}
                variant="outline"
                className="border-voka-border text-voka-gray hover:text-voka-white font-montserrat"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? "animate-spin" : ""}`} />
                Actualizar
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Lista de backups */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader>
          <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
            <HardDrive className="h-5 w-5 text-voka-magenta" />
            Backups del Sistema ({filteredBackups.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="flex flex-col items-center gap-2">
                <RefreshCw className="h-8 w-8 text-voka-magenta animate-spin" />
                <p className="text-voka-gray font-montserrat">Cargando backups...</p>
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
            <div className="space-y-4">
              {filteredBackups.map((backup) => (
                <div key={backup.id} className="p-4 bg-voka-dark rounded-lg border border-voka-border">
                  <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-voka-white font-montserrat font-semibold">{backup.name}</h3>
                        <Badge className={`${getStatusColor(backup.status)} font-montserrat`}>
                          {backup.status === "completed"
                            ? "Completado"
                            : backup.status === "in-progress"
                              ? "En progreso"
                              : backup.status === "failed"
                                ? "Fallido"
                                : backup.status === "scheduled"
                                  ? "Programado"
                                  : "Desconocido"}
                        </Badge>
                        <Badge className={`${getTypeColor(backup.type)} font-montserrat`}>
                          {backup.type === "full"
                            ? "Completo"
                            : backup.type === "incremental"
                              ? "Incremental"
                              : backup.type === "differential"
                                ? "Diferencial"
                                : backup.type}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-voka-gray font-montserrat">Origen:</span>
                          <p className="text-voka-white font-montserrat">{backup.source}</p>
                        </div>
                        <div>
                          <span className="text-voka-gray font-montserrat">Destino:</span>
                          <p className="text-voka-white font-montserrat">{backup.destination}</p>
                        </div>
                        <div>
                          <span className="text-voka-gray font-montserrat">Tamaño:</span>
                          <p className="text-voka-white font-montserrat">{formatSize(backup.size)}</p>
                        </div>
                        <div>
                          <span className="text-voka-gray font-montserrat">Inicio:</span>
                          <p className="text-voka-white font-montserrat">{backup.startTime}</p>
                        </div>
                      </div>
                      {backup.status === "in-progress" && (
                        <div className="mt-3">
                          <Progress value={Math.random() * 100} className="h-2" />
                          <p className="text-voka-gray font-montserrat text-xs mt-1">Progreso estimado</p>
                        </div>
                      )}
                    </div>
                    <div className="flex gap-2 lg:flex-shrink-0">
                      {backup.status === "in-progress" && (
                        <Button
                          size="sm"
                          onClick={() => handleCancelBackup(backup.id)}
                          className="bg-voka-red hover:bg-voka-red/80 text-white font-montserrat"
                        >
                          <Square className="h-3 w-3 mr-1" />
                          Cancelar
                        </Button>
                      )}
                      {backup.status === "completed" && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="border-voka-border text-voka-gray hover:text-voka-white font-montserrat"
                        >
                          <Download className="h-3 w-3 mr-1" />
                          Descargar
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="outline"
                        className="border-voka-border text-voka-gray hover:text-voka-white font-montserrat"
                      >
                        Ver detalles
                      </Button>
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

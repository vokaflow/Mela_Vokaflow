"use client"

import { useState, useEffect, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { FileText, RefreshCw, Search, Download, Play, Pause, AlertTriangle } from "lucide-react"
import { logService } from "@/services/infrastructure-service"
import type { LogEntry } from "@/types/infrastructure"

export function InfraestructuraLogs() {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)
  const [searchTerm, setSearchTerm] = useState("")
  const [levelFilter, setLevelFilter] = useState("all")
  const [sourceFilter, setSourceFilter] = useState("all")
  const [limit, setLimit] = useState("100")
  const [autoRefresh, setAutoRefresh] = useState(false)
  const [autoScroll, setAutoScroll] = useState(true)
  const logsEndRef = useRef<HTMLDivElement>(null)

  const fetchLogs = async () => {
    try {
      setRefreshing(true)
      const level = levelFilter !== "all" ? levelFilter : undefined
      const data = await logService.getLogs(Number.parseInt(limit), level)
      setLogs(data)
      setError(null)
    } catch (err) {
      setError("Error al cargar los logs. Intente nuevamente.")
      console.error(err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchLogs()
  }, [levelFilter, limit])

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null

    if (autoRefresh) {
      interval = setInterval(fetchLogs, 5000)
    }

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [autoRefresh, levelFilter, limit])

  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [logs, autoScroll])

  const getLevelColor = (level: string) => {
    switch (level) {
      case "error":
        return "bg-voka-red/20 text-voka-red border-voka-red"
      case "warning":
        return "bg-voka-orange/20 text-voka-orange border-voka-orange"
      case "info":
        return "bg-voka-blue/20 text-voka-blue border-voka-blue"
      case "debug":
        return "bg-voka-gray/20 text-voka-gray border-voka-gray"
      default:
        return "bg-voka-gray/20 text-voka-gray border-voka-gray"
    }
  }

  const getLevelTextColor = (level: string) => {
    switch (level) {
      case "error":
        return "text-voka-red"
      case "warning":
        return "text-voka-orange"
      case "info":
        return "text-voka-blue"
      case "debug":
        return "text-voka-gray"
      default:
        return "text-voka-white"
    }
  }

  // Filtrar logs
  const filteredLogs = logs.filter((log) => {
    const matchesSearch =
      log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.source.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesSource = sourceFilter === "all" || log.source === sourceFilter

    return matchesSearch && matchesSource
  })

  // Obtener fuentes únicas
  const uniqueSources = Array.from(new Set(logs.map((log) => log.source)))

  const exportLogs = () => {
    const logContent = filteredLogs
      .map((log) => `[${log.timestamp}] ${log.level.toUpperCase()} - ${log.source} - ${log.message}`)
      .join("\n")

    const blob = new Blob([logContent], { type: "text/plain" })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `infrastructure_logs_${new Date().toISOString().split("T")[0]}.log`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      {/* Controles */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardContent className="pt-6">
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-voka-gray" />
                <Input
                  placeholder="Buscar en logs..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-voka-dark border-voka-border text-voka-white placeholder:text-voka-gray"
                />
              </div>
            </div>
            <Select value={levelFilter} onValueChange={setLevelFilter}>
              <SelectTrigger className="w-full lg:w-48 bg-voka-dark border-voka-border text-voka-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-voka-blue-black border-voka-border">
                <SelectItem value="all">Todos los niveles</SelectItem>
                <SelectItem value="error">Error</SelectItem>
                <SelectItem value="warning">Warning</SelectItem>
                <SelectItem value="info">Info</SelectItem>
                <SelectItem value="debug">Debug</SelectItem>
              </SelectContent>
            </Select>
            <Select value={sourceFilter} onValueChange={setSourceFilter}>
              <SelectTrigger className="w-full lg:w-48 bg-voka-dark border-voka-border text-voka-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-voka-blue-black border-voka-border">
                <SelectItem value="all">Todas las fuentes</SelectItem>
                {uniqueSources.map((source) => (
                  <SelectItem key={source} value={source}>
                    {source}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={limit} onValueChange={setLimit}>
              <SelectTrigger className="w-full lg:w-32 bg-voka-dark border-voka-border text-voka-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-voka-blue-black border-voka-border">
                <SelectItem value="50">50</SelectItem>
                <SelectItem value="100">100</SelectItem>
                <SelectItem value="500">500</SelectItem>
                <SelectItem value="1000">1000</SelectItem>
              </SelectContent>
            </Select>
            <div className="flex gap-2">
              <Button
                onClick={() => setAutoRefresh(!autoRefresh)}
                variant={autoRefresh ? "default" : "outline"}
                className={
                  autoRefresh
                    ? "bg-voka-green hover:bg-voka-green/80 text-white"
                    : "border-voka-border text-voka-gray hover:text-voka-white"
                }
              >
                {autoRefresh ? <Pause className="h-4 w-4 mr-2" /> : <Play className="h-4 w-4 mr-2" />}
                {autoRefresh ? "Pausar" : "Auto"}
              </Button>
              <Button
                onClick={fetchLogs}
                disabled={refreshing}
                className="bg-voka-magenta hover:bg-voka-magenta/80 text-white font-montserrat"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? "animate-spin" : ""}`} />
                Actualizar
              </Button>
              <Button
                onClick={exportLogs}
                variant="outline"
                className="border-voka-border text-voka-gray hover:text-voka-white font-montserrat"
              >
                <Download className="h-4 w-4 mr-2" />
                Exportar
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Visor de logs */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
              <FileText className="h-5 w-5 text-voka-magenta" />
              Logs del Sistema
              {autoRefresh && (
                <Badge className="bg-voka-green/20 text-voka-green border-voka-green font-montserrat animate-pulse">
                  🔴 LIVE
                </Badge>
              )}
            </CardTitle>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="text-voka-gray font-montserrat text-sm">Auto-scroll:</span>
                <Button
                  size="sm"
                  variant={autoScroll ? "default" : "outline"}
                  className={
                    autoScroll
                      ? "bg-voka-blue hover:bg-voka-blue/80 text-white"
                      : "border-voka-border text-voka-gray hover:text-voka-white"
                  }
                  onClick={() => setAutoScroll(!autoScroll)}
                >
                  {autoScroll ? "ON" : "OFF"}
                </Button>
              </div>
              <span className="text-voka-gray font-montserrat text-sm">{filteredLogs.length} entradas</span>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="flex flex-col items-center gap-2">
                <RefreshCw className="h-8 w-8 text-voka-magenta animate-spin" />
                <p className="text-voka-gray font-montserrat">Cargando logs...</p>
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
            <div className="bg-voka-dark rounded-lg p-4 h-96 overflow-y-auto border border-voka-border font-mono text-sm">
              {filteredLogs.map((log) => (
                <div key={log.id} className="flex items-start gap-3 mb-2 hover:bg-voka-border/20 p-1 rounded">
                  <span className="text-voka-gray font-mono text-xs whitespace-nowrap">[{log.timestamp}]</span>
                  <Badge className={`${getLevelColor(log.level)} font-montserrat text-xs`}>
                    {log.level.toUpperCase()}
                  </Badge>
                  <span className="text-voka-blue font-mono text-xs">{log.source}</span>
                  <span className="text-voka-gray">-</span>
                  <span className={`${getLevelTextColor(log.level)} flex-1`}>{log.message}</span>
                </div>
              ))}
              <div ref={logsEndRef} />
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

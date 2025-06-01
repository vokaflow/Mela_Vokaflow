"use client"

import { useState, useEffect, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { FileText, Pause, Play, Square, Download, Search } from "lucide-react"

interface LogEntry {
  id: number
  timestamp: string
  level: "INFO" | "WARN" | "ERROR" | "DEBUG"
  component: string
  message: string
}

export function TerminalLogs() {
  const [logs, setLogs] = useState<LogEntry[]>([
    {
      id: 1,
      timestamp: "23:52:45",
      level: "INFO",
      component: "vokaflow-backend",
      message: "Health check requested",
    },
    {
      id: 2,
      timestamp: "23:52:42",
      level: "INFO",
      component: "src.backend.routers.vicky",
      message: "Processing request",
    },
    {
      id: 3,
      timestamp: "23:52:40",
      level: "DEBUG",
      component: "databases",
      message: "Query executed in 0.003s",
    },
    {
      id: 4,
      timestamp: "23:52:38",
      level: "WARN",
      component: "monitoring",
      message: "High CPU usage detected: 67%",
    },
    {
      id: 5,
      timestamp: "23:52:35",
      level: "INFO",
      component: "system",
      message: "User authentication successful",
    },
    {
      id: 6,
      timestamp: "23:52:33",
      level: "ERROR",
      component: "translate",
      message: "Rate limit exceeded for user",
    },
    {
      id: 7,
      timestamp: "23:52:30",
      level: "INFO",
      component: "api",
      message: "New API key generated",
    },
  ])

  const [isStreaming, setIsStreaming] = useState(true)
  const [autoScroll, setAutoScroll] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [levelFilter, setLevelFilter] = useState("all")
  const [logSource, setLogSource] = useState("vokaflow_backend.log")
  const [refreshRate, setRefreshRate] = useState("500")
  const logsEndRef = useRef<HTMLDivElement>(null)

  const filteredLogs = logs.filter((log) => {
    const matchesSearch =
      log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.component.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesLevel = levelFilter === "all" || log.level === levelFilter
    return matchesSearch && matchesLevel
  })

  const getLevelColor = (level: string) => {
    switch (level) {
      case "ERROR":
        return "text-voka-red"
      case "WARN":
        return "text-voka-orange"
      case "INFO":
        return "text-voka-green"
      case "DEBUG":
        return "text-voka-gray"
      default:
        return "text-voka-white"
    }
  }

  const getLevelBadge = (level: string) => {
    const colors = {
      ERROR: "bg-voka-red/20 text-voka-red border-voka-red",
      WARN: "bg-voka-orange/20 text-voka-orange border-voka-orange",
      INFO: "bg-voka-green/20 text-voka-green border-voka-green",
      DEBUG: "bg-voka-gray/20 text-voka-gray border-voka-gray",
    }
    return (
      <Badge className={`${colors[level as keyof typeof colors]} font-montserrat font-mono text-xs`}>{level}</Badge>
    )
  }

  const exportLogs = () => {
    const logContent = filteredLogs
      .map((log) => `[${log.timestamp}] ${log.level} - ${log.component} - ${log.message}`)
      .join("\n")

    const blob = new Blob([logContent], { type: "text/plain" })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `${logSource}_${new Date().toISOString().split("T")[0]}.log`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  const clearLogs = () => {
    setLogs([])
  }

  // Simulate real-time log streaming
  useEffect(() => {
    if (!isStreaming) return

    const interval = setInterval(() => {
      const newLog: LogEntry = {
        id: Date.now(),
        timestamp: new Date().toLocaleTimeString("es-ES", { hour12: false }),
        level: ["INFO", "WARN", "ERROR", "DEBUG"][Math.floor(Math.random() * 4)] as LogEntry["level"],
        component: ["vokaflow-backend", "monitoring", "api", "system"][Math.floor(Math.random() * 4)],
        message: [
          "Request processed successfully",
          "Database connection established",
          "Cache miss for key: user_session",
          "Memory usage: 67%",
          "New user registration",
          "API rate limit check passed",
        ][Math.floor(Math.random() * 6)],
      }

      setLogs((prev) => [...prev.slice(-49), newLog]) // Keep last 50 logs
    }, Number.parseInt(refreshRate))

    return () => clearInterval(interval)
  }, [isStreaming, refreshRate])

  // Auto-scroll to bottom
  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [logs, autoScroll])

  return (
    <div className="space-y-4">
      {/* Controls */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardContent className="pt-6">
          <div className="flex flex-col lg:flex-row gap-4">
            <Select value={logSource} onValueChange={setLogSource}>
              <SelectTrigger className="w-full lg:w-48 bg-voka-dark border-voka-border text-voka-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-voka-blue-black border-voka-border">
                <SelectItem value="vokaflow_backend.log">vokaflow_backend.log</SelectItem>
                <SelectItem value="system.log">system.log</SelectItem>
                <SelectItem value="error.log">error.log</SelectItem>
                <SelectItem value="access.log">access.log</SelectItem>
              </SelectContent>
            </Select>

            <div className="flex items-center gap-2">
              <span className="text-voka-gray font-montserrat text-sm">Auto-scroll:</span>
              <Button
                size="sm"
                variant={autoScroll ? "default" : "outline"}
                className={
                  autoScroll
                    ? "bg-voka-green hover:bg-voka-green/80 text-white"
                    : "border-voka-border text-voka-gray hover:text-voka-white"
                }
                onClick={() => setAutoScroll(!autoScroll)}
              >
                {autoScroll ? "ON" : "OFF"}
              </Button>
            </div>

            <Select value={refreshRate} onValueChange={setRefreshRate}>
              <SelectTrigger className="w-full lg:w-32 bg-voka-dark border-voka-border text-voka-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-voka-blue-black border-voka-border">
                <SelectItem value="250">250ms</SelectItem>
                <SelectItem value="500">500ms</SelectItem>
                <SelectItem value="1000">1s</SelectItem>
                <SelectItem value="2000">2s</SelectItem>
              </SelectContent>
            </Select>

            <div className="flex gap-2">
              <Button
                size="sm"
                variant="outline"
                className={`border-voka-border ${isStreaming ? "text-voka-orange hover:bg-voka-orange hover:text-white" : "text-voka-green hover:bg-voka-green hover:text-white"}`}
                onClick={() => setIsStreaming(!isStreaming)}
              >
                {isStreaming ? <Pause className="h-4 w-4 mr-2" /> : <Play className="h-4 w-4 mr-2" />}
                {isStreaming ? "Pausar" : "Reanudar"}
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="border-voka-border text-voka-gray hover:text-voka-white"
                onClick={clearLogs}
              >
                <Square className="h-4 w-4 mr-2" />
                Limpiar
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="border-voka-border text-voka-gray hover:text-voka-white"
                onClick={exportLogs}
              >
                <Download className="h-4 w-4 mr-2" />
                Guardar
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Filters */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
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
              <SelectTrigger className="w-full md:w-48 bg-voka-dark border-voka-border text-voka-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-voka-blue-black border-voka-border">
                <SelectItem value="all">Todos los Niveles</SelectItem>
                <SelectItem value="ERROR">ERROR</SelectItem>
                <SelectItem value="WARN">WARN</SelectItem>
                <SelectItem value="INFO">INFO</SelectItem>
                <SelectItem value="DEBUG">DEBUG</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Log Viewer */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
              <FileText className="h-5 w-5 text-voka-magenta" />
              Logs del Sistema en Tiempo Real
              {isStreaming && (
                <Badge className="bg-voka-green/20 text-voka-green border-voka-green font-montserrat animate-pulse">
                  🔴 LIVE
                </Badge>
              )}
            </CardTitle>
            <div className="text-voka-gray font-montserrat text-sm">{filteredLogs.length} entradas</div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="bg-voka-dark rounded-lg p-4 h-96 overflow-y-auto border border-voka-border font-mono text-sm">
            {filteredLogs.map((log) => (
              <div key={log.id} className="flex items-start gap-3 mb-2 hover:bg-voka-border/20 p-1 rounded">
                <span className="text-voka-gray font-mono text-xs whitespace-nowrap">[{log.timestamp}]</span>
                {getLevelBadge(log.level)}
                <span className="text-voka-blue font-mono text-xs">{log.component}</span>
                <span className="text-voka-gray">-</span>
                <span className={`${getLevelColor(log.level)} flex-1`}>{log.message}</span>
              </div>
            ))}
            <div ref={logsEndRef} />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

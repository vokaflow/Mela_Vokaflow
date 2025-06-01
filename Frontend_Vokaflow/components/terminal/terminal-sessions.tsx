"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Users, RefreshCw, Square, AlertTriangle } from "lucide-react"

interface Session {
  pid: number
  user: string
  process: string
  cpu: number
  memory: number
  time: string
  status: "running" | "sleeping" | "zombie"
}

export function TerminalSessions() {
  const [sessions, setSessions] = useState<Session[]>([
    {
      pid: 8988,
      user: "dw7",
      process: "python src/main.py",
      cpu: 2.1,
      memory: 3.4,
      time: "0:01:23",
      status: "running",
    },
    {
      pid: 9001,
      user: "redis",
      process: "redis-server",
      cpu: 0.5,
      memory: 1.2,
      time: "5:32:10",
      status: "sleeping",
    },
    {
      pid: 9123,
      user: "dw7",
      process: "nginx worker",
      cpu: 0.1,
      memory: 0.8,
      time: "2:15:45",
      status: "running",
    },
    {
      pid: 9234,
      user: "dw7",
      process: "python identify_routers.py",
      cpu: 0.3,
      memory: 2.1,
      time: "0:00:05",
      status: "running",
    },
  ])
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [systemMetrics, setSystemMetrics] = useState({
    totalCpu: 3.0,
    totalMemory: 7.5,
    activeSessions: 4,
    totalProcesses: 127,
  })

  const refreshSessions = async () => {
    setIsRefreshing(true)
    // Simulate API call to /api/monitoring/metrics
    setTimeout(() => {
      setSessions((prev) =>
        prev.map((session) => ({
          ...session,
          cpu: Math.max(0, session.cpu + (Math.random() - 0.5) * 0.5),
          memory: Math.max(0, session.memory + (Math.random() - 0.5) * 0.3),
        })),
      )
      setSystemMetrics((prev) => ({
        ...prev,
        totalCpu: Math.max(0, prev.totalCpu + (Math.random() - 0.5) * 1),
        totalMemory: Math.max(0, prev.totalMemory + (Math.random() - 0.5) * 0.5),
      }))
      setIsRefreshing(false)
    }, 1000)
  }

  const killProcess = (pid: number) => {
    if (confirm(`¿Estás seguro de que quieres terminar el proceso ${pid}?`)) {
      setSessions((prev) => prev.filter((session) => session.pid !== pid))
      setSystemMetrics((prev) => ({
        ...prev,
        activeSessions: prev.activeSessions - 1,
        totalProcesses: prev.totalProcesses - 1,
      }))
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "running":
        return <Badge className="bg-voka-green/20 text-voka-green border-voka-green font-montserrat">Running</Badge>
      case "sleeping":
        return <Badge className="bg-voka-yellow/20 text-voka-yellow border-voka-yellow font-montserrat">Sleeping</Badge>
      case "zombie":
        return <Badge className="bg-voka-red/20 text-voka-red border-voka-red font-montserrat">Zombie</Badge>
      default:
        return <Badge className="bg-voka-gray/20 text-voka-gray border-voka-gray font-montserrat">Unknown</Badge>
    }
  }

  useEffect(() => {
    const interval = setInterval(refreshSessions, 5000) // Auto-refresh every 5 seconds
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="space-y-6">
      {/* System Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-voka-blue-black border-voka-border">
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-voka-white font-montserrat">{systemMetrics.activeSessions}</div>
            <p className="text-voka-gray font-montserrat text-sm">Sesiones Activas</p>
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border">
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-voka-blue font-montserrat">
              {systemMetrics.totalCpu.toFixed(1)}%
            </div>
            <p className="text-voka-gray font-montserrat text-sm">CPU Total</p>
            <Progress value={systemMetrics.totalCpu} className="h-2 mt-2" />
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border">
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-voka-magenta font-montserrat">
              {systemMetrics.totalMemory.toFixed(1)}%
            </div>
            <p className="text-voka-gray font-montserrat text-sm">Memoria Total</p>
            <Progress value={systemMetrics.totalMemory} className="h-2 mt-2" />
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border">
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-voka-green font-montserrat">{systemMetrics.totalProcesses}</div>
            <p className="text-voka-gray font-montserrat text-sm">Procesos Totales</p>
          </CardContent>
        </Card>
      </div>

      {/* Sessions Table */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
              <Users className="h-5 w-5 text-voka-magenta" />
              Sesiones Activas (Tiempo Real)
            </CardTitle>
            <Button
              onClick={refreshSessions}
              disabled={isRefreshing}
              size="sm"
              className="bg-voka-magenta hover:bg-voka-magenta/80 text-white font-montserrat"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? "animate-spin" : ""}`} />
              Actualizar
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-voka-border">
                  <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">PID</th>
                  <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Usuario</th>
                  <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Proceso</th>
                  <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">CPU%</th>
                  <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">MEM%</th>
                  <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Tiempo</th>
                  <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Estado</th>
                  <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Acción</th>
                </tr>
              </thead>
              <tbody>
                {sessions.map((session) => (
                  <tr key={session.pid} className="border-b border-voka-border/50 hover:bg-voka-border/20">
                    <td className="py-3 px-4 text-voka-white font-montserrat font-mono">{session.pid}</td>
                    <td className="py-3 px-4 text-voka-white font-montserrat">{session.user}</td>
                    <td className="py-3 px-4 text-voka-white font-montserrat font-mono text-sm">{session.process}</td>
                    <td className="py-3 px-4 text-voka-blue font-montserrat font-mono">{session.cpu.toFixed(1)}%</td>
                    <td className="py-3 px-4 text-voka-magenta font-montserrat font-mono">
                      {session.memory.toFixed(1)}%
                    </td>
                    <td className="py-3 px-4 text-voka-white font-montserrat font-mono">{session.time}</td>
                    <td className="py-3 px-4">{getStatusBadge(session.status)}</td>
                    <td className="py-3 px-4">
                      <Button
                        size="sm"
                        variant="outline"
                        className="border-voka-red text-voka-red hover:bg-voka-red hover:text-white"
                        onClick={() => killProcess(session.pid)}
                      >
                        <Square className="h-3 w-3 mr-1" />
                        Kill
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Warning */}
      <Card className="bg-voka-orange/10 border-voka-orange/30">
        <CardContent className="pt-6">
          <div className="flex items-center gap-3">
            <AlertTriangle className="h-5 w-5 text-voka-orange" />
            <div>
              <p className="text-voka-orange font-montserrat font-semibold">Zona de Peligro</p>
              <p className="text-voka-gray font-montserrat text-sm">
                Terminar procesos críticos puede afectar el funcionamiento del sistema.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

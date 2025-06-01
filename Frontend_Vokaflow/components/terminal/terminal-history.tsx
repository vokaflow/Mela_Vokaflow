"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { History, Search, Download, Trash2, Play, CheckCircle, XCircle } from "lucide-react"

interface CommandEntry {
  id: number
  timestamp: string
  user: string
  command: string
  status: "success" | "error"
  exitCode: number
  duration: string
}

export function TerminalHistory() {
  const [commands] = useState<CommandEntry[]>([
    {
      id: 1,
      timestamp: "23:52:15",
      user: "dw7",
      command: "python identify_routers.py",
      status: "success",
      exitCode: 0,
      duration: "2.3s",
    },
    {
      id: 2,
      timestamp: "23:51:45",
      user: "dw7",
      command: "curl localhost:8000/health",
      status: "success",
      exitCode: 0,
      duration: "0.1s",
    },
    {
      id: 3,
      timestamp: "23:51:30",
      user: "dw7",
      command: "ps aux | grep python",
      status: "success",
      exitCode: 0,
      duration: "0.2s",
    },
    {
      id: 4,
      timestamp: "23:51:21",
      user: "dw7",
      command: "python src/main.py --debug",
      status: "error",
      exitCode: 1,
      duration: "3.2s",
    },
    {
      id: 5,
      timestamp: "23:50:10",
      user: "dw7",
      command: "git status",
      status: "success",
      exitCode: 0,
      duration: "0.1s",
    },
    {
      id: 6,
      timestamp: "23:49:55",
      user: "dw7",
      command: "systemctl restart vokaflow",
      status: "success",
      exitCode: 0,
      duration: "1.8s",
    },
    {
      id: 7,
      timestamp: "23:49:30",
      user: "dw7",
      command: "tail -f logs/vokaflow_backend.log",
      status: "success",
      exitCode: 0,
      duration: "0.1s",
    },
    {
      id: 8,
      timestamp: "23:48:12",
      user: "dw7",
      command: "docker ps -a",
      status: "error",
      exitCode: 127,
      duration: "0.1s",
    },
  ])

  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [userFilter, setUserFilter] = useState("all")

  const filteredCommands = commands.filter((cmd) => {
    const matchesSearch = cmd.command.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "all" || cmd.status === statusFilter
    const matchesUser = userFilter === "all" || cmd.user === userFilter
    return matchesSearch && matchesStatus && matchesUser
  })

  const getStatusIcon = (status: string) => {
    return status === "success" ? (
      <CheckCircle className="h-4 w-4 text-voka-green" />
    ) : (
      <XCircle className="h-4 w-4 text-voka-red" />
    )
  }

  const getStatusBadge = (status: string, exitCode: number) => {
    return status === "success" ? (
      <Badge className="bg-voka-green/20 text-voka-green border-voka-green font-montserrat">✅ {exitCode}</Badge>
    ) : (
      <Badge className="bg-voka-red/20 text-voka-red border-voka-red font-montserrat">❌ {exitCode}</Badge>
    )
  }

  const executeCommand = (command: string) => {
    console.log(`Ejecutando comando: ${command}`)
    // Aquí se integraría con el componente de terminal
  }

  const exportHistory = () => {
    const csvContent = [
      "Timestamp,User,Command,Status,Exit Code,Duration",
      ...filteredCommands.map(
        (cmd) => `${cmd.timestamp},${cmd.user},"${cmd.command}",${cmd.status},${cmd.exitCode},${cmd.duration}`,
      ),
    ].join("\n")

    const blob = new Blob([csvContent], { type: "text/csv" })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "terminal_history.csv"
    a.click()
    window.URL.revokeObjectURL(url)
  }

  const clearHistory = () => {
    if (confirm("¿Estás seguro de que quieres limpiar todo el historial?")) {
      // Aquí se haría la llamada a la API para limpiar el historial
      console.log("Historial limpiado")
    }
  }

  const successRate = Math.round((commands.filter((cmd) => cmd.status === "success").length / commands.length) * 100)
  const mostUsedCommand = "python"
  const totalCommands = commands.length

  return (
    <div className="space-y-6">
      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-voka-blue-black border-voka-border">
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-voka-green font-montserrat">{successRate}%</div>
            <p className="text-voka-gray font-montserrat text-sm">Tasa de Éxito</p>
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border">
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-voka-blue font-montserrat">{totalCommands}</div>
            <p className="text-voka-gray font-montserrat text-sm">Comandos Totales</p>
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border">
          <CardContent className="pt-6">
            <div className="text-lg font-bold text-voka-magenta font-montserrat font-mono">{mostUsedCommand}</div>
            <p className="text-voka-gray font-montserrat text-sm">Comando Más Usado</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-voka-gray" />
                <Input
                  placeholder="Buscar comandos..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-voka-dark border-voka-border text-voka-white placeholder:text-voka-gray"
                />
              </div>
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full md:w-48 bg-voka-dark border-voka-border text-voka-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-voka-blue-black border-voka-border">
                <SelectItem value="all">Todos los Estados</SelectItem>
                <SelectItem value="success">Exitosos</SelectItem>
                <SelectItem value="error">Con Errores</SelectItem>
              </SelectContent>
            </Select>
            <Select value={userFilter} onValueChange={setUserFilter}>
              <SelectTrigger className="w-full md:w-48 bg-voka-dark border-voka-border text-voka-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-voka-blue-black border-voka-border">
                <SelectItem value="all">Todos los Usuarios</SelectItem>
                <SelectItem value="dw7">dw7</SelectItem>
                <SelectItem value="redis">redis</SelectItem>
              </SelectContent>
            </Select>
            <div className="flex gap-2">
              <Button
                onClick={exportHistory}
                size="sm"
                variant="outline"
                className="border-voka-border text-voka-gray hover:text-voka-white"
              >
                <Download className="h-4 w-4 mr-2" />
                Exportar
              </Button>
              <Button
                onClick={clearHistory}
                size="sm"
                variant="outline"
                className="border-voka-red text-voka-red hover:bg-voka-red hover:text-white"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Limpiar
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* History Table */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader>
          <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
            <History className="h-5 w-5 text-voka-magenta" />
            Historial de Comandos ({filteredCommands.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-voka-border">
                  <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Hora</th>
                  <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Usuario</th>
                  <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Comando</th>
                  <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Estado</th>
                  <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Duración</th>
                  <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Acción</th>
                </tr>
              </thead>
              <tbody>
                {filteredCommands.map((cmd) => (
                  <tr key={cmd.id} className="border-b border-voka-border/50 hover:bg-voka-border/20">
                    <td className="py-3 px-4 text-voka-gray font-montserrat font-mono text-sm">🕐 {cmd.timestamp}</td>
                    <td className="py-3 px-4 text-voka-white font-montserrat">{cmd.user}</td>
                    <td className="py-3 px-4 text-voka-white font-montserrat font-mono text-sm max-w-md truncate">
                      {cmd.command}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(cmd.status)}
                        {getStatusBadge(cmd.status, cmd.exitCode)}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-voka-gray font-montserrat font-mono text-sm">({cmd.duration})</td>
                    <td className="py-3 px-4">
                      <Button
                        size="sm"
                        variant="outline"
                        className="border-voka-border text-voka-gray hover:text-voka-white"
                        onClick={() => executeCommand(cmd.command)}
                      >
                        <Play className="h-3 w-3 mr-1" />
                        Ejecutar
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

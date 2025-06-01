"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Zap, Search, Square, Pause, AlertTriangle } from "lucide-react"

interface Process {
  pid: number
  process: string
  cpu: number
  memory: number
  user: string
  status: "running" | "sleeping" | "zombie"
  critical: boolean
}

export function TerminalProcesses() {
  const [processes, setProcesses] = useState<Process[]>([
    { pid: 8988, process: "python src/main.py", cpu: 2.1, memory: 3.4, user: "dw7", status: "running", critical: true },
    { pid: 9001, process: "redis-server", cpu: 0.5, memory: 1.2, user: "redis", status: "sleeping", critical: true },
    { pid: 9123, process: "nginx worker", cpu: 0.1, memory: 0.8, user: "dw7", status: "running", critical: true },
    {
      pid: 9234,
      process: "python identify_routers.py",
      cpu: 0.3,
      memory: 2.1,
      user: "dw7",
      status: "running",
      critical: false,
    },
    { pid: 9456, process: "node server.js", cpu: 1.2, memory: 4.5, user: "dw7", status: "running", critical: false },
    { pid: 9567, process: "postgres", cpu: 0.8, memory: 6.2, user: "postgres", status: "sleeping", critical: true },
  ])

  const [selectedProcesses, setSelectedProcesses] = useState<number[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")

  const filteredProcesses = processes.filter((proc) => {
    const matchesSearch = proc.process.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "all" || proc.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const toggleProcessSelection = (pid: number) => {
    setSelectedProcesses((prev) => (prev.includes(pid) ? prev.filter((p) => p !== pid) : [...prev, pid]))
  }

  const killProcess = (pid: number) => {
    const process = processes.find((p) => p.pid === pid)
    if (process?.critical) {
      if (
        !confirm(
          `⚠️ ADVERTENCIA: Este es un proceso crítico (${process.process}). ¿Estás seguro de que quieres terminarlo?`,
        )
      ) {
        return
      }
    }

    setProcesses((prev) => prev.filter((p) => p.pid !== pid))
    setSelectedProcesses((prev) => prev.filter((p) => p !== pid))
  }

  const killSelectedProcesses = () => {
    const criticalProcesses = selectedProcesses.filter((pid) => processes.find((p) => p.pid === pid)?.critical)

    if (criticalProcesses.length > 0) {
      if (!confirm(`⚠️ ADVERTENCIA: Vas a terminar ${criticalProcesses.length} proceso(s) crítico(s). ¿Continuar?`)) {
        return
      }
    }

    setProcesses((prev) => prev.filter((p) => !selectedProcesses.includes(p.pid)))
    setSelectedProcesses([])
  }

  const stopProcess = (pid: number) => {
    setProcesses((prev) => prev.map((p) => (p.pid === pid ? { ...p, status: "sleeping" as const } : p)))
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

  return (
    <div className="space-y-6">
      {/* Filters */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-voka-gray" />
                <Input
                  placeholder="Buscar por nombre de proceso..."
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
                <SelectItem value="all">Todos los Procesos</SelectItem>
                <SelectItem value="running">En Ejecución</SelectItem>
                <SelectItem value="sleeping">Durmiendo</SelectItem>
                <SelectItem value="zombie">Zombie</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Process Manager */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
              <Zap className="h-5 w-5 text-voka-magenta" />
              Gestor de Procesos
              <Badge className="bg-voka-red/20 text-voka-red border-voka-red font-montserrat ml-2">
                ⚠️ ZONA PELIGROSA
              </Badge>
            </CardTitle>
            <div className="flex gap-2">
              <Button
                onClick={killSelectedProcesses}
                disabled={selectedProcesses.length === 0}
                size="sm"
                className="bg-voka-red hover:bg-voka-red/80 text-white font-montserrat"
              >
                <Square className="h-4 w-4 mr-2" />
                Terminar Seleccionados ({selectedProcesses.length})
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-voka-border">
                  <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">
                    <Checkbox
                      checked={selectedProcesses.length === filteredProcesses.length && filteredProcesses.length > 0}
                      onCheckedChange={(checked) => {
                        if (checked) {
                          setSelectedProcesses(filteredProcesses.map((p) => p.pid))
                        } else {
                          setSelectedProcesses([])
                        }
                      }}
                    />
                  </th>
                  <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">PID</th>
                  <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Proceso</th>
                  <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">CPU%</th>
                  <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">MEM%</th>
                  <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Usuario</th>
                  <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Estado</th>
                  <th className="text-left py-3 px-4 text-voka-gray font-montserrat font-semibold">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filteredProcesses.map((process) => (
                  <tr key={process.pid} className="border-b border-voka-border/50 hover:bg-voka-border/20">
                    <td className="py-3 px-4">
                      <Checkbox
                        checked={selectedProcesses.includes(process.pid)}
                        onCheckedChange={() => toggleProcessSelection(process.pid)}
                      />
                    </td>
                    <td className="py-3 px-4 text-voka-white font-montserrat font-mono">{process.pid}</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        {process.critical && <AlertTriangle className="h-4 w-4 text-voka-orange" />}
                        <span className="text-voka-white font-montserrat font-mono text-sm">{process.process}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-voka-blue font-montserrat font-mono">{process.cpu.toFixed(1)}%</td>
                    <td className="py-3 px-4 text-voka-magenta font-montserrat font-mono">
                      {process.memory.toFixed(1)}%
                    </td>
                    <td className="py-3 px-4 text-voka-white font-montserrat">{process.user}</td>
                    <td className="py-3 px-4">{getStatusBadge(process.status)}</td>
                    <td className="py-3 px-4">
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          className="border-voka-yellow text-voka-yellow hover:bg-voka-yellow hover:text-voka-dark"
                          onClick={() => stopProcess(process.pid)}
                          disabled={process.status === "sleeping"}
                        >
                          <Pause className="h-3 w-3 mr-1" />
                          Stop
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className={`${
                            process.critical
                              ? "border-voka-orange text-voka-orange hover:bg-voka-orange hover:text-white"
                              : "border-voka-red text-voka-red hover:bg-voka-red hover:text-white"
                          }`}
                          onClick={() => killProcess(process.pid)}
                        >
                          <Square className="h-3 w-3 mr-1" />
                          Kill
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Safety Warning */}
      <Card className="bg-voka-red/10 border-voka-red/30">
        <CardContent className="pt-6">
          <div className="flex items-center gap-3">
            <AlertTriangle className="h-5 w-5 text-voka-red" />
            <div>
              <p className="text-voka-red font-montserrat font-semibold">⚠️ Advertencia de Seguridad</p>
              <p className="text-voka-gray font-montserrat text-sm">
                Los procesos marcados con ⚠️ son críticos para el sistema. Terminarlos puede causar inestabilidad o
                pérdida de datos.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

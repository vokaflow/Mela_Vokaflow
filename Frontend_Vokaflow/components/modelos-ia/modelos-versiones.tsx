"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Download, Upload, GitBranch, Clock, CheckCircle, AlertTriangle } from "lucide-react"

interface ModelVersion {
  id: string
  name: string
  version: string
  status: "active" | "deprecated" | "beta" | "archived"
  size: string
  accuracy: number
  releaseDate: string
  description: string
}

export function ModelosVersiones() {
  const [versions] = useState<ModelVersion[]>([
    {
      id: "gpt4-v1",
      name: "GPT-4 Turbo",
      version: "v1.2.3",
      status: "active",
      size: "175GB",
      accuracy: 98.5,
      releaseDate: "2024-01-10",
      description: "Versión optimizada para traducción multiidioma",
    },
    {
      id: "gpt4-v2",
      name: "GPT-4 Turbo",
      version: "v1.3.0-beta",
      status: "beta",
      size: "180GB",
      accuracy: 99.1,
      releaseDate: "2024-01-15",
      description: "Versión beta con mejoras en contexto emocional",
    },
    {
      id: "whisper-v1",
      name: "Whisper Large",
      version: "v3.0.1",
      status: "active",
      size: "3.9GB",
      accuracy: 96.8,
      releaseDate: "2024-01-08",
      description: "Modelo de reconocimiento de voz multiidioma",
    },
    {
      id: "gpt4-old",
      name: "GPT-4 Turbo",
      version: "v1.1.5",
      status: "deprecated",
      size: "170GB",
      accuracy: 97.2,
      releaseDate: "2023-12-20",
      description: "Versión anterior, marcada para deprecación",
    },
  ])

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-500"
      case "beta":
        return "bg-blue-500"
      case "deprecated":
        return "bg-yellow-500"
      case "archived":
        return "bg-gray-500"
      default:
        return "bg-gray-500"
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "active":
        return <CheckCircle className="h-4 w-4" />
      case "beta":
        return <GitBranch className="h-4 w-4" />
      case "deprecated":
        return <AlertTriangle className="h-4 w-4" />
      case "archived":
        return <Clock className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="bg-slate-900 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Versiones Activas</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{versions.filter((v) => v.status === "active").length}</div>
            <p className="text-xs text-slate-400">En producción</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Versiones Beta</CardTitle>
            <GitBranch className="h-4 w-4 text-blue-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{versions.filter((v) => v.status === "beta").length}</div>
            <p className="text-xs text-slate-400">En testing</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Espacio Total</CardTitle>
            <Download className="h-4 w-4 text-purple-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">528GB</div>
            <p className="text-xs text-slate-400">Todas las versiones</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Última Actualización</CardTitle>
            <Upload className="h-4 w-4 text-green-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">Hoy</div>
            <p className="text-xs text-slate-400">v1.3.0-beta</p>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-slate-900 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Gestión de Versiones</CardTitle>
          <CardDescription className="text-slate-400">
            Control y administración de versiones de modelos IA
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {versions.map((version) => (
              <div key={version.id} className="flex items-center justify-between p-4 bg-slate-800 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">{getStatusIcon(version.status)}</div>
                  <div>
                    <h4 className="text-white font-medium">{version.name}</h4>
                    <p className="text-slate-400 text-sm">{version.description}</p>
                    <div className="flex items-center space-x-2 mt-1">
                      <Badge variant="outline" className="text-xs">
                        {version.version}
                      </Badge>
                      <span className="text-slate-500 text-xs">•</span>
                      <span className="text-slate-500 text-xs">{version.size}</span>
                      <span className="text-slate-500 text-xs">•</span>
                      <span className="text-slate-500 text-xs">{version.accuracy}% precisión</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <Badge className={`${getStatusColor(version.status)} text-white`}>{version.status}</Badge>

                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm" className="text-slate-300 border-slate-600">
                      <Download className="h-4 w-4 mr-1" />
                      Descargar
                    </Button>
                    {version.status === "active" && (
                      <Button variant="outline" size="sm" className="text-slate-300 border-slate-600">
                        Configurar
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

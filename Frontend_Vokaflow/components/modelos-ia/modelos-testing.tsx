"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Play, CheckCircle, XCircle, Clock } from "lucide-react"

interface TestResult {
  id: string
  modelName: string
  testType: string
  status: "running" | "completed" | "failed" | "pending"
  accuracy: number
  latency: number
  timestamp: string
}

export function ModelosTesting() {
  const [tests, setTests] = useState<TestResult[]>([
    {
      id: "test-001",
      modelName: "GPT-4 Turbo",
      testType: "Traducción ES-EN",
      status: "completed",
      accuracy: 98.5,
      latency: 120,
      timestamp: "2024-01-15 14:30:00",
    },
    {
      id: "test-002",
      modelName: "Whisper Large",
      testType: "Reconocimiento de Voz",
      status: "running",
      accuracy: 0,
      latency: 0,
      timestamp: "2024-01-15 14:35:00",
    },
  ])

  const [runningTest, setRunningTest] = useState<string | null>("test-002")

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="bg-slate-900 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Tests Ejecutados</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">24</div>
            <p className="text-xs text-slate-400">+3 desde ayer</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Tasa de Éxito</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">96.8%</div>
            <p className="text-xs text-slate-400">+2.1% desde ayer</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Latencia Promedio</CardTitle>
            <Clock className="h-4 w-4 text-blue-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">145ms</div>
            <p className="text-xs text-slate-400">-12ms desde ayer</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Tests Activos</CardTitle>
            <Play className="h-4 w-4 text-purple-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">2</div>
            <p className="text-xs text-slate-400">En ejecución</p>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-slate-900 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Resultados de Testing</CardTitle>
          <CardDescription className="text-slate-400">
            Historial y estado actual de las pruebas de modelos
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {tests.map((test) => (
              <div key={test.id} className="flex items-center justify-between p-4 bg-slate-800 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    {test.status === "completed" && <CheckCircle className="h-5 w-5 text-green-400" />}
                    {test.status === "failed" && <XCircle className="h-5 w-5 text-red-400" />}
                    {test.status === "running" && <Play className="h-5 w-5 text-purple-400 animate-pulse" />}
                    {test.status === "pending" && <Clock className="h-5 w-5 text-yellow-400" />}
                  </div>
                  <div>
                    <h4 className="text-white font-medium">{test.modelName}</h4>
                    <p className="text-slate-400 text-sm">{test.testType}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <Badge
                    variant={
                      test.status === "completed"
                        ? "default"
                        : test.status === "failed"
                          ? "destructive"
                          : test.status === "running"
                            ? "secondary"
                            : "outline"
                    }
                  >
                    {test.status}
                  </Badge>

                  {test.status === "completed" && (
                    <div className="text-right">
                      <div className="text-white text-sm">Precisión: {test.accuracy}%</div>
                      <div className="text-slate-400 text-xs">Latencia: {test.latency}ms</div>
                    </div>
                  )}

                  {test.status === "running" && (
                    <div className="w-32">
                      <Progress value={65} className="h-2" />
                      <div className="text-slate-400 text-xs mt-1">65% completado</div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useEffect, useState } from "react"
import { TrendingUp, AlertTriangle, CheckCircle, Clock, Zap, Globe, Shield } from "lucide-react"

export function SystemOverview() {
  const [alerts, setAlerts] = useState([
    { id: 1, type: "success", message: "Sistema funcionando óptimamente", time: "Ahora" },
    { id: 2, type: "warning", message: "Actualización programada en 2h", time: "2h" },
    { id: 3, type: "info", message: "Nuevo modelo IA disponible", time: "5m" },
  ])

  const [systemStats, setSystemStats] = useState({
    uptime: "99.9%",
    translations: 15234,
    conversations: 8567,
    aiQueries: 3421,
    globalUsers: 156,
  })

  useEffect(() => {
    const interval = setInterval(() => {
      setSystemStats((prev) => ({
        ...prev,
        translations: prev.translations + Math.floor(Math.random() * 10),
        conversations: prev.conversations + Math.floor(Math.random() * 5),
        aiQueries: prev.aiQueries + Math.floor(Math.random() * 3),
      }))
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  const getAlertIcon = (type: string) => {
    switch (type) {
      case "success":
        return <CheckCircle className="h-4 w-4 text-voka-green" />
      case "warning":
        return <AlertTriangle className="h-4 w-4 text-voka-yellow" />
      case "error":
        return <AlertTriangle className="h-4 w-4 text-voka-red" />
      default:
        return <Clock className="h-4 w-4 text-voka-blue" />
    }
  }

  const getAlertColor = (type: string) => {
    switch (type) {
      case "success":
        return "border-voka-green/30 bg-voka-green/10"
      case "warning":
        return "border-voka-yellow/30 bg-voka-yellow/10"
      case "error":
        return "border-voka-red/30 bg-voka-red/10"
      default:
        return "border-voka-blue/30 bg-voka-blue/10"
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Estadísticas en Tiempo Real */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader>
          <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-voka-green" />
            Actividad en Tiempo Real
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 rounded-lg bg-voka-border/20">
              <div className="flex items-center gap-2">
                <Globe className="h-4 w-4 text-voka-blue" />
                <span className="text-voka-white font-montserrat">Traducciones Hoy</span>
              </div>
              <div className="text-right">
                <div className="text-voka-white font-bold">{systemStats.translations.toLocaleString()}</div>
                <Badge className="bg-voka-green/20 text-voka-green border-voka-green">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +8.2%
                </Badge>
              </div>
            </div>

            <div className="flex justify-between items-center p-3 rounded-lg bg-voka-border/20">
              <div className="flex items-center gap-2">
                <Zap className="h-4 w-4 text-voka-magenta" />
                <span className="text-voka-white font-montserrat">Consultas Vicky AI</span>
              </div>
              <div className="text-right">
                <div className="text-voka-white font-bold">{systemStats.aiQueries.toLocaleString()}</div>
                <Badge className="bg-voka-magenta/20 text-voka-magenta border-voka-magenta">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +23.1%
                </Badge>
              </div>
            </div>

            <div className="flex justify-between items-center p-3 rounded-lg bg-voka-border/20">
              <div className="flex items-center gap-2">
                <Shield className="h-4 w-4 text-voka-yellow" />
                <span className="text-voka-white font-montserrat">Uptime Sistema</span>
              </div>
              <div className="text-right">
                <div className="text-voka-white font-bold">{systemStats.uptime}</div>
                <Badge className="bg-voka-green/20 text-voka-green border-voka-green">Estable</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Centro de Alertas */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader>
          <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-voka-orange" />
            Centro de Alertas
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className={`flex items-center gap-3 p-3 rounded-lg border ${getAlertColor(alert.type)}`}
              >
                {getAlertIcon(alert.type)}
                <div className="flex-1">
                  <span className="text-voka-white font-montserrat text-sm">{alert.message}</span>
                </div>
                <span className="text-voka-gray text-xs">{alert.time}</span>
              </div>
            ))}
          </div>

          <Button variant="outline" className="w-full mt-4 border-voka-border text-voka-white hover:bg-voka-border/50">
            Ver Todas las Alertas
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}

"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Activity, Users, Zap, Globe } from "lucide-react"

export function DashboardContent() {
  const stats = [
    {
      title: "Usuarios Activos",
      value: "2,847",
      change: "+12.5%",
      icon: Users,
      color: "text-voka-blue",
    },
    {
      title: "Traducciones Hoy",
      value: "15,234",
      change: "+8.2%",
      icon: Globe,
      color: "text-voka-green",
    },
    {
      title: "Vicky AI Consultas",
      value: "3,421",
      change: "+23.1%",
      icon: Zap,
      color: "text-voka-magenta",
    },
    {
      title: "Uptime Sistema",
      value: "99.9%",
      change: "Estable",
      icon: Activity,
      color: "text-voka-yellow",
    },
  ]

  return (
    <div className="flex-1 space-y-6 p-6 bg-voka-dark">
      {/* Header de bienvenida */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-voka-white font-montserrat">¡Bienvenido al Dashboard VokaFlow! 🚀</h1>
        <p className="text-voka-gray font-montserrat">Centro de comando para tu plataforma de comunicación global</p>
      </div>

      {/* Métricas principales */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card
            key={stat.title}
            className="bg-voka-blue-black border-voka-border hover:border-voka-magenta/50 transition-colors"
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-voka-gray font-montserrat">{stat.title}</CardTitle>
              <stat.icon className={`h-5 w-5 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-voka-white font-montserrat">{stat.value}</div>
              <Badge variant="secondary" className={`mt-2 ${stat.color} bg-transparent border font-montserrat`}>
                {stat.change}
              </Badge>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Secciones principales */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card className="bg-voka-blue-black border-voka-border">
          <CardHeader>
            <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
              <Zap className="h-5 w-5 text-voka-magenta" />
              Estado de Vicky AI
            </CardTitle>
            <CardDescription className="text-voka-gray font-montserrat">
              Monitoreo en tiempo real de la IA central
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-voka-gray font-montserrat">Procesamiento</span>
                <Badge className="bg-voka-green/20 text-voka-green border-voka-green font-montserrat">Óptimo</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-voka-gray font-montserrat">Latencia</span>
                <span className="text-voka-white font-montserrat">45ms</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-voka-gray font-montserrat">Precisión</span>
                <span className="text-voka-white font-montserrat">98.7%</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border">
          <CardHeader>
            <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
              <Globe className="h-5 w-5 text-voka-blue" />
              Actividad Global
            </CardTitle>
            <CardDescription className="text-voka-gray font-montserrat">
              Comunicaciones en tiempo real por región
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-voka-gray font-montserrat">América</span>
                <span className="text-voka-white font-montserrat">1,247 activos</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-voka-gray font-montserrat">Europa</span>
                <span className="text-voka-white font-montserrat">892 activos</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-voka-gray font-montserrat">Asia</span>
                <span className="text-voka-white font-montserrat">708 activos</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Alertas y notificaciones */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader>
          <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
            <Activity className="h-5 w-5 text-voka-orange" />
            Centro de Alertas
          </CardTitle>
          <CardDescription className="text-voka-gray font-montserrat">
            Monitoreo de eventos críticos del sistema
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center gap-3 p-3 rounded-lg bg-voka-green/10 border border-voka-green/30">
              <div className="w-2 h-2 rounded-full bg-voka-green animate-pulse"></div>
              <span className="text-voka-white font-montserrat">Sistema funcionando correctamente</span>
              <Badge className="ml-auto bg-voka-green/20 text-voka-green border-voka-green font-montserrat">OK</Badge>
            </div>
            <div className="flex items-center gap-3 p-3 rounded-lg bg-voka-yellow/10 border border-voka-yellow/30">
              <div className="w-2 h-2 rounded-full bg-voka-yellow animate-pulse"></div>
              <span className="text-voka-white font-montserrat">Actualización programada en 2 horas</span>
              <Badge className="ml-auto bg-voka-yellow/20 text-voka-yellow border-voka-yellow font-montserrat">
                INFO
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

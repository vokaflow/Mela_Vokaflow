"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Bell, Mail, MessageSquare, AlertTriangle, CheckCircle, Clock } from "lucide-react"

export function NotificacionesMain() {
  const [notifications] = useState([
    {
      id: 1,
      type: "alert",
      title: "Uso elevado de GPU",
      message: "GPU #3 alcanzó 95% de uso durante 10 minutos",
      time: "Hace 5 min",
      read: false,
      priority: "high",
    },
    {
      id: 2,
      type: "info",
      title: "Modelo actualizado",
      message: "GPT-4 Turbo v1.3.0-beta disponible para descarga",
      time: "Hace 1h",
      read: false,
      priority: "medium",
    },
    {
      id: 3,
      type: "success",
      title: "Backup completado",
      message: "Respaldo automático finalizado exitosamente",
      time: "Hace 2h",
      read: true,
      priority: "low",
    },
    {
      id: 4,
      type: "warning",
      title: "Límite de API próximo",
      message: "85% del límite mensual de OpenAI alcanzado",
      time: "Hace 3h",
      read: false,
      priority: "high",
    },
  ])

  const getIcon = (type: string) => {
    switch (type) {
      case "alert":
        return <AlertTriangle className="h-4 w-4 text-red-400" />
      case "success":
        return <CheckCircle className="h-4 w-4 text-green-400" />
      case "warning":
        return <AlertTriangle className="h-4 w-4 text-yellow-400" />
      case "info":
        return <Bell className="h-4 w-4 text-blue-400" />
      default:
        return <Bell className="h-4 w-4 text-gray-400" />
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "bg-red-500"
      case "medium":
        return "bg-yellow-500"
      case "low":
        return "bg-green-500"
      default:
        return "bg-gray-500"
    }
  }

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <h1 className="text-4xl font-bold text-white font-montserrat">🔔 Notificaciones</h1>
        <p className="text-xl text-slate-400 font-montserrat">Centro de notificaciones y alertas del sistema</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="bg-slate-900 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">No Leídas</CardTitle>
            <Bell className="h-4 w-4 text-red-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{notifications.filter((n) => !n.read).length}</div>
            <p className="text-xs text-slate-400">Requieren atención</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Alta Prioridad</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {notifications.filter((n) => n.priority === "high").length}
            </div>
            <p className="text-xs text-slate-400">Críticas</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Hoy</CardTitle>
            <Clock className="h-4 w-4 text-blue-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">12</div>
            <p className="text-xs text-slate-400">Notificaciones</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Configuración</CardTitle>
            <MessageSquare className="h-4 w-4 text-green-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">8</div>
            <p className="text-xs text-slate-400">Canales activos</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-2">
          <Card className="bg-slate-900 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">Notificaciones Recientes</CardTitle>
              <CardDescription className="text-slate-400">Últimas alertas y mensajes del sistema</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={`flex items-start space-x-4 p-4 rounded-lg transition-colors ${
                      notification.read ? "bg-slate-800" : "bg-slate-800 border-l-4 border-blue-400"
                    }`}
                  >
                    <div className="flex-shrink-0 mt-1">{getIcon(notification.type)}</div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h4 className="text-white font-medium truncate">{notification.title}</h4>
                        <div className="flex items-center space-x-2">
                          <div className={`w-2 h-2 rounded-full ${getPriorityColor(notification.priority)}`}></div>
                          <span className="text-slate-400 text-xs">{notification.time}</span>
                        </div>
                      </div>
                      <p className="text-slate-400 text-sm mt-1">{notification.message}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <div>
          <Card className="bg-slate-900 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">Configuración</CardTitle>
              <CardDescription className="text-slate-400">Ajustes de notificaciones</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Mail className="h-4 w-4 text-blue-400" />
                    <span className="text-white text-sm">Email</span>
                  </div>
                  <Badge variant="outline" className="text-green-400 border-green-400">
                    Activo
                  </Badge>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <MessageSquare className="h-4 w-4 text-green-400" />
                    <span className="text-white text-sm">Slack</span>
                  </div>
                  <Badge variant="outline" className="text-green-400 border-green-400">
                    Activo
                  </Badge>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Bell className="h-4 w-4 text-purple-400" />
                    <span className="text-white text-sm">Push</span>
                  </div>
                  <Badge variant="outline" className="text-gray-400 border-gray-400">
                    Inactivo
                  </Badge>
                </div>

                <Button className="w-full mt-4" variant="outline">
                  Configurar Canales
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

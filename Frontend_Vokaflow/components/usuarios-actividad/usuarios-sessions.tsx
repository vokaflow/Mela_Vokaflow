"use client"

import { useState, useEffect } from "react"
import { Shield, Activity, AlertTriangle, Download } from "lucide-react"
import { usersService } from "../../services/users-service"
import type { SessionInfo, UserActivity } from "../../types/users"

export function UsuariosSessions() {
  const [sessions, setSessions] = useState<SessionInfo[]>([])
  const [activities, setActivities] = useState<UserActivity[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadData = async () => {
      try {
        const [sessionsData, activitiesData] = await Promise.all([
          usersService.getActiveSessions(),
          usersService.getUserActivity(),
        ])
        setSessions(sessionsData)
        setActivities(activitiesData)
      } catch (error) {
        console.error("Error loading sessions data:", error)
      } finally {
        setLoading(false)
      }
    }

    loadData()
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [])

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  if (loading) {
    return (
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-voka-border rounded w-1/4"></div>
          <div className="h-32 bg-voka-border rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Sesiones Activas */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-voka-white font-montserrat font-bold text-lg flex items-center">
            <Shield className="mr-2 text-voka-green" />🔐 SESIONES ACTIVAS
          </h3>
          <button className="bg-voka-blue hover:bg-voka-blue/80 text-white px-4 py-2 rounded-lg text-sm font-montserrat">
            🔄 Actualizar
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-voka-dark">
              <tr>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">USUARIO</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">ID SESIÓN</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">DIRECCIÓN IP</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">DISPOSITIVO</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">DURACIÓN</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">ESTADO</th>
              </tr>
            </thead>
            <tbody>
              {sessions.map((session) => (
                <tr key={session.session_id} className="border-t border-voka-border hover:bg-voka-dark/50">
                  <td className="p-4">
                    <span className="text-voka-white font-bold">dw7</span>
                  </td>
                  <td className="p-4">
                    <span className="text-voka-gray font-mono text-sm">{session.session_id}</span>
                  </td>
                  <td className="p-4">
                    <span className="text-voka-blue">{session.ip_address}</span>
                  </td>
                  <td className="p-4">
                    <div>
                      <div className="text-voka-white">{session.browser}</div>
                      <div className="text-voka-gray text-sm">{session.os}</div>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className="text-voka-green">{formatDuration(session.duration)}</span>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-voka-green rounded-full animate-pulse"></div>
                      <span className="text-voka-green text-sm">🟢 ACTIVA</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {sessions.length === 0 && <div className="text-center py-8 text-voka-gray">No hay sesiones activas</div>}
      </div>

      {/* Log de Actividad de Sesiones */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-voka-white font-montserrat font-bold text-lg flex items-center">
            <Activity className="mr-2 text-voka-blue" />📋 LOG DE ACTIVIDAD DE SESIONES
          </h3>
          <button className="bg-voka-magenta hover:bg-voka-magenta/80 text-white px-4 py-2 rounded-lg text-sm font-montserrat flex items-center">
            <Download className="w-4 h-4 mr-1" />📄 Exportar
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-voka-dark">
              <tr>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">HORA</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">USUARIO</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">ACCIÓN</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">IP</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">ESTADO</th>
              </tr>
            </thead>
            <tbody>
              {activities.slice(0, 10).map((activity) => (
                <tr key={activity.id} className="border-t border-voka-border hover:bg-voka-dark/50">
                  <td className="p-4">
                    <span className="text-voka-gray text-sm font-mono">
                      {new Date(activity.timestamp).toLocaleTimeString()}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className="text-voka-white">dw7</span>
                  </td>
                  <td className="p-4">
                    <span className="text-voka-white">{activity.action}</span>
                  </td>
                  <td className="p-4">
                    <span className="text-voka-blue">{activity.ip_address}</span>
                  </td>
                  <td className="p-4">
                    <span className={activity.success ? "text-voka-green" : "text-voka-orange"}>
                      {activity.success ? "✅" : "❌"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Resumen de Seguridad */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <h3 className="text-voka-white font-montserrat font-bold text-lg mb-4 flex items-center">
          <AlertTriangle className="mr-2 text-voka-orange" />
          🛡️ RESUMEN DE SEGURIDAD
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-voka-gray">Intentos de Login Fallidos:</span>
              <span className="text-voka-green font-bold">0</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-voka-gray">Actividad Sospechosa:</span>
              <span className="text-voka-green font-bold">0</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-voka-gray">Lista Blanca de IPs:</span>
              <span className="text-voka-blue">Todas</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-voka-gray">2FA Requerido:</span>
              <span className="text-voka-orange">No</span>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-voka-gray">Timeout de Sesión:</span>
              <span className="text-voka-white">24h</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-voka-gray">Política de Contraseñas:</span>
              <span className="text-voka-blue">Básica</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-voka-gray">Último Evento de Seguridad:</span>
              <span className="text-voka-gray">Ninguno</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-voka-gray">Puntuación de Seguridad:</span>
              <span className="text-voka-orange font-bold">85/100 🟡</span>
            </div>
          </div>
        </div>

        <div className="mt-6 p-4 bg-voka-dark rounded-lg">
          <div className="flex items-center space-x-2 text-voka-orange">
            <AlertTriangle className="w-4 h-4" />
            <span className="text-sm font-montserrat">
              Recomendación: Habilitar autenticación de dos factores (2FA) para mejorar la seguridad
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

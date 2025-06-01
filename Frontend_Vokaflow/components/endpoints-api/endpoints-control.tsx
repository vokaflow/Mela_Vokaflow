"use client"

import { useState, useEffect } from "react"
import { AlertTriangle, Settings, BarChart, Pause, Play, Calendar } from "lucide-react"
import { apiEndpointsService } from "../../services/api-endpoints-service"
import type { ApiRouter } from "../../types/api-endpoints"

export function EndpointsControl() {
  const [routers, setRouters] = useState<ApiRouter[]>([])
  const [maintenanceMode, setMaintenanceMode] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const routersData = await apiEndpointsService.getApiRouters()
      setRouters(routersData)
    } catch (error) {
      console.error("Error loading routers:", error)
    } finally {
      setLoading(false)
    }
  }

  const toggleMaintenanceMode = async () => {
    try {
      const success = await apiEndpointsService.setMaintenanceMode(!maintenanceMode)
      if (success) {
        setMaintenanceMode(!maintenanceMode)
      }
    } catch (error) {
      console.error("Error toggling maintenance mode:", error)
    }
  }

  const toggleRouter = (routerName: string) => {
    setRouters(
      routers.map((router) =>
        router.name === routerName ? { ...router, status: router.status === "online" ? "offline" : "online" } : router,
      ),
    )
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "online":
        return "🟢"
      case "offline":
        return "⚫"
      case "maintenance":
        return "🟡"
      default:
        return "⚫"
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "online":
        return "text-green-400"
      case "offline":
        return "text-gray-400"
      case "maintenance":
        return "text-yellow-400"
      default:
        return "text-gray-400"
    }
  }

  if (loading) {
    return (
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-2 border-voka-magenta border-t-transparent rounded-full animate-spin"></div>
          <span className="ml-3 text-voka-white font-montserrat">Cargando control de rutas...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* System Control */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-voka-white font-montserrat">⚙️ CONTROL DE SISTEMA Y MANTENIMIENTO</h3>
          <div className="flex items-center gap-2 text-sm">
            <AlertTriangle className="w-4 h-4 text-yellow-400" />
            <span className="text-yellow-400 font-semibold">ADMIN ONLY</span>
          </div>
        </div>

        {/* System Status */}
        <div className="bg-voka-dark border border-voka-border rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="text-lg font-semibold text-voka-white">
                Estado Actual:{" "}
                {maintenanceMode ? (
                  <span className="text-yellow-400">🔧 Modo Mantenimiento</span>
                ) : (
                  <span className="text-green-400">🟢 Todos los Sistemas Operativos</span>
                )}
              </div>
              <div className="text-sm text-voka-gray">Último Mantenimiento: 2025-01-25 03:00 AM</div>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={toggleMaintenanceMode}
              className={`px-4 py-2 rounded font-semibold transition-colors ${
                maintenanceMode
                  ? "bg-green-600 hover:bg-green-700 text-white"
                  : "bg-yellow-600 hover:bg-yellow-700 text-white"
              }`}
            >
              {maintenanceMode ? "🚀 ACTIVAR SISTEMA" : "🔧 MODO MANTENIMIENTO"}
            </button>
            <button className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded font-semibold transition-colors">
              ⏸️ DESACTIVAR API
            </button>
            <button className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded font-semibold transition-colors">
              🚀 ACTIVAR TODO
            </button>
          </div>
        </div>
      </div>

      {/* Router Control */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg overflow-hidden">
        <div className="p-6 border-b border-voka-border">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-voka-white font-montserrat">📡 CONTROL DE ROUTERS</h3>
            <div className="flex gap-2">
              <select className="bg-voka-dark border border-voka-border rounded px-3 py-1 text-voka-white text-sm">
                <option>🔍 Filtrar por estado</option>
                <option>🟢 Online</option>
                <option>⚫ Offline</option>
                <option>🟡 Mantenimiento</option>
              </select>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-voka-dark border-b border-voka-border">
              <tr>
                <th className="text-left p-4 text-voka-white font-montserrat font-semibold">ROUTER</th>
                <th className="text-left p-4 text-voka-white font-montserrat font-semibold">ESTADO</th>
                <th className="text-left p-4 text-voka-white font-montserrat font-semibold">ENDPOINTS</th>
                <th className="text-left p-4 text-voka-white font-montserrat font-semibold">ACCIONES</th>
                <th className="text-left p-4 text-voka-white font-montserrat font-semibold">ÚLTIMO TOGGLE</th>
              </tr>
            </thead>
            <tbody>
              {routers.map((router) => (
                <tr
                  key={router.name}
                  className="border-b border-voka-border/30 hover:bg-voka-dark/30 transition-colors"
                >
                  <td className="p-4">
                    <div className="flex items-center gap-3">
                      <span className="text-xl">{router.icon}</span>
                      <span className="text-voka-white font-medium">{router.name}</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <span>{getStatusIcon(router.status)}</span>
                      <span className={`font-medium ${getStatusColor(router.status)}`}>
                        {router.status.toUpperCase()}
                      </span>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className="text-voka-white font-mono">{router.totalEndpoints}</span>
                  </td>
                  <td className="p-4">
                    <div className="flex gap-2">
                      <button
                        onClick={() => toggleRouter(router.name)}
                        className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                          router.status === "online"
                            ? "bg-red-600 hover:bg-red-700 text-white"
                            : "bg-green-600 hover:bg-green-700 text-white"
                        }`}
                      >
                        {router.status === "online" ? (
                          <>
                            <Pause className="w-3 h-3 inline mr-1" />
                            ⏸️
                          </>
                        ) : (
                          <>
                            <Play className="w-3 h-3 inline mr-1" />
                            ▶️
                          </>
                        )}
                      </button>
                      <button className="px-3 py-1 bg-voka-border text-voka-gray rounded text-xs hover:bg-voka-magenta hover:text-white transition-colors">
                        <Settings className="w-3 h-3 inline mr-1" />
                        ⚙️
                      </button>
                      <button className="px-3 py-1 bg-voka-border text-voka-gray rounded text-xs hover:bg-voka-magenta hover:text-white transition-colors">
                        <BarChart className="w-3 h-3 inline mr-1" />📊
                      </button>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className="text-voka-gray text-sm">Never</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Maintenance Scheduler */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <h3 className="text-lg font-bold text-voka-white font-montserrat mb-4">📅 PROGRAMADOR DE MANTENIMIENTO</h3>

        <div className="bg-voka-dark border border-voka-border rounded-lg p-4 mb-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-voka-gray mb-1">Próximo Mantenimiento</div>
              <div className="text-lg font-semibold text-voka-white">Domingo 03:00-03:30 AM CET</div>
              <div className="text-sm text-voka-gray">
                Servicios Afectados: Todas las APIs, Base de Datos, Sistema de Archivos
              </div>
            </div>
            <div>
              <div className="text-sm text-voka-gray mb-1">Configuración</div>
              <div className="text-sm text-voka-white">
                <div>Notificación Previa: 30 minutos</div>
                <div>Auto-Reanudar: ✅ Habilitado</div>
              </div>
            </div>
          </div>

          <div className="flex gap-3 mt-4">
            <button className="px-4 py-2 bg-voka-magenta hover:bg-voka-magenta/80 text-white rounded font-semibold transition-colors">
              ✏️ Editar
            </button>
          </div>
        </div>

        <div className="bg-voka-dark border border-voka-border rounded-lg p-4">
          <h4 className="text-sm font-semibold text-voka-white mb-3">ACCIONES DE MANTENIMIENTO</h4>
          <div className="flex flex-wrap gap-3">
            <button className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded font-semibold transition-colors">
              🔧 INICIAR MANTENIMIENTO AHORA
            </button>
            <button className="px-4 py-2 bg-voka-border text-voka-gray rounded hover:bg-voka-magenta hover:text-white transition-colors">
              <Calendar className="w-4 h-4 inline mr-2" />⏰ PROGRAMAR
            </button>
            <button className="px-4 py-2 bg-voka-border text-voka-gray rounded hover:bg-voka-magenta hover:text-white transition-colors">
              📧 NOTIFICAR USUARIOS
            </button>
          </div>
        </div>
      </div>

      {/* Emergency Actions */}
      <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-6">
        <div className="flex items-center gap-3 mb-4">
          <AlertTriangle className="w-6 h-6 text-red-400" />
          <h3 className="text-lg font-bold text-red-400 font-montserrat">🚨 ACCIONES DE EMERGENCIA</h3>
        </div>

        <div className="text-sm text-red-300 mb-4">
          Estas acciones afectarán inmediatamente a todos los usuarios conectados. Usar solo en caso de emergencia.
        </div>

        <div className="flex gap-3">
          <button className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded font-semibold transition-colors">
            🛑 PARADA DE EMERGENCIA
          </button>
          <button className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded font-semibold transition-colors">
            🔄 REINICIO COMPLETO
          </button>
          <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded font-semibold transition-colors">
            💤 HIBERNAR SISTEMA
          </button>
        </div>
      </div>
    </div>
  )
}

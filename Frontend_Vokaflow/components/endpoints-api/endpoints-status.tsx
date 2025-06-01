"use client"

import { useState, useEffect } from "react"
import { RefreshCw, TrendingUp, TrendingDown, Minus } from "lucide-react"
import { apiEndpointsService } from "../../services/api-endpoints-service"
import type { ApiRouter } from "../../types/api-endpoints"

export function EndpointsStatus() {
  const [routers, setRouters] = useState<ApiRouter[]>([])
  const [metrics, setMetrics] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(true)

  useEffect(() => {
    loadData()

    if (autoRefresh) {
      const interval = setInterval(loadData, 30000) // Actualizar cada 30 segundos
      return () => clearInterval(interval)
    }
  }, [autoRefresh])

  const loadData = async () => {
    try {
      const [routersData, metricsData] = await Promise.all([
        apiEndpointsService.getApiRouters(),
        apiEndpointsService.getMonitoringMetrics(),
      ])
      setRouters(routersData)
      setMetrics(metricsData)
    } catch (error) {
      console.error("Error loading API status:", error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "online":
        return "text-green-400"
      case "slow":
        return "text-yellow-400"
      case "error":
        return "text-red-400"
      case "offline":
        return "text-gray-400"
      default:
        return "text-gray-400"
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "online":
        return "🟢"
      case "slow":
        return "🟡"
      case "error":
        return "🔴"
      case "offline":
        return "⚫"
      default:
        return "⚫"
    }
  }

  if (loading) {
    return (
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="w-8 h-8 text-voka-magenta animate-spin" />
          <span className="ml-3 text-voka-white font-montserrat">Cargando estado de endpoints...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Overview Stats */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-voka-white font-montserrat">📊 ESTADO GENERAL DE ENDPOINTS</h3>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                autoRefresh
                  ? "bg-voka-magenta text-white"
                  : "bg-voka-border text-voka-gray hover:bg-voka-magenta hover:text-white"
              }`}
            >
              🔄 Auto-refresh
            </button>
            <button
              onClick={loadData}
              className="px-3 py-1 bg-voka-border text-voka-gray rounded hover:bg-voka-magenta hover:text-white transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {metrics && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-voka-dark border border-green-500/20 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-green-400 font-montserrat">{metrics.healthy_endpoints}</div>
              <div className="text-sm text-green-300">🟢 HEALTHY</div>
              <div className="text-xs text-voka-gray">
                {((metrics.healthy_endpoints / metrics.total_endpoints) * 100).toFixed(1)}%
              </div>
            </div>
            <div className="bg-voka-dark border border-yellow-500/20 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-yellow-400 font-montserrat">{metrics.slow_endpoints}</div>
              <div className="text-sm text-yellow-300">🟡 SLOW</div>
              <div className="text-xs text-voka-gray">
                {((metrics.slow_endpoints / metrics.total_endpoints) * 100).toFixed(1)}%
              </div>
            </div>
            <div className="bg-voka-dark border border-red-500/20 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-red-400 font-montserrat">{metrics.error_endpoints}</div>
              <div className="text-sm text-red-300">🔴 ERRORS</div>
              <div className="text-xs text-voka-gray">
                {((metrics.error_endpoints / metrics.total_endpoints) * 100).toFixed(1)}%
              </div>
            </div>
            <div className="bg-voka-dark border border-voka-magenta/20 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-voka-magenta font-montserrat">{metrics.total_endpoints}</div>
              <div className="text-sm text-voka-magenta">📡 TOTAL</div>
              <div className="text-xs text-voka-gray">Endpoints</div>
            </div>
          </div>
        )}

        {/* Filtros */}
        <div className="flex flex-wrap gap-3 mb-4">
          <select className="bg-voka-dark border border-voka-border rounded px-3 py-1 text-voka-white text-sm">
            <option>Todos los Routers</option>
            <option>🏥 Health</option>
            <option>🧠 Vicky</option>
            <option>🌍 Translate</option>
          </select>
          <select className="bg-voka-dark border border-voka-border rounded px-3 py-1 text-voka-white text-sm">
            <option>Estado: Todos</option>
            <option>🟢 Healthy</option>
            <option>🟡 Slow</option>
            <option>🔴 Error</option>
          </select>
          <select className="bg-voka-dark border border-voka-border rounded px-3 py-1 text-voka-white text-sm">
            <option>Método: Todos</option>
            <option>GET</option>
            <option>POST</option>
            <option>PUT</option>
            <option>DELETE</option>
          </select>
        </div>
      </div>

      {/* Routers Table */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-voka-dark border-b border-voka-border">
              <tr>
                <th className="text-left p-4 text-voka-white font-montserrat font-semibold">ROUTER</th>
                <th className="text-left p-4 text-voka-white font-montserrat font-semibold">ENDPOINTS</th>
                <th className="text-left p-4 text-voka-white font-montserrat font-semibold">ESTADO</th>
                <th className="text-left p-4 text-voka-white font-montserrat font-semibold">LATENCIA</th>
                <th className="text-left p-4 text-voka-white font-montserrat font-semibold">ACCIONES</th>
              </tr>
            </thead>
            <tbody>
              {routers.map((router, index) => (
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
                    <div className="text-voka-white">
                      <span className="font-bold">{router.totalEndpoints}</span>
                      <span className="text-voka-gray text-sm ml-2">endpoints</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <span>{getStatusIcon(router.status)}</span>
                      <span className={`font-medium ${getStatusColor(router.status)}`}>
                        {router.status.toUpperCase()}
                      </span>
                      <span className="text-voka-gray text-sm">
                        ({router.healthyEndpoints}/{router.totalEndpoints})
                      </span>
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="text-voka-white">
                      <span className="font-mono">
                        {router.name === "vicky"
                          ? "245ms"
                          : router.name === "translate"
                            ? "145ms"
                            : router.name === "health"
                              ? "12ms"
                              : "45-120ms"}
                      </span>
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="flex gap-2">
                      <button className="px-2 py-1 bg-voka-border text-voka-gray rounded text-xs hover:bg-voka-magenta hover:text-white transition-colors">
                        ⏸️
                      </button>
                      <button className="px-2 py-1 bg-voka-border text-voka-gray rounded text-xs hover:bg-voka-magenta hover:text-white transition-colors">
                        ⚙️
                      </button>
                      <button className="px-2 py-1 bg-voka-border text-voka-gray rounded text-xs hover:bg-voka-magenta hover:text-white transition-colors">
                        📊
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Performance Chart */}
      {metrics && (
        <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
          <h3 className="text-lg font-bold text-voka-white font-montserrat mb-4">
            📈 MÉTRICAS DE RENDIMIENTO (Últimas 24 Horas)
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-voka-dark border border-voka-border rounded-lg p-4">
              <div className="text-sm text-voka-gray mb-1">Tasa de Éxito</div>
              <div className="text-2xl font-bold text-green-400 font-montserrat">{metrics.success_rate}%</div>
              <div className="flex items-center gap-1 text-xs text-green-300">
                <TrendingUp className="w-3 h-3" />
                +0.2% vs ayer
              </div>
            </div>
            <div className="bg-voka-dark border border-voka-border rounded-lg p-4">
              <div className="text-sm text-voka-gray mb-1">Tasa de Error</div>
              <div className="text-2xl font-bold text-red-400 font-montserrat">{metrics.error_rate}%</div>
              <div className="flex items-center gap-1 text-xs text-red-300">
                <TrendingDown className="w-3 h-3" />
                -0.1% vs ayer
              </div>
            </div>
            <div className="bg-voka-dark border border-voka-border rounded-lg p-4">
              <div className="text-sm text-voka-gray mb-1">Respuesta Promedio</div>
              <div className="text-2xl font-bold text-voka-magenta font-montserrat">{metrics.avg_response_time}ms</div>
              <div className="flex items-center gap-1 text-xs text-voka-gray">
                <Minus className="w-3 h-3" />
                Sin cambios
              </div>
            </div>
          </div>

          <div className="bg-voka-dark border border-voka-border rounded-lg p-4">
            <div className="text-sm text-voka-gray mb-2">Volumen de Peticiones</div>
            <div className="flex items-baseline gap-4">
              <span className="text-lg font-bold text-voka-white">
                Pico: {metrics.requests_per_hour.toLocaleString()} req/h
              </span>
              <span className="text-sm text-voka-gray">P95: 280ms</span>
            </div>

            {/* Gráfico ASCII simple */}
            <div className="mt-4 font-mono text-xs text-voka-gray">
              <div>Response Time (ms)</div>
              <div>1000 │ ████</div>
              <div> 800 │ █████</div>
              <div> 600 │ ██████ ███</div>
              <div> 400 │████████████</div>
              <div> 200 │████████████████</div>
              <div> 0 │────────────────────────────</div>
              <div> │00 04 08 12 16 20 24</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

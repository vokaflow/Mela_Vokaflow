"use client"

import { useState, useEffect } from "react"
import { Search, Download, Eye, TrendingUp, TrendingDown } from "lucide-react"
import { apiEndpointsService } from "../../services/api-endpoints-service"
import type { ApiMetrics } from "../../types/api-endpoints"

export function EndpointsHistory() {
  const [requests, setRequests] = useState<ApiMetrics[]>([])
  const [filteredRequests, setFilteredRequests] = useState<ApiMetrics[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedRequest, setSelectedRequest] = useState<ApiMetrics | null>(null)
  const [filters, setFilters] = useState({
    timeRange: "24h",
    status: "all",
    method: "all",
    user: "all",
  })

  useEffect(() => {
    loadHistory()
  }, [])

  useEffect(() => {
    filterRequests()
  }, [requests, searchTerm, filters])

  const loadHistory = async () => {
    try {
      const data = await apiEndpointsService.getApiMetrics()
      // Generar más datos de historial para la demo
      const extendedData = generateMockHistory(data)
      setRequests(extendedData)
    } catch (error) {
      console.error("Error loading request history:", error)
    } finally {
      setLoading(false)
    }
  }

  const generateMockHistory = (baseData: ApiMetrics[]): ApiMetrics[] => {
    const mockRequests: ApiMetrics[] = []
    const endpoints = [
      "/api/health/status",
      "/api/vicky/process",
      "/api/translate/",
      "/api/users/me",
      "/api/files/upload",
      "/api/analytics/usage",
      "/api/translate/history",
      "/api/monitoring/metrics",
    ]
    const methods = ["GET", "POST", "PUT", "DELETE"]
    const statusCodes = [200, 201, 400, 401, 404, 429, 500]

    for (let i = 0; i < 50; i++) {
      const timestamp = new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000)
      const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)]
      const method = methods[Math.floor(Math.random() * methods.length)]
      const status = statusCodes[Math.floor(Math.random() * statusCodes.length)]

      mockRequests.push({
        endpoint,
        method,
        status_code: status,
        response_time: status >= 400 ? (status === 500 ? 30000 : Math.random() * 1000) : Math.random() * 500,
        timestamp: timestamp.toISOString(),
        user_id: "dw7",
        ip_address: "192.168.1.119",
        error_message: status >= 400 ? getErrorMessage(status) : undefined,
      })
    }

    return [...baseData, ...mockRequests].sort(
      (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime(),
    )
  }

  const getErrorMessage = (status: number): string => {
    switch (status) {
      case 400:
        return "Bad Request - Invalid parameters"
      case 401:
        return "Unauthorized - Invalid credentials"
      case 404:
        return "Not Found - Endpoint does not exist"
      case 429:
        return "Rate Limited - Too many requests"
      case 500:
        return "Internal Server Error - Database connection timeout"
      default:
        return "Unknown error"
    }
  }

  const filterRequests = () => {
    let filtered = requests

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(
        (req) =>
          req.endpoint.toLowerCase().includes(searchTerm.toLowerCase()) ||
          req.method.toLowerCase().includes(searchTerm.toLowerCase()) ||
          req.user_id?.toLowerCase().includes(searchTerm.toLowerCase()),
      )
    }

    // Filter by status
    if (filters.status !== "all") {
      if (filters.status === "success") {
        filtered = filtered.filter((req) => req.status_code >= 200 && req.status_code < 300)
      } else if (filters.status === "error") {
        filtered = filtered.filter((req) => req.status_code >= 400)
      }
    }

    // Filter by method
    if (filters.method !== "all") {
      filtered = filtered.filter((req) => req.method === filters.method)
    }

    setFilteredRequests(filtered)
  }

  const getStatusIcon = (status: number) => {
    if (status >= 200 && status < 300) return "🟢"
    if (status >= 300 && status < 400) return "🟡"
    if (status >= 400) return "🔴"
    return "⚫"
  }

  const getStatusColor = (status: number) => {
    if (status >= 200 && status < 300) return "text-green-400"
    if (status >= 300 && status < 400) return "text-yellow-400"
    if (status >= 400) return "text-red-400"
    return "text-gray-400"
  }

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString("es-ES", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    })
  }

  const formatResponseTime = (time: number) => {
    if (time >= 30000) return "TIMEOUT"
    return `${Math.round(time)}ms`
  }

  const exportHistory = () => {
    const csv = [
      "Timestamp,Method,Endpoint,Status,Response Time,User,IP",
      ...filteredRequests.map(
        (req) =>
          `${req.timestamp},${req.method},${req.endpoint},${req.status_code},${req.response_time},${req.user_id},${req.ip_address}`,
      ),
    ].join("\n")

    const blob = new Blob([csv], { type: "text/csv" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "api-history.csv"
    a.click()
  }

  // Calculate error analytics
  const errorAnalytics = requests.reduce(
    (acc, req) => {
      if (req.status_code >= 400) {
        const errorType = `${req.status_code} ${getErrorMessage(req.status_code).split(" - ")[0]}`
        acc[errorType] = (acc[errorType] || 0) + 1
      }
      return acc
    },
    {} as Record<string, number>,
  )

  const totalRequests = requests.length
  const successRate = (
    (requests.filter((r) => r.status_code >= 200 && r.status_code < 300).length / totalRequests) *
    100
  ).toFixed(1)
  const errorRate = ((requests.filter((r) => r.status_code >= 400).length / totalRequests) * 100).toFixed(1)

  if (loading) {
    return (
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-2 border-voka-magenta border-t-transparent rounded-full animate-spin"></div>
          <span className="ml-3 text-voka-white font-montserrat">Cargando historial de peticiones...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Filters and Search */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-voka-white font-montserrat">📋 HISTORIAL DE PETICIONES API</h3>
          <div className="flex gap-3">
            <button
              onClick={exportHistory}
              className="px-3 py-1 bg-voka-border text-voka-gray rounded hover:bg-voka-magenta hover:text-white transition-colors text-sm"
            >
              <Download className="w-4 h-4 inline mr-1" />📄 Export
            </button>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-wrap gap-3 mb-4">
          <div className="flex-1 min-w-64">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-voka-gray" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Buscar endpoints, métodos, usuarios..."
                className="w-full pl-10 pr-4 py-2 bg-voka-dark border border-voka-border rounded text-voka-white text-sm"
              />
            </div>
          </div>

          <select
            value={filters.timeRange}
            onChange={(e) => setFilters({ ...filters, timeRange: e.target.value })}
            className="bg-voka-dark border border-voka-border rounded px-3 py-2 text-voka-white text-sm"
          >
            <option value="1h">Última hora</option>
            <option value="24h">Últimas 24h</option>
            <option value="7d">Últimos 7 días</option>
            <option value="30d">Últimos 30 días</option>
          </select>

          <select
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            className="bg-voka-dark border border-voka-border rounded px-3 py-2 text-voka-white text-sm"
          >
            <option value="all">Todos los estados</option>
            <option value="success">🟢 Éxito</option>
            <option value="error">🔴 Error</option>
          </select>

          <select
            value={filters.method}
            onChange={(e) => setFilters({ ...filters, method: e.target.value })}
            className="bg-voka-dark border border-voka-border rounded px-3 py-2 text-voka-white text-sm"
          >
            <option value="all">Todos los métodos</option>
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="DELETE">DELETE</option>
          </select>

          <select
            value={filters.user}
            onChange={(e) => setFilters({ ...filters, user: e.target.value })}
            className="bg-voka-dark border border-voka-border rounded px-3 py-2 text-voka-white text-sm"
          >
            <option value="all">Todos los usuarios</option>
            <option value="dw7">dw7</option>
          </select>
        </div>
      </div>

      {/* Request History Table */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-voka-dark border-b border-voka-border">
              <tr>
                <th className="text-left p-4 text-voka-white font-montserrat font-semibold">TIEMPO</th>
                <th className="text-left p-4 text-voka-white font-montserrat font-semibold">MÉTODO</th>
                <th className="text-left p-4 text-voka-white font-montserrat font-semibold">ENDPOINT</th>
                <th className="text-left p-4 text-voka-white font-montserrat font-semibold">ESTADO</th>
                <th className="text-left p-4 text-voka-white font-montserrat font-semibold">TIEMPO</th>
                <th className="text-left p-4 text-voka-white font-montserrat font-semibold">USUARIO</th>
                <th className="text-left p-4 text-voka-white font-montserrat font-semibold">ACCIONES</th>
              </tr>
            </thead>
            <tbody>
              {filteredRequests.slice(0, 20).map((request, index) => (
                <tr key={index} className="border-b border-voka-border/30 hover:bg-voka-dark/30 transition-colors">
                  <td className="p-4">
                    <span className="text-voka-white font-mono text-sm">{formatTime(request.timestamp)}</span>
                  </td>
                  <td className="p-4">
                    <span
                      className={`px-2 py-1 rounded text-xs font-mono font-semibold ${
                        request.method === "GET"
                          ? "bg-blue-600/20 text-blue-300"
                          : request.method === "POST"
                            ? "bg-green-600/20 text-green-300"
                            : request.method === "PUT"
                              ? "bg-yellow-600/20 text-yellow-300"
                              : request.method === "DELETE"
                                ? "bg-red-600/20 text-red-300"
                                : "bg-gray-600/20 text-gray-300"
                      }`}
                    >
                      {request.method}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className="text-voka-white font-mono text-sm">{request.endpoint}</span>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <span>{getStatusIcon(request.status_code)}</span>
                      <span className={`font-semibold ${getStatusColor(request.status_code)}`}>
                        {request.status_code}
                      </span>
                    </div>
                  </td>
                  <td className="p-4">
                    <span
                      className={`font-mono text-sm ${
                        request.response_time > 1000
                          ? "text-red-400"
                          : request.response_time > 500
                            ? "text-yellow-400"
                            : "text-voka-white"
                      }`}
                    >
                      {formatResponseTime(request.response_time)}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className="text-voka-white text-sm">{request.user_id}</span>
                  </td>
                  <td className="p-4">
                    <button
                      onClick={() => setSelectedRequest(request)}
                      className="px-2 py-1 bg-voka-border text-voka-gray rounded text-xs hover:bg-voka-magenta hover:text-white transition-colors"
                    >
                      <Eye className="w-3 h-3 inline mr-1" />
                      Ver
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Error Analytics */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <h3 className="text-lg font-bold text-voka-white font-montserrat mb-4">🚨 ANÁLISIS DE ERRORES</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="border-b border-voka-border">
                  <tr>
                    <th className="text-left p-3 text-voka-white font-semibold text-sm">TIPO DE ERROR</th>
                    <th className="text-left p-3 text-voka-white font-semibold text-sm">COUNT</th>
                    <th className="text-left p-3 text-voka-white font-semibold text-sm">%</th>
                    <th className="text-left p-3 text-voka-white font-semibold text-sm">TREND</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(errorAnalytics).map(([errorType, count]) => (
                    <tr key={errorType} className="border-b border-voka-border/30">
                      <td className="p-3 text-voka-white text-sm">{errorType}</td>
                      <td className="p-3 text-voka-white font-mono">{count}</td>
                      <td className="p-3 text-voka-white font-mono">{((count / totalRequests) * 100).toFixed(1)}%</td>
                      <td className="p-3">
                        {Math.random() > 0.5 ? (
                          <div className="flex items-center gap-1 text-red-300 text-xs">
                            <TrendingUp className="w-3 h-3" />+{Math.floor(Math.random() * 50)}%
                          </div>
                        ) : (
                          <div className="flex items-center gap-1 text-green-300 text-xs">
                            <TrendingDown className="w-3 h-3" />-{Math.floor(Math.random() * 30)}%
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="space-y-4">
            <div className="bg-voka-dark border border-voka-border rounded-lg p-4">
              <div className="text-sm text-voka-gray mb-1">Total de Peticiones Hoy</div>
              <div className="text-2xl font-bold text-voka-white font-montserrat">{totalRequests.toLocaleString()}</div>
            </div>
            <div className="bg-voka-dark border border-voka-border rounded-lg p-4">
              <div className="text-sm text-voka-gray mb-1">Tasa de Éxito</div>
              <div className="text-2xl font-bold text-green-400 font-montserrat">{successRate}%</div>
            </div>
            <div className="bg-voka-dark border border-voka-border rounded-lg p-4">
              <div className="text-sm text-voka-gray mb-1">Tasa de Error</div>
              <div className="text-2xl font-bold text-red-400 font-montserrat">{errorRate}%</div>
            </div>
          </div>
        </div>
      </div>

      {/* Request Details Modal */}
      {selectedRequest && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-voka-blue-black border border-voka-border rounded-lg max-w-2xl w-full max-h-[80vh] overflow-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-voka-white font-montserrat">🔍 DETALLES DE REQUEST</h3>
                <button
                  onClick={() => setSelectedRequest(null)}
                  className="text-voka-gray hover:text-white transition-colors"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-voka-gray">Timestamp</div>
                    <div className="text-voka-white font-mono">{selectedRequest.timestamp}</div>
                  </div>
                  <div>
                    <div className="text-sm text-voka-gray">Método</div>
                    <div className="text-voka-white font-mono">{selectedRequest.method}</div>
                  </div>
                  <div>
                    <div className="text-sm text-voka-gray">Endpoint</div>
                    <div className="text-voka-white font-mono">{selectedRequest.endpoint}</div>
                  </div>
                  <div>
                    <div className="text-sm text-voka-gray">Estado</div>
                    <div className={`font-semibold ${getStatusColor(selectedRequest.status_code)}`}>
                      {getStatusIcon(selectedRequest.status_code)} {selectedRequest.status_code}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-voka-gray">Tiempo de Respuesta</div>
                    <div className="text-voka-white font-mono">{formatResponseTime(selectedRequest.response_time)}</div>
                  </div>
                  <div>
                    <div className="text-sm text-voka-gray">Usuario</div>
                    <div className="text-voka-white">
                      {selectedRequest.user_id} ({selectedRequest.ip_address})
                    </div>
                  </div>
                </div>

                {selectedRequest.error_message && (
                  <div>
                    <div className="text-sm text-voka-gray mb-2">Detalles del Error</div>
                    <div className="bg-red-900/20 border border-red-500/30 rounded p-3 text-red-300 font-mono text-sm">
                      {selectedRequest.error_message}
                    </div>
                  </div>
                )}

                <div className="flex gap-3 pt-4">
                  <button className="px-4 py-2 bg-voka-border text-voka-gray rounded hover:bg-voka-magenta hover:text-white transition-colors">
                    📋 Copiar
                  </button>
                  <button className="px-4 py-2 bg-voka-border text-voka-gray rounded hover:bg-voka-magenta hover:text-white transition-colors">
                    🔄 Reintentar Request
                  </button>
                  {selectedRequest.status_code >= 400 && (
                    <button className="px-4 py-2 bg-voka-border text-voka-gray rounded hover:bg-voka-magenta hover:text-white transition-colors">
                      🐛 Reportar Bug
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

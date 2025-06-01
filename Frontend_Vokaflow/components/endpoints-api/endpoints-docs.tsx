"use client"

import { useState, useEffect } from "react"
import { RefreshCw, Search, ExternalLink, Copy, Download } from "lucide-react"
import { apiEndpointsService } from "../../services/api-endpoints-service"

export function EndpointsDocs() {
  const [schema, setSchema] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedEndpoint, setSelectedEndpoint] = useState<any>(null)
  const [expandedRouters, setExpandedRouters] = useState<Set<string>>(new Set(["health", "vicky", "translate"]))

  useEffect(() => {
    loadSchema()
  }, [])

  const loadSchema = async () => {
    try {
      const schemaData = await apiEndpointsService.loadApiSchema()
      setSchema(schemaData)
    } catch (error) {
      console.error("Error loading API schema:", error)
    } finally {
      setLoading(false)
    }
  }

  const organizeEndpoints = () => {
    if (!schema?.paths) return {}

    const organized: Record<string, any[]> = {}

    Object.entries(schema.paths).forEach(([path, methods]: [string, any]) => {
      const router = path.split("/")[2] || "root" // Extract router from path

      if (!organized[router]) {
        organized[router] = []
      }

      Object.entries(methods).forEach(([method, details]: [string, any]) => {
        organized[router].push({
          path,
          method: method.toUpperCase(),
          summary: details.summary || "No description",
          description: details.description || "",
          parameters: details.parameters || [],
          requestBody: details.requestBody,
          responses: details.responses || {},
        })
      })
    })

    return organized
  }

  const getRouterIcon = (router: string) => {
    const icons: Record<string, string> = {
      health: "🏥",
      vicky: "🧠",
      translate: "🌍",
      conversations: "💬",
      files: "📁",
      system: "🔧",
      models: "🧬",
      analytics: "📊",
      notifications: "🔔",
      admin: "👑",
      "api-keys": "🔑",
      webhooks: "🔗",
      monitoring: "📡",
      kinect: "🎮",
      users: "👥",
      auth: "🔐",
    }
    return icons[router] || "📡"
  }

  const getMethodColor = (method: string) => {
    switch (method) {
      case "GET":
        return "bg-blue-600/20 text-blue-300 border-blue-500/30"
      case "POST":
        return "bg-green-600/20 text-green-300 border-green-500/30"
      case "PUT":
        return "bg-yellow-600/20 text-yellow-300 border-yellow-500/30"
      case "DELETE":
        return "bg-red-600/20 text-red-300 border-red-500/30"
      case "PATCH":
        return "bg-purple-600/20 text-purple-300 border-purple-500/30"
      default:
        return "bg-gray-600/20 text-gray-300 border-gray-500/30"
    }
  }

  const toggleRouter = (router: string) => {
    const newExpanded = new Set(expandedRouters)
    if (newExpanded.has(router)) {
      newExpanded.delete(router)
    } else {
      newExpanded.add(router)
    }
    setExpandedRouters(newExpanded)
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const exportSchema = () => {
    const blob = new Blob([JSON.stringify(schema, null, 2)], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "vokaflow-api-schema.json"
    a.click()
  }

  const organizedEndpoints = organizeEndpoints()
  const totalEndpoints = Object.values(organizedEndpoints).reduce((sum, endpoints) => sum + endpoints.length, 0)

  if (loading) {
    return (
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="w-8 h-8 text-voka-magenta animate-spin" />
          <span className="ml-3 text-voka-white font-montserrat">Cargando documentación API...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-voka-white font-montserrat">📚 DOCUMENTACIÓN API</h3>
          <button
            onClick={loadSchema}
            className="px-3 py-1 bg-voka-border text-voka-gray rounded hover:bg-voka-magenta hover:text-white transition-colors"
          >
            <RefreshCw className="w-4 h-4 inline mr-1" />🔄 Refresh Schema
          </button>
        </div>

        {/* Search */}
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-voka-gray" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Buscar endpoints..."
            className="w-full pl-10 pr-4 py-2 bg-voka-dark border border-voka-border rounded text-voka-white"
          />
        </div>

        <div className="text-sm text-voka-gray">📂 Estructura API ({totalEndpoints} endpoints total)</div>
      </div>

      {/* API Structure */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg overflow-hidden">
        <div className="p-4">
          {Object.entries(organizedEndpoints).map(([router, endpoints]) => {
            const filteredEndpoints = endpoints.filter(
              (endpoint) =>
                searchTerm === "" ||
                endpoint.path.toLowerCase().includes(searchTerm.toLowerCase()) ||
                endpoint.summary.toLowerCase().includes(searchTerm.toLowerCase()),
            )

            if (filteredEndpoints.length === 0 && searchTerm !== "") return null

            return (
              <div key={router} className="mb-4">
                <button
                  onClick={() => toggleRouter(router)}
                  className="flex items-center gap-3 w-full text-left p-3 bg-voka-dark border border-voka-border rounded hover:border-voka-magenta transition-colors"
                >
                  <span className="text-xl">{getRouterIcon(router)}</span>
                  <span className="text-voka-white font-semibold">{router}</span>
                  <span className="text-voka-gray text-sm">({filteredEndpoints.length} endpoints)</span>
                  <span className="ml-auto text-voka-gray">{expandedRouters.has(router) ? "▼" : "▶"}</span>
                  <button className="px-2 py-1 bg-voka-border text-voka-gray rounded text-xs hover:bg-voka-magenta hover:text-white transition-colors">
                    📊 Test
                  </button>
                </button>

                {expandedRouters.has(router) && (
                  <div className="mt-2 ml-6 space-y-2">
                    {filteredEndpoints.map((endpoint, index) => (
                      <div
                        key={index}
                        className="flex items-center gap-3 p-3 bg-voka-dark/50 border border-voka-border/50 rounded hover:border-voka-magenta/50 transition-colors cursor-pointer"
                        onClick={() => setSelectedEndpoint(endpoint)}
                      >
                        <span
                          className={`px-2 py-1 rounded text-xs font-mono font-semibold border ${getMethodColor(endpoint.method)}`}
                        >
                          {endpoint.method}
                        </span>
                        <span className="text-voka-white font-mono text-sm flex-1">{endpoint.path}</span>
                        <span className="text-voka-gray text-sm">{endpoint.summary}</span>
                        <ExternalLink className="w-4 h-4 text-voka-gray" />
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Export Options */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <h3 className="text-lg font-bold text-voka-white font-montserrat mb-4">📄 EXPORTAR E INTEGRACIÓN</h3>

        <div className="flex flex-wrap gap-3 mb-6">
          <button
            onClick={() => copyToClipboard(JSON.stringify(schema, null, 2))}
            className="px-4 py-2 bg-voka-border text-voka-gray rounded hover:bg-voka-magenta hover:text-white transition-colors"
          >
            <Copy className="w-4 h-4 inline mr-2" />📋 Copy OpenAPI JSON
          </button>
          <button
            onClick={exportSchema}
            className="px-4 py-2 bg-voka-border text-voka-gray rounded hover:bg-voka-magenta hover:text-white transition-colors"
          >
            <Download className="w-4 h-4 inline mr-2" />💾 Download Schema
          </button>
          <button className="px-4 py-2 bg-voka-border text-voka-gray rounded hover:bg-voka-magenta hover:text-white transition-colors">
            <ExternalLink className="w-4 h-4 inline mr-2" />🔗 External Links
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <h4 className="text-sm font-semibold text-voka-white mb-2">ENLACES DE INTEGRACIÓN</h4>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <span className="text-voka-gray">📚 Swagger UI:</span>
                <a
                  href="http://localhost:8000/docs"
                  target="_blank"
                  className="text-voka-magenta hover:underline font-mono"
                  rel="noreferrer"
                >
                  http://localhost:8000/docs
                </a>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-voka-gray">📖 ReDoc:</span>
                <a
                  href="http://localhost:8000/redoc"
                  target="_blank"
                  className="text-voka-magenta hover:underline font-mono"
                  rel="noreferrer"
                >
                  http://localhost:8000/redoc
                </a>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-voka-gray">🔧 OpenAPI JSON:</span>
                <a
                  href="http://localhost:8000/openapi.json"
                  target="_blank"
                  className="text-voka-magenta hover:underline font-mono"
                  rel="noreferrer"
                >
                  http://localhost:8000/openapi.json
                </a>
              </div>
            </div>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-voka-white mb-2">GENERACIÓN DE SDK</h4>
            <div className="flex flex-wrap gap-2">
              <button className="px-3 py-1 bg-voka-border text-voka-gray rounded text-sm hover:bg-voka-magenta hover:text-white transition-colors">
                🐍 Python SDK
              </button>
              <button className="px-3 py-1 bg-voka-border text-voka-gray rounded text-sm hover:bg-voka-magenta hover:text-white transition-colors">
                📱 JavaScript SDK
              </button>
              <button className="px-3 py-1 bg-voka-border text-voka-gray rounded text-sm hover:bg-voka-magenta hover:text-white transition-colors">
                ☕ Java SDK
              </button>
              <button className="px-3 py-1 bg-voka-border text-voka-gray rounded text-sm hover:bg-voka-magenta hover:text-white transition-colors">
                🦀 Rust SDK
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Endpoint Details Modal */}
      {selectedEndpoint && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-voka-blue-black border border-voka-border rounded-lg max-w-4xl w-full max-h-[80vh] overflow-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <span
                    className={`px-3 py-1 rounded font-mono font-semibold border ${getMethodColor(selectedEndpoint.method)}`}
                  >
                    {selectedEndpoint.method}
                  </span>
                  <span className="text-lg font-bold text-voka-white font-mono">{selectedEndpoint.path}</span>
                </div>
                <div className="flex gap-2">
                  <button className="px-3 py-1 bg-voka-magenta text-white rounded hover:bg-voka-magenta/80 transition-colors">
                    🧪 Try it out
                  </button>
                  <button
                    onClick={() => setSelectedEndpoint(null)}
                    className="text-voka-gray hover:text-white transition-colors"
                  >
                    ✕
                  </button>
                </div>
              </div>

              <div className="space-y-6">
                {/* Description */}
                <div>
                  <h4 className="text-sm font-semibold text-voka-white mb-2">📝 DESCRIPCIÓN</h4>
                  <p className="text-voka-gray">{selectedEndpoint.summary}</p>
                  {selectedEndpoint.description && (
                    <p className="text-voka-gray mt-2">{selectedEndpoint.description}</p>
                  )}
                </div>

                {/* Request Schema */}
                {selectedEndpoint.requestBody && (
                  <div>
                    <h4 className="text-sm font-semibold text-voka-white mb-2">📥 REQUEST SCHEMA</h4>
                    <div className="bg-voka-dark border border-voka-border rounded p-4 font-mono text-sm">
                      <pre className="text-voka-white whitespace-pre-wrap">
                        {JSON.stringify(
                          {
                            message: "string (required, 1-10000 chars)",
                            personality: "balanced|technical|creative|analytical",
                            context: { user_id: "string", session_id: "string" },
                            temperature: "number (0.0-2.0, default: 0.7)",
                          },
                          null,
                          2,
                        )}
                      </pre>
                    </div>
                  </div>
                )}

                {/* Response Schema */}
                <div>
                  <h4 className="text-sm font-semibold text-voka-white mb-2">📤 RESPONSE SCHEMA</h4>
                  <div className="bg-voka-dark border border-voka-border rounded p-4 font-mono text-sm">
                    <pre className="text-voka-white whitespace-pre-wrap">
                      {JSON.stringify(
                        {
                          response: "string",
                          metadata: {
                            processingTime: "number",
                            hemisphere: { technical: "number", emotional: "number" },
                          },
                        },
                        null,
                        2,
                      )}
                    </pre>
                  </div>
                </div>

                {/* Response Codes */}
                <div>
                  <h4 className="text-sm font-semibold text-voka-white mb-2">📊 CÓDIGOS DE RESPUESTA</h4>
                  <div className="grid grid-cols-3 gap-3">
                    <div className="bg-green-600/20 border border-green-500/30 rounded p-3 text-center">
                      <div className="text-green-300 font-semibold">200</div>
                      <div className="text-xs text-green-400">Success</div>
                    </div>
                    <div className="bg-red-600/20 border border-red-500/30 rounded p-3 text-center">
                      <div className="text-red-300 font-semibold">400</div>
                      <div className="text-xs text-red-400">Bad Request</div>
                    </div>
                    <div className="bg-red-600/20 border border-red-500/30 rounded p-3 text-center">
                      <div className="text-red-300 font-semibold">500</div>
                      <div className="text-xs text-red-400">Server Error</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

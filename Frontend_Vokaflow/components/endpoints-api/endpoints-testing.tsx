"use client"

import { useState } from "react"
import { Play, Trash2 } from "lucide-react"
import { apiEndpointsService } from "../../services/api-endpoints-service"
import type { TestRequest, TestResponse } from "../../types/api-endpoints"

export function EndpointsTesting() {
  const [request, setRequest] = useState<TestRequest>({
    method: "GET",
    url: "http://localhost:8000/api/health/status",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    auth: {
      type: "bearer",
      value: "sk-vkf-test-key-123",
    },
  })

  const [response, setResponse] = useState<TestResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [savedRequests, setSavedRequests] = useState<any[]>([])

  const quickTests = [
    {
      name: "🏥 Health Check",
      method: "GET",
      url: "http://localhost:8000/api/health/status",
      body: null,
    },
    {
      name: "🧠 Vicky Chat",
      method: "POST",
      url: "http://localhost:8000/api/vicky/process",
      body: {
        message: "Hola Vicky, ¿cómo estás?",
        personality: "balanced",
        context: { user_id: "dw7", session_id: "test_session" },
      },
    },
    {
      name: "🌍 Translation",
      method: "POST",
      url: "http://localhost:8000/api/translate/",
      body: {
        text: "Hello world",
        source_lang: "en",
        target_lang: "es",
      },
    },
    {
      name: "👤 User Info",
      method: "GET",
      url: "http://localhost:8000/api/users/me",
      body: null,
    },
  ]

  const executeRequest = async () => {
    setLoading(true)
    try {
      const result = await apiEndpointsService.executeApiTest(request)
      setResponse(result)
    } catch (error) {
      console.error("Error executing request:", error)
    } finally {
      setLoading(false)
    }
  }

  const loadQuickTest = (test: any) => {
    setRequest({
      ...request,
      method: test.method,
      url: test.url,
      body: test.body,
    })
    setResponse(null)
  }

  const updateHeader = (key: string, value: string) => {
    setRequest({
      ...request,
      headers: {
        ...request.headers,
        [key]: value,
      },
    })
  }

  const addHeader = () => {
    const key = prompt("Nombre del header:")
    const value = prompt("Valor del header:")
    if (key && value) {
      updateHeader(key, value)
    }
  }

  const removeHeader = (key: string) => {
    const newHeaders = { ...request.headers }
    delete newHeaders[key]
    setRequest({ ...request, headers: newHeaders })
  }

  const getStatusColor = (status: number) => {
    if (status >= 200 && status < 300) return "text-green-400"
    if (status >= 300 && status < 400) return "text-yellow-400"
    if (status >= 400) return "text-red-400"
    return "text-gray-400"
  }

  const getStatusIcon = (status: number) => {
    if (status >= 200 && status < 300) return "🟢"
    if (status >= 300 && status < 400) return "🟡"
    if (status >= 400) return "🔴"
    return "⚫"
  }

  return (
    <div className="space-y-6">
      {/* Request Builder */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <h3 className="text-xl font-bold text-voka-white font-montserrat mb-6">🧪 INTERFAZ DE TESTING API</h3>

        {/* Method and URL */}
        <div className="flex gap-3 mb-4">
          <select
            value={request.method}
            onChange={(e) => setRequest({ ...request, method: e.target.value })}
            className="bg-voka-dark border border-voka-border rounded px-3 py-2 text-voka-white font-mono"
          >
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="DELETE">DELETE</option>
            <option value="PATCH">PATCH</option>
          </select>
          <input
            type="text"
            value={request.url}
            onChange={(e) => setRequest({ ...request, url: e.target.value })}
            className="flex-1 bg-voka-dark border border-voka-border rounded px-3 py-2 text-voka-white font-mono"
            placeholder="http://localhost:8000/api/..."
          />
          <button className="px-4 py-2 bg-voka-border text-voka-gray rounded hover:bg-voka-magenta hover:text-white transition-colors">
            📚 Examples
          </button>
        </div>

        {/* Authentication */}
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-voka-white mb-2">🔑 AUTENTICACIÓN</h4>
          <div className="flex gap-3">
            <select
              value={request.auth?.type || "bearer"}
              onChange={(e) =>
                setRequest({
                  ...request,
                  auth: { ...request.auth!, type: e.target.value as "bearer" | "apikey" },
                })
              }
              className="bg-voka-dark border border-voka-border rounded px-3 py-2 text-voka-white"
            >
              <option value="bearer">Bearer Token</option>
              <option value="apikey">API Key</option>
            </select>
            <input
              type="text"
              value={request.auth?.value || ""}
              onChange={(e) =>
                setRequest({
                  ...request,
                  auth: { ...request.auth!, value: e.target.value },
                })
              }
              className="flex-1 bg-voka-dark border border-voka-border rounded px-3 py-2 text-voka-white font-mono"
              placeholder="sk-vkf-•••••••••••••••••••••••"
            />
          </div>
        </div>

        {/* Headers */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-semibold text-voka-white">📋 HEADERS</h4>
            <button
              onClick={addHeader}
              className="text-xs px-2 py-1 bg-voka-border text-voka-gray rounded hover:bg-voka-magenta hover:text-white transition-colors"
            >
              + Add Header
            </button>
          </div>
          <div className="space-y-2">
            {Object.entries(request.headers).map(([key, value]) => (
              <div key={key} className="flex gap-2">
                <input
                  type="text"
                  value={key}
                  onChange={(e) => {
                    const newHeaders = { ...request.headers }
                    delete newHeaders[key]
                    newHeaders[e.target.value] = value
                    setRequest({ ...request, headers: newHeaders })
                  }}
                  className="flex-1 bg-voka-dark border border-voka-border rounded px-3 py-1 text-voka-white text-sm"
                />
                <input
                  type="text"
                  value={value}
                  onChange={(e) => updateHeader(key, e.target.value)}
                  className="flex-1 bg-voka-dark border border-voka-border rounded px-3 py-1 text-voka-white text-sm"
                />
                <button
                  onClick={() => removeHeader(key)}
                  className="px-2 py-1 text-red-400 hover:bg-red-400/20 rounded transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Request Body */}
        {(request.method === "POST" || request.method === "PUT" || request.method === "PATCH") && (
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-semibold text-voka-white">📄 REQUEST BODY (JSON)</h4>
              <button className="text-xs px-2 py-1 bg-voka-border text-voka-gray rounded hover:bg-voka-magenta hover:text-white transition-colors">
                🎯 Beautify
              </button>
            </div>
            <textarea
              value={request.body ? JSON.stringify(request.body, null, 2) : ""}
              onChange={(e) => {
                try {
                  const parsed = JSON.parse(e.target.value)
                  setRequest({ ...request, body: parsed })
                } catch {
                  // Invalid JSON, keep as string for now
                }
              }}
              className="w-full h-32 bg-voka-dark border border-voka-border rounded px-3 py-2 text-voka-white font-mono text-sm resize-none"
              placeholder='{\n  "message": "Hello world",\n  "context": {\n    "user_id": "dw7"\n  }\n}'
            />
          </div>
        )}

        {/* Send Button */}
        <div className="text-center">
          <button
            onClick={executeRequest}
            disabled={loading}
            className="px-8 py-3 bg-voka-magenta text-white rounded-lg font-semibold hover:bg-voka-magenta/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <div className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                Enviando...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 inline mr-2" />🚀 ENVIAR REQUEST
              </>
            )}
          </button>
        </div>
      </div>

      {/* Response Viewer */}
      {response && (
        <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
          <h3 className="text-xl font-bold text-voka-white font-montserrat mb-4">📨 RESPONSE</h3>

          {/* Response Status */}
          <div className="flex items-center gap-4 mb-4 p-3 bg-voka-dark border border-voka-border rounded">
            <div className="flex items-center gap-2">
              <span>Status:</span>
              <span>{getStatusIcon(response.status)}</span>
              <span className={`font-bold ${getStatusColor(response.status)}`}>
                {response.status} {response.statusText}
              </span>
            </div>
            <div className="text-voka-gray">
              Time: <span className="text-voka-white font-mono">{Math.round(response.responseTime)}ms</span>
            </div>
            <div className="text-voka-gray">
              Size:{" "}
              <span className="text-voka-white font-mono">
                {response.body ? `${JSON.stringify(response.body).length} bytes` : "0 bytes"}
              </span>
            </div>
          </div>

          {/* Response Headers */}
          <div className="mb-4">
            <h4 className="text-sm font-semibold text-voka-white mb-2">📋 RESPONSE HEADERS</h4>
            <div className="bg-voka-dark border border-voka-border rounded p-3 font-mono text-sm">
              {Object.entries(response.headers).map(([key, value]) => (
                <div key={key} className="text-voka-gray">
                  <span className="text-voka-white">{key}:</span> {value}
                </div>
              ))}
            </div>
          </div>

          {/* Response Body */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-semibold text-voka-white">📄 RESPONSE BODY</h4>
              <div className="flex gap-2">
                <button className="text-xs px-2 py-1 bg-voka-border text-voka-gray rounded hover:bg-voka-magenta hover:text-white transition-colors">
                  📋 Copy
                </button>
                <button className="text-xs px-2 py-1 bg-voka-border text-voka-gray rounded hover:bg-voka-magenta hover:text-white transition-colors">
                  💾 Save
                </button>
              </div>
            </div>
            <div className="bg-voka-dark border border-voka-border rounded p-3 font-mono text-sm max-h-64 overflow-auto">
              {response.error ? (
                <div className="text-red-400">Error: {response.error}</div>
              ) : (
                <pre className="text-voka-white whitespace-pre-wrap">
                  {typeof response.body === "string" ? response.body : JSON.stringify(response.body, null, 2)}
                </pre>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Quick Tests */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <h3 className="text-lg font-bold text-voka-white font-montserrat mb-4">🎯 TESTS RÁPIDOS</h3>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          {quickTests.map((test, index) => (
            <button
              key={index}
              onClick={() => loadQuickTest(test)}
              className="p-3 bg-voka-dark border border-voka-border rounded hover:border-voka-magenta hover:bg-voka-magenta/10 transition-colors text-left"
            >
              <div className="text-sm font-medium text-voka-white">{test.name}</div>
              <div className="text-xs text-voka-gray mt-1">{test.method}</div>
            </button>
          ))}
        </div>

        <div>
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-semibold text-voka-white">📚 REQUESTS GUARDADOS</h4>
            <button className="text-xs px-2 py-1 bg-voka-border text-voka-gray rounded hover:bg-voka-magenta hover:text-white transition-colors">
              + New Collection
            </button>
          </div>

          <div className="bg-voka-dark border border-voka-border rounded p-3">
            <div className="text-sm text-voka-gray">
              └─ 🏠 VokaFlow Tests
              <div className="ml-4 space-y-1 mt-2">
                <div className="text-voka-white hover:text-voka-magenta cursor-pointer">├─ Health Check</div>
                <div className="text-voka-white hover:text-voka-magenta cursor-pointer">├─ User Authentication</div>
                <div className="text-voka-white hover:text-voka-magenta cursor-pointer">├─ Translation Test</div>
                <div className="text-voka-white hover:text-voka-magenta cursor-pointer">└─ Vicky AI Test</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

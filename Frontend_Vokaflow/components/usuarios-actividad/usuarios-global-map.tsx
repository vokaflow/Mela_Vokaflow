"use client"

import { useState, useEffect } from "react"
import { Globe, Activity } from "lucide-react"
import { usersService } from "../../services/users-service"
import type { User, GeographicData } from "../../types/users"

export function UsuariosGlobalMap() {
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [geoData, setGeoData] = useState<GeographicData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadData = async () => {
      try {
        const [user, geographic] = await Promise.all([usersService.getCurrentUser(), usersService.getGeographicData()])
        setCurrentUser(user)
        setGeoData(geographic)
      } catch (error) {
        console.error("Error loading map data:", error)
      } finally {
        setLoading(false)
      }
    }

    loadData()
    const interval = setInterval(loadData, 30000) // Actualizar cada 30s
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-voka-border rounded w-1/4 mb-4"></div>
          <div className="h-64 bg-voka-border rounded"></div>
        </div>
      </div>
    )
  }

  const totalUsers = geoData.reduce((sum, country) => sum + country.users_count, 0)
  const totalSessions = geoData.reduce((sum, country) => sum + country.sessions_count, 0)
  const totalCountries = geoData.length

  return (
    <div className="space-y-6">
      {/* Header con usuario actual */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-voka-green rounded-full animate-pulse"></div>
            <span className="text-voka-white font-montserrat">
              👤 Conectado como: <span className="text-voka-magenta font-bold">{currentUser?.username}</span>{" "}
              (Administrador)
            </span>
          </div>
          <div className="text-voka-gray text-sm">🔄 Tiempo real</div>
        </div>
      </div>

      {/* Mapa Mundial Simulado */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <h3 className="text-voka-white font-montserrat font-bold text-lg mb-4 flex items-center">
          <Globe className="mr-2 text-voka-blue" />
          🗺️ MAPA GLOBAL DE ACTIVIDAD DE USUARIOS
        </h3>

        {/* Simulación visual del mapa */}
        <div className="relative bg-voka-dark rounded-lg p-8 mb-6" style={{ minHeight: "300px" }}>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className="text-6xl mb-4">🌍</div>
              <div className="space-y-2">
                {geoData.map((country, index) => (
                  <div key={index} className="bg-voka-blue-black border border-voka-border rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-4 h-4 bg-voka-green rounded-full animate-pulse"></div>
                        <span className="text-voka-white font-montserrat">
                          🇪🇸 {country.country} - {country.users_count} Usuario{country.users_count !== 1 ? "s" : ""}{" "}
                          Activo{country.users_count !== 1 ? "s" : ""}
                        </span>
                      </div>
                      <div className="text-voka-gray text-sm">📍 IP: {currentUser?.location.ip}</div>
                    </div>
                    <div className="mt-2 text-voka-gray text-sm">
                      ⏱️ Sesión: {Math.floor((currentUser?.session_duration || 0) / 3600)}h{" "}
                      {Math.floor(((currentUser?.session_duration || 0) % 3600) / 60)}m activa
                    </div>
                    <div className="mt-1 text-voka-gray text-sm">
                      🎯 Actividad: Alta ({currentUser?.stats.total_sessions} acciones)
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Estadísticas globales */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-voka-dark border border-voka-border rounded-lg p-4 text-center">
            <div className="text-voka-green text-2xl font-bold">{totalUsers}</div>
            <div className="text-voka-gray text-sm">🟢 ONLINE</div>
            <div className="text-voka-gray text-xs">Usuarios</div>
          </div>
          <div className="bg-voka-dark border border-voka-border rounded-lg p-4 text-center">
            <div className="text-voka-blue text-2xl font-bold">{totalSessions}</div>
            <div className="text-voka-gray text-sm">🕐 SESIONES</div>
            <div className="text-voka-gray text-xs">Activas</div>
          </div>
          <div className="bg-voka-dark border border-voka-border rounded-lg p-4 text-center">
            <div className="text-voka-magenta text-2xl font-bold">{totalCountries}</div>
            <div className="text-voka-gray text-sm">🌍 PAÍSES</div>
            <div className="text-voka-gray text-xs">España</div>
          </div>
          <div className="bg-voka-dark border border-voka-border rounded-lg p-4 text-center">
            <div className="text-voka-orange text-2xl font-bold">ALTA</div>
            <div className="text-voka-gray text-sm">🎯 ACTIVIDAD</div>
            <div className="text-voka-gray text-xs">{currentUser?.stats.total_sessions} acciones</div>
          </div>
        </div>
      </div>

      {/* Feed de actividad en tiempo real */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <h3 className="text-voka-white font-montserrat font-bold text-lg mb-4 flex items-center">
          <Activity className="mr-2 text-voka-green" />📊 STREAM DE ACTIVIDAD EN VIVO
        </h3>
        <div className="space-y-2 max-h-48 overflow-y-auto">
          <div className="text-voka-gray text-sm p-2 bg-voka-dark rounded">
            [{new Date().toLocaleTimeString()}] 👤 {currentUser?.username} → Acceso a Dashboard: Usuarios/Actividad
          </div>
          <div className="text-voka-gray text-sm p-2 bg-voka-dark rounded">
            [{new Date(Date.now() - 2 * 60 * 1000).toLocaleTimeString()}] 👤 {currentUser?.username} → Traducción: "Hola
            mundo" ES→EN
          </div>
          <div className="text-voka-gray text-sm p-2 bg-voka-dark rounded">
            [{new Date(Date.now() - 5 * 60 * 1000).toLocaleTimeString()}] 👤 {currentUser?.username} → Interacción Vicky
            AI: "Help with coding"
          </div>
          <div className="text-voka-gray text-sm p-2 bg-voka-dark rounded">
            [{new Date(Date.now() - 8 * 60 * 1000).toLocaleTimeString()}] 👤 {currentUser?.username} → Acceso Dashboard:
            Infraestructura
          </div>
          <div className="text-voka-gray text-sm p-2 bg-voka-dark rounded">
            [{new Date(Date.now() - 12 * 60 * 1000).toLocaleTimeString()}] 👤 {currentUser?.username} → API call:
            /api/monitoring/metrics
          </div>
        </div>
      </div>
    </div>
  )
}

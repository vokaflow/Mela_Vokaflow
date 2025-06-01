"use client"

import { useState, useEffect } from "react"
import { Globe, Languages, Users } from "lucide-react"
import { usersService } from "../../services/users-service"
import type { GeographicData, LanguageUsage } from "../../types/users"

export function UsuariosActivity() {
  const [geoData, setGeoData] = useState<GeographicData[]>([])
  const [languageData, setLanguageData] = useState<LanguageUsage[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadData = async () => {
      try {
        const [geographic, language] = await Promise.all([
          usersService.getGeographicData(),
          usersService.getLanguageUsage(),
        ])
        setGeoData(geographic)
        setLanguageData(language)
      } catch (error) {
        console.error("Error loading activity data:", error)
      } finally {
        setLoading(false)
      }
    }

    loadData()
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [])

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
      {/* Actividad por Geografía */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <h3 className="text-voka-white font-montserrat font-bold text-lg mb-4 flex items-center">
          <Globe className="mr-2 text-voka-blue" />🌍 ACTIVIDAD POR GEOGRAFÍA
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-voka-dark">
              <tr>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">PAÍS</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">USUARIOS</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">SESIONES</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">TRADUCCIONES</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">HORAS PICO</th>
              </tr>
            </thead>
            <tbody>
              {geoData.map((country, index) => (
                <tr key={index} className="border-t border-voka-border hover:bg-voka-dark/50">
                  <td className="p-4">
                    <div className="flex items-center space-x-2">
                      <span className="text-2xl">🇪🇸</span>
                      <span className="text-voka-white font-montserrat">{country.country}</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className="text-voka-green font-bold">{country.users_count}</span>
                  </td>
                  <td className="p-4">
                    <span className="text-voka-blue font-bold">{country.sessions_count}</span>
                  </td>
                  <td className="p-4">
                    <span className="text-voka-magenta font-bold">{country.translations_count.toLocaleString()}</span>
                  </td>
                  <td className="p-4">
                    <div className="space-y-1">
                      {country.peak_hours.map((hour, idx) => (
                        <div key={idx} className="text-voka-gray text-sm">
                          {hour} CET
                        </div>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-4 p-4 bg-voka-dark rounded-lg">
          <div className="flex justify-between items-center text-sm">
            <span className="text-voka-gray">Total Global:</span>
            <div className="flex space-x-6">
              <span className="text-voka-green">{geoData.reduce((sum, c) => sum + c.users_count, 0)} Usuarios</span>
              <span className="text-voka-blue">{geoData.reduce((sum, c) => sum + c.sessions_count, 0)} Sesiones</span>
              <span className="text-voka-magenta">Pico Global: 22:00 CET</span>
            </div>
          </div>
        </div>
      </div>

      {/* Distribución de Idiomas */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <h3 className="text-voka-white font-montserrat font-bold text-lg mb-4 flex items-center">
          <Languages className="mr-2 text-voka-green" />🔤 DISTRIBUCIÓN DE ACTIVIDAD POR IDIOMA
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-voka-dark">
              <tr>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">IDIOMA ORIGEN</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">IDIOMA DESTINO</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">TRADUCCIONES</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">PORCENTAJE</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">TENDENCIA</th>
              </tr>
            </thead>
            <tbody>
              {languageData.map((lang, index) => (
                <tr key={index} className="border-t border-voka-border hover:bg-voka-dark/50">
                  <td className="p-4">
                    <div className="flex items-center space-x-2">
                      <span className="text-xl">🇪🇸</span>
                      <span className="text-voka-white">{lang.source_lang}</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center space-x-2">
                      <span className="text-xl">
                        {lang.target_lang === "English" ? "🇺🇸" : lang.target_lang === "French" ? "🇫🇷" : "🇪🇸"}
                      </span>
                      <span className="text-voka-white">{lang.target_lang}</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className="text-voka-blue font-bold">{lang.translations_count.toLocaleString()}</span>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center space-x-2">
                      <div className="w-16 bg-voka-dark rounded-full h-2">
                        <div
                          className="bg-voka-magenta h-2 rounded-full"
                          style={{ width: `${lang.percentage}%` }}
                        ></div>
                      </div>
                      <span className="text-voka-white text-sm">{lang.percentage}%</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <span
                      className={`flex items-center space-x-1 ${
                        lang.trend === "up"
                          ? "text-voka-green"
                          : lang.trend === "down"
                            ? "text-voka-orange"
                            : "text-voka-gray"
                      }`}
                    >
                      {lang.trend === "up" ? "↗️" : lang.trend === "down" ? "↘️" : "→"}
                      <span className="text-sm">
                        {lang.trend === "up" ? "+15%" : lang.trend === "down" ? "-5%" : "0%"}
                      </span>
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Actividad por Rol */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <h3 className="text-voka-white font-montserrat font-bold text-lg mb-4 flex items-center">
          <Users className="mr-2 text-voka-magenta" />👑 ACTIVIDAD POR ROL DE USUARIO
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-voka-dark">
              <tr>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">ROL</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">USUARIOS</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">LLAMADAS API</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">FUNCIONES USADAS</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">PERMISOS</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-t border-voka-border hover:bg-voka-dark/50">
                <td className="p-4">
                  <div className="flex items-center space-x-2">
                    <span className="text-xl">👑</span>
                    <span className="text-voka-magenta font-bold">Admin</span>
                  </div>
                </td>
                <td className="p-4">
                  <span className="text-voka-green font-bold">1</span>
                </td>
                <td className="p-4">
                  <span className="text-voka-blue font-bold">45,000</span>
                </td>
                <td className="p-4">
                  <span className="text-voka-white">Todas (100%)</span>
                </td>
                <td className="p-4">
                  <span className="text-voka-green">Acceso Completo</span>
                </td>
              </tr>
              <tr className="border-t border-voka-border hover:bg-voka-dark/50">
                <td className="p-4">
                  <div className="flex items-center space-x-2">
                    <span className="text-xl">👤</span>
                    <span className="text-voka-blue font-bold">Estándar</span>
                  </div>
                </td>
                <td className="p-4">
                  <span className="text-voka-gray">0</span>
                </td>
                <td className="p-4">
                  <span className="text-voka-gray">0</span>
                </td>
                <td className="p-4">
                  <span className="text-voka-gray">Ninguna</span>
                </td>
                <td className="p-4">
                  <span className="text-voka-orange">Limitado</span>
                </td>
              </tr>
              <tr className="border-t border-voka-border hover:bg-voka-dark/50">
                <td className="p-4">
                  <div className="flex items-center space-x-2">
                    <span className="text-xl">🤖</span>
                    <span className="text-voka-blue font-bold">API User</span>
                  </div>
                </td>
                <td className="p-4">
                  <span className="text-voka-gray">0</span>
                </td>
                <td className="p-4">
                  <span className="text-voka-gray">0</span>
                </td>
                <td className="p-4">
                  <span className="text-voka-gray">Ninguna</span>
                </td>
                <td className="p-4">
                  <span className="text-voka-blue">Solo API</span>
                </td>
              </tr>
              <tr className="border-t border-voka-border hover:bg-voka-dark/50">
                <td className="p-4">
                  <div className="flex items-center space-x-2">
                    <span className="text-xl">🔧</span>
                    <span className="text-voka-blue font-bold">Sistema</span>
                  </div>
                </td>
                <td className="p-4">
                  <span className="text-voka-gray">0</span>
                </td>
                <td className="p-4">
                  <span className="text-voka-gray">0</span>
                </td>
                <td className="p-4">
                  <span className="text-voka-gray">Ninguna</span>
                </td>
                <td className="p-4">
                  <span className="text-voka-gray">Solo Lectura</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

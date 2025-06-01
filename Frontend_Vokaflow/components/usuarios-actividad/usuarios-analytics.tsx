"use client"

import { useState, useEffect } from "react"
import { TrendingUp, BarChart3, PieChart } from "lucide-react"
import { usersService } from "../../services/users-service"

export function UsuariosAnalytics() {
  const [analytics, setAnalytics] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadData = async () => {
      try {
        const analyticsData = await usersService.getAnalytics()
        setAnalytics(analyticsData)
      } catch (error) {
        console.error("Error loading analytics:", error)
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

  // Datos simulados para el gráfico de actividad diaria
  const dailyActivity = [
    { day: "Lun", actions: 850 },
    { day: "Mar", actions: 920 },
    { day: "Mié", actions: 780 },
    { day: "Jue", actions: 1100 },
    { day: "Vie", actions: 950 },
    { day: "Sáb", actions: 650 },
    { day: "Dom", actions: 720 },
  ]

  const maxActions = Math.max(...dailyActivity.map((d) => d.actions))

  // Datos de uso de funciones
  const featureUsage = [
    { feature: "🌍 Traducción", count: 12500, percentage: 78, lastUsed: "2 minutos" },
    { feature: "🧠 Vicky AI", count: 2340, percentage: 15, lastUsed: "5 minutos" },
    { feature: "💻 Terminal", count: 856, percentage: 5, lastUsed: "1 hora" },
    { feature: "📊 Analytics", count: 234, percentage: 1.5, lastUsed: "Ahora" },
    { feature: "📁 Gestor Archivos", count: 89, percentage: 0.5, lastUsed: "1 día" },
  ]

  return (
    <div className="space-y-6">
      {/* Métricas de Engagement */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <h3 className="text-voka-white font-montserrat font-bold text-lg mb-4 flex items-center">
          <TrendingUp className="mr-2 text-voka-green" />📈 ANALYTICS DE RETENCIÓN Y ENGAGEMENT
        </h3>

        {/* Gráfico de Actividad Diaria */}
        <div className="mb-6">
          <h4 className="text-voka-white font-montserrat font-bold mb-4 text-center">📊 GRÁFICO DE ACTIVIDAD DIARIA</h4>
          <div className="bg-voka-dark rounded-lg p-4">
            <div className="flex items-end justify-between h-48 space-x-2">
              {dailyActivity.map((day, index) => (
                <div key={index} className="flex flex-col items-center flex-1">
                  <div className="flex flex-col justify-end h-40 w-full">
                    <div
                      className="bg-voka-magenta rounded-t transition-all duration-500 hover:bg-voka-magenta/80"
                      style={{ height: `${(day.actions / maxActions) * 100}%`, minHeight: "4px" }}
                      title={`${day.actions} acciones`}
                    ></div>
                  </div>
                  <div className="text-voka-gray text-xs mt-2">{day.day}</div>
                </div>
              ))}
            </div>
            <div className="mt-4 text-center">
              <div className="text-voka-gray text-sm">Acciones por día de la semana</div>
            </div>
          </div>
        </div>

        {/* Métricas de Engagement */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-voka-dark border border-voka-border rounded-lg p-4 text-center">
            <div className="text-voka-blue text-2xl font-bold">2.5h</div>
            <div className="text-voka-gray text-sm">Sesión Promedio</div>
          </div>
          <div className="bg-voka-dark border border-voka-border rounded-lg p-4 text-center">
            <div className="text-voka-green text-2xl font-bold">100%</div>
            <div className="text-voka-gray text-sm">Tasa de Retorno</div>
          </div>
          <div className="bg-voka-dark border border-voka-border rounded-lg p-4 text-center">
            <div className="text-voka-magenta text-2xl font-bold">0%</div>
            <div className="text-voka-gray text-sm">Tasa de Rebote</div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          <div className="bg-voka-dark border border-voka-border rounded-lg p-4 text-center">
            <div className="text-voka-orange text-2xl font-bold">1</div>
            <div className="text-voka-gray text-sm">Activos Diarios</div>
          </div>
          <div className="bg-voka-dark border border-voka-border rounded-lg p-4 text-center">
            <div className="text-voka-blue text-2xl font-bold">1</div>
            <div className="text-voka-gray text-sm">Activos Semanales</div>
          </div>
          <div className="bg-voka-dark border border-voka-border rounded-lg p-4 text-center">
            <div className="text-voka-green text-2xl font-bold">1</div>
            <div className="text-voka-gray text-sm">Activos Mensuales</div>
          </div>
        </div>
      </div>

      {/* Adopción y Uso de Funciones */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <h3 className="text-voka-white font-montserrat font-bold text-lg mb-4 flex items-center">
          <PieChart className="mr-2 text-voka-blue" />🎯 ADOPCIÓN Y USO DE FUNCIONES
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-voka-dark">
              <tr>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">FUNCIÓN</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">CONTADOR DE USO</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">PORCENTAJE</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">ÚLTIMO USO</th>
              </tr>
            </thead>
            <tbody>
              {featureUsage.map((feature, index) => (
                <tr key={index} className="border-t border-voka-border hover:bg-voka-dark/50">
                  <td className="p-4">
                    <span className="text-voka-white font-montserrat">{feature.feature}</span>
                  </td>
                  <td className="p-4">
                    <span className="text-voka-blue font-bold">{feature.count.toLocaleString()}</span>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center space-x-2">
                      <div className="w-20 bg-voka-dark rounded-full h-2">
                        <div
                          className="bg-voka-magenta h-2 rounded-full"
                          style={{ width: `${feature.percentage}%` }}
                        ></div>
                      </div>
                      <span className="text-voka-white text-sm">{feature.percentage}%</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className="text-voka-gray">{feature.lastUsed} atrás</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Tendencias de Uso */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <h3 className="text-voka-white font-montserrat font-bold text-lg mb-4 flex items-center">
          <BarChart3 className="mr-2 text-voka-orange" />📈 TENDENCIAS DE USO Y CRECIMIENTO
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <h4 className="text-voka-white font-montserrat font-bold">Métricas de Crecimiento</h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-voka-gray">Crecimiento Semanal:</span>
                <span className="text-voka-green">+15% ↗️</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-voka-gray">Crecimiento Mensual:</span>
                <span className="text-voka-green">+45% ↗️</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-voka-gray">Nuevas Funciones Adoptadas:</span>
                <span className="text-voka-blue">3 este mes</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-voka-gray">Tiempo Promedio por Sesión:</span>
                <span className="text-voka-magenta">+20% ↗️</span>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <h4 className="text-voka-white font-montserrat font-bold">Patrones de Uso</h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-voka-gray">Hora Pico:</span>
                <span className="text-voka-white">21:00 - 23:00 CET</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-voka-gray">Día Más Activo:</span>
                <span className="text-voka-white">Jueves</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-voka-gray">Función Más Usada:</span>
                <span className="text-voka-green">Traducción (78%)</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-voka-gray">Dispositivo Principal:</span>
                <span className="text-voka-blue">Desktop Linux</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

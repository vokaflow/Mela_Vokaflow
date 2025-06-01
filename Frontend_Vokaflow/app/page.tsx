import { DashboardLayout } from "../components/dashboard-layout"
import { ProtectedRoute } from "../components/auth/protected-route"
import { NeuralNetworkBg } from "../components/home/neural-network-bg"
import { NeuralHead3D } from "../components/home/neural-head-3d"
import { FuturisticMetrics } from "../components/home/futuristic-metrics"
import { SystemOverview } from "../components/home/system-overview"

export default function HomePage() {
  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="relative min-h-screen bg-voka-dark">
          {/* Fondo de red neural animado */}
          <NeuralNetworkBg />

          <div className="relative z-10 flex-1 space-y-8 p-6">
            {/* Header futurista */}
            <div className="text-center space-y-4 mb-8">
              <h1 className="text-5xl font-bold text-voka-white font-montserrat bg-gradient-to-r from-voka-magenta via-voka-blue to-voka-green bg-clip-text text-transparent">
                🚀 VokaFlow Command Center
              </h1>
              <p className="text-xl text-voka-gray font-montserrat max-w-3xl mx-auto">
                Centro de comando futurista para la plataforma de comunicación global más avanzada del mundo
              </p>
              <div className="flex justify-center gap-4 mt-6">
                <div className="px-4 py-2 bg-voka-green/20 border border-voka-green/30 rounded-full">
                  <span className="text-voka-green font-montserrat text-sm">🟢 Sistema Operativo</span>
                </div>
                <div className="px-4 py-2 bg-voka-blue/20 border border-voka-blue/30 rounded-full">
                  <span className="text-voka-blue font-montserrat text-sm">🌐 Global Ready</span>
                </div>
                <div className="px-4 py-2 bg-voka-magenta/20 border border-voka-magenta/30 rounded-full">
                  <span className="text-voka-magenta font-montserrat text-sm">🧠 IA Activa</span>
                </div>
              </div>
            </div>

            {/* Sección principal con cabeza neural 3D */}
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 mb-8">
              {/* Cabeza Neural 3D - Elemento central */}
              <div className="xl:col-span-1">
                <NeuralHead3D />
              </div>

              {/* Métricas del sistema */}
              <div className="xl:col-span-2">
                <div className="space-y-6">
                  <h2 className="text-3xl font-bold text-voka-white font-montserrat mb-6">📊 Métricas del Sistema</h2>
                  <FuturisticMetrics />
                </div>
              </div>
            </div>

            {/* Vista general del sistema */}
            <div className="space-y-6">
              <h2 className="text-3xl font-bold text-voka-white font-montserrat">🌐 Vista General del Sistema</h2>
              <SystemOverview />
            </div>

            {/* Sección de accesos rápidos */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-8">
              {[
                {
                  title: "🧠 Vicky AI",
                  desc: "Inteligencia Artificial",
                  color: "border-voka-magenta hover:bg-voka-magenta/10",
                },
                {
                  title: "🌍 Traducción",
                  desc: "Motor de Traducción",
                  color: "border-voka-green hover:bg-voka-green/10",
                },
                { title: "💬 Conversaciones", desc: "Chat Global", color: "border-voka-blue hover:bg-voka-blue/10" },
                {
                  title: "📊 Analytics",
                  desc: "Análisis Avanzado",
                  color: "border-voka-yellow hover:bg-voka-yellow/10",
                },
              ].map((item, index) => (
                <div
                  key={index}
                  className={`p-6 bg-voka-blue-black border-2 ${item.color} rounded-lg cursor-pointer transition-all duration-300 hover:scale-105 group`}
                >
                  <h3 className="text-voka-white font-montserrat font-semibold text-lg mb-2 group-hover:text-voka-magenta transition-colors">
                    {item.title}
                  </h3>
                  <p className="text-voka-gray font-montserrat text-sm">{item.desc}</p>
                  <div className="mt-4 flex justify-end">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-voka-magenta to-voka-blue flex items-center justify-center">
                      <span className="text-white text-sm">→</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Footer futurista */}
            <div className="text-center mt-12 p-6 border-t border-voka-border">
              <p className="text-voka-gray font-montserrat">
                🚀 VokaFlow Dashboard v2.0 - Conectando el mundo sin barreras idiomáticas
              </p>
              <div className="flex justify-center gap-6 mt-4 text-sm text-voka-gray">
                <span>🌐 156 países conectados</span>
                <span>🗣️ 95+ idiomas soportados</span>
                <span>⚡ 99.9% uptime</span>
                <span>🧠 IA de última generación</span>
              </div>
            </div>
          </div>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}

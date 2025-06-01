import { DashboardLayout } from "../../components/dashboard-layout"

export default function ModelosIAPage() {
  return (
    <DashboardLayout>
      <div className="flex-1 space-y-6 p-6 bg-voka-dark">
        <div className="space-y-4">
          <h1 className="text-4xl font-bold text-voka-white font-montserrat">🧬 Modelos IA</h1>
          <p className="text-xl text-voka-gray font-montserrat">Gestión de modelos de inteligencia artificial</p>
        </div>

        <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
          <p className="text-voka-white font-montserrat">Configuración, entrenamiento y despliegue de modelos de IA.</p>
        </div>
      </div>
    </DashboardLayout>
  )
}

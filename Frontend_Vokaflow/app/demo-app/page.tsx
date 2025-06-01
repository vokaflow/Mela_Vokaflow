import { DashboardLayout } from "../../components/dashboard-layout"

export default function DemoAppPage() {
  return (
    <DashboardLayout>
      <div className="flex-1 space-y-6 p-6 bg-voka-dark">
        <div className="space-y-4">
          <h1 className="text-4xl font-bold text-voka-white font-montserrat">🚀 Demo App</h1>
          <p className="text-xl text-voka-gray font-montserrat">Aplicación de demostración de VokaFlow</p>
        </div>

        <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
          <p className="text-voka-white font-montserrat">
            Demo interactiva de las capacidades de traducción y comunicación de VokaFlow.
          </p>
        </div>
      </div>
    </DashboardLayout>
  )
}

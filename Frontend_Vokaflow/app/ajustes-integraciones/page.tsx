import { DashboardLayout } from "../../components/dashboard-layout"
import { AjustesIntegracionesMain } from "../../components/ajustes-integraciones/ajustes-integraciones-main"

export default function AjustesIntegracionesPage() {
  return (
    <DashboardLayout>
      <div className="flex-1 space-y-6 p-6 bg-slate-950">
        <AjustesIntegracionesMain />
      </div>
    </DashboardLayout>
  )
}

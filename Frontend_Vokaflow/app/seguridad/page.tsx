import { DashboardLayout } from "../../components/dashboard-layout"
import { SeguridadMain } from "../../components/seguridad/seguridad-main"

export default function SeguridadPage() {
  return (
    <DashboardLayout>
      <div className="flex-1 space-y-6 p-6 bg-slate-950">
        <SeguridadMain />
      </div>
    </DashboardLayout>
  )
}

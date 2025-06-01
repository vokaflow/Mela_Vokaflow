import { DashboardLayout } from "../../components/dashboard-layout"
import { EstadoEconomicoMain } from "../../components/estado-economico/estado-economico-main"

export default function EstadoEconomicoPage() {
  return (
    <DashboardLayout>
      <div className="flex-1 p-6 bg-voka-dark">
        <EstadoEconomicoMain />
      </div>
    </DashboardLayout>
  )
}

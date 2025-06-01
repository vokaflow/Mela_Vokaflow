import { DashboardLayout } from "../../components/dashboard-layout"
import { InfraestructuraMain } from "../../components/infraestructura/infraestructura-main"

export default function InfraestructuraPage() {
  return (
    <DashboardLayout>
      <div className="flex-1 p-6 bg-voka-dark">
        <InfraestructuraMain />
      </div>
    </DashboardLayout>
  )
}

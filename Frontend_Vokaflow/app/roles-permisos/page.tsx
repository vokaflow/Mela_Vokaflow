import { DashboardLayout } from "../../components/dashboard-layout"
import { RolesPermisosMain } from "../../components/roles-permisos/roles-permisos-main"

export default function RolesPermisosPage() {
  return (
    <DashboardLayout>
      <div className="flex-1 space-y-6 p-6 bg-slate-950">
        <RolesPermisosMain />
      </div>
    </DashboardLayout>
  )
}

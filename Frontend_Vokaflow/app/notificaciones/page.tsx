import { DashboardLayout } from "../../components/dashboard-layout"
import { NotificacionesMain } from "../../components/notificaciones/notificaciones-main"

export default function NotificacionesPage() {
  return (
    <DashboardLayout>
      <div className="flex-1 space-y-6 p-6 bg-slate-950">
        <NotificacionesMain />
      </div>
    </DashboardLayout>
  )
}

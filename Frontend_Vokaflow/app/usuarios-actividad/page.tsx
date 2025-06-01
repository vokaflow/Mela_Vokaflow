import { DashboardLayout } from "../../components/dashboard-layout"
import { UsuariosActividadMain } from "../../components/usuarios-actividad/usuarios-actividad-main"

export default function UsuariosActividadPage() {
  return (
    <DashboardLayout>
      <div className="flex-1 p-6 bg-voka-dark">
        <UsuariosActividadMain />
      </div>
    </DashboardLayout>
  )
}

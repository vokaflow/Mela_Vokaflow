import { DashboardLayout } from "../../components/dashboard-layout"
import { EndpointsAPIMain } from "../../components/endpoints-api/endpoints-api-main"

export default function EndpointsAPIPage() {
  return (
    <DashboardLayout>
      <div className="flex-1 p-6 bg-voka-dark">
        <EndpointsAPIMain />
      </div>
    </DashboardLayout>
  )
}

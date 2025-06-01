import { DashboardLayout } from "../../components/dashboard-layout"
import { VickyAIMain } from "../../components/vicky-ai/vicky-ai-main"

export default function VickyAIPage() {
  return (
    <DashboardLayout>
      <div className="flex-1 p-6 bg-voka-dark">
        <VickyAIMain />
      </div>
    </DashboardLayout>
  )
}

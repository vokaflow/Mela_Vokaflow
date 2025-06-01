import { DashboardLayout } from "../../components/dashboard-layout"
import { TerminalMain } from "../../components/terminal/terminal-main"

export default function TerminalPage() {
  return (
    <DashboardLayout>
      <div className="flex-1 p-6 bg-voka-dark">
        <TerminalMain />
      </div>
    </DashboardLayout>
  )
}

"use client"

import { VokaFlowSidebar } from "./components/vokaflow-sidebar"
import { DashboardHeader } from "./components/dashboard-header"
import { DashboardContent } from "./components/dashboard-content"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"

export default function VokaFlowDashboard() {
  return (
    <div className="min-h-screen bg-voka-dark font-montserrat">
      <SidebarProvider defaultOpen={true}>
        <VokaFlowSidebar />
        <SidebarInset className="bg-voka-dark">
          <DashboardHeader />
          <DashboardContent />
        </SidebarInset>
      </SidebarProvider>
    </div>
  )
}

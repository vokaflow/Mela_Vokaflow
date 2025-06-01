"use client"

import type React from "react"
import { VokaFlowSidebar } from "./vokaflow-sidebar"

interface DashboardLayoutProps {
  children: React.ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-voka-dark font-montserrat">
      <VokaFlowSidebar />
      <div className="ml-16 transition-all duration-300">{children}</div>
    </div>
  )
}

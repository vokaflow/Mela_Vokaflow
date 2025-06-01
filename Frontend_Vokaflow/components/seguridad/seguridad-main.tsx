"use client"
import { SectionTabs } from "@/components/ui/section-tabs"
import { SeguridadFirewall } from "./seguridad-firewall"
import { SeguridadLogs } from "./seguridad-logs"

const tabs = [
  {
    id: "firewall",
    label: "🛡️ Firewall",
    component: SeguridadFirewall,
  },
  {
    id: "logs",
    label: "📋 Logs de Seguridad",
    component: SeguridadLogs,
  },
]

export function SeguridadMain() {
  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <h1 className="text-4xl font-bold text-white font-montserrat">🔐 Seguridad</h1>
        <p className="text-xl text-slate-400 font-montserrat">Control y monitoreo de la seguridad del sistema</p>
      </div>

      <SectionTabs tabs={tabs} />
    </div>
  )
}

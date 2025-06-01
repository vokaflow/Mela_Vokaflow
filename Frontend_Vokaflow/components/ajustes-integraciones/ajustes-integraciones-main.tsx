"use client"

import { SectionTabs } from "@/components/ui/section-tabs"
import { ConfiguracionGeneral } from "./configuracion-general"
import { IntegracionesAPI } from "./integraciones-api"

const tabs = [
  {
    id: "configuracion",
    label: "⚙️ Configuración General",
    component: ConfiguracionGeneral,
  },
  {
    id: "integraciones",
    label: "🔗 Integraciones API",
    component: IntegracionesAPI,
  },
]

export function AjustesIntegracionesMain() {
  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <h1 className="text-4xl font-bold text-white font-montserrat">🧰 Ajustes / Integraciones</h1>
        <p className="text-xl text-slate-400 font-montserrat">Configuración del sistema y gestión de integraciones</p>
      </div>

      <SectionTabs tabs={tabs} />
    </div>
  )
}

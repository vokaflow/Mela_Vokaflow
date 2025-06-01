"use client"

import { SectionTabs } from "@/components/ui/section-tabs"
import { ModelosActivos } from "./modelos-activos"
import { ModelosCargaDescarga } from "./modelos-carga-descarga"
import { ModelosGPUStats } from "./modelos-gpu-stats"
import { ModelosConfiguracion } from "./modelos-configuracion"
import { ModelosTesting } from "./modelos-testing"
import { ModelosVersiones } from "./modelos-versiones"

const tabs = [
  {
    id: "activos",
    label: "🟢 Modelos Activos",
    component: ModelosActivos,
  },
  {
    id: "carga-descarga",
    label: "⬇️ Carga/Descarga",
    component: ModelosCargaDescarga,
  },
  {
    id: "gpu-stats",
    label: "🖥️ GPU Stats",
    component: ModelosGPUStats,
  },
  {
    id: "configuracion",
    label: "⚙️ Configuración",
    component: ModelosConfiguracion,
  },
  {
    id: "testing",
    label: "🧪 Testing",
    component: ModelosTesting,
  },
  {
    id: "versiones",
    label: "📦 Versiones",
    component: ModelosVersiones,
  },
]

export function ModelosIAMain() {
  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <h1 className="text-4xl font-bold text-white font-montserrat">🧬 Modelos IA</h1>
        <p className="text-xl text-slate-400 font-montserrat">
          Gestión y control de modelos de inteligencia artificial
        </p>
      </div>

      <SectionTabs tabs={tabs} />
    </div>
  )
}

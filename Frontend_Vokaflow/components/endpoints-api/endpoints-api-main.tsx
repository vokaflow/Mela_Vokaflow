"use client"

import { Radio, Globe, Zap, Shield, BarChart } from "lucide-react"
import { SectionTabs } from "../ui/section-tabs"
import { EndpointsStatus } from "./endpoints-status"
import { EndpointsTesting } from "./endpoints-testing"
import { EndpointsControl } from "./endpoints-control"
import { EndpointsHistory } from "./endpoints-history"
import { EndpointsDocs } from "./endpoints-docs"

const endpointsApiTabs = [
  {
    id: "status",
    label: "Estado",
    icon: Radio,
    badge: "103",
    component: <EndpointsStatus />,
  },
  {
    id: "testing",
    label: "Testing",
    icon: Globe,
    badge: "API",
    component: <EndpointsTesting />,
  },
  {
    id: "control",
    label: "Control",
    icon: Zap,
    component: <EndpointsControl />,
  },
  {
    id: "history",
    label: "Historial",
    icon: Shield,
    badge: "1.8K",
    component: <EndpointsHistory />,
  },
  {
    id: "docs",
    label: "Documentación",
    icon: BarChart,
    component: <EndpointsDocs />,
  },
]

export function EndpointsAPIMain() {
  return (
    <SectionTabs
      title="📡 API CONTROL CENTER"
      subtitle="Gestión Avanzada, Testing y Monitoreo de 103 Endpoints"
      tabs={endpointsApiTabs}
      defaultTab="status"
    />
  )
}

"use client"

import { Server, Network, AlertTriangle, FileText, Settings, HardDrive, Layers } from "lucide-react"
import { SectionTabs } from "../ui/section-tabs"
import { InfraestructuraServers } from "./infraestructura-servers"
import { InfraestructuraNetwork } from "./infraestructura-network"
import { InfraestructuraAlerts } from "./infraestructura-alerts"
import { InfraestructuraLogs } from "./infraestructura-logs"
import { InfraestructuraServices } from "./infraestructura-services"
import { InfraestructuraBackup } from "./infraestructura-backup"
import { InfraestructuraClusters } from "./infraestructura-clusters"

const infraestructuraTabs = [
  {
    id: "servers",
    label: "Servidores",
    icon: Server,
    badge: "12",
    component: <InfraestructuraServers />,
  },
  {
    id: "network",
    label: "Red",
    icon: Network,
    component: <InfraestructuraNetwork />,
  },
  {
    id: "alerts",
    label: "Alertas",
    icon: AlertTriangle,
    badge: "3",
    component: <InfraestructuraAlerts />,
  },
  {
    id: "logs",
    label: "Logs",
    icon: FileText,
    badge: "LIVE",
    component: <InfraestructuraLogs />,
  },
  {
    id: "services",
    label: "Servicios",
    icon: Settings,
    badge: "24",
    component: <InfraestructuraServices />,
  },
  {
    id: "backup",
    label: "Backup",
    icon: HardDrive,
    badge: "89%",
    component: <InfraestructuraBackup />,
  },
  {
    id: "clusters",
    label: "Clusters",
    icon: Layers,
    badge: "OK",
    component: <InfraestructuraClusters />,
  },
]

export function InfraestructuraMain() {
  return (
    <SectionTabs
      title="🔧 INFRASTRUCTURE CONTROL"
      subtitle="Centro de Control de Infraestructura - Estilo NASA Mission Control"
      tabs={infraestructuraTabs}
      defaultTab="servers"
      navColumns={4}
    />
  )
}

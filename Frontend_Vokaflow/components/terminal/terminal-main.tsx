"use client"

import { Terminal, Users, History, Zap, FileText, Activity } from "lucide-react"
import { SectionTabs } from "../ui/section-tabs"
import { TerminalConsole } from "./terminal-console"
import { TerminalSessions } from "./terminal-sessions"
import { TerminalHistory } from "./terminal-history"
import { TerminalProcesses } from "./terminal-processes"
import { TerminalLogs } from "./terminal-logs"

const terminalTabs = [
  {
    id: "console",
    label: "Consola",
    icon: Terminal,
    component: <TerminalConsole />,
  },
  {
    id: "sessions",
    label: "Sesiones",
    icon: Users,
    badge: "4",
    component: <TerminalSessions />,
  },
  {
    id: "history",
    label: "Historial",
    icon: History,
    badge: "156",
    component: <TerminalHistory />,
  },
  {
    id: "processes",
    label: "Procesos",
    icon: Zap,
    badge: "12",
    component: <TerminalProcesses />,
  },
  {
    id: "logs",
    label: "Logs",
    icon: FileText,
    badge: "LIVE",
    component: <TerminalLogs />,
  },
  {
    id: "monitoring",
    label: "Monitoreo",
    icon: Activity,
    component: (
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <p className="text-voka-white font-montserrat">System Monitoring - Monitoreo del sistema en tiempo real</p>
      </div>
    ),
  },
]

export function TerminalMain() {
  return (
    <SectionTabs
      title="💻 TERMINAL CONTROL"
      subtitle="Interfaz Avanzada de Línea de Comandos"
      tabs={terminalTabs}
      defaultTab="console"
    />
  )
}

"use client"

import { useState, useEffect } from "react"
import { FileText, AlertTriangle, CheckCircle, XCircle, Clock, User, Shield, Search } from "lucide-react"
import { InternalNavCompact } from "@/components/ui/internal-nav-compact"

const navItems = [
  {
    title: "Todos",
    href: "/seguridad/logs",
    icon: FileText,
  },
  {
    title: "Alertas",
    href: "/seguridad/logs/alertas",
    icon: AlertTriangle,
  },
  {
    title: "Exitosos",
    href: "/seguridad/logs/exitosos",
    icon: CheckCircle,
  },
  {
    title: "Fallidos",
    href: "/seguridad/logs/fallidos",
    icon: XCircle,
  },
  {
    title: "Pendientes",
    href: "/seguridad/logs/pendientes",
    icon: Clock,
  },
  {
    title: "Usuarios",
    href: "/seguridad/logs/usuarios",
    icon: User,
  },
  {
    title: "Seguridad",
    href: "/seguridad/logs/seguridad",
    icon: Shield,
  },
]

const SeguridadLogs = () => {
  const [search, setSearch] = useState("")

  useEffect(() => {
    // Implement search functionality here
    console.log("Search term:", search)
  }, [search])

  return (
    <div>
      <div className="md:hidden">
        <InternalNavCompact items={navItems} />
      </div>
      <div className="hidden md:flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-2xl font-semibold tracking-tight">Logs de Seguridad</h2>
          <p className="text-sm text-muted-foreground">
            Monitorea la actividad y eventos relacionados con la seguridad.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Buscar..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="flex h-10 w-[200px] rounded-md border border-input bg-background px-8 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
            />
          </div>
        </div>
      </div>
      <div className="mt-4">
        {/* Table or list of logs will go here */}
        <p>Contenido de los logs de seguridad.</p>
      </div>
    </div>
  )
}

export default SeguridadLogs

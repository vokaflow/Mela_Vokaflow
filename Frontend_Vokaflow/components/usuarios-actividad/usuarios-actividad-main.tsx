"use client"

import { Users, Globe, Activity, UserCheck, MapPin, Clock } from "lucide-react"
import { SectionTabs } from "../ui/section-tabs"
import { UsuariosGlobalMap } from "./usuarios-global-map"
import { UsuariosList } from "./usuarios-list"
import { UsuariosActivity } from "./usuarios-activity"
import { UsuariosSessions } from "./usuarios-sessions"
import { UsuariosAnalytics } from "./usuarios-analytics"
import { UsuariosProfiles } from "./usuarios-profiles"

const usuariosActividadTabs = [
  {
    id: "global-map",
    label: "Mapa Global",
    icon: Globe,
    badge: "LIVE",
    component: <UsuariosGlobalMap />,
  },
  {
    id: "users-list",
    label: "Lista Usuarios",
    icon: Users,
    badge: "1",
    component: <UsuariosList />,
  },
  {
    id: "activity",
    label: "Actividad",
    icon: Activity,
    component: <UsuariosActivity />,
  },
  {
    id: "sessions",
    label: "Sesiones",
    icon: UserCheck,
    badge: "1",
    component: <UsuariosSessions />,
  },
  {
    id: "analytics",
    label: "Analytics",
    icon: MapPin,
    component: <UsuariosAnalytics />,
  },
  {
    id: "profiles",
    label: "Perfiles",
    icon: Clock,
    component: <UsuariosProfiles />,
  },
]

export function UsuariosActividadMain() {
  return (
    <SectionTabs
      title="🌍 USERS & ACTIVITY CONTROL"
      subtitle="Centro de Control Global de Usuarios y Analíticas de Participación"
      tabs={usuariosActividadTabs}
      defaultTab="global-map"
    />
  )
}

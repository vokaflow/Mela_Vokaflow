"use client"

import type * as React from "react"
import { useState } from "react"
import Image from "next/image"
import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  Home,
  Brain,
  Terminal,
  Wrench,
  TrendingUp,
  Globe,
  Radio,
  Dna,
  Briefcase,
  Shield,
  Users,
  Bell,
  Rocket,
  Languages,
  MessageSquare,
  BarChart,
  FolderOpen,
  Key,
  Webhook,
  Crown,
} from "lucide-react"

// Datos del menú de navegación
const menuItems = [
  {
    title: "🏠 Inicio",
    url: "/",
    icon: Home,
    color: "text-voka-magenta",
  },
  {
    title: "🧠 Vicky AI",
    url: "/vicky-ai",
    icon: Brain,
    color: "text-voka-blue",
  },
  {
    title: "💻 Terminal",
    url: "/terminal",
    icon: Terminal,
    color: "text-voka-green",
  },
  {
    title: "🔧 Infraestructura",
    url: "/infraestructura",
    icon: Wrench,
    color: "text-voka-orange",
  },
  {
    title: "📈 Estado Económico",
    url: "/estado-economico",
    icon: TrendingUp,
    color: "text-voka-yellow",
  },
  {
    title: "🌍 Usuarios / Actividad",
    url: "/usuarios-actividad",
    icon: Globe,
    color: "text-voka-blue",
  },
  {
    title: "📡 Endpoints API",
    url: "/endpoints-api",
    icon: Radio,
    color: "text-voka-green",
  },
  {
    title: "🧬 Laboratorio Kinect",
    url: "/laboratorio-kinect",
    icon: Dna,
    color: "text-voka-blue",
  },
  {
    title: "🧬 Modelos IA",
    url: "/modelos-ia",
    icon: Dna,
    color: "text-voka-magenta",
  },
  {
    title: "🌍 Traducción",
    url: "/traduccion",
    icon: Languages,
    color: "text-voka-green",
  },
  {
    title: "💬 Conversaciones",
    url: "/conversaciones",
    icon: MessageSquare,
    color: "text-voka-blue",
  },
  {
    title: "📊 Analytics",
    url: "/analytics",
    icon: BarChart,
    color: "text-voka-yellow",
  },
  {
    title: "📁 Files",
    url: "/files",
    icon: FolderOpen,
    color: "text-voka-orange",
  },
  {
    title: "🔑 API Keys",
    url: "/api-keys",
    icon: Key,
    color: "text-voka-blue",
  },
  {
    title: "🔗 Webhooks",
    url: "/webhooks",
    icon: Webhook,
    color: "text-voka-green",
  },
  {
    title: "👑 Admin",
    url: "/admin",
    icon: Crown,
    color: "text-voka-yellow",
  },
  {
    title: "🧰 Ajustes / Integraciones",
    url: "/ajustes-integraciones",
    icon: Briefcase,
    color: "text-voka-gray",
  },
  {
    title: "🔐 Seguridad",
    url: "/seguridad",
    icon: Shield,
    color: "text-voka-red",
  },
  {
    title: "👥 Roles y Permisos",
    url: "/roles-permisos",
    icon: Users,
    color: "text-voka-orange",
  },
  {
    title: "🔔 Notificaciones",
    url: "/notificaciones",
    icon: Bell,
    color: "text-voka-yellow",
  },
  {
    title: "🚀 Demo App",
    url: "/demo-app",
    icon: Rocket,
    color: "text-voka-magenta",
  },
]

export function VokaFlowSidebar({ ...props }: React.ComponentProps<"div">) {
  const pathname = usePathname()
  const [isExpanded, setIsExpanded] = useState(false)

  const scrollbarHideStyles = `
  /* Ocultar scrollbar para Chrome, Safari y Opera */
  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }
  
  /* Ocultar scrollbar para IE, Edge y Firefox */
  .scrollbar-hide {
    -ms-overflow-style: none;  /* IE y Edge */
    scrollbar-width: none;  /* Firefox */
  }
`

  return (
    <>
      <style jsx global>
        {scrollbarHideStyles}
      </style>
      <div
        className={`fixed left-0 top-0 h-full bg-voka-blue-black border-r border-voka-border transition-all duration-300 ease-in-out z-50 flex flex-col ${
          isExpanded ? "w-64" : "w-16"
        }`}
        onMouseEnter={() => setIsExpanded(true)}
        onMouseLeave={() => setIsExpanded(false)}
        {...props}
      >
        {/* Header */}
        <div className="border-b border-voka-border p-4 flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="relative flex-shrink-0">
              <Image src="/logo_vokaflow_icon.png" alt="VokaFlow" width={32} height={32} className="rounded-lg" />
              <div className="absolute inset-0 rounded-lg bg-voka-magenta/20 animate-neon-pulse"></div>
            </div>
            {isExpanded && (
              <div className="flex flex-col overflow-hidden">
                <span className="text-voka-white font-montserrat font-bold text-lg whitespace-nowrap">VokaFlow</span>
                <span className="text-voka-gray text-xs font-montserrat whitespace-nowrap">Dashboard Central</span>
              </div>
            )}
          </div>
        </div>

        {/* Menu Items */}
        <div className="flex-1 overflow-y-auto scrollbar-hide py-4">
          {menuItems.map((item) => {
            const isActive = pathname === item.url
            return (
              <Link
                key={item.title}
                href={item.url}
                className={`flex items-center gap-3 px-4 py-3 mx-2 mb-1 rounded-lg transition-all duration-200 font-montserrat group hover:bg-voka-border/50 ${
                  isActive ? "bg-voka-magenta/20 border-voka-magenta/50" : ""
                }`}
              >
                <item.icon
                  className={`h-5 w-5 flex-shrink-0 ${item.color} group-hover:animate-neon-pulse ${
                    isActive ? "text-voka-magenta" : ""
                  }`}
                />
                {isExpanded && (
                  <span
                    className={`text-voka-white group-hover:text-voka-magenta transition-colors whitespace-nowrap overflow-hidden ${
                      isActive ? "text-voka-magenta" : ""
                    }`}
                  >
                    {item.title}
                  </span>
                )}
              </Link>
            )
          })}
        </div>
      </div>
    </>
  )
}

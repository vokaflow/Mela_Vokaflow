"use client"

import { Bell, Search, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { useAuth } from "../hooks/use-auth"
import { useWebSocket } from "../hooks/use-websocket"
import { useEffect, useState } from "react"
import { Badge } from "@/components/ui/badge"

export function DashboardHeader() {
  const { user, logout } = useAuth()
  const { isConnected, subscribe, unsubscribe } = useWebSocket()
  const [unreadCount, setUnreadCount] = useState(0)

  useEffect(() => {
    if (isConnected && user) {
      // Suscribirse a notificaciones en tiempo real
      const handleNotification = (data: any) => {
        if (data.type === "unread_count") {
          setUnreadCount(data.count)
        }
      }

      subscribe("notifications", handleNotification)

      return () => {
        unsubscribe("notifications", handleNotification)
      }
    }
  }, [isConnected, user, subscribe, unsubscribe])

  return (
    <header className="flex h-16 items-center gap-4 border-b border-voka-border bg-voka-blue-black px-6">
      <SidebarTrigger className="text-voka-white hover:text-voka-magenta" />

      <div className="flex-1 flex items-center gap-4">
        <div className="relative max-w-md flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-voka-gray" />
          <Input
            placeholder="Buscar en VokaFlow..."
            className="pl-10 bg-voka-dark border-voka-border text-voka-white placeholder:text-voka-gray focus:border-voka-magenta font-montserrat"
          />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          className="text-voka-gray hover:text-voka-yellow hover:bg-voka-border/50 relative"
        >
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <Badge
              variant="destructive"
              className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs bg-voka-red"
            >
              {unreadCount > 99 ? "99+" : unreadCount}
            </Badge>
          )}
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="text-voka-gray hover:text-voka-magenta hover:bg-voka-border/50"
            >
              <User className="h-5 w-5" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="bg-voka-blue-black border-voka-border text-voka-white">
            <DropdownMenuLabel className="text-voka-magenta font-montserrat">
              {user?.username || "Usuario"}
            </DropdownMenuLabel>
            <DropdownMenuSeparator className="bg-voka-border" />
            <DropdownMenuItem className="hover:bg-voka-border/50 font-montserrat">Perfil</DropdownMenuItem>
            <DropdownMenuItem className="hover:bg-voka-border/50 font-montserrat">Configuración</DropdownMenuItem>
            <DropdownMenuSeparator className="bg-voka-border" />
            <DropdownMenuItem
              className="hover:bg-voka-border/50 text-voka-red font-montserrat cursor-pointer"
              onClick={logout}
            >
              Cerrar Sesión
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Indicador de conexión WebSocket */}
        <div
          className={`w-2 h-2 rounded-full ${isConnected ? "bg-green-500" : "bg-red-500"}`}
          title={isConnected ? "Conectado en tiempo real" : "Desconectado"}
        />
      </div>
    </header>
  )
}

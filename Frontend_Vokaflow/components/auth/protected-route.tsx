"use client"

import type React from "react"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "../../hooks/use-auth"
import { Loader2 } from "lucide-react"

interface ProtectedRouteProps {
  children: React.ReactNode
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login")
    }
  }, [user, isLoading, router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-voka-dark">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-voka-magenta mx-auto mb-4" />
          <p className="text-voka-white font-montserrat">Verificando autenticación...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return null // Se redirigirá al login
  }

  return <>{children}</>
}

"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Eye, EyeOff, Loader2 } from "lucide-react"
import { useAuth } from "../../hooks/use-auth"

export function LoginForm() {
  const [username, setUsername] = useState("dw7")
  const [password, setPassword] = useState("0069")
  const [showPassword, setShowPassword] = useState(false)
  const { login, isLoading, error, clearError } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()

    try {
      await login({ username, password })
      router.push("/") // Redirigir al dashboard
    } catch (error) {
      // El error ya se maneja en el hook useAuth
      console.error("Error en login:", error)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-voka-dark p-4">
      <Card className="w-full max-w-md bg-voka-blue-black border-voka-border">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 w-16 h-16 bg-voka-magenta rounded-lg flex items-center justify-center">
            <span className="text-2xl font-bold text-white">V</span>
          </div>
          <CardTitle className="text-2xl font-bold text-voka-white font-montserrat">VokaFlow Dashboard</CardTitle>
          <CardDescription className="text-voka-gray font-montserrat">
            Ingresa tus credenciales para acceder
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <Alert className="border-voka-red bg-voka-red/10">
                <AlertDescription className="text-voka-red font-montserrat">{error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="username" className="text-voka-white font-montserrat">
                Usuario
              </Label>
              <Input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="bg-voka-dark border-voka-border text-voka-white placeholder:text-voka-gray focus:border-voka-magenta font-montserrat"
                placeholder="Ingresa tu usuario"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-voka-white font-montserrat">
                Contraseña
              </Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="bg-voka-dark border-voka-border text-voka-white placeholder:text-voka-gray focus:border-voka-magenta font-montserrat pr-10"
                  placeholder="Ingresa tu contraseña"
                  required
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute right-0 top-0 h-full px-3 text-voka-gray hover:text-voka-white"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
              </div>
            </div>

            <Button
              type="submit"
              className="w-full bg-voka-magenta hover:bg-voka-magenta/80 text-white font-montserrat"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Iniciando sesión...
                </>
              ) : (
                "Iniciar Sesión"
              )}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-voka-gray font-montserrat">
              Usuario por defecto: <span className="text-voka-magenta">dw7</span>
            </p>
            <p className="text-sm text-voka-gray font-montserrat">
              Contraseña: <span className="text-voka-magenta">0069</span>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

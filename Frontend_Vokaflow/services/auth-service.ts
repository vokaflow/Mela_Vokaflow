import { buildApiUrl, ENDPOINTS } from "../lib/api-config"
import type { LoginCredentials, RegisterData, AuthResponse, AuthUser } from "../types/auth"

class AuthService {
  private readonly TOKEN_KEY = "vokaflow_token"
  private readonly USER_KEY = "vokaflow_user"

  // Login con credenciales
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await fetch(buildApiUrl(ENDPOINTS.AUTH.LOGIN), {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          username: credentials.username,
          password: credentials.password,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Error ${response.status}: ${response.statusText}`)
      }

      const authData: AuthResponse = await response.json()

      // Guardar token en localStorage
      if (authData.access_token) {
        this.setToken(authData.access_token)

        // Si viene información del usuario, guardarla
        if (authData.user) {
          this.setUser(authData.user)
        }
      }

      return authData
    } catch (error) {
      console.error("Error en login:", error)
      throw error
    }
  }

  // Registro de nuevo usuario
  async register(userData: RegisterData): Promise<AuthResponse> {
    try {
      const response = await fetch(buildApiUrl(ENDPOINTS.AUTH.REGISTER), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(userData),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Error ${response.status}: ${response.statusText}`)
      }

      const authData: AuthResponse = await response.json()

      // Guardar token si viene en el registro
      if (authData.access_token) {
        this.setToken(authData.access_token)

        if (authData.user) {
          this.setUser(authData.user)
        }
      }

      return authData
    } catch (error) {
      console.error("Error en registro:", error)
      throw error
    }
  }

  // Obtener información del usuario actual
  async getCurrentUser(): Promise<AuthUser> {
    const token = this.getToken()
    if (!token) {
      throw new Error("No hay token de autenticación")
    }

    try {
      const response = await fetch(buildApiUrl(ENDPOINTS.USERS.ME), {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      })

      if (!response.ok) {
        if (response.status === 401) {
          this.logout() // Token inválido, hacer logout
          throw new Error("Token inválido")
        }
        throw new Error(`Error ${response.status}: ${response.statusText}`)
      }

      const userData = await response.json()
      const user: AuthUser = {
        ...userData,
        isAuthenticated: true,
      }

      this.setUser(user)
      return user
    } catch (error) {
      console.error("Error obteniendo usuario actual:", error)
      throw error
    }
  }

  // Logout
  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY)
    localStorage.removeItem(this.USER_KEY)
  }

  // Verificar si está autenticado
  isAuthenticated(): boolean {
    const token = this.getToken()
    const user = this.getStoredUser()
    return !!(token && user)
  }

  // Obtener token del localStorage
  getToken(): string | null {
    if (typeof window === "undefined") return null
    return localStorage.getItem(this.TOKEN_KEY)
  }

  // Guardar token en localStorage
  private setToken(token: string): void {
    if (typeof window !== "undefined") {
      localStorage.setItem(this.TOKEN_KEY, token)
    }
  }

  // Obtener usuario del localStorage
  getStoredUser(): AuthUser | null {
    if (typeof window === "undefined") return null
    const userStr = localStorage.getItem(this.USER_KEY)
    if (!userStr) return null

    try {
      return JSON.parse(userStr)
    } catch {
      return null
    }
  }

  // Guardar usuario en localStorage
  private setUser(user: Partial<AuthUser>): void {
    if (typeof window !== "undefined") {
      const fullUser: AuthUser = {
        id: user.id || "",
        username: user.username || "",
        email: user.email || "",
        role: user.role || "user",
        isAuthenticated: true,
      }
      localStorage.setItem(this.USER_KEY, JSON.stringify(fullUser))
    }
  }

  // Verificar si el token está expirado (opcional)
  isTokenExpired(): boolean {
    // Implementar lógica de verificación de expiración si es necesario
    // Por ahora retornamos false
    return false
  }

  // Refrescar token (si tu API lo soporta)
  async refreshToken(): Promise<string | null> {
    // Implementar si tu API tiene endpoint de refresh
    return null
  }
}

export const authService = new AuthService()

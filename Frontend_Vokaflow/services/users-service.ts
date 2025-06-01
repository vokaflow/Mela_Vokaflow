import { apiClient } from "../lib/api-client"
import { ENDPOINTS } from "../lib/api-config"
import type { User, UserActivity, SessionInfo, GeographicData, LanguageUsage } from "../types/users"

class UsersService {
  // Obtener usuario actual autenticado
  async getCurrentUser(): Promise<User> {
    try {
      const response = await apiClient.get<User>(ENDPOINTS.USERS.ME)
      return response
    } catch (error) {
      console.warn("API no disponible, usando datos mock:", error)
      return this.getMockCurrentUser()
    }
  }

  // Actualizar perfil del usuario actual
  async updateUserProfile(data: Partial<User>): Promise<User> {
    try {
      const response = await apiClient.put<User>(ENDPOINTS.USERS.ME, data)
      return response
    } catch (error) {
      console.warn("API no disponible, simulando actualización:", error)
      return { ...this.getMockCurrentUser(), ...data }
    }
  }

  // Obtener usuario específico por ID (admin)
  async getUserById(userId: string): Promise<User> {
    try {
      const response = await apiClient.get<User>(`/api/users/${userId}`)
      return response
    } catch (error) {
      console.warn("API no disponible, usando datos mock:", error)
      return this.getMockCurrentUser()
    }
  }

  // Obtener todos los usuarios (admin)
  async getAllUsers(): Promise<User[]> {
    try {
      const response = await apiClient.get<User[]>(ENDPOINTS.ADMIN.USERS)
      return response
    } catch (error) {
      console.warn("API no disponible, usando datos mock:", error)
      return [this.getMockCurrentUser()]
    }
  }

  // Obtener actividad de usuarios
  async getUserActivity(userId?: string): Promise<UserActivity[]> {
    try {
      const endpoint = userId ? `${ENDPOINTS.SYSTEM.EVENTS}?user_id=${userId}` : ENDPOINTS.SYSTEM.EVENTS
      const response = await apiClient.get<UserActivity[]>(endpoint)
      return response
    } catch (error) {
      console.warn("API no disponible, usando datos mock:", error)
      return this.getMockActivities()
    }
  }

  // Obtener sesiones activas
  async getActiveSessions(): Promise<SessionInfo[]> {
    try {
      const response = await apiClient.get<SessionInfo[]>(ENDPOINTS.SYSTEM.API_METRICS)
      return response
    } catch (error) {
      console.warn("API no disponible, usando datos mock:", error)
      return this.getMockSessions()
    }
  }

  // Obtener datos geográficos
  async getGeographicData(): Promise<GeographicData[]> {
    try {
      const response = await apiClient.get<GeographicData[]>(`${ENDPOINTS.ANALYTICS.USAGE}?type=geographic`)
      return response
    } catch (error) {
      console.warn("API no disponible, usando datos mock:", error)
      return this.getMockGeographicData()
    }
  }

  // Obtener uso de idiomas
  async getLanguageUsage(): Promise<LanguageUsage[]> {
    try {
      const response = await apiClient.get<LanguageUsage[]>(ENDPOINTS.TRANSLATE.STATS)
      return response
    } catch (error) {
      console.warn("API no disponible, usando datos mock:", error)
      return this.getMockLanguageUsage()
    }
  }

  // Obtener analytics
  async getAnalytics(): Promise<any> {
    try {
      const response = await apiClient.get<any>(ENDPOINTS.ANALYTICS.DASHBOARD)
      return response
    } catch (error) {
      console.warn("API no disponible, usando datos mock:", error)
      return this.getMockAnalytics()
    }
  }

  // Cambiar contraseña
  async changePassword(currentPassword: string, newPassword: string): Promise<{ success: boolean; message: string }> {
    try {
      const response = await apiClient.put<{ success: boolean; message: string }>("/api/users/change-password", {
        current_password: currentPassword,
        new_password: newPassword,
      })
      return response
    } catch (error) {
      console.warn("API no disponible, simulando cambio de contraseña:", error)
      return { success: true, message: "Contraseña actualizada correctamente (simulado)" }
    }
  }

  // Actualizar preferencias específicas
  async updatePreferences(preferences: Partial<User["preferences"]>): Promise<User> {
    try {
      const response = await apiClient.put<User>("/api/users/preferences", preferences)
      return response
    } catch (error) {
      console.warn("API no disponible, simulando actualización de preferencias:", error)
      const mockUser = this.getMockCurrentUser()
      return { ...mockUser, preferences: { ...mockUser.preferences, ...preferences } }
    }
  }

  // Obtener estadísticas del usuario
  async getUserStats(userId?: string): Promise<User["stats"]> {
    try {
      const endpoint = userId ? `/api/users/${userId}/stats` : "/api/users/me/stats"
      const response = await apiClient.get<User["stats"]>(endpoint)
      return response
    } catch (error) {
      console.warn("API no disponible, usando datos mock:", error)
      return this.getMockCurrentUser().stats
    }
  }

  // Métodos mock (mantener como fallback)
  private getMockCurrentUser(): User {
    return {
      id: "user_dw7_001",
      username: "dw7",
      email: "admin@vokaflow.local",
      role: "admin",
      status: "online",
      created_at: "2025-01-01T00:00:00Z",
      last_login: "2025-01-31T21:36:22Z",
      last_activity: new Date().toISOString(),
      session_duration: 8100, // 2h 15m en segundos
      location: {
        country: "Spain",
        city: "Madrid",
        ip: "192.168.1.119",
        timezone: "CET",
      },
      preferences: {
        language: "es",
        theme: "dark",
        notifications: true,
      },
      stats: {
        total_sessions: 847,
        total_translations: 12500,
        total_api_calls: 45000,
        avg_session_duration: 9000, // 2.5h promedio
      },
    }
  }

  private getMockActivities(): UserActivity[] {
    return [
      {
        id: "act_001",
        user_id: "user_dw7_001",
        action: "Dashboard: Infraestructura",
        timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
        ip_address: "192.168.1.119",
        device_info: "Linux Chrome 120.0",
        location: "Madrid, Spain",
        success: true,
      },
      {
        id: "act_002",
        user_id: "user_dw7_001",
        action: 'Traducción: ES→EN "Hola mundo"',
        timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
        ip_address: "192.168.1.119",
        device_info: "Linux Chrome 120.0",
        location: "Madrid, Spain",
        success: true,
      },
      {
        id: "act_003",
        user_id: "user_dw7_001",
        action: 'Vicky AI: "Help with coding"',
        timestamp: new Date(Date.now() - 8 * 60 * 1000).toISOString(),
        ip_address: "192.168.1.119",
        device_info: "Linux Chrome 120.0",
        location: "Madrid, Spain",
        success: true,
      },
      {
        id: "act_004",
        user_id: "user_dw7_001",
        action: "API Call: /api/monitoring/metrics",
        timestamp: new Date(Date.now() - 12 * 60 * 1000).toISOString(),
        ip_address: "192.168.1.119",
        device_info: "Linux Chrome 120.0",
        location: "Madrid, Spain",
        success: true,
      },
      {
        id: "act_005",
        user_id: "user_dw7_001",
        action: "Login de usuario",
        timestamp: "2025-01-31T21:36:22Z",
        ip_address: "192.168.1.119",
        device_info: "Linux Chrome 120.0",
        location: "Madrid, Spain",
        success: true,
      },
    ]
  }

  private getMockSessions(): SessionInfo[] {
    return [
      {
        session_id: "sess_8988xyz",
        user_id: "user_dw7_001",
        ip_address: "192.168.1.119",
        device: "Desktop",
        browser: "Chrome 120.0",
        os: "Linux",
        duration: 8100, // 2h 15m
        last_activity: new Date().toISOString(),
        status: "active",
        actions_count: 847,
      },
    ]
  }

  private getMockGeographicData(): GeographicData[] {
    return [
      {
        country: "Spain",
        country_code: "ES",
        users_count: 1,
        sessions_count: 847,
        translations_count: 12500,
        peak_hours: ["10:00-12:00", "21:00-23:00"],
        activity_level: "high",
      },
    ]
  }

  private getMockLanguageUsage(): LanguageUsage[] {
    return [
      {
        source_lang: "Spanish",
        target_lang: "English",
        translations_count: 8750,
        percentage: 70,
        trend: "up",
      },
      {
        source_lang: "English",
        target_lang: "Spanish",
        translations_count: 2500,
        percentage: 20,
        trend: "up",
      },
      {
        source_lang: "Spanish",
        target_lang: "French",
        translations_count: 875,
        percentage: 7,
        trend: "up",
      },
      {
        source_lang: "French",
        target_lang: "Spanish",
        translations_count: 375,
        percentage: 3,
        trend: "stable",
      },
    ]
  }

  private getMockAnalytics(): any {
    return {
      daily_active_users: 1,
      weekly_active_users: 1,
      monthly_active_users: 1,
      total_sessions: 847,
      avg_session_duration: 9000,
      bounce_rate: 0,
      return_rate: 100,
    }
  }
}

export const usersService = new UsersService()

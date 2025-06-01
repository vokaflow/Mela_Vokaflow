import type {
  User,
  Role,
  Permission,
  PermissionCategory,
  AccessPolicy,
  AuditLog,
  UserSession,
  PermissionMatrix,
  RoleHierarchy,
  AccessStats,
} from "@/types/roles-permissions"

class RolesPermissionsService {
  private baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

  // User Management
  async getUsers(): Promise<User[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/users`)
      if (!response.ok) throw new Error("Failed to fetch users")
      return await response.json()
    } catch (error) {
      console.error("Error fetching users:", error)
      return this.getMockUsers()
    }
  }

  async createUser(user: Omit<User, "id" | "created_at" | "session_count">): Promise<User> {
    try {
      const response = await fetch(`${this.baseUrl}/api/users`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(user),
      })
      if (!response.ok) throw new Error("Failed to create user")
      return await response.json()
    } catch (error) {
      console.error("Error creating user:", error)
      throw error
    }
  }

  async updateUser(id: string, user: Partial<User>): Promise<User> {
    try {
      const response = await fetch(`${this.baseUrl}/api/users/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(user),
      })
      if (!response.ok) throw new Error("Failed to update user")
      return await response.json()
    } catch (error) {
      console.error("Error updating user:", error)
      throw error
    }
  }

  async deleteUser(id: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/users/${id}`, {
        method: "DELETE",
      })
      if (!response.ok) throw new Error("Failed to delete user")
    } catch (error) {
      console.error("Error deleting user:", error)
      throw error
    }
  }

  async getUserPermissions(id: string): Promise<string[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/users/${id}/permissions`)
      if (!response.ok) throw new Error("Failed to fetch user permissions")
      return await response.json()
    } catch (error) {
      console.error("Error fetching user permissions:", error)
      return []
    }
  }

  async assignRolesToUser(userId: string, roleIds: string[]): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/users/${userId}/roles`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role_ids: roleIds }),
      })
      if (!response.ok) throw new Error("Failed to assign roles")
    } catch (error) {
      console.error("Error assigning roles:", error)
      throw error
    }
  }

  // Role Management
  async getRoles(): Promise<Role[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/roles`)
      if (!response.ok) throw new Error("Failed to fetch roles")
      return await response.json()
    } catch (error) {
      console.error("Error fetching roles:", error)
      return this.getMockRoles()
    }
  }

  async createRole(role: Omit<Role, "id" | "created_at" | "updated_at" | "user_count">): Promise<Role> {
    try {
      const response = await fetch(`${this.baseUrl}/api/roles`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(role),
      })
      if (!response.ok) throw new Error("Failed to create role")
      return await response.json()
    } catch (error) {
      console.error("Error creating role:", error)
      throw error
    }
  }

  async updateRole(id: string, role: Partial<Role>): Promise<Role> {
    try {
      const response = await fetch(`${this.baseUrl}/api/roles/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(role),
      })
      if (!response.ok) throw new Error("Failed to update role")
      return await response.json()
    } catch (error) {
      console.error("Error updating role:", error)
      throw error
    }
  }

  async deleteRole(id: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/roles/${id}`, {
        method: "DELETE",
      })
      if (!response.ok) throw new Error("Failed to delete role")
    } catch (error) {
      console.error("Error deleting role:", error)
      throw error
    }
  }

  // Permission Management
  async getPermissions(): Promise<Permission[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/permissions`)
      if (!response.ok) throw new Error("Failed to fetch permissions")
      return await response.json()
    } catch (error) {
      console.error("Error fetching permissions:", error)
      return this.getMockPermissions()
    }
  }

  async getPermissionCategories(): Promise<PermissionCategory[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/permissions/categories`)
      if (!response.ok) throw new Error("Failed to fetch permission categories")
      return await response.json()
    } catch (error) {
      console.error("Error fetching permission categories:", error)
      return this.getMockPermissionCategories()
    }
  }

  async getPermissionMatrix(): Promise<PermissionMatrix> {
    try {
      const response = await fetch(`${this.baseUrl}/api/admin/access-matrix`)
      if (!response.ok) throw new Error("Failed to fetch permission matrix")
      return await response.json()
    } catch (error) {
      console.error("Error fetching permission matrix:", error)
      return this.getMockPermissionMatrix()
    }
  }

  async updatePermissionMatrix(matrix: Record<string, Record<string, boolean>>): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/admin/access-matrix`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ matrix }),
      })
      if (!response.ok) throw new Error("Failed to update permission matrix")
    } catch (error) {
      console.error("Error updating permission matrix:", error)
      throw error
    }
  }

  // Access Policies
  async getAccessPolicies(): Promise<AccessPolicy[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/auth/policies`)
      if (!response.ok) throw new Error("Failed to fetch access policies")
      return await response.json()
    } catch (error) {
      console.error("Error fetching access policies:", error)
      return this.getMockAccessPolicies()
    }
  }

  async updateAccessPolicies(policies: AccessPolicy[]): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/auth/policies`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ policies }),
      })
      if (!response.ok) throw new Error("Failed to update access policies")
    } catch (error) {
      console.error("Error updating access policies:", error)
      throw error
    }
  }

  // Audit and Monitoring
  async getAuditLogs(limit = 100, filters?: any): Promise<AuditLog[]> {
    try {
      const params = new URLSearchParams({ limit: limit.toString() })
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value) params.append(key, value as string)
        })
      }

      const response = await fetch(`${this.baseUrl}/api/auth/audit?${params}`)
      if (!response.ok) throw new Error("Failed to fetch audit logs")
      return await response.json()
    } catch (error) {
      console.error("Error fetching audit logs:", error)
      return this.getMockAuditLogs()
    }
  }

  async getActiveSessions(): Promise<UserSession[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/auth/sessions`)
      if (!response.ok) throw new Error("Failed to fetch active sessions")
      return await response.json()
    } catch (error) {
      console.error("Error fetching active sessions:", error)
      return this.getMockActiveSessions()
    }
  }

  async terminateSession(sessionId: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/auth/sessions/${sessionId}`, {
        method: "DELETE",
      })
      if (!response.ok) throw new Error("Failed to terminate session")
    } catch (error) {
      console.error("Error terminating session:", error)
      throw error
    }
  }

  async getAccessStats(): Promise<AccessStats> {
    try {
      const response = await fetch(`${this.baseUrl}/api/auth/stats`)
      if (!response.ok) throw new Error("Failed to fetch access stats")
      return await response.json()
    } catch (error) {
      console.error("Error fetching access stats:", error)
      return this.getMockAccessStats()
    }
  }

  async getRoleHierarchy(): Promise<RoleHierarchy[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/roles/hierarchy`)
      if (!response.ok) throw new Error("Failed to fetch role hierarchy")
      return await response.json()
    } catch (error) {
      console.error("Error fetching role hierarchy:", error)
      return this.getMockRoleHierarchy()
    }
  }

  // Emergency Actions
  async emergencyLockdown(): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/auth/emergency/lockdown`, {
        method: "POST",
      })
      if (!response.ok) throw new Error("Failed to activate emergency lockdown")
    } catch (error) {
      console.error("Error activating emergency lockdown:", error)
      throw error
    }
  }

  async revokeAllSessions(userId: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/users/${userId}/sessions/revoke-all`, {
        method: "POST",
      })
      if (!response.ok) throw new Error("Failed to revoke all sessions")
    } catch (error) {
      console.error("Error revoking all sessions:", error)
      throw error
    }
  }

  // Mock Data Methods
  private getMockUsers(): User[] {
    return [
      {
        id: "1",
        username: "dw7",
        email: "dw7@vokaflow.com",
        full_name: "David Wilson",
        avatar_url: "/placeholder.svg?height=40&width=40",
        status: "online",
        roles: ["super_admin"],
        created_at: "2025-01-01T00:00:00Z",
        last_login: "2025-01-31T11:45:00Z",
        last_activity: "2025-01-31T11:50:00Z",
        is_active: true,
        failed_login_attempts: 0,
        session_count: 3,
        location: {
          country: "Spain",
          city: "Madrid",
          ip: "192.168.1.100",
        },
      },
    ]
  }

  private getMockRoles(): Role[] {
    return [
      {
        id: "super_admin",
        name: "super_admin",
        display_name: "Super Admin",
        description: "Acceso total al sistema VokaFlow",
        icon: "👑",
        color: "#D8409F",
        level: 0,
        permissions: ["*"],
        user_count: 1,
        created_at: "2025-01-01T00:00:00Z",
        updated_at: "2025-01-01T00:00:00Z",
        is_system_role: true,
      },
      {
        id: "admin_tecnico",
        name: "admin_tecnico",
        display_name: "Admin Técnico",
        description: "Gestión de infraestructura y sistemas",
        icon: "🔧",
        color: "#0078FF",
        level: 1,
        parent_role_id: "super_admin",
        permissions: ["system.*", "infrastructure.*", "security.*"],
        user_count: 0,
        created_at: "2025-01-01T00:00:00Z",
        updated_at: "2025-01-01T00:00:00Z",
        is_system_role: true,
      },
      {
        id: "admin_ia",
        name: "admin_ia",
        display_name: "Admin IA",
        description: "Gestión de modelos de IA y Vicky",
        icon: "🧠",
        color: "#35FF83",
        level: 1,
        parent_role_id: "super_admin",
        permissions: ["models.*", "vicky.*", "ai.*"],
        user_count: 0,
        created_at: "2025-01-01T00:00:00Z",
        updated_at: "2025-01-01T00:00:00Z",
        is_system_role: true,
      },
      {
        id: "admin_negocio",
        name: "admin_negocio",
        display_name: "Admin Negocio",
        description: "Analytics, usuarios y métricas comerciales",
        icon: "💼",
        color: "#FFA700",
        level: 1,
        parent_role_id: "super_admin",
        permissions: ["analytics.*", "users.read", "business.*"],
        user_count: 0,
        created_at: "2025-01-01T00:00:00Z",
        updated_at: "2025-01-01T00:00:00Z",
        is_system_role: true,
      },
      {
        id: "developer",
        name: "developer",
        display_name: "Developer",
        description: "Desarrollo, APIs y testing",
        icon: "👨‍💻",
        color: "#FF3366",
        level: 2,
        permissions: ["api.*", "endpoints.*", "testing.*", "logs.read"],
        user_count: 0,
        created_at: "2025-01-01T00:00:00Z",
        updated_at: "2025-01-01T00:00:00Z",
        is_system_role: true,
      },
      {
        id: "analyst",
        name: "analyst",
        display_name: "Analyst",
        description: "Solo lectura, reportes y métricas",
        icon: "📊",
        color: "#FFFB00",
        level: 3,
        permissions: ["*.read", "reports.*", "analytics.read"],
        user_count: 0,
        created_at: "2025-01-01T00:00:00Z",
        updated_at: "2025-01-01T00:00:00Z",
        is_system_role: true,
      },
    ]
  }

  private getMockPermissions(): Permission[] {
    const categories = [
      "system",
      "users",
      "roles",
      "ai",
      "api",
      "data",
      "security",
      "analytics",
      "infrastructure",
      "business",
    ]
    const actions = ["create", "read", "update", "delete", "execute", "manage"]

    const permissions: Permission[] = []
    let id = 1

    categories.forEach((category) => {
      actions.forEach((action) => {
        permissions.push({
          id: `${id}`,
          name: `${category}.${action}`,
          display_name: `${category.charAt(0).toUpperCase() + category.slice(1)} ${action.charAt(0).toUpperCase() + action.slice(1)}`,
          description: `Permite ${action} en ${category}`,
          category,
          resource: category,
          action,
          is_dangerous: action === "delete" || (category === "system" && action === "execute"),
          requires_approval: action === "delete" && ["users", "system", "data"].includes(category),
          created_at: "2025-01-01T00:00:00Z",
        })
        id++
      })
    })

    return permissions
  }

  private getMockPermissionCategories(): PermissionCategory[] {
    return [
      {
        id: "system",
        name: "system",
        display_name: "Sistema",
        description: "Permisos de sistema y configuración",
        icon: "⚙️",
        color: "#0078FF",
        permissions: this.getMockPermissions().filter((p) => p.category === "system"),
      },
      {
        id: "users",
        name: "users",
        display_name: "Usuarios",
        description: "Gestión de usuarios y perfiles",
        icon: "👥",
        color: "#35FF83",
        permissions: this.getMockPermissions().filter((p) => p.category === "users"),
      },
      {
        id: "ai",
        name: "ai",
        display_name: "Inteligencia Artificial",
        description: "Modelos de IA y Vicky",
        icon: "🧠",
        color: "#D8409F",
        permissions: this.getMockPermissions().filter((p) => p.category === "ai"),
      },
    ]
  }

  private getMockPermissionMatrix(): PermissionMatrix {
    const roles = this.getMockRoles()
    const permissions = this.getMockPermissions()
    const matrix: Record<string, Record<string, boolean | "inherited" | "conditional">> = {}

    roles.forEach((role) => {
      matrix[role.id] = {}
      permissions.forEach((permission) => {
        if (role.id === "super_admin") {
          matrix[role.id][permission.id] = true
        } else if (role.permissions.includes("*")) {
          matrix[role.id][permission.id] = true
        } else if (role.permissions.some((p) => permission.name.startsWith(p.replace(".*", "")))) {
          matrix[role.id][permission.id] = true
        } else if (role.parent_role_id) {
          matrix[role.id][permission.id] = "inherited"
        } else {
          matrix[role.id][permission.id] = false
        }
      })
    })

    return { roles, permissions, matrix }
  }

  private getMockAccessPolicies(): AccessPolicy[] {
    return [
      {
        id: "1",
        name: "Horario Laboral",
        description: "Restricción de acceso fuera del horario laboral",
        type: "time_restriction",
        enabled: true,
        rules: [
          {
            condition: "time_range",
            action: "deny",
            value: { start: "18:00", end: "08:00", timezone: "Europe/Madrid" },
          },
        ],
        applies_to: {
          roles: ["developer", "analyst"],
        },
        created_at: "2025-01-01T00:00:00Z",
        updated_at: "2025-01-01T00:00:00Z",
      },
      {
        id: "2",
        name: "Geo-restricción",
        description: "Bloquear acceso desde países de alto riesgo",
        type: "ip_restriction",
        enabled: true,
        rules: [
          {
            condition: "country_code",
            action: "deny",
            value: ["CN", "RU", "KP"],
          },
        ],
        applies_to: {},
        created_at: "2025-01-01T00:00:00Z",
        updated_at: "2025-01-01T00:00:00Z",
      },
    ]
  }

  private getMockAuditLogs(): AuditLog[] {
    return [
      {
        id: "1",
        timestamp: "2025-01-31T11:45:00Z",
        user_id: "1",
        user_name: "dw7",
        action: "login",
        resource_type: "user",
        resource_id: "1",
        resource_name: "dw7",
        changes: [],
        ip_address: "192.168.1.100",
        user_agent: "Mozilla/5.0 (X11; Linux x86_64) Chrome/131.0",
        success: true,
      },
      {
        id: "2",
        timestamp: "2025-01-31T10:30:00Z",
        user_id: "1",
        user_name: "dw7",
        action: "update_permissions",
        resource_type: "role",
        resource_id: "developer",
        resource_name: "Developer",
        changes: [
          {
            field: "permissions",
            old_value: ["api.read"],
            new_value: ["api.read", "api.write"],
          },
        ],
        ip_address: "192.168.1.100",
        user_agent: "Mozilla/5.0 (X11; Linux x86_64) Chrome/131.0",
        success: true,
      },
    ]
  }

  private getMockActiveSessions(): UserSession[] {
    return [
      {
        id: "1",
        user_id: "1",
        user_name: "dw7",
        ip_address: "192.168.1.100",
        user_agent: "Mozilla/5.0 (X11; Linux x86_64) Chrome/131.0",
        location: {
          country: "Spain",
          city: "Madrid",
          coordinates: [40.4168, -3.7038],
        },
        created_at: "2025-01-31T08:00:00Z",
        last_activity: "2025-01-31T11:50:00Z",
        expires_at: "2025-02-01T08:00:00Z",
        is_active: true,
      },
      {
        id: "2",
        user_id: "1",
        user_name: "dw7",
        ip_address: "192.168.1.101",
        user_agent: "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
        location: {
          country: "Spain",
          city: "Madrid",
          coordinates: [40.4168, -3.7038],
        },
        created_at: "2025-01-31T09:30:00Z",
        last_activity: "2025-01-31T11:30:00Z",
        expires_at: "2025-02-01T09:30:00Z",
        is_active: true,
      },
    ]
  }

  private getMockAccessStats(): AccessStats {
    return {
      total_users: 1,
      active_users: 1,
      total_roles: 6,
      total_permissions: 47,
      active_sessions: 3,
      failed_logins_today: 0,
      permission_changes_today: 2,
      policy_violations_today: 0,
    }
  }

  private getMockRoleHierarchy(): RoleHierarchy[] {
    const roles = this.getMockRoles()
    const superAdmin = roles.find((r) => r.id === "super_admin")!

    return [
      {
        role: superAdmin,
        children: [
          {
            role: roles.find((r) => r.id === "admin_tecnico")!,
            children: [],
            inherited_permissions: ["*"],
          },
          {
            role: roles.find((r) => r.id === "admin_ia")!,
            children: [],
            inherited_permissions: ["*"],
          },
          {
            role: roles.find((r) => r.id === "admin_negocio")!,
            children: [
              {
                role: roles.find((r) => r.id === "analyst")!,
                children: [],
                inherited_permissions: ["analytics.*", "users.read", "business.*"],
              },
            ],
            inherited_permissions: ["*"],
          },
          {
            role: roles.find((r) => r.id === "developer")!,
            children: [],
            inherited_permissions: [],
          },
        ],
        inherited_permissions: [],
      },
    ]
  }
}

export const rolesPermissionsService = new RolesPermissionsService()

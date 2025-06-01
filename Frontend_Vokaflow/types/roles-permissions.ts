export interface User {
  id: string
  username: string
  email: string
  full_name: string
  avatar_url?: string
  status: "online" | "offline" | "away"
  roles: string[]
  created_at: string
  last_login?: string
  last_activity?: string
  is_active: boolean
  failed_login_attempts: number
  locked_until?: string
  session_count: number
  location?: {
    country: string
    city: string
    ip: string
  }
}

export interface Role {
  id: string
  name: string
  display_name: string
  description: string
  icon: string
  color: string
  level: number
  parent_role_id?: string
  permissions: string[]
  user_count: number
  created_at: string
  updated_at: string
  is_system_role: boolean
}

export interface Permission {
  id: string
  name: string
  display_name: string
  description: string
  category: string
  resource: string
  action: string
  is_dangerous: boolean
  requires_approval: boolean
  created_at: string
}

export interface PermissionCategory {
  id: string
  name: string
  display_name: string
  description: string
  icon: string
  color: string
  permissions: Permission[]
}

export interface AccessPolicy {
  id: string
  name: string
  description: string
  type: "ip_restriction" | "time_restriction" | "device_restriction" | "mfa_requirement"
  enabled: boolean
  rules: {
    condition: string
    action: "allow" | "deny" | "require_mfa"
    value: any
  }[]
  applies_to: {
    users?: string[]
    roles?: string[]
    permissions?: string[]
  }
  created_at: string
  updated_at: string
}

export interface AuditLog {
  id: string
  timestamp: string
  user_id: string
  user_name: string
  action: string
  resource_type: "user" | "role" | "permission" | "policy"
  resource_id: string
  resource_name: string
  changes: {
    field: string
    old_value: any
    new_value: any
  }[]
  ip_address: string
  user_agent: string
  success: boolean
  reason?: string
}

export interface UserSession {
  id: string
  user_id: string
  user_name: string
  ip_address: string
  user_agent: string
  location: {
    country: string
    city: string
    coordinates?: [number, number]
  }
  created_at: string
  last_activity: string
  expires_at: string
  is_active: boolean
}

export interface PermissionMatrix {
  roles: Role[]
  permissions: Permission[]
  matrix: Record<string, Record<string, boolean | "inherited" | "conditional">>
}

export interface RoleHierarchy {
  role: Role
  children: RoleHierarchy[]
  inherited_permissions: string[]
}

export interface AccessStats {
  total_users: number
  active_users: number
  total_roles: number
  total_permissions: number
  active_sessions: number
  failed_logins_today: number
  permission_changes_today: number
  policy_violations_today: number
}

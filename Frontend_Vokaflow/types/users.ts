export interface User {
  id: string
  username: string
  email: string
  role: "admin" | "user" | "api" | "system"
  status: "online" | "offline" | "away"
  created_at: string
  last_login: string
  last_activity: string
  session_duration: number
  location: {
    country: string
    city: string
    ip: string
    timezone: string
  }
  preferences: {
    language: string
    theme: string
    notifications: boolean
  }
  stats: {
    total_sessions: number
    total_translations: number
    total_api_calls: number
    avg_session_duration: number
  }
}

export interface UserActivity {
  id: string
  user_id: string
  action: string
  timestamp: string
  ip_address: string
  device_info: string
  location: string
  success: boolean
  details?: any
}

export interface SessionInfo {
  session_id: string
  user_id: string
  ip_address: string
  device: string
  browser: string
  os: string
  duration: number
  last_activity: string
  status: "active" | "expired" | "terminated"
  actions_count: number
}

export interface GeographicData {
  country: string
  country_code: string
  users_count: number
  sessions_count: number
  translations_count: number
  peak_hours: string[]
  activity_level: "high" | "medium" | "low"
}

export interface LanguageUsage {
  source_lang: string
  target_lang: string
  translations_count: number
  percentage: number
  trend: "up" | "down" | "stable"
}

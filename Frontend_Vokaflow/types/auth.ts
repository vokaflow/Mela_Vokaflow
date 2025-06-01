export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  role?: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  expires_in?: number
  user?: {
    id: string
    username: string
    email: string
    role: string
  }
}

export interface AuthUser {
  id: string
  username: string
  email: string
  role: string
  isAuthenticated: boolean
}

export interface AuthState {
  user: AuthUser | null
  token: string | null
  isLoading: boolean
  error: string | null
}

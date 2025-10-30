import { apiFetch } from '@/utils/api'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface User {
  id: number
  workos_id: string
  email: string
  role: 'user' | 'admin'
}

export class AuthService {
  static async getLoginUrl(provider: string = 'GoogleOAuth'): Promise<{ authorization_url: string }> {
    const response = await fetch(`${API_BASE_URL}/auth/login?provider=${encodeURIComponent(provider)}`)
    if (!response.ok) {
      throw new Error('Failed to get login URL')
    }
    return response.json()
  }

  static async handleCallback(code: string, state: string): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/exchange`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code, state }),
    })
    if (!response.ok) {
      throw new Error('Authentication failed')
    }
    return response.json()
  }

  static async refreshToken(token: string): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token }),
    })
    if (!response.ok) {
      throw new Error('Token refresh failed')
    }
    return response.json()
  }

  static async getCurrentUser(): Promise<User> {
    const response = await apiFetch('/auth/me')
    if (!response.ok) {
      throw new Error('Failed to get user info')
    }
    return response.json()
  }
}

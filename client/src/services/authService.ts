import { apiFetch } from '@/utils/api'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export interface User {
  id: number
  workos_id: string | null
  email: string | null
  role: 'user' | 'admin'
}

export class AuthService {
  static async getLoginUrl(): Promise<{ authorization_url: string }> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      credentials: 'include',
    })
    if (!response.ok) {
      throw new Error('Failed to get login URL')
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

  static async logout(): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/auth/logout`, {
      method: 'GET',
      credentials: 'include',
    })
    if (!response.ok) {
      throw new Error('Logout failed')
    }
    window.location.href = window.location.origin
  }
}

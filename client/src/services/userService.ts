import { apiFetch } from '@/utils/api'

export interface User {
  id: number
  workos_id: string | null
  email: string | null
  role: 'user' | 'admin'
  created_at: string
  updated_at: string
}

export interface UserListResponse {
  users: User[]
  total: number
  skip: number
  limit: number
}

export class UserService {
  static async getUsers(skip: number = 0, limit: number = 100): Promise<UserListResponse> {
    const response = await apiFetch(`/auth/users?skip=${skip}&limit=${limit}`)

    if (!response.ok) {
      throw new Error(`Failed to fetch users: ${response.statusText}`)
    }

    return response.json()
  }

  static async getUser(userId: number): Promise<User> {
    const response = await apiFetch(`/auth/users/${userId}`)

    if (!response.ok) {
      throw new Error(`Failed to fetch user: ${response.statusText}`)
    }

    return response.json()
  }

  static async createUser(email: string, role: 'user' | 'admin' = 'user'): Promise<User> {
    const response = await apiFetch('/auth/users', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, role }),
    })

    if (!response.ok) {
      throw new Error(`Failed to create user: ${response.statusText}`)
    }

    return response.json()
  }

  static async updateUser(userId: number, email?: string, role?: 'user' | 'admin'): Promise<User> {
    const response = await apiFetch(`/auth/users/${userId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, role }),
    })

    if (!response.ok) {
      throw new Error(`Failed to update user: ${response.statusText}`)
    }

    return response.json()
  }

  static async deleteUser(userId: number): Promise<void> {
    const response = await apiFetch(`/auth/users/${userId}`, {
      method: 'DELETE',
    })

    if (!response.ok) {
      throw new Error(`Failed to delete user: ${response.statusText}`)
    }
  }
}

import React, { createContext, useContext, useEffect, useState } from 'react'
import { AuthService } from '../services/authService'
import type { User } from '../services/authService'

interface AuthContextType {
  user: User | null
  login: (user: User) => void
  logout: () => void
  isAuthenticated: boolean
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: React.ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const currentUser = await AuthService.getCurrentUser()
        setUser(currentUser)
        localStorage.setItem('auth_user', JSON.stringify(currentUser))
      } catch (error) {
        setUser(null)
        localStorage.removeItem('auth_user')
        if (error instanceof Error && !error.message.includes('Unauthorized')) {
          console.error('Auth check error:', error)
        }
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [])

  const login = (newUser: User) => {
    setUser(newUser)
    localStorage.setItem('auth_user', JSON.stringify(newUser))
  }

  const logout = async () => {
    try {
      await AuthService.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setUser(null)
      localStorage.removeItem('auth_user')
    }
  }

  const isAuthenticated = !!user

  return (
    <AuthContext.Provider value={{
      user,
      login,
      logout,
      isAuthenticated,
      isLoading
    }}>
      {children}
    </AuthContext.Provider>
  )
}

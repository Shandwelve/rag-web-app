import React, { useState } from 'react'
import { Button } from './ui/button'
import { AuthService } from '../services/authService'
import { useAuth } from '../contexts/AuthContext'

export const LoginButton: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false)
  const { login } = useAuth()

  const handleLogin = async () => {
    setIsLoading(true)
    try {
      const { authorization_url } = await AuthService.getLoginUrl()
      window.location.href = authorization_url
    } catch (error) {
      console.error('Login failed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Button onClick={handleLogin} disabled={isLoading}>
      {isLoading ? 'Logging in...' : 'Login with WorkOS'}
    </Button>
  )
}
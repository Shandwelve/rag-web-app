import React, { useState } from 'react'
import { Button } from './ui/button'
import { AuthService } from '../services/authService'

interface LoginButtonProps {
  label?: string
  icon?: React.ReactNode
}

export const LoginButton: React.FC<LoginButtonProps> = ({ 
  label = 'Login or Sign up',
  icon 
}) => {
  const [isLoading, setIsLoading] = useState(false)

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
    <Button 
      onClick={handleLogin} 
      disabled={isLoading} 
      size="lg" 
      className="w-full px-8 flex items-center justify-center gap-2"
    >
      {icon && <span>{icon}</span>}
      {isLoading ? 'Logging in...' : label}
    </Button>
  )
}

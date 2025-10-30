import React, { useState } from 'react'
import { Button } from './ui/button'
import { AuthService } from '../services/authService'
import { useAuth } from '../contexts/AuthContext'

interface LoginButtonProps {
  provider?: string
  label?: string
  icon?: React.ReactNode
}

export const LoginButton: React.FC<LoginButtonProps> = ({ 
  provider = 'GoogleOAuth', 
  label,
  icon 
}) => {
  const [isLoading, setIsLoading] = useState(false)
  const { _login } = useAuth()

  const handleLogin = async () => {
    setIsLoading(true)
    try {
      const { authorization_url } = await AuthService.getLoginUrl(provider)
      window.location.href = authorization_url
    } catch (error) {
      console.error('Login failed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const buttonLabel = label || (provider === 'GoogleOAuth' ? 'Continue with Google' : 
                                provider === 'MicrosoftOAuth' ? 'Continue with Microsoft' :
                                provider === 'GitHubOAuth' ? 'Continue with GitHub' :
                                'Login or Sign up')

  return (
    <Button 
      onClick={handleLogin} 
      disabled={isLoading} 
      size="lg" 
      className="w-full px-8 flex items-center justify-center gap-2"
      variant={provider !== 'GoogleOAuth' ? 'outline' : 'default'}
    >
      {icon && <span>{icon}</span>}
      {isLoading ? 'Logging in...' : buttonLabel}
    </Button>
  )
}

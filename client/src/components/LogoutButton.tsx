import React from 'react'
import { Button } from './ui/button'
import { useAuth } from '../contexts/AuthContext'

export const LogoutButton: React.FC = () => {
  const { logout } = useAuth()

  return (
    <Button onClick={logout} variant="outline">
      Logout
    </Button>
  )
}
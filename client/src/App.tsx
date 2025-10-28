import React, { useEffect } from 'react'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { ProtectedRoute } from './components/ProtectedRoute'
import { LoginButton } from './components/LoginButton'
import { LogoutButton } from './components/LogoutButton'
import { FileUpload } from './components/FileUpload'
import { FileList } from './components/FileList'
import { AdminPanel } from './components/AdminPanel'
import { AuthService } from './services/authService'

const AppContent: React.FC = () => {
  const { isAuthenticated, user, login, isLoading } = useAuth()

  useEffect(() => {
    const handleAuthCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search)
      const code = urlParams.get('code')
      
      if (code && !isAuthenticated) {
        try {
          const tokenResponse = await AuthService.handleCallback(code)
          const userResponse = await AuthService.getCurrentUser(tokenResponse.access_token)
          login(tokenResponse.access_token, userResponse)
          
          window.history.replaceState({}, document.title, window.location.pathname)
        } catch (error) {
          console.error('Authentication callback failed:', error)
        }
      }
    }

    handleAuthCallback()
  }, [isAuthenticated, login])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen space-y-4">
        <h1 className="text-3xl font-bold">RAG Web Application</h1>
        <p className="text-gray-600">Please log in to access the application</p>
        <LoginButton />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-xl font-semibold">RAG Web Application</h1>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Welcome, {user?.email} ({user?.role})
              </span>
              <LogoutButton />
            </div>
          </div>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="space-y-8">
          {user?.role === 'admin' && (
            <ProtectedRoute requiredRole="admin">
              <AdminPanel />
            </ProtectedRoute>
          )}
          <ProtectedRoute>
            <FileUpload />
          </ProtectedRoute>
          <ProtectedRoute>
            <FileList />
          </ProtectedRoute>
        </div>
      </main>
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App

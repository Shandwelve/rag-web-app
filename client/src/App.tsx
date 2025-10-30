import React, { useEffect, useState } from 'react'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { ProtectedRoute } from './components/ProtectedRoute'
import { LoginButton } from './components/LoginButton'
import { LogoutButton } from './components/LogoutButton'
import { FileUpload } from './components/FileUpload'
import { FileList } from './components/FileList'
import { AdminPanel } from './components/AdminPanel'
import { RAGChat } from './components/RAGChat'
import { QuestionHistory } from './components/QuestionHistory'
import { RAGStats } from './components/RAGStats'
import { AuthService } from './services/authService'
import { FileService } from './services/fileService'
import { Home, FileText, MessageSquare, History, BarChart3, Users, Loader2, Lock } from 'lucide-react'
import { Button } from './components/ui/button'
import { Card } from './components/ui/card'

const AppContent: React.FC = () => {
  const { isAuthenticated, user, login, isLoading } = useAuth()
  const [activeTab, setActiveTab] = useState<'chat' | 'files' | 'history' | 'stats' | 'admin'>('chat')
  const [files, setFiles] = useState<any[]>([])
  const [filesLoading, setFilesLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [filesError, setFilesError] = useState<string | null>(null)
  const authCallbackProcessed = React.useRef(false)

  useEffect(() => {
    const handleAuthCallback = async () => {
      // Prevent duplicate processing
      if (authCallbackProcessed.current) {
        return
      }

      const urlParams = new URLSearchParams(window.location.search)
      const code = urlParams.get('code')
      const state = urlParams.get('state')
      const error = urlParams.get('error')
      const errorMessage = urlParams.get('message')
      
      // Handle error cases
      if (error) {
        authCallbackProcessed.current = true
        console.error('Authentication error:', error, errorMessage)
        setFilesError(errorMessage || `Authentication failed: ${error}`)
        window.history.replaceState({}, document.title, window.location.pathname)
        return
      }
      
      if (code && state && !isAuthenticated && !authCallbackProcessed.current) {
        authCallbackProcessed.current = true
        try {
          const tokenResponse = await AuthService.handleCallback(code, state)
          // Save token to localStorage immediately so apiFetch can use it
          localStorage.setItem('auth_token', tokenResponse.access_token)
          const userResponse = await AuthService.getCurrentUser()
          login(tokenResponse.access_token, userResponse)
          
          window.history.replaceState({}, document.title, window.location.pathname)
        } catch (error) {
          console.error('Authentication callback failed:', error)
          setFilesError('Authentication failed')
          authCallbackProcessed.current = false // Allow retry on error
        }
      }
    }

    handleAuthCallback()
  }, [isAuthenticated, login])

  useEffect(() => {
    if (isAuthenticated && user?.role === 'user' && activeTab !== 'chat') {
      setActiveTab('chat')
    }
  }, [isAuthenticated, user, activeTab])

  useEffect(() => {
    if (isAuthenticated && activeTab === 'files') {
      loadFiles()
    }
  }, [isAuthenticated, activeTab])

  const loadFiles = async () => {
    setFilesLoading(true)
    setFilesError(null)
    try {
      const loadedFiles = await FileService.getFiles()
      setFiles(loadedFiles)
    } catch (error) {
      console.error('Error loading files:', error)
      setFilesError('Failed to load files')
    } finally {
      setFilesLoading(false)
    }
  }

  const handleFileUpload = async (file: File) => {
    setUploading(true)
    setFilesError(null)
    try {
      await FileService.uploadFile(file)
      await loadFiles()
    } catch (error) {
      console.error('Error uploading file:', error)
      setFilesError('Failed to upload file')
    } finally {
      setUploading(false)
    }
  }

  const handleFileDelete = async (fileId: number) => {
    try {
      await FileService.deleteFile(fileId)
      await loadFiles()
    } catch (error) {
      console.error('Error deleting file:', error)
      setFilesError('Failed to delete file')
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-gradient-to-br from-gray-50 to-white">
        <Card className="p-10 max-w-lg w-full shadow-lg border-0">
          {/* Icon in?gradient container */}
          <div className="flex justify-center mb-6">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-gray-300 to-white flex items-center justify-center shadow-md">
              <Lock className="h-10 w-10 text-gray-700" />
            </div>
          </div>
          
          {/* Welcome text */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold mb-3 text-gray-900">Welcome</h1>
            <p className="text-lg text-muted-foreground">
              Sign in to your account to access the RAG Web Application
            </p>
          </div>
          
          {/* Login buttons */}
          <div className="space-y-3">
            <LoginButton provider="GoogleOAuth" />
            <LoginButton provider="MicrosoftOAuth" />
            <LoginButton provider="GitHubOAuth" />
          </div>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-xl font-semibold flex items-center gap-2">
              <Home className="h-5 w-5" />
              RAG Web Application
            </h1>
            <div className="flex items-center gap-4">
              <span className="text-sm text-muted-foreground">
                {user?.email} ({user?.role})
              </span>
              <LogoutButton />
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex gap-6">
          <aside className="w-64 shrink-0">
            <Card className="p-4">
              <nav className="space-y-2">
                <Button
                  variant={activeTab === 'chat' ? 'default' : 'ghost'}
                  className="w-full justify-start"
                  onClick={() => setActiveTab('chat')}
                >
                  <MessageSquare className="mr-2 h-4 w-4" />
                  Chat
                </Button>
                {user?.role === 'admin' && (
                  <>
                    <Button
                      variant={activeTab === 'files' ? 'default' : 'ghost'}
                      className="w-full justify-start"
                      onClick={() => setActiveTab('files')}
                    >
                      <FileText className="mr-2 h-4 w-4" />
                      Files
                    </Button>
                    <Button
                      variant={activeTab === 'history' ? 'default' : 'ghost'}
                      className="w-full justify-start"
                      onClick={() => setActiveTab('history')}
                    >
                      <History className="mr-2 h-4 w-4" />
                      History
                    </Button>
                    <Button
                      variant={activeTab === 'stats' ? 'default' : 'ghost'}
                      className="w-full justify-start"
                      onClick={() => setActiveTab('stats')}
                    >
                      <BarChart3 className="mr-2 h-4 w-4" />
                      Statistics
                    </Button>
                    <Button
                      variant={activeTab === 'admin' ? 'default' : 'ghost'}
                      className="w-full justify-start"
                      onClick={() => setActiveTab('admin')}
                    >
                      <Users className="mr-2 h-4 w-4" />
                      Admin
                    </Button>
                  </>
                )}
              </nav>
            </Card>
          </aside>

          <main className="flex-1">
            {filesError && (
              <Card className="p-4 mb-4 border-destructive bg-destructive/10">
                <p className="text-sm text-destructive">{filesError}</p>
              </Card>
            )}

            {activeTab === 'chat' && (
              <ProtectedRoute>
                <RAGChat />
              </ProtectedRoute>
            )}

            {activeTab === 'files' && user?.role === 'admin' && (
              <ProtectedRoute requiredRole="admin">
                <div className="space-y-6">
                  <Card>
                    <div className="p-6">
                      <h2 className="text-2xl font-semibold mb-4">Upload Files</h2>
                      <FileUpload onFileUpload={handleFileUpload} isUploading={uploading} />
                    </div>
                  </Card>
                  <Card>
                    <div className="p-6">
                      <h2 className="text-2xl font-semibold mb-4">Your Files</h2>
                      {filesLoading ? (
                        <div className="flex items-center justify-center py-8">
                          <Loader2 className="h-6 w-6 animate-spin" />
                        </div>
                      ) : (
                        <FileList
                          files={files}
                          onDeleteFile={handleFileDelete}
                          isDeleting={filesLoading}
                        />
                      )}
                    </div>
                  </Card>
                </div>
              </ProtectedRoute>
            )}

            {activeTab === 'history' && user?.role === 'admin' && (
              <ProtectedRoute requiredRole="admin">
                <QuestionHistory />
              </ProtectedRoute>
            )}

            {activeTab === 'stats' && user?.role === 'admin' && (
              <ProtectedRoute requiredRole="admin">
                <RAGStats />
              </ProtectedRoute>
            )}

            {activeTab === 'admin' && user?.role === 'admin' && (
              <ProtectedRoute requiredRole="admin">
                <AdminPanel />
              </ProtectedRoute>
            )}
          </main>
        </div>
      </div>
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

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * Handles 401 Unauthorized responses by clearing auth and redirecting to login
 */
const handleUnauthorized = () => {
  // Clear auth data from localStorage
  localStorage.removeItem('auth_token')
  localStorage.removeItem('auth_user')
  
  // Reload the page which will show the login screen
  window.location.href = window.location.origin
}

/**
 * Wrapper around fetch that handles 401 responses
 */
export async function apiFetch(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = localStorage.getItem('auth_token')
  
  // Add auth headers if token exists
  const headers: HeadersInit = {
    ...options.headers,
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
  }

  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers,
  })

  // Handle 401 Unauthorized
  if (response.status === 401) {
    handleUnauthorized()
    throw new Error('Unauthorized - Please sign in again')
  }

  return response
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * Handles 401 Unauthorized responses by clearing auth and redirecting to login
 */
const handleUnauthorized = () => {
  // Clear auth data from localStorage (if any)
  localStorage.removeItem('auth_user')
  
  // Only redirect if we're not already on the home page
  // This prevents redirect loops
  if (window.location.pathname !== '/' && !window.location.pathname.includes('/auth/')) {
    window.location.href = window.location.origin
  }
}

/**
 * Wrapper around fetch that handles 401 responses
 * Cookies are automatically included via credentials: 'include'
 */
export async function apiFetch(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    credentials: 'include', // Include cookies in requests
    headers: {
      ...options.headers,
    },
  })

  // Handle 401 Unauthorized
  if (response.status === 401) {
    handleUnauthorized()
    throw new Error('Unauthorized - Please sign in again')
  }

  return response
}

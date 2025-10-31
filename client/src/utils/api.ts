const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const handleUnauthorized = () => {
  localStorage.removeItem('auth_user')
  
  if (window.location.pathname !== '/' && !window.location.pathname.includes('/auth/')) {
    window.location.href = window.location.origin
  }
}

export async function apiFetch(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    credentials: 'include',
    headers: {
      ...options.headers,
    },
  })

  if (response.status === 401) {
    handleUnauthorized()
    throw new Error('Unauthorized - Please sign in again')
  }

  return response
}

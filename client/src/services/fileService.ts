const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"

export interface FileItem {
  id: number
  filename: string
  original_filename: string
  file_size: number
  file_type: string
  status: string
  created_at: string
  error_message?: string
}

const getAuthHeaders = (): HeadersInit => {
  const token = localStorage.getItem('auth_token')
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

export class FileService {
  static async uploadFile(file: File): Promise<FileItem> {
    const formData = new FormData()
    formData.append("file", file)

    const response = await fetch(`${API_BASE_URL}/files/upload`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`)
    }

    return response.json()
  }

  static async getFiles(): Promise<FileItem[]> {
    const response = await fetch(`${API_BASE_URL}/files/`, {
      headers: getAuthHeaders(),
    })

    if (!response.ok) {
      throw new Error(`Failed to fetch files: ${response.statusText}`)
    }

    return response.json()
  }

  static async getFile(fileId: number): Promise<FileItem> {
    const response = await fetch(`${API_BASE_URL}/files/${fileId}`, {
      headers: getAuthHeaders(),
    })

    if (!response.ok) {
      throw new Error(`Failed to fetch file: ${response.statusText}`)
    }

    return response.json()
  }

  static async deleteFile(fileId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/files/${fileId}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    })

    if (!response.ok) {
      throw new Error(`Failed to delete file: ${response.statusText}`)
    }
  }
}
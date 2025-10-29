import { apiFetch } from '@/utils/api'

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

export class FileService {
  static async uploadFile(file: File): Promise<FileItem> {
    const formData = new FormData()
    formData.append("file", file)

    const response = await apiFetch('/files/upload', {
      method: "POST",
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`)
    }

    return response.json()
  }

  static async getFiles(): Promise<FileItem[]> {
    const response = await apiFetch('/files/')

    if (!response.ok) {
      throw new Error(`Failed to fetch files: ${response.statusText}`)
    }

    return response.json()
  }

  static async getFile(fileId: number): Promise<FileItem> {
    const response = await apiFetch(`/files/${fileId}`)

    if (!response.ok) {
      throw new Error(`Failed to fetch file: ${response.statusText}`)
    }

    return response.json()
  }

  static async deleteFile(fileId: number): Promise<void> {
    const response = await apiFetch(`/files/${fileId}`, {
      method: "DELETE",
    })

    if (!response.ok) {
      throw new Error(`Failed to delete file: ${response.statusText}`)
    }
  }
}
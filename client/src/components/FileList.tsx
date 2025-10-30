import { useState } from "react"
import { File, Download, Trash2, CheckCircle, AlertCircle, Clock } from "lucide-react"
import { Button } from "@/components/ui/button"

interface FileItem {
  id: number
  filename: string
  original_filename: string
  file_size: number
  file_type: string
  status: string
  created_at: string
  error_message?: string
}

interface FileListProps {
  files: FileItem[]
  onDeleteFile: (fileId: number) => Promise<void>
  isDeleting?: boolean
}

export function FileList({ files, onDeleteFile, isDeleting = false }: FileListProps) {
  const [deletingFiles, setDeletingFiles] = useState<Set<number>>(new Set())

  const handleDelete = async (fileId: number) => {
    setDeletingFiles(prev => new Set(prev).add(fileId))
    try {
      await onDeleteFile(fileId)
    } catch (error) {
      console.error("Delete failed:", error)
    } finally {
      setDeletingFiles(prev => {
        const newSet = new Set(prev)
        newSet.delete(fileId)
        return newSet
      })
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "uploading":
        return <Clock className="h-4 w-4 text-yellow-600" />
      case "processing":
        return <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600" />
      case "ready":
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case "error":
        return <AlertCircle className="h-4 w-4 text-red-600" />
      default:
        return <File className="h-4 w-4 text-gray-600" />
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case "uploading":
        return "Uploading..."
      case "processing":
        return "Processing..."
      case "ready":
        return "Ready"
      case "error":
        return "Error"
      default:
        return status
    }
  }

  if (files.length === 0) {
    return (
      <div className="text-center py-8">
        <File className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-gray-500">No files uploaded yet</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {files.map((file) => (
        <div
          key={file.id}
          className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg shadow-sm"
        >
          <div className="flex items-center space-x-4">
            {getStatusIcon(file.status)}
            <div>
              <p className="font-medium text-gray-900">{file.original_filename}</p>
              <div className="flex items-center space-x-4 text-sm text-gray-500">
                <span>{formatFileSize(file.file_size)}</span>
                <span>•</span>
                <span className="capitalize">{file.file_type}</span>
                <span>•</span>
                <span>{formatDate(file.created_at)}</span>
                <span>•</span>
                <span className={`font-medium ${
                  file.status === "ready" ? "text-green-600" :
                  file.status === "error" ? "text-red-600" :
                  "text-yellow-600"
                }`}>
                  {getStatusText(file.status)}
                </span>
              </div>
              {file.error_message && (
                <p className="text-sm text-red-600 mt-1">{file.error_message}</p>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {file.status === "ready" && (
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleDelete(file.id)}
              disabled={deletingFiles.has(file.id) || isDeleting}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              {deletingFiles.has(file.id) ? "Deleting..." : "Delete"}
            </Button>
          </div>
        </div>
      ))}
    </div>
  )
}
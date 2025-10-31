import { useCallback, useState } from "react"
import { useDropzone } from "react-dropzone"
import { Upload, File, X, CheckCircle, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"

interface FileUploadProps {
  onFileUpload: (file: File) => Promise<void>
  isUploading?: boolean
}

interface UploadedFile {
  id: number
  filename: string
  file_size: number
  file_type: string
  status: string
  created_at: string
}

export function FileUpload({ onFileUpload, isUploading = false }: FileUploadProps) {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return
    
    const file = acceptedFiles[0]
    const fileId = Date.now()
    const newFile: UploadedFile = {
      id: fileId,
      filename: file.name,
      file_size: file.size,
      file_type: file.type,
      status: "uploading",
      created_at: new Date().toISOString(),
    }
    setUploadedFiles([newFile])
    
    try {
      await onFileUpload(file)
      setUploadedFiles(prev => prev.map(f =>
        f.id === fileId ? { ...f, status: "ready" } : f
      ))
    } catch (error) {
      console.error("Upload failed:", error)
      setUploadedFiles(prev => prev.map(f =>
        f.id === fileId ? { ...f, status: "error" } : f
      ))
    }
  }, [onFileUpload])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "text/plain": [".txt"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "text/markdown": [".md"],
    },
    maxFiles: 10,
    disabled: isUploading,
  })

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "uploading":
        return <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600" />
      case "ready":
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case "error":
        return <AlertCircle className="h-4 w-4 text-red-600" />
      default:
        return <File className="h-4 w-4 text-gray-600" />
    }
  }

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? "border-blue-500 bg-blue-50"
            : "border-gray-300 hover:border-gray-400"
        } ${isUploading ? "opacity-50 cursor-not-allowed" : ""}`}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-lg font-medium text-gray-700 mb-2">
          {isDragActive ? "Drop file here" : "Drag & drop file here, or click to select"}
        </p>
        <p className="text-sm text-gray-500">
          Supports PDF and DOCX files (single file upload)
        </p>
      </div>

      {uploadedFiles.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Uploaded File</h3>
          <div className="space-y-2">
            {uploadedFiles.map((file) => (
              <div
                key={file.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  {getStatusIcon(file.status)}
                  <div>
                    <p className="font-medium text-gray-900">{file.filename}</p>
                    <p className="text-sm text-gray-500">
                      {formatFileSize(file.file_size)}
                    </p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() =>
                    setUploadedFiles(prev => prev.filter(f => f.id !== file.id))
                  }
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

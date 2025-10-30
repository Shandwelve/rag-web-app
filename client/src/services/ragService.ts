import { apiFetch } from '@/utils/api'

export interface SourceReference {
  file_id: number
  filename: string
  page_number: number | null
  chunk_index: number
  relevance_score: number
}

export interface ImageReference {
  image_path: string
  description: string | null
  page_number: number | null
  file_id: number
}

export interface AnswerResponse {
  answer: string
  sources: SourceReference[]
  images: ImageReference[]
  confidence_score: number
  question_id: number
}

export interface QuestionResponse {
  id: number
  question_text: string
  user_id: number
  session_id: string | null
  context_files: string | null
  created_at: string
  updated_at: string
}

export interface QAResponse {
  id: number
  answer_text: string
  question_id: number
  confidence_score: number
  sources_used: string | null
  images_used: string | null
  processing_time_ms: string | null
  created_at: string
  updated_at: string
}

export interface QAPairResponse {
  question: QuestionResponse
  answer: QAResponse
  images: ImageReference[]
}

export interface QuestionStats {
  total_questions: number
  total_answers: number
  avg_confidence: number
}

export class RAGService {
  static async askQuestion(question: string, sessionId?: string): Promise<AnswerResponse> {
    const response = await apiFetch('/rag/ask', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        session_id: sessionId,
      }),
    })

    if (!response.ok) {
      throw new Error(`Failed to ask question: ${response.statusText}`)
    }

    return response.json()
  }

  static async askVoiceQuestion(audioFile: File, sessionId?: string): Promise<AnswerResponse> {
    const formData = new FormData()
    formData.append('audio_file', audioFile)
    if (sessionId) {
      formData.append('session_id', sessionId)
    }

    const response = await apiFetch('/rag/ask-voice', {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`Failed to process voice question: ${response.statusText}`)
    }

    return response.json()
  }

  static async getQuestionHistory(limit: number = 50): Promise<QAPairResponse[]> {
    const response = await apiFetch(`/rag/history?limit=${limit}`)

    if (!response.ok) {
      throw new Error(`Failed to fetch history: ${response.statusText}`)
    }

    return response.json()
  }

  static async getSessionHistory(sessionId: string): Promise<QAPairResponse[]> {
    const response = await apiFetch(`/rag/session/${sessionId}`)

    if (!response.ok) {
      throw new Error(`Failed to fetch session history: ${response.statusText}`)
    }

    return response.json()
  }

  static async deleteQuestion(questionId: number): Promise<void> {
    const response = await apiFetch(`/rag/question/${questionId}`, {
      method: 'DELETE',
    })

    if (!response.ok) {
      throw new Error(`Failed to delete question: ${response.statusText}`)
    }
  }

  static async getStats(): Promise<QuestionStats> {
    const response = await apiFetch('/rag/stats')

    if (!response.ok) {
      throw new Error(`Failed to fetch stats: ${response.statusText}`)
    }

    return response.json()
  }
}

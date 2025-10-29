import { useState } from 'react'
import { Send, Mic, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { RAGService, type AnswerResponse, type ImageReference } from '@/services/ragService'
import { cn } from '@/lib/utils'

interface Message {
  question: string
  answer: string
  sources: Array<{
    file_id: number
    filename: string
    page_number: number | null
    chunk_index: number
    relevance_score: number
  }>
  images: ImageReference[]
  confidence_score: number
  timestamp: Date
  questionId?: number
}

export function RAGChat() {
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId] = useState(() => `session-${Date.now()}`)
  const [isRecording, setIsRecording] = useState(false)
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null)

  const handleAskQuestion = async () => {
    if (!question.trim() || isLoading) return

    const userQuestion = question.trim()
    setQuestion('')
    setIsLoading(true)

    const tempMessage: Message = {
      question: userQuestion,
      answer: '',
      sources: [],
      images: [],
      confidence_score: 0,
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, tempMessage])

    try {
      const response: AnswerResponse = await RAGService.askQuestion(userQuestion, sessionId)
      
      setMessages(prev => {
        const updated = [...prev]
        const lastIndex = updated.length - 1
        if (lastIndex >= 0) {
          updated[lastIndex] = {
            ...updated[lastIndex],
            answer: response.answer,
            sources: response.sources,
            images: response.images,
            confidence_score: response.confidence_score,
            questionId: response.question_id,
          }
        }
        return updated
      })
    } catch (error) {
      console.error('Error asking question:', error)
      setMessages(prev => {
        const updated = [...prev]
        const lastIndex = updated.length - 1
        if (lastIndex >= 0) {
          updated[lastIndex] = {
            ...updated[lastIndex],
            answer: 'Sorry, an error occurred while processing your question.',
          }
        }
        return updated
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleVoiceQuestion = async () => {
    if (isRecording) {
      mediaRecorder?.stop()
      setIsRecording(false)
      return
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
      const audioChunks: Blob[] = []

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data)
        }
      }

      recorder.onstop = async () => {
        stream.getTracks().forEach(track => track.stop())
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' })
        const audioFile = new File([audioBlob], 'voice-question.webm', { type: 'audio/webm' })

        setIsLoading(true)
        try {
          const response: AnswerResponse = await RAGService.askVoiceQuestion(audioFile, sessionId)
          
          setMessages(prev => [...prev, {
            question: '[Voice Question]',
            answer: response.answer,
            sources: response.sources,
            images: response.images,
            confidence_score: response.confidence_score,
            timestamp: new Date(),
            questionId: response.question_id,
          }])
        } catch (error) {
          console.error('Error processing voice question:', error)
          setMessages(prev => [...prev, {
            question: '[Voice Question]',
            answer: 'Sorry, an error occurred while processing your voice question.',
            sources: [],
            images: [],
            confidence_score: 0,
            timestamp: new Date(),
          }])
        } finally {
          setIsLoading(false)
        }
      }

      recorder.start()
      setMediaRecorder(recorder)
      setIsRecording(true)
    } catch (error) {
      console.error('Error accessing microphone:', error)
      alert('Failed to access microphone. Please grant permission.')
    }
  }

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle>Ask Questions</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col gap-4">
        <ScrollArea className="flex-1 pr-4">
          <div className="space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-muted-foreground py-8">
                Ask a question to get started
              </div>
            )}
            {messages.map((message, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-start gap-2">
                  <Badge variant="outline" className="mt-1">You</Badge>
                  <div className="flex-1 bg-muted rounded-lg p-3">
                    <p className="text-sm">{message.question}</p>
                  </div>
                </div>
                {message.answer && (
                  <div className="flex items-start gap-2">
                    <Badge variant="default" className="mt-1">AI</Badge>
                    <div className="flex-1 space-y-2">
                      <div className="bg-card border rounded-lg p-3">
                        <p className="text-sm whitespace-pre-wrap">{message.answer}</p>
                      </div>
                      {message.images.length > 0 && (
                        <div className="space-y-2">
                          <p className="text-xs text-muted-foreground font-medium">Images:</p>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                            {message.images.map((image, idx) => (
                              <div key={idx} className="relative rounded-lg overflow-hidden border">
                                <img
                                  src={image.image_path}
                                  alt={image.description || `Image ${idx + 1}`}
                                  className="w-full h-auto object-contain max-h-64"
                                />
                                {image.description && (
                                  <div className="absolute bottom-0 left-0 right-0 bg-black/60 text-white text-xs p-2">
                                    {image.description}
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      {message.sources.length > 0 && (
                        <div className="space-y-1">
                          <p className="text-xs text-muted-foreground font-medium">Sources:</p>
                          {message.sources.map((source, idx) => (
                            <div key={idx} className="text-xs text-muted-foreground bg-muted rounded px-2 py-1">
                              {source.filename}
                              {source.page_number && ` (page ${source.page_number})`}
                              <span className="ml-2">Score: {source.relevance_score.toFixed(2)}</span>
                            </div>
                          ))}
                        </div>
                      )}
                      <div className="text-xs text-muted-foreground">
                        Confidence: {(message.confidence_score * 100).toFixed(1)}%
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
            {isLoading && messages.length > 0 && messages[messages.length - 1]?.answer === '' && (
              <div className="flex items-center gap-2 text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm">Thinking...</span>
              </div>
            )}
          </div>
        </ScrollArea>
        <div className="space-y-2">
          <div className="flex gap-2">
            <Textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleAskQuestion()
                }
              }}
              placeholder="Ask a question about your documents..."
              className="min-h-[80px] resize-none"
              disabled={isLoading}
            />
            <Button
              onClick={handleVoiceQuestion}
              variant={isRecording ? "destructive" : "outline"}
              size="icon"
              className="h-[80px]"
              disabled={isLoading}
            >
              <Mic className={cn("h-5 w-5", isRecording && "animate-pulse")} />
            </Button>
          </div>
          <Button
            onClick={handleAskQuestion}
            disabled={!question.trim() || isLoading}
            className="w-full"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Send className="mr-2 h-4 w-4" />
                Send
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

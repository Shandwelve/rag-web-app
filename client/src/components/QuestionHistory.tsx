import { useState, useEffect, useRef } from 'react'
import { History, Trash2, Loader2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Skeleton } from '@/components/ui/skeleton'
import { RAGService, type QAPairResponse } from '@/services/ragService'

export function QuestionHistory() {
  const [history, setHistory] = useState<QAPairResponse[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [deletingIds, setDeletingIds] = useState<Set<number>>(new Set())
  const fetchInProgress = useRef(false)

  const fetchHistory = async () => {
    setIsLoading(true)
    try {
      const data = await RAGService.getQuestionHistory(50)
      setHistory(data)
    } catch (error) {
      console.error('Error fetching history:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (fetchInProgress.current) return
    
    fetchInProgress.current = true
    
    const loadHistory = async () => {
      setIsLoading(true)
      try {
        const data = await RAGService.getQuestionHistory(50)
        setHistory(data)
      } catch (error) {
        console.error('Error fetching history:', error)
      } finally {
        setIsLoading(false)
        fetchInProgress.current = false
      }
    }

    loadHistory()
  }, [])

  const handleDelete = async (questionId: number) => {
    setDeletingIds(prev => new Set(prev).add(questionId))
    try {
      await RAGService.deleteQuestion(questionId)
      setHistory(prev => prev.filter(item => item.question.id !== questionId))
    } catch (error) {
      console.error('Error deleting question:', error)
    } finally {
      setDeletingIds(prev => {
        const newSet = new Set(prev)
        newSet.delete(questionId)
        return newSet
      })
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <History className="h-5 w-5" />
              Question History
            </CardTitle>
            <CardDescription>View your previous questions and answers</CardDescription>
          </div>
          <Button variant="outline" size="sm" onClick={fetchHistory} disabled={isLoading}>
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px]">
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="space-y-2">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-2/3" />
                </div>
              ))}
            </div>
          ) : history.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              No history yet
            </div>
          ) : (
            <div className="space-y-4">
              {history.map((qaPair) => (
                <div key={qaPair.question.id} className="border rounded-lg p-4 space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="outline">Question</Badge>
                        <span className="text-xs text-muted-foreground">
                          {formatDate(qaPair.question.created_at)}
                        </span>
                      </div>
                      <p className="text-sm mb-3">{qaPair.question.question_text}</p>
                      <div className="flex items-center gap-2 mb-2">
                        <Badge>Answer</Badge>
                        <span className="text-xs text-muted-foreground">
                          Confidence: {(qaPair.answer.confidence_score * 100).toFixed(1)}%
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                        {qaPair.answer.answer_text}
                      </p>
                      {qaPair.images && qaPair.images.length > 0 && (
                        <div className="mt-3 space-y-2">
                          <p className="text-xs text-muted-foreground font-medium">Images:</p>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                            {qaPair.images.map((image, idx) => (
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
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(qaPair.question.id)}
                      disabled={deletingIds.has(qaPair.question.id)}
                    >
                      {deletingIds.has(qaPair.question.id) ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Trash2 className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  )
}

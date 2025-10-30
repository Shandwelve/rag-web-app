import { useState, useEffect } from 'react'
import { BarChart3 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { RAGService, type QuestionStats } from '@/services/ragService'

let statsFetchPromise: Promise<void> | null = null

export function RAGStats() {
  const [stats, setStats] = useState<QuestionStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (statsFetchPromise) return
    
    const abortController = new AbortController()
    
    statsFetchPromise = (async () => {
      setIsLoading(true)
      try {
        const data = await RAGService.getStats()
        if (!abortController.signal.aborted) {
          setStats(data)
        }
      } catch (error) {
        if (!abortController.signal.aborted) {
          console.error('Error fetching stats:', error)
        }
      } finally {
        if (!abortController.signal.aborted) {
          setIsLoading(false)
        }
        statsFetchPromise = null
      }
    })()

    return () => {
      abortController.abort()
    }
  }, [])

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          Statistics
        </CardTitle>
        <CardDescription>Your RAG usage statistics</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-4">
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
          </div>
        ) : stats ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
              <span className="text-sm font-medium">Total Questions</span>
              <span className="text-2xl font-bold">{stats.total_questions}</span>
            </div>
            <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
              <span className="text-sm font-medium">Total Answers</span>
              <span className="text-2xl font-bold">{stats.total_answers}</span>
            </div>
            <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
              <span className="text-sm font-medium">Average Confidence</span>
              <span className="text-2xl font-bold">
                {(stats.avg_confidence * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        ) : (
          <div className="text-center text-muted-foreground py-8">
            No statistics available
          </div>
        )}
      </CardContent>
    </Card>
  )
}

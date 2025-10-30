import { useState, useEffect, useRef } from 'react'
import { BarChart3 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { RAGService, type QuestionStats } from '@/services/ragService'

export function RAGStats() {
  const [stats, setStats] = useState<QuestionStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const fetchInProgress = useRef(false)

  useEffect(() => {
    if (fetchInProgress.current) return
    
    fetchInProgress.current = true
    
    const fetchStats = async () => {
      setIsLoading(true)
      try {
        const data = await RAGService.getStats()
        setStats(data)
      } catch (error) {
        console.error('Error fetching stats:', error)
      } finally {
        setIsLoading(false)
        fetchInProgress.current = false
      }
    }

    fetchStats()
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
                {stats.avg_confidence != null && !isNaN(stats.avg_confidence)
                  ? `${(stats.avg_confidence * 100).toFixed(1)}%`
                  : '0%'}
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

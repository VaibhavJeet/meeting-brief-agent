'use client'

import { useQuery, useMutation } from '@tanstack/react-query'
import { useParams, useRouter } from 'next/navigation'
import { ArrowLeft, Download, Trash2, Loader2, AlertTriangle, Sparkles, CheckCircle } from 'lucide-react'
import { api } from '@/lib/api'
import { format } from 'date-fns'
import Link from 'next/link'
import ReactMarkdown from 'react-markdown'

export default function BriefDetailPage() {
  const params = useParams()
  const router = useRouter()
  const briefId = params.id as string

  const { data: brief, isLoading } = useQuery({
    queryKey: ['brief', briefId],
    queryFn: () => api.getBrief(briefId),
  })

  const deleteMutation = useMutation({
    mutationFn: () => api.deleteBrief(briefId),
    onSuccess: () => router.push('/briefs'),
  })

  const exportMutation = useMutation({
    mutationFn: () => api.exportBrief(briefId, 'markdown'),
    onSuccess: (data) => {
      const blob = new Blob([data.content], { type: 'text/markdown' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${brief?.title || 'brief'}.md`
      a.click()
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (!brief) {
    return (
      <div className="p-8 text-center">
        <p className="text-muted-foreground">Brief not found</p>
      </div>
    )
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <Link
          href="/briefs"
          className="flex items-center gap-2 text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-5 w-5" />
          Back to Briefs
        </Link>
        <div className="flex items-center gap-2">
          <button
            onClick={() => exportMutation.mutate()}
            disabled={exportMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 border rounded-lg hover:bg-secondary"
          >
            <Download className="h-4 w-4" />
            Export
          </button>
          <button
            onClick={() => deleteMutation.mutate()}
            disabled={deleteMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 border border-destructive text-destructive rounded-lg hover:bg-destructive hover:text-destructive-foreground"
          >
            <Trash2 className="h-4 w-4" />
            Delete
          </button>
        </div>
      </div>

      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold mb-2">{brief.title}</h1>
          <p className="text-muted-foreground">
            Generated {format(new Date(brief.generated_at), 'MMMM d, yyyy h:mm a')}
          </p>
          {brief.data_sources_used?.length > 0 && (
            <div className="flex gap-2 mt-2">
              {brief.data_sources_used.map((source: string) => (
                <span key={source} className="text-xs bg-secondary px-2 py-1 rounded">
                  {source}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Executive Summary */}
        <section className="bg-card border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Executive Summary</h2>
          <p className="text-muted-foreground leading-relaxed">
            {brief.executive_summary}
          </p>
          {brief.meeting_objective && (
            <div className="mt-4 p-4 bg-secondary/50 rounded-lg">
              <p className="text-sm font-medium">Meeting Objective</p>
              <p className="text-muted-foreground">{brief.meeting_objective}</p>
            </div>
          )}
        </section>

        {/* Participants */}
        {brief.participant_profiles?.length > 0 && (
          <section className="bg-card border rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Participants</h2>
            <div className="grid gap-4">
              {brief.participant_profiles.map((p: any, i: number) => (
                <div key={i} className="p-4 bg-secondary/50 rounded-lg">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-medium">{p.name || p.email}</p>
                      {p.title && <p className="text-sm text-muted-foreground">{p.title}</p>}
                      {p.company && <p className="text-sm text-muted-foreground">{p.company}</p>}
                    </div>
                    {p.sentiment && (
                      <span className={`text-xs px-2 py-1 rounded ${
                        p.sentiment === 'positive' ? 'bg-green-100 text-green-700' :
                        p.sentiment === 'negative' ? 'bg-red-100 text-red-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {p.sentiment}
                      </span>
                    )}
                  </div>
                  {p.key_topics?.length > 0 && (
                    <div className="flex gap-2 mt-2 flex-wrap">
                      {p.key_topics.map((topic: string, j: number) => (
                        <span key={j} className="text-xs bg-background px-2 py-1 rounded">
                          {topic}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Talking Points */}
        {brief.talking_points?.length > 0 && (
          <section className="bg-card border rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Talking Points</h2>
            <div className="space-y-3">
              {brief.talking_points.map((tp: any, i: number) => (
                <div key={i} className="flex gap-3">
                  <span className={`h-6 w-6 rounded-full flex items-center justify-center text-xs font-bold ${
                    tp.priority === 'high' ? 'bg-red-100 text-red-700' :
                    tp.priority === 'low' ? 'bg-gray-100 text-gray-700' :
                    'bg-blue-100 text-blue-700'
                  }`}>
                    {i + 1}
                  </span>
                  <div>
                    <p className="font-medium">{tp.topic}</p>
                    <p className="text-sm text-muted-foreground">{tp.context}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Action Items */}
        {brief.open_action_items?.length > 0 && (
          <section className="bg-card border rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Open Action Items</h2>
            <div className="space-y-2">
              {brief.open_action_items.map((ai: any, i: number) => (
                <div key={i} className="flex items-start gap-3 p-3 bg-secondary/50 rounded-lg">
                  <CheckCircle className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p>{ai.description}</p>
                    {ai.assignee && (
                      <p className="text-sm text-muted-foreground">Assigned to: {ai.assignee}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Risks & Opportunities */}
        {brief.risks_opportunities?.length > 0 && (
          <section className="bg-card border rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Risks & Opportunities</h2>
            <div className="grid gap-4 md:grid-cols-2">
              {brief.risks_opportunities.map((ro: any, i: number) => (
                <div
                  key={i}
                  className={`p-4 rounded-lg border ${
                    ro.type === 'risk'
                      ? 'border-orange-200 bg-orange-50'
                      : 'border-green-200 bg-green-50'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    {ro.type === 'risk' ? (
                      <AlertTriangle className="h-4 w-4 text-orange-600" />
                    ) : (
                      <Sparkles className="h-4 w-4 text-green-600" />
                    )}
                    <span className={`text-sm font-medium ${
                      ro.type === 'risk' ? 'text-orange-700' : 'text-green-700'
                    }`}>
                      {ro.type === 'risk' ? 'Risk' : 'Opportunity'}
                    </span>
                  </div>
                  <p className="font-medium">{ro.title}</p>
                  <p className="text-sm text-muted-foreground mt-1">{ro.description}</p>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  )
}

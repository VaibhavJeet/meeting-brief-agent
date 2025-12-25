'use client'

import { useQuery } from '@tanstack/react-query'
import { FileText, Loader2 } from 'lucide-react'
import { api } from '@/lib/api'
import { format } from 'date-fns'
import Link from 'next/link'

export default function BriefsPage() {
  const { data: briefs, isLoading } = useQuery({
    queryKey: ['briefs'],
    queryFn: () => api.getBriefs(),
  })

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Briefs</h1>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : briefs?.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground">No briefs generated yet</p>
          <Link
            href="/meetings"
            className="text-primary hover:underline mt-2 inline-block"
          >
            Go to Meetings to generate briefs
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {briefs?.map((brief: any) => (
            <Link
              key={brief.id}
              href={`/briefs/${brief.id}`}
              className="bg-card border rounded-lg p-6 hover:border-primary transition-colors"
            >
              <h3 className="font-semibold mb-2 line-clamp-1">{brief.title}</h3>
              <p className="text-sm text-muted-foreground line-clamp-3 mb-4">
                {brief.executive_summary}
              </p>
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>
                  {format(new Date(brief.generated_at), 'MMM d, yyyy')}
                </span>
                <span>
                  {brief.data_sources_used?.length || 0} sources
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

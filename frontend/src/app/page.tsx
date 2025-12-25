'use client'

import { useQuery } from '@tanstack/react-query'
import { Calendar, FileText, Users, Clock } from 'lucide-react'
import { api } from '@/lib/api'
import { format } from 'date-fns'
import Link from 'next/link'

export default function DashboardPage() {
  const { data: meetings } = useQuery({
    queryKey: ['meetings'],
    queryFn: () => api.getMeetings(),
  })

  const { data: briefs } = useQuery({
    queryKey: ['briefs'],
    queryFn: () => api.getBriefs(),
  })

  const upcomingMeetings = meetings?.filter(
    (m: any) => new Date(m.start_time) > new Date()
  ).slice(0, 5) || []

  const recentBriefs = briefs?.slice(0, 5) || []

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Upcoming Meetings"
          value={upcomingMeetings.length}
          icon={<Calendar className="h-6 w-6" />}
          color="bg-blue-500"
        />
        <StatCard
          title="Briefs Generated"
          value={briefs?.length || 0}
          icon={<FileText className="h-6 w-6" />}
          color="bg-green-500"
        />
        <StatCard
          title="Contacts"
          value="--"
          icon={<Users className="h-6 w-6" />}
          color="bg-purple-500"
        />
        <StatCard
          title="Avg Brief Time"
          value="~30s"
          icon={<Clock className="h-6 w-6" />}
          color="bg-orange-500"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upcoming Meetings */}
        <div className="bg-card rounded-lg border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Upcoming Meetings</h2>
            <Link href="/meetings" className="text-sm text-primary hover:underline">
              View all
            </Link>
          </div>
          {upcomingMeetings.length === 0 ? (
            <p className="text-muted-foreground">No upcoming meetings</p>
          ) : (
            <div className="space-y-4">
              {upcomingMeetings.map((meeting: any) => (
                <div
                  key={meeting.id}
                  className="flex items-center justify-between p-3 bg-secondary/50 rounded-lg"
                >
                  <div>
                    <p className="font-medium">{meeting.title}</p>
                    <p className="text-sm text-muted-foreground">
                      {format(new Date(meeting.start_time), 'MMM d, yyyy h:mm a')}
                    </p>
                  </div>
                  {meeting.has_brief ? (
                    <Link
                      href={`/briefs/${meeting.brief_id}`}
                      className="text-sm bg-green-100 text-green-700 px-3 py-1 rounded-full"
                    >
                      View Brief
                    </Link>
                  ) : (
                    <Link
                      href={`/meetings/${meeting.id}`}
                      className="text-sm bg-primary text-primary-foreground px-3 py-1 rounded-full hover:opacity-90"
                    >
                      Generate Brief
                    </Link>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Briefs */}
        <div className="bg-card rounded-lg border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Recent Briefs</h2>
            <Link href="/briefs" className="text-sm text-primary hover:underline">
              View all
            </Link>
          </div>
          {recentBriefs.length === 0 ? (
            <p className="text-muted-foreground">No briefs generated yet</p>
          ) : (
            <div className="space-y-4">
              {recentBriefs.map((brief: any) => (
                <Link
                  key={brief.id}
                  href={`/briefs/${brief.id}`}
                  className="block p-3 bg-secondary/50 rounded-lg hover:bg-secondary transition-colors"
                >
                  <p className="font-medium">{brief.title}</p>
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {brief.executive_summary}
                  </p>
                  <p className="text-xs text-muted-foreground mt-2">
                    Generated {format(new Date(brief.generated_at), 'MMM d, yyyy')}
                  </p>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function StatCard({
  title,
  value,
  icon,
  color,
}: {
  title: string
  value: string | number
  icon: React.ReactNode
  color: string
}) {
  return (
    <div className="bg-card rounded-lg border p-6">
      <div className="flex items-center gap-4">
        <div className={`${color} text-white p-3 rounded-lg`}>{icon}</div>
        <div>
          <p className="text-sm text-muted-foreground">{title}</p>
          <p className="text-2xl font-bold">{value}</p>
        </div>
      </div>
    </div>
  )
}

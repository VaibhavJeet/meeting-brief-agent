'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Calendar, Plus, Loader2 } from 'lucide-react'
import { api } from '@/lib/api'
import { format } from 'date-fns'
import Link from 'next/link'

export default function MeetingsPage() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)

  const { data: meetings, isLoading } = useQuery({
    queryKey: ['meetings'],
    queryFn: () => api.getMeetings(),
  })

  const createMutation = useMutation({
    mutationFn: api.createMeeting,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['meetings'] })
      setShowForm(false)
    },
  })

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    createMutation.mutate({
      title: formData.get('title') as string,
      start_time: new Date(formData.get('start_time') as string).toISOString(),
      end_time: new Date(formData.get('end_time') as string).toISOString(),
      description: formData.get('description') as string,
      participants: (formData.get('participants') as string)
        .split(',')
        .map((p) => p.trim())
        .filter(Boolean),
    })
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Meetings</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:opacity-90"
        >
          <Plus className="h-5 w-5" />
          Add Meeting
        </button>
      </div>

      {showForm && (
        <div className="bg-card border rounded-lg p-6 mb-8">
          <h2 className="text-lg font-semibold mb-4">New Meeting</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Title</label>
              <input
                name="title"
                required
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Meeting title"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Start Time</label>
                <input
                  name="start_time"
                  type="datetime-local"
                  required
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">End Time</label>
                <input
                  name="end_time"
                  type="datetime-local"
                  required
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Participants (comma-separated emails)</label>
              <input
                name="participants"
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="john@example.com, jane@example.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Description</label>
              <textarea
                name="description"
                rows={3}
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Meeting description..."
              />
            </div>
            <div className="flex gap-2">
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:opacity-90 disabled:opacity-50"
              >
                {createMutation.isPending ? 'Creating...' : 'Create Meeting'}
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="px-4 py-2 border rounded-lg hover:bg-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : meetings?.length === 0 ? (
        <div className="text-center py-12">
          <Calendar className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground">No meetings found</p>
        </div>
      ) : (
        <div className="space-y-4">
          {meetings?.map((meeting: any) => (
            <MeetingCard key={meeting.id} meeting={meeting} />
          ))}
        </div>
      )}
    </div>
  )
}

function MeetingCard({ meeting }: { meeting: any }) {
  const queryClient = useQueryClient()
  const generateMutation = useMutation({
    mutationFn: () => api.generateBrief(meeting.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['meetings'] })
    },
  })

  const isPast = new Date(meeting.start_time) < new Date()

  return (
    <div className="bg-card border rounded-lg p-6">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-semibold">{meeting.title}</h3>
          <p className="text-muted-foreground">
            {format(new Date(meeting.start_time), 'EEEE, MMMM d, yyyy')}
          </p>
          <p className="text-sm text-muted-foreground">
            {format(new Date(meeting.start_time), 'h:mm a')} -{' '}
            {format(new Date(meeting.end_time), 'h:mm a')}
          </p>
          {meeting.participants?.length > 0 && (
            <p className="text-sm mt-2">
              <span className="text-muted-foreground">Participants:</span>{' '}
              {meeting.participants.map((p: any) => p.email || p).join(', ')}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2">
          {meeting.has_brief ? (
            <Link
              href={`/briefs/${meeting.brief_id}`}
              className="bg-green-100 text-green-700 px-4 py-2 rounded-lg hover:bg-green-200"
            >
              View Brief
            </Link>
          ) : (
            <button
              onClick={() => generateMutation.mutate()}
              disabled={generateMutation.isPending}
              className="bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:opacity-90 disabled:opacity-50 flex items-center gap-2"
            >
              {generateMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              Generate Brief
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

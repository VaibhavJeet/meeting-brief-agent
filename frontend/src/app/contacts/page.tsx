'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Users, Plus, Search, Loader2 } from 'lucide-react'
import { api } from '@/lib/api'
import { format } from 'date-fns'

export default function ContactsPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [showForm, setShowForm] = useState(false)

  const { data: contacts, isLoading } = useQuery({
    queryKey: ['contacts', search],
    queryFn: () => api.getContacts(search || undefined),
  })

  const createMutation = useMutation({
    mutationFn: api.createContact,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] })
      setShowForm(false)
    },
  })

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    createMutation.mutate({
      email: formData.get('email') as string,
      name: formData.get('name') as string,
      title: formData.get('title') as string,
      company: formData.get('company') as string,
    })
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Contacts</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:opacity-90"
        >
          <Plus className="h-5 w-5" />
          Add Contact
        </button>
      </div>

      {/* Search */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search contacts..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
        />
      </div>

      {showForm && (
        <div className="bg-card border rounded-lg p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">New Contact</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Email *</label>
                <input
                  name="email"
                  type="email"
                  required
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="john@example.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Name</label>
                <input
                  name="name"
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="John Doe"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Title</label>
                <input
                  name="title"
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="Product Manager"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Company</label>
                <input
                  name="company"
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="Acme Inc"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:opacity-90 disabled:opacity-50"
              >
                {createMutation.isPending ? 'Creating...' : 'Create Contact'}
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
      ) : contacts?.length === 0 ? (
        <div className="text-center py-12">
          <Users className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground">No contacts found</p>
        </div>
      ) : (
        <div className="bg-card border rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-secondary/50">
              <tr>
                <th className="text-left px-6 py-3 text-sm font-medium">Name</th>
                <th className="text-left px-6 py-3 text-sm font-medium">Email</th>
                <th className="text-left px-6 py-3 text-sm font-medium">Company</th>
                <th className="text-left px-6 py-3 text-sm font-medium">Interactions</th>
                <th className="text-left px-6 py-3 text-sm font-medium">Last Contact</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {contacts?.map((contact: any) => (
                <tr key={contact.id} className="hover:bg-secondary/30">
                  <td className="px-6 py-4">
                    <p className="font-medium">{contact.name || '-'}</p>
                    {contact.title && (
                      <p className="text-sm text-muted-foreground">{contact.title}</p>
                    )}
                  </td>
                  <td className="px-6 py-4 text-muted-foreground">{contact.email}</td>
                  <td className="px-6 py-4">{contact.company || '-'}</td>
                  <td className="px-6 py-4">{contact.total_interactions}</td>
                  <td className="px-6 py-4 text-muted-foreground">
                    {contact.last_interaction
                      ? format(new Date(contact.last_interaction), 'MMM d, yyyy')
                      : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

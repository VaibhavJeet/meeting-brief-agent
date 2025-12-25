import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const api = {
  // Meetings
  getMeetings: async (params?: { start_date?: string; end_date?: string }) => {
    const { data } = await client.get('/meetings', { params })
    return data
  },

  getMeeting: async (id: string) => {
    const { data } = await client.get(`/meetings/${id}`)
    return data
  },

  createMeeting: async (meeting: {
    title: string
    start_time: string
    end_time: string
    participants?: string[]
    description?: string
  }) => {
    const { data } = await client.post('/meetings', meeting)
    return data
  },

  generateBrief: async (
    meetingId: string,
    options?: {
      include_email?: boolean
      include_crm?: boolean
      include_calendar?: boolean
      lookback_days?: number
    }
  ) => {
    const { data } = await client.post(`/meetings/${meetingId}/brief`, null, {
      params: options,
    })
    return data
  },

  deleteMeeting: async (id: string) => {
    const { data } = await client.delete(`/meetings/${id}`)
    return data
  },

  // Briefs
  getBriefs: async () => {
    const { data } = await client.get('/briefs')
    return data
  },

  getBrief: async (id: string) => {
    const { data } = await client.get(`/briefs/${id}`)
    return data
  },

  updateBrief: async (id: string, updates: Record<string, any>) => {
    const { data } = await client.put(`/briefs/${id}`, updates)
    return data
  },

  deleteBrief: async (id: string) => {
    const { data } = await client.delete(`/briefs/${id}`)
    return data
  },

  exportBrief: async (id: string, format: 'markdown' | 'json') => {
    const { data } = await client.get(`/briefs/${id}/export`, {
      params: { format },
    })
    return data
  },

  // Contacts
  getContacts: async (search?: string) => {
    const { data } = await client.get('/contacts', { params: { search } })
    return data
  },

  getContact: async (id: string) => {
    const { data } = await client.get(`/contacts/${id}`)
    return data
  },

  createContact: async (contact: {
    email: string
    name?: string
    title?: string
    company?: string
  }) => {
    const { data } = await client.post('/contacts', contact)
    return data
  },

  getContactHistory: async (id: string) => {
    const { data } = await client.get(`/contacts/${id}/history`)
    return data
  },

  // Settings
  getIntegrationStatus: async () => {
    const { data } = await client.get('/settings/integrations')
    return data
  },

  getLLMConfig: async () => {
    const { data } = await client.get('/settings/llm')
    return data
  },
}

'use client'

import { useQuery } from '@tanstack/react-query'
import { CheckCircle, XCircle, Loader2 } from 'lucide-react'
import { api } from '@/lib/api'

export default function SettingsPage() {
  const { data: integrations, isLoading } = useQuery({
    queryKey: ['integrations'],
    queryFn: () => api.getIntegrationStatus(),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="p-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-8">Settings</h1>

      {/* LLM Configuration */}
      <section className="bg-card border rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">LLM Configuration</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-secondary/50 rounded-lg">
            <div>
              <p className="font-medium">Provider</p>
              <p className="text-sm text-muted-foreground">
                {integrations?.llm?.provider || 'Not configured'}
              </p>
            </div>
            <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm">
              Active
            </span>
          </div>
          <div className="flex items-center justify-between p-4 bg-secondary/50 rounded-lg">
            <div>
              <p className="font-medium">Model</p>
              <p className="text-sm text-muted-foreground">
                {integrations?.llm?.model || 'Not configured'}
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Integrations */}
      <section className="bg-card border rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Integrations</h2>
        <div className="space-y-4">
          <IntegrationCard
            name="Calendar"
            description="Google Calendar or Outlook integration for meeting data"
            status={integrations?.calendar?.status}
            provider={integrations?.calendar?.provider}
          />
          <IntegrationCard
            name="Email"
            description="Gmail or IMAP email integration for context gathering"
            status={integrations?.email?.status}
            provider={integrations?.email?.provider}
          />
          <IntegrationCard
            name="CRM"
            description="HubSpot or Salesforce integration for contact data"
            status={integrations?.crm?.status}
            provider={integrations?.crm?.provider}
          />
        </div>
      </section>

      {/* Environment Variables */}
      <section className="bg-card border rounded-lg p-6 mt-6">
        <h2 className="text-xl font-semibold mb-4">Configuration</h2>
        <p className="text-muted-foreground mb-4">
          Configure integrations by setting environment variables in your <code className="bg-secondary px-1 rounded">.env</code> file.
        </p>
        <div className="bg-secondary/50 rounded-lg p-4 font-mono text-sm">
          <p className="text-muted-foreground"># LLM Provider</p>
          <p>LLM_PROVIDER=openai</p>
          <p>OPENAI_API_KEY=sk-...</p>
          <p className="mt-2 text-muted-foreground"># Calendar (Google)</p>
          <p>GOOGLE_CREDENTIALS_PATH=./credentials/google.json</p>
          <p className="mt-2 text-muted-foreground"># CRM (HubSpot)</p>
          <p>CRM_PROVIDER=hubspot</p>
          <p>CRM_API_KEY=...</p>
        </div>
      </section>
    </div>
  )
}

function IntegrationCard({
  name,
  description,
  status,
  provider,
}: {
  name: string
  description: string
  status?: string
  provider?: string
}) {
  const isConfigured = status === 'configured'

  return (
    <div className="flex items-center justify-between p-4 bg-secondary/50 rounded-lg">
      <div>
        <p className="font-medium">{name}</p>
        <p className="text-sm text-muted-foreground">{description}</p>
        {provider && (
          <p className="text-xs text-muted-foreground mt-1">Provider: {provider}</p>
        )}
      </div>
      <div className="flex items-center gap-2">
        {isConfigured ? (
          <>
            <CheckCircle className="h-5 w-5 text-green-600" />
            <span className="text-sm text-green-600">Configured</span>
          </>
        ) : (
          <>
            <XCircle className="h-5 w-5 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">Not configured</span>
          </>
        )}
      </div>
    </div>
  )
}

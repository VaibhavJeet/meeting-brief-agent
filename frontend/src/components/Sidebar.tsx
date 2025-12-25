'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Calendar, FileText, Users, Settings, Home } from 'lucide-react'
import { cn } from '@/lib/utils'

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Meetings', href: '/meetings', icon: Calendar },
  { name: 'Briefs', href: '/briefs', icon: FileText },
  { name: 'Contacts', href: '/contacts', icon: Users },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="w-64 bg-card border-r flex flex-col">
      <div className="p-6 border-b">
        <h1 className="text-xl font-bold">Meeting Brief</h1>
        <p className="text-sm text-muted-foreground">AI-powered intelligence</p>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          )
        })}
      </nav>

      <div className="p-4 border-t">
        <div className="bg-secondary/50 rounded-lg p-3">
          <p className="text-sm font-medium">Quick Tip</p>
          <p className="text-xs text-muted-foreground mt-1">
            Generate briefs before meetings to stay prepared with context from emails and CRM.
          </p>
        </div>
      </div>
    </div>
  )
}

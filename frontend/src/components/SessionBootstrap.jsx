import { useEffect, useState } from 'react'
import { BookOpen, LoaderCircle } from 'lucide-react'
import { useLocation } from 'react-router'

import { restoreSessionFromCookie } from '../services/apiClient'
import { hasRefreshSessionHint, hasStoredSession } from '../services/authSession'

const PUBLIC_PATHS = new Set(['/', '/cadastro', '/esqueci-senha', '/auth/reset-password', '/compartilhamento'])

export function SessionBootstrap({ children }) {
  const location = useLocation()
  const shouldRestore = hasStoredSession()
    || hasRefreshSessionHint()
    || !PUBLIC_PATHS.has(location.pathname)
  const [checkingSession, setCheckingSession] = useState(shouldRestore)

  useEffect(() => {
    if (!shouldRestore) return undefined
    let active = true

    restoreSessionFromCookie().finally(() => {
      if (active) setCheckingSession(false)
    })

    return () => {
      active = false
    }
  }, [shouldRestore])

  if (checkingSession) {
    return (
      <div
        className="flex min-h-screen items-center justify-center bg-background p-6"
        role="status"
        aria-live="polite"
      >
        <div className="flex flex-col items-center gap-4 text-primary">
          <BookOpen className="h-10 w-10" strokeWidth={1.5} aria-hidden="true" />
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <LoaderCircle className="h-4 w-4 animate-spin" aria-hidden="true" />
            <span>Verificando sua sessão...</span>
          </div>
        </div>
      </div>
    )
  }

  return children
}

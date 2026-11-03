import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router'
import { ClockAlert } from 'lucide-react'

import { SESSION_EXPIRED_EVENT } from '../services/authSession'


export function SessionExpiredModal() {
  const navigate = useNavigate()
  const [message, setMessage] = useState('')

  useEffect(() => {
    const handleExpiration = (event) => {
      setMessage(
        event.detail?.message
          || 'Suas credenciais expiraram. Entre novamente para continuar.',
      )
    }
    window.addEventListener(SESSION_EXPIRED_EVENT, handleExpiration)
    return () => window.removeEventListener(SESSION_EXPIRED_EVENT, handleExpiration)
  }, [])

  if (!message) return null

  const returnToLogin = () => {
    const notification = message
    setMessage('')
    navigate('/', {
      replace: true,
      state: { mensagem: notification },
    })
  }

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/55 p-4"
      role="alertdialog"
      aria-modal="true"
      aria-labelledby="session-expired-title"
      aria-describedby="session-expired-description"
    >
      <div className="w-full max-w-md rounded-2xl border border-border bg-card p-6 text-center shadow-xl">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
          <ClockAlert className="h-6 w-6 text-primary" aria-hidden="true" />
        </div>
        <h2 id="session-expired-title" className="mb-2 text-xl">
          Sessão expirada
        </h2>
        <p id="session-expired-description" className="mb-6 text-sm text-muted-foreground">
          {message}
        </p>
        <button
          type="button"
          onClick={returnToLogin}
          autoFocus
          className="w-full rounded-lg bg-primary px-4 py-3 text-primary-foreground transition-opacity hover:opacity-90"
        >
          Entrar novamente
        </button>
      </div>
    </div>
  )
}

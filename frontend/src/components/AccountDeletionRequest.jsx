import { useRef, useState } from 'react'
import { useNavigate } from 'react-router'
import { Trash2 } from 'lucide-react'
import { requestAccountDeletion } from '../services/authApi'
import { clearSession, useAuth } from '../services/authSession'

export function AccountDeletionRequest() {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [expanded, setExpanded] = useState(false)
  const [sending, setSending] = useState(false)
  const [sent, setSent] = useState(false)
  const [error, setError] = useState('')
  const pending = useRef(false)

  async function handleRequest() {
    if (pending.current) return
    pending.current = true
    setSending(true)
    setError('')
    try {
      await requestAccountDeletion()
      setSent(true)
    } catch (err) {
      if (err.status === 401) {
        clearSession()
        navigate('/', { replace: true, state: { mensagem: 'Entre novamente para solicitar a exclusão da conta.' } })
        return
      }
      setError('Não foi possível solicitar o e-mail de confirmação. Tente novamente.')
    } finally {
      pending.current = false
      setSending(false)
    }
  }

  return (
    <section className="space-y-4">
      <button type="button" disabled={!isAuthenticated || sending} aria-expanded={expanded}
        aria-controls="account-deletion-request" onClick={() => setExpanded(true)}
        className="w-full flex items-center justify-center gap-2 py-3 bg-destructive text-white rounded-lg hover:opacity-90 disabled:opacity-60">
        <Trash2 className="w-4 h-4" /> Excluir conta
      </button>
      {expanded && (
        <div id="account-deletion-request" className="space-y-4 p-4 border border-destructive/30 rounded-xl">
          <h3 className="font-semibold">Solicitar exclusão da conta</h3>
          <p className="text-sm text-muted-foreground">
            Você receberá um link no e-mail cadastrado para confirmar a exclusão.
            Após a confirmação, sua conta será desativada e todas as sessões serão encerradas.
            Os dados não serão apagados definitivamente.
          </p>
          {sent && <p role="status" className="text-sm">
            Solicitação recebida. Aguarde o e-mail e confira também a caixa de spam.
            Sua conta permanece ativa até você confirmar. Ao reenviar, o link anterior deixa de valer.
          </p>}
          {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
          <div className="flex flex-wrap gap-3">
            <button type="button" onClick={handleRequest} disabled={sending}
              className="px-4 py-3 bg-destructive text-white rounded-lg disabled:opacity-60">
              {sending ? 'Solicitando...' : sent ? 'Reenviar e-mail de confirmação' : 'Enviar e-mail de confirmação'}
            </button>
            <button type="button" disabled={sending} onClick={() => setExpanded(false)}
              className="px-4 py-3 border border-border rounded-lg disabled:opacity-60">
              {sent ? 'Fechar' : 'Cancelar'}
            </button>
          </div>
          <p className="text-sm text-muted-foreground">Se mudar de ideia, ignore o e-mail e não confirme a exclusão.</p>
        </div>
      )}
    </section>
  )
}

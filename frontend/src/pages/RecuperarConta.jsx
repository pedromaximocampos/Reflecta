import { useRef, useState } from 'react'
import { Link } from 'react-router'
import { BookOpen } from 'lucide-react'
import { requestAccountRecovery } from '../services/authApi'

export function RecuperarConta() {
  const [email, setEmail] = useState('')
  const [sending, setSending] = useState(false)
  const [sent, setSent] = useState(false)
  const [error, setError] = useState('')
  const pending = useRef(false)

  async function handleSubmit(event) {
    event.preventDefault()
    if (pending.current) return
    pending.current = true
    setSending(true)
    setSent(false)
    setError('')
    try {
      await requestAccountRecovery(email)
      setSent(true)
    } catch (err) {
      setError(err.status === 422
        ? 'Informe um e-mail válido.'
        : 'Não foi possível solicitar a recuperação. Tente novamente em instantes.')
    } finally {
      pending.current = false
      setSending(false)
    }
  }

  return (
    <main className="min-h-screen bg-background flex items-center justify-center p-6">
      <section className="w-full max-w-md bg-card border border-border rounded-2xl p-8 space-y-6">
        <BookOpen className="w-10 h-10 text-primary" />
        <h1 className="text-2xl">Recuperar conta excluída</h1>
        <p className="text-muted-foreground">Informe o e-mail da conta excluída para solicitar um link de reativação.</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <label htmlFor="recovery-email" className="block">E-mail cadastrado</label>
          <input id="recovery-email" type="email" autoComplete="email" required value={email}
            disabled={sending} onChange={(event) => { setEmail(event.target.value); setSent(false); setError('') }}
            className="w-full px-4 py-3 bg-input-background rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-ring" />
          {sent && <p role="status" className="text-sm text-primary">
            Se houver uma conta excluída associada a esse e-mail, você receberá um link de recuperação.
            Aguarde e confira também a caixa de spam. Ao solicitar novamente, use o link mais recente.
          </p>}
          {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
          <button type="submit" disabled={sending}
            className="w-full bg-primary text-primary-foreground py-3 rounded-lg hover:opacity-90 disabled:opacity-60">
            {sending ? 'Solicitando...' : sent ? 'Reenviar link de recuperação' : 'Enviar link de recuperação'}
          </button>
        </form>
        <nav className="flex flex-col gap-3 text-sm" aria-label="Opções de acesso">
          <Link to="/" className="text-primary">Voltar para o login</Link>
          <Link to="/cadastro" className="text-primary">Criar conta</Link>
          <Link to="/esqueci-senha" className="text-muted-foreground">Esqueci minha senha</Link>
        </nav>
      </section>
    </main>
  )
}

import { useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router'
import { BookOpen, CheckCircle2, Loader2, LogOut, Trash2 } from 'lucide-react'
import { confirmAccountDeletion } from '../services/authApi'
import { clearSession } from '../services/authSession'

export function ConfirmarExclusao() {
  const [params, setParams] = useSearchParams()
  const code = params.get('code')?.trim() ?? ''
  const [deleting, setDeleting] = useState(false)
  const [deleted, setDeleted] = useState(false)
  const [error, setError] = useState('')
  const [invalid, setInvalid] = useState(false)
  const pending = useRef(false)

  async function handleConfirm() {
    if (!code || pending.current || deleted || invalid) return
    pending.current = true
    setDeleting(true)
    setError('')
    try {
      await confirmAccountDeletion(code)
      clearSession()
      setDeleted(true)
      setParams({}, { replace: true })
    } catch (err) {
      if ([400, 404, 410, 422].includes(err.status)) {
        setInvalid(true)
        setError('Este link é inválido, expirou ou já foi utilizado. Se sua conta ainda estiver ativa, entre e solicite um novo link pelo perfil.')
      } else {
        setError('Não foi possível confirmar a exclusão. Verifique sua conexão e tente novamente.')
      }
    } finally {
      pending.current = false
      setDeleting(false)
    }
  }

  return (
    <main className="min-h-screen bg-background flex flex-col items-center justify-center gap-8 px-5 py-10">
      <Link to="/" className="flex items-center gap-2 text-primary" aria-label="Reflecta — início">
        <BookOpen className="h-7 w-7" aria-hidden="true" /><span className="text-2xl font-semibold">Reflecta</span>
      </Link>
      <section aria-labelledby="deletion-title" aria-busy={deleting}
        className="w-full max-w-lg bg-card border border-border rounded-3xl p-6 sm:p-10 shadow-lg space-y-6">
        <div className={`inline-flex h-14 w-14 items-center justify-center rounded-2xl ${deleted ? 'bg-primary/10 text-primary' : 'bg-destructive/10 text-destructive'}`}>
          {deleted ? <CheckCircle2 className="h-7 w-7" aria-hidden="true" /> : <Trash2 className="h-7 w-7" aria-hidden="true" />}
        </div>
        <div className="space-y-2">
          <p className="text-sm font-medium text-muted-foreground">{deleted ? 'Solicitação concluída' : 'Confirmação de exclusão'}</p>
          <h1 id="deletion-title" className="text-2xl sm:text-3xl font-semibold leading-tight">
            {deleted ? 'Sua conta foi excluída' : 'Tem certeza de que deseja excluir sua conta?'}
          </h1>
        </div>
        {deleted ? (
          <>
            <p role="status">Sua conta foi desativada e as sessões foram encerradas.</p>
            <Link to="/" replace className="block text-center px-5 py-3 rounded-xl bg-primary text-primary-foreground">Voltar para o login</Link>
          </>
        ) : !code ? (
          <>
            <p role="alert">O link está incompleto. Abra o link de confirmação recebido por e-mail ou solicite um novo pelo perfil.</p>
            <Link to="/auth/perfil" className="inline-block text-primary">Ir para o perfil</Link>
          </>
        ) : (
          <>
            <p className="text-muted-foreground leading-relaxed">Antes de continuar, confira o que acontece ao confirmar a exclusão da conta vinculada a este link.</p>
            <div className="rounded-2xl bg-muted p-5 space-y-3 text-sm leading-relaxed">
              <p className="flex items-start gap-3"><LogOut className="h-5 w-5 shrink-0 text-muted-foreground" aria-hidden="true" />Sua conta será desativada e todas as sessões serão encerradas.</p>
              <p>Seus dados não serão apagados definitivamente. Você poderá solicitar a recuperação da conta pela tela de login.</p>
            </div>
            {error && <p role="alert" className="rounded-xl bg-destructive/10 p-4 text-sm text-destructive">{error}</p>}
            <button type="button" disabled={deleting || invalid} onClick={handleConfirm}
              className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-destructive text-white rounded-xl font-medium hover:opacity-90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-destructive focus-visible:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed">
              {deleting && <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" />}
              {deleting ? 'Excluindo conta...' : 'Sim, quero excluir minha conta'}
            </button>
            {!deleting && <Link to="/auth/perfil" replace className="block text-center px-4 py-3 border border-border rounded-xl hover:bg-muted">
              {invalid ? 'Ir para o perfil' : 'Cancelar e manter minha conta'}
            </Link>}
            <p className="text-xs text-muted-foreground text-center">A exclusão só será realizada quando você confirmar no botão acima.</p>
          </>
        )}
      </section>
    </main>
  )
}

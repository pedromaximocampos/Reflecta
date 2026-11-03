import { useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router'
import { BookOpen } from 'lucide-react'
import { confirmAccountRecovery } from '../services/authApi'

export function ConfirmarRecuperacao() {
  const [params, setParams] = useSearchParams()
  const code = params.get('code')?.trim() ?? ''
  const [confirming, setConfirming] = useState(false)
  const [recovered, setRecovered] = useState(false)
  const [error, setError] = useState('')
  const [invalidCode, setInvalidCode] = useState(null)
  const pending = useRef(false)
  const invalid = invalidCode === code

  async function handleConfirm() {
    if (!code || pending.current || recovered || invalid) return
    pending.current = true
    setConfirming(true)
    setError('')
    try {
      await confirmAccountRecovery(code)
      setRecovered(true)
      setParams({}, { replace: true })
    } catch (err) {
      if ([400, 404, 410, 422].includes(err.status)) {
        setInvalidCode(code)
        setError('Este link é inválido, expirou ou já foi utilizado. Solicite um novo link para recuperar sua conta.')
      } else {
        setError('Não foi possível confirmar a recuperação. Verifique sua conexão e tente novamente.')
      }
    } finally {
      pending.current = false
      setConfirming(false)
    }
  }

  return (
    <main className="min-h-screen bg-background flex items-center justify-center p-6">
      <section className="w-full max-w-lg bg-card border border-border rounded-2xl p-8 space-y-6">
        <BookOpen className="w-10 h-10 text-primary" />
        <h1 className="text-2xl">{recovered ? 'Conta recuperada' : 'Confirmar recuperação da conta'}</h1>
        {recovered ? (
          <>
            <p role="status">Sua conta foi reativada. Entre novamente com seu e-mail e sua senha.</p>
            <Link to="/" replace className="inline-block text-primary">Ir para o login</Link>
          </>
        ) : !code ? (
          <>
            <p role="alert">O link está incompleto. Abra o link recebido por e-mail ou solicite um novo.</p>
            <Link to="/auth/request-recovery" className="inline-block text-primary">Solicitar novo link</Link>
          </>
        ) : (
          <>
            <p className="text-muted-foreground">Confirme para reativar a conta vinculada a este link. Depois, você poderá fazer login com suas credenciais existentes.</p>
            {error && <p role="alert" className="text-destructive">{error}</p>}
            <button type="button" onClick={handleConfirm} disabled={confirming || invalid}
              className="w-full bg-primary text-primary-foreground py-3 rounded-lg hover:opacity-90 disabled:opacity-60">
              {confirming ? 'Recuperando...' : 'Confirmar recuperação da conta'}
            </button>
            {!confirming && <nav className="flex flex-col gap-3 text-sm" aria-label="Opções de recuperação">
              <Link to="/auth/request-recovery" className="text-primary">Solicitar novo link</Link>
              <Link to="/" replace className="text-muted-foreground">Cancelar e voltar ao login</Link>
            </nav>}
          </>
        )}
      </section>
    </main>
  )
}

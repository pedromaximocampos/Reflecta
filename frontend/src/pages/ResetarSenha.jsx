import { useRef, useState } from 'react'
import { BookOpen, CheckCircle, Eye, EyeOff, KeyRound } from 'lucide-react'
import { Link, useSearchParams } from 'react-router'
import { resetPassword } from '../services/authApi'

const MIN_PASSWORD_LENGTH = 12

export function ResetarSenha() {
  const [params, setParams] = useSearchParams()
  const code = params.get('code')?.trim() ?? ''
  const [password, setPassword] = useState('')
  const [repeatedPassword, setRepeatedPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showRepeatedPassword, setShowRepeatedPassword] = useState(false)
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')
  const pending = useRef(false)

  async function handleSubmit(event) {
    event.preventDefault()
    if (pending.current || success) return
    setError('')
    if (!code) {
      setError('O link de redefinição está incompleto. Solicite um novo e-mail.')
      return
    }
    if (password.length < MIN_PASSWORD_LENGTH) {
      setError(`A senha deve ter pelo menos ${MIN_PASSWORD_LENGTH} caracteres.`)
      return
    }
    if (password !== repeatedPassword) {
      setError('As senhas não coincidem.')
      return
    }

    pending.current = true
    setSaving(true)
    try {
      await resetPassword(code, password, repeatedPassword)
      setSuccess(true)
      setPassword('')
      setRepeatedPassword('')
      setParams({}, { replace: true })
    } catch (requestError) {
      setError(requestError.message || 'Não foi possível redefinir a senha. Solicite um novo link e tente novamente.')
    } finally {
      pending.current = false
      setSaving(false)
    }
  }

  const inputClass = 'w-full px-4 py-3 pr-12 bg-input-background rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-ring'

  return (
    <main className="min-h-screen bg-gradient-to-br from-background via-background to-primary/10 flex items-center justify-center p-6">
      <section className="w-full max-w-md">
        <div className="flex flex-col items-center mb-8">
          <div className="flex items-center gap-3 mb-4">
            <BookOpen className="w-10 h-10 text-primary" strokeWidth={1.5} />
            <h1 className="text-4xl text-primary">Reflecta</h1>
          </div>
          <p className="text-muted-foreground text-center">Proteja sua conta com uma nova senha.</p>
        </div>

        <div className="bg-card rounded-2xl shadow-sm border border-border p-8">
          {success ? (
            <div className="space-y-5 text-center">
              <CheckCircle className="w-12 h-12 mx-auto text-primary" />
              <h2 className="text-2xl">Senha redefinida</h2>
              <p role="status" className="text-muted-foreground">Sua senha foi alterada com sucesso. Use a nova senha para entrar na sua conta.</p>
              <Link to="/" replace className="block w-full bg-primary text-primary-foreground py-3 rounded-lg hover:opacity-90">Ir para o login</Link>
            </div>
          ) : !code ? (
            <div className="space-y-5 text-center">
              <KeyRound className="w-12 h-12 mx-auto text-destructive" />
              <h2 className="text-2xl">Link inválido</h2>
              <p role="alert" className="text-muted-foreground">O código de redefinição não foi encontrado na URL. Solicite um novo link.</p>
              <Link to="/esqueci-senha" className="block text-primary underline">Solicitar novo link</Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5" aria-busy={saving}>
              <div>
                <h2 className="text-2xl mb-2">Redefinir senha</h2>
                <p className="text-sm text-muted-foreground">Digite uma senha nova para concluir a recuperação da sua conta.</p>
              </div>

              <div>
                <label htmlFor="new-password" className="block mb-2">Nova senha</label>
                <div className="relative">
                  <input id="new-password" type={showPassword ? 'text' : 'password'} autoComplete="new-password" required minLength={MIN_PASSWORD_LENGTH} value={password} disabled={saving} onChange={(event) => { setPassword(event.target.value); setError('') }} className={inputClass} />
                  <button type="button" aria-label={showPassword ? 'Ocultar nova senha' : 'Mostrar nova senha'} onClick={() => setShowPassword((value) => !value)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
                <p className="mt-1 text-xs text-muted-foreground">Mínimo de {MIN_PASSWORD_LENGTH} caracteres.</p>
              </div>

              <div>
                <label htmlFor="repeated-password" className="block mb-2">Repita a nova senha</label>
                <div className="relative">
                  <input id="repeated-password" type={showRepeatedPassword ? 'text' : 'password'} autoComplete="new-password" required minLength={MIN_PASSWORD_LENGTH} value={repeatedPassword} disabled={saving} onChange={(event) => { setRepeatedPassword(event.target.value); setError('') }} className={inputClass} />
                  <button type="button" aria-label={showRepeatedPassword ? 'Ocultar confirmação da senha' : 'Mostrar confirmação da senha'} onClick={() => setShowRepeatedPassword((value) => !value)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                    {showRepeatedPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>

              {error && <p role="alert" className="p-3 rounded-lg border border-red-200 bg-red-50 text-red-700 text-sm">{error}</p>}
              <button type="submit" disabled={saving} className="w-full bg-primary text-primary-foreground py-3 rounded-lg hover:opacity-90 disabled:opacity-60">
                {saving ? 'Redefinindo...' : 'Redefinir senha'}
              </button>
              <Link to="/" className="block text-center text-sm text-muted-foreground underline">Cancelar e voltar ao login</Link>
            </form>
          )}
        </div>
      </section>
    </main>
  )
}

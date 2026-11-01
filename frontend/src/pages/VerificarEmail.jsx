import { useEffect, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router'
import { BookOpen, CheckCircle2, CircleAlert, Loader2 } from 'lucide-react'
import { verifyEmail } from '../services/authApi'

export function VerificarEmail() {
  const [params, setParams] = useSearchParams()
  const code = params.get('code')?.trim() ?? ''
  const [status, setStatus] = useState('checking')
  const [message, setMessage] = useState('')
  const request = useRef(null)
  const confirmed = useRef(false)

  useEffect(() => {
    if (confirmed.current) return
    let active = true
    if (!code) return
    // Reuse the request during StrictMode's effect replay: codes are one-time.
    if (request.current?.code !== code) request.current = { code, promise: verifyEmail(code) }
    request.current.promise.then(() => {
      if (!active) return
      confirmed.current = true
      setStatus('verified')
      setParams({}, { replace: true })
    }).catch(error => {
      if (!active) return
      setStatus('error')
      setMessage(error.status === 410
        ? 'Este link expirou. Solicitamos o envio de um novo e-mail de confirmação. Confira sua caixa de entrada e a pasta de spam.'
        : [400, 401, 404, 409, 422].includes(error.status)
        ? 'Este link é inválido, expirou ou já foi utilizado. Se você já confirmou seu e-mail, pode entrar normalmente.'
        : 'Não foi possível confirmar seu e-mail agora. Tente abrir o link novamente em alguns instantes.')
    })
    return () => { active = false }
  }, [code, setParams])

  const verified = status === 'verified'
  const checking = status === 'checking' && Boolean(code)
  return <main className="min-h-screen bg-background flex flex-col items-center justify-center gap-8 px-5 py-10">
    <Link to="/" className="flex items-center gap-2 text-primary" aria-label="Reflecta — início">
      <BookOpen className="h-7 w-7" aria-hidden="true" /><span className="text-2xl font-semibold">Reflecta</span>
    </Link>
    <section aria-labelledby="verification-title" aria-busy={checking}
      className="w-full max-w-lg bg-card border border-border rounded-3xl p-6 sm:p-10 shadow-lg text-center space-y-6">
      <div className={`inline-flex h-16 w-16 items-center justify-center rounded-2xl ${!checking && !verified ? 'bg-destructive/10 text-destructive' : 'bg-primary/10 text-primary'}`}>
        {checking ? <Loader2 className="h-8 w-8 animate-spin" aria-hidden="true" />
          : verified ? <CheckCircle2 className="h-8 w-8" aria-hidden="true" /> : <CircleAlert className="h-8 w-8" aria-hidden="true" />}
      </div>
      <div className="space-y-2">
        <p className="text-sm font-medium text-muted-foreground">Confirmação de e-mail</p>
        <h1 id="verification-title" className="text-2xl sm:text-3xl font-semibold leading-tight">
          {checking ? 'Confirmando seu e-mail...' : verified ? 'E-mail confirmado!' : 'Não foi possível confirmar'}
        </h1>
      </div>
      {checking ? <p role="status" className="text-muted-foreground">Aguarde um instante enquanto confirmamos seu endereço de e-mail.</p>
        : verified ? <div role="status" className="space-y-4">
          <p className="text-muted-foreground leading-relaxed">Obrigado por confirmar seu e-mail e fazer parte do Reflecta. Sua conta está pronta para você entrar e começar suas reflexões.</p>
          <p className="rounded-2xl bg-muted p-5 font-medium">Tudo certo! Você já pode fechar esta aba.</p>
        </div> : <p role="alert" className="text-muted-foreground leading-relaxed">{message || 'O link está incompleto. Abra o link de confirmação recebido por e-mail.'}</p>}
      {!checking && <Link to="/" replace className="block px-5 py-3 rounded-xl bg-primary text-primary-foreground hover:opacity-90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
        {verified ? 'Ir para o login' : 'Voltar para o login'}
      </Link>}
    </section>
  </main>
}

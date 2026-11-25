import { useState } from 'react'
import { BookOpen, ShieldCheck } from 'lucide-react'
import { Link, useLocation, useSearchParams } from 'react-router'

import { restoreSessionFromCookie } from '../services/apiClient'
import { acceptAdminInvitation } from '../services/authApi'
import { useAuth } from '../services/authSession'


export function AceitarConviteAdmin() {
  const [params] = useSearchParams()
  const location = useLocation()
  const code = params.get('code')?.trim() ?? ''
  const { isAuthenticated, isAdmin, user } = useAuth()
  const [busy, setBusy] = useState(false)
  const [accepted, setAccepted] = useState(false)
  const [requiresLogin, setRequiresLogin] = useState(false)
  const [error, setError] = useState('')
  const returnPath = `${location.pathname}${location.search}`
  const loginPath = `/?${new URLSearchParams({ next: returnPath })}`

  async function accept() {
    if (!code || busy) return
    setBusy(true)
    setError('')
    try {
      await acceptAdminInvitation(code)
      const refreshed = await restoreSessionFromCookie()
      setRequiresLogin(!refreshed)
      setAccepted(true)
    } catch (err) {
      if (err.status === 400) {
        setError('Este convite não pertence à conta conectada, expirou ou já foi utilizado.')
      } else {
        setError(err.message || 'Não foi possível aceitar o convite agora.')
      }
    } finally {
      setBusy(false)
    }
  }

  return <main className="min-h-screen bg-background flex items-center justify-center p-6">
    <section className="w-full max-w-lg bg-card border border-border rounded-2xl p-8 space-y-6">
      <div className="flex items-center gap-3 text-primary"><BookOpen className="w-9 h-9" /><span className="text-2xl">Reflecta</span></div>
      <div className="flex items-start gap-3"><ShieldCheck className="w-7 h-7 text-primary shrink-0" /><div><h1 className="text-2xl">Convite administrativo</h1><p className="mt-2 text-muted-foreground">Confirme conscientemente o novo nível de acesso da sua conta.</p></div></div>

      {!code ? <>
        <p role="alert">O link está incompleto. Peça ao administrador para enviar um novo convite.</p>
        <Link to="/" className="text-primary">Voltar para o login</Link>
      </> : accepted || isAdmin ? <>
        <p role="status">Sua conta agora possui acesso administrativo ao Reflecta.</p>
        {requiresLogin
          ? <Link to={loginPath} className="catalog-primary inline-flex">Entrar novamente</Link>
          : <Link to="/deshboard/administradores" className="catalog-primary inline-flex">Abrir painel administrativo</Link>}
      </> : !isAuthenticated ? <>
        <p>Entre com a mesma conta que recebeu este convite. Nenhuma permissão será alterada antes da sua confirmação.</p>
        <Link to={loginPath} className="catalog-primary inline-flex">Entrar para revisar o convite</Link>
      </> : <>
        <div className="rounded-xl bg-muted p-4 text-sm"><strong>Conta conectada</strong><p className="mt-1 text-muted-foreground">{user?.email}</p></div>
        <p>Ao aceitar, você poderá gerenciar temas, obras, passagens, processamentos e outros administradores.</p>
        {error && <p role="alert" className="text-destructive">{error}</p>}
        <div className="flex justify-end gap-3"><Link to="/inicio" className="catalog-button">Cancelar</Link><button type="button" disabled={busy} onClick={accept} className="catalog-primary disabled:opacity-60">{busy ? 'Confirmando…' : 'Aceitar convite'}</button></div>
      </>}
    </section>
  </main>
}

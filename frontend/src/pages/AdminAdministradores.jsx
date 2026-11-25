import { useCallback, useEffect, useState } from 'react'
import { MailPlus, RefreshCw, ShieldCheck, X } from 'lucide-react'

import { PageLoading } from '../components/PageLoading'
import {
  createAdminInvitation,
  listAdminInvitations,
  revokeAdminInvitation,
} from '../services/authApi'


const STATUS = {
  PENDING: ['Pendente', 'admin-invitation-pending'],
  ACCEPTED: ['Aceito', 'admin-invitation-accepted'],
  EXPIRED: ['Expirado', 'admin-invitation-expired'],
  REVOKED: ['Revogado', 'admin-invitation-revoked'],
}

const formatDate = value => value
  ? new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' }).format(new Date(value))
  : '—'


export function AdminAdministradores() {
  const [invitations, setInvitations] = useState([])
  const [email, setEmail] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const load = useCallback(async () => {
    setError('')
    try {
      const response = await listAdminInvitations()
      setInvitations(response.invitations || [])
    } catch (err) {
      setError(err.message || 'Não foi possível carregar os convites.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  async function invite(event, invitationEmail = email) {
    event?.preventDefault()
    setBusy(true)
    setError('')
    setMessage('')
    try {
      await createAdminInvitation(invitationEmail)
      setMessage('Convite registrado e encaminhado para envio.')
      setEmail('')
      setShowForm(false)
      await load()
    } catch (err) {
      const messages = {
        404: 'Nenhuma conta ativa foi encontrada para este e-mail.',
        409: 'A conta já é administradora ou ainda não confirmou o próprio e-mail.',
      }
      setError(messages[err.status] || err.message || 'Não foi possível criar o convite.')
    } finally {
      setBusy(false)
    }
  }

  async function revoke(invitation) {
    if (!window.confirm(`Revogar o convite enviado para ${invitation.target_email}?`)) return
    setBusy(true)
    setError('')
    try {
      await revokeAdminInvitation(invitation.id)
      setMessage('Convite revogado.')
      await load()
    } catch (err) {
      setError(err.message || 'Não foi possível revogar o convite.')
    } finally {
      setBusy(false)
    }
  }

  return <div className="admin-fixed-shell bg-background p-5 md:p-8"><div className="admin-fixed-page max-w-6xl mx-auto">
    <header className="catalog-page-header catalog-page-intro">
      <div className="catalog-page-intro-copy"><h1 className="text-3xl">Administradores e convites</h1><p>Convide contas verificadas e acompanhe cada alteração de acesso.</p></div>
      <div className="catalog-header-actions"><button type="button" onClick={() => setShowForm(true)} className="catalog-primary catalog-hover-primary"><MailPlus size={16} />Novo convite</button><button type="button" onClick={() => { setLoading(true); load() }} className="catalog-button catalog-hover-secondary"><RefreshCw size={15} />Atualizar</button></div>
    </header>

    <div className="admin-scroll-region">
      {showForm && <form onSubmit={invite} className="catalog-card admin-invitation-form"><div><h2>Convidar administrador</h2><p>Por segurança, o e-mail deve pertencer a uma conta ativa e já verificada no Reflecta.</p></div><label htmlFor="admin-email">E-mail da conta<input id="admin-email" type="email" required autoFocus value={email} onChange={event => setEmail(event.target.value)} placeholder="usuario@exemplo.com" /></label><div className="flex justify-end gap-2"><button type="button" onClick={() => setShowForm(false)} className="catalog-button">Cancelar</button><button type="submit" disabled={busy} className="catalog-primary">{busy ? 'Enviando…' : 'Enviar convite'}</button></div></form>}
      {message && <p role="status" className="admin-invitation-feedback">{message}</p>}
      {error && <p role="alert" className="text-destructive">{error}</p>}
      {loading ? <PageLoading variant="cards" label="Carregando convites administrativos…" /> : invitations.length ? <section className="admin-invitation-list" aria-label="Convites administrativos">{invitations.map(invitation => {
        const [statusLabel, statusClass] = STATUS[invitation.status] || [invitation.status, '']
        return <article key={invitation.id} className="catalog-card admin-invitation-card"><div className="admin-invitation-icon"><ShieldCheck size={21} /></div><div className="admin-invitation-copy"><div className="admin-invitation-title"><h2>{invitation.target_username}</h2><span className={`admin-invitation-status ${statusClass}`}>{statusLabel}</span></div><p>{invitation.target_email}</p><dl><div><dt>Enviado</dt><dd>{formatDate(invitation.created_at)}</dd></div><div><dt>Expira</dt><dd>{formatDate(invitation.expires_at)}</dd></div></dl></div><div className="admin-invitation-actions">{invitation.status === 'PENDING' && <button type="button" disabled={busy} onClick={() => revoke(invitation)} className="catalog-button catalog-destructive-outline"><X size={14} />Revogar</button>}{['EXPIRED', 'REVOKED'].includes(invitation.status) && <button type="button" disabled={busy} onClick={() => invite(null, invitation.target_email)} className="catalog-button">Reenviar</button>}</div></article>
      })}</section> : <div className="catalog-card catalog-empty-state"><ShieldCheck size={38} /><h2>Nenhum convite criado</h2><p>Convide uma conta verificada quando precisar dividir a administração do catálogo.</p></div>}
    </div>
  </div></div>
}

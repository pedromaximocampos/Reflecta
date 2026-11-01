import { useEffect, useRef, useState } from 'react'
import { buildContextShareLink, createContextShare, listContextShares, revokeContextShare } from '../../services/contextSharesApi'
import { clearSession } from '../../services/authSession'

export function ContextShareControls({ analysis }) {
  const [opened, setOpened] = useState(false)
  const [confirmed, setConfirmed] = useState(false)
  const [shares, setShares] = useState([])
  const [loading, setLoading] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [created, setCreated] = useState(null)
  const [clock, setClock] = useState(() => Date.now())
  const [revision, setRevision] = useState(0)
  const pending = useRef(false)
  useEffect(() => {
    if (!opened) return
    const controller = new AbortController()
    const timer = setInterval(() => setClock(Date.now()), 30000)
    listContextShares(analysis.id, { signal: controller.signal }).then(data => {
      if (!controller.signal.aborted) { setShares(data.shares); setClock(Date.now()) }
    }).catch(err => {
      if (controller.signal.aborted) return
      if (err.status === 401) clearSession()
      setError(err.message)
    }).finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => { controller.abort(); clearInterval(timer) }
  }, [opened, analysis.id, revision])

  async function perform(action) {
    if (pending.current) return
    pending.current = true
    setBusy(true)
    setError('')
    setMessage('')
    try { await action() } catch (err) {
      if (err.status === 401) clearSession()
      setError(err.message)
    } finally { pending.current = false; setBusy(false) }
  }
  function refresh() { setLoading(true); setRevision(value => value + 1) }
  if (!analysis.period) return <p className="text-sm text-muted-foreground">Para compartilhar, gere uma análise com período de 7 dias.</p>
  return <section className="border-t border-border pt-4 space-y-4" aria-label="Compartilhar análise">
    <button type="button" className="px-4 py-2 rounded-lg border border-border" disabled={busy} onClick={() => { if (!opened) setLoading(true); setOpened(value => !value) }}>{opened ? 'Fechar compartilhamento' : 'Compartilhar análise'}</button>
    {opened && <div className="space-y-4">
      <p>O link mostrará a síntese acima, com o período, resumo, padrões, mudanças e perguntas. As entradas do diário e seus dados de perfil não serão compartilhados.</p>
      <p>Qualquer pessoa com o link poderá consultar a análise por 3 dias. Copie e envie somente a quem você escolher. Você pode revogar o acesso antes do vencimento.</p>
      <label className="flex gap-2 items-start"><input type="checkbox" checked={confirmed} disabled={busy} onChange={event => setConfirmed(event.target.checked)} />Conferi a análise acima e confirmo o compartilhamento desse conteúdo.</label>
      <button type="button" disabled={!confirmed || busy} className="px-4 py-2 rounded-lg bg-primary text-primary-foreground disabled:opacity-50" onClick={() => perform(async () => {
        const result = await createContextShare(analysis.id)
        setCreated({ ...result, url: buildContextShareLink(result.token) })
        setConfirmed(false)
        setMessage('Link criado. Envie-o diretamente à pessoa escolhida.')
        refresh()
      })}>{busy ? 'Aguarde...' : 'Gerar link válido por 3 dias'}</button>
      {created && <div className="space-y-2"><label className="block">Link de acesso<input className="block w-full border border-border rounded-lg p-2" readOnly value={created.url} onFocus={event => event.target.select()} /></label>
        <p className="text-sm">Expira em {new Date(created.expires_at).toLocaleString('pt-BR')}. Guarde o link agora; ele não será exibido novamente após sair da página.</p>
        <button type="button" className="underline" onClick={async () => { try { await navigator.clipboard.writeText(created.url); setMessage('Link copiado.') } catch { setMessage('Selecione o link acima e copie manualmente.') } }}>Copiar link</button></div>}
      {message && <p role="status">{message}</p>}
      {error && <p role="alert" className="text-destructive">{error}</p>}
      <div className="flex justify-between gap-3"><h4 className="font-medium">Links desta análise</h4><button type="button" disabled={busy || loading} className="underline" onClick={refresh}>Atualizar links</button></div>
      {loading ? <p role="status">Carregando links...</p> : !shares.length ? <p>Nenhum link gerado para esta análise.</p> : <ul className="space-y-3">{shares.map(share => <li className="border border-border rounded-lg p-3 space-y-2" key={share.id}>
        <p>Criado em {new Date(share.created_at).toLocaleString('pt-BR')} · {share.state === 'revoked' ? 'Revogado' : share.state === 'expired' || Date.parse(share.expires_at) <= clock ? 'Expirado' : 'Ativo'}</p>
        <p className="text-sm">Vencimento: {new Date(share.expires_at).toLocaleString('pt-BR')}</p>
        {share.state === 'active' && Date.parse(share.expires_at) > clock && <button type="button" disabled={busy} className="text-destructive underline" onClick={() => perform(async () => {
          await revokeContextShare(analysis.id, share.id)
          if (created?.id === share.id) setCreated(null)
          setMessage('Link revogado. O acesso por esse link foi encerrado.')
          refresh()
        })}>Revogar link</button>}
      </li>)}</ul>}
    </div>}
  </section>
}

import { useEffect, useRef, useState } from 'react'
import { Copy, RefreshCw, Share2 } from 'lucide-react'
import { buildContextShareLink, createContextShare, listContextShares, revokeContextShare, rotateContextShareToken } from '../../services/contextSharesApi'
import { clearSession } from '../../services/authSession'

export function ContextShareControls({ analysis, placement = 'footer', heading = '' }) {
  const [opened, setOpened] = useState(false)
  const [confirmed, setConfirmed] = useState(false)
  const [includeJournals, setIncludeJournals] = useState(false)
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
  async function copyLink(token) {
    try {
      await navigator.clipboard.writeText(buildContextShareLink(token))
      setMessage('Link copiado.')
    } catch {
      setMessage('Selecione o link e copie manualmente.')
    }
  }
  if (!analysis.period) return <p className="text-sm text-muted-foreground">Para compartilhar, gere uma análise com período de 7 dias.</p>
  return <section className={`context-share-controls is-${placement}`} aria-label="Compartilhar análise">
    <div className="context-share-controls-heading">
      {heading && <h3>{heading}</h3>}
      <button type="button" className="catalog-button catalog-hover-secondary context-share-trigger" disabled={busy}
        onClick={() => { if (!opened) setLoading(true); setOpened(value => !value) }}>
        <Share2 size={15} aria-hidden="true" />{opened ? 'Fechar compartilhamento' : 'Compartilhar análise'}
      </button>
    </div>
    {opened && <div className="context-share-panel space-y-4">
      <p>O link mostrará a síntese acima, com o período, resumo, padrões, mudanças e perguntas.</p>
      <p>Qualquer pessoa com o link poderá consultar a análise por 3 dias. Copie e envie somente a quem você escolher. Você pode revogar o acesso antes do vencimento.</p>
      <label className="context-share-journals-option">
        <input type="checkbox" checked={includeJournals} disabled={busy}
          onChange={event => setIncludeJournals(event.target.checked)} />
        <span><strong>Incluir também as {analysis.entry_count ?? analysis.entry_ids?.length ?? ''} reflexões utilizadas</strong>
          <small>Serão compartilhados os textos, as conclusões individuais da IA, os temas mantidos e as passagens relacionadas. Dados de perfil e informações técnicas não serão incluídos.</small></span>
      </label>
      <label className="flex gap-2 items-start"><input type="checkbox" checked={confirmed} disabled={busy} onChange={event => setConfirmed(event.target.checked)} />Conferi a análise acima e confirmo o compartilhamento desse conteúdo.</label>
      <button type="button" disabled={!confirmed || busy} className="catalog-primary catalog-hover-primary disabled:opacity-50" onClick={() => perform(async () => {
        const result = await createContextShare(analysis.id, { includeJournals })
        setCreated({ ...result, url: buildContextShareLink(result.token) })
        setConfirmed(false)
        setIncludeJournals(false)
        setMessage('Link criado. Envie-o diretamente à pessoa escolhida.')
        refresh()
      })}>{busy ? 'Aguarde...' : 'Gerar link válido por 3 dias'}</button>
      {created && <div className="space-y-2"><label className="block">Link de acesso<input className="block w-full border border-border rounded-lg p-2" readOnly value={created.url} onFocus={event => event.target.select()} /></label>
        <p className="text-sm">Expira em {new Date(created.expires_at).toLocaleString('pt-BR')}. Guarde o link agora; ele não será exibido novamente após sair da página.</p>
        <button type="button" className="catalog-button catalog-hover-secondary" onClick={async () => { try { await navigator.clipboard.writeText(created.url); setMessage('Link copiado.') } catch { setMessage('Selecione o link acima e copie manualmente.') } }}>Copiar link</button></div>}
      {message && <p role="status">{message}</p>}
      {error && <p role="alert" className="text-destructive">{error}</p>}
      <div className="flex justify-between gap-3"><h4 className="font-medium">Links desta análise</h4><button type="button" disabled={busy || loading} className="catalog-button catalog-hover-secondary" onClick={refresh}>Atualizar links</button></div>
      {loading ? <p role="status">Carregando links...</p> : !shares.length ? <p>Nenhum link gerado para esta análise.</p> : <ul className="space-y-3">{shares.map(share => <li className="border border-border rounded-lg p-3 space-y-2" key={share.id}>
        <p>Criado em {new Date(share.created_at).toLocaleString('pt-BR')} · {share.state === 'revoked' ? 'Revogado' : share.state === 'expired' || Date.parse(share.expires_at) <= clock ? 'Expirado' : 'Ativo'}</p>
        <p className="text-sm">{share.includes_journals ? 'Inclui as reflexões autorizadas' : 'Somente análise contextual'} · Expira em {new Date(share.expires_at).toLocaleString('pt-BR')}</p>
        {share.state === 'active' && Date.parse(share.expires_at) > clock && <><button type="button" disabled={busy} className="catalog-button catalog-hover-destructive text-destructive" onClick={() => perform(async () => {
          await revokeContextShare(analysis.id, share.id)
          if (created?.id === share.id) setCreated(null)
          setMessage('Link revogado. O acesso por esse link foi encerrado.')
          refresh()
        })}>Revogar link</button>{share.token ? <div className="sharing-link-panel"><label htmlFor={`analysis-share-${share.id}`}>Link de acesso</label><div className="sharing-link-row"><input id={`analysis-share-${share.id}`} readOnly value={buildContextShareLink(share.token)} onFocus={event => event.target.select()} /><button type="button" className="catalog-button catalog-hover-secondary" onClick={() => copyLink(share.token)}><Copy size={14} />Copiar</button></div></div> : <div className="sharing-legacy-link"><p>Este endereço antigo não pode ser reconstruído. Gere outro para substituir o anterior.</p><button type="button" disabled={busy} className="catalog-button catalog-hover-secondary" onClick={() => perform(async () => {
          const rotated = await rotateContextShareToken(analysis.id, share.id)
          setCreated({ ...rotated, url: buildContextShareLink(rotated.token) })
          setMessage('Novo link gerado. O endereço anterior deixou de funcionar.')
          refresh()
        })}><RefreshCw size={14} />Gerar novo link</button></div>}</>}
      </li>)}</ul>}
    </div>}
  </section>
}

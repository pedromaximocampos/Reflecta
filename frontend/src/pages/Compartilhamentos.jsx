import { ChevronLeft, ChevronRight, Copy, ExternalLink, ListFilter, Plus, RefreshCw, Share2 } from 'lucide-react'
import { Link } from 'react-router'
import { useEffect, useState } from 'react'
import { buildContextShareLink, listOwnerContextShares, revokeContextShare, rotateContextShareToken } from '../services/contextSharesApi'
import { clearSession } from '../services/authSession'
import { formatPeriodDate } from '../services/contextPeriod'

const PAGE_SIZE = 6
const STATUS_LABELS = { active: 'Ativo', expired: 'Expirado', revoked: 'Revogado' }

export function Compartilhamentos() {
  const [state, setState] = useState('')
  const [page, setPage] = useState(1)
  const [data, setData] = useState({ shares: [], total: 0 })
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState('')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [revision, setRevision] = useState(0)

  useEffect(() => {
    const controller = new AbortController()
    listOwnerContextShares({ state, limit: PAGE_SIZE, offset: (page - 1) * PAGE_SIZE, signal: controller.signal })
      .then(setData)
      .catch((requestError) => {
        if (requestError.name === 'AbortError') return
        if (requestError.status === 401) clearSession()
        setError(requestError.message || 'Não foi possível carregar os compartilhamentos.')
      })
      .finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [state, page, revision])

  const totalPages = Math.max(1, Math.ceil(data.total / PAGE_SIZE))
  const changeState = (value) => {
    if (value === state && page === 1) return
    setLoading(true)
    setError('')
    setState(value)
    setPage(1)
  }
  const changePage = (value) => {
    setLoading(true)
    setError('')
    setPage(value)
  }
  const revoke = async (share) => {
    if (busyId) return
    setBusyId(share.id)
    setError('')
    setMessage('')
    try {
      await revokeContextShare(share.analysis_id, share.id)
      setLoading(true)
      setRevision((value) => value + 1)
    } catch (requestError) {
      if (requestError.status === 401) clearSession()
      setError(requestError.message || 'Não foi possível revogar o compartilhamento.')
    } finally {
      setBusyId('')
    }
  }
  const copyLink = async (share) => {
    if (!share.token) return
    try {
      await navigator.clipboard.writeText(buildContextShareLink(share.token))
      setMessage('Link copiado para a área de transferência.')
      setError('')
    } catch {
      setError('Não foi possível copiar automaticamente. Selecione o endereço e copie manualmente.')
    }
  }
  const rotateLink = async (share) => {
    if (busyId) return
    setBusyId(share.id)
    setError('')
    setMessage('')
    try {
      const rotated = await rotateContextShareToken(share.analysis_id, share.id)
      setData((current) => ({
        ...current,
        shares: current.shares.map((item) => item.id === share.id ? { ...item, ...rotated } : item),
      }))
      setMessage('Novo link gerado. O endereço anterior deixou de funcionar.')
    } catch (requestError) {
      if (requestError.status === 401) clearSession()
      setError(requestError.message || 'Não foi possível gerar um novo link.')
    } finally {
      setBusyId('')
    }
  }

  return <div className="admin-fixed-shell min-h-screen bg-background p-5 md:p-8">
    <div className="admin-fixed-page max-w-6xl mx-auto">
      <header className="catalog-page-header catalog-page-intro">
        <div className="catalog-page-intro-copy"><h1 className="text-3xl">Compartilhamentos</h1><p>Acompanhe os links de análises que você decidiu compartilhar.</p></div>
        <div className="catalog-header-actions">
          <Link to="/inicio/analises" className="catalog-primary catalog-hover-primary"><Plus size={16} />Novo compartilhamento</Link>
          <div className="profile-sharing-filter">
            <button type="button" className="catalog-button catalog-hover-secondary profile-sharing-filter-trigger" aria-haspopup="true"><ListFilter size={15} />Filtrar{state && <span aria-label={`Filtro ativo: ${STATUS_LABELS[state]}`} />}</button>
            <div className="profile-sharing-filter-popover">
              <label htmlFor="share-state">Status</label>
              <select id="share-state" value={state} onChange={(event) => changeState(event.target.value)}>
                <option value="">Todos</option>
                <option value="active">Ativos</option>
                <option value="expired">Expirados</option>
                <option value="revoked">Revogados</option>
              </select>
            </div>
          </div>
        </div>
      </header>

      <div className="admin-scroll-region sharing-scroll-region">
        <div className="flex flex-wrap items-center justify-end gap-4">
          <nav className="theme-pagination" aria-label="Paginação dos compartilhamentos"><button type="button" aria-label="Página anterior" disabled={page === 1} onClick={() => changePage(page - 1)}><ChevronLeft size={15} /></button><span>{totalPages > 1 ? `Página ${page} de ${totalPages}` : 'Página 1'}</span><button type="button" aria-label="Próxima página" disabled={page >= totalPages} onClick={() => changePage(page + 1)}><ChevronRight size={15} /></button></nav>
        </div>

        {error && <p role="alert" className="text-destructive">{error}</p>}
        {message && <p role="status" className="text-sm text-primary">{message}</p>}
        {loading ? <p role="status">Carregando compartilhamentos...</p> : !data.shares.length ? <div className="bg-card border border-border rounded-2xl p-8 text-center"><Share2 className="w-8 h-8 text-primary mx-auto mb-3" /><h2 className="text-lg mb-2">Nenhum compartilhamento encontrado</h2><p className="text-muted-foreground">Gere uma análise histórica, confira o conteúdo e crie um link para a pessoa escolhida.</p></div> : <div className="grid grid-cols-1 md:grid-cols-2 gap-4">{data.shares.map((share) => <article className="bg-card border border-border rounded-2xl p-5 space-y-3" key={share.id}>
          <div className="flex justify-between items-start gap-4"><div><h2 className="text-lg">Análise de {share.entry_count} reflexões</h2>{share.period && <p className="text-sm text-muted-foreground">{formatPeriodDate(share.period.start_date)} a {formatPeriodDate(share.period.end_date)}</p>}</div><span className={`sharing-status sharing-status-${share.state}`}>{STATUS_LABELS[share.state]}</span></div>
          {share.summary && <p className="text-sm text-muted-foreground line-clamp-3">{share.summary}</p>}
          <div className="text-xs text-muted-foreground"><p>Criado em {new Date(share.created_at).toLocaleString('pt-BR')}</p><p>Expira em {new Date(share.expires_at).toLocaleString('pt-BR')}</p></div>
          <div className="flex items-center justify-between gap-3 border-t border-border pt-3"><Link className="catalog-button catalog-hover-secondary" to="/inicio/analises"><ExternalLink size={14} />Ver análises</Link>{share.state === 'active' && <button type="button" className="catalog-button catalog-hover-destructive text-destructive" disabled={busyId === share.id} onClick={() => revoke(share)}>{busyId === share.id ? 'Revogando...' : 'Revogar acesso'}</button>}</div>
          {share.state === 'active' && (share.token ? <div className="sharing-link-panel"><label htmlFor={`share-link-${share.id}`}>Link de acesso</label><div className="sharing-link-row"><input id={`share-link-${share.id}`} readOnly value={buildContextShareLink(share.token)} onFocus={(event) => event.target.select()} /><button type="button" className="catalog-button catalog-hover-secondary" onClick={() => copyLink(share)}><Copy size={14} />Copiar</button></div></div> : <div className="sharing-legacy-link"><p>Este link foi criado antes do histórico permitir nova cópia. Gere outro endereço para substituí-lo.</p><button type="button" className="catalog-button catalog-hover-secondary" disabled={busyId === share.id} onClick={() => rotateLink(share)}><RefreshCw size={14} />{busyId === share.id ? 'Gerando...' : 'Gerar novo link'}</button></div>)}
        </article>)}</div>}
        <p className="text-xs text-muted-foreground">Somente links ativos podem ser copiados. Revogar encerra imediatamente o acesso compartilhado.</p>
      </div>
    </div>
  </div>
}


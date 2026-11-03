import { useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { useSearchParams } from 'react-router'
import { ChevronLeft, ChevronRight, ListFilter } from 'lucide-react'
import { listOperationalFailures, getOperationalFailure, reprocessOperationalFailure, getAnalysisProcessingSettings } from '../services/operationalFailuresApi'
import { clearSession } from '../services/authSession'

const PAGE_SIZE = 20
const SOURCES = { journal: 'Análise do diário', work_ingestion: 'Ingestão de obra', work_chunk: 'Trecho de obra', inbox: 'Recebimento de evento', outbox: 'Envio de evento' }
const STATES = { draft: 'Rascunho', pending_analysis: 'Nova análise pendente', analysis_failed: 'Falha na análise', analyzed: 'Analisada', deleted: 'Entrada excluída', pending: 'Pendente', processing: 'Em processamento', failed: 'Falha', completed: 'Concluído', pending_review: 'Aguardando revisão', processed: 'Processado', PENDING: 'Evento pendente', PROCESSING: 'Evento em processamento', SENT: 'Evento enviado', FAILED: 'Falha no evento' }
const EMPTY_FILTERS = { source: '', state: '', entity_id: '', since: '', until: '' }
const formatDate = value => value ? new Date(value).toLocaleString('pt-BR') : 'Não informado'

function FailureDetail({ source, id, onClose, onReprocessed }) {
  const [detail, setDetail] = useState(null)
  const [error, setError] = useState('')
  const [revision, setRevision] = useState(0)
  const [confirming, setConfirming] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [settings, setSettings] = useState(null)
  const [settingsError, setSettingsError] = useState('')
  const pending = useRef(false)
  const dialog = useRef(null)
  useEffect(() => {
    const element = dialog.current
    const previousOverflow = document.body.style.overflow
    element.showModal()
    document.body.style.overflow = 'hidden'
    return () => {
      element.close()
      document.body.style.overflow = previousOverflow
    }
  }, [])
  useEffect(() => {
    const controller = new AbortController()
    getOperationalFailure(source, id, { signal: controller.signal }).then(data => {
      if (!controller.signal.aborted) setDetail(data)
    }).catch(err => {
      if (controller.signal.aborted) return
      if (err.status === 401) clearSession()
      setError(err.status === 403 ? 'Acesso restrito a administradores.' : err.message)
    })
    return () => controller.abort()
  }, [source, id, revision])
  useEffect(() => {
    if (source !== 'journal') return
    const controller = new AbortController()
    getAnalysisProcessingSettings({ signal: controller.signal }).then(value => {
      if (!controller.signal.aborted) { setSettings(value); setSettingsError('') }
    }).catch(err => {
      if (!controller.signal.aborted) setSettingsError(err.message)
    })
    return () => controller.abort()
  }, [source, revision])
  async function reprocess() {
    if (pending.current || !confirming || !detail?.can_admin_reprocess || !settings) return
    pending.current = true
    setSubmitting(true)
    try {
      const result = await reprocessOperationalFailure(id, {
        ...settings, timeout_seconds: Number(settings.timeout_seconds), max_output_tokens: Number(settings.max_output_tokens),
      })
      onReprocessed(result.already_pending ? 'Esta análise já está na fila de processamento.' : 'Reprocessamento solicitado. A análise está na fila de processamento.')
    } catch (err) {
      if (err.status === 401) clearSession()
      setError(err.status === 403 ? 'Acesso restrito a administradores.' : err.message)
      setConfirming(false)
    } finally {
      pending.current = false
      setSubmitting(false)
    }
  }

  return createPortal(<dialog ref={dialog}
    aria-labelledby="failure-detail-title"
    className="m-auto w-[calc(100%-2rem)] max-w-3xl max-h-[90dvh] overflow-y-auto rounded-2xl border border-border bg-card p-5 md:p-8 text-foreground shadow-2xl backdrop:bg-black/50"
    onCancel={event => { event.preventDefault(); if (!pending.current) onClose() }}
    onClick={event => {
      if (event.target !== event.currentTarget || pending.current) return
      const bounds = event.currentTarget.getBoundingClientRect()
      if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) onClose()
    }}>
    <section className="space-y-4">
    <div className="flex flex-wrap items-center justify-between gap-3"><h2 id="failure-detail-title" className="text-xl font-medium">Detalhes da falha</h2><button type="button" autoFocus onClick={onClose} disabled={submitting} className="catalog-button">Fechar detalhes</button></div>
    {error ? <div role="alert"><p className="text-destructive">{error}</p><button type="button" className="underline mt-2" onClick={() => { setError(''); setDetail(null); setRevision(value => value + 1) }}>Tentar consultar novamente</button></div> : !detail ? <p role="status">Carregando detalhes...</p> : <>
      <p>{detail.message}</p>
      <dl className="grid sm:grid-cols-2 gap-4 break-words">
        {[
          ['Origem', SOURCES[detail.source]], ['Estado atual', STATES[detail.state] || detail.state],
          ['Código', detail.code], ['Tentativas registradas', detail.attempts ?? 'Não informado'],
          ['ID da falha', detail.id], ['ID do registro ou evento', detail.entity_id],
          ['ID relacionado', detail.related_id || 'Não se aplica'], ['Ocorrência registrada', formatDate(detail.occurred_at)],
          ['Atualização do registro', formatDate(detail.updated_at)],
        ].map(([label, value]) => <div key={label}><dt className="text-sm text-muted-foreground">{label}</dt><dd className="whitespace-pre-wrap break-all">{value}</dd></div>)}
      </dl>
      {detail.processing_settings && <div className="rounded-xl border border-border p-4 space-y-2">
        <h3 className="font-medium">Parâmetros da tentativa</h3>
        <p className="text-sm break-words">Modelo: {detail.processing_settings.model} · Tempo limite: {detail.processing_settings.timeout_seconds}s · Tokens de saída: {detail.processing_settings.max_output_tokens} · Raciocínio: {detail.processing_settings.reasoning_effort ?? 'Padrão do modelo'}</p>
      </div>}
      {detail.reprocess && <p>Solicitações do usuário: {detail.reprocess.user_used} de {detail.reprocess.user_limit}. {detail.reprocess.requires_admin && 'Somente a administração pode solicitar novas tentativas.'}</p>}
      {detail.can_admin_reprocess && (!confirming ? <button type="button" className="catalog-primary" onClick={() => setConfirming(true)}>Solicitar reprocessamento</button> : <form className="space-y-4 rounded-xl border border-border p-4" aria-label="Confirmar reprocessamento" onSubmit={event => { event.preventDefault(); reprocess() }}>
        <p>Escolha os parâmetros para esta tentativa. A configuração das outras análises e a cota do usuário permanecem iguais.</p>
        {settingsError ? <p role="alert" className="text-destructive">{settingsError} <button type="button" className="underline" onClick={() => { setSettingsError(''); setSettings(null); setRevision(value => value + 1) }}>Tentar novamente</button></p> : !settings ? <p role="status">Carregando parâmetros...</p> : <fieldset disabled={submitting} className="grid sm:grid-cols-2 gap-4">
          <label className="grid gap-1 text-sm">Modelo<input required maxLength={128} pattern="[A-Za-z0-9._:\-]+" className="w-full rounded-lg border border-border p-2 bg-background" value={settings.model} onChange={event => setSettings({ ...settings, model: event.target.value })} /></label>
          <label className="grid gap-1 text-sm">Tempo limite (segundos)<input required type="number" min="1" max="600" step="any" className="w-full rounded-lg border border-border p-2 bg-background" value={settings.timeout_seconds} onChange={event => setSettings({ ...settings, timeout_seconds: event.target.value })} /></label>
          <label className="grid gap-1 text-sm">Máximo de tokens de saída<input required type="number" min="1" max="128000" step="1" className="w-full rounded-lg border border-border p-2 bg-background" value={settings.max_output_tokens} onChange={event => setSettings({ ...settings, max_output_tokens: event.target.value })} /></label>
          <label className="grid gap-1 text-sm">Esforço de raciocínio<select className="w-full rounded-lg border border-border p-2 bg-background" value={settings.reasoning_effort ?? ''} onChange={event => setSettings({ ...settings, reasoning_effort: event.target.value || null })}>
            <option value="">Padrão do modelo</option>{['none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max'].map(value => <option key={value} value={value}>{value}</option>)}
          </select></label>
          <button type="button" className="catalog-button sm:col-span-2" onClick={() => setSettings({ ...settings, timeout_seconds: 60, max_output_tokens: 12000, reasoning_effort: 'low' })}>Usar 60 segundos e 12.000 tokens</button>
        </fieldset>}
        <p className="text-sm text-muted-foreground">Mais tempo e tokens podem ajudar a concluir a resposta. O modelo precisa estar disponível na conta e aceitar o esforço escolhido.</p>
        <div className="flex flex-wrap gap-3"><button className="catalog-primary" disabled={submitting || !settings || Boolean(settingsError)}>{submitting ? 'Solicitando...' : 'Confirmar reprocessamento'}</button><button type="button" className="catalog-button" disabled={submitting} onClick={() => setConfirming(false)}>Cancelar</button></div>
      </form>)}
      {detail.source === 'journal' && !detail.can_admin_reprocess && <p className="text-sm text-muted-foreground">Esta falha não está disponível para nova tentativa. Consulte o estado atual e a falha mais recente da entrada.</p>}
    </>}
    </section>
  </dialog>, document.body)
}

export function AdminFalhas() {
  const [searchParams, setSearchParams] = useSearchParams()
  const requestedSource = searchParams.get('source')
  const requestedFailureId = searchParams.get('failure_id')
  const [draft, setDraft] = useState(EMPTY_FILTERS)
  const [filters, setFilters] = useState(EMPTY_FILTERS)
  const [offset, setOffset] = useState(0)
  const [revision, setRevision] = useState(0)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selected, setSelected] = useState(() => (
    requestedSource && requestedFailureId
      ? { source: requestedSource, id: requestedFailureId }
      : null
  ))
  const [message, setMessage] = useState('')

  useEffect(() => {
    const controller = new AbortController()
    const parameters = { ...filters, limit: PAGE_SIZE, offset }
    for (const key of ['since', 'until']) if (parameters[key]) parameters[key] = new Date(parameters[key]).toISOString()
    listOperationalFailures(parameters, { signal: controller.signal }).then(result => {
      if (!controller.signal.aborted) setData(result)
    }).catch(err => {
      if (controller.signal.aborted) return
      if (err.status === 401) clearSession()
      setError(err.status === 403 ? 'Acesso restrito a administradores.' : err.message)
    }).finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [filters, offset, revision])

  function reload(nextOffset = offset) {
    setLoading(true)
    setError('')
    setSelected(null)
    setOffset(nextOffset)
    setRevision(value => value + 1)
  }

  function apply(event) {
    event.preventDefault()
    if (draft.since && draft.until && new Date(draft.since) > new Date(draft.until)) {
      setError('A data inicial deve ser anterior à data final.')
      return
    }
    setFilters({ ...draft, entity_id: draft.entity_id.trim() })
    reload(0)
  }

  function closeFailureDetail() {
    setSelected(null)
    if (!searchParams.has('source') && !searchParams.has('failure_id')) return
    const next = new URLSearchParams(searchParams)
    next.delete('source')
    next.delete('failure_id')
    setSearchParams(next, { replace: true })
  }

  const activeFilterCount = Object.values(filters).filter(Boolean).length
  const totalPages = Math.max(1, Math.ceil((data?.total || 0) / PAGE_SIZE))
  const currentPage = Math.min(totalPages, Math.floor(offset / PAGE_SIZE) + 1)

  return <div className="catalog-page admin-fixed-page">
    <header className="catalog-page-header catalog-page-intro">
      <div className="catalog-page-intro-copy"><h1 className="text-3xl">Falhas operacionais</h1><p>Consulte diagnósticos e estados dos processamentos registrados.</p></div>
      <div className="catalog-header-actions">
        <div className="passage-filter-control">
          <button type="button" className="catalog-button passage-filter-trigger" aria-haspopup="true"><ListFilter size={15} aria-hidden="true" />Filtros{activeFilterCount > 0 && <span>{activeFilterCount}</span>}</button>
          <form className="passage-filter-popover failure-filter-popover" onSubmit={apply} aria-label="Filtros de falhas operacionais">
            <label>Origem<select value={draft.source} onChange={event => setDraft({ ...draft, source: event.target.value })}><option value="">Todas as origens</option>{Object.entries(SOURCES).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
            <label>Estado atual<select value={draft.state} onChange={event => setDraft({ ...draft, state: event.target.value })}><option value="">Todos os estados</option>{Object.entries(STATES).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
            <label>ID do registro ou evento<input maxLength={128} value={draft.entity_id} onChange={event => setDraft({ ...draft, entity_id: event.target.value })} /></label>
            <label>Ocorrências a partir de<input type="datetime-local" value={draft.since} onChange={event => setDraft({ ...draft, since: event.target.value })} /></label>
            <label>Ocorrências até<input type="datetime-local" value={draft.until} onChange={event => setDraft({ ...draft, until: event.target.value })} /></label>
            <div className="failure-filter-actions"><button type="button" className="catalog-button catalog-hover-neutral" disabled={loading} onClick={() => { setDraft(EMPTY_FILTERS); setFilters(EMPTY_FILTERS); reload(0) }}>Limpar</button><button type="button" className="catalog-button catalog-hover-secondary" disabled={loading} onClick={() => reload()}>Atualizar</button><button className="catalog-primary catalog-hover-primary" disabled={loading}>Aplicar filtros</button></div>
            <p>Os filtros são aplicados ao consultar os registros operacionais.</p>
          </form>
        </div>
      </div>
    </header>
    <div className="admin-scroll-region">
    {message && <p role="status" className="text-primary">{message}</p>}
    {loading ? <p role="status">Carregando falhas...</p> : error ? <div role="alert"><p className="text-destructive">{error}</p><button type="button" onClick={() => reload()} className="underline">Tentar consultar novamente</button></div> : <>
      <div className="theme-list-toolbar">
        <p>{data?.total || 0} registros encontrados. O estado atual pode indicar recuperação após uma falha.</p>
        <nav aria-label="Paginação de falhas" className="theme-pagination">
          <button type="button" aria-label="Página anterior" disabled={loading || offset === 0} onClick={() => reload(Math.max(0, offset - PAGE_SIZE))}><ChevronLeft size={16} aria-hidden="true" /></button>
          <span>Página {currentPage} de {totalPages}</span>
          <button type="button" aria-label="Próxima página" disabled={loading || !data || currentPage === totalPages} onClick={() => reload(offset + PAGE_SIZE)}><ChevronRight size={16} aria-hidden="true" /></button>
        </nav>
      </div>
      {!data?.failures.length ? <div className="catalog-card">Nenhuma falha registrada para os filtros selecionados.</div> : <ul className="space-y-3">{data.failures.map(item => <li key={`${item.source}:${item.id}`} className="catalog-card space-y-2">
        <div className="flex flex-wrap justify-between gap-3"><h2>{SOURCES[item.source]}</h2><span>{STATES[item.state] || item.state}</span></div>
        <p>{item.message}</p><p className="text-sm text-muted-foreground">{formatDate(item.occurred_at)} · Código: {item.code} · Tentativas: {item.attempts ?? 'Não informado'}</p>
        <p className="text-sm break-all">Registro: {item.entity_id}</p>
        <button type="button" className="catalog-button" onClick={() => setSelected({ source: item.source, id: item.id })}>Ver detalhes</button>
      </li>)}</ul>}
    </>}
    {selected && <FailureDetail key={`${selected.source}:${selected.id}`} {...selected} onClose={closeFailureDetail} onReprocessed={text => { setMessage(text); reload() }} />}
    </div>
  </div>
}

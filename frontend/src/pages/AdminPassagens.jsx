import { useCallback, useEffect, useMemo, useState } from 'react'
import { Check, ChevronLeft, ChevronRight, ListFilter, Plus, RefreshCw, Search, Trash2, X } from 'lucide-react'
import { useSearchParams } from 'react-router'
import { createPassage, deletePassage, getPassage, listPassages, listThemes, listWorks, passageAction, updatePassage } from '../services/catalogApi'
import { readCatalog, replaceCatalog } from '../services/catalogState'
import { filterPassages } from '../services/passageFilters'

const statuses = { PENDING_REVIEW: 'Pendente de revisão', APPROVED: 'Aprovada', REJECTED: 'Rejeitada', ACTIVE: 'Ativa', INACTIVE: 'Inativa' }
const THEME_PAGE_SIZE = 5

function passageActions(status) {
  if (status === 'PENDING_REVIEW') return [['approve', 'Aprovar'], ['reject', 'Rejeitar']]
  if (status === 'APPROVED') return [['activate', 'Ativar'], ['deactivate', 'Desativar']]
  if (status === 'ACTIVE') return [['deactivate', 'Desativar']]
  if (status === 'INACTIVE') return [['activate', 'Ativar']]
  return []
}

function PassageCard({ passage, work, busy, editing, onEdit, onAction }) {
  return <article className="catalog-card passage-review-card" aria-busy={busy}>
    <div className="passage-card-heading">
      <div className="passage-heading-copy">
        <div className="passage-title-row">
          <h2>{work?.title || 'Obra não encontrada no catálogo'}</h2>
          <span className="passage-metadata">{passage.locator} · {passage.source === 'ai' ? 'Sugestão da IA' : 'Criação manual'} · Prioridade {passage.priority}</span>
        </div>
        <p>{work?.author?.name || `ID da obra: ${passage.work_id}`}</p>
      </div>
      <span className={`catalog-badge passage-status passage-status-${passage.status.toLowerCase()}`}>{statuses[passage.status] || passage.status}</span>
    </div>
    <div className="passage-theme-list">{passage.themes?.map((theme) => <span className="catalog-badge" key={theme.theme_id}>{theme.label || theme.theme_id} · {Math.round(theme.confidence * 100)}%</span>)}</div>
    <section className="passage-original"><h3>Passagem original</h3><blockquote className="catalog-quote">“{passage.short_text}”</blockquote></section>
    <div className="passage-explanation-grid">
      <section><h3>Paráfrase</h3><p className="whitespace-pre-wrap">{passage.paraphrase}</p></section>
      <section><h3>Por que foi associada</h3><p className="whitespace-pre-wrap">{passage.interpretation_note}</p></section>
    </div>
    <div className="passage-card-actions">
      <button className="catalog-button passage-action-edit" disabled={busy || !!editing} onClick={() => onEdit(passage)}>Editar</button>
      <div className="passage-card-state-actions">{passageActions(passage.status).map(([type, label]) => <button key={type} className={`${type === 'approve' || type === 'activate' ? 'catalog-primary passage-action-approve' : 'catalog-button'}${type === 'reject' ? ' passage-action-reject' : ''}`} disabled={busy} onClick={() => onAction(passage, type)}>{type === 'approve' && <Check size={15} aria-hidden="true" />}{type === 'reject' && <X size={15} aria-hidden="true" />}{label}</button>)}
        {['PENDING_REVIEW', 'APPROVED', 'ACTIVE'].includes(passage.status) && <button className="catalog-button passage-action-remove" disabled={busy} onClick={() => onAction(passage, 'delete')}><Trash2 size={15} aria-hidden="true" />Retirar do catálogo</button>}
      </div>
    </div>
  </article>
}

export function AdminPassagens() {
  const [initialCatalog] = useState(readCatalog)
  const [params, setParams] = useSearchParams()
  const filters = {
    status: params.has('status') ? params.get('status') : 'PENDING_REVIEW',
    work_id: params.get('work_id') || '',
    ingestion_id: params.get('ingestion_id') || '',
    work_title: params.get('work_title') || '',
    author_name: params.get('author_name') || '',
    confidence_range: params.get('confidence_range') || '',
  }
  const [passages, setPassages] = useState([])
  const [themes, setThemes] = useState(initialCatalog.themes)
  const [works, setWorks] = useState(initialCatalog.works)
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [editing, setEditing] = useState(null)
  const [poll, setPoll] = useState(false)
  const [themeSearch, setThemeSearch] = useState('')
  const [themePage, setThemePage] = useState(1)

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const data = await listPassages()
      setPassages(data.passages || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [setError, setLoading, setPassages])

  useEffect(() => {
    let active = true
    listPassages().then((data) => {
      if (active) setPassages(data.passages || [])
    }).catch((err) => {
      if (active) setError(err.message)
    }).finally(() => {
      if (active) setLoading(false)
    })
    return () => { active = false }
  }, [])

  useEffect(() => {
    let active = true
    const requests = []
    if (!initialCatalog.loaded.themes) requests.push({ kind: 'themes', request: listThemes().then((data) => data.themes || []) })
    if (!initialCatalog.loaded.works) requests.push({ kind: 'works', request: listWorks().then((data) => data.works || []) })
    if (!requests.length) return () => { active = false }
    Promise.allSettled(requests.map(({ request }) => request)).then((results) => {
      if (!active) return
      results.forEach((result, index) => {
        const { kind } = requests[index]
        if (result.status === 'rejected') {
          setError(result.reason.message)
          return
        }
        if (kind === 'themes') setThemes(result.value)
        else setWorks(result.value)
        replaceCatalog(kind, result.value)
      })
    })
    return () => { active = false }
  }, [initialCatalog])

  useEffect(() => {
    if (!poll || busy || editing) return undefined
    const timer = setInterval(load, 10000)
    return () => clearInterval(timer)
  }, [poll, busy, editing, load])

  const worksById = useMemo(() => new Map(works.map((work) => [work.id, work])), [works])
  const visiblePassages = filterPassages(passages, filters, works)
  const activeFilterCount = [filters.status, filters.work_id, filters.ingestion_id, filters.work_title, filters.author_name, filters.confidence_range].filter(Boolean).length
  const activeThemes = themes.filter((theme) => theme.is_active)
  const normalizedThemeSearch = themeSearch.trim().toLowerCase()
  const filteredThemes = activeThemes.filter((theme) => `${theme.label} ${theme.slug || ''}`.toLowerCase().includes(normalizedThemeSearch))
  const themeTotalPages = Math.max(1, Math.ceil(filteredThemes.length / THEME_PAGE_SIZE))
  const currentThemePage = Math.min(themePage, themeTotalPages)
  const visibleThemes = filteredThemes.slice((currentThemePage - 1) * THEME_PAGE_SIZE, currentThemePage * THEME_PAGE_SIZE)

  function updateFilter(name, value) {
    const next = new URLSearchParams(params)
    if (value || name === 'status') next.set(name, value)
    else next.delete(name)
    setParams(next, { replace: true })
  }

  async function action(passage, type) {
    if (type === 'reject' && !window.confirm('Rejeitar esta passagem? Ela não poderá ser aprovada novamente pelo fluxo atual.')) return
    if (type === 'delete' && !window.confirm('Retirar esta passagem? Pendentes serão rejeitadas; aprovadas ou ativas serão desativadas.')) return
    setBusy(true)
    setError('')
    setMessage('')
    try {
      if (type === 'delete') await deletePassage(passage.id)
      else await passageAction(passage.id, type)
      setMessage('Passagem atualizada.')
      await load()
      if (['activate', 'deactivate', 'delete'].includes(type)) {
        try {
          const workData = await listWorks()
          const refreshedWorks = workData.works || []
          setWorks(refreshedWorks)
          replaceCatalog('works', refreshedWorks)
        } catch {
          setError('A passagem foi atualizada, mas não foi possível atualizar agora o status das obras em cache.')
        }
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  async function edit(passage) {
    setBusy(true)
    setError('')
    try {
      const full = await getPassage(passage.id)
      setThemeSearch('')
      setThemePage(1)
      setEditing({ ...full, originalThemes: full.themes.map(({ theme_id, confidence }) => ({ theme_id, confidence })) })
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  async function save(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    const data = Object.fromEntries(new FormData(event.currentTarget))
    try {
      const fields = { locator: data.locator, paraphrase: data.paraphrase, priority: Number(data.priority), themes: editing.themes.map((theme) => ({ theme_id: theme.theme_id, confidence: Number(theme.confidence) })) }
      if (!editing.id) {
        fields.short_text = data.short_text
        fields.interpretation_note = data.interpretation_note
      }
      if (data.start_page || data.end_page) {
        if (!data.start_page || !data.end_page || Number(data.end_page) < Number(data.start_page)) throw new Error('Informe as duas páginas, com a página final maior ou igual à inicial.')
        fields.start_page = Number(data.start_page)
        fields.end_page = Number(data.end_page)
      }
      if (editing.id) {
        const changed = Object.fromEntries(Object.entries(fields).filter(([key, value]) => JSON.stringify(value) !== JSON.stringify(key === 'themes' ? editing.originalThemes : editing[key])))
        if ('start_page' in changed || 'end_page' in changed) { changed.start_page = fields.start_page; changed.end_page = fields.end_page }
        if (changed.themes?.some((item) => !themes.some((theme) => theme.id === item.theme_id && theme.is_active))) throw new Error('Remova os temas indisponíveis antes de salvar as associações.')
        if (Object.keys(changed).length) await updatePassage(editing.id, changed)
      } else {
        await createPassage({ ...fields, work_id: data.work_id })
      }
      setEditing(null)
      setMessage('Passagem salva.')
      await load()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return <div className="catalog-page passages-page">
    <div className="passage-fixed-region">
      <header className="catalog-page-header passage-page-header">
      <h1>Passagens que convidam a pensar</h1>
      <div className="catalog-header-actions passage-header-actions">
        <button className="catalog-primary catalog-hover-primary" disabled={busy || !!editing} onClick={() => { setThemeSearch(''); setThemePage(1); setEditing({ themes: [], priority: 0 }) }}><Plus size={16} aria-hidden="true" />Nova passagem</button>
        <button className="catalog-button catalog-hover-secondary inline-flex items-center gap-2" disabled={busy || loading} onClick={load}><RefreshCw size={15} aria-hidden="true" />{loading ? 'Atualizando…' : 'Atualizar'}</button>
        <label className="passage-auto-refresh flex"><input type="checkbox" checked={poll} onChange={(event) => setPoll(event.target.checked)} /><span>Atualização automática</span></label>
        <div className="passage-filter-control">
          <button type="button" className="catalog-button passage-filter-trigger"><ListFilter size={15} aria-hidden="true" />Filtros{activeFilterCount > 0 && <span>{activeFilterCount}</span>}</button>
          <div className="passage-filter-popover" role="group" aria-label="Filtros locais de passagens">
            <label>Status<select value={filters.status} onChange={(event) => updateFilter('status', event.target.value)}><option value="">Todos</option>{Object.entries(statuses).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></label>
            <label>Nome da obra<input value={filters.work_title} onChange={(event) => updateFilter('work_title', event.target.value)} placeholder="Digite todo ou parte do título" /></label>
            <label>Nome do autor<input value={filters.author_name} onChange={(event) => updateFilter('author_name', event.target.value)} placeholder="Digite todo ou parte do nome" /></label>
            <label>ID da obra<input value={filters.work_id} onChange={(event) => updateFilter('work_id', event.target.value)} placeholder="Digite todo ou parte do ID" /></label>
            <label>ID da ingestão<input value={filters.ingestion_id} onChange={(event) => updateFilter('ingestion_id', event.target.value)} placeholder="Digite todo ou parte do ID" /></label>
            <label>Maior confiança entre os temas<select value={filters.confidence_range} onChange={(event) => updateFilter('confidence_range', event.target.value)}><option value="">Todas as faixas</option><option value="high">80% a 100%</option><option value="medium">70% a 79%</option></select></label>
            <div className="passage-filter-actions"><button type="button" className="catalog-button catalog-hover-neutral passage-filter-clear" onClick={() => setParams({ status: '' }, { replace: true })}>Limpar</button></div>
            <p>Os filtros são aplicados nesta página, sem novas consultas ao banco.</p>
          </div>
        </div>
      </div>
      </header>
      {error && <p role="alert" className="text-destructive">{error}</p>}{message && <p role="status">{message}</p>}
      <p className="passage-results-summary" role="status">{visiblePassages.length} de {passages.length} passagens exibidas. Aprovar não ativa a passagem.</p>
    </div>
    <div className="passage-scroll-region">
      {editing && <form onSubmit={save} className="catalog-card passage-edit-form"><fieldset disabled={busy}><div className="passage-edit-heading"><h2>{editing.id ? 'Editar passagem' : 'Nova passagem manual'}</h2><div className="passage-edit-actions"><button className="catalog-primary">Salvar passagem</button><button type="button" className="catalog-button" onClick={() => setEditing(null)}>Cancelar</button></div></div>{!editing.id && <label>Obra<select name="work_id" required><option value="">Selecione</option>{works.map((work) => <option key={work.id} value={work.id}>{work.title} — {work.author?.name}</option>)}</select></label>}
      {editing.id ? <div className="passage-protected-content"><section><h3>Passagem original</h3><blockquote>{editing.short_text}</blockquote><p>Trecho preservado exatamente como registrado a partir da obra.</p></section><label>Paráfrase<textarea name="paraphrase" defaultValue={editing.paraphrase || ''} required rows={3} /></label><section><h3>Por que foi associada</h3><p>{editing.interpretation_note}</p><small>Justificativa original produzida durante a análise da IA.</small></section></div> : ['short_text', 'paraphrase', 'interpretation_note'].map((name, index) => <label key={name}>{['Passagem original', 'Paráfrase', 'Por que foi associada'][index]}<textarea name={name} defaultValue={editing[name] || ''} required rows={3} /></label>)}
      <div className="catalog-filters">{[['locator', 'Localização', 'text'], ['priority', 'Prioridade', 'number'], ['start_page', 'Página inicial', 'number'], ['end_page', 'Página final', 'number']].map(([name, label, type]) => <label key={name}>{label}<input name={name} type={type} defaultValue={editing[name] ?? ''} required={name === 'locator' || name === 'priority'} min={name.includes('page') ? 1 : undefined} /></label>)}</div>
      <section className="passage-theme-picker">
        <div className="passage-theme-picker-heading"><div><h3>Temas ativos</h3><p>{editing.themes.length} {editing.themes.length === 1 ? 'tema selecionado' : 'temas selecionados'}</p></div><div className="passage-theme-picker-tools">
          <div className="passage-theme-search-control"><button type="button" className="catalog-button passage-theme-search-trigger"><Search size={14} />Pesquisar</button><div className="passage-theme-search-popover" role="search"><label htmlFor="passage-theme-search">Pesquisar tema</label><input id="passage-theme-search" value={themeSearch} onChange={(event) => { setThemeSearch(event.target.value); setThemePage(1) }} placeholder="Nome ou slug do tema" />{themeSearch && <button type="button" className="catalog-button" onClick={() => { setThemeSearch(''); setThemePage(1) }}>Limpar</button>}</div></div>
          <nav className="passage-theme-pagination" aria-label="Paginação dos temas disponíveis"><button type="button" aria-label="Temas anteriores" disabled={currentThemePage === 1} onClick={() => setThemePage(currentThemePage - 1)}><ChevronLeft size={14} /></button><span>{currentThemePage}/{themeTotalPages}</span><button type="button" aria-label="Próximos temas" disabled={currentThemePage === themeTotalPages} onClick={() => setThemePage(currentThemePage + 1)}><ChevronRight size={14} /></button></nav>
        </div></div>
        <div className="passage-theme-options">{visibleThemes.map((theme) => {
          const selected = editing.themes.find((item) => item.theme_id === theme.id)
          return <div className="passage-theme-option" key={theme.id}><label className="flex items-center gap-2"><input type="checkbox" checked={!!selected} onChange={(event) => setEditing({ ...editing, originalThemes: editing.originalThemes || editing.themes, themes: event.target.checked ? [...editing.themes, { theme_id: theme.id, confidence: 1 }] : editing.themes.filter((item) => item.theme_id !== theme.id) })} /><span>{theme.label}</span></label>{selected && <label className="passage-theme-confidence flex">Confiança<input aria-label={`Confiança em ${theme.label}`} type="number" min="0" max="1" step="0.01" required value={selected.confidence} onChange={(event) => setEditing({ ...editing, originalThemes: editing.originalThemes || editing.themes, themes: editing.themes.map((item) => item.theme_id === theme.id ? { ...item, confidence: event.target.value } : item) })} /></label>}</div>
        })}{!visibleThemes.length && <p className="passage-theme-empty">Nenhum tema encontrado nesta pesquisa.</p>}</div>
        {editing.themes.filter((item) => !themes.some((theme) => theme.id === item.theme_id && theme.is_active)).map((item) => <label key={item.theme_id} className="passage-theme-unavailable"><input type="checkbox" checked onChange={() => setEditing({ ...editing, originalThemes: editing.originalThemes || editing.themes, themes: editing.themes.filter((theme) => theme.theme_id !== item.theme_id) })} />{item.label || item.theme_id} (indisponível; remova para alterar)</label>)}
      </section>
        <div className="passage-edit-actions passage-edit-actions-bottom"><button className="catalog-primary">Salvar passagem</button><button type="button" className="catalog-button" onClick={() => setEditing(null)}>Cancelar</button></div></fieldset></form>}
      {!loading && !visiblePassages.length && <div className="catalog-card"><h2>Nenhuma passagem para estes filtros</h2><p>Altere os filtros locais ou atualize a lista para buscar mudanças recentes.</p></div>}
      {visiblePassages.map((passage) => <PassageCard key={passage.id} passage={passage} work={worksById.get(passage.work_id)} busy={busy} editing={editing} onEdit={edit} onAction={action} />)}
    </div>
  </div>
}

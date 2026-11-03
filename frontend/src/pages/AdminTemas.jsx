import { useCallback, useEffect, useState } from 'react'
import { ChevronLeft, ChevronRight, Eye, Loader2, Plus, RefreshCw, Search, X } from 'lucide-react'
import { createTheme, deleteTheme, getTheme, updateTheme } from '../services/catalogApi'
import { clearSession } from '../services/authSession'
import { refreshThemesCache } from '../services/catalogCache'
import { readCatalog } from '../services/catalogState'

const PAGE_SIZE = 20
const THEME_COLOR_FALLBACK = '#8B5CF6'
const empty = { label: '', description: '', is_active: true }

export function AdminTemas() {
  const [initialCatalog] = useState(readCatalog)
  const [themes, setThemes] = useState(initialCatalog.themes)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [selected, setSelected] = useState(null)
  const [form, setForm] = useState(null)
  const [draft, setDraft] = useState(empty)
  const [loading, setLoading] = useState(!initialCatalog.loaded.themes)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const nextThemes = await refreshThemesCache()
      setThemes(nextThemes)
      return nextThemes
    } catch (err) {
      if (err.status === 401) clearSession()
      setError(err.message)
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (initialCatalog.loaded.themes) return undefined
    let active = true
    refreshThemesCache().then((nextThemes) => {
      if (active) setThemes(nextThemes)
    }).catch((err) => {
      if (!active) return
      if (err.status === 401) clearSession()
      setError(err.message)
    }).finally(() => {
      if (active) setLoading(false)
    })
    return () => { active = false }
  }, [initialCatalog])

  async function save(event) {
    event.preventDefault()
    if (form?.id && !window.confirm(`Confirmar as alterações no tema "${form.label}"?`)) return
    setError('')
    setBusy(true)
    try {
      if (form?.id) {
        const changed = Object.fromEntries(
          Object.entries(draft).filter(
            ([key, value]) => value !== form[key],
          ),
        )
        if (Object.keys(changed).length) await updateTheme(form.id, changed)
      } else {
        await createTheme(draft)
      }
      setForm(null)
      setDraft(empty)
      await load()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  async function view(theme) {
    setError('')
    setBusy(true)
    try {
      setSelected(await getTheme(theme.id))
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  function edit(theme) {
    setSelected(null)
    setForm(theme)
    setDraft({
      label: theme.label,
      description: theme.description,
      is_active: theme.is_active,
    })
  }

  async function remove(theme) {
    if (!window.confirm(`Excluir permanentemente o tema "${theme.label}"?`)) return
    setBusy(true)
    setError('')
    try {
      await deleteTheme(theme.id)
      setSelected(null)
      await load()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const normalizedSearch = search.trim().toLowerCase()
  const filtered = themes.filter((theme) => `${theme.label} ${theme.slug || ''}`.toLowerCase().includes(normalizedSearch))
  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))
  const currentPage = Math.min(page, totalPages)
  const pageThemes = filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE)
  const firstResult = filtered.length ? (currentPage - 1) * PAGE_SIZE + 1 : 0
  const lastResult = Math.min(currentPage * PAGE_SIZE, filtered.length)

  return <div className="admin-fixed-shell relative min-h-screen bg-background p-5 md:p-8"><div className="admin-fixed-page max-w-6xl mx-auto" aria-busy={loading || busy}>
    {(loading || busy) && <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/60 backdrop-blur-sm" role="status" aria-label="Carregando"><Loader2 className="h-10 w-10 animate-spin text-primary" /></div>}
    <header className="catalog-page-header catalog-page-intro">
      <div className="catalog-page-intro-copy"><h1 className="text-3xl">Gerenciar temas</h1><p>Organize os temas que orientam as análises e associações realizadas pela IA.</p></div>
      <div className="catalog-header-actions">
        <button disabled={loading || busy} onClick={() => { setSelected(null); setForm({}); setDraft(empty) }} className="catalog-primary catalog-hover-primary"><Plus size={16} />Novo tema</button>
        <div className="theme-search-control">
          <button type="button" className="catalog-button theme-search-trigger"><Search size={15} />Pesquisar{search && <span aria-label="Pesquisa ativa" />}</button>
          <div className="theme-search-popover" role="search">
            <label htmlFor="theme-search">Pesquisar tema</label>
            <input id="theme-search" value={search} onChange={(event) => { setSearch(event.target.value); setPage(1) }} placeholder="Digite o nome ou slug" />
            {search && <button type="button" className="catalog-button theme-search-clear" onClick={() => { setSearch(''); setPage(1) }}>Limpar pesquisa</button>}
          </div>
        </div>
        <button disabled={loading || busy} onClick={load} className="catalog-button catalog-hover-secondary"><RefreshCw size={15} />Atualizar temas</button>
      </div>
    </header>

    <div className="admin-scroll-region">
    {form !== null && <form onSubmit={save} className="bg-card border border-border rounded-2xl p-6 space-y-4"><h2 className="text-xl">{form?.id ? 'Editar tema' : 'Novo tema'}</h2><input required minLength={3} maxLength={50} placeholder="Nome do tema" value={draft.label} onChange={(event) => setDraft({ ...draft, label: event.target.value })} className="w-full px-4 py-3 bg-input-background rounded-lg border border-border" /><textarea required minLength={3} maxLength={255} placeholder="Descrição" value={draft.description} onChange={(event) => setDraft({ ...draft, description: event.target.value })} className="w-full px-4 py-3 bg-input-background rounded-lg border border-border" /><p className="text-sm text-muted-foreground">A cor de destaque será definida automaticamente pelo sistema.</p><label className="flex gap-2"><input type="checkbox" checked={draft.is_active} onChange={(event) => setDraft({ ...draft, is_active: event.target.checked })} />Tema ativo</label><div className="flex gap-3"><button className="catalog-primary">Salvar tema</button><button type="button" onClick={() => setForm(null)} className="catalog-button">Cancelar</button></div></form>}

    {error && <p role="alert" className="text-destructive">{error}</p>}

    <div className="theme-list-toolbar">
      <p>{firstResult}–{lastResult} de {filtered.length} temas{search ? ' encontrados' : ''}</p>
      <nav className="theme-pagination" aria-label="Paginação dos temas">
        <button type="button" aria-label="Página anterior" disabled={currentPage === 1} onClick={() => setPage(currentPage - 1)}><ChevronLeft size={16} /></button>
        <span>Página {currentPage} de {totalPages}</span>
        <button type="button" aria-label="Próxima página" disabled={currentPage === totalPages} onClick={() => setPage(currentPage + 1)}><ChevronRight size={16} /></button>
      </nav>
    </div>

    {!loading && pageThemes.length > 0 && <section className="theme-card-grid" aria-label="Temas cadastrados">{pageThemes.map((theme) => <button type="button" className="theme-compact-card" key={theme.id} style={{ '--theme-color': theme.color || THEME_COLOR_FALLBACK }} onClick={() => view(theme)} aria-label={`Ver detalhes e editar ${theme.label}`}>
      <div className="theme-compact-copy"><div className="theme-compact-title"><span className="theme-color-dot" style={{ backgroundColor: theme.color || THEME_COLOR_FALLBACK }} aria-label={`Cor ${theme.color || THEME_COLOR_FALLBACK}`} /><h2>{theme.label}</h2></div><span className={`theme-status theme-status-${theme.is_active ? 'active' : 'inactive'}`}>{theme.is_active ? 'Ativo' : 'Inativo'}</span></div>
      <span className="theme-view-button" title="Ver detalhes"><Eye size={17} aria-hidden="true" /></span>
    </button>)}</section>}
    {!loading && !pageThemes.length && <div className="catalog-card catalog-empty-state"><Search size={32} /><h2>Nenhum tema encontrado</h2><p>Altere a pesquisa ou cadastre um novo tema.</p></div>}
    </div>

    {selected && <div className="theme-detail-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setSelected(null) }}><section className="theme-detail-modal" role="dialog" aria-modal="true" aria-labelledby="theme-detail-title">
      <button type="button" className="theme-detail-close" onClick={() => setSelected(null)} aria-label="Fechar detalhes"><X size={18} /></button>
      <div className="theme-detail-heading"><div className="theme-detail-title"><span className="theme-color-dot" style={{ backgroundColor: selected.color || THEME_COLOR_FALLBACK }} /><h2 id="theme-detail-title">{selected.label}</h2></div><span className={`theme-status theme-status-${selected.is_active ? 'active' : 'inactive'}`}>{selected.is_active ? 'Ativo' : 'Inativo'}</span></div>
      <dl className="theme-detail-list"><div><dt>Slug</dt><dd>{selected.slug}</dd></div><div><dt>Descrição</dt><dd>{selected.description}</dd></div><div><dt>Cor gerada pelo sistema</dt><dd>{selected.color || THEME_COLOR_FALLBACK}</dd></div></dl>
      <div className="theme-detail-actions"><button type="button" className="catalog-button catalog-destructive-outline" onClick={() => remove(selected)}>Excluir tema</button><button type="button" className="catalog-primary" onClick={() => edit(selected)}>Editar tema</button></div>
    </section></div>}
  </div></div>
}

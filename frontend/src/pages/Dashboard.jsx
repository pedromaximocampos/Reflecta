import {
  AlertCircle, BarChart3, BookOpen, Calendar, CheckCircle, ChevronLeft,
  ChevronRight, Clock, FileText, Plus, Sparkles, Tags,
} from 'lucide-react'
import { Link } from 'react-router'
import { useEffect, useState } from 'react'
import { listJournalEntries } from '../services/journalApi'
import { getDashboardSummary, listWorkRecommendations } from '../services/dashboardApi'
import { clearSession } from '../services/authSession'
import { RecommendationWorkCard } from '../components/RecommendationWorkCard'

const ENTRY_PAGE_SIZE = 4
const RECOMMENDATION_PAGE_SIZE = 3

function getStatus(status) {
  if (['analyzed', 'completed'].includes(status)) return { icon: <CheckCircle className="w-5 h-5 text-primary" />, label: 'Analisada' }
  if (['analysis_failed', 'failed', 'error'].includes(status)) return { icon: <AlertCircle className="w-5 h-5 text-destructive" />, label: 'Falha na análise' }
  if (status === 'draft') return { icon: <BookOpen className="w-5 h-5 text-muted-foreground" />, label: 'Rascunho' }
  return { icon: <Clock className="w-5 h-5 text-secondary" />, label: 'Aguardando análise' }
}

function getUserName() {
  try {
    const user = JSON.parse(sessionStorage.getItem('auth_user'))
    return user?.name || user?.username || 'visitante'
  } catch {
    return 'visitante'
  }
}

function Pager({ label, page, hasPrevious, hasNext, onPrevious, onNext }) {
  return <nav aria-label={label} className="theme-pagination">
    <button type="button" aria-label="Página anterior" disabled={!hasPrevious} onClick={onPrevious}><ChevronLeft size={15} /></button>
    <span>Página {page}</span>
    <button type="button" aria-label="Próxima página" disabled={!hasNext} onClick={onNext}><ChevronRight size={15} /></button>
  </nav>
}

export function Dashboard() {
  const userName = getUserName()
  const [entryPage, setEntryPage] = useState(1)
  const [entries, setEntries] = useState([])
  const [entriesHasNext, setEntriesHasNext] = useState(false)
  const [loadingEntries, setLoadingEntries] = useState(true)
  const [entriesError, setEntriesError] = useState(null)
  const [summary, setSummary] = useState(null)
  const [summaryError, setSummaryError] = useState(null)
  const [recommendationPage, setRecommendationPage] = useState(1)
  const [recommendations, setRecommendations] = useState([])
  const [recommendationTotal, setRecommendationTotal] = useState(0)
  const [recommendationError, setRecommendationError] = useState(null)
  const [loadingRecommendations, setLoadingRecommendations] = useState(true)

  useEffect(() => {
    const controller = new AbortController()
    listJournalEntries({ limit: ENTRY_PAGE_SIZE + 1, offset: (entryPage - 1) * ENTRY_PAGE_SIZE, signal: controller.signal })
      .then((data) => {
        const loaded = data.entries || []
        setEntries(loaded.slice(0, ENTRY_PAGE_SIZE))
        setEntriesHasNext(loaded.length > ENTRY_PAGE_SIZE)
      })
      .catch((error) => {
        if (error.name === 'AbortError') return
        if (error.status === 401) clearSession()
        setEntriesError(error)
      })
      .finally(() => { if (!controller.signal.aborted) setLoadingEntries(false) })
    return () => controller.abort()
  }, [entryPage])

  useEffect(() => {
    const controller = new AbortController()
    getDashboardSummary({ signal: controller.signal }).then(setSummary).catch((error) => {
      if (error.name === 'AbortError') return
      if (error.status === 401) clearSession()
      setSummaryError(error)
    })
    return () => controller.abort()
  }, [])

  useEffect(() => {
    const controller = new AbortController()
    listWorkRecommendations({ limit: RECOMMENDATION_PAGE_SIZE, offset: (recommendationPage - 1) * RECOMMENDATION_PAGE_SIZE, signal: controller.signal })
      .then((data) => {
        setRecommendations(data.recommendations || [])
        setRecommendationTotal(data.total || 0)
      })
      .catch((error) => {
        if (error.name === 'AbortError') return
        if (error.status === 401) clearSession()
        setRecommendationError(error)
      })
      .finally(() => { if (!controller.signal.aborted) setLoadingRecommendations(false) })
    return () => controller.abort()
  }, [recommendationPage])

  const recommendationPages = Math.max(1, Math.ceil(recommendationTotal / RECOMMENDATION_PAGE_SIZE))
  const recurringThemes = (summary?.recurring_themes || []).slice(0, 4)
  const maxThemeCount = Math.max(1, ...recurringThemes.map((theme) => theme.reflection_count))
  const changeEntryPage = (nextPage) => {
    setLoadingEntries(true)
    setEntriesError(null)
    setEntryPage(nextPage)
  }
  const changeRecommendationPage = (nextPage) => {
    setLoadingRecommendations(true)
    setRecommendationError(null)
    setRecommendationPage(nextPage)
  }

  return <div className="dashboard-page admin-fixed-shell bg-background p-5 md:p-8">
    <div className="dashboard-fixed-page max-w-7xl mx-auto">
    <div className="flex md:hidden items-center gap-3"><BookOpen className="w-8 h-8 text-primary" strokeWidth={1.5} /><span className="text-2xl text-primary">Reflecta</span></div>
    <header className="catalog-page-header catalog-page-intro">
      <div className="catalog-page-intro-copy"><h1 className="text-3xl">Bem-vindo de volta, {userName}</h1><p>Continue sua jornada de autoconhecimento.</p></div>
      <div className="catalog-header-actions"><Link to="/inicio/diario" className="catalog-primary catalog-hover-primary"><Plus size={16} />Nova reflexão</Link><Link to="/inicio/reflexoes" className="catalog-button catalog-hover-secondary"><FileText size={15} />Minhas reflexões</Link></div>
    </header>

    <section className="dashboard-metrics grid grid-cols-1 sm:grid-cols-3 gap-4" aria-label="Resumo das reflexões">
      {[
        ['Reflexões neste mês', summary?.metrics?.reflections_this_month, Calendar],
        ['Temas explorados', summary?.metrics?.explored_themes, BarChart3],
        ['Reflexões registradas', summary?.metrics?.total_reflections, FileText],
      ].map(([label, value, Icon]) => <div className="bg-card rounded-2xl border border-border px-5 py-4" key={label}><div className="flex items-center justify-between gap-4"><div><p className="text-sm text-muted-foreground">{label}</p><strong className="text-2xl">{summaryError ? '—' : value ?? '…'}</strong></div><Icon className="w-5 h-5 text-primary" /></div></div>)}
    </section>

    <div className="dashboard-content-region">
    <div className="dashboard-primary-grid grid grid-cols-1 lg:grid-cols-2 gap-6">
      <section className="dashboard-primary-card bg-card rounded-2xl border border-border p-6">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-5"><div className="flex items-center gap-3"><Calendar className="w-5 h-5 text-primary" /><h2 className="text-xl">Histórico de reflexões</h2></div><Pager label="Paginação das reflexões" page={entryPage} hasPrevious={entryPage > 1} hasNext={entriesHasNext} onPrevious={() => changeEntryPage(entryPage - 1)} onNext={() => changeEntryPage(entryPage + 1)} /></div>
        {loadingEntries ? <p role="status">Carregando histórico...</p> : entriesError ? <p role="alert" className="text-destructive">Não foi possível carregar o histórico.</p> : !entries.length ? <p className="text-muted-foreground">Suas reflexões salvas aparecerão aqui.</p> : <div className="space-y-3">{entries.map((entry) => {
          const status = getStatus(entry.status)
          const date = entry.entry_date ? entry.entry_date.split('-').reverse().join('/') : ''
          return <Link to={`/inicio/reflexoes/${entry.id}`} key={entry.id} className="block p-4 bg-muted rounded-xl hover:bg-accent transition-colors"><div className="flex items-start justify-between gap-4"><div className="min-w-0"><h3 className="mb-1 truncate">{entry.title || 'Reflexão sem título'}</h3><p className="text-sm text-muted-foreground">{date}</p></div><div className="flex items-center gap-2 text-sm shrink-0">{status.icon}<span className="hidden sm:inline">{status.label}</span></div></div></Link>
        })}</div>}
      </section>

      <section className="dashboard-primary-card bg-card rounded-2xl border border-border p-6">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-5"><div className="flex items-center gap-3"><Sparkles className="w-5 h-5 text-primary" /><div><h2 className="text-xl">Obras que têm a ver com você</h2><p className="text-xs text-muted-foreground">Baseadas nos temas presentes em suas análises.</p></div></div><Pager label="Paginação das recomendações" page={recommendationPage} hasPrevious={recommendationPage > 1} hasNext={recommendationPage < recommendationPages} onPrevious={() => changeRecommendationPage(recommendationPage - 1)} onNext={() => changeRecommendationPage(recommendationPage + 1)} /></div>
        {loadingRecommendations ? <p role="status">Buscando obras...</p> : recommendationError ? <p role="alert" className="text-destructive">Não foi possível carregar as recomendações.</p> : !recommendations.length ? <p className="text-muted-foreground">Analise algumas reflexões para receber sugestões fundamentadas nos seus temas recorrentes.</p> : <div className="dashboard-recommendations-list space-y-3">{recommendations.map((work) => <RecommendationWorkCard key={work.work_id} work={work} compact />)}</div>}
      </section>
    </div>

    <div className="dashboard-secondary-grid grid grid-cols-1 lg:grid-cols-2 gap-6">
      <section className="dashboard-secondary-card bg-card rounded-2xl border border-border p-6">
        <div className="dashboard-card-heading"><Tags className="w-5 h-5 text-primary" /><h2 className="text-xl">Temas recorrentes</h2></div>
        {!recurringThemes.length ? <p className="text-muted-foreground">Os temas aparecerão após suas primeiras análises.</p> : <div className="dashboard-theme-list">{recurringThemes.map((theme) => <div key={theme.theme_id}><div className="flex justify-between text-sm mb-1"><span className="truncate">{theme.label}</span><span className="text-muted-foreground shrink-0">{theme.reflection_count} {theme.reflection_count === 1 ? 'reflexão' : 'reflexões'}</span></div><div className="h-1.5 bg-muted rounded-full overflow-hidden"><div className="h-full rounded-full" style={{ width: `${(theme.reflection_count / maxThemeCount) * 100}%`, backgroundColor: theme.color || 'var(--primary)' }} /></div></div>)}</div>}
      </section>
      <section className="dashboard-secondary-card dashboard-latest-reference bg-gradient-to-br from-primary/10 to-secondary/10 rounded-2xl border border-border p-6"><div className="dashboard-card-heading"><BookOpen className="w-5 h-5 text-primary" /><h2 className="text-xl">Referência recente</h2></div>{summary?.latest_reference ? <div className="dashboard-reference-content"><blockquote className="text-sm italic text-muted-foreground">“{summary.latest_reference.short_text}”</blockquote><p className="text-sm"><span className="text-muted-foreground">— {summary.latest_reference.author_name || 'Autor não informado'},</span> {summary.latest_reference.work_title}</p></div> : <p className="text-muted-foreground">Uma referência aparecerá quando uma passagem for associada à sua reflexão.</p>}</section>
    </div>
    </div>
    </div>
  </div>
}

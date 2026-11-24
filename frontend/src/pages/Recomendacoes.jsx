import { BookOpen, ChevronLeft, ChevronRight, Compass, Sparkles } from 'lucide-react'
import { useEffect, useState } from 'react'
import { RecommendationWorkCard } from '../components/RecommendationWorkCard'
import { clearSession } from '../services/authSession'
import { listExploreWorks, listWorkRecommendations } from '../services/dashboardApi'

const PAGE_SIZE = 6

function Pager({ label, page, total, onChange }) {
  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE))
  return <nav aria-label={label} className="theme-pagination">
    <button type="button" aria-label="Página anterior" disabled={page <= 1} onClick={() => onChange(page - 1)}><ChevronLeft size={15} /></button>
    <span>Página {page} de {pages}</span>
    <button type="button" aria-label="Próxima página" disabled={page >= pages} onClick={() => onChange(page + 1)}><ChevronRight size={15} /></button>
  </nav>
}

function RecommendationSection({ icon: Icon, title, description, page, total, onPageChange, loading, error, empty, children }) {
  return <section className="recommendation-section">
    <div className="recommendation-section-heading">
      <div><div className="recommendation-section-title"><Icon size={19} aria-hidden="true" /><h2>{title}</h2></div><p>{description}</p></div>
      <Pager label={`Paginação de ${title}`} page={page} total={total} onChange={onPageChange} />
    </div>
    {loading ? <p role="status" className="recommendation-state">Carregando obras...</p> : error ? <p role="alert" className="recommendation-state text-destructive">Não foi possível carregar estas obras.</p> : children.length ? <div className="recommendation-work-grid">{children}</div> : <div className="recommendation-state"><BookOpen size={28} aria-hidden="true" /><p>{empty}</p></div>}
  </section>
}

export function Recomendacoes() {
  const [personalPage, setPersonalPage] = useState(1)
  const [personal, setPersonal] = useState({ items: [], total: 0, loading: true, error: null })
  const [explorePage, setExplorePage] = useState(1)
  const [explore, setExplore] = useState({ items: [], total: 0, loading: true, error: null })

  useEffect(() => {
    const controller = new AbortController()
    listWorkRecommendations({ limit: PAGE_SIZE, offset: (personalPage - 1) * PAGE_SIZE, signal: controller.signal })
      .then((data) => setPersonal({ items: data.recommendations || [], total: data.total || 0, loading: false, error: null }))
      .catch((error) => {
        if (error.name === 'AbortError') return
        if (error.status === 401) clearSession()
        setPersonal((current) => ({ ...current, loading: false, error }))
      })
    return () => controller.abort()
  }, [personalPage])

  useEffect(() => {
    const controller = new AbortController()
    listExploreWorks({ limit: PAGE_SIZE, offset: (explorePage - 1) * PAGE_SIZE, signal: controller.signal })
      .then((data) => setExplore({ items: data.works || [], total: data.total || 0, loading: false, error: null }))
      .catch((error) => {
        if (error.name === 'AbortError') return
        if (error.status === 401) clearSession()
        setExplore((current) => ({ ...current, loading: false, error }))
      })
    return () => controller.abort()
  }, [explorePage])

  const changePersonalPage = (page) => {
    setPersonal((current) => ({ ...current, loading: true, error: null }))
    setPersonalPage(page)
  }
  const changeExplorePage = (page) => {
    setExplore((current) => ({ ...current, loading: true, error: null }))
    setExplorePage(page)
  }

  return <div className="recommendations-page max-w-7xl mx-auto p-5 md:p-8">
    <header className="catalog-page-header catalog-page-intro">
      <div className="catalog-page-intro-copy"><h1 className="text-3xl">Recomendações</h1><p>Encontre obras relacionadas às suas reflexões e novas referências para explorar.</p></div>
    </header>
    <div className="recommendations-content">
      <RecommendationSection icon={Sparkles} title="Obras que têm a ver com você" description="Selecionadas a partir dos temas recorrentes nas suas análises." page={personalPage} total={personal.total} onPageChange={changePersonalPage} loading={personal.loading} error={personal.error} empty="Analise algumas reflexões para receber recomendações personalizadas.">
        {personal.items.map((work) => <RecommendationWorkCard key={work.work_id} work={work} />)}
      </RecommendationSection>
      <RecommendationSection icon={Compass} title="Obras para explorar" description="Referências ativas do catálogo para ampliar seus caminhos de reflexão." page={explorePage} total={explore.total} onPageChange={changeExplorePage} loading={explore.loading} error={explore.error} empty="Ainda não há obras ativas disponíveis no catálogo.">
        {explore.items.map((work) => <RecommendationWorkCard key={work.work_id} work={work} />)}
      </RecommendationSection>
    </div>
  </div>
}

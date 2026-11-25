import { ArrowLeft, BookOpen, Languages, Sparkles, UserRound } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useLocation, useParams } from 'react-router'
import { WorkCover } from '../components/WorkCover'
import { PageLoading } from '../components/PageLoading'
import { clearSession } from '../services/authSession'
import { getRecommendedWork } from '../services/dashboardApi'

const workTypeLabels = {
  academic_introduction: 'Introdução acadêmica',
  article: 'Artigo',
  book: 'Livro',
  essay: 'Ensaio',
}

function displayWorkType(value) {
  if (!value) return 'Não informado'
  return workTypeLabels[value] || value.replaceAll('_', ' ')
}

export function ObraRecomendada() {
  const { workId } = useParams()
  const location = useLocation()
  const [work, setWork] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const context = location.state?.recommendationContext
  const returnTo = location.state?.returnTo || '/inicio/recomendacoes'
  const returnLabel = location.state?.returnLabel || 'Voltar para recomendações'

  useEffect(() => {
    const controller = new AbortController()
    getRecommendedWork(workId, { signal: controller.signal })
      .then(setWork)
      .catch((requestError) => {
        if (requestError.name === 'AbortError') return
        if (requestError.status === 401) clearSession()
        setError(requestError.status === 404 ? 'Esta obra não está mais disponível no catálogo.' : 'Não foi possível carregar os detalhes da obra.')
      })
      .finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [workId])

  if (loading) return <div className="catalog-page recommended-work-detail-page"><PageLoading variant="detail" label="Carregando detalhes da obra…" /></div>

  if (error || !work) return <div className="catalog-page recommended-work-detail-page">
    <section className="catalog-card catalog-empty-state">
      <BookOpen size={30} aria-hidden="true" />
      <h1>Obra indisponível</h1>
      <p role="alert">{error || 'Obra não encontrada.'}</p>
      <Link className="catalog-button" to={returnTo}><ArrowLeft size={15} aria-hidden="true" />{returnLabel}</Link>
    </section>
  </div>

  const themes = context?.matchedThemes || []
  return <div className="catalog-page recommended-work-detail-page">
    <header className="catalog-page-header catalog-page-intro">
      <div className="catalog-page-intro-copy">
        <h1>{work.title}</h1>
        <p>Conheça melhor esta referência do catálogo do Reflecta.</p>
      </div>
      <Link className="catalog-button catalog-hover-secondary" to={returnTo}><ArrowLeft size={15} aria-hidden="true" />{returnLabel}</Link>
    </header>

    <div className="work-detail-layout recommended-work-layout">
      <aside className="catalog-card work-detail-cover recommended-work-cover-panel">
        <WorkCover work={work} />
      </aside>
      <section className="catalog-card work-detail-content" aria-labelledby="recommended-work-about">
        <div className="work-detail-content-heading"><h2 id="recommended-work-about">Sobre a obra</h2></div>
        <dl className="work-detail-list">
          <div><dt><UserRound size={14} aria-hidden="true" />Autor</dt><dd>{work.author_name || 'Não informado'}</dd></div>
          <div><dt><BookOpen size={14} aria-hidden="true" />Tipo</dt><dd>{displayWorkType(work.work_type)}</dd></div>
          <div><dt><Languages size={14} aria-hidden="true" />Idioma</dt><dd>{work.language || 'Não informado'}</dd></div>
          <div><dt>Sobre o autor</dt><dd>{work.author_description || 'Não informado'}</dd></div>
          <div className="work-detail-wide"><dt>Sinopse</dt><dd className="whitespace-pre-wrap">{work.synopsis || 'Sinopse não informada.'}</dd></div>
        </dl>
      </section>
    </div>

    {!!themes.length && <section className="catalog-card recommended-work-context" aria-labelledby="recommendation-context-title">
      <div className="recommended-work-context-heading"><Sparkles size={20} aria-hidden="true" /><div><h2 id="recommendation-context-title">Conexão com suas reflexões</h2><p>Esta obra apareceu por dialogar com temas recorrentes nas suas análises.</p></div></div>
      <div className="recommendation-theme-list">
        {themes.map((theme) => <span key={theme.theme_id}>{theme.label}</span>)}
      </div>
      {context.samplePassage && <blockquote>{context.samplePassage}</blockquote>}
    </section>}
  </div>
}

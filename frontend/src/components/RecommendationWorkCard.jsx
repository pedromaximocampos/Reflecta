import { ArrowRight } from 'lucide-react'
import { Link, useLocation } from 'react-router'
import { WorkCover } from './WorkCover'

export function RecommendationWorkCard({ work, compact = false }) {
  const location = useLocation()
  const themes = work.matched_themes || []
  const returnLabel = location.pathname === '/inicio' ? 'Voltar para o início' : 'Voltar para recomendações'

  return <Link
    className="recommendation-work-link"
    to={`/inicio/recomendacoes/${encodeURIComponent(work.work_id)}`}
    state={{
      recommendationContext: {
        matchedThemes: themes,
        samplePassage: work.sample_passage || null,
      },
      returnTo: location.pathname,
      returnLabel,
    }}
    aria-label={`Ver detalhes de ${work.title}`}
  >
    <article className={`recommendation-work-card${compact ? ' is-compact' : ''}`}>
      <WorkCover work={work} className="recommendation-work-cover" />
      <div className="recommendation-work-copy">
        <div>
          <div className="recommendation-work-title-row"><h3>{work.title}</h3><ArrowRight size={15} aria-hidden="true" /></div>
          <p className="recommendation-work-author">{work.author_name}</p>
        </div>
        {!compact && work.synopsis && <p className="recommendation-work-synopsis">{work.synopsis}</p>}
        {!!themes.length && <div className="recommendation-theme-list" aria-label="Temas relacionados">
          {themes.slice(0, 3).map((theme) => <span key={theme.theme_id}>{theme.label}</span>)}
        </div>}
      </div>
    </article>
  </Link>
}

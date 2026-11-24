import { ContextShareControls } from './ContextShareControls'
import { formatPeriodDate } from '../../services/contextPeriod'
import { Link } from 'react-router'
import {
  BookOpen,
  CalendarDays,
  Clock3,
  Info,
  Lightbulb,
  Repeat2,
  Sparkles,
  TrendingUp,
} from 'lucide-react'

const RESULT_SECTIONS = [
  { key: 'recurring_patterns', label: 'Padrões observados', icon: Repeat2 },
  { key: 'changes_over_time', label: 'Mudanças ao longo do tempo', icon: TrendingUp },
  { key: 'reflection_questions', label: 'Perguntas para refletir', icon: Lightbulb, ordered: true },
]

export function ContextAnalysisResult({ analysis, publicView = false, sharePlacement = 'footer', shareTitle = '' }) {
  const entryIds = analysis.entry_ids ?? []
  const entryCount = analysis.entry_count ?? entryIds.length
  const result = analysis.result ?? {}

  return <div className="context-analysis-result">
      {!publicView && sharePlacement === 'header' && <ContextShareControls key={analysis.id} analysis={analysis}
        placement="header" heading={shareTitle} />}

      <div className="context-result-meta" aria-label="Informações da análise">
        <div className="context-result-meta-item">
          <CalendarDays size={17} aria-hidden="true" />
          <div>
            <span>Período analisado</span>
            <strong>{analysis.period
              ? `${formatPeriodDate(analysis.period.start_date)} a ${formatPeriodDate(analysis.period.end_date)}`
              : 'Análise sem período registrado'}</strong>
          </div>
        </div>
        <div className="context-result-meta-item">
          <Clock3 size={17} aria-hidden="true" />
          <div>
            <span>Gerada em</span>
            <strong>{new Date(analysis.created_at).toLocaleString('pt-BR')}</strong>
          </div>
        </div>
        <div className="context-result-meta-item">
          <BookOpen size={17} aria-hidden="true" />
          <div>
            <span>Reflexões consideradas</span>
            <strong>{entryCount} {entryCount === 1 ? 'reflexão' : 'reflexões'}</strong>
          </div>
        </div>
      </div>

      {!publicView && entryIds.length > 0 && <details className="context-result-reflections">
        <summary>
          <span>Consultar reflexões incluídas</span>
          <small>{entryIds.length}</small>
        </summary>
        <ol>{entryIds.map((id, index) => <li key={id}>
          <Link to={`/inicio/reflexoes/${encodeURIComponent(id)}`}>Reflexão {index + 1}</Link>
        </li>)}</ol>
      </details>}

      <section className="context-result-summary" aria-labelledby={`context-summary-${analysis.id}`}>
        <div className="context-result-summary-heading">
          <Sparkles size={19} aria-hidden="true" />
          <h3 id={`context-summary-${analysis.id}`}>Síntese do período</h3>
        </div>
        <p>{result.summary || 'Não foi possível gerar uma síntese para este período.'}</p>
      </section>

      <div className="context-result-sections">
        {RESULT_SECTIONS.map(({ key, label, icon: SectionIcon, ordered }) => {
          const items = result[key] ?? []
          const ListTag = ordered ? 'ol' : 'ul'

          return <section className="context-result-section" key={key}>
            <div className="context-result-section-heading">
              <SectionIcon size={18} aria-hidden="true" />
              <h3>{label}</h3>
            </div>
            {items.length > 0
              ? <ListTag className={ordered ? 'is-ordered' : ''}>{items.map((text, index) => <li key={`${key}-${index}`}>
                  <span>{text}</span>
                </li>)}</ListTag>
              : <p className="context-result-empty">Nenhum ponto foi identificado nesta seção.</p>}
          </section>
        })}
      </div>

      <p className="context-result-disclaimer">
        <Info size={15} aria-hidden="true" />
        <span>Interpretação gerada por IA para apoiar a reflexão, sem finalidade de diagnóstico clínico.</span>
      </p>
      {!publicView && sharePlacement === 'footer' && <ContextShareControls key={analysis.id} analysis={analysis} placement="footer" />}
  </div>
}

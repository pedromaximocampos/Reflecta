import { useEffect, useState } from 'react'
import { ChevronDown, ChevronLeft, ChevronRight } from 'lucide-react'
import { formatPeriodDate } from '../../services/contextPeriod'
import { listContextAnalyses } from '../../services/contextAnalysisApi'
import { clearSession } from '../../services/authSession'
import { ContextAnalysisResult } from './ContextAnalysisResult'

const PAGE_SIZE = 5

export function ContextAnalysisHistory({ revision = 0 }) {
  const [offset, setOffset] = useState(0)
  const [retryRevision, setRetryRevision] = useState(0)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const controller = new AbortController()
    listContextAnalyses({ limit: PAGE_SIZE, offset, signal: controller.signal }).then((result) => {
      if (!controller.signal.aborted) setData(result)
    }).catch((err) => {
      if (controller.signal.aborted) return
      if (err.status === 401) clearSession()
      setError(err.message)
    }).finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [offset, retryRevision, revision])

  function changePage(nextOffset) {
    setLoading(true)
    setError('')
    setOffset(nextOffset)
  }

  function retry() {
    setLoading(true)
    setError('')
    setRetryRevision((value) => value + 1)
  }

  const total = data?.total ?? 0
  const currentPage = Math.floor(offset / PAGE_SIZE) + 1
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  return <section aria-labelledby="context-history-title" className="context-analysis-history-card">
    <div className="context-analysis-history-heading">
      <div><h2 id="context-history-title">Análises anteriores</h2><p>Consulte os resultados já solicitados, do mais recente ao mais antigo.</p></div>
      <div className="context-analysis-history-meta">
        <span>{total} {total === 1 ? 'análise registrada' : 'análises registradas'}</span>
        <nav aria-label="Paginação do histórico de análises" className="theme-pagination">
          <button type="button" aria-label="Página anterior" disabled={loading || offset === 0} onClick={() => changePage(Math.max(0, offset - PAGE_SIZE))}><ChevronLeft size={16} aria-hidden="true" /></button>
          <span>Página {currentPage} de {totalPages}</span>
          <button type="button" aria-label="Próxima página" disabled={loading || Boolean(error) || !data || currentPage === totalPages} onClick={() => changePage(offset + PAGE_SIZE)}><ChevronRight size={16} aria-hidden="true" /></button>
        </nav>
      </div>
    </div>

    <div className="context-analysis-history-list" aria-busy={loading}>
      {loading ? <p role="status">Carregando análises anteriores...</p> : error ? <div role="alert" className="context-analysis-history-error"><p>{error}</p><button type="button" className="catalog-button catalog-hover-secondary" onClick={retry}>Tentar novamente</button></div> : !data?.analyses.length ? <div className="context-analysis-history-empty">
        <h3>{offset ? 'Não há análises nesta página' : 'Você ainda não criou uma análise do histórico'}</h3>
        <p>{offset ? 'Retorne à página anterior.' : 'Use “Nova análise” para observar um período de sete dias do seu diário.'}</p>
      </div> : <ul>{data.analyses.map((analysis) => <li key={analysis.id}>
        {analysis.available ? <details className="context-analysis-history-item">
          <summary>
            <span className="context-analysis-history-summary-copy">
              <span>Análise de {new Date(analysis.created_at).toLocaleString('pt-BR')}</span>
              <small>{analysis.entry_count} reflexões{analysis.period ? ` · ${formatPeriodDate(analysis.period.start_date)} a ${formatPeriodDate(analysis.period.end_date)}` : ' · Período legado'}</small>
            </span>
            <span className="context-analysis-history-toggle" aria-hidden="true">
              <ChevronDown size={18} />
            </span>
          </summary>
          <div className="context-analysis-history-result"><ContextAnalysisResult analysis={analysis} sharePlacement="header"
            shareTitle={`Análise de ${new Date(analysis.created_at).toLocaleString('pt-BR')}`} /></div>
        </details> : <div className="context-analysis-history-item is-unavailable">
          <strong>Análise de {new Date(analysis.created_at).toLocaleString('pt-BR')}</strong>
          <small>{analysis.entry_count} reflexões</small>
          <p>Resultado indisponível porque uma ou mais reflexões utilizadas foram excluídas ou não estão mais disponíveis.</p>
        </div>}
      </li>)}</ul>}
    </div>
  </section>
}

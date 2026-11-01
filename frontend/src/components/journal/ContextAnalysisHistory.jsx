import { formatPeriodDate } from '../../services/contextPeriod'
import { useEffect, useState } from 'react'
import { listContextAnalyses } from '../../services/contextAnalysisApi'
import { clearSession } from '../../services/authSession'
import { ContextAnalysisResult } from './ContextAnalysisResult'

const PAGE_SIZE = 5

export function ContextAnalysisHistory() {
  const [offset, setOffset] = useState(0)
  const [revision, setRevision] = useState(0)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const controller = new AbortController()
    listContextAnalyses({ limit: PAGE_SIZE, offset, signal: controller.signal }).then(result => {
      if (!controller.signal.aborted) setData(result)
    }).catch(err => {
      if (controller.signal.aborted) return
      if (err.status === 401) clearSession()
      setError(err.message)
    }).finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [offset, revision])

  function changePage(nextOffset) {
    setLoading(true)
    setError('')
    setOffset(nextOffset)
  }

  function refreshHistory() {
    setLoading(true)
    setError('')
    setRevision(value => value + 1)
  }

  return <section aria-label="Histórico de análises contextuais" className="border-t border-border pt-5 space-y-4">
    <div className="flex flex-wrap items-center justify-between gap-3">
      <h3 className="text-lg font-medium">Análises anteriores</h3>
      <button type="button" disabled={loading} onClick={refreshHistory} className="underline disabled:opacity-50">Atualizar lista</button>
    </div>
    <p className="text-sm text-muted-foreground">Consulte os resultados já solicitados, do mais recente ao mais antigo. Abrir este histórico não gera novas análises.</p>
    {loading ? <p role="status">Carregando análises anteriores...</p> : error ? <p role="alert" className="text-destructive">{error}</p> : <>
      {!data?.analyses.length ? <p>{offset ? 'Não há análises nesta página.' : 'Você ainda não solicitou uma análise contextual.'}</p> : <>
        <p className="text-sm text-muted-foreground">{data.total} análises registradas</p>
        <ul className="space-y-3">{data.analyses.map(analysis => <li key={analysis.id}>
          {analysis.available ? <details className="rounded-xl border border-border p-4">
            <summary className="cursor-pointer font-medium">Análise de {new Date(analysis.created_at).toLocaleString('pt-BR')} · {analysis.entry_count} reflexões{analysis.period ? ` · ${formatPeriodDate(analysis.period.start_date)} a ${formatPeriodDate(analysis.period.end_date)}` : ' · Período legado'}</summary>
            <div className="mt-4"><ContextAnalysisResult analysis={analysis} /></div>
          </details> : <div className="rounded-xl border border-border p-4 space-y-2">
            <p className="font-medium">Análise de {new Date(analysis.created_at).toLocaleString('pt-BR')} · {analysis.entry_count} reflexões</p>
            <p className="text-sm text-muted-foreground">Resultado indisponível porque uma ou mais reflexões utilizadas foram excluídas ou não estão mais disponíveis.</p>
          </div>}
        </li>)}</ul>
      </>}
    </>}
    <nav aria-label="Paginação do histórico de análises" className="flex flex-wrap items-center justify-between gap-3">
      <button type="button" disabled={loading || offset === 0} onClick={() => changePage(Math.max(0, offset - PAGE_SIZE))} className="px-4 py-2 rounded-lg border border-border disabled:opacity-40">Análises mais recentes</button>
      <span className="text-sm text-muted-foreground">Página {offset / PAGE_SIZE + 1}</span>
      <button type="button" disabled={loading || Boolean(error) || !data || offset + PAGE_SIZE >= data.total} onClick={() => changePage(offset + PAGE_SIZE)} className="px-4 py-2 rounded-lg border border-border disabled:opacity-40">Análises mais antigas</button>
    </nav>
  </section>
}

import { defaultContextPeriod, shiftDate, formatPeriodDate } from '../../services/contextPeriod'
import { useEffect, useRef, useState } from 'react'
import { ContextAnalysisHistory } from './ContextAnalysisHistory'
import { ContextAnalysisResult } from './ContextAnalysisResult'
import { getContextAnalysis, submitContextAnalysis } from '../../services/contextAnalysisApi'
import { clearSession } from '../../services/authSession'

export function ContextAnalysis({ revision }) {
  const [period, setPeriod] = useState(defaultContextPeriod)
  const [status, setStatus] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [refresh, setRefresh] = useState(0)
  const pending = useRef(false)
  const generation = useRef(0)

  useEffect(() => {
    const controller = new AbortController()
    generation.current += 1
    getContextAnalysis(period, { signal: controller.signal }).then(data => {
      if (controller.signal.aborted) return
      setStatus(data)
      setAnalysis(data.analysis)
    }).catch(err => {
      if (controller.signal.aborted) return
      if (err.status === 401) clearSession()
      setError(err.message)
    })
    return () => { generation.current += 1; controller.abort() }
  }, [revision, refresh, period])

  function refreshStatus() {
    setStatus(null)
    setAnalysis(null)
    setError('')
    setRefresh(value => value + 1)
  }

  function changePeriod(key, value) {
    if (!value || busy) return
    generation.current += 1
    setStatus(null)
    setAnalysis(null)
    setError('')
    setPeriod(key === 'start_date' ? { start_date: value, end_date: shiftDate(value, 6) } : { start_date: shiftDate(value, -6), end_date: value })
  }

  async function analyze() {
    if (pending.current || !status?.eligible) return
    pending.current = true
    const requestGeneration = generation.current
    setBusy(true)
    setError('')
    try {
      const result = await submitContextAnalysis(period)
      if (generation.current === requestGeneration) setAnalysis(result)
    } catch (err) {
      if (err.status === 401) clearSession()
      if (generation.current === requestGeneration) setError(err.message)
    } finally {
      pending.current = false
      setBusy(false)
    }
  }

  return <section className="bg-card border border-border rounded-2xl p-5 md:p-6 space-y-4" aria-busy={busy}>
    <h2 className="text-xl">Análise do meu histórico</h2>
    <p className="text-muted-foreground">Escolha um período de exatamente 7 dias com pelo menos 5 reflexões. A análise reúne todas as reflexões desse intervalo para observar padrões e mudanças. Ela só é feita quando você solicita. Ao solicitar, você autoriza o envio dessas reflexões ao provedor de IA.</p>
    <fieldset disabled={busy} className="grid sm:grid-cols-2 gap-4">
      <label>Início do período<input className="block w-full px-3 py-2 rounded-lg border border-border" type="date" required value={period.start_date} onChange={event => changePeriod('start_date', event.target.value)} /></label>
      <label>Fim do período<input className="block w-full px-3 py-2 rounded-lg border border-border" type="date" required value={period.end_date} onChange={event => changePeriod('end_date', event.target.value)} /></label>
    </fieldset>
    <p className="text-sm text-muted-foreground">De {formatPeriodDate(period.start_date)} a {formatPeriodDate(period.end_date)}: 7 dias, incluindo início e fim, no horário de Brasília. Ao alterar uma data, a outra é ajustada.</p>
    {status && <p>{status.entry_count} reflexões neste período. Mínimo necessário: {status.minimum_entries}.</p>}
    {status && !status.eligible && <p>Este período precisa de pelo menos {status.minimum_entries} reflexões. Selecione outro intervalo ou registre novas reflexões nesse período.</p>}
    {!status && !error && <p role="status">Consultando histórico...</p>}
    <button type="button" disabled={!status?.eligible || busy || Boolean(analysis)} onClick={analyze}
      className="px-5 py-3 rounded-lg bg-primary text-primary-foreground disabled:opacity-50">
      {busy ? 'Analisando histórico...' : analysis ? 'Histórico já analisado' : 'Analisar meu histórico'}
    </button>
    {busy && <p role="status">Aguarde enquanto a análise é gerada.</p>}
    {error && <div role="alert"><p className="text-destructive">{error}</p><button type="button" disabled={busy} className="underline mt-2" onClick={refreshStatus}>Atualizar histórico</button></div>}
    {analysis && <ContextAnalysisResult analysis={analysis} />}
    <ContextAnalysisHistory key={`${revision}:${refresh}:${analysis?.id || ''}`} />
  </section>
}

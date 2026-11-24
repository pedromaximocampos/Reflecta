import { useEffect, useRef, useState } from 'react'
import { CalendarDays, Check, ChevronLeft, ChevronRight, ShieldCheck, X } from 'lucide-react'
import { defaultContextPeriod, shiftDate, formatPeriodDate } from '../../services/contextPeriod'
import { ContextAnalysisResult } from './ContextAnalysisResult'
import { getContextAnalysis, submitContextAnalysis } from '../../services/contextAnalysisApi'
import { clearSession } from '../../services/authSession'
import { ContextPeriodDatePicker } from './ContextPeriodDatePicker'
import { ContextEntryReviewList } from './ContextEntryReviewList'

const steps = ['Escolher período', 'Revisar e autorizar', 'Resultado']

export function ContextAnalysis({ onClose, onCreated }) {
  const [period, setPeriod] = useState(defaultContextPeriod)
  const [status, setStatus] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [refresh, setRefresh] = useState(0)
  const [step, setStep] = useState(1)
  const pending = useRef(false)
  const generation = useRef(0)

  useEffect(() => {
    const controller = new AbortController()
    generation.current += 1
    getContextAnalysis(period, { signal: controller.signal }).then((data) => {
      if (controller.signal.aborted) return
      setStatus(data)
      setAnalysis(data.analysis)
    }).catch((err) => {
      if (controller.signal.aborted) return
      if (err.status === 401) clearSession()
      setError(err.message)
    })
    return () => { generation.current += 1; controller.abort() }
  }, [refresh, period])

  useEffect(() => {
    function closeOnEscape(event) {
      if (event.key === 'Escape' && !busy) onClose()
    }
    window.addEventListener('keydown', closeOnEscape)
    return () => window.removeEventListener('keydown', closeOnEscape)
  }, [busy, onClose])

  function refreshStatus() {
    setStatus(null)
    setAnalysis(null)
    setError('')
    setRefresh((value) => value + 1)
  }

  function changePeriod(key, value) {
    if (!value || busy) return
    generation.current += 1
    setStatus(null)
    setAnalysis(null)
    setError('')
    setPeriod(key === 'start_date'
      ? { start_date: value, end_date: shiftDate(value, 6) }
      : { start_date: shiftDate(value, -6), end_date: value })
  }

  async function analyze() {
    if (pending.current || !status?.eligible) return
    pending.current = true
    const requestGeneration = generation.current
    setBusy(true)
    setError('')
    try {
      const result = await submitContextAnalysis(period)
      if (generation.current !== requestGeneration) return
      setAnalysis(result)
      setStep(3)
      onCreated(result)
    } catch (err) {
      if (err.status === 401) clearSession()
      if (generation.current === requestGeneration) setError(err.message)
    } finally {
      pending.current = false
      setBusy(false)
    }
  }

  const periodLabel = `${formatPeriodDate(period.start_date)} a ${formatPeriodDate(period.end_date)}`
  const maxDate = defaultContextPeriod().end_date
  const missingEntries = status ? Math.max(0, status.minimum_entries - status.entry_count) : 0

  return <div className="context-analysis-backdrop" role="presentation" onMouseDown={(event) => {
    if (event.target === event.currentTarget && !busy) onClose()
  }}>
    <section className="context-analysis-modal" role="dialog" aria-modal="true" aria-labelledby="context-analysis-title" aria-busy={busy}>
      <button type="button" className="context-analysis-close" onClick={onClose} disabled={busy} aria-label="Fechar nova análise"><X size={18} /></button>
      <header className="context-analysis-modal-heading">
        <span>ANÁLISE CONTEXTUAL</span>
        <h2 id="context-analysis-title">Nova análise do histórico</h2>
        <p>Escolha um intervalo, confira o que será analisado e autorize o processamento.</p>
      </header>

      <ol className="context-analysis-steps" aria-label="Etapas da nova análise">
        {steps.map((label, index) => {
          const number = index + 1
          const current = number === step
          const done = number < step
          return <li key={label} className={current || done ? 'is-active' : ''} aria-current={current ? 'step' : undefined}>
            <span>{done ? <Check size={15} aria-hidden="true" /> : number}</span>
            <small>{label}</small>
          </li>
        })}
      </ol>

      {step === 1 && <div className="context-analysis-step">
        <div className="context-analysis-step-copy">
          <CalendarDays size={22} aria-hidden="true" />
          <div><h3>Qual período você quer observar?</h3><p>O intervalo deve conter exatamente 7 dias e pelo menos 5 reflexões.</p></div>
        </div>
        <fieldset disabled={busy} className="context-analysis-period-grid">
          <ContextPeriodDatePicker label="Início do período" value={period.start_date} period={period}
            maxDate={shiftDate(maxDate, -6)} onChange={(value) => changePeriod('start_date', value)} />
          <ContextPeriodDatePicker label="Fim do período" value={period.end_date} period={period}
            maxDate={maxDate} onChange={(value) => changePeriod('end_date', value)} />
        </fieldset>
        <div className="context-analysis-period-summary">
          <strong>{periodLabel}</strong>
          <span>7 dias completos no horário de Brasília</span>
        </div>
        {!status && !error && <p role="status" className="text-sm text-muted-foreground">Consultando suas reflexões nesse período...</p>}
        {status && <>
          <p className={`context-analysis-eligibility ${status.eligible ? 'is-eligible' : 'is-ineligible'}`}>
            {status.eligible
              ? `${status.entry_count} reflexões encontradas · período disponível para análise`
              : `${status.entry_count} reflexões encontradas · ${missingEntries === 1 ? 'falta 1 reflexão' : `faltam ${missingEntries} reflexões`}`}
          </p>
          <ContextEntryReviewList entries={status.entries} />
        </>}
        {analysis && <p className="context-analysis-existing" role="note">Esse período já possui uma análise. Escolha outro intervalo ou consulte o resultado na lista de análises anteriores.</p>}
        {error && <div role="alert" className="context-analysis-error"><p>{error}</p><button type="button" onClick={refreshStatus}>Consultar novamente</button></div>}
        <div className="context-analysis-actions is-right">
          <button type="button" className="catalog-button catalog-hover-secondary" onClick={onClose}>Cancelar</button>
          <button type="button" className="catalog-primary catalog-hover-primary" disabled={!status?.eligible || busy || Boolean(analysis)} onClick={() => setStep(2)}>Continuar<ChevronRight size={16} /></button>
        </div>
      </div>}

      {step === 2 && <div className="context-analysis-step">
        <div className="context-analysis-step-copy">
          <ShieldCheck size={23} aria-hidden="true" />
          <div><h3>Revise antes de gerar</h3><p>Nenhuma análise é iniciada sem sua confirmação explícita.</p></div>
        </div>
        <dl className="context-analysis-review">
          <div><dt>Período</dt><dd>{periodLabel}</dd></div>
          <div><dt>Reflexões incluídas</dt><dd>{status?.entry_count ?? 0}</dd></div>
          <div><dt>Objetivo</dt><dd>Observar padrões, mudanças e pontos recorrentes nas reflexões selecionadas.</dd></div>
        </dl>
        <ContextEntryReviewList entries={status?.entries} title="Reflexões que serão analisadas" />
        <p className="context-analysis-consent">Ao continuar, você autoriza o envio das reflexões desse período ao provedor de IA. O resultado não é diagnóstico clínico e deve ser entendido como apoio à reflexão.</p>
        {error && <div role="alert" className="context-analysis-error"><p>{error}</p></div>}
        {busy && <p role="status" className="text-sm text-muted-foreground">Gerando a análise. Aguarde um momento...</p>}
        <div className="context-analysis-actions">
          <button type="button" className="catalog-button catalog-hover-secondary" disabled={busy} onClick={() => setStep(1)}><ChevronLeft size={16} />Voltar</button>
          <button type="button" className="catalog-primary catalog-hover-primary" disabled={busy} onClick={analyze}>{busy ? 'Analisando...' : 'Gerar análise'}</button>
        </div>
      </div>}

      {step === 3 && <div className="context-analysis-step context-analysis-result-step">
        <div className="context-analysis-success"><Check size={20} aria-hidden="true" /><div><h3>Análise concluída</h3><p>O resultado também foi adicionado ao seu histórico.</p></div></div>
        {analysis && <ContextAnalysisResult analysis={analysis} />}
        <div className="context-analysis-actions is-right"><button type="button" className="catalog-primary catalog-hover-primary" onClick={onClose}>Concluir</button></div>
      </div>}
    </section>
  </div>
}

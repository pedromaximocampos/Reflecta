import { useEffect, useMemo, useRef, useState } from 'react'
import { getJournalAnalysis, submitJournalAnalysis } from '../../services/journalApi'
import { clearSession } from '../../services/authSession'
import { JournalError } from './JournalFeedback'
import { highlightStyle } from '../../services/journalHighlights'
import { contextualPassages } from '../../services/journalAnalysis'

export function JournalAnalysis({ entry, onStatusChange, onAnalysisChange, embedded = false, passageFocusRequest = null }) {
  const [visible, setVisible] = useState(embedded)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [revision, setRevision] = useState(0)
  const [focusedPassageId, setFocusedPassageId] = useState(null)
  const busy = useRef(false)
  const passageRefs = useRef(new Map())
  const trackAnalysis = visible || ['analyzed', 'pending_analysis'].includes(entry.status)

  useEffect(() => {
    if (!trackAnalysis) return
    const controller = new AbortController()
    let timer
    async function load() {
      setLoading(true)
      try {
        const data = await getJournalAnalysis(entry.id, { signal: controller.signal })
        if (controller.signal.aborted) return
        setResult(data)
        onAnalysisChange(data.analysis)
        setError(null)
        onStatusChange(data.status)
        if (data.status === 'pending_analysis') timer = setTimeout(load, 5000)
      } catch (err) {
        if (controller.signal.aborted) return
        if (err.status === 401) clearSession()
        setError(err)
      } finally {
        if (!controller.signal.aborted) setLoading(false)
      }
    }
    load()
    return () => { controller.abort(); clearTimeout(timer) }
  }, [trackAnalysis, entry.id, revision, onStatusChange, onAnalysisChange])

  async function submit() {
    if (busy.current) return
    busy.current = true
    setSubmitting(true)
    setError(null)
    try {
      const data = await submitJournalAnalysis(entry.id, { expectedRevision: result?.reprocess?.revision })
      onStatusChange(data.status)
      setResult({ ...data, analysis: null })
      onAnalysisChange(null)
      setVisible(true)
      setRevision(value => value + 1)
    } catch (err) {
      if (err.status === 401) clearSession()
      setError(err)
      if ([403, 409].includes(err.status)) { setVisible(true); setRevision(value => value + 1) }
    } finally {
      busy.current = false
      setSubmitting(false)
    }
  }

  const analysis = result?.analysis
  const policy = result?.reprocess
  const canSubmit = entry.status === 'draft' || (entry.status === 'analysis_failed' && policy?.can_user_reprocess === true)
  const passages = useMemo(() => contextualPassages(analysis), [analysis])

  useEffect(() => {
    if (!passageFocusRequest) return undefined
    const passage = passages.find(item => item.themes.some(theme => theme.id === passageFocusRequest.themeId))
    const target = passage && passageRefs.current.get(passage.id)
    if (!target) return undefined
    const frame = requestAnimationFrame(() => {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' })
      setFocusedPassageId(passage.id)
    })
    const timer = setTimeout(() => setFocusedPassageId(null), 1800)
    return () => {
      cancelAnimationFrame(frame)
      clearTimeout(timer)
    }
  }, [passageFocusRequest, passages])
  return <section className={embedded ? 'space-y-4' : 'rounded-2xl border border-border bg-card p-5 md:p-8 space-y-4'}>
    {!embedded && <h2 className="text-xl">Análise da reflexão</h2>}
    {entry.status === 'analysis_failed' && <div role="alert" className="rounded-xl border border-destructive/30 bg-destructive/5 p-4 text-destructive">
      <p className="font-medium">Falha na análise</p>
      <p className="text-sm mt-1">{policy?.requires_admin ? 'As três solicitações de reprocessamento não tiveram sucesso. Sua reflexão foi preservada. Somente um administrador poderá solicitar outra tentativa.' : 'Não foi possível concluir a análise. Sua reflexão foi preservada.'}</p>
    </div>}
    {(!embedded || ['draft', 'analysis_failed'].includes(entry.status)) && <div className="flex flex-wrap gap-3">
      {canSubmit && <button type="button" disabled={submitting} onClick={submit}
        className="px-5 py-3 rounded-lg bg-primary text-primary-foreground disabled:opacity-50">
        {submitting ? 'Enviando...' : entry.status === 'analysis_failed' ? 'Solicitar análise novamente' : 'Solicitar análise de IA'}
      </button>}
      {!embedded && <button type="button" onClick={() => setVisible(value => !value)} aria-expanded={visible}
        aria-controls="journal-analysis-result" className="px-5 py-3 rounded-lg border border-border">
        {visible ? 'Ocultar análise' : 'Ver análise'}
      </button>}
    </div>}
    {policy && ['analysis_failed', 'pending_analysis'].includes(entry.status) && <p className="text-sm text-muted-foreground">Reprocessamentos solicitados por você: {policy.user_used} de {policy.user_limit}. Restantes: {policy.user_remaining}. A análise inicial não conta nesse limite.</p>}
    {entry.status === 'draft' && <p className="text-sm text-muted-foreground">Ao solicitar, a reflexão será enviada para análise e não poderá mais ser editada.</p>}
    <JournalError error={error} onRetry={() => { setVisible(true); setRevision(value => value + 1) }} />
    {visible && <div id="journal-analysis-result" className="space-y-4" aria-busy={loading}>
      {loading && !result && <p role="status">Carregando análise...</p>}
      {result?.status === 'pending_analysis' && <p role="status">Sua reflexão está na fila de análise. O resultado aparecerá aqui quando o processamento terminar.</p>}
      {result?.status === 'draft' && <p>A análise ainda não foi solicitada.</p>}
      {analysis && <>
        <div className="rounded-xl border border-border bg-muted p-4">
          <h3 className="font-medium mb-2">Conclusão geral</h3>
          <p className="whitespace-pre-wrap break-words leading-7">{analysis.main_message}</p>
        </div>
        {passages.length > 0 && <div className="space-y-3">
          <div><h3 className="font-medium mb-1">Passagens para continuar a reflexão</h3>
            <p className="text-sm text-muted-foreground">Trechos do catálogo relacionados aos pontos centrais identificados na sua reflexão.</p></div>
          <ol className="space-y-4">{passages.map(passage => <li key={passage.id}
            ref={node => node ? passageRefs.current.set(passage.id, node) : passageRefs.current.delete(passage.id)}
            className={`journal-contextual-passage rounded-xl border border-border p-4 space-y-3${focusedPassageId === passage.id ? ' is-focused' : ''}`}>
            <blockquote className="border-l-2 border-primary pl-4 whitespace-pre-wrap break-words leading-7">“{passage.short_text}”</blockquote>
            {(passage.work_title || passage.author_name || passage.locator) && <p className="text-sm text-muted-foreground">
              {[passage.work_title, passage.author_name, passage.locator].filter(Boolean).join(' · ')}
            </p>}
            {passage.themes.length > 0 && <ul className="flex flex-wrap gap-2">{passage.themes.map(theme => <li key={theme.id}
              className="text-sm rounded-full bg-secondary px-3 py-1 flex items-center gap-2"><span aria-hidden="true" className="h-3 w-3 rounded-full border border-border" style={{ backgroundColor: theme.color || '#8B5CF6' }} />{theme.label || theme.slug}</li>)}</ul>}
            {passage.reason && <div><h4 className="text-sm font-medium">Por que esta passagem foi selecionada</h4><p className="whitespace-pre-wrap break-words">{passage.reason}</p></div>}
            {passage.paraphrase && <div><h4 className="text-sm font-medium">Leitura possível</h4><p className="whitespace-pre-wrap break-words">{passage.paraphrase}</p></div>}
          </li>)}</ol>
        </div>}
        {analysis.sentences?.length > 0 && <div>
          <h3 className="font-medium mb-2">Frases e temas</h3>
          <ol className="space-y-3">{analysis.sentences.map(sentence => <li key={sentence.id}
            className="rounded-lg border border-border p-3 space-y-2">
            <p className="whitespace-pre-wrap break-words leading-7"><mark className="rounded-sm py-0.5"
              style={{ ...highlightStyle(sentence.themes), boxDecorationBreak: 'clone', WebkitBoxDecorationBreak: 'clone' }}>
              {sentence.sentence_text}
            </mark></p>
            {sentence.themes.length > 0
              ? <ul className="flex flex-wrap gap-2">{sentence.themes.map(theme => <li key={theme.id}
                className="text-sm rounded-full bg-secondary px-3 py-1 flex items-center gap-2"><span aria-hidden="true" className="h-3 w-3 rounded-full border border-border" style={{ backgroundColor: theme.color || '#8B5CF6' }} />{theme.label || theme.slug}</li>)}</ul>
              : <p className="text-sm text-muted-foreground">Sem tema associado.</p>}
          </li>)}</ol>
        </div>}
        <p className="text-sm text-muted-foreground">Interpretação gerada por IA, sem diagnóstico clínico.</p>
      </>}
    </div>}
  </section>
}

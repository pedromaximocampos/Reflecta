import { useEffect, useMemo, useRef, useState } from 'react'
import { getJournalAnalysis, submitJournalAnalysis, updateJournalAnalysisThemes } from '../../services/journalApi'
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
  const [editingThemes, setEditingThemes] = useState(false)
  const [selectedThemeIds, setSelectedThemeIds] = useState([])
  const [savingThemes, setSavingThemes] = useState(false)
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
      const data = await submitJournalAnalysis(entry.id, {
        expectedRevision: result?.reprocess?.revision,
        reanalyze: entry.status === 'analyzed',
      })
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
  const passages = useMemo(() => contextualPassages(analysis), [analysis])
  const availableThemes = useMemo(() => (
    Array.isArray(analysis?.available_themes)
      ? analysis.available_themes
      : Array.isArray(analysis?.metadata?.themes) ? analysis.metadata.themes : []
  ), [analysis])
  const effectiveThemes = Array.isArray(analysis?.metadata?.themes) ? analysis.metadata.themes : []
  const themedSentences = Array.isArray(analysis?.sentences)
    ? analysis.sentences.filter(sentence => Array.isArray(sentence.themes) && sentence.themes.length > 0)
    : []
  const lacksRelevantContent = Boolean(analysis) && (effectiveThemes.length === 0 || passages.length === 0)
  const canSubmit = entry.status === 'draft'
    || (entry.status === 'analysis_failed' && policy?.can_user_reprocess === true)
    || (entry.status === 'analyzed' && lacksRelevantContent && policy?.can_user_reanalyze === true)

  async function saveThemeSelection() {
    setSavingThemes(true)
    setError(null)
    try {
      const data = await updateJournalAnalysisThemes(entry.id, selectedThemeIds)
      setResult(data)
      onAnalysisChange(data.analysis)
      onStatusChange(data.status)
      setEditingThemes(false)
    } catch (err) {
      if (err.status === 401) clearSession()
      setError(err)
      if (err.status === 409) setRevision(value => value + 1)
    } finally {
      setSavingThemes(false)
    }
  }

  function toggleTheme(themeId) {
    setSelectedThemeIds(current => current.includes(themeId)
      ? current.filter(id => id !== themeId)
      : [...current, themeId])
  }

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
    {(!embedded || ['draft', 'analysis_failed'].includes(entry.status) || canSubmit) && <div className="flex flex-wrap gap-3">
      {canSubmit && <button type="button" disabled={submitting} onClick={submit}
        className="px-5 py-3 rounded-lg bg-primary text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-50">
        {submitting ? 'Enviando...' : entry.status === 'analyzed' ? 'Refazer análise' : entry.status === 'analysis_failed' ? 'Solicitar análise novamente' : 'Solicitar análise de IA'}
      </button>}
      {!embedded && <button type="button" onClick={() => setVisible(value => !value)} aria-expanded={visible}
        aria-controls="journal-analysis-result" className="px-5 py-3 rounded-lg border border-border">
        {visible ? 'Ocultar análise' : 'Ver análise'}
      </button>}
    </div>}
    {policy && (['analysis_failed', 'pending_analysis'].includes(entry.status) || (entry.status === 'analyzed' && lacksRelevantContent)) && <p className="text-sm text-muted-foreground">Novas análises solicitadas por você: {policy.user_used} de {policy.user_limit}. Restantes: {policy.user_remaining}. A análise inicial não conta nesse limite.</p>}
    {entry.status === 'draft' && <p className="text-sm text-muted-foreground">Ao solicitar, a reflexão será enviada para análise e não poderá mais ser editada.</p>}
    <JournalError error={error} onRetry={() => { setVisible(true); setRevision(value => value + 1) }} />
    {visible && <div id="journal-analysis-result" className="space-y-4" aria-busy={loading}>
      {loading && !result && <p role="status">Carregando análise...</p>}
      {result?.status === 'pending_analysis' && <p role="status">Sua reflexão está na fila de análise. O resultado aparecerá aqui quando o processamento terminar.</p>}
      {result?.status === 'draft' && <p>A análise ainda não foi solicitada.</p>}
      {analysis && <>
        <div className="rounded-xl border border-border bg-muted p-4">
          <h3 className="font-medium mb-2">Conclusão geral</h3>
          <p className="whitespace-pre-wrap break-words leading-7">{analysis.main_message || analysis.summary || 'A análise foi concluída sem uma conclusão textual.'}</p>
        </div>
        <div className="rounded-xl border border-border p-4 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="font-medium">Temas identificados</h3>
              <p className="text-sm text-muted-foreground">Mantenha somente os temas que representam sua reflexão.</p>
            </div>
            {entry.status === 'analyzed' && availableThemes.length > 0 && !editingThemes && <button type="button" onClick={() => {
              setSelectedThemeIds(Array.isArray(analysis.selected_theme_ids)
                ? analysis.selected_theme_ids : effectiveThemes.map(theme => theme.id))
              setEditingThemes(true)
            }}
              className="rounded-lg border border-primary px-3 py-2 text-sm text-primary transition-colors hover:bg-primary hover:text-primary-foreground">
              Editar temas
            </button>}
          </div>
          {editingThemes ? <>
            <ul className="grid gap-2 sm:grid-cols-2">{availableThemes.map(theme => <li key={theme.id}>
              <label className="flex cursor-pointer items-center gap-3 rounded-lg border border-border p-3 transition-colors hover:border-primary">
                <input type="checkbox" checked={selectedThemeIds.includes(theme.id)}
                  onChange={() => toggleTheme(theme.id)} />
                <span aria-hidden="true" className="h-3 w-3 rounded-full border border-border"
                  style={{ backgroundColor: theme.color || '#8B5CF6' }} />
                <span>{theme.label || theme.slug}</span>
              </label>
            </li>)}</ul>
            <div className="flex justify-end gap-2">
              <button type="button" disabled={savingThemes} onClick={() => {
                setEditingThemes(false)
              }} className="rounded-lg border border-border px-3 py-2 text-sm transition-colors hover:border-primary hover:text-primary">
                Cancelar
              </button>
              <button type="button" disabled={savingThemes} onClick={saveThemeSelection}
                className="rounded-lg bg-primary px-3 py-2 text-sm text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-50">
                {savingThemes ? 'Salvando...' : 'Salvar temas'}
              </button>
            </div>
          </> : effectiveThemes.length > 0
            ? <ul className="flex flex-wrap gap-2">{effectiveThemes.map(theme => <li key={theme.id}
              className="text-sm rounded-full bg-secondary px-3 py-1 flex items-center gap-2">
              <span aria-hidden="true" className="h-3 w-3 rounded-full border border-border"
                style={{ backgroundColor: theme.color || '#8B5CF6' }} />{theme.label || theme.slug}
            </li>)}</ul>
            : <p className="text-sm text-muted-foreground">Nenhum tema relevante foi mantido nesta análise.</p>}
        </div>
        {availableThemes.length === 0 && <div role="status" className="rounded-xl border border-border bg-muted/40 p-4">
          <p className="font-medium">Nenhum tema ou passagem relevante foi identificado.</p>
          <p className="mt-1 text-sm text-muted-foreground">A conclusão geral foi preservada. Você pode refazer a análise enquanto ainda houver tentativas disponíveis.</p>
        </div>}
        {availableThemes.length > 0 && effectiveThemes.length === 0 && <div role="status" className="rounded-xl border border-border bg-muted/40 p-4">
          <p className="font-medium">Nenhum tema foi mantido na curadoria.</p>
          <p className="mt-1 text-sm text-muted-foreground">As frases destacadas e as passagens relacionadas foram ocultadas. Você pode editar os temas novamente.</p>
        </div>}
        {effectiveThemes.length > 0 && passages.length === 0 && <div role="status" className="rounded-xl border border-border bg-muted/40 p-4">
          <p className="font-medium">Nenhuma passagem relacionada foi encontrada.</p>
          <p className="mt-1 text-sm text-muted-foreground">Os temas e a conclusão continuam disponíveis, e você pode refazer a análise enquanto houver tentativas.</p>
        </div>}
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
            {passage.reason && <div><h4 className="text-sm font-medium">Por que se relaciona com sua reflexão</h4><p className="whitespace-pre-wrap break-words">{passage.reason}</p></div>}
            {passage.paraphrase && <details className="journal-passage-paraphrase">
              <summary>Em outras palavras</summary>
              <p className="whitespace-pre-wrap break-words">{passage.paraphrase}</p>
            </details>}
          </li>)}</ol>
        </div>}
        {themedSentences.length > 0 && <div>
          <h3 className="font-medium mb-2">Frases e temas</h3>
          <ol className="space-y-3">{themedSentences.map(sentence => <li key={sentence.id}
            className="rounded-lg border border-border p-3 space-y-2">
            <p className="whitespace-pre-wrap break-words leading-7"><mark className="rounded-sm py-0.5"
              style={{ ...highlightStyle(sentence.themes), boxDecorationBreak: 'clone', WebkitBoxDecorationBreak: 'clone' }}>
              {sentence.sentence_text}
            </mark></p>
            <ul className="flex flex-wrap gap-2">{sentence.themes.map(theme => <li key={theme.id}
              className="text-sm rounded-full bg-secondary px-3 py-1 flex items-center gap-2"><span aria-hidden="true" className="h-3 w-3 rounded-full border border-border" style={{ backgroundColor: theme.color || '#8B5CF6' }} />{theme.label || theme.slug}</li>)}</ul>
          </li>)}</ol>
        </div>}
        <p className="text-sm text-muted-foreground">Interpretação gerada por IA, sem diagnóstico clínico.</p>
      </>}
    </div>}
  </section>
}

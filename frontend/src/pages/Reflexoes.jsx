import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router'
import { ChevronLeft, ChevronRight, Pencil, Plus, Trash2 } from 'lucide-react'
import { listJournalEntryWindow } from '../services/journalApi'
import { clearSession } from '../services/authSession'
import { tagCategories } from '../services/journalForm'
import { contextualPassages } from '../services/journalAnalysis'
import { DeleteEntryDialog } from '../components/journal/DeleteEntryDialog'
import { EntryMeta, JournalError } from '../components/journal/JournalFeedback'
import { HighlightedJournalText } from '../components/journal/HighlightedJournalText'
import { JournalAnalysis } from '../components/journal/JournalAnalysis'
import { JournalReadingPanels, JournalViewControls } from '../components/journal/JournalReadingPanels'

const WINDOW_DAYS = 15

export function Reflexoes() {
  const [searchParams] = useSearchParams()
  const targetEntryId = searchParams.get('entry_id')
  const centerDate = searchParams.get('center_date')
  const [entries, setEntries] = useState([])
  const [entryIndex, setEntryIndex] = useState(0)
  const [nextEndDate, setNextEndDate] = useState(null)
  const [revision, setRevision] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selected, setSelected] = useState(null)
  const [message, setMessage] = useState('')
  const [analysis, setAnalysis] = useState(null)
  const [readingView, setReadingView] = useState('both')
  const [activeThemeId, setActiveThemeId] = useState(null)
  const [passageFocusRequest, setPassageFocusRequest] = useState(null)

  const entry = entries[entryIndex] ?? null
  const hasOlderEntry = entryIndex < entries.length - 1 || Boolean(nextEndDate)

  useEffect(() => {
    const controller = new AbortController()
    listJournalEntryWindow({
      days: WINDOW_DAYS,
      centerDate: targetEntryId && centerDate ? centerDate : undefined,
      beforeDays: WINDOW_DAYS,
      afterDays: WINDOW_DAYS,
      signal: controller.signal,
    }).then((data) => {
      if (!controller.signal.aborted) {
        setEntries(data.entries)
        const targetIndex = targetEntryId
          ? data.entries.findIndex((item) => item.id === targetEntryId)
          : 0
        setEntryIndex(targetIndex >= 0 ? targetIndex : 0)
        setNextEndDate(data.next_end_date)
      }
    }).catch((err) => {
      if (controller.signal.aborted) return
      if (err.status === 401) clearSession()
      setError(err)
    }).finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [revision, targetEntryId, centerDate])

  const updateAnalysisStatus = useCallback((status) => {
    setEntries((previous) => previous.map((item, index) => index === entryIndex ? { ...item, status } : item))
  }, [entryIndex])

  const passageThemeIds = useMemo(() => new Set(
    contextualPassages(analysis).flatMap((passage) => passage.themes.map((theme) => theme.id)),
  ), [analysis])

  function focusPassageForTheme(themeId) {
    setReadingView((previous) => previous === 'reflection' ? 'both' : previous)
    setPassageFocusRequest({ themeId, requestId: Date.now() })
  }

  function prepareEntryChange() {
    setError(null)
    setMessage('')
    setAnalysis(null)
    setActiveThemeId(null)
    setPassageFocusRequest(null)
  }

  function showNewerEntry() {
    if (entryIndex === 0) return
    prepareEntryChange()
    setEntryIndex((value) => value - 1)
  }

  async function showOlderEntry() {
    if (!hasOlderEntry) return
    prepareEntryChange()
    if (entryIndex < entries.length - 1) {
      setEntryIndex((value) => value + 1)
      return
    }

    setLoading(true)
    try {
      const data = await listJournalEntryWindow({
        days: WINDOW_DAYS,
        endDate: nextEndDate,
      })
      const firstNewIndex = entries.length
      setEntries((previous) => [...previous, ...data.entries])
      setEntryIndex(firstNewIndex)
      setNextEndDate(data.next_end_date)
    } catch (err) {
      if (err.status === 401) clearSession()
      setError(err)
    } finally {
      setLoading(false)
    }
  }

  function deleted() {
    setSelected(null)
    setLoading(true)
    setMessage('Reflexão excluída com sucesso.')
    setAnalysis(null)
    setActiveThemeId(null)
    setPassageFocusRequest(null)
    setRevision((value) => value + 1)
  }

  function retry() {
    setLoading(true)
    setError(null)
    setAnalysis(null)
    setActiveThemeId(null)
    setPassageFocusRequest(null)
    setRevision((value) => value + 1)
  }

  return <div className="diary-page max-w-screen-2xl mx-auto p-5 md:p-8">
    <header className="catalog-page-header catalog-page-intro diary-page-header">
      <div className="catalog-page-intro-copy">
        <h1 className="text-3xl">Meu diário</h1>
        <p>Folheie suas reflexões da mais recente para as mais antigas e releia as análises e passagens relacionadas.</p>
      </div>
      <div className="catalog-header-actions diary-header-actions">
        {entry && <JournalViewControls view={readingView} onViewChange={setReadingView} />}
        <Link to="/inicio/diario" className="catalog-primary catalog-hover-primary"><Plus size={16} aria-hidden="true" />Nova reflexão</Link>
      </div>
    </header>

    {message && <p role="status" className="text-primary">{message}</p>}
    {loading ? <p role="status" className="diary-loading">Abrindo seu diário...</p> : error ? <JournalError error={error} onRetry={retry} /> : !entry ? <div className="diary-empty-state">
      <div className="diary-empty-mark" aria-hidden="true">R</div>
      <h2 className="text-xl">Seu diário ainda está vazio</h2>
      <p className="text-muted-foreground">Quando você registrar uma reflexão, ela aparecerá aqui como a primeira página.</p>
      <Link to="/inicio/diario" className="catalog-primary catalog-hover-primary"><Plus size={16} aria-hidden="true" />Escrever a primeira reflexão</Link>
    </div> : <>
      <nav aria-label="Folhear o diário" className="diary-turner">
        <button type="button" disabled={!hasOlderEntry} onClick={showOlderEntry} className="diary-turn-button">
          <ChevronLeft size={18} aria-hidden="true" /><span>Voltar no tempo</span>
        </button>
        <div className="diary-position" aria-live="polite">
          <span className="diary-position-rule" />
          <span>{targetEntryId
            ? (entry.id === targetEntryId ? 'Reflexão selecionada' : 'Navegando pelo período selecionado')
            : (entryIndex === 0 ? 'Reflexão mais recente' : `${entryIndex + 1}ª reflexão a partir da mais recente`)}</span>
          <span className="diary-position-rule" />
        </div>
        <button type="button" disabled={entryIndex === 0} onClick={showNewerEntry} className="diary-turn-button">
          <span>Avançar no diário</span><ChevronRight size={18} aria-hidden="true" />
        </button>
      </nav>

      <JournalReadingPanels view={readingView} onViewChange={setReadingView} reflection={<article className="diary-entry-content space-y-6">
        <div className="diary-entry-heading">
          <span className="diary-entry-kicker">Página do diário</span>
          <h2 className="text-2xl break-words">{entry.title || 'Reflexão sem título'}</h2>
          <EntryMeta entry={entry} />
        </div>
        <HighlightedJournalText text={entry.content_text} sentences={analysis?.sentences}
          activeThemeId={activeThemeId} passageThemeIds={passageThemeIds}
          onThemeHover={setActiveThemeId} onThemeSelect={focusPassageForTheme} />
        {Object.entries(tagCategories).map(([key, label]) => entry.context_tags?.[key]?.length > 0 && <div key={key}>
          <h3 className="text-sm text-muted-foreground mb-2">{label}</h3>
          <div className="flex flex-wrap gap-2">{entry.context_tags[key].map((tag, index) => <span key={index} className="px-3 py-1 rounded-full bg-muted break-words">{tag.label}</span>)}</div>
        </div>)}
        <div className="journal-entry-actions diary-entry-actions">
          {['draft', 'analyzed', 'analysis_failed'].includes(entry.status) && <Link to={`/inicio/reflexoes/${entry.id}/editar`} className="catalog-button catalog-hover-secondary"><Pencil size={16} aria-hidden="true" />Editar</Link>}
          <button type="button" onClick={() => setSelected(entry)} className="catalog-button catalog-destructive-outline journal-entry-action-delete"><Trash2 size={16} aria-hidden="true" />Excluir</button>
        </div>
      </article>} analysis={<JournalAnalysis key={entry.id} embedded entry={entry} onStatusChange={updateAnalysisStatus}
        onAnalysisChange={setAnalysis} passageFocusRequest={passageFocusRequest} />} />
    </>}
    {selected && <DeleteEntryDialog entry={selected} onClose={() => setSelected(null)} onDeleted={deleted} />}
  </div>
}

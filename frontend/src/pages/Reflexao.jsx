import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router'
import { ArrowLeft, CalendarDays, LockKeyhole, Plus, X } from 'lucide-react'
import { getJournalEntry, submitJournalAnalysis, updateJournalEntry } from '../services/journalApi'
import { entryChanges, entryFields, tagCategories } from '../services/journalForm'
import { clearSession } from '../services/authSession'
import { DeleteEntryDialog } from '../components/journal/DeleteEntryDialog'
import { EntryMeta, JournalError } from '../components/journal/JournalFeedback'
import { JournalAnalysis } from '../components/journal/JournalAnalysis'
import { JournalReadingPanels, JournalViewControls } from '../components/journal/JournalReadingPanels'
import { HighlightedJournalText } from '../components/journal/HighlightedJournalText'
import { contextualPassages } from '../services/journalAnalysis'
import { formatPeriodDate } from '../services/contextPeriod'

export function Reflexao({ editing = false }) {
  const { id } = useParams()
  return <EntryPage key={`${id}-${editing}`} id={id} editing={editing} />
}

function EntryPage({ id, editing }) {
  const navigate = useNavigate()
  const [entry, setEntry] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [fields, setFields] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [saveError, setSaveError] = useState(null)
  const [revision, setRevision] = useState(0)
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [message, setMessage] = useState('')
  const [tagCategory, setTagCategory] = useState('domains')
  const [tagDraft, setTagDraft] = useState('')
  const [readingView, setReadingView] = useState('both')
  const [activeThemeId, setActiveThemeId] = useState(null)
  const [passageFocusRequest, setPassageFocusRequest] = useState(null)
  const pending = useRef(false)
  const updateAnalysisStatus = useCallback(status => {
    setEntry(previous => previous.status === status ? previous : { ...previous, status })
  }, [])

  useEffect(() => {
    const controller = new AbortController()
    getJournalEntry(id, { signal: controller.signal }).then((data) => {
      if (controller.signal.aborted) return
      setEntry(data)
      setFields(entryFields(data))
    }).catch((err) => {
      if (controller.signal.aborted) return
      if (err.status === 401) clearSession()
      setError(err)
    }).finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [id, revision])

  async function save(event) {
    event.preventDefault()
    if (pending.current) return
    setSaveError(null)
    setMessage('')
    try {
      const changes = entryChanges(entry, fields)
      if (!Object.keys(changes).length) {
        if (entry.status !== 'draft') {
          setMessage('Nenhuma alteração para salvar.')
          return
        }
        pending.current = true
        setSaving(true)
        await submitJournalAnalysis(id)
        navigate(`/inicio/reflexoes/${id}`, { replace: true })
        return
      }
      pending.current = true
      setSaving(true)
      const updated = await updateJournalEntry(id, changes)
      setEntry(updated)
      setFields(entryFields(updated))
      await submitJournalAnalysis(id)
      navigate(`/inicio/reflexoes/${id}`, { replace: true })
    } catch (err) {
      if (err.status === 401) clearSession()
      setSaveError(err)
    } finally {
      pending.current = false
      setSaving(false)
    }
  }

  function change(key, value) {
    setFields((previous) => ({ ...previous, [key]: value }))
    setMessage('')
  }

  function fieldTags(category) {
    return (fields?.[category] ?? '').split(';').map((label) => label.trim()).filter(Boolean)
  }

  function addTags() {
    const additions = tagDraft.split(';').map((label) => label.trim()).filter(Boolean)
    if (!additions.length) return
    const labels = [...new Set([...fieldTags(tagCategory), ...additions])]
    change(tagCategory, labels.join('; '))
    setTagDraft('')
  }

  function removeTag(category, labelToRemove) {
    change(category, fieldTags(category).filter((label) => label !== labelToRemove).join('; '))
  }

  const inputClass = 'w-full px-4 py-3 rounded-lg border border-border bg-input-background focus:outline-none focus:ring-2 focus:ring-ring'
  const passageThemeIds = useMemo(() => new Set(
    contextualPassages(analysis).flatMap(passage => passage.themes.map(theme => theme.id)),
  ), [analysis])

  function focusPassageForTheme(themeId) {
    setReadingView(previous => previous === 'reflection' ? 'both' : previous)
    setPassageFocusRequest({ themeId, requestId: Date.now() })
  }

  function retry() {
    setLoading(true)
    setError(null)
    setRevision((value) => value + 1)
  }

  return <div className={`${editing ? 'max-w-4xl' : 'max-w-screen-2xl'} mx-auto p-5 md:p-8 space-y-6`}>
    <header className="catalog-page-header catalog-page-intro reflection-page-header">
      <div className="catalog-page-intro-copy reflection-page-heading">
        <h1 className="text-3xl">{editing ? 'Editar reflexão' : 'Consultar reflexão'}</h1>
        {!loading && !error && entry && <EntryMeta entry={entry} />}
      </div>
      <div className="reflection-page-actions">
        <Link to="/inicio/reflexoes" className="reflection-page-back">
          <ArrowLeft size={16} aria-hidden="true" />Voltar para minhas reflexões
        </Link>
        {!editing && entry && <JournalViewControls view={readingView} onViewChange={setReadingView} />}
      </div>
    </header>
    {loading ? <p role="status">Carregando reflexão...</p> : error ? <JournalError error={error} onRetry={retry} /> : entry && <>
      {editing ? <form onSubmit={save} aria-busy={saving} className="rounded-2xl bg-card border border-border p-5 md:p-8 space-y-5">
        <fieldset disabled={saving} className="space-y-5">
          <div className="grid grid-cols-1 md:grid-cols-[minmax(0,1fr)_220px] gap-4">
            <div><label htmlFor="entry-title" className="block mb-2 font-semibold">Título (opcional)</label>
              <input id="entry-title" value={fields.title} maxLength={200} onChange={(event) => change('title', event.target.value)} className={inputClass} /></div>
            <div><span className="block mb-2 font-semibold">Data da reflexão</span>
              <div className="journal-date-readonly" role="textbox" aria-readonly="true" aria-label={`Data da reflexão: ${formatPeriodDate(fields.entry_date)}`}>
                <CalendarDays size={17} aria-hidden="true" />
                <span>{formatPeriodDate(fields.entry_date)}</span>
                <LockKeyhole size={14} aria-hidden="true" />
              </div>
              <small className="journal-date-readonly-note">A data original é preservada no histórico.</small>
            </div>
          </div>
          <div><label htmlFor="entry-content" className="block mb-2 font-semibold">Reflexão</label>
            <textarea id="entry-content" required maxLength={20000} rows={12} value={fields.content_text} onChange={(event) => change('content_text', event.target.value)} className={inputClass} /></div>
          <section className="space-y-4" aria-labelledby="entry-context-title">
            <div>
              <h2 id="entry-context-title" className="font-semibold">Contexto opcional</h2>
              <p className="mt-1 text-sm text-muted-foreground">Escolha uma categoria e separe várias tags usando ponto e vírgula.</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-[180px_minmax(0,1fr)_auto] gap-3 items-end">
              <div>
                <label htmlFor="entry-tag-category" className="block mb-2 text-sm font-semibold">Categoria</label>
                <select id="entry-tag-category" value={tagCategory} onChange={(event) => setTagCategory(event.target.value)} className={inputClass}>
                  {Object.entries(tagCategories).map(([key, label]) => <option key={key} value={key}>{label}</option>)}
                </select>
              </div>
              <div>
                <label htmlFor="entry-tag-value" className="block mb-2 text-sm font-semibold">Tags</label>
                <input id="entry-tag-value" value={tagDraft} onChange={(event) => setTagDraft(event.target.value)}
                  onKeyDown={(event) => { if (event.key === 'Enter') { event.preventDefault(); addTags() } }}
                  placeholder="Ex: família; trabalho; rotina" className={inputClass} />
              </div>
              <button type="button" onClick={addTags} disabled={!tagDraft.trim()}
                className="catalog-button catalog-hover-secondary h-[50px] disabled:opacity-50">
                <Plus size={15} aria-hidden="true" />Adicionar
              </button>
            </div>
            <div className="space-y-3">
              {Object.entries(tagCategories).map(([key, label]) => fieldTags(key).length > 0 && <div key={key}>
                <h3 className="mb-2 text-sm font-semibold">{label}</h3>
                <div className="flex flex-wrap gap-2">
                  {fieldTags(key).map((tag) => <button key={tag} type="button" onClick={() => removeTag(key, tag)}
                    className="inline-flex items-center gap-1.5 rounded-full border border-border bg-muted px-3 py-1.5 text-sm transition-colors hover:border-destructive/50 hover:text-destructive"
                    aria-label={`Remover ${tag} de ${label}`}>
                    {tag}<X size={13} aria-hidden="true" />
                  </button>)}
                </div>
              </div>)}
              {Object.keys(tagCategories).every((key) => fieldTags(key).length === 0) && <p className="text-sm text-muted-foreground">Nenhuma tag adicionada.</p>}
            </div>
          </section>
          <div className="flex flex-wrap justify-end gap-3 pt-2">
            {!saving && <Link to={`/inicio/reflexoes?${new URLSearchParams({ entry_id: id, center_date: entry.entry_date })}`} className="catalog-button catalog-hover-secondary">Cancelar</Link>}
            <button type="submit" className="catalog-primary catalog-hover-primary disabled:opacity-50">{saving ? 'Salvando...' : 'Salvar e reanalisar'}</button>
          </div>
        </fieldset>
        {saveError && <p className="text-sm text-muted-foreground">Seu texto foi mantido nesta tela. Se precisar sair para fazer login, copie as alterações antes.</p>}
        <JournalError error={saveError} />
        {message && <p role="status" className="text-primary">{message}</p>}
      </form> : <JournalReadingPanels view={readingView} onViewChange={setReadingView} reflection={<article className="space-y-6">
        <h2 className="text-2xl break-words">{entry.title || 'Reflexão sem título'}</h2>
        <HighlightedJournalText text={entry.content_text} sentences={analysis?.sentences}
          activeThemeId={activeThemeId} passageThemeIds={passageThemeIds}
          onThemeHover={setActiveThemeId} onThemeSelect={focusPassageForTheme} />
        {Object.entries(tagCategories).map(([key, label]) => entry.context_tags?.[key]?.length > 0 && <div key={key}>
          <h3 className="text-sm text-muted-foreground mb-2">{label}</h3>
          <div className="flex flex-wrap gap-2">{entry.context_tags[key].map((tag, index) => <span key={index} className="px-3 py-1 rounded-full bg-muted break-words">{tag.label}</span>)}</div>
        </div>)}
        <div className="flex flex-wrap gap-3">
          {['draft', 'analyzed', 'analysis_failed'].includes(entry.status) && <Link to={`/inicio/reflexoes/${id}/editar`} className="px-5 py-3 rounded-lg bg-primary text-primary-foreground">Editar reflexão</Link>}
          <button type="button" onClick={() => setDeleting(true)} className="px-5 py-3 rounded-lg border border-destructive/30 text-destructive">Excluir reflexão</button>
        </div>
      </article>} analysis={<JournalAnalysis embedded entry={entry} onStatusChange={updateAnalysisStatus}
        onAnalysisChange={setAnalysis} passageFocusRequest={passageFocusRequest} />} />}
      {deleting && <DeleteEntryDialog entry={entry} onClose={() => setDeleting(false)} onDeleted={() => navigate('/inicio/reflexoes', { replace: true })} />}
    </>}
  </div>
}

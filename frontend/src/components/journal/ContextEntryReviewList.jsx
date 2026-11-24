import { useEffect, useRef, useState } from 'react'
import { ChevronDown, Eye, X } from 'lucide-react'
import { getJournalEntry } from '../../services/journalApi'
import { clearSession } from '../../services/authSession'
import { calendarDateLabel } from './journalCalendar'

const STATUS_LABELS = {
  draft: 'Rascunho',
  pending_analysis: 'Análise pendente',
  analyzed: 'Analisada',
  analysis_failed: 'Falha na análise',
}

function statusLabel(status) {
  return STATUS_LABELS[status] || 'Reflexão disponível'
}

export function ContextEntryReviewList({ entries = [], title = 'Reflexões encontradas' }) {
  const requestRef = useRef(null)
  const [selectedId, setSelectedId] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => () => requestRef.current?.abort(), [])

  function closePreview() {
    requestRef.current?.abort()
    requestRef.current = null
    setSelectedId(null)
    setPreview(null)
    setLoading(false)
    setError('')
  }

  async function togglePreview(entry) {
    if (selectedId === entry.id) {
      closePreview()
      return
    }
    requestRef.current?.abort()
    const controller = new AbortController()
    requestRef.current = controller
    setSelectedId(entry.id)
    setPreview(null)
    setError('')
    setLoading(true)
    try {
      const data = await getJournalEntry(entry.id, { signal: controller.signal })
      if (!controller.signal.aborted) setPreview(data)
    } catch (requestError) {
      if (controller.signal.aborted) return
      if (requestError.status === 401) clearSession()
      setError(requestError.message || 'Não foi possível abrir esta reflexão.')
    } finally {
      if (!controller.signal.aborted) setLoading(false)
    }
  }

  return <section className="context-entry-review" aria-label={title}>
    <div className="context-entry-review-heading">
      <h4>{title}</h4>
      <span>{entries.length} {entries.length === 1 ? 'reflexão' : 'reflexões'}</span>
    </div>
    {entries.length === 0 ? <p className="context-entry-review-empty">Nenhuma reflexão foi encontrada neste período.</p> : <ul>
      {entries.map((entry) => {
        const expanded = selectedId === entry.id
        return <li key={entry.id} className={expanded ? 'is-expanded' : ''}>
          <button type="button" className="context-entry-review-trigger" aria-expanded={expanded}
            onClick={() => togglePreview(entry)}>
            <span className="context-entry-review-copy">
              <strong>{entry.title?.trim() || 'Reflexão sem título'}</strong>
              <small>{calendarDateLabel(entry.entry_date)} · {statusLabel(entry.status)}</small>
            </span>
            <span className="context-entry-review-action">
              <Eye size={15} aria-hidden="true" />
              <span>Visualizar</span>
              <ChevronDown size={15} aria-hidden="true" />
            </span>
          </button>
          {expanded && <div className="context-entry-preview">
            <div className="context-entry-preview-heading">
              <div><strong>{entry.title?.trim() || 'Reflexão sem título'}</strong><small>{calendarDateLabel(entry.entry_date)}</small></div>
              <button type="button" onClick={closePreview} aria-label="Fechar visualização"><X size={15} /></button>
            </div>
            {loading && <p role="status">Carregando reflexão...</p>}
            {error && <p role="alert" className="context-entry-preview-error">{error}</p>}
            {preview && <p className="context-entry-preview-content">{preview.content_text}</p>}
          </div>}
        </li>
      })}
    </ul>}
  </section>
}

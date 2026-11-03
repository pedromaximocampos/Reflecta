import { ContextAnalysis } from '../components/journal/ContextAnalysis'
import { useEffect, useState } from 'react'
import { Link } from 'react-router'
import { BookOpen, Eye, Pencil, Plus, Trash2 } from 'lucide-react'
import { listJournalEntries } from '../services/journalApi'
import { clearSession } from '../services/authSession'
import { DeleteEntryDialog } from '../components/journal/DeleteEntryDialog'
import { EntryMeta, JournalError } from '../components/journal/JournalFeedback'

const PAGE_SIZE = 10

export function Reflexoes() {
  const [entries, setEntries] = useState([])
  const [offset, setOffset] = useState(0)
  const [revision, setRevision] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selected, setSelected] = useState(null)
  const [message, setMessage] = useState('')

  useEffect(() => {
    const controller = new AbortController()
    listJournalEntries({ limit: PAGE_SIZE, offset, signal: controller.signal }).then((data) => {
      if (!controller.signal.aborted) setEntries(data.entries)
    }).catch((err) => {
      if (controller.signal.aborted) return
      if (err.status === 401) clearSession()
      setError(err)
    }).finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [offset, revision])

  function deleted() {
    setSelected(null)
    setLoading(true)
    setMessage('Reflexão excluída com sucesso.')
    if (entries.length === 1 && offset > 0) setOffset(offset - PAGE_SIZE)
    setRevision((value) => value + 1)
  }

  function changePage(nextOffset) {
    setLoading(true)
    setError(null)
    setOffset(nextOffset)
  }

  function retry() {
    setLoading(true)
    setError(null)
    setRevision((value) => value + 1)
  }

  return <div className="max-w-5xl mx-auto p-5 md:p-8 space-y-6">
    <header className="catalog-page-header catalog-page-intro">
      <div className="catalog-page-intro-copy">
        <h1 className="text-3xl">Minhas reflexões</h1>
        <p>Releia seus registros, edite seus pensamentos ou exclua uma reflexão.</p>
      </div>
      <div className="catalog-header-actions">
        <Link to="/inicio/diario" className="catalog-primary catalog-hover-primary"><Plus size={16} aria-hidden="true" />Nova reflexão</Link>
      </div>
    </header>
    <ContextAnalysis key={revision} revision={revision} />
    {message && <p role="status" className="text-primary">{message}</p>}
    {loading ? <p role="status">Carregando reflexões...</p> : error ? <JournalError error={error} onRetry={retry} /> : <>
      {!entries.length ? <div className="bg-card border border-border rounded-2xl p-8 text-center space-y-3">
        <BookOpen className="w-10 h-10 mx-auto text-primary" />
        <h2 className="text-xl">{offset ? 'Não há mais reflexões nesta página' : 'Seu diário ainda está vazio'}</h2>
        <p className="text-muted-foreground">{offset ? 'Volte à página anterior para consultar seus registros.' : 'Suas reflexões salvas aparecerão aqui.'}</p>
      </div> : <ul className="space-y-4">
        {entries.map((entry) => <li key={entry.id} className="bg-card border border-border rounded-2xl p-5 md:p-6">
          <h2 className="text-xl mb-2 break-words">{entry.title || 'Reflexão sem título'}</h2>
          <EntryMeta entry={entry} />
          <p className="mt-4 text-muted-foreground whitespace-pre-wrap break-words">{entry.content_text.slice(0, 220)}{entry.content_text.length > 220 ? '…' : ''}</p>
          <div className="journal-entry-actions">
            <Link to={`/inicio/reflexoes/${entry.id}/editar`} className="catalog-button catalog-hover-secondary"><Pencil size={16} aria-hidden="true" />Editar</Link>
            <div className="journal-entry-state-actions">
              <Link to={`/inicio/reflexoes/${entry.id}`} className="catalog-primary catalog-hover-primary"><Eye size={16} aria-hidden="true" />Consultar</Link>
              <button type="button" onClick={() => setSelected(entry)} className="catalog-button catalog-destructive-outline journal-entry-action-delete"><Trash2 size={16} aria-hidden="true" />Excluir</button>
            </div>
          </div>
        </li>)}
      </ul>}
      <nav aria-label="Paginação das reflexões" className="flex items-center justify-between gap-4">
        <button type="button" disabled={!offset} onClick={() => changePage(Math.max(0, offset - PAGE_SIZE))} className="px-4 py-2 rounded-lg border border-border disabled:opacity-40">Anterior</button>
        <span className="text-sm text-muted-foreground">Página {offset / PAGE_SIZE + 1}</span>
        <button type="button" disabled={entries.length < PAGE_SIZE} onClick={() => changePage(offset + PAGE_SIZE)} className="px-4 py-2 rounded-lg border border-border disabled:opacity-40">Próxima</button>
      </nav>
    </>}
    {selected && <DeleteEntryDialog entry={selected} onClose={() => setSelected(null)} onDeleted={deleted} />}
  </div>
}

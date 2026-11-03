import { useEffect, useRef, useState } from 'react'
import { deleteJournalEntry } from '../../services/journalApi'
import { clearSession } from '../../services/authSession'
import { JournalError } from './JournalFeedback'

export function DeleteEntryDialog({ entry, onClose, onDeleted }) {
  const dialog = useRef(null)
  const pending = useRef(false)
  const [deleting, setDeleting] = useState(false)
  const [error, setError] = useState(null)
  useEffect(() => {
    const element = dialog.current
    element.showModal()
    return () => element.close()
  }, [])

  async function confirm() {
    if (pending.current) return
    pending.current = true
    setDeleting(true)
    setError(null)
    try {
      await deleteJournalEntry(entry.id)
    } catch (err) {
      if (err.status === 401) clearSession()
      setError(err)
      pending.current = false
      setDeleting(false)
      return
    }
    onDeleted(entry.id)
  }

  return <dialog ref={dialog} aria-labelledby="delete-entry-title"
    onCancel={(event) => { event.preventDefault(); if (!pending.current) onClose() }}
    className="m-auto w-[calc(100%-2rem)] max-w-lg rounded-2xl border border-border bg-card p-6 text-foreground shadow-xl backdrop:bg-black/40">
    <h2 id="delete-entry-title" className="text-xl mb-3">Excluir reflexão?</h2>
    <p className="mb-2 break-words font-medium">{entry.title || 'Reflexão sem título'}</p>
    <p className="text-muted-foreground mb-5">Esta reflexão deixará de aparecer no seu diário. Não há opção de restaurá-la nesta tela.</p>
    <JournalError error={error} />
    <div className="flex justify-end gap-3 mt-6">
      <button type="button" autoFocus disabled={deleting} onClick={onClose} className="px-4 py-3 border border-border rounded-lg disabled:opacity-50">Cancelar</button>
      <button type="button" disabled={deleting} onClick={confirm} className="px-4 py-3 rounded-lg bg-destructive text-white disabled:opacity-50">
        {deleting ? 'Excluindo...' : 'Confirmar exclusão'}
      </button>
    </div>
  </dialog>
}

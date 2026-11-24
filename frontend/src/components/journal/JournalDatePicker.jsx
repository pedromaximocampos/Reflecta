import { useEffect, useMemo, useRef, useState } from 'react'
import { CalendarDays, ChevronLeft, ChevronRight } from 'lucide-react'
import { listJournalEntryCalendar } from '../../services/journalApi'
import {
  WEEKDAYS,
  calendarCells,
  calendarDateLabel,
  calendarMonthBounds,
  calendarMonthLabel,
  moveCalendarMonth,
} from './journalCalendar'

export function JournalDatePicker({ value, maxDate, onChange, onExistingEntry }) {
  const rootRef = useRef(null)
  const [open, setOpen] = useState(false)
  const [displayMonth, setDisplayMonth] = useState(value.slice(0, 7))
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const bounds = useMemo(() => calendarMonthBounds(displayMonth), [displayMonth])
  const entriesByDate = useMemo(
    () => new Map(entries.map((entry) => [entry.entry_date, entry])),
    [entries],
  )

  useEffect(() => {
    if (!open) return undefined
    const controller = new AbortController()
    listJournalEntryCalendar({
      startDate: bounds.startDate,
      endDate: bounds.endDate,
      signal: controller.signal,
    }).then((response) => {
      if (!controller.signal.aborted) setEntries(response.entries)
    }).catch((requestError) => {
      if (!controller.signal.aborted) {
        setEntries([])
        setError(requestError.message || 'Não foi possível consultar este mês.')
      }
    }).finally(() => {
      if (!controller.signal.aborted) setLoading(false)
    })
    return () => controller.abort()
  }, [open, bounds.startDate, bounds.endDate])

  useEffect(() => {
    if (!open) return undefined
    function closeOnOutsideClick(event) {
      if (!rootRef.current?.contains(event.target)) setOpen(false)
    }
    function closeOnEscape(event) {
      if (event.key === 'Escape') setOpen(false)
    }
    document.addEventListener('mousedown', closeOnOutsideClick)
    document.addEventListener('keydown', closeOnEscape)
    return () => {
      document.removeEventListener('mousedown', closeOnOutsideClick)
      document.removeEventListener('keydown', closeOnEscape)
    }
  }, [open])

  const cells = useMemo(() => calendarCells(displayMonth), [displayMonth])

  function selectDate(dayValue) {
    const existing = entriesByDate.get(dayValue)
    if (existing) {
      setOpen(false)
      onExistingEntry(existing)
      return
    }
    onChange(dayValue)
    setOpen(false)
  }

  function toggleCalendar() {
    if (!open) {
      setDisplayMonth(value.slice(0, 7))
      setLoading(true)
      setError('')
    }
    setOpen((current) => !current)
  }

  function changeMonth(amount) {
    setLoading(true)
    setError('')
    setDisplayMonth((month) => moveCalendarMonth(month, amount))
  }

  return <div ref={rootRef} className="journal-date-picker">
    <button type="button" className="journal-date-trigger" aria-haspopup="dialog" aria-expanded={open}
      onClick={toggleCalendar}>
      <CalendarDays size={17} aria-hidden="true" />
      <span><small>Data da reflexão</small><strong>{calendarDateLabel(value)}</strong></span>
    </button>
    {open && <div className="journal-calendar" role="dialog" aria-label="Escolher data da reflexão">
      <div className="journal-calendar-heading">
        <button type="button" aria-label="Mês anterior" onClick={() => changeMonth(-1)}>
          <ChevronLeft size={17} />
        </button>
        <strong>{calendarMonthLabel(displayMonth)}</strong>
        <button type="button" aria-label="Próximo mês" disabled={moveCalendarMonth(displayMonth, 1) > maxDate.slice(0, 7)}
          onClick={() => changeMonth(1)}>
          <ChevronRight size={17} />
        </button>
      </div>
      <div className="journal-calendar-weekdays" aria-hidden="true">
        {WEEKDAYS.map((weekday) => <span key={weekday}>{weekday}</span>)}
      </div>
      <div className="journal-calendar-grid">
        {cells.map((cell, index) => cell === null ? <span key={`empty-${index}`} /> : (() => {
          const existing = entriesByDate.get(cell.value)
          const future = cell.value > maxDate
          return <button key={cell.value} type="button" disabled={future}
            className={`journal-calendar-day${cell.value === value ? ' is-selected' : ''}${existing ? ' has-entry' : ''}`}
            aria-label={`${calendarDateLabel(cell.value)}${existing ? ', possui reflexão' : ''}`}
            title={existing ? 'Abrir reflexão existente' : 'Criar reflexão nesta data'}
            onClick={() => selectDate(cell.value)}>
            <span>{cell.day}</span>
          </button>
        })())}
      </div>
      <div className="journal-calendar-footer">
        <span><i />Data com reflexão</span>
        {loading && <small role="status">Consultando...</small>}
      </div>
      {error && <p role="alert" className="journal-calendar-error">{error}</p>}
    </div>}
  </div>
}

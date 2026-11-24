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

function entryMarkerClass(entry) {
  if (!entry) return ''
  return entry.status === 'analyzed' ? ' has-entry has-analysis' : ' has-entry needs-analysis'
}

function entryDescription(entry) {
  if (!entry) return ''
  return entry.status === 'analyzed' ? ', possui reflexão analisada' : ', possui reflexão sem análise concluída'
}

export function ContextPeriodDatePicker({ label, value, period, maxDate, onChange }) {
  const rootRef = useRef(null)
  const [open, setOpen] = useState(false)
  const [displayMonth, setDisplayMonth] = useState(value.slice(0, 7))
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const bounds = useMemo(() => calendarMonthBounds(displayMonth), [displayMonth])
  const cells = useMemo(() => calendarCells(displayMonth), [displayMonth])
  const entriesByDate = useMemo(
    () => new Map(entries.map((entry) => [entry.entry_date, entry])),
    [entries],
  )

  useEffect(() => {
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
  }, [bounds.startDate, bounds.endDate])

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

  function toggleCalendar() {
    if (!open) {
      const valueMonth = value.slice(0, 7)
      if (valueMonth !== displayMonth) {
        setLoading(true)
        setDisplayMonth(valueMonth)
      }
      setError('')
    }
    setOpen((current) => !current)
  }

  function selectDate(dayValue) {
    onChange(dayValue)
    setOpen(false)
  }

  function changeMonth(amount) {
    setError('')
    setLoading(true)
    setDisplayMonth((month) => moveCalendarMonth(month, amount))
  }

  return <div ref={rootRef} className="journal-date-picker context-period-date-picker">
    <button type="button" className="journal-date-trigger" aria-haspopup="dialog" aria-expanded={open}
      onClick={toggleCalendar}>
      <CalendarDays size={17} aria-hidden="true" />
      <span><small>{label}</small><strong>{calendarDateLabel(value)}</strong></span>
    </button>
    {open && <div className="journal-calendar" role="dialog" aria-label={`Escolher ${label.toLowerCase()}`}>
      <div className="journal-calendar-heading">
        <button type="button" aria-label="Mês anterior" onClick={() => changeMonth(-1)}>
          <ChevronLeft size={17} />
        </button>
        <strong>{calendarMonthLabel(displayMonth)}</strong>
        <button type="button" aria-label="Próximo mês"
          disabled={moveCalendarMonth(displayMonth, 1) > maxDate.slice(0, 7)} onClick={() => changeMonth(1)}>
          <ChevronRight size={17} />
        </button>
      </div>
      <div className="journal-calendar-weekdays" aria-hidden="true">
        {WEEKDAYS.map((weekday) => <span key={weekday}>{weekday}</span>)}
      </div>
      <div className="journal-calendar-grid">
        {cells.map((cell, index) => cell === null ? <span key={`empty-${index}`} /> : (() => {
          const entry = entriesByDate.get(cell.value)
          const future = cell.value > maxDate
          const inRange = cell.value >= period.start_date && cell.value <= period.end_date
          return <button key={cell.value} type="button" disabled={future}
            className={`journal-calendar-day${inRange ? ' is-period-range' : ''}${cell.value === period.start_date ? ' is-period-start' : ''}${cell.value === period.end_date ? ' is-period-end' : ''}${entryMarkerClass(entry)}`}
            aria-label={`${calendarDateLabel(cell.value)}${entryDescription(entry)}`}
            title={entry ? 'Reflexão existente nesta data' : 'Selecionar esta data'}
            onClick={() => selectDate(cell.value)}>
            <span>{cell.day}</span>
          </button>
        })())}
      </div>
      <div className="journal-calendar-footer context-period-calendar-legend">
        <span><i className="is-analyzed" />Reflexão analisada</span>
        <span><i className="is-pending" />Sem análise concluída</span>
        {loading && <small role="status">Consultando...</small>}
      </div>
      {error && <p role="alert" className="journal-calendar-error">{error}</p>}
    </div>}
  </div>
}

export const WEEKDAYS = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']

export function calendarParts(isoValue) {
  const [year, month, day] = isoValue.split('-').map(Number)
  return { year, month, day }
}

export function calendarIsoDate(year, month, day) {
  return `${String(year).padStart(4, '0')}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
}

export function calendarMonthBounds(monthValue) {
  const { year, month } = calendarParts(`${monthValue}-01`)
  const lastDay = new Date(Date.UTC(year, month, 0)).getUTCDate()
  return {
    startDate: calendarIsoDate(year, month, 1),
    endDate: calendarIsoDate(year, month, lastDay),
    lastDay,
    leadingDays: new Date(Date.UTC(year, month - 1, 1)).getUTCDay(),
  }
}

export function moveCalendarMonth(monthValue, amount) {
  const { year, month } = calendarParts(`${monthValue}-01`)
  const moved = new Date(Date.UTC(year, month - 1 + amount, 1))
  return calendarIsoDate(moved.getUTCFullYear(), moved.getUTCMonth() + 1, 1).slice(0, 7)
}

export function calendarMonthLabel(monthValue) {
  const { year, month } = calendarParts(`${monthValue}-01`)
  const label = new Intl.DateTimeFormat('pt-BR', {
    month: 'long',
    year: 'numeric',
    timeZone: 'UTC',
  }).format(new Date(Date.UTC(year, month - 1, 1)))
  return label.charAt(0).toUpperCase() + label.slice(1)
}

export function calendarDateLabel(value) {
  const { year, month, day } = calendarParts(value)
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    timeZone: 'UTC',
  }).format(new Date(Date.UTC(year, month - 1, day)))
}

export function calendarCells(monthValue) {
  const bounds = calendarMonthBounds(monthValue)
  const { year, month } = calendarParts(bounds.startDate)
  const cells = Array.from({ length: bounds.leadingDays + bounds.lastDay }, (_, index) => {
    if (index < bounds.leadingDays) return null
    const day = index - bounds.leadingDays + 1
    return { day, value: calendarIsoDate(year, month, day) }
  })
  while (cells.length % 7 !== 0) cells.push(null)
  return cells
}

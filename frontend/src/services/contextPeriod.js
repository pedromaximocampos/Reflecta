export function shiftDate(value, days) {
  const date = new Date(`${value}T12:00:00Z`)
  date.setUTCDate(date.getUTCDate() + days)
  return date.toISOString().slice(0, 10)
}

export function defaultContextPeriod(now = new Date()) {
  const parts = Object.fromEntries(new Intl.DateTimeFormat('en-US', { timeZone: 'America/Sao_Paulo', year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(now).map(part => [part.type, part.value]))
  const end_date = `${parts.year}-${parts.month}-${parts.day}`
  return { start_date: shiftDate(end_date, -6), end_date }
}

export const formatPeriodDate = value => value.split('-').reverse().join('/')

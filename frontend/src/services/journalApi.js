import { request } from './apiClient.js'
import { invalidateDashboardCache } from './dashboardApi.js'

function authenticatedRequest(path, options = {}) {
  const token = sessionStorage.getItem('access_token')
  if (!token) {
    return Promise.reject(Object.assign(new Error('Sua sessão expirou. Entre novamente.'), { status: 401 }))
  }
  return request(`/journal/entries${path}`, {
    ...options,
    credentials: 'omit',
    headers: { Authorization: `Bearer ${token}`, ...options.headers },
  })
}

export function createJournalEntry(fields) {
  return authenticatedRequest('', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(fields),
  }).then((result) => { invalidateDashboardCache(); return result })
}

export function listJournalEntries({ limit = 10, offset = 0, signal } = {}) {
  return authenticatedRequest(`?${new URLSearchParams({ limit, offset })}`, { signal })
}

export function listJournalEntryWindow({
  endDate,
  days = 15,
  centerDate,
  beforeDays = 15,
  afterDays = 15,
  signal,
} = {}) {
  const params = new URLSearchParams({ days })
  if (endDate) params.set('end_date', endDate)
  if (centerDate) {
    params.set('center_date', centerDate)
    params.set('before_days', beforeDays)
    params.set('after_days', afterDays)
  }
  return authenticatedRequest(`/window?${params}`, { signal })
}

export function listJournalEntryCalendar({ startDate, endDate, signal } = {}) {
  const params = new URLSearchParams({ start_date: startDate, end_date: endDate })
  return authenticatedRequest(`/calendar?${params}`, { signal })
}

export function getJournalEntry(id, { signal } = {}) {
  return authenticatedRequest(`/${encodeURIComponent(id)}`, { signal })
}

export function updateJournalEntry(id, fields) {
  const payload = Object.fromEntries(Object.entries(fields).filter(([key]) =>
    ['title', 'content_text', 'context_tags'].includes(key)))
  return authenticatedRequest(`/${encodeURIComponent(id)}`, {
    method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
  }).then((result) => { invalidateDashboardCache(); return result })
}

export function deleteJournalEntry(id) {
  return authenticatedRequest(`/${encodeURIComponent(id)}`, { method: 'DELETE' })
    .then((result) => { invalidateDashboardCache(); return result })
}

export function submitJournalAnalysis(id, { expectedRevision, reanalyze = false } = {}) {
  const payload = {}
  if (expectedRevision) payload.expected_revision = expectedRevision
  if (reanalyze) payload.reanalyze = true
  const options = Object.keys(payload).length > 0
    ? { headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }
    : {}
  return authenticatedRequest(`/${encodeURIComponent(id)}/analysis`, { method: 'POST', ...options })
    .then((result) => { invalidateDashboardCache(); return result })
}

export function getJournalAnalysis(id, { signal } = {}) {
  return authenticatedRequest(`/${encodeURIComponent(id)}/analysis`, { signal })
}

export function updateJournalAnalysisThemes(id, themeIds) {
  return authenticatedRequest(`/${encodeURIComponent(id)}/analysis/themes`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ theme_ids: themeIds }),
  }).then((result) => { invalidateDashboardCache(); return result })
}

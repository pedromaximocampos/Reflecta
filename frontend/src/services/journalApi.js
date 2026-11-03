import { request } from './apiClient.js'

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
  })
}

export function listJournalEntries({ limit = 10, offset = 0, signal } = {}) {
  return authenticatedRequest(`?${new URLSearchParams({ limit, offset })}`, { signal })
}

export function getJournalEntry(id, { signal } = {}) {
  return authenticatedRequest(`/${encodeURIComponent(id)}`, { signal })
}

export function updateJournalEntry(id, fields) {
  const payload = Object.fromEntries(Object.entries(fields).filter(([key]) =>
    ['title', 'content_text', 'context_tags'].includes(key)))
  return authenticatedRequest(`/${encodeURIComponent(id)}`, {
    method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
  })
}

export function deleteJournalEntry(id) {
  return authenticatedRequest(`/${encodeURIComponent(id)}`, { method: 'DELETE' })
}

export function submitJournalAnalysis(id, { expectedRevision } = {}) {
  const options = expectedRevision ? { headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ expected_revision: expectedRevision }) } : {}
  return authenticatedRequest(`/${encodeURIComponent(id)}/analysis`, { method: 'POST', ...options })
}

export function getJournalAnalysis(id, { signal } = {}) {
  return authenticatedRequest(`/${encodeURIComponent(id)}/analysis`, { signal })
}

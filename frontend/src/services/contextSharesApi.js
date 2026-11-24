import { request } from './apiClient.js'

function ownerRequest(analysisId, suffix = '', options = {}) {
  const token = sessionStorage.getItem('access_token')
  if (!token) return Promise.reject(Object.assign(new Error('Sua sessão expirou. Entre novamente.'), { status: 401 }))
  return request(`/journal/context-analyses/${encodeURIComponent(analysisId)}/shares${suffix}`, {
    ...options, credentials: 'omit', cache: 'no-store',
    headers: { Authorization: `Bearer ${token}`, ...options.headers },
  })
}
export function listContextShares(id, { signal } = {}) { return ownerRequest(id, '', { signal }) }
export function listOwnerContextShares({ state = '', limit = 10, offset = 0, signal } = {}) {
  const token = sessionStorage.getItem('access_token')
  if (!token) return Promise.reject(Object.assign(new Error('Sua sessão expirou. Entre novamente.'), { status: 401 }))
  const query = new URLSearchParams({ limit, offset })
  if (state) query.set('state', state)
  return request(`/journal/context-shares?${query}`, {
    signal, credentials: 'omit', cache: 'no-store',
    headers: { Authorization: `Bearer ${token}` },
  })
}
export function createContextShare(id, { includeJournals = false } = {}) {
  return ownerRequest(id, '', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ confirmed: true, include_journals: includeJournals }) })
}
export function revokeContextShare(id, shareId) { return ownerRequest(id, `/${encodeURIComponent(shareId)}`, { method: 'DELETE' }) }
export function rotateContextShareToken(id, shareId) { return ownerRequest(id, `/${encodeURIComponent(shareId)}/rotate`, { method: 'POST' }) }
export function resolveContextShare(token, { signal } = {}) {
  return request('/shared/context-analysis/resolve', { method: 'POST', credentials: 'omit', cache: 'no-store', referrerPolicy: 'no-referrer', signal,
    headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ token }) })
}
export function createProfessionalActivities(token, activities) {
  return request('/shared/professional-activities', {
    method: 'POST', credentials: 'omit', cache: 'no-store', referrerPolicy: 'no-referrer',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      token,
      activities: activities.map(activity => ({
        kind: activity.kind,
        title: activity.title,
        description: activity.description,
        due_date: activity.dueDate || null,
      })),
    }),
  })
}
export function buildContextShareLink(token, origin = window.location.origin) {
  return `${origin}/compartilhamento#token=${encodeURIComponent(token)}`
}

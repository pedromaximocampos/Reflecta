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
export function createContextShare(id) {
  return ownerRequest(id, '', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ confirmed: true }) })
}
export function revokeContextShare(id, shareId) { return ownerRequest(id, `/${encodeURIComponent(shareId)}`, { method: 'DELETE' }) }
export function resolveContextShare(token, { signal } = {}) {
  return request('/shared/context-analysis/resolve', { method: 'POST', credentials: 'omit', cache: 'no-store', referrerPolicy: 'no-referrer', signal,
    headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ token }) })
}
export function buildContextShareLink(token, origin = window.location.origin) {
  return `${origin}/compartilhamento#token=${encodeURIComponent(token)}`
}

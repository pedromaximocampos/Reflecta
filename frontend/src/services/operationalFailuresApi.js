import { request } from './apiClient.js'

function adminRequest(path = '', options = {}) {
  const token = sessionStorage.getItem('access_token')
  if (!token) return Promise.reject(Object.assign(new Error('Sua sessão expirou. Entre novamente.'), { status: 401 }))
  return request(`/admin/operational-failures${path}`, {
    ...options, credentials: 'omit', headers: { ...options.headers, Authorization: `Bearer ${token}` },
  })
}

export function listOperationalFailures(filters = {}, { signal } = {}) {
  const allowed = ['source', 'state', 'entity_id', 'since', 'until', 'limit', 'offset']
  const query = new URLSearchParams(Object.entries(filters).filter(([key, value]) => allowed.includes(key) && value !== '' && value != null))
  return adminRequest(`?${query}`, { signal })
}

export function getOperationalFailure(source, id, { signal } = {}) {
  return adminRequest(`/${encodeURIComponent(source)}/${encodeURIComponent(id)}`, { signal })
}

export function getAnalysisProcessingSettings({ signal } = {}) {
  return adminRequest('/analysis-settings', { signal })
}

export function reprocessOperationalFailure(failureId, settings) {
  const configuration = settings ? Object.fromEntries(['model', 'timeout_seconds', 'max_output_tokens', 'reasoning_effort'].map(key => [key, settings[key]])) : null
  return adminRequest(`/journal/${encodeURIComponent(failureId)}/reprocess`, {
    method: 'POST',
    ...(configuration ? { headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(configuration) } : {}),
  })
}

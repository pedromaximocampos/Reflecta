import { request } from './apiClient.js'

function authenticatedRequest(path, options = {}) {
  const token = sessionStorage.getItem('access_token')
  if (!token) return Promise.reject(Object.assign(new Error('Sua sessão expirou. Entre novamente.'), { status: 401 }))
  return request(path, {
    ...options,
    credentials: 'omit',
    cache: 'no-store',
    headers: { Authorization: `Bearer ${token}`, ...options.headers },
  })
}

export function getDashboardSummary({ signal } = {}) {
  return authenticatedRequest('/journal/dashboard', { signal })
}

export function listWorkRecommendations({ limit = 4, offset = 0, signal } = {}) {
  const query = new URLSearchParams({ limit, offset })
  return authenticatedRequest(`/recommendations/works?${query}`, { signal })
}

export function listExploreWorks({ limit = 6, offset = 0, signal } = {}) {
  const query = new URLSearchParams({ limit, offset })
  return authenticatedRequest(`/recommendations/explore?${query}`, { signal })
}

export function getRecommendedWork(workId, { signal } = {}) {
  return authenticatedRequest(`/recommendations/works/${encodeURIComponent(workId)}`, { signal })
}


import { request } from './apiClient.js'

const DASHBOARD_CACHE_TTL_MS = 30_000
const responseCache = new Map()
const inFlight = new Map()

function sessionOwner() {
  try {
    const user = JSON.parse(sessionStorage.getItem('auth_user'))
    return user?.id || user?.user_id || 'authenticated-user'
  } catch {
    return 'authenticated-user'
  }
}

function abortError() {
  const error = new Error('A solicitação foi cancelada.')
  error.name = 'AbortError'
  return error
}

function observe(promise, signal) {
  if (!signal) return promise
  if (signal.aborted) return Promise.reject(abortError())
  return new Promise((resolve, reject) => {
    const abort = () => reject(abortError())
    signal.addEventListener('abort', abort, { once: true })
    promise.then(resolve, reject).finally(() => signal.removeEventListener('abort', abort))
  })
}

function cachedAuthenticatedRequest(path, { signal, ttl = DASHBOARD_CACHE_TTL_MS } = {}) {
  const key = `${sessionOwner()}:${path}`
  const cached = responseCache.get(key)
  if (cached && Date.now() - cached.savedAt < ttl) return observe(Promise.resolve(cached.data), signal)

  let pending = inFlight.get(key)
  if (!pending) {
    pending = authenticatedRequest(path)
      .then((data) => {
        responseCache.set(key, { data, savedAt: Date.now() })
        return data
      })
      .finally(() => inFlight.delete(key))
    inFlight.set(key, pending)
  }
  return observe(pending, signal)
}

export function invalidateDashboardCache() {
  responseCache.clear()
}

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
  return cachedAuthenticatedRequest('/journal/dashboard', { signal })
}

export function getHomeDashboard({
  entryLimit = 4,
  entryOffset = 0,
  recommendationLimit = 3,
  recommendationOffset = 0,
  signal,
} = {}) {
  const query = new URLSearchParams({
    entry_limit: entryLimit,
    entry_offset: entryOffset,
    recommendation_limit: recommendationLimit,
    recommendation_offset: recommendationOffset,
  })
  return cachedAuthenticatedRequest(`/recommendations/dashboard?${query}`, { signal })
}

export function listWorkRecommendations({ limit = 4, offset = 0, signal } = {}) {
  const query = new URLSearchParams({ limit, offset })
  return cachedAuthenticatedRequest(`/recommendations/works?${query}`, { signal })
}

export function listExploreWorks({ limit = 6, offset = 0, signal } = {}) {
  const query = new URLSearchParams({ limit, offset })
  return cachedAuthenticatedRequest(`/recommendations/explore?${query}`, { signal })
}

export function getRecommendedWork(workId, { signal } = {}) {
  return cachedAuthenticatedRequest(`/recommendations/works/${encodeURIComponent(workId)}`, { signal, ttl: 120_000 })
}


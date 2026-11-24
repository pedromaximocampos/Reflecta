import { request } from './apiClient.js'

export const PROFESSIONAL_ACTIVITIES_CHANGED = 'professional-activities:changed'

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

export function listProfessionalActivities({ status = '', limit = 8, offset = 0, signal } = {}) {
  const query = new URLSearchParams({ limit, offset })
  if (status) query.set('status', status)
  return authenticatedRequest(`/sharing/professional-activities?${query}`, { signal })
}

export function completeProfessionalActivity(activityId) {
  return authenticatedRequest(`/sharing/professional-activities/${encodeURIComponent(activityId)}/complete`, {
    method: 'PATCH',
  })
}

export function notifyProfessionalActivitiesChanged() {
  window.dispatchEvent(new CustomEvent(PROFESSIONAL_ACTIVITIES_CHANGED))
}

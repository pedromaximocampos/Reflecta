import { request } from './apiClient'

export async function getFeaturedWork({ signal } = {}) {
  const response = await request('/recommendations/public/featured-work', {
    credentials: 'omit',
    signal,
  })
  return response?.featured_work ?? null
}

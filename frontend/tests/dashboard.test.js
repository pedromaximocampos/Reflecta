import test from 'node:test'
import assert from 'node:assert/strict'
import {
  getDashboardSummary,
  getHomeDashboard,
  getRecommendedWork,
  invalidateDashboardCache,
  listExploreWorks,
  listWorkRecommendations,
} from '../src/services/dashboardApi.js'

test('dashboard and recommendations use authenticated read-only requests', async () => {
  const previousFetch = globalThis.fetch
  const previousStorage = globalThis.sessionStorage
  const calls = []
  globalThis.sessionStorage = { getItem: () => 'access-token' }
  globalThis.fetch = async (url, options) => {
    calls.push({ url, ...options })
    return new Response(JSON.stringify({}))
  }
  try {
    invalidateDashboardCache()
    await getHomeDashboard({ entryLimit: 4, entryOffset: 8, recommendationLimit: 3, recommendationOffset: 6 })
    await getDashboardSummary()
    await listWorkRecommendations({ limit: 3, offset: 6 })
    await listExploreWorks({ limit: 6, offset: 12 })
    await getRecommendedWork('work/id')
    assert.equal(new URL(calls[0].url).pathname, '/recommendations/dashboard')
    assert.equal(new URL(calls[0].url).search, '?entry_limit=4&entry_offset=8&recommendation_limit=3&recommendation_offset=6')
    assert.equal(new URL(calls[1].url).pathname, '/journal/dashboard')
    assert.equal(new URL(calls[2].url).pathname, '/recommendations/works')
    assert.equal(new URL(calls[2].url).search, '?limit=3&offset=6')
    assert.equal(new URL(calls[3].url).pathname, '/recommendations/explore')
    assert.equal(new URL(calls[3].url).search, '?limit=6&offset=12')
    assert.equal(new URL(calls[4].url).pathname, '/recommendations/works/work%2Fid')
    for (const call of calls) {
      assert.equal(call.method, undefined)
      assert.equal(call.credentials, 'omit')
      assert.equal(call.cache, 'no-store')
      assert.equal(call.headers.Authorization, 'Bearer access-token')
    }
  } finally {
    globalThis.fetch = previousFetch
    globalThis.sessionStorage = previousStorage
  }
})

test('dashboard cache reuses the same response during its short TTL', async () => {
  const previousFetch = globalThis.fetch
  const previousStorage = globalThis.sessionStorage
  let calls = 0
  globalThis.sessionStorage = { getItem: () => 'access-token' }
  globalThis.fetch = async () => {
    calls += 1
    return new Response(JSON.stringify({ metrics: {} }))
  }
  try {
    invalidateDashboardCache()
    await getDashboardSummary()
    await getDashboardSummary()
    assert.equal(calls, 1)
  } finally {
    invalidateDashboardCache()
    globalThis.fetch = previousFetch
    globalThis.sessionStorage = previousStorage
  }
})


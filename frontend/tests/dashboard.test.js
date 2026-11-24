import test from 'node:test'
import assert from 'node:assert/strict'
import { getDashboardSummary, getRecommendedWork, listExploreWorks, listWorkRecommendations } from '../src/services/dashboardApi.js'

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
    await getDashboardSummary()
    await listWorkRecommendations({ limit: 3, offset: 6 })
    await listExploreWorks({ limit: 6, offset: 12 })
    await getRecommendedWork('work/id')
    assert.equal(new URL(calls[0].url).pathname, '/journal/dashboard')
    assert.equal(new URL(calls[1].url).pathname, '/recommendations/works')
    assert.equal(new URL(calls[1].url).search, '?limit=3&offset=6')
    assert.equal(new URL(calls[2].url).pathname, '/recommendations/explore')
    assert.equal(new URL(calls[2].url).search, '?limit=6&offset=12')
    assert.equal(new URL(calls[3].url).pathname, '/recommendations/works/work%2Fid')
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


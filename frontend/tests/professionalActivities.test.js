import test from 'node:test'
import assert from 'node:assert/strict'
import { completeProfessionalActivity, listProfessionalActivities } from '../src/services/professionalActivitiesApi.js'

test('activities list and completion are authenticated and owner scoped by the API', async () => {
  const previousFetch = globalThis.fetch
  const previousStorage = globalThis.sessionStorage
  const calls = []
  globalThis.sessionStorage = { getItem: () => 'user-token' }
  globalThis.fetch = async (url, options) => {
    calls.push({ url, ...options })
    return new Response(JSON.stringify({ activities: [], total: 0 }))
  }
  try {
    await listProfessionalActivities({ status: 'pending', limit: 6, offset: 12 })
    const listUrl = new URL(calls[0].url)
    assert.equal(listUrl.pathname, '/sharing/professional-activities')
    assert.equal(listUrl.searchParams.get('status'), 'pending')
    assert.equal(listUrl.searchParams.get('limit'), '6')
    assert.equal(listUrl.searchParams.get('offset'), '12')
    assert.equal(calls[0].headers.Authorization, 'Bearer user-token')
    assert.equal(calls[0].credentials, 'omit')

    await completeProfessionalActivity('activity/id')
    assert.equal(new URL(calls[1].url).pathname, '/sharing/professional-activities/activity%2Fid/complete')
    assert.equal(calls[1].method, 'PATCH')
    assert.equal(calls[1].headers.Authorization, 'Bearer user-token')
  } finally {
    globalThis.fetch = previousFetch
    globalThis.sessionStorage = previousStorage
  }
})

test('activities API does not call the backend without a local session', async () => {
  const previousFetch = globalThis.fetch
  const previousStorage = globalThis.sessionStorage
  let calls = 0
  globalThis.sessionStorage = { getItem: () => null }
  globalThis.fetch = async () => { calls++; return new Response('{}') }
  try {
    await assert.rejects(listProfessionalActivities(), { status: 401 })
    await assert.rejects(completeProfessionalActivity('activity-id'), { status: 401 })
    assert.equal(calls, 0)
  } finally {
    globalThis.fetch = previousFetch
    globalThis.sessionStorage = previousStorage
  }
})

import test from 'node:test'
import assert from 'node:assert/strict'
import { submitJournalAnalysis, getJournalAnalysis } from '../src/services/journalApi.js'

test('owner reads retry policy and submits the current failure revision without caller-supplied quota or role', async () => {
  const previousFetch = globalThis.fetch
  const previousStorage = globalThis.sessionStorage
  const calls = []
  globalThis.sessionStorage = { getItem: () => 'owner-token' }
  globalThis.fetch = async (url, options) => {
    calls.push({ url, ...options })
    return { ok: true, json: async () => ({ reprocess: { user_used: 2, user_remaining: 1, revision: '2026-10-27T12:00:00+00:00' } }) }
  }
  try {
    const status = await getJournalAnalysis('entry/id')
    await submitJournalAnalysis('entry/id', { expectedRevision: status.reprocess.revision })
    assert.match(calls[1].url, /\/entries\/entry%2Fid\/analysis$/)
    assert.equal(calls[1].method, 'POST')
    assert.equal(calls[1].headers.Authorization, 'Bearer owner-token')
    assert.equal(calls[1].headers['Content-Type'], 'application/json')
    assert.deepEqual(JSON.parse(calls[1].body), { expected_revision: status.reprocess.revision })
    await submitJournalAnalysis('legacy-draft')
    assert.equal(calls[2].body, undefined) // initial submission is not a reprocessing request
  } finally {
    globalThis.fetch = previousFetch
    globalThis.sessionStorage = previousStorage
  }
})

test('quota and stale revision errors are preserved without retrying automatically', async () => {
  const previousFetch = globalThis.fetch
  const previousStorage = globalThis.sessionStorage
  let calls = 0
  globalThis.sessionStorage = { getItem: () => 'owner-token' }
  try {
    for (const status of [403, 409, 503]) {
      globalThis.fetch = async () => { calls++; return { ok: false, status, json: async () => ({ detail: 'Solicitação indisponível.' }) } }
      await assert.rejects(submitJournalAnalysis('entry', { expectedRevision: '2026-10-27T12:00:00Z' }), { status })
    }
    assert.equal(calls, 3)
  } finally {
    globalThis.fetch = previousFetch
    globalThis.sessionStorage = previousStorage
  }
})

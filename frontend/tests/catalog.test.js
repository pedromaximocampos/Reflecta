import test from 'node:test'
import assert from 'node:assert/strict'
import { createWork, getWork, listPassages, listWorkIngestions, listWorks, passageAction, removeWorkCover, updatePassage, uploadWork, uploadWorkCover } from '../src/services/catalogApi.js'

test('catalog authenticates, encodes filters, validates PDF and uploads multipart document', async () => {
  const previousFetch = globalThis.fetch
  const previousStorage = globalThis.sessionStorage
  const calls = []
  globalThis.sessionStorage = { getItem: () => 'admin-token' }
  globalThis.fetch = async (url, options) => { calls.push({ url, ...options }); return { ok: true, json: async () => ({}) } }
  try {
    await createWork({ title: 'Introdução', author: { name: 'Aldo Dinucci' } })
    assert.equal(calls[0].headers.Authorization, 'Bearer admin-token')
    assert.equal(calls[0].credentials, 'omit')
    assert.equal(JSON.parse(calls[0].body).author.name, 'Aldo Dinucci')
    await listWorks()
    assert.match(calls[1].url, /catalog\/works$/)
    assert.equal(calls[1].method, undefined)
    await getWork('work/id')
    assert.match(calls[2].url, /catalog\/works\/work%2Fid$/)
    await uploadWorkCover('work/id', new File(['image'], 'cover.webp', { type: 'image/webp' }))
    assert.match(calls[3].url, /catalog\/works\/work%2Fid\/cover$/)
    assert.equal(calls[3].method, 'PUT')
    assert.equal(calls[3].body.get('cover').name, 'cover.webp')
    await removeWorkCover('work/id')
    assert.equal(calls[4].method, 'DELETE')
    await listPassages({ status: 'PENDING_REVIEW', ingestion_id: 'a/b', work_id: '' })
    assert.equal(new URL(calls[5].url).searchParams.get('ingestion_id'), 'a/b')
    assert.equal(new URL(calls[5].url).searchParams.has('work_id'), false)
    await uploadWork('work/id', new File(['pdf'], 'fonte.pdf', { type: 'application/pdf' }))
    assert.equal(calls[6].headers['Content-Type'], undefined)
    assert.equal(calls[6].body.get('document').name, 'fonte.pdf')
    assert.match(calls[6].url, /works\/work%2Fid\/ingestions$/)
    await assert.rejects(uploadWork('id', new File([], 'empty.pdf', { type: 'application/pdf' })))
    await assert.rejects(uploadWork('id', new File(['text'], 'source.txt', { type: 'text/plain' })))
    await passageAction('passage', 'approve')
    assert.equal(calls.at(-1).body, undefined)
    assert.match(calls.at(-1).url, /passages\/passage\/approve$/)
    await updatePassage('passage', { paraphrase: 'Explicação revisada' })
    assert.deepEqual(JSON.parse(calls.at(-1).body), { paraphrase: 'Explicação revisada' })
    assert.throws(() => passageAction('passage', 'unknown'))
    await listWorkIngestions(25)
    assert.equal(new URL(calls.at(-1).url).pathname, '/ai-processing/work-ingestions')
    assert.equal(new URL(calls.at(-1).url).searchParams.get('limit'), '25')
    assert.equal(calls.at(-1).headers.Authorization, 'Bearer admin-token')
  } finally { globalThis.fetch = previousFetch; globalThis.sessionStorage = previousStorage }
})

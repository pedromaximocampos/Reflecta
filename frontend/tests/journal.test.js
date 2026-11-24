import { beforeEach, test } from 'node:test'
import assert from 'node:assert/strict'
import { createJournalEntry, listJournalEntries, listJournalEntryCalendar, listJournalEntryWindow, getJournalEntry, updateJournalEntry, deleteJournalEntry } from '../src/services/journalApi.js'
import { entryChanges, entryFields } from '../src/services/journalForm.js'

beforeEach(() => {
  const data = new Map([['access_token', 'access-token']])
  globalThis.sessionStorage = {
    getItem: (key) => data.get(key) ?? null,
    setItem: (key, value) => data.set(key, value),
    removeItem: (key) => data.delete(key),
  }
  globalThis.window = new EventTarget()
})

test('list and detail use Bearer auth, pagination and no cookies', async () => {
  const paths = []
  globalThis.fetch = async (url, options) => {
    paths.push(new URL(url).pathname + new URL(url).search)
    assert.equal(options.credentials, 'omit')
    assert.equal(options.headers.Authorization, 'Bearer access-token')
    return new Response(JSON.stringify({ entries: [] }))
  }
  assert.deepEqual(await listJournalEntries({ limit: 10, offset: 20 }), { entries: [] })
  await getJournalEntry('id/encoded')
  assert.deepEqual(paths, ['/journal/entries?limit=10&offset=20', '/journal/entries/id%2Fencoded'])
})

test('journal window sends the 15-day cursor only when loading older entries', async () => {
  const paths = []
  globalThis.fetch = async (url) => {
    paths.push(new URL(url).pathname + new URL(url).search)
    return new Response(JSON.stringify({ entries: [], next_end_date: null }))
  }
  await listJournalEntryWindow()
  await listJournalEntryWindow({ endDate: '2026-10-01' })
  await listJournalEntryWindow({ centerDate: '2026-07-04' })
  assert.deepEqual(paths, [
    '/journal/entries/window?days=15',
    '/journal/entries/window?days=15&end_date=2026-10-01',
    '/journal/entries/window?days=15&center_date=2026-07-04&before_days=15&after_days=15',
  ])
})

test('journal calendar requests only the selected date range', async () => {
  globalThis.fetch = async (url) => {
    assert.equal(new URL(url).pathname + new URL(url).search,
      '/journal/entries/calendar?start_date=2026-07-01&end_date=2026-07-31')
    return new Response(JSON.stringify({ entries: [] }))
  }
  await listJournalEntryCalendar({ startDate: '2026-07-01', endDate: '2026-07-31' })
})

test('duplicate journal date exposes the existing entry for redirect', async () => {
  globalThis.fetch = async () => new Response(JSON.stringify({
    errors: [{
      title: 'JournalEntryDateConflictError',
      status: 409,
      data: 'A journal entry already exists for this date.',
      details: { existing_entry_id: 'existing-id', entry_date: '2026-07-04' },
    }],
  }), { status: 409 })

  await assert.rejects(
    createJournalEntry({ content_text: 'Duplicada', entry_date: '2026-07-04' }),
    (error) => error.status === 409
      && error.details.existing_entry_id === 'existing-id'
      && error.details.entry_date === '2026-07-04',
  )
})

test('PATCH sends only supported fields and returns updated reflection', async () => {
  globalThis.fetch = async (url, options) => {
    assert.equal(new URL(url).pathname, '/journal/entries/entry-id')
    assert.equal(options.method, 'PATCH')
    assert.deepEqual(JSON.parse(options.body), { title: null, content_text: 'Texto editado' })
    return new Response(JSON.stringify({ id: 'entry-id', title: null, content_text: 'Texto editado' }))
  }
  const result = await updateJournalEntry('entry-id', { title: null, content_text: 'Texto editado', entry_date: '2026-10-30', user_id: 'another', status: 'deleted' })
  assert.equal(result.content_text, 'Texto editado')
})

test('DELETE accepts empty 204 and sends no body', async () => {
  let calls = 0
  globalThis.fetch = async (url, options) => {
    calls++
    assert.equal(new URL(url).pathname, '/journal/entries/entry-id')
    assert.equal(options.method, 'DELETE')
    assert.equal(options.body, undefined)
    assert.equal(options.headers.Authorization, 'Bearer access-token')
    return new Response(null, { status: 204 })
  }
  assert.equal(await deleteJournalEntry('entry-id'), null)
  assert.equal(calls, 1)
})

test('missing session blocks all requests', async () => {
  sessionStorage.getItem = () => null
  globalThis.fetch = () => assert.fail('Must not send request')
  for (const operation of [() => listJournalEntries(), () => getJournalEntry('id'), () => updateJournalEntry('id', { title: 'Title' }), () => deleteJournalEntry('id')]) {
    await assert.rejects(operation(), { status: 401 })
  }
})

test('failures preserve status and authentication retry remains bounded', async () => {
  for (const status of [401, 403, 404, 422, 500]) {
    sessionStorage.setItem('access_token', 'access-token')
    let calls = 0
    globalThis.fetch = async () => {
      calls++
      return new Response(JSON.stringify({ detail: 'Falha' }), { status })
    }
    if (status === 401) {
      await assert.rejects(deleteJournalEntry('entry-id'), {
        status: 401,
        message: 'Sua sessão expirou. Entre novamente.',
      })
      assert.equal(calls, 2)
    } else {
      await assert.rejects(deleteJournalEntry('entry-id'), { status, message: 'Falha' })
      assert.equal(calls, 1)
    }
  }
})

test('read requests pass abort signal to fetch', async () => {
  const controller = new AbortController()
  globalThis.fetch = async (_url, options) => {
    assert.equal(options.signal, controller.signal)
    throw new DOMException('Aborted', 'AbortError')
  }
  await assert.rejects(listJournalEntries({ signal: controller.signal }), { name: 'AbortError' })
})

const entry = {
  title: 'Título', content_text: 'Meu texto',
  entry_date: '2026-10-30',
  context_tags: {
    people: [{ label: 'Ana', source: 'user' }],
    places: [{ label: 'Casa', source: 'ai', confidence: 0.9, approved: true }],
    domains: [{ label: 'Família', source: 'ai', confidence: 0.8 }],
  },
}

test('editing text does not replace tags or send unchanged fields', () => {
  assert.deepEqual(entryChanges(entry, entryFields(entry)), {})
  assert.deepEqual(entryChanges(entry, { ...entryFields(entry), content_text: ' Novo texto ' }), { content_text: 'Novo texto' })
})

test('editing fields never sends a changed journal date', () => {
  assert.deepEqual(
    entryChanges(entry, { ...entryFields(entry), entry_date: '2026-10-29' }),
    {},
  )
})

test('editing tags preserves categories and metadata, removes duplicates and permits clearing', () => {
  const changed = entryChanges(entry, { ...entryFields(entry), places: 'Casa; Trabalho; Trabalho', people: '' })
  assert.deepEqual(changed.context_tags, {
    people: [],
    places: [entry.context_tags.places[0], { label: 'Trabalho', source: 'user' }],
    domains: entry.context_tags.domains,
  })
  assert.deepEqual(entryChanges(entry, { ...entryFields(entry), title: ' ' }), { title: null })
})

test('edit validates empty text and field limits', () => {
  for (const invalid of [{ content_text: ' ' }, { content_text: 'a'.repeat(20001) }, { title: 'a'.repeat(201) }, { places: 'a'.repeat(101) }]) {
    assert.throws(() => entryChanges(entry, { ...entryFields(entry), ...invalid }))
  }
})

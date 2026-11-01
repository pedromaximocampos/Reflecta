import test from 'node:test'
import assert from 'node:assert/strict'

import { filterPassages } from '../src/services/passageFilters.js'

const passages = [
  { id: '1', status: 'PENDING_REVIEW', work_id: 'WORK-ALPHA', ingestion_id: 'INGESTION-ONE', themes: [{ confidence: 0.93 }] },
  { id: '2', status: 'ACTIVE', work_id: 'WORK-BETA', ingestion_id: 'INGESTION-TWO', themes: [{ confidence: 0.72 }, { confidence: 0.45 }] },
  { id: '3', status: 'PENDING_REVIEW', work_id: 'WORK-BETA', ingestion_id: 'INGESTION-THREE', themes: [{ confidence: 0.59 }] },
  { id: '4', status: 'PENDING_REVIEW', work_id: 'WORK-ALPHA', ingestion_id: 'INGESTION-FOUR', themes: [] },
]

const works = [
  { id: 'WORK-ALPHA', title: 'Manual de Epicteto', author: { name: 'Epicteto' } },
  { id: 'WORK-BETA', title: 'Meditações', author: { name: 'Marco Aurélio' } },
]

test('passage filters run locally by status and partial identifiers', () => {
  assert.deepEqual(
    filterPassages(passages, { status: 'PENDING_REVIEW', work_id: 'beta', ingestion_id: 'three' }),
    [passages[2]],
  )
  assert.deepEqual(filterPassages(passages, { status: 'ACTIVE' }), [passages[1]])
})

test('empty passage filters preserve the in-memory collection', () => {
  assert.deepEqual(filterPassages(passages, {}), passages)
  assert.deepEqual(filterPassages(null, {}), [])
})

test('passage filters search locally by work title and author name', () => {
  assert.deepEqual(filterPassages(passages, { work_title: 'manual' }, works), [passages[0], passages[3]])
  assert.deepEqual(filterPassages(passages, { author_name: 'marco aurelio' }, works), [passages[1], passages[2]])
  assert.deepEqual(filterPassages(passages, { work_title: 'medita', author_name: 'MARCO' }, works), [passages[1], passages[2]])
})

test('passage confidence ranges use the strongest associated theme locally', () => {
  assert.deepEqual(filterPassages(passages, { confidence_range: 'high' }, works), [passages[0]])
  assert.deepEqual(filterPassages(passages, { confidence_range: 'medium' }, works), [passages[1]])
  assert.deepEqual(
    filterPassages(passages, { status: 'PENDING_REVIEW', confidence_range: 'high' }, works),
    [passages[0]],
  )
})

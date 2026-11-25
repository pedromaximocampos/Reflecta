import test from 'node:test'
import assert from 'node:assert/strict'
import {
  buildPassageQuery,
  PASSAGE_PAGE_SIZE,
  readPassageFilters,
  serializePassageFilters,
} from '../src/services/passageQuery.js'

test('passage filters are rebuilt when the serialized URL changes', () => {
  const pending = readPassageFilters(new URLSearchParams('status=PENDING_REVIEW'))
  const active = readPassageFilters(new URLSearchParams('status=ACTIVE&work_title=manual&author_name=epicteto'))

  assert.equal(pending.status, 'PENDING_REVIEW')
  assert.deepEqual(active, {
    status: 'ACTIVE',
    work_id: '',
    ingestion_id: '',
    work_title: 'manual',
    author_name: 'epicteto',
    confidence_range: '',
  })
})

test('passage query combines every filter with server pagination', () => {
  const filters = {
    status: 'APPROVED',
    work_id: '01ABCDEFGHIJKLMNOPQRSTUVWX',
    ingestion_id: '01ZYXWVUTSRQPONMLKJIHGFEDC',
    work_title: 'meditações',
    author_name: 'marco',
    confidence_range: 'medium',
  }

  assert.deepEqual(buildPassageQuery(filters, 3), {
    status: 'APPROVED',
    work_id: '01ABCDEFGHIJKLMNOPQRSTUVWX',
    ingestion_id: '01ZYXWVUTSRQPONMLKJIHGFEDC',
    work_title: 'meditações',
    author_name: 'marco',
    confidence_min: 0.7,
    confidence_max: 0.8,
    limit: PASSAGE_PAGE_SIZE,
    offset: PASSAGE_PAGE_SIZE * 2,
  })
})

test('passage filter serialization preserves explicit all-status selection', () => {
  const params = serializePassageFilters({
    status: '',
    work_id: '',
    ingestion_id: '',
    work_title: 'confissões',
    author_name: '',
    confidence_range: 'high',
  })

  assert.equal(params.toString(), 'status=&work_title=confiss%C3%B5es&confidence_range=high')
})

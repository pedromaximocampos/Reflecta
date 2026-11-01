import { test } from 'node:test'
import assert from 'node:assert/strict'
import { highlightedSegments, highlightStyle } from '../src/services/journalHighlights.js'

const work = { id: 'work', label: 'Trabalho', color: '#3B82F6' }
const health = { id: 'health', label: 'Saúde', color: '#22C55E' }

test('highlights preserve original Unicode text, punctuation, whitespace and repeated sentences', () => {
  const text = '  Oi 😴.\n\nOi 😴.  '
  const first = 'Oi 😴.'
  const size = Array.from(first).length
  const sentences = [
    { sentence_text: first, start_offset: 2, end_offset: 2 + size, themes: [work] },
    { sentence_text: first, start_offset: 4 + size, end_offset: 4 + size * 2, themes: [health] },
  ]
  const segments = highlightedSegments(text, sentences)
  assert.equal(segments.map(segment => segment.text).join(''), text)
  assert.deepEqual(segments.filter(segment => segment.themes.length).map(segment => segment.themes[0].id), ['work', 'health'])
})

test('mismatched, overlapping and out-of-bounds sentences never modify or duplicate diary text', () => {
  const text = 'Um. Dois.'
  const segments = highlightedSegments(text, [
    { start_offset: 0, end_offset: 3, sentence_text: 'Um.', themes: [work] },
    { start_offset: 1, end_offset: 7, sentence_text: 'm. Doi', themes: [health] },
    { start_offset: 4, end_offset: 9, sentence_text: 'Outro', themes: [health] },
    { start_offset: 4, end_offset: 100, sentence_text: 'Dois.', themes: [health] },
  ])
  assert.equal(segments.map(segment => segment.text).join(''), text)
  assert.equal(segments.filter(segment => segment.themes.length).length, 1)
})

test('analysis without sentences displays the complete unmarked text', () => {
  assert.deepEqual(highlightedSegments('Meu diário.'), [{ text: 'Meu diário.', themes: [] }])
})

test('highlight opacity applies to background only and multiple themes retain their colors', () => {
  assert.deepEqual(highlightStyle([work]), { backgroundColor: '#3B82F633', color: 'inherit' })
  assert.deepEqual(highlightStyle([work], 'work'), { backgroundColor: '#3B82F666', color: 'inherit' })
  assert.deepEqual(highlightStyle([work], 'health'), { backgroundColor: '#3B82F633', color: 'inherit' })
  const multi = highlightStyle([work, health])
  assert.ok(multi.backgroundImage.includes('#3B82F633'))
  assert.ok(multi.backgroundImage.includes('#22C55E33'))
  assert.equal(multi.color, 'inherit')
  assert.equal(multi.opacity, undefined)
  assert.equal(highlightStyle([]).backgroundColor, 'transparent')
})

test('invalid colors fall back to a valid translucent color', () => {
  assert.equal(highlightStyle([{ color: 'url(https://untrusted)' }]).backgroundColor, '#8B5CF633')
})

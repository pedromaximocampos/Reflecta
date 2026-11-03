const DEFAULT_COLOR = '#8B5CF6'

export function themeColor(theme) {
  return /^#[0-9a-f]{6}$/i.test(theme.color || '') ? theme.color.toUpperCase() : DEFAULT_COLOR
}

export function highlightStyle(themes, activeThemeId = null) {
  const colors = [...new Set(themes.map(themeColor))]
  if (!colors.length) return { backgroundColor: 'transparent', color: 'inherit' }
  const emphasized = Boolean(activeThemeId) && themes.some(theme => theme.id === activeThemeId)
  const translucent = color => `${color}${emphasized ? '66' : '33'}`
  if (colors.length === 1) return { backgroundColor: translucent(colors[0]), color: 'inherit' }
  const stops = colors.map((color, index) => `${translucent(color)} ${index * 100 / colors.length}% ${(index + 1) * 100 / colors.length}%`)
  return { backgroundImage: `linear-gradient(to bottom, ${stops.join(', ')})`, backgroundColor: 'transparent', color: 'inherit' }
}

export function highlightedSegments(text, sentences = []) {
  // Backend offsets count Unicode characters, while JS offsets count UTF-16 units.
  const chars = Array.from(text)
  const segments = []
  let cursor = 0
  for (const sentence of [...sentences].sort((a, b) => a.start_offset - b.start_offset)) {
    const { start_offset: start, end_offset: end } = sentence
    if (!Number.isInteger(start) || !Number.isInteger(end) || start < cursor || end <= start || end > chars.length) continue
    const original = chars.slice(start, end).join('')
    // Never highlight a stale or mismatched analysis, or replace the user's text.
    if (original !== sentence.sentence_text) continue
    if (start > cursor) segments.push({ text: chars.slice(cursor, start).join(''), themes: [] })
    segments.push({ text: original, themes: sentence.themes || [] })
    cursor = end
  }
  if (cursor < chars.length) segments.push({ text: chars.slice(cursor).join(''), themes: [] })
  return segments
}

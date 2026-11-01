export const tagCategories = { people: 'Pessoas', places: 'Lugares', domains: 'Temas' }

export function entryFields(entry) {
  return {
    title: entry.title ?? '', content_text: entry.content_text,
    ...Object.fromEntries(Object.keys(tagCategories).map((key) =>
      [key, (entry.context_tags?.[key] ?? []).map((tag) => tag.label).join(', ')])),
  }
}

export function entryChanges(entry, fields) {
  const changes = {}
  const title = fields.title.trim() || null
  const content = fields.content_text.trim()
  if (!content) throw new Error('Escreva sua reflexão antes de salvar.')
  if (title?.length > 200) throw new Error('O título deve ter no máximo 200 caracteres.')
  if (content.length > 20000) throw new Error('A reflexão deve ter no máximo 20.000 caracteres.')
  if (title !== entry.title) changes.title = title
  if (content !== entry.content_text) changes.content_text = content
  const originalFields = entryFields(entry)
  const tags = { ...(entry.context_tags ?? {}) }
  let tagsChanged = false
  for (const key of Object.keys(tagCategories)) {
    if (fields[key] === originalFields[key]) continue
    const labels = [...new Set(fields[key].split(',').map((label) => label.trim()).filter(Boolean))]
    if (labels.some((label) => label.length > 100)) throw new Error('Cada tag deve ter no máximo 100 caracteres.')
    tags[key] = labels.map((label) => (entry.context_tags?.[key] ?? []).find((tag) => tag.label === label)
      ?? { label, source: 'user' })
    tagsChanged = true
  }
  if (tagsChanged) changes.context_tags = tags
  return changes
}

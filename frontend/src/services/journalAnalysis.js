export function contextualPassages(analysis) {
  if (!Array.isArray(analysis?.sentences)) return []

  return analysis.sentences.flatMap((sentence) => {
    if (!Array.isArray(sentence.passages)) return []

    return sentence.passages.flatMap((passage) => {
      const snapshot = passage?.payload_snapshot
      if (!snapshot || typeof snapshot.short_text !== 'string' || !snapshot.short_text.trim()) return []
      const sentenceThemes = Array.isArray(sentence.themes) ? sentence.themes : []
      const matchedThemeIds = new Set(
        Array.isArray(snapshot.theme_matches)
          ? snapshot.theme_matches.map(match => match?.theme_id).filter(Boolean)
          : [],
      )
      const passageThemes = matchedThemeIds.size > 0
        ? sentenceThemes.filter(theme => matchedThemeIds.has(theme.id))
        : sentenceThemes

      return [{
        id: passage.id || `${sentence.id}-${passage.passage_id}`,
        passage_id: passage.passage_id,
        sentence_text: sentence.sentence_text,
        themes: passageThemes,
        confidence: passage.confidence,
        reason: passage.reason,
        short_text: snapshot.short_text,
        paraphrase: snapshot.paraphrase,
        interpretation_note: snapshot.interpretation_note,
        locator: snapshot.locator,
        work_title: snapshot.work?.title,
        author_name: snapshot.work?.author_name,
      }]
    })
  })
}

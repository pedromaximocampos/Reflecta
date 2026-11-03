import { useState } from 'react'
import { highlightedSegments, highlightStyle, themeColor } from '../../services/journalHighlights'

export function HighlightedJournalText({
  text,
  sentences = [],
  activeThemeId = null,
  passageThemeIds = new Set(),
  onThemeHover = () => {},
  onThemeSelect = () => {},
}) {
  const [enabled, setEnabled] = useState(true)
  const segments = highlightedSegments(text, sentences)
  const themes = [...new Map(segments.flatMap(segment => segment.themes).map(theme => [theme.id, theme])).values()]
  return <div className="space-y-4">
    {themes.length > 0 && <div className="space-y-3">
      <label className="inline-flex items-center gap-2 text-sm cursor-pointer">
        <input type="checkbox" checked={enabled} onChange={event => setEnabled(event.target.checked)} />
        Destacar frases por tema
      </label>
      <ul aria-label="Legenda dos temas" className="flex flex-wrap gap-2">
        {themes.map(theme => {
          const hasPassage = passageThemeIds.has(theme.id)
          const content = <><span className="h-3 w-3 rounded-full border border-border" style={{ backgroundColor: themeColor(theme) }} aria-hidden="true" />
            {theme.label || theme.slug}</>
          const interactionProps = {
            onMouseEnter: () => onThemeHover(theme.id),
            onMouseLeave: () => onThemeHover(null),
            onFocus: () => onThemeHover(theme.id),
            onBlur: () => onThemeHover(null),
          }
          return <li key={theme.id}>{hasPassage
            ? <button type="button" {...interactionProps} onClick={() => onThemeSelect(theme.id)}
              className={`journal-theme-chip has-passage${activeThemeId === theme.id ? ' is-active' : ''}`}
              title="Ir para a primeira passagem relacionada a este tema">
              {content}
            </button>
            : <span tabIndex={0} {...interactionProps}
              className={`journal-theme-chip${activeThemeId === theme.id ? ' is-active' : ''}`}
              title="Este tema ainda não possui passagem relacionada">
              {content}
            </span>}
          </li>
        })}
      </ul>
      <p className="text-xs text-muted-foreground">As cores indicam os temas sugeridos pela IA. Frases com mais de um tema exibem faixas de cores.</p>
    </div>}
    <p className="whitespace-pre-wrap break-words leading-8">{segments.map((segment, index) => enabled && segment.themes.length > 0
      ? <mark key={index} title={segment.themes.map(theme => theme.label || theme.slug).join(' · ')}
        className={`journal-theme-highlight rounded-sm py-0.5${activeThemeId && segment.themes.some(theme => theme.id === activeThemeId) ? ' is-emphasized' : ''}`}
        style={{ ...highlightStyle(segment.themes, activeThemeId), boxDecorationBreak: 'clone', WebkitBoxDecorationBreak: 'clone' }}>
        {segment.text}
      </mark> : <span key={index}>{segment.text}</span>)}</p>
  </div>
}

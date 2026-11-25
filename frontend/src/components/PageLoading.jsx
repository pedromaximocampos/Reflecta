const VARIANT_LAYOUTS = {
  cards: { blocks: 4, lines: 3 },
  dashboard: { blocks: 4, lines: 4 },
  detail: { blocks: 1, lines: 7 },
  journal: { blocks: 2, lines: 6 },
  list: { blocks: 4, lines: 2 },
  passages: { blocks: 3, lines: 6 },
  table: { blocks: 5, lines: 2 },
  themes: { blocks: 12, lines: 2 },
  works: { blocks: 4, lines: 4 },
}

function SkeletonBlock({ lines, index }) {
  return <div className="page-skeleton-block" aria-hidden="true">
    <div className="page-skeleton-heading">
      <span className="page-skeleton-icon" />
      <span className="page-skeleton-line page-skeleton-line-title" />
      <span className="page-skeleton-pill" />
    </div>
    {Array.from({ length: lines }, (_, line) => <span
      className="page-skeleton-line"
      key={line}
      style={{ '--skeleton-width': `${Math.max(38, 94 - ((line + index) % 4) * 14)}%` }}
    />)}
  </div>
}

export function PageLoading({ variant = 'cards', label = 'Carregando informações…', compact = false }) {
  const layout = VARIANT_LAYOUTS[variant] || VARIANT_LAYOUTS.cards
  return <div className={`page-loading page-loading-${variant}${compact ? ' page-loading-compact' : ''}`} role="status" aria-live="polite" aria-label={label}>
    <div className="page-loading-progress" aria-hidden="true"><span /></div>
    <span className="sr-only">{label}</span>
    <div className="page-skeleton-grid">
      {Array.from({ length: layout.blocks }, (_, index) => <SkeletonBlock key={index} lines={layout.lines} index={index} />)}
    </div>
  </div>
}

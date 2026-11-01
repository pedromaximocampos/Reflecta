import { Children, useCallback, useEffect, useRef, useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'

function getPagination(track, itemCount) {
  if (!track || itemCount === 0) return { currentPage: 1, totalPages: 1, positions: [0] }

  const firstItem = track.firstElementChild
  const itemWidth = firstItem?.getBoundingClientRect().width || 280
  const gap = Number.parseFloat(window.getComputedStyle(track).columnGap) || 0
  const itemStep = itemWidth + gap
  const itemsPerPage = Math.max(1, Math.floor((track.clientWidth + gap) / itemStep))
  const totalPages = Math.max(1, Math.ceil(itemCount / itemsPerPage))
  const maximum = Math.max(0, track.scrollWidth - track.clientWidth)
  const positions = Array.from(
    { length: totalPages },
    (_, index) => Math.min(index * itemsPerPage * itemStep, maximum),
  )
  const currentIndex = positions.reduce(
    (closest, position, index) => (
      Math.abs(position - track.scrollLeft) < Math.abs(positions[closest] - track.scrollLeft)
        ? index
        : closest
    ),
    0,
  )

  return { currentPage: currentIndex + 1, totalPages, positions }
}

export function CatalogCarousel({
  children,
  label,
  title,
  titleId,
  description,
  action = null,
  className = '',
}) {
  const trackRef = useRef(null)
  const [pagination, setPagination] = useState({ currentPage: 1, totalPages: 1 })
  const items = Children.toArray(children)

  const updateControls = useCallback(() => {
    const track = trackRef.current
    const { currentPage, totalPages } = getPagination(track, items.length)
    setPagination((current) => (
      current.currentPage === currentPage && current.totalPages === totalPages
        ? current
        : { currentPage, totalPages }
    ))
  }, [items.length])

  useEffect(() => {
    const track = trackRef.current
    if (!track) return undefined
    const frame = window.requestAnimationFrame(updateControls)
    const observer = typeof ResizeObserver === 'undefined'
      ? null
      : new ResizeObserver(updateControls)
    observer?.observe(track)
    window.addEventListener('resize', updateControls)
    return () => {
      window.cancelAnimationFrame(frame)
      observer?.disconnect()
      window.removeEventListener('resize', updateControls)
    }
  }, [children, updateControls])

  const move = (direction) => {
    const track = trackRef.current
    if (!track) return
    const { currentPage, totalPages, positions } = getPagination(track, items.length)
    const targetPage = Math.min(totalPages, Math.max(1, currentPage + direction))
    setPagination({ currentPage: targetPage, totalPages })
    track.scrollTo({
      left: positions[targetPage - 1],
      behavior: 'smooth',
    })
  }

  const pageLabel = pagination.totalPages > 1
    ? `Página ${pagination.currentPage} de ${pagination.totalPages}`
    : 'Página 1'

  return (
    <div className={`catalog-carousel ${className}`.trim()}>
      <div className="catalog-carousel-heading">
        <div>
          <div className="catalog-carousel-title-line">
            <h2 id={titleId}>{title}</h2>
          </div>
          {description && <p>{description}</p>}
        </div>
        <div className="catalog-carousel-heading-actions">
          {action}
          <div className="catalog-carousel-controls" role="group" aria-label={`Navegar por ${label}`}>
            <button
              type="button"
              className="catalog-carousel-arrow"
              aria-label={`Mostrar página anterior de ${label}`}
              disabled={pagination.currentPage === 1}
              onClick={() => move(-1)}
            >
              <ChevronLeft aria-hidden="true" />
            </button>
            <span className="catalog-carousel-page" aria-live="polite">{pageLabel}</span>
            <button
              type="button"
              className="catalog-carousel-arrow"
              aria-label={`Mostrar próxima página de ${label}`}
              disabled={pagination.currentPage === pagination.totalPages}
              onClick={() => move(1)}
            >
              <ChevronRight aria-hidden="true" />
            </button>
          </div>
        </div>
      </div>
      {items.length > 0 && <div
          ref={trackRef}
          className="catalog-carousel-track"
          aria-label={label}
          onScroll={updateControls}
        >
          {items}
        </div>}
    </div>
  )
}

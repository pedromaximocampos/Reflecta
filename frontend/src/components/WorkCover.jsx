import { useState } from 'react'
import { BookOpen } from 'lucide-react'

export function WorkCover({ work, className = '' }) {
  const [failed, setFailed] = useState(false)
  const imageUrl = work?.cover_image_url?.trim()

  if (imageUrl && !failed) {
    return <img
      className={`work-cover ${className}`.trim()}
      src={imageUrl}
      alt={`Capa de ${work.title}`}
      loading="lazy"
      decoding="async"
      onError={() => setFailed(true)}
    />
  }

  return <div className={`work-cover work-cover-fallback ${className}`.trim()} role="img" aria-label={`Obra sem capa: ${work?.title || 'sem título'}`}>
    <BookOpen size={42} strokeWidth={1.4} aria-hidden="true" />
    <span>Sem capa</span>
  </div>
}

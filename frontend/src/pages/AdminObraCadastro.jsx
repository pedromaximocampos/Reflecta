import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { ArrowLeft, ArrowRight } from 'lucide-react'
import { createWork, uploadWorkCover } from '../services/catalogApi'
import { refreshWorksAndIngestionsCache } from '../services/catalogCache'
import { rememberCatalog } from '../services/catalogState'
import { CatalogWorkSteps } from '../components/CatalogWorkSteps'

export function AdminObraCadastro() {
  const navigate = useNavigate()
  const [coverFile, setCoverFile] = useState(null)
  const [coverPreviewUrl, setCoverPreviewUrl] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const pending = useRef(false)

  useEffect(() => () => {
    if (coverPreviewUrl) URL.revokeObjectURL(coverPreviewUrl)
  }, [coverPreviewUrl])

  async function save(event) {
    event.preventDefault()
    if (pending.current) return
    pending.current = true
    setBusy(true)
    setError('')
    const data = Object.fromEntries(new FormData(event.currentTarget))
    try {
      const work = await createWork({
        title: data.title, synopsis: data.synopsis, type: data.type, language: data.language,
        author: { name: data.author, ...(data.description ? { description: data.description } : {}) },
      })
      rememberCatalog('works', work)
      if (coverFile) {
        try {
          const workWithCover = await uploadWorkCover(work.id, coverFile)
          rememberCatalog('works', workWithCover)
        } catch (coverUploadError) {
          await refreshWorksAndIngestionsCache()
          navigate(`/deshboard/obras/${encodeURIComponent(work.id)}`, {
            state: { coverUploadError: coverUploadError.message },
          })
          return
        }
      }
      await refreshWorksAndIngestionsCache()
      navigate(`/deshboard/obras/${encodeURIComponent(work.id)}/pdf`)
    } catch (err) {
      setError(err.message)
    } finally {
      pending.current = false
      setBusy(false)
    }
  }

  return <div className="catalog-page catalog-work-flow">
    <header><h1>Uma nova fonte de reflexão</h1><p>Primeiro, cadastre os dados da obra. Na próxima etapa, você poderá enviar o PDF.</p></header>
    <CatalogWorkSteps step={1} />
    <form onSubmit={save} className="catalog-card work-registration-card w-full" aria-busy={busy}>
      <fieldset disabled={busy}>
        <h2>Dados da obra</h2>
        <p>Indique o autor do texto enviado, inclusive em introduções e comentários.</p>
        <div className="work-registration-fields">
        {[
          ['title', 'Título', 'Introdução ao Manual de Epicteto'],
          ['author', 'Autor do texto', 'Aldo Dinucci'],
          ['type', 'Tipo', 'academic_introduction'],
          ['language', 'Idioma', 'pt-BR'],
          ['description', 'Descrição do autor (opcional)', ''],
        ].map(([name, label, placeholder]) => <label key={name}>{label}
          {name === 'description' ? <textarea name={name} rows={3} placeholder="Sobre o autor do texto" /> : <input name={name} required placeholder={placeholder} defaultValue={name === 'language' ? 'pt-BR' : name === 'type' ? 'academic_introduction' : ''} />}
        </label>)}
        <label>Capa da obra (opcional)<input type="file" accept="image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp" onChange={(event) => {
          const nextFile = event.target.files[0] || null
          setCoverFile(nextFile)
          setCoverPreviewUrl(nextFile ? URL.createObjectURL(nextFile) : '')
        }} /></label>
        <label>Sinopse<textarea name="synopsis" required rows={3} /></label>
        </div>
        {coverPreviewUrl && <div className="work-cover-preview">
          <img src={coverPreviewUrl} alt="Pré-visualização da capa da obra" />
          <p>{coverFile.name} · {(coverFile.size / 1024 / 1024).toFixed(2)} MB</p>
        </div>}
        {error && <p role="alert" className="text-destructive my-4">{error}</p>}
        <div className="work-registration-actions">
          <Link className="catalog-button inline-flex items-center gap-2" to="/deshboard/obras"><ArrowLeft size={17} aria-hidden="true" />Cancelar</Link>
          <button className="catalog-primary inline-flex items-center gap-2">{busy ? 'Cadastrando…' : 'Cadastrar e continuar'}<ArrowRight size={17} aria-hidden="true" /></button>
        </div>
      </fieldset>
    </form>
  </div>
}

import { useEffect, useState } from 'react'
import { Link, useLocation, useParams } from 'react-router'
import { ArrowLeft, CircleAlert, FileText, ImagePlus, Upload } from 'lucide-react'
import { WorkCover } from '../components/WorkCover'
import { getWork, listWorkIngestions, removeWorkCover, uploadWorkCover } from '../services/catalogApi'
import { rememberCatalog } from '../services/catalogState'
import { formatCatalogDate, formatCatalogDateTime } from '../services/workCatalog'

const workStatuses = { ACTIVE: 'Ativa', INACTIVE: 'Inativa' }

export function AdminObraDetalhe() {
  const { workId } = useParams()
  const location = useLocation()
  const [work, setWork] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [editingCover, setEditingCover] = useState(false)
  const [coverFile, setCoverFile] = useState(null)
  const [coverPreviewUrl, setCoverPreviewUrl] = useState('')
  const [coverBusy, setCoverBusy] = useState(false)
  const [coverError, setCoverError] = useState(location.state?.coverUploadError || '')
  const [coverMessage, setCoverMessage] = useState('')
  const [ingestions, setIngestions] = useState([])

  useEffect(() => {
    let active = true
    getWork(workId).then((data) => { if (active) { rememberCatalog('works', data); setWork(data) } }).catch((err) => { if (active) setError(err.message) }).finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [workId])

  useEffect(() => {
    const controller = new AbortController()
    listWorkIngestions(100)
      .then((data) => {
        if (!controller.signal.aborted) setIngestions(data.ingestions || [])
      })
      .catch(() => {
        if (!controller.signal.aborted) setIngestions([])
      })
    return () => controller.abort()
  }, [workId])

  useEffect(() => () => {
    if (coverPreviewUrl) URL.revokeObjectURL(coverPreviewUrl)
  }, [coverPreviewUrl])

  function selectCover(event) {
    const nextFile = event.target.files[0] || null
    setCoverError('')
    setCoverMessage('')
    if (!nextFile) {
      setCoverFile(null)
      setCoverPreviewUrl('')
      return
    }
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp']
    const valid = nextFile.size > 0 && nextFile.size <= 5 * 1024 * 1024
      && allowedTypes.includes(nextFile.type) && /\.(jpe?g|png|webp)$/i.test(nextFile.name)
    if (!valid) {
      event.target.value = ''
      setCoverFile(null)
      setCoverPreviewUrl('')
      setCoverError('Selecione uma imagem JPEG, PNG ou WebP não vazia, de até 5 MB.')
      return
    }
    setCoverFile(nextFile)
    setCoverPreviewUrl(URL.createObjectURL(nextFile))
  }

  function closeCoverEditor() {
    setEditingCover(false)
    setCoverFile(null)
    setCoverPreviewUrl('')
    setCoverError('')
  }

  async function saveCover(event) {
    event.preventDefault()
    if (coverBusy) return
    setCoverBusy(true)
    setCoverError('')
    setCoverMessage('')
    try {
      if (!coverFile) throw new Error('Selecione uma nova imagem de capa.')
      const updated = await uploadWorkCover(work.id, coverFile)
      rememberCatalog('works', updated)
      setWork(updated)
      setCoverFile(null)
      setCoverPreviewUrl('')
      setEditingCover(false)
      setCoverMessage(work.cover_image_url ? 'Capa alterada.' : 'Capa adicionada.')
    } catch (err) {
      setCoverError(err.message)
    } finally {
      setCoverBusy(false)
    }
  }

  async function removeCover() {
    if (coverBusy || !window.confirm('Remover a capa atual desta obra?')) return
    setCoverBusy(true)
    setCoverError('')
    setCoverMessage('')
    try {
      const updated = await removeWorkCover(work.id)
      rememberCatalog('works', updated)
      setWork(updated)
      setEditingCover(false)
      setCoverFile(null)
      setCoverPreviewUrl('')
      setCoverMessage('Capa removida.')
    } catch (err) {
      setCoverError(err.message)
    } finally {
      setCoverBusy(false)
    }
  }

  if (loading) return <div className="catalog-page"><p role="status">Carregando obra…</p></div>
  if (error || !work) return <div className="catalog-page"><div className="catalog-card"><h1>Não foi possível carregar a obra</h1><p role="alert" className="text-destructive">{error || 'Obra não encontrada.'}</p><Link className="catalog-button inline-flex items-center gap-2 mt-4" to="/deshboard/obras"><ArrowLeft size={16} aria-hidden="true" />Voltar para obras</Link></div></div>

  const counts = work.passage_counts || { total: 0, active: 0, inactive: 0 }
  const displayedWork = coverPreviewUrl ? { ...work, cover_image_url: coverPreviewUrl } : work
  const coverAction = work.cover_image_url ? 'Alterar capa' : 'Adicionar capa'
  const latestFailure = ingestions
    .filter((ingestion) => ingestion.work_id === work.id && ingestion.failure)
    .sort((left, right) => new Date(right.failure.occurred_at) - new Date(left.failure.occurred_at))[0]
  return <div className="catalog-page work-detail-page">
    <Link className="inline-flex items-center gap-2 text-sm text-primary w-fit" to="/deshboard/obras"><ArrowLeft size={16} aria-hidden="true" />Voltar para obras</Link>
    <header className="catalog-page-header"><div><div className="flex items-center gap-3 flex-wrap"><h1>{work.title}</h1><span className={`catalog-badge work-status-${work.status?.toLowerCase()}`}>{workStatuses[work.status] || work.status}</span></div></div><div className="catalog-header-actions"><Link className="catalog-button" to={`/deshboard/passagens?work_id=${encodeURIComponent(work.id)}`}><FileText size={15} aria-hidden="true" />Ver passagens</Link><Link className="catalog-primary" to={`/deshboard/obras/${encodeURIComponent(work.id)}/pdf`}><Upload size={15} aria-hidden="true" />Enviar PDF</Link></div></header>

    {latestFailure && <section className="catalog-card work-operational-failure" aria-labelledby="work-failure-title">
      <CircleAlert size={22} aria-hidden="true" />
      <div>
        <h2 id="work-failure-title">Falha na ingestão da obra</h2>
        <p>{latestFailure.failure.message}</p>
        <span>{formatCatalogDateTime(latestFailure.failure.occurred_at)} · Código: {latestFailure.failure.code}</span>
      </div>
      <Link className="catalog-button catalog-hover-destructive" to={`/deshboard/falhas?source=${encodeURIComponent(latestFailure.failure.source)}&failure_id=${encodeURIComponent(latestFailure.failure.failure_id)}`}>Ver falha operacional</Link>
    </section>}

    <section className="catalog-summary-grid" aria-label="Resumo das passagens da obra">
      {[['Passagens associadas', counts.total], ['Passagens ativas', counts.active], ['Passagens não ativas', counts.inactive]].map(([label, value]) => <article className="catalog-card catalog-summary-card" key={label}><FileText size={22} aria-hidden="true" /><div><p>{label}</p><strong>{value}</strong></div></article>)}
    </section>

    <div className="work-detail-layout">
      <aside className="catalog-card work-detail-cover">
        <WorkCover key={coverPreviewUrl || work.cover_image_url || 'without-cover'} work={displayedWork} />
        {coverPreviewUrl && <p className="work-cover-preview-message" role="status">Pré-visualização da nova capa. Confirme para salvar.</p>}
        {!editingCover && <button className="catalog-button inline-flex items-center justify-center gap-2 w-full" type="button" onClick={() => { setCoverFile(null); setCoverPreviewUrl(''); setCoverError(''); setCoverMessage(''); setEditingCover(true) }}><ImagePlus size={17} aria-hidden="true" />{coverAction}</button>}
        {editingCover && <form className="work-cover-form" onSubmit={saveCover} aria-busy={coverBusy}>
          <fieldset disabled={coverBusy}>
            <label>{work.cover_image_url ? 'Selecionar nova capa' : 'Selecionar capa'}<input type="file" required accept="image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp" onChange={selectCover} /></label>
            <p>JPEG, PNG ou WebP de até 5 MB. A imagem será normalizada antes do armazenamento.</p>
            {coverError && <p role="alert" className="text-destructive">{coverError}</p>}
            <div className="flex gap-2 flex-wrap"><button className="catalog-primary" type="submit">{coverBusy ? (work.cover_image_url ? 'Alterando…' : 'Adicionando…') : coverAction}</button>{work.cover_image_url && <button className="catalog-button text-destructive" type="button" onClick={removeCover}>Remover capa</button>}<button className="catalog-button" type="button" onClick={closeCoverEditor}>Cancelar</button></div>
          </fieldset>
        </form>}
        {coverMessage && <p role="status" className="text-sm text-primary">{coverMessage}</p>}
      </aside>
      <section className="catalog-card work-detail-content">
        <div className="work-detail-content-heading"><h2>Informações da obra</h2><p>Cadastrada em {formatCatalogDate(work.created_at)}</p></div>
        <dl className="work-detail-list">
          <div><dt>Título</dt><dd>{work.title}</dd></div>
          <div><dt>Autor do texto</dt><dd>{work.author?.name || 'Não informado'}</dd></div>
          <div><dt>Tipo</dt><dd>{work.type}</dd></div>
          <div><dt>Idioma</dt><dd>{work.language}</dd></div>
          <div><dt>Descrição do autor</dt><dd>{work.author?.description || 'Não informada'}</dd></div>
          <div><dt>URL da capa</dt><dd>{work.cover_image_url ? <a className="text-primary" href={work.cover_image_url} target="_blank" rel="noreferrer">Abrir capa</a> : 'Não informada'}</dd></div>
          <div className="work-detail-wide"><dt>Sinopse</dt><dd className="whitespace-pre-wrap">{work.synopsis}</dd></div>
        </dl>
      </section>
    </div>
  </div>
}

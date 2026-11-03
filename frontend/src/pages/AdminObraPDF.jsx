import { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router'
import { ArrowLeft, CheckCircle2, FileText, Upload } from 'lucide-react'
import { getWork, uploadWork } from '../services/catalogApi'
import { refreshWorksAndIngestionsCache } from '../services/catalogCache'
import { readCatalog, rememberCatalog } from '../services/catalogState'
import { CatalogWorkSteps } from '../components/CatalogWorkSteps'

export function AdminObraPDF() {
  const { workId } = useParams()
  return <WorkPDF key={workId} workId={workId} />
}

function WorkPDF({ workId }) {
  const [catalog] = useState(readCatalog)
  const [work, setWork] = useState(() => catalog.works.find((item) => item.id === workId) || null)
  const [workLoading, setWorkLoading] = useState(true)
  const [workError, setWorkError] = useState('')
  const [ingestion, setIngestion] = useState(() => catalog.ingestions.find((item) => item.work_id === workId) || null)
  const [file, setFile] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const pending = useRef(false)

  useEffect(() => {
    let active = true
    getWork(workId).then((result) => {
      if (!active) return
      rememberCatalog('works', result)
      setWork(result)
    }).catch((err) => { if (active) setWorkError(err.message) }).finally(() => { if (active) setWorkLoading(false) })
    return () => { active = false }
  }, [workId])

  async function upload(event) {
    event.preventDefault()
    if (!work || pending.current || ingestion) return
    pending.current = true
    setBusy(true)
    setError('')
    try {
      const result = await uploadWork(work.id, file)
      rememberCatalog('ingestions', { ...result, id: result.ingestion_id })
      await refreshWorksAndIngestionsCache()
      setIngestion(result)
    } catch (err) {
      setError(err.message)
    } finally {
      pending.current = false
      setBusy(false)
    }
  }

  if (workLoading && !work) return <div className="catalog-page"><p role="status">Carregando obra…</p></div>
  if (!work) return <div className="catalog-page catalog-work-flow">
    <header><h1>Não foi possível carregar a obra</h1><p>{workError || 'A obra informada não existe no catálogo.'}</p></header>
    <Link className="catalog-primary w-fit" to="/deshboard/obras">Voltar para obras</Link>
  </div>

  return <div className="catalog-page catalog-work-flow">
    <header><h1>{ingestion ? 'PDF enviado para processamento' : 'Agora, envie o PDF'}</h1><p>{ingestion ? 'Acompanhe as passagens sugeridas para iniciar a revisão.' : 'A obra já foi cadastrada. Selecione o documento para solicitar a análise.'}</p></header>
    <CatalogWorkSteps step={2} />
    <div className="catalog-columns">
      <section className="catalog-card">
        {ingestion ? <>
          <CheckCircle2 className="text-primary mb-4" size={32} aria-hidden="true" />
          <h2>Processamento solicitado</h2>
          <p role="status">O envio foi aceito. As passagens podem aparecer aos poucos enquanto o documento é processado.</p>
          <p className="mt-3 text-sm text-muted-foreground">A ausência de passagens ainda não confirma a conclusão do processamento.</p>
          <div className="flex flex-wrap gap-3 mt-6">
            <Link className="catalog-primary" to={`/deshboard/passagens?ingestion_id=${encodeURIComponent(ingestion.ingestion_id)}&work_id=${encodeURIComponent(work.id)}`}>Acompanhar passagens</Link>
            <Link className="catalog-button" to="/deshboard/obras">Voltar para obras</Link>
          </div>
        </> : <form onSubmit={upload} aria-busy={busy}>
          <fieldset disabled={busy}>
            <Upload className="text-primary mb-4" size={28} aria-hidden="true" />
            <h2>Documento da obra</h2>
            <p>Envie um arquivo PDF não vazio, correspondente à obra cadastrada.</p>
            <label>Selecionar PDF<input type="file" accept="application/pdf,.pdf" required onChange={(event) => { setFile(event.target.files[0] || null); setError('') }} /></label>
            {file && <p className="text-sm text-muted-foreground mb-4 break-all">{file.name} · {(file.size / 1024 / 1024).toFixed(2)} MB</p>}
            {error && <p role="alert" className="text-destructive my-4">{error}</p>}
            <button className="catalog-primary" disabled={!file}>{busy ? 'Enviando PDF…' : 'Enviar PDF e iniciar processamento'}</button>
          </fieldset>
        </form>}
      </section>
      <aside className="catalog-card">
        {work.cover_image_url && <img className="work-cover-image" src={work.cover_image_url} alt={`Capa de ${work.title}`} loading="lazy" decoding="async" />}
        <div className="flex items-center gap-2 text-primary mb-4"><FileText size={19} aria-hidden="true" /><span className="text-sm">Obra cadastrada</span></div>
        <h2>{work.title}</h2><p>{work.author?.name}</p>
        <p className="mt-4 whitespace-pre-wrap">{work.synopsis}</p>
        <dl className="mt-5 text-sm space-y-3"><div><dt className="text-muted-foreground">Tipo</dt><dd>{work.type}</dd></div><div><dt className="text-muted-foreground">Idioma</dt><dd>{work.language}</dd></div></dl>
      </aside>
    </div>
    <Link className="inline-flex items-center gap-2 text-sm text-primary w-fit" to="/deshboard/obras"><ArrowLeft size={16} aria-hidden="true" />Voltar para obras</Link>
  </div>
}

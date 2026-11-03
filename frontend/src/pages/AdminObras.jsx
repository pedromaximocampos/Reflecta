import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router'
import {
  BookOpen,
  CheckCircle2,
  CircleAlert,
  Clock3,
  FileText,
  ListFilter,
  LoaderCircle,
  Plus,
  RefreshCw,
} from 'lucide-react'
import { CatalogCarousel } from '../components/CatalogCarousel'
import { WorkCover } from '../components/WorkCover'
import { listWorkIngestions, listWorks } from '../services/catalogApi'
import { readCatalog, replaceCatalog } from '../services/catalogState'
import {
  describeIngestion,
  formatCatalogDate,
  formatCatalogDateTime,
  summarizeWorks,
} from '../services/workCatalog'

const workStatuses = { ACTIVE: 'Ativa', INACTIVE: 'Inativa' }
const ingestionIcons = {
  pending: Clock3,
  processing: LoaderCircle,
  failed: CircleAlert,
  pending_review: FileText,
  completed: CheckCircle2,
}

function CarouselStatusFilter({ label, value, onChange, options }) {
  return <div className="catalog-carousel-filter">
    <button type="button" className="catalog-carousel-filter-trigger" aria-haspopup="true">
      <ListFilter size={14} aria-hidden="true" />Filtrar
      {value && <span aria-label={`Filtro ativo em ${label}`} />}
    </button>
    <div className="catalog-carousel-filter-popover">
      <label htmlFor={`${label}-status-filter`}>Status</label>
      <select id={`${label}-status-filter`} value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="">Todos</option>
        {options.map(([optionValue, optionLabel]) => <option value={optionValue} key={optionValue}>{optionLabel}</option>)}
      </select>
    </div>
  </div>
}

function IngestionCard({ ingestion, work }) {
  const presentation = describeIngestion(ingestion)
  const StatusIcon = ingestionIcons[presentation.status] || Clock3
  const progress = ingestion.progress || {}
  const passagesPath = `/deshboard/passagens?ingestion_id=${encodeURIComponent(ingestion.ingestion_id)}&work_id=${encodeURIComponent(ingestion.work_id)}`
  const detailsPath = presentation.status === 'failed'
    ? `/deshboard/obras/${encodeURIComponent(ingestion.work_id)}`
    : progress.total > 0
    ? passagesPath
    : `/deshboard/obras/${encodeURIComponent(ingestion.work_id)}`
  const detailsLabel = presentation.status === 'failed'
    ? 'Ver falha'
    : progress.total > 0 ? 'Ver passagens' : 'Ver obra'

  return (
    <Link
      className={`catalog-card ingestion-card ingestion-status-${presentation.status}`}
      to={detailsPath}
      aria-label={`${detailsLabel} da ingestão de ${work?.title || ingestion.work_id}`}
    >
      <div className="ingestion-card-heading">
        <span className="ingestion-status-label">
          <StatusIcon
            className={presentation.status === 'processing' ? 'animate-spin' : ''}
            size={17}
            aria-hidden="true"
          />
          {presentation.label}
        </span>
        <span>{formatCatalogDateTime(ingestion.failure?.occurred_at || ingestion.created_at)}</span>
      </div>
      <div>
        <p className="ingestion-card-eyebrow">Ingestão da obra</p>
        <h3>{work?.title || `Obra ${ingestion.work_id.slice(0, 8)}`}</h3>
        <p>{work?.author?.name || 'Autor não informado'}</p>
      </div>
      <div className="ingestion-progress-copy">
        <span>{presentation.detail}</span>
        <strong>{presentation.percentage === null ? '—' : `${presentation.percentage}%`}</strong>
      </div>
      <div
        className={`ingestion-progress-track ${presentation.percentage === null ? 'is-indeterminate' : ''}`}
        role={presentation.percentage === null ? undefined : 'progressbar'}
        aria-label="Progresso do processamento"
        aria-valuemin={presentation.percentage === null ? undefined : 0}
        aria-valuemax={presentation.percentage === null ? undefined : 100}
        aria-valuenow={presentation.percentage ?? undefined}
      >
        <span style={presentation.percentage === null ? undefined : { width: `${presentation.percentage}%` }} />
      </div>
      <div className="ingestion-card-footer">
        <span>{ingestion.attempts} {ingestion.attempts === 1 ? 'tentativa' : 'tentativas'}</span>
        <strong>{detailsLabel} →</strong>
      </div>
    </Link>
  )
}

export function AdminObras() {
  const [initialCatalog] = useState(readCatalog)
  const [works, setWorks] = useState(initialCatalog.works)
  const [ingestions, setIngestions] = useState(initialCatalog.ingestions)
  const [worksLoading, setWorksLoading] = useState(!initialCatalog.loaded.works)
  const [ingestionsLoading, setIngestionsLoading] = useState(!initialCatalog.loaded.ingestions)
  const [worksError, setWorksError] = useState('')
  const [ingestionsError, setIngestionsError] = useState('')
  const [workStatusFilter, setWorkStatusFilter] = useState('')
  const [ingestionStatusFilter, setIngestionStatusFilter] = useState('')

  const loadWorks = useCallback(async () => {
    setWorksLoading(true)
    setWorksError('')
    try {
      const data = await listWorks()
      const nextWorks = data.works || []
      setWorks(nextWorks)
      replaceCatalog('works', nextWorks)
    } catch (error) {
      setWorksError(error.message)
    } finally {
      setWorksLoading(false)
    }
  }, [])

  const loadIngestions = useCallback(async ({ silent = false } = {}) => {
    if (!silent) setIngestionsLoading(true)
    setIngestionsError('')
    try {
      const data = await listWorkIngestions(50)
      const nextIngestions = data.ingestions || []
      setIngestions(nextIngestions)
      replaceCatalog('ingestions', nextIngestions)
    } catch (error) {
      setIngestionsError(error.message)
    } finally {
      if (!silent) setIngestionsLoading(false)
    }
  }, [])

  useEffect(() => {
    let active = true
    const requests = []
    if (!initialCatalog.loaded.works) {
      requests.push({
        kind: 'works',
        request: listWorks().then((data) => data.works || []),
      })
    }
    if (!initialCatalog.loaded.ingestions) {
      requests.push({
        kind: 'ingestions',
        request: listWorkIngestions(50).then((data) => data.ingestions || []),
      })
    }
    if (requests.length === 0) return () => { active = false }
    Promise.allSettled(requests.map(({ request }) => request)).then(
      (results) => {
        if (!active) return
        results.forEach((result, index) => {
          const { kind } = requests[index]
          if (result.status === 'fulfilled') {
            if (kind === 'works') setWorks(result.value)
            else setIngestions(result.value)
            replaceCatalog(kind, result.value)
          } else if (kind === 'works') setWorksError(result.reason.message)
          else setIngestionsError(result.reason.message)
          if (kind === 'works') setWorksLoading(false)
          else setIngestionsLoading(false)
        })
      },
    )
    return () => { active = false }
  }, [initialCatalog])

  const worksById = useMemo(
    () => new Map(works.map((work) => [work.id, work])),
    [works],
  )
  const failedWorkIds = useMemo(
    () => new Set(
      ingestions
        .filter((ingestion) => ingestion.failure)
        .map((ingestion) => ingestion.work_id),
    ),
    [ingestions],
  )
  const summary = summarizeWorks(works)
  const filteredWorks = useMemo(
    () => workStatusFilter
      ? works.filter((work) => work.status === workStatusFilter)
      : works,
    [workStatusFilter, works],
  )
  const filteredIngestions = useMemo(
    () => ingestionStatusFilter
      ? ingestions.filter((ingestion) => describeIngestion(ingestion).status === ingestionStatusFilter)
      : ingestions,
    [ingestionStatusFilter, ingestions],
  )
  const loading = worksLoading || ingestionsLoading

  const refreshAll = async () => {
    await Promise.allSettled([loadWorks(), loadIngestions()])
  }

  return <div className="catalog-page works-catalog-page admin-fixed-page">
    <header className="catalog-page-header catalog-page-intro">
      <div className="catalog-page-intro-copy"><h1>Obras e fontes de reflexão</h1><p>Gerencie as fontes utilizadas para identificar e revisar passagens reflexivas.</p></div>
      <div className="catalog-header-actions">
        <Link className="catalog-primary catalog-hover-primary" to="/deshboard/obras/nova"><Plus size={16} aria-hidden="true" />Nova obra</Link>
        <button className="catalog-button catalog-hover-secondary" onClick={refreshAll} disabled={loading}><RefreshCw size={15} aria-hidden="true" />{loading ? 'Atualizando…' : 'Atualizar informações'}</button>
      </div>
    </header>

    <div className="admin-scroll-region">
    <section className="catalog-summary-grid" aria-label="Resumo do catálogo de obras">
      {[
        ['Obras cadastradas', summary.total, BookOpen],
        ['Obras ativas', summary.active, BookOpen],
        ['Passagens associadas', summary.passages, FileText],
      ].map(([label, value, Icon]) => <article className="catalog-card catalog-summary-card" key={label}>
        <Icon size={22} aria-hidden="true" /><div><p>{label}</p><strong>{value}</strong></div>
      </article>)}
    </section>

    <section className="catalog-overview-section" aria-labelledby="works-section-title">
      <CatalogCarousel
        key={`works-${workStatusFilter}`}
        label="Obras adicionadas"
        title="Obras adicionadas"
        titleId="works-section-title"
        className="works-carousel"
        action={<CarouselStatusFilter label="obras" value={workStatusFilter} onChange={setWorkStatusFilter} options={[["ACTIVE", "Ativas"], ["INACTIVE", "Inativas"]]} />}
      >
        {!worksLoading && !worksError && filteredWorks.map((work) => <Link className="catalog-card work-card" key={work.id} to={`/deshboard/obras/${encodeURIComponent(work.id)}`}>
          <WorkCover work={work} className="work-card-cover" />
          <div className="work-card-content">
            <div className="work-card-heading"><span>{formatCatalogDate(work.created_at)}</span><span className="work-card-statuses"><span className={`catalog-badge work-status-${work.status?.toLowerCase()}`}>{workStatuses[work.status] || work.status}</span>{failedWorkIds.has(work.id) && <span className="catalog-badge work-ingestion-failure"><CircleAlert size={12} aria-hidden="true" />Falha na ingestão</span>}</span></div>
            <h2>{work.title}</h2>
            <p className="work-author">{work.author?.name || 'Autor não informado'}</p>
            <p className="work-synopsis">{work.synopsis}</p>
            <div className="work-card-footer"><span><FileText size={16} aria-hidden="true" />{work.passage_counts?.total || 0} passagens</span><strong>Ver detalhes →</strong></div>
          </div>
        </Link>)}
      </CatalogCarousel>
      {worksError && <div className="catalog-card catalog-state-card works-state-card"><p role="alert" className="text-destructive">{worksError}</p><button className="catalog-button mt-4" onClick={loadWorks}>Tentar novamente</button></div>}
      {worksLoading && !worksError && <p role="status">Carregando obras…</p>}
      {!worksLoading && !worksError && works.length === 0 && <div className="catalog-card catalog-empty-state"><BookOpen size={38} aria-hidden="true" /><h2>Nenhuma obra cadastrada</h2><p>Cadastre a primeira fonte para depois enviar o PDF e iniciar o processamento.</p><Link className="catalog-primary" to="/deshboard/obras/nova">Cadastrar primeira obra</Link></div>}
      {!worksLoading && !worksError && works.length > 0 && filteredWorks.length === 0 && <div className="catalog-card catalog-empty-state"><BookOpen size={34} aria-hidden="true" /><h2>Nenhuma obra neste status</h2><p>Altere o filtro para visualizar outras obras cadastradas.</p></div>}
    </section>

    <section className="catalog-overview-section" aria-labelledby="ingestions-section-title">
      <CatalogCarousel
        key={`ingestions-${ingestionStatusFilter}`}
        label="Últimas ingestões"
        title="Últimas ingestões"
        titleId="ingestions-section-title"
        className="ingestions-carousel"
        action={<CarouselStatusFilter label="ingestões" value={ingestionStatusFilter} onChange={setIngestionStatusFilter} options={[["pending", "Na fila"], ["processing", "Em processamento"], ["pending_review", "Aguardando revisão"], ["completed", "Revisadas"], ["failed", "Com falha"]]} />}
      >
        {!ingestionsLoading && !ingestionsError && filteredIngestions.map((ingestion) => <IngestionCard key={ingestion.ingestion_id} ingestion={ingestion} work={worksById.get(ingestion.work_id)} />)}
      </CatalogCarousel>
      {ingestionsError && <div className="catalog-card catalog-state-card"><p role="alert" className="text-destructive">{ingestionsError}</p><button className="catalog-button mt-4" onClick={() => loadIngestions()}>Tentar novamente</button></div>}
      {ingestionsLoading && !ingestionsError && <p role="status">Carregando ingestões…</p>}
      {!ingestionsLoading && !ingestionsError && ingestions.length === 0 && <div className="catalog-card catalog-empty-state"><FileText size={38} aria-hidden="true" /><h2>Nenhuma ingestão solicitada</h2><p>Envie o PDF de uma obra para acompanhar o processamento aqui.</p></div>}
      {!ingestionsLoading && !ingestionsError && ingestions.length > 0 && filteredIngestions.length === 0 && <div className="catalog-card catalog-empty-state"><FileText size={34} aria-hidden="true" /><h2>Nenhuma ingestão neste status</h2><p>Altere o filtro para visualizar outros processamentos.</p></div>}
    </section>
    </div>
  </div>
}

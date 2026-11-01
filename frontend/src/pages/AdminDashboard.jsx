import { useEffect, useState } from 'react'
import { Link } from 'react-router'
import { listPassages, listThemes, listWorks } from '../services/catalogApi'
import { readCatalog, replaceCatalog } from '../services/catalogState'
export function AdminDashboard() {
  const [initialCatalog] = useState(readCatalog)
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => {
    const themesRequest = initialCatalog.loaded.themes
      ? Promise.resolve(initialCatalog.themes)
      : listThemes().then((result) => {
        const themes = result.themes || []
        replaceCatalog('themes', themes)
        return themes
      })
    const worksRequest = initialCatalog.loaded.works
      ? Promise.resolve(initialCatalog.works)
      : listWorks().then((result) => {
        const works = result.works || []
        replaceCatalog('works', works)
        return works
      })
    Promise.all([themesRequest, listPassages(), worksRequest])
      .then(([themes, passages, works]) => setData({ themes, passages: passages.passages || [], works }))
      .catch((err) => setError(err.message))
  }, [initialCatalog])
  return <div className="catalog-page"><header><h1>Conhecimento com curadoria</h1><p>Da fonte original à passagem aprovada, acompanhe o catálogo.</p></header>{error && <p role="alert" className="text-destructive">{error}</p>}{!data && !error && <p role="status">Carregando catálogo…</p>}{data && <div className="catalog-filters">{[['Temas cadastrados', data.themes.length], ['Obras cadastradas', data.works.length], ['Aguardando revisão', data.passages.filter((item) => item.status === 'PENDING_REVIEW').length], ['Passagens ativas', data.passages.filter((item) => item.status === 'ACTIVE').length]].map(([label, value]) => <div className="catalog-card" key={label}><p>{label}</p><strong className="text-3xl">{value}</strong></div>)}</div>}<div className="catalog-columns">{[['falhas', '00', 'Falhas operacionais', 'Consulte falhas, estados e diagnósticos dos processamentos.'], ['temas', '01', 'Gerenciar temas', 'Defina os temas que orientam as associações da IA.'], ['obras', '02', 'Gerenciar obras e PDFs', 'Preserve as fontes, acompanhe passagens e solicite o processamento.'], ['passagens', '03', 'Revisar passagens', 'Confira a citação, ajuste a explicação e aprove o conteúdo.']].map(([path, number, title, description]) => <Link className="catalog-card admin-dashboard-link" key={path} to={`/deshboard/${path}`}><h2><span>{number}</span><span aria-hidden="true">•</span><span>{title}</span><span aria-hidden="true">→</span></h2><p>{description}</p></Link>)}</div></div>
}

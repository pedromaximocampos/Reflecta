const CATALOG_STORAGE_KEY = 'reflecta_catalog_v3'
const CATALOG_KINDS = new Set(['themes', 'works', 'ingestions'])

function emptyCatalog() {
  return {
    themes: [],
    works: [],
    ingestions: [],
    loaded: { themes: false, works: false, ingestions: false },
    updated_at: null,
  }
}

function getStorage() {
  return typeof localStorage === 'undefined' ? null : localStorage
}

function normalizeCatalog(value) {
  const catalog = emptyCatalog()
  if (!value || typeof value !== 'object') return catalog
  catalog.themes = Array.isArray(value.themes) ? value.themes : []
  catalog.works = Array.isArray(value.works) ? value.works : []
  catalog.ingestions = Array.isArray(value.ingestions) ? value.ingestions : []
  catalog.loaded = {
    themes: value.loaded?.themes === true,
    works: value.loaded?.works === true,
    ingestions: value.loaded?.ingestions === true,
  }
  catalog.updated_at = typeof value.updated_at === 'string' ? value.updated_at : null
  return catalog
}

function saveCatalog(catalog) {
  try {
    getStorage()?.setItem(CATALOG_STORAGE_KEY, JSON.stringify(catalog))
  } catch {
    // Storage may be unavailable in private browsing or restricted environments.
  }
  return catalog
}

function requireCatalogKind(kind) {
  if (!CATALOG_KINDS.has(kind)) throw new Error(`Unsupported catalog cache kind: ${kind}`)
}

export function readCatalog() {
  try {
    const raw = getStorage()?.getItem(CATALOG_STORAGE_KEY)
    return raw ? normalizeCatalog(JSON.parse(raw)) : emptyCatalog()
  } catch {
    return emptyCatalog()
  }
}

export function replaceCatalog(kind, items) {
  requireCatalogKind(kind)
  const catalog = readCatalog()
  catalog[kind] = Array.isArray(items) ? items : []
  catalog.loaded[kind] = true
  catalog.updated_at = new Date().toISOString()
  return saveCatalog(catalog)
}

export function rememberCatalog(kind, item) {
  requireCatalogKind(kind)
  if (!item || typeof item !== 'object') return readCatalog()
  const identity = item.id ?? item.ingestion_id
  const catalog = readCatalog()
  catalog[kind] = [
    item,
    ...catalog[kind].filter((old) => (old.id ?? old.ingestion_id) !== identity),
  ]
  catalog.updated_at = new Date().toISOString()
  return saveCatalog(catalog)
}

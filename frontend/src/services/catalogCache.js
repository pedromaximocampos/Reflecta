import { listThemes, listWorkIngestions, listWorks } from './catalogApi.js'
import { replaceCatalog } from './catalogState.js'

export async function refreshThemesCache() {
  const data = await listThemes()
  const themes = data.themes || []
  replaceCatalog('themes', themes)
  return themes
}

export async function refreshWorksAndIngestionsCache(limit = 50) {
  const requests = await Promise.allSettled([
    listWorks(),
    listWorkIngestions(limit),
  ])
  const [worksResult, ingestionsResult] = requests
  const result = { works: null, ingestions: null, errors: [] }

  if (worksResult.status === 'fulfilled') {
    result.works = worksResult.value.works || []
    replaceCatalog('works', result.works)
  } else {
    result.errors.push(worksResult.reason)
  }

  if (ingestionsResult.status === 'fulfilled') {
    result.ingestions = ingestionsResult.value.ingestions || []
    replaceCatalog('ingestions', result.ingestions)
  } else {
    result.errors.push(ingestionsResult.reason)
  }

  return result
}

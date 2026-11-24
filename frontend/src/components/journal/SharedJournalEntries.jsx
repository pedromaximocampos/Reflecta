import { useState } from 'react'
import { BookOpen, Sparkles } from 'lucide-react'
import { formatPeriodDate } from '../../services/contextPeriod'

function ThemeList({ themes = [] }) {
  if (!themes.length) return null
  return <ul className="shared-journal-themes" aria-label="Temas confirmados">
    {themes.map((theme, index) => <li key={`${theme.label}-${index}`}>
      <span aria-hidden="true" style={{ backgroundColor: theme.color || '#8B5CF6' }} />
      {theme.label}
    </li>)}
  </ul>
}

export function SharedJournalEntries({ entries = [] }) {
  const [selectedIndex, setSelectedIndex] = useState(0)
  const orderedEntries = [...entries].sort((first, second) => String(first.entry_date || '').localeCompare(String(second.entry_date || '')))
  const visibleIndex = orderedEntries.length ? Math.min(selectedIndex, orderedEntries.length - 1) : 0
  const entry = orderedEntries[visibleIndex]

  return <section className="shared-journals" aria-labelledby="shared-journals-title">
    <header className="shared-journals-heading">
      <BookOpen size={20} aria-hidden="true" />
      <div>
        <h2 id="shared-journals-title">Reflexões compartilhadas</h2>
        <p>Textos e interpretações individuais autorizados junto desta análise.</p>
      </div>
    </header>

    {!orderedEntries.length ? <div className="shared-journals-empty">
      <p>As reflexões não foram incluídas neste compartilhamento.</p>
      <small>Este link apresenta somente a análise contextual autorizada.</small>
    </div> : <>
      <label className="shared-journal-selector">
        <span>Reflexão exibida</span>
        <select value={visibleIndex} onChange={event => setSelectedIndex(Number(event.target.value))}>
          {orderedEntries.map((item, index) => <option value={index} key={`${item.entry_date}-${item.title || index}`}>
            {formatPeriodDate(item.entry_date)} — {item.title || 'Reflexão sem título'}
          </option>)}
        </select>
      </label>

      <article className="shared-journal-selected">
        <header className="shared-journal-selected-heading">
          <h3>{entry.title || `Reflexão de ${formatPeriodDate(entry.entry_date)}`}</h3>
          <time dateTime={entry.entry_date}>{formatPeriodDate(entry.entry_date)}</time>
        </header>

        <div className="shared-journal-content">
            <section>
              <h3>Texto da reflexão</h3>
              <p className="shared-journal-original">{entry.content_text}</p>
            </section>

            {entry.analysis ? <div className="shared-journal-analysis">
              <section className="shared-journal-conclusion">
                <div><Sparkles size={17} aria-hidden="true" /><h3>Leitura da IA</h3></div>
                <p>{entry.analysis.conclusion || 'A análise foi concluída sem uma conclusão textual.'}</p>
              </section>

              <section>
                <h3>Temas mantidos pelo usuário</h3>
                <ThemeList themes={entry.analysis.themes} />
                {!entry.analysis.themes?.length && <p className="shared-journal-empty">Nenhum tema foi mantido nesta reflexão.</p>}
              </section>

              {entry.analysis.passages?.length > 0 && <section>
                <h3>Passagens relacionadas</h3>
                <ol className="shared-journal-passages">{entry.analysis.passages.map((passage, passageIndex) => <li key={`${passage.short_text}-${passageIndex}`}>
                  <blockquote>“{passage.short_text}”</blockquote>
                  {(passage.work_title || passage.author_name || passage.locator) && <p className="shared-passage-source">
                    {[passage.work_title, passage.author_name, passage.locator].filter(Boolean).join(' · ')}
                  </p>}
                  <ThemeList themes={passage.themes} />
                  {passage.reason && <div className="shared-passage-explanation">
                    <h4>Por que se relaciona com a reflexão</h4>
                    <p>{passage.reason}</p>
                  </div>}
                  {passage.paraphrase && <details className="shared-passage-paraphrase">
                    <summary>Em outras palavras</summary>
                    <p>{passage.paraphrase}</p>
                  </details>}
                </li>)}</ol>
              </section>}
            </div> : <p className="shared-journal-empty">Esta reflexão não possuía uma análise individual disponível no momento do compartilhamento.</p>}
        </div>
      </article>
    </>}
  </section>
}

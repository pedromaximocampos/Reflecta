import { useState } from 'react';
import { useNavigate } from 'react-router';
import { Lock, Save, FileText } from 'lucide-react';
import { createJournalEntry } from '../services/journalApi';
import { clearSession } from '../services/authSession';
import { defaultContextPeriod } from '../services/contextPeriod';
import { JournalDatePicker } from '../components/journal/JournalDatePicker';

export function Journaling() {
  const navigate = useNavigate();
  const [titulo, setTitulo] = useState('');
  const [conteudo, setConteudo] = useState('');
  const [peopleContext, setPeopleContext] = useState('');
  const [placesContext, setPlacesContext] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [entryDate, setEntryDate] = useState(() => defaultContextPeriod().end_date);


  const today = defaultContextPeriod().end_date;

  function openExistingEntry(entry) {
    const params = new URLSearchParams({
      entry_id: entry.id,
      center_date: entry.entry_date,
    })
    navigate(`/inicio/reflexoes?${params}`)
  }

  return (
    <div className="max-w-screen-2xl mx-auto p-5 md:p-8">
      <header className="catalog-page-header catalog-page-intro mb-6">
        <div className="catalog-page-intro-copy">
          <h1 className="text-3xl">Nova reflexão</h1>
          <p>Registre seus pensamentos no dia em que eles aconteceram.</p>
        </div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Lock className="w-4 h-4" aria-hidden="true" />
          <span>Reflexão pessoal</span>
        </div>
      </header>

      <div className="w-full max-w-4xl mx-auto">
        <p role="note" className="mb-4 text-sm text-muted-foreground">Ao salvar, sua reflexão será enviada automaticamente para análise de IA. Depois, você ainda poderá revisá-la e solicitar uma nova análise.</p>

        <div className="bg-card rounded-2xl shadow-lg border border-border overflow-hidden">
          <div className="bg-gradient-to-r from-secondary/10 to-accent/10 px-5 md:px-8 py-5 border-b border-border flex flex-col sm:flex-row sm:items-center gap-4">
            <input
              aria-label="Título da reflexão"
              type="text"
              value={titulo}
              onChange={(e) => setTitulo(e.target.value)}
              placeholder="Título da reflexão (opcional)"
              className="w-full min-w-0 flex-1 bg-transparent border-none outline-none text-2xl placeholder:text-muted-foreground/50"
            />
            <JournalDatePicker value={entryDate} maxDate={today} onChange={setEntryDate}
              onExistingEntry={openExistingEntry} />
          </div>

          <div className="p-5 md:p-8">
            <div className="relative">
              <div
                className="absolute inset-0 pointer-events-none"
                style={{
                  backgroundImage: 'repeating-linear-gradient(transparent, transparent 39px, rgba(58, 74, 58, 0.08) 39px, rgba(58, 74, 58, 0.08) 40px)',
                }}
              ></div>

              <textarea
                aria-label="Conteúdo da reflexão"
                maxLength={20000}
                value={conteudo}
                onChange={(e) => setConteudo(e.target.value)}
                placeholder="Escreva seus pensamentos aqui... Este é seu espaço seguro para reflexão."
                className="w-full min-h-[400px] bg-transparent border-none outline-none resize-none relative z-10 leading-10"
                style={{ lineHeight: '40px' }}
              />
            </div>
          </div>

          <div className="px-8 pb-6">
            <div className="mb-6 grid gap-4 sm:grid-cols-2">
              <label htmlFor="journal-people" className="space-y-2 text-sm text-muted-foreground">
                <span className="block font-medium text-foreground">Pessoas (opcional)</span>
                <input id="journal-people" type="text" value={peopleContext}
                  onChange={(event) => setPeopleContext(event.target.value)}
                  placeholder="Ex: mãe; João; equipe..."
                  className="w-full px-4 py-2 bg-input-background rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-ring" />
              </label>
              <label htmlFor="journal-places" className="space-y-2 text-sm text-muted-foreground">
                <span className="block font-medium text-foreground">Lugares (opcional)</span>
                <input id="journal-places" type="text" value={placesContext}
                  onChange={(event) => setPlacesContext(event.target.value)}
                  placeholder="Ex: casa; trabalho; faculdade..."
                  className="w-full px-4 py-2 bg-input-background rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-ring" />
              </label>
            </div>

            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                disabled={saving || !conteudo.trim()}
                onClick={async () => {
                  setError('');
                  setSaving(true);
                  try {
                    const toTags = (value) => [...new Set(value.split(';').map((tag) => tag.trim()).filter(Boolean))]
                      .map((label) => ({ label, source: 'user' }));
                    const entry = await createJournalEntry({
                      title: titulo.trim() || null,
                      content_text: conteudo.trim(),
                      entry_date: entryDate,
                      context_tags: {
                        people: toTags(peopleContext),
                        places: toTags(placesContext),
                        domains: [],
                      },
                    });
                    navigate(`/inicio/reflexoes/${entry.id}`);
                  } catch (err) {
                    if (err.status === 401) clearSession();
                    if (err.status === 409 && err.details?.existing_entry_id) {
                      openExistingEntry({
                        id: err.details.existing_entry_id,
                        entry_date: err.details.entry_date || entryDate,
                      })
                      return
                    }
                    setError(err.message || 'Não foi possível salvar a reflexão.');
                  } finally { setSaving(false); }
                }}
                className="flex-1 flex items-center justify-center gap-2 bg-primary text-primary-foreground py-3 rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Save className="w-4 h-4" />
                {saving ? 'Salvando...' : 'Salvar reflexão'}
              </button>
              <button
                disabled title="Em breve"
                className="flex items-center gap-2 px-6 py-3 bg-muted hover:bg-accent rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <FileText className="w-4 h-4" />
                Rascunho
              </button>
            </div>
            {error && <p role="alert" className="mt-3 text-sm text-destructive">{error}</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

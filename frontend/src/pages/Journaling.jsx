import { useState } from 'react';
import { useNavigate } from 'react-router';
import { Lock, Save, FileText } from 'lucide-react';
import { createJournalEntry } from '../services/journalApi';
import { clearSession } from '../services/authSession';

export function Journaling() {
  const navigate = useNavigate();
  const [titulo, setTitulo] = useState('');
  const [conteudo, setConteudo] = useState('');
  const [contexto, setContexto] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');


  const hoje = new Date().toLocaleDateString('pt-BR', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/30 flex items-center justify-center p-5 md:p-8">
      <div className="w-full max-w-4xl">
        <div className="mb-6 flex flex-wrap gap-3 items-center justify-between">
          <div>
            <h1 className="text-3xl mb-1">Meu Diário</h1>
            <p className="text-sm text-muted-foreground capitalize">{hoje}</p>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Lock className="w-4 h-4" />
            <span>Reflexão pessoal</span>
          </div>
        </div>

        <p role="note" className="mb-4 text-sm text-muted-foreground">Ao salvar, sua reflexão será enviada automaticamente para análise de IA e não poderá mais ser editada. Você poderá acompanhar o resultado na próxima tela.</p>

        <div className="bg-card rounded-2xl shadow-lg border border-border overflow-hidden">
          <div className="bg-gradient-to-r from-secondary/10 to-accent/10 px-8 py-6 border-b border-border">
            <input
              aria-label="Título da reflexão"
              type="text"
              value={titulo}
              onChange={(e) => setTitulo(e.target.value)}
              placeholder="Título da reflexão (opcional)"
              className="w-full bg-transparent border-none outline-none text-2xl placeholder:text-muted-foreground/50"
            />
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
            <div className="mb-6">
              <label htmlFor="journal-context" className="block mb-2 text-sm text-muted-foreground">
                Contexto ou tags (opcional)
              </label>
              <input
                id="journal-context"
                type="text"
                value={contexto}
                onChange={(e) => setContexto(e.target.value)}
                placeholder="Ex: trabalho, família, objetivos..."
                className="w-full px-4 py-2 bg-input-background rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>

            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                disabled={saving || !conteudo.trim()}
                onClick={async () => {
                  setError('');
                  setSaving(true);
                  try {
                    const contextTags = contexto.split(',').map((tag) => tag.trim()).filter(Boolean);
                    const entry = await createJournalEntry({
                      title: titulo.trim() || null,
                      content_text: conteudo.trim(),
                      context_tags: { people: [], places: [], domains: contextTags.map((label) => ({ label, source: 'user' })) },
                    });
                    navigate(`/inicio/reflexoes/${entry.id}`);
                  } catch (err) {
                    if (err.status === 401) clearSession();
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

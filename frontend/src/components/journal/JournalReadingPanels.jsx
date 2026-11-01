import { BookOpen, Sparkles, Columns2, Maximize2, PanelLeftClose, PanelRightClose } from 'lucide-react'

export function JournalViewControls({ view, onViewChange }) {
  return <div className="journal-view-controls" role="group" aria-label="Organização dos cards">
    {[
      ['both', 'Lado a lado', Columns2],
      ['reflection', 'Só reflexão', BookOpen],
      ['analysis', 'Só análise', Sparkles],
    ].map(([value, label, Icon]) => <button key={value} type="button" aria-pressed={view === value} onClick={() => onViewChange(value)}>
      <Icon size={16} aria-hidden="true" />{label}
    </button>)}
  </div>
}

export function JournalReadingPanels({ reflection, analysis, view, onViewChange }) {
  return <div className="journal-reading-workspace">
    <div className={`journal-reading-panels journal-view-${view}`}>
      <ReadingPanel name="reflection" title="Sua reflexão" Icon={BookOpen} CloseIcon={PanelLeftClose}
        collapsed={view === 'analysis'} focused={view === 'reflection'}
        onOpen={() => onViewChange('both')} onFocus={() => onViewChange('reflection')} onCollapse={() => onViewChange('analysis')}>
        {reflection}
      </ReadingPanel>
      <ReadingPanel name="analysis" title="Análise da reflexão" Icon={Sparkles} CloseIcon={PanelRightClose}
        collapsed={view === 'reflection'} focused={view === 'analysis'}
        onOpen={() => onViewChange('both')} onFocus={() => onViewChange('analysis')} onCollapse={() => onViewChange('reflection')}>
        {analysis}
      </ReadingPanel>
    </div>
  </div>
}

function ReadingPanel({ name, title, Icon, CloseIcon, collapsed, focused, onOpen, onFocus, onCollapse, children }) {
  const shortTitle = name === 'reflection' ? 'reflexão' : 'análise'
  return <section className={`journal-reading-panel${collapsed ? ' is-collapsed' : ''}`} aria-labelledby={`journal-${name}-heading`}>
    <header className="journal-panel-header">
      <h2 id={`journal-${name}-heading`}><Icon size={19} aria-hidden="true" />{title}</h2>
      {collapsed ? <button type="button" className="journal-panel-reopen" aria-expanded={false} aria-controls={`journal-${name}-body`} onClick={onOpen}>
        <Columns2 size={18} aria-hidden="true" /><span>Abrir {shortTitle} ao lado</span>
      </button> : <div className="journal-panel-actions">
        <button type="button" title={focused ? 'Dividir tela' : `Ampliar ${shortTitle}`} aria-label={focused ? 'Dividir tela' : `Ampliar ${shortTitle}`} onClick={focused ? onOpen : onFocus}>
          {focused ? <Columns2 size={18} aria-hidden="true" /> : <Maximize2 size={17} aria-hidden="true" />}
        </button>
        <button type="button" title={`Recolher ${shortTitle}`} aria-label={`Recolher ${shortTitle}`} aria-expanded={true} aria-controls={`journal-${name}-body`} onClick={onCollapse}>
          <CloseIcon size={18} aria-hidden="true" />
        </button>
      </div>}
    </header>
    <div id={`journal-${name}-body`} className="journal-panel-body" hidden={collapsed} role="region" aria-label={`Conteúdo da ${shortTitle}`} tabIndex={collapsed ? undefined : 0}>
      {children}
    </div>
  </section>
}

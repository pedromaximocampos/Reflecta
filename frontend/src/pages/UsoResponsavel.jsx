import { ArrowLeft, BookOpen, HeartHandshake, LockKeyhole, ShieldCheck } from 'lucide-react'
import { Link } from 'react-router'

export function UsoResponsavel() {
  return <div className="responsible-use-page">
    <header className="home-header">
      <Link to="/" className="home-brand" aria-label="Reflecta — página inicial">
        <BookOpen aria-hidden="true" strokeWidth={1.5} />
        <span>Reflecta</span>
      </Link>
      <div />
      <div className="home-header-actions">
        <Link className="home-login-link" to="/login">Entrar</Link>
        <Link className="home-primary-button" to="/cadastro">Criar conta</Link>
      </div>
    </header>
    <main className="responsible-use-content">
      <Link className="responsible-use-back" to="/"><ArrowLeft size={16} aria-hidden="true" /> Voltar para o início</Link>
      <span className="home-eyebrow"><ShieldCheck size={15} aria-hidden="true" /> Uso responsável</span>
      <h1>Um espaço de reflexão, não uma ferramenta de diagnóstico.</h1>
      <p className="responsible-use-intro">O Reflecta combina escrita pessoal, organização de temas e referências culturais para ajudar você a observar sua própria trajetória com mais atenção.</p>
      <div className="responsible-use-grid">
        <article><HeartHandshake aria-hidden="true" /><h2>Apoio à reflexão</h2><p>As análises organizam o conteúdo escrito e apresentam perspectivas para continuar pensando. Elas não determinam o significado da sua experiência.</p></article>
        <article><ShieldCheck aria-hidden="true" /><h2>Sem diagnóstico</h2><p>O sistema não realiza diagnóstico, tratamento, prevenção ou atendimento psicológico e não deve ser utilizado em situações de emergência.</p></article>
        <article><LockKeyhole aria-hidden="true" /><h2>Compartilhamento sob controle</h2><p>Suas entradas são pessoais. Uma análise só é compartilhada quando você cria deliberadamente um acesso temporário para alguém de sua confiança.</p></article>
      </div>
      <section className="responsible-use-note">
        <h2>Sobre acompanhamento profissional</h2>
        <p>Você pode escolher levar suas reflexões a um profissional como material de apoio para uma conversa. Esse compartilhamento não transforma o Reflecta em prontuário clínico nem substitui uma avaliação realizada por pessoa qualificada.</p>
      </section>
    </main>
  </div>
}

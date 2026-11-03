import { Check } from 'lucide-react'

export function CatalogWorkSteps({ step }) {
  return <ol className="flex flex-wrap gap-4 sm:gap-8 text-sm" aria-label="Etapas do cadastro da obra">
    {['Cadastrar obra', 'Enviar PDF'].map((label, index) => {
      const current = index + 1 === step
      const done = index + 1 < step
      return <li key={label} aria-current={current ? 'step' : undefined} className={`flex items-center gap-3 ${current || done ? 'text-primary' : 'text-muted-foreground'}`}>
        <span className={`inline-flex h-8 w-8 items-center justify-center rounded-full border ${current ? 'bg-primary text-primary-foreground border-primary' : 'border-border bg-card'}`}>
          {done ? <Check size={16} aria-hidden="true" /> : index + 1}
        </span>
        <span className={current ? 'font-medium' : ''}>{label}{done && <span className="sr-only"> — concluída</span>}</span>
      </li>
    })}
  </ol>
}

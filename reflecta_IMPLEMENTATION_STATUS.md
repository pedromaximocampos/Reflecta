# Reflecta - Implementation Status

> **Estado inicial:** ainda não verificado contra o repositório de código.
>
> Este arquivo deve ser atualizado pelo agente que tiver acesso ao projeto real. Nenhum item de documentação deve ser marcado como implementado sem evidência de arquivo, migration, teste ou execução.

---

## 1. Como atualizar este documento

Use os status:

- `NOT_VERIFIED` - documentação existe, código ainda não inspecionado;
- `NOT_STARTED` - código foi inspecionado e não há implementação relevante;
- `PARTIAL` - existe parte funcional/estrutural, mas o caso não está completo;
- `IMPLEMENTED` - implementação encontrada e coerente;
- `TESTED` - implementado e validado por testes relevantes;
- `BLOCKED` - implementação depende de decisão/infra/credencial/contrato;
- `DIVERGENT` - código e documentação estão em conflito significativo.

Sempre adicione **evidência**: caminho de arquivo, migration, teste, endpoint ou comando executado.

---

# 2. Stack real do repositório

| Item | Valor encontrado | Status | Evidência |
|---|---|---|---|
| Linguagem backend | A verificar | NOT_VERIFIED | - |
| Framework backend | A verificar | NOT_VERIFIED | - |
| ORM/data mapper | A verificar | NOT_VERIFIED | - |
| Migration tool | A verificar | NOT_VERIFIED | - |
| Framework frontend | A verificar | NOT_VERIFIED | - |
| UI/component library | A verificar | NOT_VERIFIED | - |
| Test framework backend | A verificar | NOT_VERIFIED | - |
| Test framework frontend | A verificar | NOT_VERIFIED | - |
| PostgreSQL | Documentado | NOT_VERIFIED | projeto ainda não inspecionado |
| pgvector | Modelado | NOT_VERIFIED | projeto ainda não inspecionado |
| Neo4j | Documentado | NOT_VERIFIED | projeto ainda não inspecionado |
| S3 | Documentado | NOT_VERIFIED | projeto ainda não inspecionado |
| SES | Documentado | NOT_VERIFIED | projeto ainda não inspecionado |
| LLM provider | Não especificado nos artefatos atuais | NOT_VERIFIED | - |
| Embedding model | Não especificado | NOT_VERIFIED | - |
| Docker/Compose | A verificar | NOT_VERIFIED | - |
| CI/CD | A verificar | NOT_VERIFIED | - |
| Observabilidade | A verificar | NOT_VERIFIED | - |

---

# 3. Estrutura arquitetural real

| Área | Status | Evidência | Observação |
|---|---|---|---|
| Monólito modular | NOT_VERIFIED | - | decisão documentada |
| Clean Architecture | NOT_VERIFIED | - | decisão para implementação |
| DDD/bounded module boundaries | NOT_VERIFIED | - | verificar dependências reais |
| API/BFF | NOT_VERIFIED | - | verificar forma física |
| Config/env | NOT_VERIFIED | - | - |
| Dependency injection | NOT_VERIFIED | - | se aplicável à stack |

---

# 4. Auth Module

| Capacidade | Status | Evidência | Observação |
|---|---|---|---|
| User model | NOT_VERIFIED | - | - |
| Cadastro | NOT_VERIFIED | - | - |
| Login | NOT_VERIFIED | - | - |
| Password hashing | NOT_VERIFIED | - | - |
| Sessões/tokens | NOT_VERIFIED | - | - |
| Reset de senha | NOT_VERIFIED | - | - |
| Perfil | NOT_VERIFIED | - | - |
| Avatar/S3 | NOT_VERIFIED | - | - |
| Exclusão/anonimização | NOT_VERIFIED | - | - |
| Exportação geral de conta | NOT_VERIFIED | - | - |
| Admin authorization | BLOCKED | - | decisão do modelo precisa ser confirmada |
| MFA | NOT_VERIFIED | - | modelado, prioridade não confirmada |
| E-mail de cadastro/confirmação | NOT_VERIFIED | - | modelagem de email verification incompleta |

---

# 5. Journal Module

| Capacidade | Status | Evidência | Observação |
|---|---|---|---|
| JournalEntry | NOT_VERIFIED | - | - |
| Criar entrada | NOT_VERIFIED | - | texto obrigatório |
| Listar histórico | NOT_VERIFIED | - | - |
| Detalhar entrada | NOT_VERIFIED | - | - |
| Editar entrada | NOT_VERIFIED | - | deve reanalisar quando necessário |
| Excluir entrada | NOT_VERIFIED | - | política lógica/física a verificar |
| Ownership/authorization | NOT_VERIFIED | - | crítico |
| Analysis | NOT_VERIFIED | - | - |
| JournalSentence | NOT_VERIFIED | - | - |
| SentenceTheme | NOT_VERIFIED | - | - |
| confirmação de tema | NOT_VERIFIED | - | - |
| SentencePassage | NOT_VERIFIED | - | - |
| EntryEmbedding | NOT_VERIFIED | - | - |
| SentenceEmbedding | NOT_VERIFIED | - | - |
| DRAFT | BLOCKED | - | enum modelado, fluxo não confirmado |
| versionamento de Analysis | BLOCKED | - | 1:N sem regra explícita de current/version |

---

# 6. AI Processing Module

| Capacidade | Status | Evidência | Observação |
|---|---|---|---|
| LLM port/interface | NOT_VERIFIED | - | - |
| Provider adapter | NOT_VERIFIED | - | - |
| Structured output schema | NOT_VERIFIED | - | obrigatório validar saída |
| Análise de journal | NOT_VERIFIED | - | - |
| Classificação em temas ativos | NOT_VERIFIED | - | não criar tema livre |
| Sentence extraction | NOT_VERIFIED | - | - |
| Embeddings | NOT_VERIFIED | - | - |
| Contexto semântico do usuário | NOT_VERIFIED | - | definição concreta a verificar |
| Processamento de obra | NOT_VERIFIED | - | - |
| Sugestão de passagens | NOT_VERIFIED | - | revisão admin esperada |
| Failure/retry | NOT_VERIFIED | - | - |

---

# 7. Catalog / Knowledge Module

| Capacidade | Status | Evidência | Observação |
|---|---|---|---|
| Neo4j adapter | NOT_VERIFIED | - | - |
| Theme | NOT_VERIFIED | - | - |
| Author | NOT_VERIFIED | - | - |
| Work | NOT_VERIFIED | - | - |
| Passage | NOT_VERIFIED | - | - |
| RELATES_TO | NOT_VERIFIED | - | Passage -> Theme |
| BELONGS_TO | NOT_VERIFIED | - | Passage -> Work |
| WRITTEN_BY | NOT_VERIFIED | - | Work -> Author |
| Admin CRUD themes | NOT_VERIFIED | - | - |
| Admin CRUD works/authors/passages | NOT_VERIFIED | - | - |
| Review/approve/reject passage | NOT_VERIFIED | - | - |
| PDF/capa S3 | NOT_VERIFIED | - | - |
| Work ingestion event | NOT_VERIFIED | - | nome/contrato a confirmar |

---

# 8. Recommendation Module

| Capacidade | Status | Evidência | Observação |
|---|---|---|---|
| RecommendationItem | NOT_VERIFIED | - | responsabilidade x Work precisa confirmar |
| Recommendation | NOT_VERIFIED | - | - |
| Recommendation Engine | NOT_VERIFIED | - | - |
| Consulta Journal por interface | NOT_VERIFIED | - | sem acesso direto ao schema |
| Consulta Catalog por interface | NOT_VERIFIED | - | - |
| Geração assíncrona | NOT_VERIFIED | - | - |
| Reason/explainability | NOT_VERIFIED | - | - |
| Mark viewed | NOT_VERIFIED | - | - |
| Save | NOT_VERIFIED | - | - |
| Dismiss | NOT_VERIFIED | - | modelado em classe, verificar UI/requisito |

---

# 9. Sharing / Professional Module

| Capacidade | Status | Evidência | Observação |
|---|---|---|---|
| SharedExport | NOT_VERIFIED | - | - |
| Seleção de período | NOT_VERIFIED | - | - |
| Permissions | NOT_VERIFIED | - | contrato JSON a definir/verificar |
| Token generation | NOT_VERIFIED | - | - |
| Token hash | NOT_VERIFIED | - | crítico |
| Expiration | NOT_VERIFIED | - | - |
| Revocation | NOT_VERIFIED | - | - |
| ExportSummaryService | NOT_VERIFIED | - | - |
| S3 export | NOT_VERIFIED | - | - |
| Professional public access | NOT_VERIFIED | - | - |
| ProfessionalActivity | NOT_VERIFIED | - | - |
| ConsentService/Repository | BLOCKED | - | entidade de persistência não definida |
| Professional identity/email | BLOCKED | - | modelo de dados incompleto |

---

# 10. Notification Module

| Capacidade | Status | Evidência | Observação |
|---|---|---|---|
| NotificationWorker | NOT_VERIFIED | - | - |
| TemplateRenderer | NOT_VERIFIED | - | - |
| EmailAdapter | NOT_VERIFIED | - | - |
| SES adapter/config | NOT_VERIFIED | - | - |
| NotificationLogRepository | NOT_VERIFIED | - | - |
| UserRegistered notification | NOT_VERIFIED | - | - |
| ProfessionalActivitySuggested notification | NOT_VERIFIED | - | - |

---

# 11. Internal Events / Outbox

| Capacidade | Status | Evidência | Observação |
|---|---|---|---|
| Outbox table/model | NOT_VERIFIED | - | - |
| Transactional outbox write | NOT_VERIFIED | - | crítico |
| Event Dispatcher | NOT_VERIFIED | - | - |
| Event Router | NOT_VERIFIED | - | - |
| ProcessedEvent repository | NOT_VERIFIED | - | - |
| Idempotency | NOT_VERIFIED | - | verificar por consumer |
| Retry/backoff | NOT_VERIFIED | - | - |
| Failure visibility | NOT_VERIFIED | - | admin precisa consultar falhas |
| JournalAnalysisWorker | NOT_VERIFIED | - | - |
| EmbeddingWorker | NOT_VERIFIED | - | - |
| WorkIngestionWorker | NOT_VERIFIED | - | - |
| ReferenceMatchingWorker | NOT_VERIFIED | - | - |
| RecommendationWorker | NOT_VERIFIED | - | - |
| NotificationWorker | NOT_VERIFIED | - | - |

---

# 12. Banco e migrations

| Item | Status | Evidência | Observação |
|---|---|---|---|
| auth_schema | NOT_VERIFIED | - | - |
| journal_schema | NOT_VERIFIED | - | - |
| recommendation_schema | NOT_VERIFIED | - | - |
| sharing_schema | NOT_VERIFIED | - | - |
| event_schema | NOT_VERIFIED | - | - |
| vector extension | NOT_VERIFIED | - | - |
| índices | NOT_VERIFIED | - | planejar após queries reais |
| constraints/uniques | NOT_VERIFIED | - | - |
| soft delete policy | NOT_VERIFIED | - | - |

---

# 13. Frontend

| Tela/fluxo | Status | Evidência | Observação |
|---|---|---|---|
| Cadastro | NOT_VERIFIED | - | mockup no TCC |
| Login | NOT_VERIFIED | - | mockup no TCC |
| Perfil/privacidade | NOT_VERIFIED | - | mockup no TCC |
| Dashboard usuário | NOT_VERIFIED | - | mockup no TCC |
| Journaling | NOT_VERIFIED | - | mockup no TCC |
| Histórico | NOT_VERIFIED | - | requisito, verificar mockup/código |
| Detalhe/análise | NOT_VERIFIED | - | - |
| Recomendações | NOT_VERIFIED | - | mockup no TCC |
| Compartilhamento | NOT_VERIFIED | - | mockup no TCC |
| Atividades/orientações | NOT_VERIFIED | - | mockup no TCC |
| Admin dashboard | NOT_VERIFIED | - | mockup no TCC |
| Admin obras | NOT_VERIFIED | - | mockup no TCC |
| Admin temas | NOT_VERIFIED | - | mockup no TCC |
| Admin passagens/review | NOT_VERIFIED | - | mockup no TCC |
| Admin recomendações culturais | NOT_VERIFIED | - | mockup no TCC |

---

# 14. Testes encontrados no repositório

Preencher após inspeção:

| Test suite | Status | Caminho | Cobertura/escopo |
|---|---|---|---|
| Unit domain | NOT_VERIFIED | - | - |
| Application | NOT_VERIFIED | - | - |
| Repository integration | NOT_VERIFIED | - | - |
| HTTP/API | NOT_VERIFIED | - | - |
| Neo4j integration | NOT_VERIFIED | - | - |
| LLM adapter contract | NOT_VERIFIED | - | - |
| Outbox/idempotency | NOT_VERIFIED | - | - |
| Frontend | NOT_VERIFIED | - | - |
| E2E | NOT_VERIFIED | - | - |

---

# 15. Divergências código x documentação

Preencher usando o formato:

```text
### DIV-001 - Título curto
Status: OPEN | DECIDED | FIXED
Área: Auth / Journal / ...
Documentação diz:
Código diz:
Impacto:
Decisão:
Arquivos/ADR relacionados:
```

Nenhuma divergência pode ser registrada aqui sem evidência do repositório.

---

# 16. Decisões bloqueadoras atuais derivadas da documentação

Estas não são divergências de código; são lacunas do modelo que devem ser verificadas/resolvidas na implementação:

- [ ] Como representar autorização/role de Administrador?
- [ ] Consentimento precisa de entidade própria ou é representado por SharedExport.permissions?
- [ ] Como representar identidade/e-mail do profissional sem exigir conta?
- [ ] RecommendationItem e Work possuem quais responsabilidades canônicas?
- [ ] Analysis mantém histórico? Como marcar a análise corrente?
- [ ] ProcessedEvent precisa de chave `(event_id, consumer_name)`?
- [ ] DRAFT será usado?
- [ ] MFA faz parte desta entrega?
- [ ] Cadastro exige verificação real de e-mail? Onde fica o estado?
- [ ] Qual política de criptografia de content_text existe/será adotada?
- [ ] Exportação geral de conta precisa de job/entity própria?

---

# 17. Próxima ação obrigatória

Quando este arquivo for colocado no repositório, pedir ao agente:

```text
Não implemente nada ainda.
Leia AGENTS.md e PROJECT_CONTEXT.md.
Depois faça um inventário do repositório e substitua os NOT_VERIFIED deste arquivo por estados baseados em evidência.
Inclua caminhos concretos de código/migrations/testes.
Não marque como IMPLEMENTED algo que existe apenas em documentação.
Ao final, apresente as divergências código x documentação e proponha o menor próximo incremento de desenvolvimento.
```

Depois dessa primeira atualização, `IMPLEMENTATION_STATUS.md` passa a funcionar como mapa vivo do desenvolvimento.

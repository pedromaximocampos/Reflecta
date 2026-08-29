# AGENTS.md - Reflecta

Este arquivo contém instruções obrigatórias para qualquer agente de IA trabalhando no repositório.

## 1. Antes de editar qualquer código

Leia, nesta ordem:

1. `PROJECT_CONTEXT.md`
2. `IMPLEMENTATION_STATUS.md`
3. `README.md` e documentação técnica existente no repositório
4. arquivos `.puml`/`.mmd` diretamente relacionados à tarefa
5. migrations, testes e código atual do módulo que será alterado

Se algum desses arquivos não existir na raiz, localize-o antes de concluir que não existe.

## 2. Regra de evidência

Não confunda **documentado** com **implementado**.

Antes de dizer que algo já existe, encontre evidência no código, migration, teste ou configuração.

Ao encontrar diferença entre documentação e código:

- não esconda a divergência;
- determine se o código representa decisão nova, implementação parcial ou erro;
- para mudança irreversível/arquitetural, peça decisão ou registre ADR conforme processo do projeto.

## 3. Identidade e escopo

- Nome atual: **Reflecta**.
- `Individuum` e `Sophia` são nomes históricos.
- Journaling atual: **texto**.
- Áudio e imagem foram removidos do escopo atual.
- Rede social, premium, anúncios, cursos e outras ideias do material conceitual não pertencem automaticamente ao MVP/TCC.

## 4. Arquitetura obrigatória

- Backend em **monólito modular**.
- Aplicar **Clean Architecture + DDD**.
- Não converter para microsserviços sem decisão explícita.
- Domain não depende de framework, ORM, banco, AWS ou SDK de IA.
- Controllers não acessam banco diretamente.
- Regra de negócio não deve ficar em controllers/repositories.
- Um módulo não consulta diretamente tabelas/repositories privados de outro módulo.
- Integração síncrona entre módulos deve usar interfaces públicas/application ports.
- Integração assíncrona deve seguir Outbox/Internal Events quando o fluxo exigir.

Módulos atuais:

- Auth
- Journal
- AI Processing
- Catalog / Knowledge
- Recommendation
- Sharing / Professional
- Notification
- Internal Events

## 5. Persistência

- PostgreSQL: transacional/privado/operacional.
- Schemas atuais: auth, journal, recommendation, sharing, event.
- Neo4j: grafo de conhecimento curado.
- **Nunca armazenar entradas privadas do journaling no Neo4j.**
- S3: PDFs/capas/avatares/exportações conforme caso de uso.
- SES: e-mail.
- Não criar integração/broker novo sem necessidade explícita.

## 6. IA/LLM

- Toda saída de LLM utilizada pelo sistema deve ser tratada como não confiável até validação.
- Preferir saída estruturada com schema.
- Temas canônicos pertencem ao catálogo; o LLM não cria Theme automaticamente.
- Não inventar obra/passagem inexistente para preencher recomendação.
- Minimize conteúdo privado enviado ao provedor.
- Não logar texto de journal ou prompts com conteúdo privado sem necessidade explícita e proteção adequada.

## 7. Eventos

O projeto usa Outbox + workers + Processed Events.

Ao criar/alterar fluxo assíncrono:

- garanta atomicidade entre alteração de negócio e Outbox quando aplicável;
- handler deve ser idempotente;
- retry deve registrar attempts/error/next attempt;
- falha final deve permanecer observável;
- não altere payload/nome de evento de forma incompatível sem avaliar producers/consumers/testes/documentação.

## 8. Segurança e autorização

Em toda feature com dados do usuário:

- validar autenticação;
- validar ownership;
- evitar IDOR;
- não confiar em user_id enviado pelo cliente quando ele puder ser obtido da identidade autenticada;
- não vazar journal em logs/audit;
- respeitar status de token compartilhado: ativo, expirado, revogado;
- nunca armazenar token sensível em plaintext se o modelo prevê hash.

O modelo de autorização do Administrador ainda precisa ser confirmado no código. Não inventar role definitiva sem verificar.

## 9. Inconsistências conhecidas que exigem atenção

Leia a seção "Inconsistências e decisões pendentes" de `PROJECT_CONTEXT.md` antes de migrations.

Em especial:

- numeração divergente de UCs;
- Admin sem role explícita no modelo atual;
- ConsentRepository sem tabela correspondente;
- identidade do profissional incompleta no modelo;
- RecommendationItem x Work;
- histórico/versionamento de Analysis;
- chave de ProcessedEvent por consumidor;
- DRAFT não confirmado no fluxo;
- MFA modelado sem fluxo completo;
- verificação de e-mail não totalmente modelada;
- criptografia de content_text precisa ser verificada.

## 10. Procedimento para cada tarefa

### Antes

1. Declare o caso de uso/módulo afetado.
2. Inspecione implementação existente.
3. Liste rapidamente arquivos prováveis de alteração.
4. Identifique impacto em DB/eventos/API/documentação.
5. Se houver ambiguidade arquitetural importante, não implemente por adivinhação.

### Durante

- faça a menor mudança coerente;
- preserve boundaries;
- reutilize padrões do repositório;
- evite refactor não relacionado;
- escreva/ajuste testes junto com código.

### Depois

Informe:

1. arquivos modificados;
2. comportamento implementado;
3. testes executados e resultado;
4. migrations criadas;
5. eventos/API afetados;
6. decisões/assunções realizadas;
7. documentação atualizada;
8. pendências restantes.

Atualize `IMPLEMENTATION_STATUS.md` quando o estado real do projeto mudar.

## 11. Definition of Done mínima

Uma tarefa relevante só deve ser marcada como pronta após verificar:

- [ ] requisito atendido;
- [ ] regras de domínio no local correto;
- [ ] autorização/ownership;
- [ ] persistência consistente;
- [ ] transações/eventos consistentes;
- [ ] idempotência/retry quando necessário;
- [ ] testes;
- [ ] ausência de dados privados em logs;
- [ ] documentação impactada;
- [ ] status de implementação atualizado.

## 12. Prompt de bootstrap para agente novo

Quando uma IA abrir o repositório pela primeira vez, instrua:

```text
Leia AGENTS.md, PROJECT_CONTEXT.md e IMPLEMENTATION_STATUS.md por completo.
Não altere código ainda.
Inspecione a estrutura, dependências, migrations, módulos, endpoints, testes e configurações existentes.
Depois compare o código real com a documentação e atualize o IMPLEMENTATION_STATUS.md usando somente evidências do repositório.
Liste também divergências e decisões pendentes que bloqueiam implementação.
```

## 13. Regra de ouro

**Não redesenhe o Reflecta. Implemente e evolua o Reflecta já modelado, registrando conscientemente qualquer mudança de decisão.**

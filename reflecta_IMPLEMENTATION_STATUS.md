# Reflecta — Estado real da implementação

> Auditoria focal atualizada em 2026-10-10 após a sincronização do backend desenvolvido na branch
> `feature/atividade-a3-pedro` do repositório acadêmico com este repositório privado.
>
> Este documento registra somente capacidades comprovadas por código, migrations, testes ou execução.
> Diagramas e documentação de produto continuam sendo referência do planejado, não evidência de implementação.

## 1. Legenda

- `IMPLEMENTED`: implementação concreta e verificada no escopo indicado.
- `PARTIAL`: existe implementação relevante, mas o fluxo ainda possui lacunas ou validação externa pendente.
- `NOT_STARTED`: não foi encontrada implementação relevante.
- `BLOCKED`: depende de decisão ou contrato ainda não definido.
- `NOT_VERIFIED`: existe código/configuração, mas a integração real não foi exercitada nesta auditoria.

## 2. Verificações desta atualização

- 829 arquivos rastreados do backend acadêmico foram comparados por SHA-256 após a sincronização;
- `uv sync`: 73 pacotes resolvidos; `pypdf` e stubs S3 adicionados ao ambiente;
- `pytest -q`: **287 testes aprovados**, com oito avisos de depreciação Pydantic;
- `compileall`: código de `src`, `tests` e `alembic` compilado sem erro;
- Alembic: cadeia linear, uma head `a3d9e7f4b612`, banco local na head;
- `alembic check`: nenhuma nova operação de upgrade detectada;
- FastAPI/OpenAPI: aplicação importada e **25 paths / 37 operações HTTP** gerados;
- `git diff --check`: nenhum erro de whitespace; somente avisos de conversão LF/CRLF no Windows;
- integrações AWS e chamada real ao OpenAI não foram reexecutadas neste repositório durante esta atualização.

## 3. Resumo executivo

| Área | Status | Estado real |
|---|---|---|
| Backend/API | PARTIAL | FastAPI expõe Auth, CRUD Journal, análise de Journal, catálogo de temas, criação/ingestão de obras e curadoria de passagens. |
| Monólito modular | PARTIAL | Módulos físicos em `src/modules`, shared técnico em `src/shared` e composição em `src/main`; ainda existem acoplamentos de Presentation e dívidas antigas em Auth. |
| Clean Architecture / DDD | PARTIAL | Entidades, VOs, ports, casos de uso, repositories, UoWs e adapters estão separados nos fluxos recentes; nem todo código legado segue o mesmo rigor. |
| Auth | PARTIAL | Cadastro, login, refresh/logoff, verificação, reset, exclusão lógica, recuperação, perfil e role existem; faltam E2E automatizado e distinção criptográfica entre access/refresh token. |
| Journal | PARTIAL | CRUD com ownership e exclusão lógica está implementado; submissão/consulta de análise e worker existem, mas o pipeline futuro de sentenças, embeddings e referências continua incompleto. |
| AI Processing | PARTIAL | Interpretação de Journal e ingestão de PDF com extração, normalização, chunks, OpenAI, retry local, Inbox e persistência de estado estão implementadas; operação externa não foi revalidada nesta auditoria. |
| Catalog / Knowledge | PARTIAL | CRUD de temas, criação de obra/autor, solicitação de ingestão e CRUD/revisão de passagens existem; faltam listagem/edição de obras e endpoint público de status da ingestão. |
| Recommendation | NOT_STARTED | Não existe módulo funcional. |
| Sharing / Professional | NOT_STARTED | Não existe módulo funcional. |
| Notification | PARTIAL | Handler unificado, SMTP, SES e consumer Lambda/SQS existem; idempotência persistente e deploy reproduzível permanecem pendentes. |
| Internal Events | PARTIAL | Outbox, dispatcher SNS/SQS/RabbitMQ e retries existem; recovery de eventos presos e processed events gerais continuam incompletos. |
| Frontend | NOT_STARTED | Não existe aplicação frontend neste repositório. |

## 4. Stack real

| Tecnologia | Status | Evidência |
|---|---|---|
| Python >= 3.12 / Docker Python 3.14 | IMPLEMENTED | `pyproject.toml`, `Dockerfile` |
| FastAPI / Uvicorn | IMPLEMENTED | `src/main/server/fast_api/` |
| Pydantic / pydantic-settings | IMPLEMENTED | validators dos módulos e `src/shared/config/settings.py` |
| SQLAlchemy assíncrono / asyncpg | IMPLEMENTED | persistência PostgreSQL em `src/shared` e módulos |
| Alembic | IMPLEMENTED | `alembic/`; head `a3d9e7f4b612` aplicada localmente |
| PostgreSQL 16 / pgvector | PARTIAL | Compose, schemas/tabelas e colunas vector; busca vetorial ainda não implementada |
| Neo4j 5.26 / driver assíncrono | IMPLEMENTED | providers compartilhados, UoW e repositories Catalog |
| AWS S3 / boto3 | PARTIAL | adapters Catalog e AI Processing com testes unitários; integração externa não revalidada nesta atualização |
| AWS SNS/SQS | PARTIAL | dispatcher Outbox, publishers e consumer de ingestão; recursos cloud permanecem fora do repositório |
| OpenAI Responses API / httpx | PARTIAL | adapters de análise estruturada com testes; credencial e chamada externa não revalidadas nesta atualização |
| RabbitMQ / aio-pika | PARTIAL | caminho local legado/transicional continua no código e Compose |
| Amazon SES | PARTIAL | notifier e Lambda de e-mail existem; infraestrutura cloud não é versionada como IaC |
| Pytest / pytest-asyncio | IMPLEMENTED | 287 testes aprovados |
| CI/CD | NOT_STARTED | nenhum workflow encontrado |

## 5. Arquitetura real

Estrutura vigente:

```text
src/
  modules/
    auth/
    journal/
    catalog/
    ai_processing/
    internal_events/
    notification/
  shared/
  main/
```

Os fluxos mais recentes usam:

`Presentation -> Application -> Domain <- Infrastructure`

Evidências:

- use cases e DTOs: `src/modules/*/application/`;
- entidades, VOs, eventos e ports: `src/modules/*/domain/`;
- PostgreSQL, Neo4j, S3, SQS e OpenAI: `src/modules/*/infrastructure/`;
- rotas/controllers/validators: `src/modules/*/presentation/`;
- composição: `src/modules/*/bootstrap/` e `src/main/`.

Violações/dívidas ainda observáveis:

1. rotas Journal e Catalog importam a dependency FastAPI privada de Auth;
2. erros compartilhados ainda carregam semântica HTTP dentro de `shared.domain`;
3. `Settings` mantém configuração Pydantic depreciada;
4. partes legadas de Auth ainda usam composição global e possuem riscos de concorrência;
5. `DEBUG` pode expor detalhes internos quando habilitado;
6. não há transação distribuída entre PostgreSQL, S3 e Neo4j; compensação/reconciliação permanece necessária.

## 6. Persistência

### PostgreSQL — PARTIAL

Implementado:

- tabelas Auth e Outbox no schema legado padrão;
- `journal_schema` com entries, analyses, sentenças, associações e embeddings;
- `catalog_schema.work_ingestions`;
- `ai_processing_schema.work_ingestion_chunks`;
- `ai_processing_schema.inbox_events`;
- repositories e UoWs para os fluxos recentes.

Migrations recentes:

- `b81f4e2a9c07_create_catalog_work_ingestions.py`;
- `f6c2a91d4e08_create_ai_processing_chunks.py`;
- `a3d9e7f4b612_create_ai_processing_inbox.py`.

### Neo4j — IMPLEMENTED no código / NOT_VERIFIED externamente nesta atualização

- constraints para Theme, Work, Author e Passage;
- repositories de Theme, Work e Passage;
- relações `WRITTEN_BY`, `BELONGS_TO` e `RELATES_TO`;
- passagens carregam origem, localização, explicação, status, offsets e temas associados.

### S3 — PARTIAL

- Catalog envia o PDF original;
- AI Processing lê o original e persiste texto normalizado/chunks;
- ports e adapters ficam fora do domínio;
- falhas são convertidas em exceções de aplicação.

## 7. Eventos e processamento assíncrono

### Outbox — PARTIAL

- solicitação de ingestão persiste `WorkIngestion` e `catalog.work_ingestion.requested` na mesma transação;
- dispatcher publica eventos no SNS;
- filtros SNS/SQS e DLQ são configuração externa;
- evento só deve ser marcado como enviado após publicação aceita.

### Inbox de AI Processing — IMPLEMENTED

- claim atômico por `event_id`/consumer;
- lease, heartbeat, tentativas, estado de falha e conclusão;
- deduplicação de entrega `at-least-once`;
- migration e testes automatizados.

### Consumer de ingestão — PARTIAL

- long polling SQS;
- parser de mensagem;
- visibility heartbeat durante processamento;
- mensagem só é removida após sucesso;
- falha deixa a mensagem disponível para retry/DLQ;
- recursos AWS, políticas e redrive não são declarados por IaC no repositório.

## 8. IA

### Análise de obras — PARTIAL

Fluxo implementado:

1. recebe evento SQS de ingestão;
2. aplica Inbox/idempotência;
3. baixa o PDF do S3;
4. extrai e normaliza texto;
5. cria chunks com sobreposição e metadados de página/offset;
6. persiste chunks e seus estados no PostgreSQL;
7. envia cada chunk ao OpenAI com schema estrito;
8. valida tema permitido, citação literal, páginas e offsets;
9. descarta sugestão individual inválida sem perder sugestões válidas;
10. persiste passagens candidatas no Neo4j como `PENDING_REVIEW`;
11. retoma somente chunks pendentes/falhos em nova entrega;
12. move a ingestão para revisão ou falha conforme resultado.

Evidências principais:

- `src/modules/ai_processing/application/use_cases/process_work_ingestion/`;
- `src/modules/ai_processing/infrastructure/analysis/openai_work_passage_analyzer.py`;
- `src/modules/ai_processing/infrastructure/document/`;
- `src/modules/ai_processing/infrastructure/messaging/aws_sqs/`;
- `src/modules/ai_processing/infrastructure/persistence/postgresql/`;
- `tests/unit/ai_processing/`.

### Análise de Journal — PARTIAL

- submissão autenticada e consulta do resultado existem;
- worker PostgreSQL seleciona entradas pendentes;
- OpenAI retorna saída estruturada com temas do catálogo ativo;
- análise é persistida atomicamente com a mudança de status;
- ainda faltam o pipeline completo de sentenças, passagens contextuais e embeddings.

## 9. API existente

### Auth

- login, cadastro, refresh, logoff;
- verificação e reset de senha;
- solicitação/confirmação de exclusão lógica;
- solicitação/confirmação de recuperação;
- atualização parcial de perfil.

### Journal

- CRUD autenticado de `/journal/entries`;
- `POST /journal/entries/{id}/analysis`;
- `GET /journal/entries/{id}/analysis`.

### Catalog

- CRUD de `/catalog/themes`;
- `POST /catalog/works`;
- `POST /catalog/works/{work_id}/ingestions` com PDF;
- criação/listagem/detalhe/edição/remoção de passagens;
- aprovação, rejeição, ativação e desativação de passagens;
- filtros de passagem por status, obra e ingestão;
- respostas de passagem incluem `theme_id`, `label` e `confidence`.

Lacunas HTTP relevantes:

- não existe listagem/detalhe/edição de obras;
- não existe endpoint de consulta do estado/erro da ingestão;
- não existe paginação de passagens;
- não existe API operacional para DLQ/reprocessamento.

## 10. Testes

| Área | Status | Evidência |
|---|---|---|
| Auth | IMPLEMENTED unitariamente | `tests/unit/auth/`, testes legados login/logoff atualizados |
| Journal | IMPLEMENTED unitariamente | domínio, CRUD, gateway de análise e persistência |
| Catalog | IMPLEMENTED unitariamente | temas, obras, ingestão, passagens, validators e repositories |
| AI Processing | IMPLEMENTED unitariamente | Inbox, chunks, documentos, S3, SQS, OpenAI, worker e casos de uso |
| Notification | IMPLEMENTED unitariamente | handlers, templates, SES e payloads |
| API E2E real | NOT_STARTED | não existe suíte persistente com FastAPI + PostgreSQL + Neo4j + AWS |
| Integrações cloud | NOT_VERIFIED | dependem da conta e recursos externos |

Resultado atual: **287 passed, 8 warnings**.

## 11. Divergências e riscos atuais

1. documentação histórica ainda usa UUID, enquanto o código usa ULID textual;
2. Auth/Outbox permanecem no schema padrão, enquanto o modelo planejado separa schemas;
3. o repositório preserva RabbitMQ/SMTP junto do caminho alvo SNS/SQS/Lambda/SES;
4. infraestrutura AWS foi configurada manualmente e não possui IaC reproduzível;
5. a ausência de endpoint de status impede o frontend de distinguir processamento, zero resultados e falha;
6. a ingestão cruza PostgreSQL, S3, SQS e Neo4j sem transação distribuída;
7. passagens são persistidas progressivamente; falha posterior exige retomada/reconciliação correta;
8. custos e rate limits do provedor de IA precisam de limites operacionais;
9. conteúdo privado do Journal exige política explícita de retenção, redaction e observabilidade;
10. não há CI, métricas, tracing, health/readiness ou testes E2E automatizados.

## 12. Menor próximo incremento coerente

Para a entrega administrativa atual, o menor incremento vertical é um endpoint autenticado:

```text
GET /catalog/work-ingestions/{ingestion_id}
```

Ele deve retornar status, tentativas, timestamps e um erro sanitizado. Isso permite ao frontend distinguir
`pending`, `processing`, `pending_review`, `completed` e `failed` sem consultar diretamente o banco ou
inferir estado apenas pela presença de passagens. O incremento ainda não foi iniciado.

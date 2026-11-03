# Reflecta — Estado real da implementação

> Auditoria focal atualizada em 2026-11-01 após a sincronização da branch `develop` do repositório
> acadêmico com este repositório de portfólio. Backend e frontend foram sincronizados.
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

- 976 arquivos rastreados do backend e 81 do frontend foram comparados por SHA-256 após a sincronização;
- duas adaptações locais de portabilidade foram aplicadas: `tzdata` explícito e teste sem dependência do nome da pasta raiz;
- `uv sync --locked`: 75 pacotes resolvidos;
- `pytest -q`: **557 testes aprovados, 5 ignorados**, com oito avisos de depreciação Pydantic;
- frontend: **73 testes aprovados**, lint sem erros e build Vite de produção concluído;
- Alembic: cadeia linear, uma head `d8c51a700003`;
- FastAPI/OpenAPI: aplicação importada e **39 paths / 58 operações HTTP** gerados;
- `git diff --check`: nenhum erro de whitespace; somente avisos de conversão LF/CRLF no Windows;
- o fluxo equivalente da branch acadêmica sincronizada foi exercitado manualmente com S3, SNS, SQS,
  OpenAI e Neo4j reais; a execução externa não foi repetida a partir desta cópia privada após a sincronização.

## 3. Resumo executivo

| Área | Status | Estado real |
|---|---|---|
| Backend/API | PARTIAL | FastAPI expõe Auth, Journal, análise contextual, catálogo, ingestão, curadoria, compartilhamento e operações administrativas. |
| Monólito modular | PARTIAL | Módulos físicos em `src/modules`, shared técnico em `src/shared` e composição em `src/main`; ainda existem acoplamentos de Presentation e dívidas antigas em Auth. |
| Clean Architecture / DDD | PARTIAL | Entidades, VOs, ports, casos de uso, repositories, UoWs e adapters estão separados nos fluxos recentes; nem todo código legado segue o mesmo rigor. |
| Auth | PARTIAL | Cadastro, login, refresh/logoff, verificação, reset, exclusão lógica, recuperação, perfil e role existem; faltam E2E automatizado e distinção criptográfica entre access/refresh token. |
| Journal | PARTIAL | CRUD com ownership, análise estruturada, sentenças/temas, conclusão, passagens contextuais, histórico e compartilhamento controlado existem; embeddings continuam incompletos. |
| AI Processing | PARTIAL | Interpretação do Journal, seleção contextual e ingestão de PDF com chunks, OpenAI, validação, retry, Inbox e persistência de estado estão implementadas; faltam E2E cloud automatizado e operação reproduzível. |
| Catalog / Knowledge | PARTIAL | CRUD de temas e passagens, criação/listagem/detalhe de obras, capas, solicitação e acompanhamento de ingestões existem; edição ampla de obras e recuperação automática ainda são lacunas. |
| Recommendation | NOT_STARTED | Não existe módulo funcional. |
| Sharing / Professional | PARTIAL | Análises contextuais podem ser compartilhadas por token, resolvidas publicamente e revogadas; o fluxo completo do profissional ainda não existe. |
| Notification | PARTIAL | Handler unificado, SMTP, SES e consumer Lambda/SQS existem; idempotência persistente e deploy reproduzível permanecem pendentes. |
| Internal Events | PARTIAL | Outbox, dispatcher SNS/SQS/RabbitMQ e retries existem; recovery de eventos presos e processed events gerais continuam incompletos. |
| Operations | PARTIAL | Falhas de Journal e ingestão podem ser listadas/detalhadas; Journal possui reprocessamento administrativo parametrizado. |
| Frontend | PARTIAL | React/Vite em `frontend/` cobre áreas de usuário e administrador; faltam E2E automatizado, acessibilidade sistemática e deploy reproduzível. |

## 4. Stack real

| Tecnologia | Status | Evidência |
|---|---|---|
| Python >= 3.12 / Docker Python 3.14 | IMPLEMENTED | `pyproject.toml`, `Dockerfile` |
| FastAPI / Uvicorn | IMPLEMENTED | `src/main/server/fast_api/` |
| Pydantic / pydantic-settings | IMPLEMENTED | validators dos módulos e `src/shared/config/settings.py` |
| SQLAlchemy assíncrono / asyncpg | IMPLEMENTED | persistência PostgreSQL em `src/shared` e módulos |
| Alembic | IMPLEMENTED | `alembic/`; head versionada `d8c51a700003` |
| PostgreSQL 16 / pgvector | PARTIAL | Compose, schemas/tabelas e colunas vector; busca vetorial ainda não implementada |
| Neo4j 5.26 / driver assíncrono | IMPLEMENTED | providers compartilhados, UoW e repositories Catalog |
| AWS S3 / boto3 | PARTIAL | adapters Catalog e AI Processing, testes unitários e upload/leitura reais exercitados; bucket e políticas permanecem fora do repositório |
| AWS SNS/SQS | PARTIAL | dispatcher, consumers, retry e DLQ existem; `infra/terraform` declara tópico, filas, DLQs, policies e subscriptions, mas ainda não foi importado/aplicado |
| OpenAI Responses API / httpx | PARTIAL | análise estruturada de chunks e validação de respostas exercitadas com o provedor real; faltam E2E automatizado, métricas e limites operacionais |
| RabbitMQ / aio-pika | PARTIAL | caminho local legado/transicional continua no código e Compose |
| Amazon SES | PARTIAL | notifier e Lambda de e-mail existem; infraestrutura cloud não é versionada como IaC |
| Pytest / pytest-asyncio | IMPLEMENTED | 557 testes aprovados e 5 ignorados |
| React / Vite | IMPLEMENTED | `frontend/src`, 73 testes, lint e build aprovados |
| Amazon SES | PARTIAL | notifier e Lambda de e-mail existem; SES e Lambda ainda não fazem parte da cobertura Terraform |
| Terraform / IaC | PARTIAL | primeira fatia SNS/SQS/DLQ versionada em `infra/terraform`; HCL analisado sintaticamente, sem `plan`, import ou `apply` |
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
    operations/
  shared/
  main/
frontend/
  src/
  tests/
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
- `a3d9e7f4b612_create_ai_processing_inbox.py`;
- `a31b7d5e0001_context_analysis_period.py`;
- `b31c72e00002_context_sharing.py`;
- `c7e2b4a91d08_add_user_avatar_object_key.py`;
- `e183a62b07c4_context_analyses.py`;
- `f29a30c3b001_analysis_reprocess_limit.py`;
- `d8c51a700003_admin_analysis_settings.py`.

### Neo4j — IMPLEMENTED

- constraints para Theme, Work, Author e Passage;
- repositories de Theme, Work e Passage;
- relações `WRITTEN_BY`, `BELONGS_TO` e `RELATES_TO`;
- passagens carregam origem, localização, explicação, status, offsets e temas associados.
- persistência e consulta de passagens candidatas foram exercitadas manualmente no Neo4j local.

### S3 — PARTIAL

- Catalog envia o PDF original;
- AI Processing lê o original e persiste texto normalizado/chunks;
- ports e adapters ficam fora do domínio;
- falhas são convertidas em exceções de aplicação.
- upload do PDF, leitura do original e gravação do texto normalizado foram exercitados manualmente
  no bucket de desenvolvimento.

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
- tópico SNS, filas SQS, DLQs, policies, filtros e redrive possuem uma configuração Terraform inicial;
- recursos existentes ainda precisam ser importados e comparados por `plan`; Lambda, SES, S3, bancos e deploy continuam fora dessa cobertura.

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

Validação contra citações inventadas:

1. o schema estruturado exige que o provedor retorne a citação em `exact_text`;
2. o adapter procura primeiro uma correspondência literal dentro do texto original do chunk;
3. quando a extração do PDF introduz espaços, quebras ou hifenização de fim de linha, uma representação
   canônica é usada somente para localizar a origem, preservando os offsets do texto-fonte;
4. o `short_text` persistido é recortado do próprio `chunk_text` pelos offsets encontrados, e não copiado
   cegamente da resposta do modelo;
5. temas inexistentes, citações não localizadas e duplicatas são descartados individualmente com códigos
   como `invalid_theme`, `quote_not_found` e `duplicate_quote`;
6. `paraphrase` e `interpretation_note` continuam sendo conteúdo interpretativo gerado pela IA e ficam
   sujeitos à revisão humana antes da ativação da passagem.

Evidências principais:

- `src/modules/ai_processing/application/use_cases/process_work_ingestion/`;
- `src/modules/ai_processing/infrastructure/analysis/openai_work_passage_analyzer.py`;
- `src/modules/ai_processing/infrastructure/document/`;
- `src/modules/ai_processing/infrastructure/messaging/aws_sqs/`;
- `src/modules/ai_processing/infrastructure/persistence/postgresql/`;
- `src/modules/catalog/infrastructure/persistence/neo4j/repositories/passage_repository.py`;
- `tests/unit/ai_processing/infrastructure/analysis/test_openai_work_passage_analyzer.py`;
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
| Integrações cloud | PARTIAL | fluxo de obras validado manualmente com S3, SNS, SQS/DLQ e OpenAI; configuração ainda é externa e não há suíte E2E reproduzível |

Resultado atual: **287 passed, 8 warnings**.

Validação funcional manual já observada no fluxo de obras:

- criação e manutenção de temas administrativos;
- criação de obra e autor;
- upload de PDF real para o S3;
- publicação Outbox -> SNS -> SQS e consumo assíncrono;
- extração do PDF em 25 chunks no documento exercitado;
- retomada a partir de chunks pendentes/falhos após nova entrega da mensagem;
- respostas estruturadas reais da OpenAI;
- descarte de sugestão cuja citação não existe no chunk (`quote_not_found`);
- persistência de passagens `PENDING_REVIEW` no Neo4j;
- listagem de passagens com citação literal, paráfrase, justificativa e label do tema.

Aprovação e rejeição possuem implementação e testes automatizados, mas a execução manual desses dois
comandos não foi registrada nesta atualização.

## 11. Divergências e riscos atuais

1. documentação histórica ainda usa UUID, enquanto o código usa ULID textual;
2. Auth/Outbox permanecem no schema padrão, enquanto o modelo planejado separa schemas;
3. o repositório preserva RabbitMQ/SMTP junto do caminho alvo SNS/SQS/Lambda/SES;
4. a fatia SNS/SQS possui IaC inicial, mas os recursos manuais ainda não foram importados e o state remoto não foi definido;
5. a ausência de endpoint de status impede o frontend de distinguir processamento, zero resultados e falha;
4. infraestrutura AWS foi configurada manualmente e não possui IaC reproduzível;
5. existe acompanhamento de ingestão, mas o reprocessamento administrativo da mesma ingestão ainda não está implementado;
6. a ingestão cruza PostgreSQL, S3, SQS e Neo4j sem transação distribuída;
7. passagens são persistidas progressivamente; falha posterior exige retomada/reconciliação correta;
8. custos e rate limits do provedor de IA precisam de limites operacionais;
9. conteúdo privado do Journal exige política explícita de retenção, redaction e observabilidade;
10. não há CI para Terraform, métricas, tracing, health/readiness ou testes E2E automatizados.

## 12. Menor próximo incremento coerente

Para a infraestrutura, o menor incremento coerente é instalar a CLI Terraform, executar `init`, importar
os recursos SNS/SQS já criados manualmente e revisar um `plan` sem mudanças inesperadas. Somente depois
devem ser definidos state remoto, automação de CI e expansão para Lambda, SES, S3 ou deploy da aplicação.
O menor próximo incremento de infraestrutura é uma base Terraform isolada para o ambiente de desenvolvimento,
começando pelo caminho assíncrono SNS -> SQS -> DLQ e pelas políticas IAM mínimas. O primeiro passo deve ser
modelar/importar os recursos já existentes sem recriá-los, usar estado fora do Git, revisar o `plan` e somente
depois considerar `apply`. CI/CD, bancos gerenciados e deploy da API ficam fora desse primeiro incremento.

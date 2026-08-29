# Reflecta — Estado real da implementação

> Auditoria realizada em 2026-08-29 sobre o conteúdo existente no repositório.
>
> O arquivo solicitado como `IMPLEMENTATION_STATUS.md` existe neste repositório com o nome
> `reflecta_IMPLEMENTATION_STATUS.md`. Os arquivos operacionais e de contexto seguem a mesma
> convenção: `reflecta_AGENTS.md` e `reflecta_PROJECT_CONTEXT.md`.
>
> Este documento usa código, migrations, configuração e execução como evidência. TCC,
> diagramas, casos de uso, glossário e `reflecta_PROJECT_CONTEXT.md` representam o planejado,
> não provam implementação.

## 1. Legenda e escopo da verificação

- `IMPLEMENTED`: implementação concreta encontrada e coerente no escopo indicado.
- `PARTIAL`: há código ou estrutura relevante, mas o fluxo está incompleto, desconectado ou quebrado.
- `NOT_STARTED`: o repositório foi inspecionado e não contém implementação relevante.
- `BLOCKED`: depende de decisão ou contrato ainda não definido para poder ser concluído coerentemente.
- `NOT_VERIFIED`: há configuração ou código, mas o comportamento real não pôde ser executado no ambiente da auditoria.

Verificações realizadas:

- leitura integral, nesta ordem, de `reflecta_AGENTS.md`, `reflecta_PROJECT_CONTEXT.md` e deste arquivo;
- inventário inicial de 372 arquivos do projeto, excluindo `.git`;
- leitura do código, configurações, dependências, migrations, testes, Docker/Compose, documentação,
  seis diagramas `.puml`, sete diagramas `.mmd`, glossário e as 116 páginas do TCC;
- parsing estático dos arquivos Python atuais: **sem erro de sintaxe**;
- inspeção do grafo de imports: **um ciclo interno em Auth** e nenhum ciclo entre os quatro módulos físicos;
- comparação AST de 215 arquivos Python rastreados afetados pela reorganização: **nenhuma mudança de
  corpo executável além de imports**;
- inspeção Alembic: histórico linear e uma única head `ca9163c93ce6`;
- importação da aplicação FastAPI e geração do OpenAPI com variáveis de processo de auditoria: **sucesso**;
- execução de `pytest -p no:cacheprovider --collect-only -q`: **sete testes coletados com sucesso**;
- execução de `pytest -p no:cacheprovider -q`: **sete erros de setup** causados por fixtures incompatíveis
  com os construtores atuais; nenhum corpo de teste foi executado;
- Docker CLI/Compose foi instalado durante a preparação local; daemon, containers e banco continuam `NOT_VERIFIED` nesta auditoria;
- nenhum serviço externo e nenhum banco real foram acionados.

## 2. Resumo executivo

| Área | Status | Estado real |
|---|---|---|
| Backend/API | PARTIAL | FastAPI sobe e expõe sete rotas Auth; os demais módulos não possuem API funcional. |
| Monólito modular | PARTIAL | Auth, Journal, Internal Events e Notification possuem raízes verticais em `src/modules/`; somente infraestrutura realmente compartilhada permanece horizontal. |
| Clean Architecture / DDD | PARTIAL | Há entidades, portas, casos de uso e adapters, com violações e ciclos de dependência. |
| Auth Module | PARTIAL | É o único módulo substancial; contém falhas que quebram fluxos principais e nenhum teste chega ao corpo de execução. |
| Journal Module | PARTIAL | Entidade e caso de uso embrionário; não há persistência, endpoint nem processamento. |
| AI Processing | NOT_STARTED | Nenhum port, provider, schema, worker ou persistência de IA. |
| Recommendation | NOT_STARTED | Não existe código do módulo; o antigo placeholder vazio foi removido. |
| Catalog / Knowledge | NOT_STARTED | Nenhuma entidade, adapter Neo4j, caso de uso ou API. |
| Sharing / Professional | NOT_STARTED | Nenhuma implementação. |
| Notification | PARTIAL | SMTP, templates e consumidores de e-mail existem, mas a cadeia está desconectada e não usa SES. |
| Internal Events / Outbox | PARTIAL | Outbox e retry existem; publicação e consumo usam brokers incompatíveis e não há idempotência. |
| PostgreSQL | PARTIAL | Seis tabelas Auth/Outbox no schema padrão; execução real não verificada. |
| pgvector | PARTIAL | Dependência e imagem Docker presentes, sem extensão, coluna, migration ou consulta vetorial. |
| Neo4j | NOT_STARTED | Ausente das dependências, Compose e código. |
| Frontend | NOT_STARTED | Não existe aplicação frontend no repositório. |
| Testes automatizados | PARTIAL | Há sete testes unitários Auth desatualizados; a coleta funciona, mas todos falham no setup. |

## 3. Stack real encontrada

| Item | Status | Evidência | Observação |
|---|---|---|---|
| Python 3.12+ | IMPLEMENTED | `pyproject.toml`, `Dockerfile` | Linguagem efetiva do backend. |
| FastAPI / Uvicorn | IMPLEMENTED | `pyproject.toml`, `src/main/server/fast_api/server.py`, `src/main/server/fast_api/run.py` | Aplicação importada com sucesso durante a auditoria. |
| Pydantic / pydantic-settings | IMPLEMENTED | `pyproject.toml`, `src/core/settings.py`, `src/modules/auth/presentation/validators/` | Há warnings de configuração Pydantic legada. |
| SQLAlchemy assíncrono / asyncpg | IMPLEMENTED | `pyproject.toml`, `src/infra/postgresql/connection.py`, `src/modules/auth/infrastructure/persistence/postgresql/models/`, `src/modules/internal_events/infrastructure/persistence/postgresql/models/` | Stack de persistência efetiva. |
| Alembic | IMPLEMENTED | `alembic.ini`, `alembic/env.py`, `alembic/versions/` | Cadeia estática válida, uma head. Aplicação contra banco: `NOT_VERIFIED`. |
| PostgreSQL 16 | PARTIAL | `docker-compose.infra.yml`, `src/infra/postgresql/` | Imagem `pgvector/pgvector:pg16`; banco real não executado. |
| pgvector | PARTIAL | `pyproject.toml`, `docker-compose.infra.yml` | Somente pacote/imagem; sem uso persistente. |
| Argon2 | IMPLEMENTED | `src/modules/auth/infrastructure/security/argon2id_password_hasher.py`, `src/modules/auth/infrastructure/security/configs/argon2/` | Adapter concreto de hash e verificação. |
| JWT / PyJWT | PARTIAL | `src/modules/auth/infrastructure/security/token_service.py`, `src/modules/auth/application/services/auth_session/` | Tokens existem, mas access e refresh não têm tipo/audience distintos. |
| RabbitMQ / aio-pika | PARTIAL | `docker-compose.infra.yml`, publishers/config em `src/modules/internal_events/infrastructure/messaging/rabbitmq/`, consumers em `src/modules/notification/infrastructure/messaging/rabbitmq/` | Publicadores/consumidores existem, mas não formam a cadeia efetiva do outbox. |
| AWS SQS / boto3 | PARTIAL | `src/modules/internal_events/infrastructure/messaging/aws_sqs/`, `src/modules/internal_events/bootstrap/workers/publishers/sqs/sqs_outbox_dispatcher.py` | O dispatcher publica em SQS; não há consumer SQS implementado. |
| SMTP / aiosmtplib | PARTIAL | `src/modules/notification/infrastructure/email/smtp/` | Implementação Gmail/SMTP; entrega externa não verificada. |
| SES | NOT_STARTED | Repositório inteiro inspecionado | Não há adapter/configuração SES. |
| S3 | NOT_STARTED | Repositório inteiro inspecionado | `boto3` é usado apenas para SQS. |
| Neo4j | NOT_STARTED | `pyproject.toml`, Compose e `src/` | Sem driver, serviço ou adapter. |
| Provider de LLM | NOT_STARTED | `pyproject.toml`, `src/` | Nenhum SDK, port ou adapter de IA. |
| Frontend | NOT_STARTED | raiz do repositório | Sem manifesto, fonte, build ou assets de aplicação web. |
| Pytest / pytest-asyncio | PARTIAL | `pyproject.toml`, `tests/` | Sete testes coletam, mas fixtures desatualizadas causam erro no setup. |
| Docker / Compose | PARTIAL | `Dockerfile`, `docker-compose.infra.yml`, `docker-compose.api_workers.yml` | CLI/Compose disponível e entrypoints realinhados; daemon/containers `NOT_VERIFIED`. |
| CI/CD | NOT_STARTED | raiz do repositório | Nenhum workflow/pipeline encontrado. |
| Observabilidade | PARTIAL | `src/main/server/fast_api/server.py`, workers de mensageria | Logging básico; sem métricas, tracing, alertas ou health/readiness. |

Não existe `.env.example` ou equivalente. `src/core/settings.py` declara `.env.dev`, e
`docker-compose.api_workers.yml` também o referencia, mas esse arquivo não está no repositório.

## 4. Arquitetura real

### 4.1 Estrutura e fronteiras

| Capacidade | Status | Evidência | Diagnóstico |
|---|---|---|---|
| Um único backend implantável | IMPLEMENTED | `Dockerfile`, `src/main/server/fast_api/run.py` | É um monólito no sentido de um processo/API principal. |
| Modularidade por bounded context | PARTIAL | `src/modules/auth/`, `src/modules/journal/`, `src/modules/internal_events/`, `src/modules/notification/`, contratos `public/` | Quatro módulos possuem fronteira física; componentes técnicos compartilhados ainda usam raízes horizontais. |
| Separação Domain/Application/Infrastructure/Presentation | PARTIAL | `src/modules/auth/`, `src/modules/journal/`, `src/modules/internal_events/`, `src/modules/notification/` | Auth possui as quatro camadas; Journal só possui Domain/Application porque as demais ainda não foram implementadas. |
| Clean Architecture | PARTIAL | ports/use cases em `src/modules/*/application/` e `domain/`; adapters em `infrastructure/` | Há inversão em vários pontos, mas Domain ainda depende de configuração e semântica HTTP compartilhada. |
| DDD | PARTIAL | entidades/VOs/eventos em `src/modules/auth/domain/` e `src/modules/internal_events/domain/` | Bounded modules físicos foram iniciados, mas agregados, contratos e isolamento de persistência ainda são incompletos. |
| Composition root / DI | PARTIAL | `src/modules/auth/bootstrap/`, `src/modules/internal_events/bootstrap/`, `src/modules/notification/bootstrap/` | Composição é manual e ainda cria instâncias globais reutilizadas entre requests. |
| API/BFF | PARTIAL | `src/modules/auth/presentation/routes.py`, `src/main/server/fast_api/server.py` | Apenas Auth é exposto; não existe frontend nem BFF para os outros módulos. |
| Dependências acíclicas | PARTIAL | `src/modules/auth/infrastructure/persistence/postgresql/models/` | Não há ciclo entre os quatro módulos físicos; persiste um ciclo interno nos models de Auth. |

Dependências entre módulos observadas pelo AST após a separação física:

- `notification -> auth.public, internal_events`;
- `journal -> auth.public` apenas para o tipo público `UserId`;
- `auth -> internal_events.public` e, na composição transacional existente, implementação de Outbox;
- `internal_events` não importa Auth nem Notification.

Não há ciclo entre módulos. Ainda existe acoplamento do Domain de Auth com `src/core/settings.py` e
infraestrutura compartilhada continua fora de `src/modules/`.

### 4.2 Violações arquiteturais comprovadas

1. **Domain depende de configuração:** `src/modules/auth/domain/value_objects/password_plain.py` importa
   `src/core/settings.py`; regras do domínio ficam acopladas ao ambiente.
2. **Domain contém transporte HTTP:** `src/domain/exceptions/domain_error.py` e
   `src/domain/exceptions/api_types/` carregam status/tipos de API dentro do domínio.
3. **Ciclo Infrastructure:** `src/modules/auth/infrastructure/persistence/postgresql/models/__init__.py`
   reexporta models que importam o próprio pacote, formando ciclo interno entre o `__init__` e os models Auth.
4. **Unit of Work global e mutável:** `src/modules/auth/bootstrap/units_of_work.py`,
   `src/modules/auth/bootstrap/use_cases.py` e `src/modules/auth/presentation/routes.py`
   instanciam e reutilizam UoWs/use cases/controllers. `src/infra/postgresql/units_of_work/base_unit_of_work.py`
   mantém sessão mutável; requests concorrentes podem compartilhar estado.
5. **Middleware de autenticação desconectado:** `src/modules/auth/presentation/adapters/fast_api_auth.py` não é
   instalado na aplicação. Os imports locais inválidos desse serviço foram corrigidos apenas para refletir
   a nova estrutura; o middleware continua sem uso nas rotas.
6. **Exceção expõe internals em debug:** `src/main/server/fast_api/fast_api_exception_handler.py`
   pode devolver arquivo, linha e erro bruto; `DEBUG` tem default ativo em `src/core/settings.py`.

## 5. Auth Module

| Capacidade | Status | Evidência | Estado real |
|---|---|---|---|
| User/AuthCredentials model | PARTIAL | `src/modules/auth/domain/entities/user.py`, `src/modules/auth/infrastructure/persistence/postgresql/models/users_model.py`, `auth_credentials_model.py`, migration `1ce1f1cd457b_bancos_agora_em_docker.py` | Existe, mas diverge do modelo planejado e possui mapeamento quebrado. |
| Cadastro | PARTIAL | `src/modules/auth/application/use_cases/signup/`, `src/modules/auth/presentation/controllers/sign_up_controller.py`, `src/modules/auth/presentation/routes.py` | Fluxo substancial; não há teste de cadastro nem E2E e a cadeia de verificação por e-mail não fecha. |
| Login | PARTIAL | `src/modules/auth/application/use_cases/login/`, `src/modules/auth/presentation/controllers/login_controller.py` | Quebra ao buscar usuário por uso incorreto do mapper. |
| Password hashing | IMPLEMENTED | `src/modules/auth/domain/ports/security/ipassword_hasher.py`, `src/modules/auth/infrastructure/security/argon2id_password_hasher.py` | Argon2id concreto com verify/rehash. |
| Geração/validação JWT | PARTIAL | `src/modules/auth/application/ports/token/`, `src/modules/auth/infrastructure/security/token_service.py` | Primitiva existe; access/refresh são indistinguíveis por claim/tipo. |
| Sessões e refresh | PARTIAL | `src/modules/auth/domain/entities/auth_session.py`, `src/modules/auth/application/services/auth_session/`, `src/modules/auth/infrastructure/persistence/postgresql/repositories/auth_sessions_repository.py` | Persistência existe; refresh usa atributo inexistente `_clock`. |
| Logoff | PARTIAL | `src/modules/auth/application/use_cases/logoff/`, `src/modules/auth/presentation/controllers/logoff_controller.py` | Estrutura existe; os dois testes coletam, mas falham no setup por ausência do UoW na fixture. |
| Solicitar reset de senha | PARTIAL | `src/modules/auth/application/use_cases/request_password_reset/`, `src/modules/auth/application/services/reset_password_service/` | Implementação passa repository onde o service espera UoW e falha em runtime. |
| Efetivar reset de senha | PARTIAL | `src/modules/auth/application/use_cases/reset_password/`, `src/modules/auth/infrastructure/persistence/postgresql/repositories/reset_password_repository.py`, migration `0633c30be51a_colocando_tabela_de_reset_de_password_.py` | Estrutura/persistência existem; depende de consultas de usuário quebradas. |
| Verificação de e-mail | PARTIAL | `src/modules/auth/domain/entities/email_verification.py`, `src/modules/auth/application/use_cases/verify_email/`, `src/modules/auth/infrastructure/persistence/postgresql/repositories/user_email_verification_repository.py` | Repositório e service contêm erros funcionais; envio é desconectado. |
| Perfil | NOT_STARTED | `src/` e rotas inspecionados | Nenhum caso de uso/endpoint. |
| Avatar/S3 | NOT_STARTED | `src/` inspecionado | Nenhuma implementação S3. |
| Exclusão/anonimização | NOT_STARTED | `src/` inspecionado | Nenhum caso de uso/endpoint. |
| Exportação geral da conta | NOT_STARTED | `src/` inspecionado | Nenhum job/caso de uso/endpoint. |
| Admin authorization | BLOCKED | `src/modules/auth/domain/entities/user.py`, `src/modules/auth/application/services/http_request_auth/dto.py` | DTO tem `is_admin/roles`, mas não existe modelo persistido, claim ou decisão RBAC. |
| MFA | NOT_STARTED | `src/` inspecionado | Nenhuma implementação. |

Falhas concretas que impedem considerar os casos Auth como `IMPLEMENTED`:

- `src/modules/auth/infrastructure/persistence/postgresql/repositories/user_repository.py` chama
  `UserMapper.to_entity(model=...)`, mas `src/modules/auth/infrastructure/persistence/postgresql/mappers/user_mapper.py` não aceita esse keyword;
- o mesmo repository tenta desempacotar dois valores retornados por `UserMapper.to_model()`, que retorna um;
- `src/modules/auth/application/services/auth_session/auth_session_service_impl.py` usa `self._clock`, mas o
  atributo criado é `self.__system_clock`;
- `src/modules/auth/application/services/email_verification/email_verification_service_impl.py` testa
  `verification.is_expired` sem chamar o método;
- `src/modules/auth/infrastructure/persistence/postgresql/repositories/user_email_verification_repository.py` compara o id com
  `str(UserId)` em vez do valor persistido;
- o login de usuário ainda não verificado emite evento e depois lança exceção antes do commit,
  levando o UoW a rollback;
- `src/modules/auth/application/services/reset_password_service/password_reset_service_impl.py` trata um
  repository recebido como se fosse um UoW;
- `src/modules/auth/domain/value_objects/password_plain.py` referencia `PASSWORD_MIN_LENGTH`, nome inexistente
  em settings, no caminho de erro de senha curta;
- o validator HTTP aceita senha de 8 caracteres, enquanto o domínio exige 12;
- não há autenticação/autorização instalada nas rotas.

## 6. Journal Module

| Capacidade | Status | Evidência | Estado real |
|---|---|---|---|
| Entidade JournalEntry | PARTIAL | `src/modules/journal/domain/entities/journal_entry.py`, `src/modules/journal/domain/value_objects/` | Entidade rica existe, sem model/repository concreto/migration. |
| Criar entrada | PARTIAL | `src/modules/journal/application/use_cases/create_entry/` | Cria entidade `DRAFT`, mas nunca chama repository; apenas faz commit. |
| Port de repository/UoW | PARTIAL | `src/modules/journal/domain/ports/repositories/`, `src/modules/journal/domain/ports/units_of_work/` | Interfaces sem implementação. |
| Endpoint Journal | NOT_STARTED | `src/modules/journal/`, `src/main/server/fast_api/server.py` | Não existe camada Presentation/router Journal e nada é incluído no servidor. |
| Persistência Journal | NOT_STARTED | models em `src/modules/auth/`, `src/modules/internal_events/` e `alembic/versions/` | Nenhum model, repository, UoW concreto ou tabela Journal. |
| Listar histórico | NOT_STARTED | `src/` inspecionado | Ausente. |
| Detalhar entrada | NOT_STARTED | `src/` inspecionado | Ausente. |
| Editar/reanalisar | NOT_STARTED | `src/` inspecionado | Ausente. |
| Excluir entrada | NOT_STARTED | `src/` inspecionado | Ausente. |
| Ownership/authorization | NOT_STARTED | caso de uso `create_entry`, rotas | DTO recebe `user_id` do cliente; não há identidade autenticada. |
| Analysis persistida | NOT_STARTED | `src/` e migrations inspecionados | Campos parciais estão embutidos na entidade; não existe entidade/tabela Analysis. |
| JournalSentence / SentenceTheme / SentencePassage | NOT_STARTED | `src/` inspecionado | Ausentes. |
| EntryEmbedding / SentenceEmbedding | NOT_STARTED | `src/` inspecionado | O antigo placeholder vazio foi removido; não existe implementação. |
| DRAFT | PARTIAL | `src/modules/journal/domain/value_objects/journal_entry_status.py`, caso de uso create | Existe no código, mas o contrato do fluxo e a passagem a `PENDING_ANALYSIS` não existem. |
| Versionamento de Analysis | BLOCKED | documentação e ausência em `src/` | Não há decisão sobre histórico/análise vigente. |

## 7. Demais módulos de negócio

### 7.1 AI Processing

| Capacidade | Status | Evidência |
|---|---|---|
| LLM port/provider/structured output | NOT_STARTED | `pyproject.toml` e `src/` inspecionados |
| Análise de journals | NOT_STARTED | `src/` inspecionado |
| Classificação por temas ativos | NOT_STARTED | `src/` inspecionado |
| Extração por sentenças | NOT_STARTED | `src/` inspecionado |
| Embeddings | NOT_STARTED | `src/` e migrations inspecionados |
| Contexto semântico/histórico do usuário | BLOCKED | UC18 não possui modelo documental canônico nem implementação |
| Processamento de obras/referências | NOT_STARTED | `src/` inspecionado |
| Persistência de resultados | NOT_STARTED | models e migrations inspecionados |
| Tratamento de falhas de IA | NOT_STARTED | `src/` inspecionado |

### 7.2 Catalog / Knowledge

| Capacidade | Status | Evidência |
|---|---|---|
| Neo4j adapter/config | NOT_STARTED | `pyproject.toml`, Compose e `src/` |
| Theme / Author / Work / Passage | NOT_STARTED | `src/` inspecionado |
| Relações RELATES_TO / BELONGS_TO / WRITTEN_BY | NOT_STARTED | `src/` inspecionado |
| CRUD e revisão administrativa | NOT_STARTED | rotas e `src/` inspecionados |
| PDF/capa S3 e ingestão | NOT_STARTED | `src/` inspecionado |
| Estados de processamento de Work | BLOCKED | documentação contradiz o próprio enum `CatalogStatus` |

### 7.3 Recommendation

| Capacidade | Status | Evidência |
|---|---|---|
| Entidade Recommendation | NOT_STARTED | `src/` inspecionado; o antigo placeholder vazio foi removido |
| Engine/geração assíncrona | NOT_STARTED | `src/` inspecionado |
| Consulta Journal/Catalog por contrato | NOT_STARTED | `src/` inspecionado |
| Explainability/reason | NOT_STARTED | `src/` inspecionado |
| Viewed/save/dismiss | NOT_STARTED | `src/` inspecionado |

### 7.4 Sharing / Professional

| Capacidade | Status | Evidência |
|---|---|---|
| SharedExport e seleção de período | NOT_STARTED | `src/` e migrations inspecionados |
| Token/hash/expiração/revogação | NOT_STARTED | `src/` inspecionado |
| Resumo/export S3 | NOT_STARTED | `src/` inspecionado |
| Acesso público profissional | NOT_STARTED | rotas inspecionadas |
| ProfessionalActivity | NOT_STARTED | `src/` inspecionado |
| Consentimento | BLOCKED | documentação traz service/repository, mas não define entidade canônica |
| Identidade, envio e auditoria de acesso profissional | BLOCKED | mockup e modelo de dados são incompatíveis |

## 8. Backend/API

A aplicação importada expõe exatamente estas rotas de negócio:

| Método e rota | Status | Evidência | Observação |
|---|---|---|---|
| `POST /auth/signup` | PARTIAL | `src/modules/auth/presentation/routes.py`, `src/modules/auth/presentation/controllers/sign_up_controller.py` | Única rota com request body documentado no OpenAPI; resposta real 201, spec gerada anuncia 200/422. |
| `POST /auth/login` | PARTIAL | mesmos paths, `login_controller.py` | Usa Basic Auth fora do contrato OpenAPI e falha na consulta via mapper. |
| `POST /auth/logoff` | PARTIAL | `logoff_controller.py` | Sem security scheme no OpenAPI. |
| `POST /auth/refresh` | PARTIAL | `refresh_controller.py` | Depende de cookie; service contém erro `_clock`. |
| `POST /auth/request-reset-password` | PARTIAL | `request_reset_password_controller.py` | Não declara body no OpenAPI e o service recebe dependência incompatível. |
| `POST /auth/reset-password` | PARTIAL | `reset_password_controller.py` | Não declara body no OpenAPI. |
| `GET /auth/verify-email` | PARTIAL | `verify_email_controller.py` | Declara `code` em query; repository/service possuem erros. |
| Demais endpoints planejados | NOT_STARTED | `src/main/server/fast_api/server.py`, módulos inspecionados | Journal não possui Presentation; não há Profile, AI, Recommendation, Sharing, Catalog/Admin ou Notification API. |

DTOs e validators existem principalmente em `src/modules/auth/application/use_cases/*/dto.py` e
`src/modules/auth/presentation/validators/`, mas login/reset não estão integrados ao schema FastAPI de modo a
gerar contrato OpenAPI. Todas as rotas têm `security: []` na spec gerada.

## 9. Persistência e migrations

### 9.1 Estado real do PostgreSQL

| Item | Status | Evidência | Estado real |
|---|---|---|---|
| Metadata SQLAlchemy | IMPLEMENTED | `src/infra/postgresql/configs/base.py`, models em `src/modules/auth/` e `src/modules/internal_events/` | Seis tabelas são registradas. |
| Tabela `users` | PARTIAL | `users_model.py`, migration `1ce1f1cd457b_bancos_agora_em_docker.py` | Auth parcial; campos divergentes do planejado. |
| Tabela `auth_credentials` | PARTIAL | `auth_credentials_model.py`, mesma migration | Sem MFA/credential_type documentados. |
| Tabela `auth_sessions` | PARTIAL | `auth_sessions_model.py`, mesma migration | Sem IP/user-agent; refresh token hash existe. |
| Tabela `user_email_verifications` | PARTIAL | `user_email_verification_model.py`, mesma migration | Implementação adicional ao modelo consolidado, mas fluxo está quebrado. |
| Tabela `passwords_reset` | PARTIAL | `reset_password_model.py`, migration `0633c30be51a_colocando_tabela_de_reset_de_password_.py` | Nome e modelo divergem da documentação. |
| Tabela `outbox` | PARTIAL | `outbox_model.py`, migrations `631fd4384bca_criando_tabela_do_pattern_outbox_nao_.py` e `ca9163c93ce6_01_09_2026_atualizando_a_tabela_de_.py` | Suporta estados/retry, sem contrato documentado completo. |
| Cadeia Alembic | IMPLEMENTED | `alembic/versions/` | Uma head; `4c9d09eb81e5_criando_tabela_do_pattern_outbox.py` é migration vazia. |
| Execução em PostgreSQL real | NOT_VERIFIED | `docker-compose.infra.yml` | Docker CLI/Compose está disponível, mas daemon, container e conexão com o banco não foram verificados nesta análise. |
| `auth_schema` | NOT_STARTED | models/migrations | Todas as tabelas usam o schema padrão (`schema=None`). |
| `journal_schema` | NOT_STARTED | models/migrations | Ausente. |
| `recommendation_schema` | NOT_STARTED | models/migrations | Ausente. |
| `sharing_schema` | NOT_STARTED | models/migrations | Ausente. |
| `event_schema` | NOT_STARTED | models/migrations | Outbox usa schema padrão. |
| Extensão/colunas/índices pgvector | NOT_STARTED | migrations/models | Nenhum `CREATE EXTENSION`, `VECTOR`, dimensão ou índice. |
| Neo4j | NOT_STARTED | projeto inteiro | Ausente. |
| Relação PostgreSQL–Neo4j | NOT_STARTED | projeto inteiro | Ausente. |

Os identificadores persistidos são strings ULID de 26 caracteres, não UUID. O downgrade da migration
que adiciona o valor `PROCESSING` ao enum do outbox não remove esse valor.

`src/core/settings.py` monta `database_url` usando `POSTGRES_PORT` também na posição do host; essa URL
é inválida para a configuração nominal e aumenta o risco de falha fora do caminho atual de conexão.

## 10. Eventos, Outbox e workers

| Capacidade | Status | Evidência | Estado real |
|---|---|---|---|
| Entidade/model/tabela Outbox | PARTIAL | `src/modules/internal_events/domain/entities/outbox_event.py`, `src/modules/internal_events/infrastructure/persistence/postgresql/models/outbox_model.py`, migrations Outbox | Estrutura real existe e diverge do contrato documentado. |
| Escrita transacional Auth + Outbox | PARTIAL | `src/modules/internal_events/application/services/outbox_service_impl.py`, `src/modules/auth/infrastructure/persistence/postgresql/units_of_work/auth_unit_of_work_impl.py`, casos signup/reset | Usa o mesmo UoW, mas os fluxos possuem erros e não foram integrados. |
| Claim concorrente | IMPLEMENTED | `src/modules/internal_events/infrastructure/persistence/postgresql/repositories/outbox_repository.py` | Usa `FOR UPDATE SKIP LOCKED`, marca `PROCESSING` e incrementa tentativas. |
| Retry/backoff | PARTIAL | `src/modules/internal_events/infrastructure/strategies/exponential_retry.py`, `src/modules/internal_events/infrastructure/messaging/workers/publishers/base_sqs_publisher_worker.py` | Backoff existe; evento abandonado em `PROCESSING` não é recuperado após crash. |
| Dispatcher | PARTIAL | `src/modules/internal_events/bootstrap/aws/workers/outbox_dispatcher.py`, `src/modules/internal_events/bootstrap/workers/publishers/sqs/sqs_outbox_dispatcher.py` | Publica em SQS, mas Compose não inicia esse worker. |
| Event Router | PARTIAL | `src/modules/internal_events/infrastructure/messaging/routing/event_router.py`, `src/modules/internal_events/bootstrap/event_router.py` | Roteia apenas os dois eventos de e-mail para publisher SQS. |
| RabbitMQ publishers | PARTIAL | `src/modules/internal_events/infrastructure/messaging/rabbitmq/publishers/` | Existem, mas não são usados pelo dispatcher efetivo. |
| RabbitMQ e-mail consumers | PARTIAL | `src/modules/notification/infrastructure/messaging/rabbitmq/consumers/`, `src/modules/notification/bootstrap/workers/rabbitmq/` | Consomem RabbitMQ, enquanto o outbox publica SQS; payloads esperados também divergem. |
| Consumers SQS | NOT_STARTED | `src/modules/internal_events/infrastructure/messaging/aws_sqs/consumers/` | Apenas `__init__.py`. |
| Processed Events | NOT_STARTED | models/migrations/repositories | Nenhuma tabela ou repository. |
| Idempotência por consumer | NOT_STARTED | workers/repositories | Nenhum registro/deduplicação. |
| Visibilidade operacional de falhas | NOT_STARTED | rotas/observabilidade | Falhas só ficam consultáveis diretamente no banco. |
| JournalAnalysisWorker | NOT_STARTED | `src/` inspecionado | Ausente. |
| EmbeddingWorker | NOT_STARTED | `src/` inspecionado | Ausente. |
| WorkIngestionWorker | NOT_STARTED | `src/` inspecionado | Ausente. |
| ReferenceMatchingWorker | NOT_STARTED | `src/` inspecionado | Ausente. |
| RecommendationWorker | NOT_STARTED | `src/` inspecionado | Ausente. |

Eventos concretos encontrados:

- `emails.verification.requested` — `src/modules/auth/domain/events/emails/verification_requested.py`;
- `emails.password_reset.requested` — `src/modules/auth/domain/events/emails/password_reset_requested.py`.

Não há eventos Journal. Os códigos brutos de verificação/reset são colocados no payload do Outbox; o
consumer RabbitMQ registra o corpo integral da mensagem, criando risco de exposição de dados sensíveis.

`docker-compose.api_workers.yml` foi alinhado aos entrypoints movidos para
`src/modules/notification/bootstrap/workers/rabbitmq/`; o Compose ainda não inicia o dispatcher SQS do Outbox.

## 11. Notification e integrações externas

| Capacidade | Status | Evidência | Estado real |
|---|---|---|---|
| Email ports | IMPLEMENTED | `src/modules/notification/application/ports/` | Contratos de verificação/reset existem. |
| SMTP adapters/templates | PARTIAL | `src/modules/notification/infrastructure/email/smtp/` | HTML e envio assíncrono existem; remetente Gmail está hardcoded e entrega não foi verificada. |
| NotificationWorker | PARTIAL | `src/modules/notification/bootstrap/workers/`, consumers RabbitMQ | O módulo físico existe, mas o caminho de publicação não chega a esses consumers. |
| TemplateRenderer independente | NOT_STARTED | `src/modules/notification/infrastructure/email/smtp/` | Templates estão embutidos nos adapters. |
| NotificationLog | NOT_STARTED | models/migrations/repositories | Ausente. |
| SES | NOT_STARTED | projeto inteiro | Ausente. |
| S3 | NOT_STARTED | projeto inteiro | Ausente. |
| Neo4j | NOT_STARTED | projeto inteiro | Ausente. |
| Provedor de IA | NOT_STARTED | projeto inteiro | Ausente. |
| RabbitMQ externo | NOT_VERIFIED | Compose/config | Serviço não executado neste host. |
| SQS externo | NOT_VERIFIED | config/adapter | Nenhuma credencial/queue real foi usada. |
| SMTP externo | NOT_VERIFIED | config/adapter | Nenhum e-mail real foi enviado. |

## 12. Frontend

| Tela/fluxo | Status | Evidência |
|---|---|---|
| Cadastro e login | NOT_STARTED | nenhum projeto frontend no repositório |
| Perfil/privacidade | NOT_STARTED | nenhum projeto frontend no repositório |
| Journal e histórico | NOT_STARTED | nenhum projeto frontend no repositório |
| Análise e recomendações | NOT_STARTED | nenhum projeto frontend no repositório |
| Compartilhamento/atividades | NOT_STARTED | nenhum projeto frontend no repositório |
| Administração | NOT_STARTED | nenhum projeto frontend no repositório |
| Integração frontend–backend | NOT_STARTED | nenhum cliente/SDK/configuração frontend |

Os mockups do TCC são documentação de produto, não frontend implementado.

## 13. Testes e verificabilidade

| Suite/verificação | Status | Evidência | Resultado |
|---|---|---|---|
| Sintaxe Python | IMPLEMENTED | 346 arquivos sob `src/`, `tests/` e `alembic/` | Parsing estático sem falhas após a limpeza modular. |
| Unitários Application/Auth | PARTIAL | `tests/unit/application/use_cases/login/`, `tests/unit/application/use_cases/logoff/` | Sete testes escritos: cinco login e dois logoff; estão desatualizados. |
| Coleta pytest | IMPLEMENTED | `tests/`, `src/modules/auth/application/use_cases/login/__init__.py` | Sete testes coletados com sucesso. |
| Testes Domain | NOT_STARTED | `tests/` inspecionado | Ausentes. |
| Integração repository/PostgreSQL | NOT_STARTED | `tests/` inspecionado | Nenhum teste de integração; o antigo diretório vazio foi removido. |
| API/HTTP | NOT_STARTED | `tests/` inspecionado | Ausentes. |
| Outbox/idempotência | NOT_STARTED | `tests/` inspecionado | Ausentes. |
| Neo4j | NOT_STARTED | `tests/` inspecionado | Ausentes. |
| LLM contract | NOT_STARTED | `tests/` inspecionado | Ausentes. |
| Frontend | NOT_STARTED | repositório | Frontend ausente. |
| E2E | NOT_STARTED | `tests/` inspecionado | Nenhum teste E2E; o antigo diretório vazio foi removido. |
| API import/OpenAPI | IMPLEMENTED | `src/main/server/fast_api/run.py` | Importação e enumeração de rotas tiveram sucesso com env temporário. |
| Docker/PostgreSQL/brokers | NOT_VERIFIED | Compose | CLI disponível; daemon, containers e conexões não foram verificados nesta análise. |

O pacote de login agora exporta `LoginUseCaseImpl` sem o ciclo Application anterior. Fixtures e doubles
continuam refletindo assinaturas antigas: ausência de UoW/Outbox, `AuthSessionResultDTO` sem `session_id`
e construtores incompatíveis com os casos de uso atuais. Por isso os sete testes falham no setup.

## 14. Divergências entre código e documentação

Estas divergências permanecem abertas; o código foi usado apenas como evidência do estado atual. Este
diagnóstico **não decide automaticamente** se código ou documentação deve ser modificado.

1. **Identidade do sistema:** documentação consolidada usa Reflecta; `pyproject.toml`, settings, título
   FastAPI, Compose e remetente SMTP ainda usam Individuum.
2. **Arquitetura modular:** Auth, Journal, Internal Events e Notification possuem raízes verticais;
   infraestrutura compartilhada permanece horizontal e somente Auth é substancial.
3. **Mensageria:** o contexto atual prevê Outbox + dispatcher interno sem novo broker; o código publica
   em SQS, consome RabbitMQ e o Compose sobe RabbitMQ. A cadeia não se conecta.
4. **PostgreSQL:** os diagramas/glossário planejam cinco schemas; o código cria seis tabelas no schema
   padrão e só cobre Auth/Outbox.
5. **Identificadores:** documentação usa UUID; código e migrations usam ULID `String(26)`.
6. **User/Auth:** campos, estados, credenciais, sessão e MFA documentados não correspondem aos models
   atuais. O código adiciona verificação de e-mail própria, mas omite role/status/updated_at persistidos.
7. **Contrato de cadastro:** casos/documentação e validator não coincidem sobre campos e tamanho de
   senha; o código exige username, surname, data de nascimento e confirmação de senha.
8. **Journal create:** planejado persiste `PENDING_ANALYSIS` e evento transacional; o caso de uso atual
   cria `DRAFT`, não persiste e não publica evento.
9. **Analysis:** planejada como entidade 1:N; o código apenas embute alguns campos de análise em
   `JournalEntry`, sem tabela ou versão vigente.
10. **Outbox:** planejado `OUTBOX_EVENTS`, `PROCESSED`, aggregate e `processed_at`; código usa `outbox`,
    `SENT`, não tem aggregate nem Processed Events.
11. **Notification:** planejado SES e log de notificação; código usa SMTP Gmail e não persiste tentativas.
12. **pgvector:** planejado para embeddings; há apenas dependência/imagem, sem extensão ou dados.
13. **Neo4j, S3 e IA:** aparecem na arquitetura planejada, mas estão ausentes do código/infra real.
14. **Frontend:** TCC contém interfaces/mockups; não há frontend no repositório.
15. **Testes:** TCC descreve cenários e uma matriz de testes; o repositório tem sete testes Auth
    desatualizados, coletados com sucesso, mas todos falham no setup.
16. **Deploy/workers:** os entrypoints dos workers de e-mail acompanham o módulo Notification, mas o
    Compose não inicia o dispatcher SQS existente; o Neo4j planejado também não aparece na infra.
17. **OpenAPI/Auth:** documentação sugere contratos HTTP usuais; cinco rotas Auth não expõem
    body/parâmetros/security na spec, e login usa Basic Auth sem registrá-lo.

### Divergências internas da própria documentação

- o escopo atual é journaling textual, mas o TCC ainda mostra áudio/imagem e S3 para mídia;
- `ConsentService/Repository` existe no componente Sharing sem entidade/tabela Consent;
- casos administrativos exigem permissão, mas o modelo Auth não define RBAC;
- UC18 exige histórico contextual sem entidade persistente correspondente;
- identidade, e-mail, envio e auditoria de acesso do profissional não cabem em `SharedExport`;
- atividade profissional não tem campo para a anotação pessoal mostrada no TCC;
- `CatalogStatus` não comporta `PROCESSING/FAILED` usados em outros artefatos;
- `PROCESSED_EVENTS` tem PK somente `event_id`, incompatível com idempotência por vários consumers;
- cardinalidade de embeddings é opcional no diagrama de classes e obrigatória no DER;
- NotificationLog é opcional no componente, mas obrigatório no glossário/TCC;
- macroarquitetura omite conexões de AI/Catalog/Notification ao PostgreSQL e AI como produtor de evento;
- `password_salt`, DRAFT, confirmação/rejeição de tema e cardinalidades do grafo são inconsistentes entre
  classes, DER, glossário, casos de uso ou mockups.

## 15. Decisões pendentes e bloqueadores

1. Escolher o baseline canônico de Auth antes de ampliar as migrations: schemas e UUID versus ULID,
   campos User/Credentials/Session, verificação de e-mail, RBAC/admin e prioridade de MFA.
2. Definir o barramento interno real: sem broker, RabbitMQ ou SQS; depois alinhar dispatcher, consumers,
   Compose, payloads, retry, lease e idempotência.
3. Confirmar sem ambiguidade o ciclo Journal: uso de DRAFT, transição para análise, edição/reanálise,
   exclusão e análise vigente/versionada.
4. Definir privacidade/segurança do LLM: provider, retenção, redaction, modelo, schema de saída e falhas.
5. Definir embeddings: modelo, dimensão, versão, extensão/índice pgvector e cardinalidade assíncrona.
6. Definir contratos intermodulares para impedir acesso direto ao schema e evitar ciclo
   Catalog–Recommendation.
7. Definir consistência e reconciliação entre PostgreSQL, Neo4j e S3, inclusive referências órfãs.
8. Definir Consent e o modelo de identidade/entrega/auditoria do profissional.
9. Definir chave e semântica de Processed Events por consumer.
10. Confirmar journaling somente textual e tratar os artefatos multimídia como divergência em revisão
    documental futura, não nesta alteração.

## 16. Riscos técnicos

- **Corrupção/interferência concorrente:** UoWs globais guardam sessão/repositories mutáveis por request.
- **Fluxos Auth quebrados:** mapper, relógio, expiração e dependência de reset falham em caminhos normais.
- **Falsa proteção:** middleware Auth não está conectado; não existe autorização efetiva.
- **Refresh usado como access token:** tokens não distinguem propósito criptograficamente.
- **Perda de eventos:** crash após marcar `PROCESSING` deixa evento sem mecanismo de reclaim.
- **Entrega impossível:** outbox SQS e consumers RabbitMQ usam transportes/payloads diferentes.
- **Exposição de segredos/PII:** código bruto de verificação/reset no Outbox e log integral do consumer;
  erros detalhados em debug; `HttpRequest.__repr__` inclui headers/body.
- **Configuração não reproduzível:** sem `.env.example`, URL de banco malformada e dispatcher ausente do Compose.
- **Ausência de rede de segurança:** zero teste executado, sem integração/API/E2E/CI.
- **Migrações precoces divergentes:** expandir sobre tabelas/schema/ids atuais pode encarecer a correção do
  baseline definido no contexto.
- **Escopo sensível sem controles:** journaling/LLM/export lidam com dados pessoais e de saúde sem política
  técnica implementada de criptografia, retenção, acesso e auditoria.

## 17. Dívidas técnicas observadas

- README contém apenas o título `Individuum_MVP`;
- arquivo `.env.dev` referenciado, sem exemplo versionado;
- migration vazia `4c9d09eb81e5_criando_tabela_do_pattern_outbox.py`;
- downgrade incompleto do enum Outbox;
- imports por `__init__` e wildcard gerando ciclos;
- tabela `passwords_reset` mantém nomenclatura divergente;
- settings Pydantic com configuração depreciada e defaults inseguros;
- CORS `*` combinado com credentials;
- objetos de composição criados no import da rota;
- contratos OpenAPI incompletos e status documentado diferente do retorno;
- remetente SMTP hardcoded;
- Docker Compose ainda não inicia o dispatcher do Outbox e depende de `.env.dev` ausente;
- não há health checks da aplicação, CI, métricas ou tracing.

## 18. Menor próximo incremento vertical coerente

**Não iniciado por esta auditoria.**

O menor incremento recomendado é fechar **UC08 — cadastro com emissão transacional da solicitação de
verificação**, atravessando HTTP → Application → Domain → PostgreSQL → Outbox, com um teste de API e um
teste de integração contra PostgreSQL. O limite deve ser explícito: criar usuário/credencial/verificação,
persistir o evento na mesma transação, responder `201` e rejeitar duplicidade/entrada inválida; a entrega
externa do e-mail pode ser o incremento seguinte, desde que o evento persistido tenha contrato canônico.

Antes de implementá-lo, a revisão deste diagnóstico precisa decidir apenas o necessário para esse corte:

1. manter ou migrar agora ULID/schema padrão para UUID/`auth_schema`;
2. confirmar os campos e a regra de senha do cadastro;
3. confirmar que a verificação de e-mail pertence ao baseline;
4. definir o envelope mínimo do evento, sem escolher silenciosamente entre SQS e RabbitMQ.

Esse corte é menor e mais seguro do que iniciar Journal/IA sobre uma base Auth, transacional e de testes
que hoje não executa. Ele também força a corrigir o lifetime do UoW e torna uma capacidade real
reproduzível antes de aumentar o escopo.

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
- inventário de 372 arquivos do projeto, excluindo `.git`;
- leitura do código, configurações, dependências, migrations, testes, Docker/Compose, documentação,
  seis diagramas `.puml`, sete diagramas `.mmd`, glossário e as 116 páginas do TCC;
- parsing/compilação estática dos 334 arquivos Python: **sem erro de sintaxe**;
- inspeção do grafo de imports: **dois ciclos concretos** encontrados;
- inspeção Alembic: histórico linear e uma única head `ca9163c93ce6`;
- importação da aplicação FastAPI e geração do OpenAPI com variáveis de processo de auditoria: **sucesso**;
- execução de `pytest -p no:cacheprovider -q`: **falha na coleta**, com dois `ImportError`; zero testes executados;
- Docker/Compose não executado: o comando `docker` não está instalado/disponível neste host;
- nenhum serviço externo e nenhum banco real foram acionados.

## 2. Resumo executivo

| Área | Status | Estado real |
|---|---|---|
| Backend/API | PARTIAL | FastAPI sobe e expõe sete rotas Auth; os demais módulos não possuem API funcional. |
| Monólito modular | PARTIAL | Um único backend existe, mas a estrutura física é por camada global, não por bounded module. |
| Clean Architecture / DDD | PARTIAL | Há entidades, portas, casos de uso e adapters, com violações e ciclos de dependência. |
| Auth Module | PARTIAL | É o único módulo substancial; contém falhas que quebram fluxos principais e não tem teste executável. |
| Journal Module | PARTIAL | Entidade e caso de uso embrionário; não há persistência, endpoint nem processamento. |
| AI Processing | NOT_STARTED | Nenhum port, provider, schema, worker ou persistência de IA. |
| Recommendation | NOT_STARTED | Apenas arquivo vazio com nome incorreto; não constitui implementação. |
| Catalog / Knowledge | NOT_STARTED | Nenhuma entidade, adapter Neo4j, caso de uso ou API. |
| Sharing / Professional | NOT_STARTED | Nenhuma implementação. |
| Notification | PARTIAL | SMTP, templates e consumidores de e-mail existem, mas a cadeia está desconectada e não usa SES. |
| Internal Events / Outbox | PARTIAL | Outbox e retry existem; publicação e consumo usam brokers incompatíveis e não há idempotência. |
| PostgreSQL | PARTIAL | Seis tabelas Auth/Outbox no schema padrão; execução real não verificada. |
| pgvector | PARTIAL | Dependência e imagem Docker presentes, sem extensão, coluna, migration ou consulta vetorial. |
| Neo4j | NOT_STARTED | Ausente das dependências, Compose e código. |
| Frontend | NOT_STARTED | Não existe aplicação frontend no repositório. |
| Testes automatizados | PARTIAL | Há sete testes unitários Auth desatualizados; a suíte falha na coleta. |

## 3. Stack real encontrada

| Item | Status | Evidência | Observação |
|---|---|---|---|
| Python 3.12+ | IMPLEMENTED | `pyproject.toml`, `Dockerfile` | Linguagem efetiva do backend. |
| FastAPI / Uvicorn | IMPLEMENTED | `pyproject.toml`, `src/main/server/fast_api/server.py`, `src/main/server/fast_api/run.py` | Aplicação importada com sucesso durante a auditoria. |
| Pydantic / pydantic-settings | IMPLEMENTED | `pyproject.toml`, `src/core/settings.py`, `src/main/validators/fast_api/auth/` | Há warnings de configuração Pydantic legada. |
| SQLAlchemy assíncrono / asyncpg | IMPLEMENTED | `pyproject.toml`, `src/infra/postgresql/connection.py`, `src/infra/postgresql/models/` | Stack de persistência efetiva. |
| Alembic | IMPLEMENTED | `alembic.ini`, `alembic/env.py`, `alembic/versions/` | Cadeia estática válida, uma head. Aplicação contra banco: `NOT_VERIFIED`. |
| PostgreSQL 16 | PARTIAL | `docker-compose.infra.yml`, `src/infra/postgresql/` | Imagem `pgvector/pgvector:pg16`; banco real não executado. |
| pgvector | PARTIAL | `pyproject.toml`, `docker-compose.infra.yml` | Somente pacote/imagem; sem uso persistente. |
| Argon2 | IMPLEMENTED | `src/infra/security/argon2id_password_hasher.py`, `src/infra/security/configs/argon2/` | Adapter concreto de hash e verificação. |
| JWT / PyJWT | PARTIAL | `src/infra/security/token_service.py`, `src/application/services/auth/auth_session/` | Tokens existem, mas access e refresh não têm tipo/audience distintos. |
| RabbitMQ / aio-pika | PARTIAL | `docker-compose.infra.yml`, `src/infra/messaging/rabbitmq/` | Publicadores/consumidores existem, mas não formam a cadeia efetiva do outbox. |
| AWS SQS / boto3 | PARTIAL | `src/infra/messaging/aws_sqs/`, `src/main/workers/publishers/sqs/sqs_outbox_dispatcher.py` | O dispatcher publica em SQS; não há consumer SQS implementado. |
| SMTP / aiosmtplib | PARTIAL | `src/infra/email/smtp/` | Implementação Gmail/SMTP; entrega externa não verificada. |
| SES | NOT_STARTED | Repositório inteiro inspecionado | Não há adapter/configuração SES. |
| S3 | NOT_STARTED | Repositório inteiro inspecionado | `boto3` é usado apenas para SQS. |
| Neo4j | NOT_STARTED | `pyproject.toml`, Compose e `src/` | Sem driver, serviço ou adapter. |
| Provider de LLM | NOT_STARTED | `pyproject.toml`, `src/` | Nenhum SDK, port ou adapter de IA. |
| Frontend | NOT_STARTED | raiz do repositório | Sem manifesto, fonte, build ou assets de aplicação web. |
| Pytest / pytest-asyncio | PARTIAL | `pyproject.toml`, `tests/` | Suite presente, mas não coletável. |
| Docker / Compose | PARTIAL | `Dockerfile`, `docker-compose.infra.yml`, `docker-compose.api_workers.yml` | Análise estática concluída; runtime `NOT_VERIFIED`. |
| CI/CD | NOT_STARTED | raiz do repositório | Nenhum workflow/pipeline encontrado. |
| Observabilidade | PARTIAL | `src/main/server/fast_api/server.py`, workers de mensageria | Logging básico; sem métricas, tracing, alertas ou health/readiness. |

Não existe `.env.example` ou equivalente. `src/core/settings.py` declara `.env.dev`, e
`docker-compose.api_workers.yml` também o referencia, mas esse arquivo não está no repositório.

## 4. Arquitetura real

### 4.1 Estrutura e fronteiras

| Capacidade | Status | Evidência | Diagnóstico |
|---|---|---|---|
| Um único backend implantável | IMPLEMENTED | `Dockerfile`, `src/main/server/fast_api/run.py` | É um monólito no sentido de um processo/API principal. |
| Modularidade por bounded context | PARTIAL | `src/application/use_cases/auth/`, `src/application/use_cases/journal/` | Auth/Journal aparecem como nomes em subpastas, mas não há módulos verticais autônomos nem interfaces públicas por módulo. |
| Separação Domain/Application/Infrastructure/Presentation | PARTIAL | `src/domain/`, `src/application/`, `src/infra/`, `src/presentation/`, `src/main/` | Separação física existe; fronteiras não são integralmente respeitadas. |
| Clean Architecture | PARTIAL | portas em `src/domain/ports/` e `src/application/ports/`; adapters em `src/infra/` | Há inversão em vários pontos, mas Domain depende de configuração e semântica HTTP. |
| DDD | PARTIAL | `src/domain/entities/`, `src/domain/value_objects/`, eventos e ports | Há entidades/VOs, mas não há bounded contexts físicos, agregados/contratos intermodulares formalizados ou isolamento de persistência. |
| Composition root / DI | PARTIAL | `src/main/composables/` | Composição é manual e cria instâncias globais reutilizadas entre requests. |
| API/BFF | PARTIAL | `src/main/routes/fast_api/auth_routes.py`, `src/main/server/fast_api/server.py` | Apenas Auth é exposto; não existe frontend nem BFF para os outros módulos. |
| Dependências acíclicas | PARTIAL | `src/application/use_cases/auth/login/__init__.py`, `src/application/use_cases/auth/login/ilogin_use_case.py`, `src/infra/postgresql/models/__init__.py` e models Auth | Dois ciclos de import detectados. |

Dependências entre camadas observadas pelo AST:

- `domain -> core, domain`;
- `application -> application, core, domain`;
- `infra -> application, core, domain, infra`;
- `presentation -> application, core, domain, presentation`;
- `main -> application, core, domain, infra, main, presentation`;
- `core -> domain`.

Isso cria acoplamento bidirecional `domain <-> core`. Não foram encontrados imports concretos entre
módulos de negócio maduros porque, além de Auth, eles ainda não existem.

### 4.2 Violações arquiteturais comprovadas

1. **Domain depende de configuração:** `src/domain/value_objects/password_plain.py` importa
   `src/core/settings.py`; regras do domínio ficam acopladas ao ambiente.
2. **Domain contém transporte HTTP:** `src/domain/exceptions/domain_error.py` e
   `src/domain/exceptions/api_types/` carregam status/tipos de API dentro do domínio.
3. **Ciclo Application:** `src/application/use_cases/auth/login/__init__.py` e
   `src/application/use_cases/auth/login/ilogin_use_case.py` importam-se mutuamente.
4. **Ciclo Infrastructure:** `src/infra/postgresql/models/__init__.py` reexporta models que, por
   sua vez, importam do pacote `models`, formando ciclo entre o `__init__` e os models Auth.
5. **Unit of Work global e mutável:** `src/main/composables/use_cases/auth/units_of_work.py`,
   `src/main/composables/use_cases/auth/use_cases.py` e `src/main/routes/fast_api/auth_routes.py`
   instanciam e reutilizam UoWs/use cases/controllers. `src/infra/postgresql/units_of_work/base_unit_of_work.py`
   mantém sessão mutável; requests concorrentes podem compartilhar estado.
6. **Middleware de autenticação desconectado:** `src/main/adapters/fast_api/fast_api_auth.py` não é
   instalado na aplicação. `src/application/services/auth/http_request_auth/authenticate_request_service_impl.py`
   e `iauthenticate_request_service.py` ainda possuem imports locais absolutos inválidos.
7. **Exceção expõe internals em debug:** `src/main/server/fast_api/fast_api_exception_handler.py`
   pode devolver arquivo, linha e erro bruto; `DEBUG` tem default ativo em `src/core/settings.py`.

## 5. Auth Module

| Capacidade | Status | Evidência | Estado real |
|---|---|---|---|
| User/AuthCredentials model | PARTIAL | `src/domain/entities/user.py`, `src/infra/postgresql/models/users_model.py`, `auth_credentials_model.py`, migration `1ce1f1cd457b_bancos_agora_em_docker.py` | Existe, mas diverge do modelo planejado e possui mapeamento quebrado. |
| Cadastro | PARTIAL | `src/application/use_cases/auth/signup/`, `src/presentation/controllers/auth/sign_up_controller.py`, `src/main/routes/fast_api/auth_routes.py` | Fluxo substancial; não há teste executável nem E2E e a cadeia de verificação por e-mail não fecha. |
| Login | PARTIAL | `src/application/use_cases/auth/login/`, `src/presentation/controllers/auth/login_controller.py` | Quebra ao buscar usuário por uso incorreto do mapper. |
| Password hashing | IMPLEMENTED | `src/domain/ports/security/ipassword_hasher.py`, `src/infra/security/argon2id_password_hasher.py` | Argon2id concreto com verify/rehash. |
| Geração/validação JWT | PARTIAL | `src/application/ports/auth/token/`, `src/infra/security/token_service.py` | Primitiva existe; access/refresh são indistinguíveis por claim/tipo. |
| Sessões e refresh | PARTIAL | `src/domain/entities/auth_session.py`, `src/application/services/auth/auth_session/`, `src/infra/postgresql/repositories/auth_sessions_repository.py` | Persistência existe; refresh usa atributo inexistente `_clock`. |
| Logoff | PARTIAL | `src/application/use_cases/auth/logoff/`, `src/presentation/controllers/auth/logoff_controller.py` | Estrutura existe; cobertura prevista não pode ser coletada. |
| Solicitar reset de senha | PARTIAL | `src/application/use_cases/auth/request_password_reset/`, `src/application/services/auth/reset_password_service/` | Implementação passa repository onde o service espera UoW e falha em runtime. |
| Efetivar reset de senha | PARTIAL | `src/application/use_cases/auth/reset_password/`, `src/infra/postgresql/repositories/reset_password_repository.py`, migration `0633c30be51a_colocando_tabela_de_reset_de_password_.py` | Estrutura/persistência existem; depende de consultas de usuário quebradas. |
| Verificação de e-mail | PARTIAL | `src/domain/entities/email_verification.py`, `src/application/use_cases/auth/verify_email/`, `src/infra/postgresql/repositories/user_email_verification_repository.py` | Repositório e service contêm erros funcionais; envio é desconectado. |
| Perfil | NOT_STARTED | `src/` e rotas inspecionados | Nenhum caso de uso/endpoint. |
| Avatar/S3 | NOT_STARTED | `src/` inspecionado | Nenhuma implementação S3. |
| Exclusão/anonimização | NOT_STARTED | `src/` inspecionado | Nenhum caso de uso/endpoint. |
| Exportação geral da conta | NOT_STARTED | `src/` inspecionado | Nenhum job/caso de uso/endpoint. |
| Admin authorization | BLOCKED | `src/domain/entities/user.py`, `src/application/services/auth/http_request_auth/dto.py` | DTO tem `is_admin/roles`, mas não existe modelo persistido, claim ou decisão RBAC. |
| MFA | NOT_STARTED | `src/` inspecionado | Nenhuma implementação. |

Falhas concretas que impedem considerar os casos Auth como `IMPLEMENTED`:

- `src/infra/postgresql/repositories/user_repository.py` chama
  `UserMapper.to_entity(model=...)`, mas `src/infra/postgresql/mappers/user_mapper.py` não aceita esse keyword;
- o mesmo repository tenta desempacotar dois valores retornados por `UserMapper.to_model()`, que retorna um;
- `src/application/services/auth/auth_session/auth_session_service_impl.py` usa `self._clock`, mas o
  atributo criado é `self.__system_clock`;
- `src/application/services/auth/email_verification/email_verification_service_impl.py` testa
  `verification.is_expired` sem chamar o método;
- `src/infra/postgresql/repositories/user_email_verification_repository.py` compara o id com
  `str(UserId)` em vez do valor persistido;
- o login de usuário ainda não verificado emite evento e depois lança exceção antes do commit,
  levando o UoW a rollback;
- `src/application/services/auth/reset_password_service/password_reset_service_impl.py` trata um
  repository recebido como se fosse um UoW;
- `src/domain/value_objects/password_plain.py` referencia `PASSWORD_MIN_LENGTH`, nome inexistente
  em settings, no caminho de erro de senha curta;
- o validator HTTP aceita senha de 8 caracteres, enquanto o domínio exige 12;
- não há autenticação/autorização instalada nas rotas.

## 6. Journal Module

| Capacidade | Status | Evidência | Estado real |
|---|---|---|---|
| Entidade JournalEntry | PARTIAL | `src/domain/entities/journal_entry.py`, `src/domain/value_objects/journal_entry_status.py`, `content_tags.py` | Entidade rica existe, sem model/repository concreto/migration. |
| Criar entrada | PARTIAL | `src/application/use_cases/journal/create_entry/` | Cria entidade `DRAFT`, mas nunca chama repository; apenas faz commit. |
| Port de repository/UoW | PARTIAL | `src/domain/ports/repositories/ijournal_entry_repository.py`, `src/domain/ports/units_of_work/ijournal_unit_of_work.py` | Interfaces sem implementação. |
| Endpoint Journal | NOT_STARTED | `src/main/routes/fast_api/journal_routes.py`, `src/main/server/fast_api/server.py` | Router vazio e não incluído no servidor. |
| Persistência Journal | NOT_STARTED | `src/infra/postgresql/models/`, `alembic/versions/` | Nenhum model, repository, UoW concreto ou tabela. |
| Listar histórico | NOT_STARTED | `src/` inspecionado | Ausente. |
| Detalhar entrada | NOT_STARTED | `src/` inspecionado | Ausente. |
| Editar/reanalisar | NOT_STARTED | `src/` inspecionado | Ausente. |
| Excluir entrada | NOT_STARTED | `src/` inspecionado | Ausente. |
| Ownership/authorization | NOT_STARTED | caso de uso `create_entry`, rotas | DTO recebe `user_id` do cliente; não há identidade autenticada. |
| Analysis persistida | NOT_STARTED | `src/` e migrations inspecionados | Campos parciais estão embutidos na entidade; não existe entidade/tabela Analysis. |
| JournalSentence / SentenceTheme / SentencePassage | NOT_STARTED | `src/` inspecionado | Ausentes. |
| EntryEmbedding / SentenceEmbedding | NOT_STARTED | `src/domain/entities/entry_embedding.py` | Arquivo `entry_embedding.py` tem zero bytes; não é implementação. |
| DRAFT | PARTIAL | `src/domain/value_objects/journal_entry_status.py`, caso de uso create | Existe no código, mas o contrato do fluxo e a passagem a `PENDING_ANALYSIS` não existem. |
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
| Entidade Recommendation | NOT_STARTED | `src/domain/entities/recomendation.py` tem zero bytes e nome incorreto |
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
| `POST /auth/signup` | PARTIAL | `src/main/routes/fast_api/auth_routes.py`, `src/presentation/controllers/auth/sign_up_controller.py` | Única rota com request body documentado no OpenAPI; resposta real 201, spec gerada anuncia 200/422. |
| `POST /auth/login` | PARTIAL | mesmos paths, `login_controller.py` | Usa Basic Auth fora do contrato OpenAPI e falha na consulta via mapper. |
| `POST /auth/logoff` | PARTIAL | `logoff_controller.py` | Sem security scheme no OpenAPI. |
| `POST /auth/refresh` | PARTIAL | `refresh_controller.py` | Depende de cookie; service contém erro `_clock`. |
| `POST /auth/request-reset-password` | PARTIAL | `request_reset_password_controller.py` | Não declara body no OpenAPI e o service recebe dependência incompatível. |
| `POST /auth/reset-password` | PARTIAL | `reset_password_controller.py` | Não declara body no OpenAPI. |
| `GET /auth/verify-email` | PARTIAL | `verify_email_controller.py` | Declara `code` em query; repository/service possuem erros. |
| Demais endpoints planejados | NOT_STARTED | `src/main/server/fast_api/server.py`, `src/main/routes/fast_api/` | Journal não é montado; não há Profile, AI, Recommendation, Sharing, Catalog/Admin ou Notification API. |

DTOs e validators existem principalmente em `src/application/use_cases/auth/*/dto.py` e
`src/main/validators/fast_api/auth/`, mas login/reset não estão integrados ao schema FastAPI de modo a
gerar contrato OpenAPI. Todas as rotas têm `security: []` na spec gerada.

## 9. Persistência e migrations

### 9.1 Estado real do PostgreSQL

| Item | Status | Evidência | Estado real |
|---|---|---|---|
| Metadata SQLAlchemy | IMPLEMENTED | `src/infra/postgresql/configs/base.py`, `src/infra/postgresql/models/` | Seis tabelas são registradas. |
| Tabela `users` | PARTIAL | `users_model.py`, migration `1ce1f1cd457b_bancos_agora_em_docker.py` | Auth parcial; campos divergentes do planejado. |
| Tabela `auth_credentials` | PARTIAL | `auth_credentials_model.py`, mesma migration | Sem MFA/credential_type documentados. |
| Tabela `auth_sessions` | PARTIAL | `auth_sessions_model.py`, mesma migration | Sem IP/user-agent; refresh token hash existe. |
| Tabela `user_email_verifications` | PARTIAL | `user_email_verification_model.py`, mesma migration | Implementação adicional ao modelo consolidado, mas fluxo está quebrado. |
| Tabela `passwords_reset` | PARTIAL | `reset_password_model.py`, migration `0633c30be51a_colocando_tabela_de_reset_de_password_.py` | Nome e modelo divergem da documentação. |
| Tabela `outbox` | PARTIAL | `outbox_model.py`, migrations `631fd4384bca_criando_tabela_do_pattern_outbox_nao_.py` e `ca9163c93ce6_01_09_2026_atualizando_a_tabela_de_.py` | Suporta estados/retry, sem contrato documentado completo. |
| Cadeia Alembic | IMPLEMENTED | `alembic/versions/` | Uma head; `4c9d09eb81e5_criando_tabela_do_pattern_outbox.py` é migration vazia. |
| Execução em PostgreSQL real | NOT_VERIFIED | `docker-compose.infra.yml` | Docker indisponível no host; nenhuma conexão externa foi feita. |
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
| Entidade/model/tabela Outbox | PARTIAL | `src/domain/entities/outbox_event.py`, `src/infra/postgresql/models/outbox_model.py`, migrations Outbox | Estrutura real existe e diverge do contrato documentado. |
| Escrita transacional Auth + Outbox | PARTIAL | `src/application/services/messaging/outbox_service_impl.py`, `src/infra/postgresql/units_of_work/auth_unit_of_work_impl.py`, casos signup/reset | Usa o mesmo UoW, mas os fluxos possuem erros e não foram integrados. |
| Claim concorrente | IMPLEMENTED | `src/infra/postgresql/repositories/outbox_repository.py` | Usa `FOR UPDATE SKIP LOCKED`, marca `PROCESSING` e incrementa tentativas. |
| Retry/backoff | PARTIAL | `src/infra/strategies/exponential_retry.py`, `src/infra/messaging/workers/publishers/base_sqs_publisher_worker.py` | Backoff existe; evento abandonado em `PROCESSING` não é recuperado após crash. |
| Dispatcher | PARTIAL | `src/main/composables/messaging/aws/workers/outbox_dispatcher.py`, `src/main/workers/publishers/sqs/sqs_outbox_dispatcher.py` | Publica em SQS, mas Compose não inicia esse worker. |
| Event Router | PARTIAL | `src/infra/messaging/routing/event_router.py`, `src/main/composables/messaging/event_router.py` | Roteia apenas os dois eventos de e-mail para publisher SQS. |
| RabbitMQ publishers | PARTIAL | `src/infra/messaging/rabbitmq/publishers/` | Existem, mas não são usados pelo dispatcher efetivo. |
| RabbitMQ e-mail consumers | PARTIAL | `src/infra/messaging/rabbitmq/consumers/`, `src/main/workers/consumers/emails/rabbitmq/` | Consomem RabbitMQ, enquanto o outbox publica SQS; payloads esperados também divergem. |
| Consumers SQS | NOT_STARTED | `src/infra/messaging/aws_sqs/consumers/` | Apenas `__init__.py`. |
| Processed Events | NOT_STARTED | models/migrations/repositories | Nenhuma tabela ou repository. |
| Idempotência por consumer | NOT_STARTED | workers/repositories | Nenhum registro/deduplicação. |
| Visibilidade operacional de falhas | NOT_STARTED | rotas/observabilidade | Falhas só ficam consultáveis diretamente no banco. |
| JournalAnalysisWorker | NOT_STARTED | `src/` inspecionado | Ausente. |
| EmbeddingWorker | NOT_STARTED | `src/` inspecionado | Ausente. |
| WorkIngestionWorker | NOT_STARTED | `src/` inspecionado | Ausente. |
| ReferenceMatchingWorker | NOT_STARTED | `src/` inspecionado | Ausente. |
| RecommendationWorker | NOT_STARTED | `src/` inspecionado | Ausente. |

Eventos concretos encontrados:

- `emails.verification.requested` — `src/domain/events/emails/verification_requested.py`;
- `emails.password_reset.requested` — `src/domain/events/emails/password_reset_requested.py`.

Não há eventos Journal. Os códigos brutos de verificação/reset são colocados no payload do Outbox; o
consumer RabbitMQ registra o corpo integral da mensagem, criando risco de exposição de dados sensíveis.

`docker-compose.api_workers.yml` aponta para módulos inexistentes
`src.main.workers.auth.email_verification` e `src.main.workers.auth.email_password_reset`; os entrypoints
reais estão sob `src/main/workers/consumers/emails/rabbitmq/`.

## 11. Notification e integrações externas

| Capacidade | Status | Evidência | Estado real |
|---|---|---|---|
| Email ports | IMPLEMENTED | `src/application/ports/emails/` | Contratos de verificação/reset existem. |
| SMTP adapters/templates | PARTIAL | `src/infra/email/smtp/` | HTML e envio assíncrono existem; remetente Gmail está hardcoded e entrega não foi verificada. |
| NotificationWorker | PARTIAL | consumers RabbitMQ de e-mail | Não é módulo isolado; caminho de publicação não chega a esses consumers. |
| TemplateRenderer independente | NOT_STARTED | `src/infra/email/smtp/` | Templates estão embutidos nos adapters. |
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
| Sintaxe Python | IMPLEMENTED | 334 arquivos sob `src/` e `tests/` | Parsing/compilação estática sem falhas. |
| Unitários Application/Auth | PARTIAL | `tests/unit/application/use_cases/login/`, `tests/unit/application/use_cases/logoff/` | Sete testes escritos: cinco login e dois logoff; estão desatualizados. |
| Coleta pytest | PARTIAL | `tests/`, packages Auth | Dois `ImportError` na coleta; zero testes executados. |
| Testes Domain | NOT_STARTED | `tests/` inspecionado | Ausentes. |
| Integração repository/PostgreSQL | NOT_STARTED | `tests/integration/__init__.py` | Diretório vazio de testes. |
| API/HTTP | NOT_STARTED | `tests/` inspecionado | Ausentes. |
| Outbox/idempotência | NOT_STARTED | `tests/` inspecionado | Ausentes. |
| Neo4j | NOT_STARTED | `tests/` inspecionado | Ausentes. |
| LLM contract | NOT_STARTED | `tests/` inspecionado | Ausentes. |
| Frontend | NOT_STARTED | repositório | Frontend ausente. |
| E2E | NOT_STARTED | `tests/e2e/__init__.py` | Diretório vazio de testes. |
| API import/OpenAPI | IMPLEMENTED | `src/main/server/fast_api/run.py` | Importação e enumeração de rotas tiveram sucesso com env temporário. |
| Docker/PostgreSQL/brokers | NOT_VERIFIED | Compose | `docker` indisponível neste host. |

Os testes não coletam porque importam `LoginUseCaseImpl` de um `__init__.py` que não o exporta. Fixtures e
doubles também refletem assinaturas antigas: ausência de UoW/Outbox, `AuthSessionResultDTO` sem
`session_id` e construtores incompatíveis com os casos de uso atuais.

## 14. Divergências entre código e documentação

Estas divergências permanecem abertas; o código foi usado apenas como evidência do estado atual. Este
diagnóstico **não decide automaticamente** se código ou documentação deve ser modificado.

1. **Identidade do sistema:** documentação consolidada usa Reflecta; `pyproject.toml`, settings, título
   FastAPI, Compose e remetente SMTP ainda usam Individuum.
2. **Arquitetura modular:** o planejado descreve módulos coesos; o código está organizado por camadas
   globais e somente Auth é substancial.
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
    desatualizados e a suite não coleta.
16. **Deploy/workers:** Compose anuncia workers de e-mail em módulos que não existem e não inicia o
    dispatcher SQS existente; o Neo4j planejado também não aparece na infra.
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
- **Configuração não reproduzível:** sem `.env.example`, URL de banco malformada e entrypoints Compose inválidos.
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
- `src/domain/entities/entry_embedding.py` e `recomendation.py` vazios;
- typo `recomendation.py` e tabela `passwords_reset`;
- settings Pydantic com configuração depreciada e defaults inseguros;
- CORS `*` combinado com credentials;
- objetos de composição criados no import da rota;
- contratos OpenAPI incompletos e status documentado diferente do retorno;
- remetente SMTP hardcoded;
- Docker Compose não corresponde aos módulos executáveis;
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

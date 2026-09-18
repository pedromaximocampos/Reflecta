# Reflecta — Estado real da implementação

> Auditoria realizada em 2026-08-29, com atualização focal em 2026-09-18 após a implementação unitariamente verificada do CRUD administrativo de `Theme` no Neo4j.
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
- inspeção do grafo de imports: **um ciclo interno em Auth** e nenhum ciclo entre os cinco módulos físicos;
- comparação AST de 215 arquivos Python rastreados afetados pela reorganização: **nenhuma mudança de
  corpo executável além de imports**;
- inspeção Alembic: histórico linear e uma única head `9c4f12a7e6d3`;
- importação da aplicação FastAPI e geração do OpenAPI com variáveis de processo de auditoria: **sucesso**;
- execução de `pytest -q`: **118 testes aprovados e sete erros de setup Auth** causados
  por fixtures antigas de Login/Logoff incompatíveis com os construtores atuais;
- testes focais de recuperação, repositories relacionados e Notification: **34 aprovados**;
- testes focais da atualização parcial de perfil e do repository de usuário: **23 aprovados**;
- a migration `9c4f12a7e6d3_add_user_recovery_requests.py` é a única head, mas sua aplicação real está
  **NOT_VERIFIED** porque o Docker/PostgreSQL local estava desligado na atualização de 2026-09-14;
- publicação RabbitMQ, consumo e execução de handler com notifier falso em topologia temporária: **sucesso**; a topologia de
  teste foi removida após a verificação;
- container Neo4j 5.26 Community iniciado pelo Compose, portas HTTP/Bolt publicadas e consulta
  `RETURN 1` executada via `cypher-shell`: **sucesso**;
- testes focais de Catalog/Neo4j: **38 aprovados**, cobrindo casos de uso, DTOs, validators, repository,
  UoW e configuração de conexão; importação da aplicação e geração do OpenAPI confirmaram as cinco
  operações de `/catalog/themes` com Bearer;
- banco real, API em container e entrega SMTP externa continuam não verificados.

## 2. Resumo executivo

| Área | Status | Estado real |
|---|---|---|
| Backend/API | PARTIAL | FastAPI expõe doze rotas Auth e cinco operações administrativas de `/catalog/themes`, protegidas por papel `ADMIN`; os demais módulos não possuem API funcional. |
| Monólito modular | PARTIAL | Bounded contexts estão em `src/modules/`, componentes técnicos em `src/shared/` e a composição final em `src/main/`; permanecem violações internas e fluxos incompletos. |
| Clean Architecture / DDD | PARTIAL | Há entidades, portas, casos de uso e adapters, com violações e ciclos de dependência. |
| Auth Module | PARTIAL | É o único módulo substancial. Exclusão e recuperação possuem casos de uso e testes unitários, mas ainda não foram verificadas de ponta a ponta com PostgreSQL e AWS reais. |
| Journal Module | PARTIAL | Entidade e caso de uso embrionário; não há persistência, endpoint nem processamento. |
| AI Processing | NOT_STARTED | Nenhum port, provider, schema, worker ou persistência de IA. |
| Recommendation | NOT_STARTED | Não existe código do módulo; o antigo placeholder vazio foi removido. |
| Catalog / Knowledge | PARTIAL | `Theme` possui CRUD administrativo vertical, slug determinístico e estável, repository/UoW Neo4j e transações explícitas; faltam integração com Neo4j real e Author/Work/Passage/relações. |
| Sharing / Professional | NOT_STARTED | Nenhuma implementação. |
| Notification | PARTIAL | Handler, DTO e adapters SMTP/SES atendem verificação, reset, exclusão e recuperação; o consumer Lambda/SQS existe, mas idempotência persistente ainda não foi implementada. |
| Internal Events / Outbox | PARTIAL | Dispatcher SNS está conectado ao Outbox e ao Compose; faltam idempotência, recuperação de eventos presos em `PROCESSING` e alinhamento dos consumers locais. |
| PostgreSQL | PARTIAL | Oito tabelas Auth/Outbox no schema padrão; a nova migration de recuperação ainda não foi executada contra um banco real nesta atualização. |
| pgvector | PARTIAL | Dependência e imagem Docker presentes, sem extensão, coluna, migration ou consulta vetorial. |
| Neo4j | PARTIAL | O serviço local `neo4j_dev` respondeu via Bolt; driver, settings, constraint Cypher, mapper, repository e UoW de `Theme` existem e têm testes unitários, mas a integração do fluxo com o banco real ainda não foi verificada. |
| Frontend | NOT_STARTED | Não existe aplicação frontend no repositório. |
| Testes automatizados | PARTIAL | 125 testes coletam: 118 passam e sete testes antigos de Login/Logoff falham no setup por fixtures desatualizadas. |

## 3. Stack real encontrada

| Item | Status | Evidência | Observação |
|---|---|---|---|
| Python >=3.12; runtime Docker 3.14 | IMPLEMENTED | `pyproject.toml`, `Dockerfile` | O projeto aceita Python 3.12 ou superior e a imagem do backend executa Python 3.14. |
| FastAPI / Uvicorn | IMPLEMENTED | `pyproject.toml`, `src/main/server/fast_api/server.py`, `src/main/server/fast_api/run.py` | Aplicação importada com sucesso durante a auditoria. |
| Pydantic / pydantic-settings | IMPLEMENTED | `pyproject.toml`, `src/shared/config/settings.py`, `src/modules/auth/presentation/validators/` | Há warnings de configuração Pydantic legada. |
| SQLAlchemy assíncrono / asyncpg | IMPLEMENTED | `pyproject.toml`, `src/shared/infrastructure/persistence/postgresql/connection.py`, models nos módulos Auth/Internal Events | Stack de persistência efetiva. |
| Alembic | IMPLEMENTED | `alembic.ini`, `alembic/env.py`, `alembic/versions/` | Cadeia estática válida, uma head. Aplicação contra banco: `NOT_VERIFIED`. |
| PostgreSQL 16 | PARTIAL | `docker-compose.infra.yml`, `src/shared/infrastructure/persistence/postgresql/` | Imagem `pgvector/pgvector:pg16`; banco real não executado. |
| pgvector | PARTIAL | `pyproject.toml`, `docker-compose.infra.yml` | Somente pacote/imagem; sem uso persistente. |
| Argon2 | IMPLEMENTED | `src/modules/auth/infrastructure/security/argon2id_password_hasher.py`, `src/modules/auth/infrastructure/security/configs/argon2/` | Adapter concreto de hash e verificação. |
| JWT / PyJWT | PARTIAL | `src/modules/auth/infrastructure/security/token_service.py`, `src/modules/auth/application/services/auth_session/` | Tokens existem, mas access e refresh não têm tipo/audience distintos. |
| RabbitMQ / aio-pika | PARTIAL | `src/modules/internal_events/infrastructure/messaging/rabbitmq/`, `src/modules/internal_events/bootstrap/workers/publishers/rabbitmq/`, consumers em `src/modules/notification/` | Publisher, topologia, roteamento e consumo local foram conectados; smoke test do broker passou, sem envio SMTP externo. |
| AWS SNS/SQS / boto3 | PARTIAL | publishers em `src/modules/internal_events/infrastructure/messaging/aws_sns/` e `aws_sqs/`; consumer em `src/modules/notification/infrastructure/messaging/aws/sqs/`; bootstraps AWS de ambos os módulos | O dispatcher do Compose publica no SNS e o Lambda processa lotes SQS com `batchItemFailures`; ainda não há idempotência persistente nem deploy reproduzível. |
| SMTP / aiosmtplib | PARTIAL | `src/modules/notification/infrastructure/email/smtp/` | Implementação Gmail/SMTP; entrega externa não verificada. |
| SES | PARTIAL | `src/modules/notification/infrastructure/email/ses/ses_notifier.py`, `src/modules/notification/bootstrap/aws/lambda_emails.py` | Adapter SESv2 e composição Lambda existem; falhas registram código, status HTTP e request ID sem payload/PII. Não há infraestrutura como código ou teste externo automatizado. |
| S3 | NOT_STARTED | Repositório inteiro inspecionado | `boto3` é usado apenas para SQS. |
| Neo4j | PARTIAL | `docker-compose.infra.yml`, `src/shared/infrastructure/persistence/neo4j/`, `src/modules/catalog/infrastructure/persistence/neo4j/` | Neo4j 5.26 Community local respondeu via Bolt; pacote Python, settings, constraint Cypher, mapper, repository e UoW de `Theme` existem. A integração real do fluxo permanece não verificada. |
| Provider de LLM | NOT_STARTED | `pyproject.toml`, `src/` | Nenhum SDK, port ou adapter de IA. |
| Frontend | NOT_STARTED | raiz do repositório | Sem manifesto, fonte, build ou assets de aplicação web. |
| Pytest / pytest-asyncio | PARTIAL | `pyproject.toml`, `tests/` | 125 testes coletam; 118 passam e sete fixtures antigas de Login/Logoff causam erro no setup. |
| Docker / Compose | PARTIAL | `Dockerfile`, `docker-compose.infra.yml`, `docker-compose.api_workers.yml` | Daemon, PostgreSQL, RabbitMQ e Neo4j locais foram iniciados/verificados em momentos distintos; API e workers completos ainda não foram executados juntos. |
| CI/CD | NOT_STARTED | raiz do repositório | Nenhum workflow/pipeline encontrado. |
| Observabilidade | PARTIAL | `src/main/server/fast_api/server.py`, workers de mensageria, `src/modules/notification/infrastructure/email/ses/ses_notifier.py` | Logging básico e diagnóstico seguro de falhas SES; sem correlação completa, métricas, tracing, alertas ou health/readiness. |

Não existe `.env.example` ou equivalente. Há um `.env.dev` local ignorado pelo Git, referenciado por
`src/shared/config/settings.py` e `docker-compose.api_workers.yml`; portanto, um novo colaborador ainda não possui um contrato versionado de configuração.

## 4. Arquitetura real

### 4.1 Estrutura e fronteiras

| Capacidade | Status | Evidência | Diagnóstico |
|---|---|---|---|
| Um único backend implantável | IMPLEMENTED | `Dockerfile`, `src/main/server/fast_api/run.py` | É um monólito no sentido de um processo/API principal. |
| Modularidade por bounded context | PARTIAL | `src/modules/`, `src/shared/`, `src/main/` | Cinco módulos possuem fronteira física; Catalog possui uma fatia vertical completa do CRUD de temas. Shared Kernel técnico e composition root têm dependências direcionadas. |
| Separação Domain/Application/Infrastructure/Presentation | PARTIAL | `src/modules/auth/`, `src/modules/journal/`, `src/modules/catalog/`, `src/modules/internal_events/`, `src/modules/notification/` | Auth possui as quatro camadas; Catalog usa as quatro camadas no CRUD de temas e Journal só possui Domain/Application. |
| Clean Architecture | PARTIAL | ports/use cases em `src/modules/*/application/` e `domain/`; adapters em `infrastructure/` | Há inversão em vários pontos, mas Domain ainda depende de configuração e semântica HTTP compartilhada. |
| DDD | PARTIAL | entidades/VOs/eventos em `src/modules/auth/domain/` e `src/modules/internal_events/domain/` | Bounded modules físicos foram iniciados, mas agregados, contratos e isolamento de persistência ainda são incompletos. |
| Composition root / DI | PARTIAL | `src/modules/auth/bootstrap/`, `src/modules/internal_events/bootstrap/`, `src/modules/notification/bootstrap/` | Composição é manual e ainda cria instâncias globais reutilizadas entre requests. |
| API/BFF | PARTIAL | `src/modules/auth/presentation/routes.py`, `src/modules/catalog/presentation/routes.py`, `src/main/server/fast_api/server.py` | Auth e o CRUD administrativo de temas são expostos; não existe frontend nem API funcional para os outros módulos. |
| Dependências acíclicas | PARTIAL | `src/modules/auth/infrastructure/persistence/postgresql/models/`, `src/modules/catalog/` | Não há ciclo entre os cinco módulos físicos; Catalog depende somente da fronteira pública de Auth na autorização HTTP e persiste um ciclo interno nos models de Auth. |

Dependências entre módulos observadas pelo AST após a separação física:

- `notification -> auth.public, internal_events`;
- `journal -> auth.public` apenas para o tipo público `UserId`;
- `catalog -> auth.public` apenas na camada HTTP para principal/role;
- `auth -> internal_events.public` e, na composição transacional existente, implementação de Outbox;
- `internal_events` não importa Auth nem Notification.

Não há ciclo entre módulos. `src/shared/` não
importa módulos nem `main`, e os módulos não importam `main`. Ainda existe acoplamento do Domain de Auth
com configuração compartilhada.

### 4.2 Violações arquiteturais comprovadas

1. **Domain depende de configuração:** `src/modules/auth/domain/value_objects/password_plain.py` importa
   `src/shared/config/settings.py`; regras do domínio ficam acopladas ao ambiente.
2. **Domain contém transporte HTTP:** `src/shared/domain/errors/domain_error.py` e
   `src/shared/domain/errors/api_types/` carregam status/tipos de API dentro do domínio compartilhado.
3. **Ciclo Infrastructure:** `src/modules/auth/infrastructure/persistence/postgresql/models/__init__.py`
   reexporta models que importam o próprio pacote, formando ciclo interno entre o `__init__` e os models Auth.
4. **Unit of Work global e mutável:** `src/modules/auth/bootstrap/units_of_work.py`,
   `src/modules/auth/bootstrap/use_cases.py` e `src/modules/auth/presentation/routes.py`
   instanciam e reutilizam UoWs/use cases/controllers. `src/shared/infrastructure/persistence/postgresql/units_of_work/base_unit_of_work.py`
   mantém sessão mutável; requests concorrentes podem compartilhar estado.
5. **Middleware de autenticação desconectado:** `src/modules/auth/presentation/adapters/fast_api_auth.py` não é
   instalado na aplicação. Os imports locais inválidos desse serviço foram corrigidos apenas para refletir
   a nova estrutura; o middleware continua sem uso nas rotas.
6. **Exceção expõe internals em debug:** `src/main/server/fast_api/fast_api_exception_handler.py`
   pode devolver arquivo, linha e erro bruto; `DEBUG` tem default ativo em `src/shared/config/settings.py`.

## 5. Auth Module

| Capacidade | Status | Evidência | Estado real |
|---|---|---|---|
| User/AuthCredentials model | PARTIAL | `src/modules/auth/domain/entities/user.py`, `src/modules/auth/domain/value_objects/user_role.py`, `src/modules/auth/infrastructure/persistence/postgresql/models/users_model.py`, `src/modules/auth/infrastructure/persistence/postgresql/mappers/user_mapper.py`, migrations `1ce1f1cd457b_bancos_agora_em_docker.py` e `48f1a9d4c2b7_add_user_role_and_soft_delete.py` | Entidade, model e mapper preservam `role` e `deleted_at`; migration ainda não foi executada contra PostgreSQL nesta atualização e permanecem divergências históricas de schema/identificador/campos. |
| Cadastro | PARTIAL | `src/modules/auth/application/use_cases/signup/`, `src/modules/auth/presentation/controllers/sign_up_controller.py`, `src/modules/auth/presentation/routes.py` | Fluxo substancial; não há teste de cadastro nem E2E e a cadeia de verificação por e-mail não fecha. |
| Login | PARTIAL | `src/modules/auth/application/use_cases/login/`, `src/modules/auth/presentation/controllers/login_controller.py`, `src/modules/auth/infrastructure/persistence/postgresql/repositories/user_repository.py` | Mapper e consultas estão alinhados; os testes antigos de Login ainda não instanciam o UoW atual e não há teste E2E automatizado. Usuários com `deleted_at` deixam de ser retornados pelo repository. |
| Password hashing | IMPLEMENTED | `src/modules/auth/domain/ports/security/ipassword_hasher.py`, `src/modules/auth/infrastructure/security/argon2id_password_hasher.py` | Argon2id concreto com verify/rehash. |
| Geração/validação JWT | PARTIAL | `src/modules/auth/application/ports/token/`, `src/modules/auth/infrastructure/security/token_service.py` | Primitiva existe; access/refresh são indistinguíveis por claim/tipo. |
| Sessões e refresh | PARTIAL | `src/modules/auth/domain/entities/auth_session.py`, `src/modules/auth/application/services/auth_session/`, `src/modules/auth/infrastructure/persistence/postgresql/repositories/auth_sessions_repository.py` | Persistência existe; refresh usa atributo inexistente `_clock`. |
| Logoff | PARTIAL | `src/modules/auth/application/use_cases/logoff/`, `src/modules/auth/presentation/controllers/logoff_controller.py` | Estrutura existe; os dois testes coletam, mas falham no setup por ausência do UoW na fixture. |
| Solicitar reset de senha | PARTIAL | `src/modules/auth/application/use_cases/request_password_reset/`, `src/modules/auth/application/services/reset_password_service/`, `tests/unit/auth/application/services/test_password_reset_service.py` | Service persiste pelo repository recebido e o teste focal passa; o fluxo HTTP/mensageria não possui cobertura E2E automatizada. |
| Efetivar reset de senha | PARTIAL | `src/modules/auth/application/use_cases/reset_password/`, `src/modules/auth/infrastructure/persistence/postgresql/repositories/reset_password_repository.py`, migration `0633c30be51a_colocando_tabela_de_reset_de_password_.py` | Estrutura/persistência existem, sem cobertura automatizada completa do endpoint ao banco. |
| Verificação de e-mail | PARTIAL | `src/modules/auth/domain/entities/email_verification.py`, `src/modules/auth/application/use_cases/verify_email/`, `src/modules/auth/infrastructure/persistence/postgresql/repositories/user_email_verification_repository.py`, `tests/unit/auth/application/services/test_email_verification_service.py` | Repository/service e testes focais existem; falta cobertura E2E automatizada com banco e entrega assíncrona. |
| Perfil | PARTIAL | `src/modules/auth/domain/entities/user.py`, `src/modules/auth/application/use_cases/update_user_info/`, `src/modules/auth/infrastructure/persistence/postgresql/repositories/user_repository.py`, `src/modules/auth/presentation/controllers/update_user_info_controller.py`, `src/modules/auth/presentation/validators/update_user_info.py`, `src/modules/auth/presentation/routes.py`, testes em `tests/unit/auth/` | `PATCH /auth/user-info` exige Bearer, deriva o usuário do token e permite atualizar parcialmente apenas `name`, `surname`, `date_of_birth` e `avatar_url`. O repository restringe o SQL ao subconjunto realmente enviado e a usuários ativos. Permanece `PARTIAL` por ausência de teste HTTP/PostgreSQL real e porque upload/remoção de avatar no S3 não fazem parte deste incremento. |
| Avatar/S3 | NOT_STARTED | `src/` inspecionado | Nenhuma implementação S3. |
| Exclusão/anonimização | PARTIAL | `src/modules/auth/application/use_cases/request_delete/`, `src/modules/auth/application/use_cases/delete/`, `src/modules/auth/application/services/user_deletion/`, `src/modules/auth/domain/entities/user_deletion_request.py`, `src/modules/auth/infrastructure/persistence/postgresql/`, `src/modules/auth/presentation/controllers/request_delete_controller.py`, `src/modules/auth/presentation/controllers/delete_user_controller.py`, `src/modules/auth/presentation/routes.py`, migration `7b82d9e3a104_add_user_deletion_requests.py`, testes em `tests/unit/auth/` | Solicitação autenticada, código com hash/expiração/uso único, confirmação, `deleted_at`, revogação das sessões e eventos Outbox estão implementados e cobertos unitariamente. Permanece `PARTIAL` por ausência de teste PostgreSQL/API/AWS de ponta a ponta e de consumers de `auth.user.deleted` nos demais módulos. |
| Recuperação da conta | PARTIAL | `src/modules/auth/application/use_cases/request_recovery/`, `src/modules/auth/application/use_cases/recovery/`, `src/modules/auth/application/services/user_recovery/`, entidade/eventos/ports de recuperação, model/mapper/repository, controllers/rotas, migration `9c4f12a7e6d3_add_user_recovery_requests.py`, testes em `tests/unit/auth/` | Solicitação pública com resposta anti-enumeração, emissão de código com hash/expiração/uso único, restauração de `deleted_at` e eventos Outbox estão cobertos unitariamente. Permanece `PARTIAL` por ausência de teste PostgreSQL/API/AWS de ponta a ponta, prazo máximo de recuperação e consumers intermodulares de `auth.user.recovered`. |
| Exportação geral da conta | NOT_STARTED | `src/` inspecionado | Nenhum job/caso de uso/endpoint. |
| Admin authorization | PARTIAL | `src/modules/auth/domain/value_objects/user_role.py`, `src/modules/auth/public/authenticated_principal.py`, `src/modules/auth/application/services/http_request_auth/`, `src/modules/auth/presentation/services/fast_api_auth_service.py`, `src/modules/auth/presentation/adapters/fast_api_auth.py`, `src/modules/catalog/presentation/routes.py`, migration `48f1a9d4c2b7_add_user_role_and_soft_delete.py` | O contexto autenticado carrega a role persistida e `require_role(UserRole.ADMIN)` protege as cinco operações de `/catalog/themes`; faltam testes HTTP de acesso permitido/negado, diferenciar access/refresh token e implementar bootstrap/alteração administrativa de papel. |
| MFA | NOT_STARTED | `src/` inspecionado | Nenhuma implementação. |

Falhas concretas que impedem considerar os casos Auth como `IMPLEMENTED`:

- `src/modules/auth/application/services/auth_session/auth_session_service_impl.py` usa `self._clock`, mas o
  atributo criado é `self.__system_clock`;
- o login de usuário ainda não verificado emite evento e depois lança exceção antes do commit,
  levando o UoW a rollback;
- `src/modules/auth/domain/value_objects/password_plain.py` referencia `PASSWORD_MIN_LENGTH`, nome inexistente
  em settings, no caminho de erro de senha curta;
- o validator HTTP aceita senha de 8 caracteres, enquanto o domínio exige 12;
- a autenticação Bearer está instalada em `POST /auth/request-delete` e `PATCH /auth/user-info`, mas ainda não protege todas as rotas que exigiriam contexto autenticado.

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
| Fronteira física do módulo | PARTIAL | `src/modules/catalog/domain/`, `application/`, `infrastructure/`, `presentation/`, `bootstrap/`, `public/` |
| Neo4j runtime local | IMPLEMENTED | `docker-compose.infra.yml`; container `reflecta-neo4j-dev` respondeu a `RETURN 1` via Bolt |
| Neo4j driver/settings/adapter | PARTIAL | `pyproject.toml`, `src/shared/infrastructure/persistence/neo4j/`, `src/modules/catalog/infrastructure/persistence/neo4j/`, testes em `tests/unit/catalog/` e `tests/unit/shared/infrastructure/persistence/neo4j/` | Driver, settings, conexão, constraint, mapper, repository e UoW de `Theme` existem e têm cobertura unitária; não há teste de integração com Neo4j real. |
| Theme | PARTIAL | `src/modules/catalog/domain/entities/theme.py`, casos de uso em `src/modules/catalog/application/use_cases/`, persistência em `src/modules/catalog/infrastructure/persistence/neo4j/`, rota `src/modules/catalog/presentation/routes.py`, testes em `tests/unit/catalog/` | Criação em lote, busca por ID, listagem, atualização parcial, ativação/desativação e exclusão física estão compostas e protegidas por `ADMIN`. Atualização preserva o slug; faltam testes HTTP e integração com Neo4j real. |
| Author / Work / Passage | NOT_STARTED | `src/modules/catalog/` inspecionado; somente diretórios/arquivos vazios fora do fluxo preliminar de Theme |
| Relações RELATES_TO / BELONGS_TO / WRITTEN_BY | NOT_STARTED | `src/` inspecionado |
| CRUD e revisão administrativa | PARTIAL | O fluxo vertical de `Theme` expõe `POST`, `GET` lista, `GET` por ID, `PATCH` e `DELETE`; escritas usam commit explícito e falhas usam rollback do UoW. Não há paginação/filtros nem confirmação de exclusão física quando futuras relações existirem. |
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
| `POST /auth/request-delete` | PARTIAL | `src/modules/auth/presentation/routes.py`, `request_delete_controller.py`, caso de uso `request_delete/` | Exige Bearer, deriva o usuário do contexto autenticado e grava solicitação + evento na mesma UoW; falta teste HTTP/PostgreSQL/AWS de ponta a ponta. |
| `DELETE /auth/delete` | PARTIAL | `src/modules/auth/presentation/routes.py`, `delete_user_controller.py`, caso de uso `delete/` | Consome código de uso único, marca exclusão lógica, encerra sessões e grava evento; falta teste de integração real. |
| `POST /auth/request-recovery` | PARTIAL | `src/modules/auth/presentation/routes.py`, `request_recovery_controller.py`, caso de uso `request_recovery/` | Público; recebe e-mail validado e responde genericamente. Só conta excluída gera código/evento. Falta teste HTTP/PostgreSQL/AWS de ponta a ponta. |
| `POST /auth/recovery` | PARTIAL | `src/modules/auth/presentation/routes.py`, `recovery_controller.py`, caso de uso `recovery/` | Consome código de uso único, restaura `deleted_at` e grava evento sem criar sessão. Falta teste de integração real. |
| `PATCH /auth/user-info` | PARTIAL | `src/modules/auth/presentation/routes.py`, `update_user_info_controller.py`, caso de uso `update_user_info/`, `user_repository.py` | Exige Bearer no OpenAPI, usa o `user_id` autenticado e aceita de um a quatro campos de perfil. Há cobertura unitária de domínio, caso de uso, controller, validator e escopo do SQL; falta teste HTTP/PostgreSQL real. |
| `POST /catalog/themes` | PARTIAL | `src/modules/catalog/presentation/routes.py`, controller/validator, caso de uso `create_themes/`, bootstrap e UoW/repository Neo4j | Exige Bearer com papel `ADMIN`, aceita lote não vazio e responde 201; OpenAPI e unidades internas foram verificados, mas falta teste HTTP e Neo4j real. |
| `GET /catalog/themes` | PARTIAL | rota, `GetAllThemesController`, `GetAllThemesUseCase`, UoW/repository e testes unitários | Exige `ADMIN`, lista temas ativos e inativos e aceita resultado vazio; falta teste HTTP/Neo4j real. |
| `GET /catalog/themes/{theme_id}` | PARTIAL | rota, `GetThemeByIdController`, `GetThemeByIdUseCase`, exceção `ThemeNotFoundError` e testes unitários | Exige `ADMIN`, retorna o tema ou 404; falta teste HTTP/Neo4j real. |
| `PATCH /catalog/themes/{theme_id}` | PARTIAL | rota/validator, `UpdateThemeController`, `UpdateThemeUseCase`, entidade/repository e testes unitários | Exige `ADMIN`, atualiza label, descrição e/ou estado, rejeita payload vazio/nulo e mantém o slug estável; falta teste HTTP/Neo4j real. |
| `DELETE /catalog/themes/{theme_id}` | PARTIAL | rota, `DeleteThemeByIdController`, `DeleteThemeByIdUseCase`, repository e testes unitários | Exige `ADMIN`, retorna 204, valida existência e executa `DETACH DELETE`; falta teste HTTP/Neo4j real e decisão final sobre exclusão física com relações futuras. |
| Demais endpoints planejados | NOT_STARTED | `src/main/server/fast_api/server.py`, módulos inspecionados | Journal não possui Presentation; não há AI, Recommendation, Sharing ou Notification API, nem operações de Author/Work/Passage no Catalog. |

DTOs e validators existem principalmente em `src/modules/auth/application/use_cases/*/dto.py` e
`src/modules/auth/presentation/validators/`, mas login/reset não estão integrados ao schema FastAPI de modo a
gerar contrato OpenAPI. `POST /auth/request-delete` e `PATCH /auth/user-info` anunciam `HTTPBearer` no OpenAPI; as demais rotas continuam sem security scheme explícito.

## 9. Persistência e migrations

### 9.1 Estado real do PostgreSQL

| Item | Status | Evidência | Estado real |
|---|---|---|---|
| Metadata SQLAlchemy | IMPLEMENTED | `src/shared/infrastructure/persistence/postgresql/configs/base.py`, models em `src/modules/auth/` e `src/modules/internal_events/` | Oito tabelas são registradas. |
| Tabela `users` | PARTIAL | `users_model.py`, migration `1ce1f1cd457b_bancos_agora_em_docker.py` | Auth parcial; campos divergentes do planejado. |
| Tabela `auth_credentials` | PARTIAL | `auth_credentials_model.py`, mesma migration | Sem MFA/credential_type documentados. |
| Tabela `auth_sessions` | PARTIAL | `auth_sessions_model.py`, mesma migration | Sem IP/user-agent; refresh token hash existe. |
| Tabela `user_email_verifications` | PARTIAL | `user_email_verification_model.py`, mesma migration | Implementação adicional ao modelo consolidado, mas fluxo está quebrado. |
| Tabela `passwords_reset` | PARTIAL | `reset_password_model.py`, migration `0633c30be51a_colocando_tabela_de_reset_de_password_.py` | Nome e modelo divergem da documentação. |
| Tabela `outbox` | PARTIAL | `outbox_model.py`, migrations `631fd4384bca_criando_tabela_do_pattern_outbox_nao_.py` e `ca9163c93ce6_01_09_2026_atualizando_a_tabela_de_.py` | Suporta estados/retry, sem contrato documentado completo. |
| Tabela `user_deletion_requests` | PARTIAL | `src/modules/auth/infrastructure/persistence/postgresql/models/user_deletion_request_model.py`, mapper/repository correspondentes, migration `7b82d9e3a104_add_user_deletion_requests.py` | Modela hash, expiração, confirmação, revogação e uma única solicitação ativa por usuário; aplicação em PostgreSQL real ainda não verificada. |
| Tabela `user_recovery_requests` | PARTIAL | `src/modules/auth/infrastructure/persistence/postgresql/models/user_recovery_request_model.py`, mapper/repository correspondentes, migration `9c4f12a7e6d3_add_user_recovery_requests.py` | Modela hash, expiração, confirmação, revogação e uma única solicitação ativa por usuário; aplicação em PostgreSQL real ainda não verificada. |
| Cadeia Alembic | IMPLEMENTED | `alembic/versions/` | Uma head `9c4f12a7e6d3`; `4c9d09eb81e5_criando_tabela_do_pattern_outbox.py` é migration vazia. |
| Execução em PostgreSQL real | NOT_VERIFIED | `docker-compose.infra.yml` | Docker CLI/Compose está disponível, mas daemon, container e conexão com o banco não foram verificados nesta análise. |
| `auth_schema` | NOT_STARTED | models/migrations | Todas as tabelas usam o schema padrão (`schema=None`). |
| `journal_schema` | NOT_STARTED | models/migrations | Ausente. |
| `recommendation_schema` | NOT_STARTED | models/migrations | Ausente. |
| `sharing_schema` | NOT_STARTED | models/migrations | Ausente. |
| `event_schema` | NOT_STARTED | models/migrations | Outbox usa schema padrão. |
| Extensão/colunas/índices pgvector | NOT_STARTED | migrations/models | Nenhum `CREATE EXTENSION`, `VECTOR`, dimensão ou índice. |
| Neo4j | PARTIAL | `docker-compose.infra.yml`, `src/shared/infrastructure/persistence/neo4j/`, `src/modules/catalog/infrastructure/persistence/neo4j/` | Serviço local, driver, constraint Cypher, repository e UoW unitariamente testados; execução da constraint e criação de temas contra o Neo4j real continuam não verificadas. |
| Relação PostgreSQL–Neo4j | NOT_STARTED | projeto inteiro | Ausente. |

Os identificadores persistidos são strings ULID de 26 caracteres, não UUID. O downgrade da migration
que adiciona o valor `PROCESSING` ao enum do outbox não remove esse valor.

`src/shared/config/settings.py` monta `database_url` usando `POSTGRES_PORT` também na posição do host; essa URL
é inválida para a configuração nominal e aumenta o risco de falha fora do caminho atual de conexão.

## 10. Eventos, Outbox e workers

| Capacidade | Status | Evidência | Estado real |
|---|---|---|---|
| Entidade/model/tabela Outbox | PARTIAL | `src/modules/internal_events/domain/entities/outbox_event.py`, `src/modules/internal_events/infrastructure/persistence/postgresql/models/outbox_model.py`, migrations Outbox | Estrutura real existe e diverge do contrato documentado. |
| Escrita transacional Auth + Outbox | PARTIAL | `src/modules/internal_events/application/services/outbox_service_impl.py`, `src/modules/auth/infrastructure/persistence/postgresql/units_of_work/auth_unit_of_work_impl.py`, casos signup/reset/exclusão | Exclusão grava solicitação/estado e evento na mesma UoW; os demais fluxos ainda possuem lacunas e não há teste PostgreSQL de integração. |
| Claim concorrente | IMPLEMENTED | `src/modules/internal_events/infrastructure/persistence/postgresql/repositories/outbox_repository.py` | Usa `FOR UPDATE SKIP LOCKED`, marca `PROCESSING` e incrementa tentativas. |
| Retry/backoff | PARTIAL | `src/modules/internal_events/infrastructure/strategies/exponential_retry.py`, `src/modules/internal_events/infrastructure/messaging/workers/outbox_dispatcher_worker.py` | Backoff existe; evento abandonado em `PROCESSING` não é recuperado após crash. |
| Dispatcher | PARTIAL | `src/modules/internal_events/infrastructure/messaging/workers/outbox_dispatcher_worker.py`, `src/modules/internal_events/bootstrap/workers/publishers/sns/sns_outbox_dispatcher.py`, `docker-compose.api_workers.yml` | Worker neutro de broker está composto com publisher SNS no Compose; ciclo automatizado com PostgreSQL/AWS ainda não foi revalidado nesta atualização. |
| Event Router | IMPLEMENTED | `src/modules/internal_events/infrastructure/messaging/routing/event_router.py`, `src/modules/internal_events/bootstrap/event_router.py` | A rota SNS genérica aceita os eventos da Outbox; rotas legadas específicas para RabbitMQ/SQS permanecem no código. |
| Topologia RabbitMQ | IMPLEMENTED | `src/modules/internal_events/infrastructure/messaging/rabbitmq/topology.py` | Declara exchange direta, filas principais, retry e DLQ; publicação/retirada de mensagem foi verificada localmente. |
| RabbitMQ publishers | PARTIAL | `src/modules/internal_events/infrastructure/messaging/rabbitmq/publishers/`, `src/modules/internal_events/bootstrap/rabbitmq/publishers.py` | Os dois publishers antigos existem, mas o dispatcher efetivo no Compose foi alterado para SNS e não há publisher RabbitMQ para exclusão. |
| RabbitMQ e-mail consumers | PARTIAL | `src/modules/notification/infrastructure/messaging/rabbitmq/consumers/`, `src/modules/notification/bootstrap/workers/rabbitmq/` | Os dois adapters de fila delegam ao mesmo `EmailEventHandler`; execução com SMTP real e idempotência não foram verificadas nesta auditoria. |
| Consumer Lambda/SQS | PARTIAL | `src/modules/notification/infrastructure/messaging/aws/sqs/lambda_sqs_emails_consumer.py`, `src/modules/notification/bootstrap/aws/lambda_emails.py` | Processa raw delivery, converte `event_type`, usa handler/SES e retorna falhas parciais por item; faltam idempotência, testes do entrypoint e deploy reproduzível. |
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
- `emails.password_reset.requested` — `src/modules/auth/domain/events/emails/password_reset_requested.py`;
- `emails.user_deletion.requested` — `src/modules/auth/domain/events/emails/user_deletion_requested.py`;
- `auth.user.deleted` — `src/modules/auth/domain/events/user_account_deleted.py`;
- `emails.recovery_user.requested` — `src/modules/auth/domain/events/emails/user_recovery_requested.py`;
- `auth.user.recovered` — `src/modules/auth/domain/events/user_account_recovered.py`.

Não há eventos Journal. Os códigos brutos de verificação/reset/exclusão são colocados no payload do Outbox; o
consumer RabbitMQ registra o corpo integral da mensagem, criando risco de exposição de dados sensíveis.

`docker-compose.api_workers.yml` inicia o dispatcher SNS da Outbox e ainda inicia os dois consumers RabbitMQ.
Esses consumers locais não recebem mensagens publicadas no SNS; o caminho AWS depende do trigger SQS/Lambda configurado fora do Compose.

## 11. Notification e integrações externas

| Capacidade | Status | Evidência | Estado real |
|---|---|---|---|
| Email port/DTO unificados | IMPLEMENTED | `src/modules/notification/application/ports/notifiers/dto.py`, `iemail_notifier.py` | Um `EmailDTO` usa `link` genérico e `EmailKind`; o token bruto não atravessa o port do notifier. |
| Handler de eventos de e-mail | IMPLEMENTED | `src/modules/notification/application/handlers/email_event_handler.py`, `src/modules/notification/application/ports/handlers/iemail_event_handler.py` | Mapeia quatro `event_type`, valida payload e constrói os links sem depender de RabbitMQ/SQS. |
| SMTP adapter/templates | PARTIAL | `src/modules/notification/infrastructure/email/smtp/smtp_email_notifier.py`, `src/modules/notification/infrastructure/email/templates/` | Um adapter renderiza os quatro templates e envia de forma assíncrona; entrega externa não foi verificada nesta atualização. |
| NotificationWorker | PARTIAL | `src/modules/notification/bootstrap/workers/`, `src/modules/notification/infrastructure/messaging/aws/sqs/lambda_sqs_emails_consumer.py` | RabbitMQ e Lambda/SQS chegam ao handler unificado, mas o Compose mistura dispatcher SNS com consumers RabbitMQ e não há idempotência. |
| TemplateRenderer independente | NOT_STARTED | `src/modules/notification/infrastructure/email/smtp/` | Templates estão embutidos nos adapters. |
| NotificationLog | NOT_STARTED | models/migrations/repositories | Ausente. |
| SES | PARTIAL | `src/modules/notification/infrastructure/email/ses/ses_notifier.py`, `src/modules/notification/bootstrap/aws/lambda_emails.py`, testes SES | Adapter e composição Lambda existem e têm testes unitários; envio externo não foi revalidado nesta atualização. |
| S3 | NOT_STARTED | projeto inteiro | Ausente. |
| Neo4j | PARTIAL | `docker-compose.infra.yml`, `src/modules/catalog/infrastructure/persistence/neo4j/` | Infraestrutura local e adapter unitário de `Theme` existem; integração do UoW/Catalog com Neo4j real ainda está ausente. |
| Provedor de IA | NOT_STARTED | projeto inteiro | Ausente. |
| RabbitMQ local | IMPLEMENTED | Compose/config/topologia | Container, conexão, declaração de topologia, publicação e retirada de mensagem verificados localmente. |
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
| Sintaxe Python | IMPLEMENTED | arquivos sob `src/`, `tests/` e `alembic/` | `compileall` sem falhas após a atualização parcial de perfil. |
| Unitários Application/Auth | PARTIAL | `tests/unit/application/use_cases/login/`, `tests/unit/application/use_cases/logoff/` | Sete testes escritos: cinco login e dois logoff; estão desatualizados. |
| Coleta pytest | IMPLEMENTED | `tests/` | 125 testes coletados: 118 aprovados e sete erros de setup preexistentes. |
| Testes Domain | PARTIAL | `tests/unit/auth/domain/` | Cobrem `UserRole`, parte do estado de exclusão e as regras de atualização parcial do perfil; demais domínios continuam sem cobertura. |
| Integração repository/PostgreSQL | NOT_STARTED | `tests/` inspecionado | Nenhum teste de integração; o antigo diretório vazio foi removido. |
| API/HTTP | NOT_STARTED | `tests/` inspecionado | Ausentes. |
| Outbox/roteamento | PARTIAL | `tests/unit/internal_events/infrastructure/messaging/test_rabbitmq_outbox_dispatcher.py` | Dois testes aprovados cobrem roteamento por tipo e marcação `SENT`; idempotência permanece ausente. |
| Exclusão lógica Auth | IMPLEMENTED | `tests/unit/auth/application/services/test_user_deletion_service.py`, `tests/unit/auth/application/use_cases/test_user_deletion_use_cases.py`, testes de controller/mapper/repository | Doze testes aprovados cobrem emissão/substituição, confirmação, expiração, revogação/reuso, sessões, eventos e adapters HTTP/persistência. |
| Recuperação Auth | IMPLEMENTED | `tests/unit/auth/application/services/test_user_recovery_service.py`, `tests/unit/auth/application/use_cases/test_user_recovery_use_cases.py`, testes de controller/mapper/repository | Dezesseis testes novos cobrem emissão/substituição, anti-enumeração, confirmação, expiração, revogação/reuso, estado excluído e adapters HTTP/persistência. |
| Atualização de perfil Auth | IMPLEMENTED | `tests/unit/auth/domain/test_user_info.py`, `tests/unit/auth/application/use_cases/test_update_user_info_use_case.py`, `tests/unit/auth/presentation/controllers/test_update_user_info_controller.py`, `tests/unit/auth/infrastructure/persistence/postgresql/repositories/test_user_repository_active_users.py` | Dezessete testes novos cobrem regras de domínio, atualização de subconjunto, identidade autenticada, validação do payload e allowlist de colunas no SQL. |
| Notification handler/templates | IMPLEMENTED | `tests/unit/notification/` | Quinze testes aprovados cobrem os quatro tipos de evento, links, payload inválido, tipo desconhecido, templates SMTP/SES e diagnóstico SES sem vazamento de e-mail, código ou mensagem bruta da AWS. |
| Catalog/Neo4j | PARTIAL | `tests/unit/catalog/`, `tests/unit/shared/infrastructure/persistence/neo4j/test_connection.py` | Trinta e oito testes aprovados cobrem CRUD de casos de uso, DTOs, validators, slug estável, conflitos, 404, repository, commit/rollback do UoW e configuração do driver; ainda não há teste HTTP ou integração com Neo4j real. |
| LLM contract | NOT_STARTED | `tests/` inspecionado | Ausentes. |
| Frontend | NOT_STARTED | repositório | Frontend ausente. |
| E2E | NOT_STARTED | `tests/` inspecionado | Nenhum teste E2E; o antigo diretório vazio foi removido. |
| API import/OpenAPI | IMPLEMENTED | `src/main/server/fast_api/run.py` | Importação e enumeração de rotas tiveram sucesso com env temporário. |
| Docker/PostgreSQL/brokers | PARTIAL | Compose e smoke tests locais | Neo4j respondeu via Bolt e RabbitMQ foi verificado anteriormente; PostgreSQL e a stack completa não foram revalidados nesta atualização. |

O pacote de login agora exporta `LoginUseCaseImpl` sem o ciclo Application anterior. Fixtures e doubles
continuam refletindo assinaturas antigas: ausência de UoW/Outbox, `AuthSessionResultDTO` sem `session_id`
e construtores incompatíveis com os casos de uso atuais. Por isso os sete testes Auth falham no setup.

## 14. Divergências entre código e documentação

Estas divergências permanecem abertas; o código foi usado apenas como evidência do estado atual. Este
diagnóstico **não decide automaticamente** se código ou documentação deve ser modificado.

1. **Identidade do sistema:** documentação consolidada usa Reflecta; `pyproject.toml`, settings, título
   FastAPI, Compose e remetente SMTP ainda usam Individuum.
2. **Arquitetura modular:** Auth, Journal, Internal Events e Notification possuem raízes verticais;
   Shared Kernel técnico e `main` foram separados, mas somente Auth é substancial.
3. **Mensageria:** SQS + Lambda + SES é o alvo decidido em 2026-08-31, mas o código operacional ainda
   conecta Outbox, publisher e consumers via RabbitMQ/SMTP; o consumer SQS permanece apenas embrionário.
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
13. **Neo4j, S3 e IA:** Neo4j possui runtime local, driver, constraint e primeira fatia vertical de `Theme`,
    porém o modelo documentado usa UUID e o código usa ULID; S3 e IA continuam ausentes do código/infra real.
14. **Frontend:** TCC contém interfaces/mockups; não há frontend no repositório.
15. **Testes:** TCC descreve cenários e uma matriz ampla; atualmente, 118 testes passam e sete
    testes antigos de Login/Logoff falham no setup.
16. **Deploy/workers:** o Compose declara dispatcher RabbitMQ e dois workers Notification e depende
    de `.env.dev` não versionado; o fluxo Catalog/Neo4j ainda não foi validado de ponta a ponta.
17. **OpenAPI/Auth:** documentação sugere contratos HTTP usuais; cinco rotas Auth não expõem
    body/parâmetros/security na spec, e login usa Basic Auth sem registrá-lo.

### Divergências internas da própria documentação

- o escopo atual é journaling textual, mas o TCC ainda mostra áudio/imagem e S3 para mídia;
- `ConsentService/Repository` existe no componente Sharing sem entidade/tabela Consent;
- casos administrativos exigem autorização efetiva; o CRUD de temas usa o guard `ADMIN`, mas faltam testes HTTP do acesso e access/refresh token continuam sem propósito distinguível;
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

1. Concluir o baseline canônico de Auth: schemas e UUID versus ULID, campos ainda divergentes de
   User/Credentials/Session, prioridade de MFA, bootstrap do primeiro administrador e alteração de papel. A representação
   `USER`/`ADMIN`, a exclusão lógica por `deleted_at` e a propagação da role persistida no contexto autenticado já foram implementadas.
2. SQS + Lambda + SES foi escolhido como alvo para notificações Auth; ainda é necessário implementar o
   consumer versionado, adapter SES, idempotência, falha parcial, deploy e cutover antes de remover RabbitMQ/SMTP.
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
11. Confirmar se `Theme` poderá ser removido fisicamente quando possuir relações com Work/Passage ou se
    `is_active=false` deverá ser a única forma permitida de retirada do catálogo.

## 16. Riscos técnicos

- **Corrupção/interferência concorrente:** UoWs globais guardam sessão/repositories mutáveis por request.
- **Fluxos Auth quebrados:** mapper, relógio, expiração e dependência de reset falham em caminhos normais.
- **Proteção parcial:** `POST /auth/request-delete` e `PATCH /auth/user-info` usam Bearer, mas o middleware/guard Auth não está aplicado de forma uniforme às demais rotas protegidas planejadas.
- **Refresh usado como access token:** tokens não distinguem propósito criptograficamente.
- **Perda de eventos:** crash após marcar `PROCESSING` deixa evento sem mecanismo de reclaim.
- **Entrega ainda não comprovada de ponta a ponta:** RabbitMQ foi conectado, mas SMTP real, payload completo,
  retry e idempotência do consumer ainda não foram exercitados juntos.
- **Exposição de segredos/PII:** códigos brutos de verificação/reset/exclusão/recuperação no Outbox e log integral do consumer;
  erros detalhados em debug; `HttpRequest.__repr__` inclui headers/body.
- **Configuração não reproduzível:** sem `.env.example` e com helper de URL do banco malformado.
- **Rede de segurança insuficiente:** 118 testes unitários passam, mas não há integração/API/E2E/CI e os
  sete testes antigos de Login/Logoff continuam quebrados no setup.
- **Exclusão destrutiva futura no grafo:** o endpoint de exclusão de `Theme` usa `DETACH DELETE`; quando
  existirem relações com Work/Passage, ele também removerá essas relações sem histórico.
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
- Docker Compose declara o dispatcher do Outbox, mas depende de `.env.dev` local e não existe `.env.example` versionado;
- não há health checks da aplicação, CI, métricas ou tracing.

## 18. Menor próximo incremento vertical coerente

**Não iniciado por esta refatoração.**

O menor incremento recomendado agora é tornar idempotente e reproduzível a entrega de notificações Auth no caminho
**SNS -> SQS -> Lambda -> handler Notification -> SES**, reutilizando o `EmailEventHandler` já implementado.
O corte deve incluir:

1. persistência de idempotência por `event_id` e consumidor;
2. tratamento de lease/estado `PROCESSING` abandonado;
3. testes do envelope dos quatro eventos de e-mail, duplicidade e falhas transitória/permanente;
4. infraestrutura e pacote/deploy versionados a partir do repositório;
5. teste de integração da Outbox ao SES e observabilidade de DLQ.

RabbitMQ/SMTP não devem ser removidos antes do teste ponta a ponta do novo caminho. O incremento não altera
os nomes nem o payload canônico dos quatro eventos de e-mail Auth e não inicia Journal/IA.

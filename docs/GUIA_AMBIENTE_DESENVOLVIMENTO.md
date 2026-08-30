# Reflecta — Guia de ambiente de desenvolvimento

Este guia prepara o projeto no Windows usando PowerShell, UV, Docker Desktop com WSL 2,
PostgreSQL, RabbitMQ e Alembic.

> Estado em 2026-08-30: a infraestrutura local e o caminho RabbitMQ foram verificados. A suíte possui
> nove testes coletados: dois testes Internal Events passam e sete testes Auth ainda falham no setup por
> fixtures desatualizadas. Não interprete a inicialização do ambiente como aprovação funcional de todo o Auth.

## 1. Visão rápida

O backend é um monólito modular Python/FastAPI:

```text
src/
  main/       entrada FastAPI e composição final
  modules/    Auth, Journal, Internal Events e Notification
  shared/     configuração e infraestrutura técnica compartilhada
```

Fluxo assíncrono vigente para notificações Auth:

```text
API/Auth
  -> transação PostgreSQL
  -> tabela outbox
  -> worker_outbox_dispatcher
  -> publisher RabbitMQ
  -> consumer Notification
  -> SMTP
```

O código SQS permanece como legado inativo. O fluxo conectado atualmente usa RabbitMQ.

## 2. Pré-requisitos

- Windows 10/11 de 64 bits com virtualização habilitada no BIOS/UEFI;
- Git;
- PowerShell;
- UV;
- WSL 2 atualizado;
- Docker Desktop configurado para containers Linux/WSL 2;
- DBeaver opcional para inspecionar o banco.

Referências oficiais:

- UV: <https://docs.astral.sh/uv/getting-started/installation/>;
- WSL: <https://learn.microsoft.com/windows/wsl/install>;
- Docker Desktop no Windows: <https://docs.docker.com/desktop/setup/install/windows-install/>;
- backend WSL 2 do Docker: <https://docs.docker.com/desktop/features/wsl/>.

## 3. Obter o repositório

Clone usando a URL fornecida pelo responsável pelo projeto e entre na pasta:

```powershell
git clone <URL_DO_REPOSITORIO>
Set-Location .\Individuum_MVP
```

Se o repositório já estiver no computador, apenas entre na pasta que contém `pyproject.toml`:

```powershell
Set-Location "C:\caminho\para\Individuum_MVP"
```

## 4. Instalar e configurar o UV

### 4.1 Instalação recomendada no Windows

No PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Feche e abra o PowerShell. Depois verifique:

```powershell
uv --version
```

Alternativa oficial usando WinGet:

```powershell
winget install --id=astral-sh.uv -e
```

### 4.2 Quando `uv` não estiver no PATH

O instalador standalone normalmente coloca o executável em `.local\bin` dentro do perfil do usuário.
Defina uma variável PowerShell para evitar caminhos específicos de uma máquina:

```powershell
$UvPath = Join-Path $env:USERPROFILE ".local\bin\uv.exe"
& $UvPath --version
```

Nos comandos seguintes, use `uv` se ele estiver no PATH ou `& $UvPath` caso contrário.

### 4.3 Instalar as dependências do projeto

Na raiz do repositório:

```powershell
$UvPath = Join-Path $env:USERPROFILE ".local\bin\uv.exe"
& $UvPath sync --locked
```

- `pyproject.toml` declara as dependências diretas;
- `uv.lock` fixa as versões resolvidas;
- `.venv` é criada/atualizada automaticamente;
- não existe `requirements.txt` neste projeto;
- não edite `uv.lock` manualmente.

## 5. Instalar WSL 2 e Docker Desktop

Se WSL ainda não estiver instalado, abra o PowerShell como administrador:

```powershell
wsl --install
```

Atualize e confira:

```powershell
wsl --update
wsl --version
```

Reinicie o Windows se o instalador solicitar.

Instale o Docker Desktop pelo instalador oficial e selecione o backend WSL 2. No Docker Desktop,
confira **Settings > General > Use WSL 2 based engine**. Depois inicie o Docker Desktop e valide:

```powershell
docker version
docker compose version
```

`docker version` precisa exibir Client e Server. Se mostrar apenas Client e erro do daemon, abra o
Docker Desktop e aguarde o engine iniciar.

### 5.1 Se o Docker não detectar virtualização

Confirme no BIOS/UEFI que AMD-V/SVM ou Intel VT-x está habilitado. No PowerShell como administrador:

```powershell
Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform
Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
```

Os recursos necessários devem estar habilitados. Se o hypervisor estiver desabilitado no boot:

```powershell
bcdedit /set hypervisorlaunchtype auto
```

Reinicie o computador após mudar recursos de virtualização/hypervisor.

## 6. Criar `.env.dev`

O arquivo é local, contém segredos e está ignorado pelo Git. Crie `.env.dev` na mesma pasta de
`pyproject.toml` com o conteúdo abaixo:

```dotenv
ENV=dev
DEBUG=true
LOG_LEVEL=INFO
APP_NAME=Reflecta

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
POSTGRES_DB=individuum_mvp_dev

ALEMBIC_CONNECTION_STRING=postgresql+psycopg2://admin:admin@localhost:5432/individuum_mvp_dev
ALEMBIC_MIGRATE=false

JWT_SECRET=reflecta-local-development-secret-change-me

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=test@example.com
SMTP_PASSWORD=not-configured-yet

AWS_SQS_REGION=us-east-1
AWS_SQS_EMAILS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/000000000000/not-used
BATCH_LIMIT=10
ATTEMPTS_LIMIT=5

RABBITMQ_URL=amqp://admin:admin@rabbitmq:5672/
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=admin
RABBITMQ_VIRTUAL_HOST=/
RABBITMQ_USE_SSL=false

RABBITMQ_EMAIL_EXCHANGE=emails
RABBITMQ_EMAIL_DLX_EXCHANGE=emails.dlx

RABBITMQ_EMAIL_VERIFICATION_QUEUE=email.verification
RABBITMQ_EMAIL_VERIFICATION_RETRY_QUEUE=email.verification.retry
RABBITMQ_EMAIL_VERIFICATION_DLX_QUEUE=email.verification.dlq
RABBITMQ_EMAIL_VERIFICATION_ROUTING_KEY=email.verification
RABBITMQ_EMAIL_VERIFICATION_RETRY_ROUTING_KEY=email.verification.retry
RABBITMQ_EMAIL_VERIFICATION_DLX_ROUTING_KEY=email.verification.dlq

RABBITMQ_PASSWORD_RESET_QUEUE=password.reset
RABBITMQ_PASSWORD_RESET_RETRY_QUEUE=password.reset.retry
RABBITMQ_PASSWORD_RESET_DLX_QUEUE=password.reset.dlq
RABBITMQ_PASSWORD_RESET_ROUTING_KEY=password.reset
RABBITMQ_PASSWORD_RESET_RETRY_ROUTING_KEY=password.reset.retry
RABBITMQ_PASSWORD_RESET_DLX_ROUTING_KEY=password.reset.dlq

RABBITMQ_MAX_RETRIES=5
FRONT_END_DOMAIN=http://localhost:8000
```

Os valores SQS são placeholders porque `Settings` ainda os exige, embora o fluxo ativo use RabbitMQ.
As credenciais SMTP são fictícias. Não tente enviar e-mail antes de configurar um SMTP válido ou um
capturador local de e-mail.

O hostname `rabbitmq` funciona dentro dos containers Docker. Para executar manualmente um worker no
Windows, sobrescreva temporariamente a URL:

```powershell
$env:RABBITMQ_URL = "amqp://admin:admin@localhost:5672/"
```

## 7. Subir PostgreSQL e RabbitMQ

Na raiz do projeto:

```powershell
docker compose -f docker-compose.infra.yml up -d
docker compose -f docker-compose.infra.yml ps
```

Serviços esperados:

| Serviço | Porta no Windows | Uso |
|---|---:|---|
| `postgres_dev` | 5432 | banco de desenvolvimento |
| `postgres_test` | 5433 | banco de testes |
| `rabbitmq` | 5672 | protocolo AMQP |
| painel RabbitMQ | 15672 | interface web |

O aviso de que o atributo Compose `version` é obsoleto não impede a execução atual.

Nunca use `docker compose down -v` sem intenção explícita de apagar os volumes e todos os dados locais.

## 8. Aplicar as migrations

As migrations são executadas no host. Defina `ENV` na mesma sessão PowerShell:

```powershell
$env:ENV = "dev"
$UvPath = Join-Path $env:USERPROFILE ".local\bin\uv.exe"

& $UvPath run alembic heads
& $UvPath run alembic current
& $UvPath run alembic upgrade head
& $UvPath run alembic current
```

Head esperada:

```text
ca9163c93ce6 (head)
```

Em um banco vazio, o primeiro `alembic current` pode não mostrar revisão. Depois de `upgrade head`, deve
mostrar `ca9163c93ce6`.

Não execute `alembic revision --autogenerate` durante o setup: esse comando cria uma migration nova.

### 8.1 Erro com muitas variáveis `Field required`

Isso ocorre quando `ENV` não foi definida e `.env.dev` não foi carregado. Execute em uma única linha:

```powershell
$env:ENV="dev"; & $UvPath run alembic upgrade head
```

## 9. Conferir o PostgreSQL

Liste as tabelas pelo terminal:

```powershell
docker exec individuum-postgres-dev psql -U admin -d individuum_mvp_dev -c "\dt"
```

Tabelas esperadas no schema `public`:

```text
alembic_version
users
auth_credentials
auth_sessions
user_email_verifications
passwords_reset
outbox
```

Confira a revisão:

```powershell
docker exec individuum-postgres-dev psql -U admin -d individuum_mvp_dev -c "SELECT * FROM alembic_version;"
```

Inspecione colunas específicas:

```powershell
docker exec individuum-postgres-dev psql -U admin -d individuum_mvp_dev -c "\d users"
docker exec individuum-postgres-dev psql -U admin -d individuum_mvp_dev -c "\d auth_credentials"
docker exec individuum-postgres-dev psql -U admin -d individuum_mvp_dev -c "\d auth_sessions"
docker exec individuum-postgres-dev psql -U admin -d individuum_mvp_dev -c "\d user_email_verifications"
docker exec individuum-postgres-dev psql -U admin -d individuum_mvp_dev -c "\d passwords_reset"
docker exec individuum-postgres-dev psql -U admin -d individuum_mvp_dev -c "\d outbox"
```

## 10. Conectar pelo DBeaver

Crie uma conexão PostgreSQL com:

```text
Host: localhost
Port: 5432
Database: individuum_mvp_dev
Username: admin
Password: admin
```

Clique em **Test Connection**, aceite o download do driver se necessário e finalize. Depois navegue por:

```text
individuum_mvp_dev
  -> Databases
  -> individuum_mvp_dev
  -> Schemas
  -> public
  -> Tables
```

O modelo planejado cita `auth_schema`, mas a implementação/migrations atuais criam as tabelas em `public`.

Banco de testes, se necessário:

```text
Host: localhost
Port: 5433
Database: individuum_mvp_test
Username: admin
Password: admin
```

## 11. Subir a API e o dispatcher

Primeiro suba somente a API e o dispatcher da Outbox:

```powershell
docker compose -f docker-compose.api_workers.yml up -d --build api worker_outbox_dispatcher
docker compose -f docker-compose.api_workers.yml ps
```

Confira os logs:

```powershell
docker compose -f docker-compose.api_workers.yml logs --tail 100 api
docker compose -f docker-compose.api_workers.yml logs --tail 100 worker_outbox_dispatcher
```

Swagger/OpenAPI:

```text
http://localhost:8000/docs
```

Endpoints Auth atuais:

```text
POST /auth/signup
POST /auth/login
POST /auth/logoff
POST /auth/refresh
GET  /auth/verify-email
POST /auth/reset-password
POST /auth/request-reset-password
```

Exemplo de cadastro — use senha com pelo menos 12 caracteres para satisfazer validator e domínio:

```json
{
  "email": "teste@example.com",
  "username": "teste",
  "name": "Usuario",
  "surname": "Teste",
  "date_of_birth": "2000-01-01",
  "password": "SenhaTeste123",
  "password_confirm": "SenhaTeste123"
}
```

O Auth ainda possui falhas conhecidas. Um erro de endpoint deve ser diagnosticado; não assuma que é um
problema do Docker ou do banco.

## 12. Conferir Outbox e RabbitMQ

Após uma operação que gere evento:

```powershell
docker exec individuum-postgres-dev psql -U admin -d individuum_mvp_dev -c "SELECT id, event_type, status, attempts, last_error FROM outbox ORDER BY created_at DESC;"
```

Painel RabbitMQ:

```text
URL:      http://localhost:15672
Usuário:  admin
Senha:    admin
```

Filas esperadas:

```text
email.verification
email.verification.retry
email.verification.dlq
password.reset
password.reset.retry
password.reset.dlq
```

Também é possível listar pelo terminal:

```powershell
docker exec individuum-rabbitmq rabbitmqctl list_queues name messages consumers --formatter table
```

## 13. Subir os consumers de e-mail

Somente faça isso depois de configurar SMTP válido ou aceitar que mensagens de teste irão para retry/DLQ:

```powershell
docker compose -f docker-compose.api_workers.yml up -d --build worker_email_verification worker_email_password_reset
```

Logs:

```powershell
docker compose -f docker-compose.api_workers.yml logs -f worker_email_verification worker_email_password_reset
```

Com SMTP fictício, o comportamento esperado é falha de envio e encaminhamento segundo a política de retry.
Para comprovar e-mail sem usar uma conta real, o projeto ainda precisa adicionar um serviço local como
Mailpit/MailHog e apontar `SMTP_HOST`/`SMTP_PORT` para ele.

## 14. Executar testes

Coleta:

```powershell
& $UvPath run pytest -p no:cacheprovider --collect-only -q
```

Teste focado do dispatcher/roteamento RabbitMQ:

```powershell
& $UvPath run pytest -p no:cacheprovider -q tests/unit/internal_events/infrastructure/messaging/test_rabbitmq_outbox_dispatcher.py
```

Resultado atual esperado para o teste focado:

```text
2 passed
```

Suíte completa:

```powershell
& $UvPath run pytest -p no:cacheprovider -q
```

Estado conhecido em 2026-08-30:

```text
2 passed, 7 errors
```

Os sete erros pertencem às fixtures antigas dos casos de uso Login/Logoff. Não esconda essas falhas nem
registre a suíte como aprovada.

## 15. Parar os serviços

Pare API/workers sem apagar dados:

```powershell
docker compose -f docker-compose.api_workers.yml down
```

Pare a infraestrutura sem apagar volumes:

```powershell
docker compose -f docker-compose.infra.yml down
```

Para iniciar novamente, repita os comandos `up -d`. Não acrescente `-v` a menos que deseje apagar os
bancos e os dados persistidos do RabbitMQ.

## 16. Diagnóstico rápido

### `uv` não é reconhecido

```powershell
$UvPath = Join-Path $env:USERPROFILE ".local\bin\uv.exe"
& $UvPath --version
```

### `run` não é reconhecido

`run` não é um executável isolado. Use:

```powershell
& $UvPath run alembic upgrade head
```

### Docker mostra Client, mas não Server

Abra o Docker Desktop, confirme o backend WSL 2 e aguarde o daemon iniciar.

### `relation alembic_version does not exist`

O banco ainda não recebeu migrations. Execute `alembic upgrade head` com `ENV=dev`.

### API/worker não encontra `postgres_dev` ou `rabbitmq`

Confirme que o Compose de infraestrutura foi iniciado primeiro e que a rede existe:

```powershell
docker network inspect individuum-net
```

### E-mail não chega

Verifique, nesta ordem:

1. registro na tabela `outbox`;
2. status/erro do evento;
3. mensagens e consumers no RabbitMQ;
4. logs do dispatcher;
5. logs do consumer;
6. credenciais/conectividade SMTP.

## 17. Leitura recomendada antes de modificar código

Leia integralmente, nesta ordem:

1. `reflecta_AGENTS.md`;
2. `reflecta_PROJECT_CONTEXT.md`;
3. `reflecta_IMPLEMENTATION_STATUS.md`.

Depois consulte este guia, código, migrations, testes e diagramas. Documentação planejada não prova que
uma funcionalidade esteja implementada; use código executável e testes como evidência do estado real.

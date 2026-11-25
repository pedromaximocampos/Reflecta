# Reflecta

![Status](https://img.shields.io/badge/status-functional%20academic%20MVP-2f4a38)
![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=111827)
![Architecture](https://img.shields.io/badge/architecture-modular%20monolith-4B5563)
![Backend unit tests](https://img.shields.io/badge/backend%20unit%20tests-626%20passing-brightgreen)
![Frontend tests](https://img.shields.io/badge/frontend%20tests-88%20passing-brightgreen)

Reflecta is a private, text-based journaling platform that uses structured AI analysis and a curated knowledge catalog to help people revisit their reflections, identify recurring themes, and connect them with philosophical and literary passages.

The system was developed as a Software Engineering capstone project. AI supports reflection and content association; it does not produce clinical diagnoses or replace professional care.

## Product overview

Reflecta combines:

- private journal entries with explicit ownership rules;
- structured, validated AI interpretation;
- human-curated themes, works, authors, and passages;
- explainable passage selection for each reflection;
- contextual history analyses across a selected period;
- cultural and philosophical work recommendations;
- controlled, revocable sharing with a professional;
- professional activities and guided reflections;
- private data export in JSON or ZIP;
- administrative ingestion, review, diagnostics, and reprocessing flows.

Private journal content remains in PostgreSQL. Neo4j stores the curated knowledge graph and does not act as storage for private journal entries.

## Implemented capabilities

### Identity and privacy

- sign-up, login, refresh rotation, logout, and automatic session restoration;
- email verification and password recovery;
- authenticated profile and avatar management;
- account deletion, deleted-account recovery, and session invalidation;
- `USER` and `ADMIN` authorization boundaries;
- user-scoped JSON and ZIP data export.

### Journal and analysis

- create, edit, list, retrieve, and logically delete reflections;
- one active entry per user and reflection date;
- calendar and 15-day navigation window for historical entries;
- structured analysis with sentences, canonical themes, sentiments, and conclusion;
- up to five ranked reflective themes and contextual passage snapshots;
- user curation of identified themes without exposing unrelated passages;
- bounded reanalysis and operational failure tracking;
- contextual history analysis with explicit entry selection and authorization.

### Catalog and AI ingestion

- administrative Theme CRUD with generated, non-repeated visual colors;
- work, author, cover, and PDF ingestion management;
- Amazon S3 document storage and SNS/SQS event delivery;
- resumable PDF processing with durable chunks and Inbox idempotency;
- strict OpenAI Responses API schemas;
- literal quote, page, offset, theme, and duplicate validation;
- passage confidence and reflective-value metadata;
- human approval, rejection, editing, activation, and catalog removal;
- controlled reprocessing of an existing ingestion without repeating completed chunks.

### Recommendations and sharing

- personalized thematic recommendations and exploratory works;
- recommendation details with cover, synopsis, author, and related themes;
- contextual-analysis sharing through revocable, expiring tokens;
- immutable journal snapshots selected by the owner;
- professional activities and guided reflections associated with a share;
- consolidated email notification for an activity assignment batch;
- user activity list, status filters, details, and completion.

### Administration and operations

- dashboards for themes, works, ingestions, passages, and operational failures;
- ingestion progress based on persisted chunk states;
- administrative failure details and bounded reprocessing;
- server-side passage filtering and pagination, short-lived invalidatable client caches, and consistent responsive navigation;
- aggregated user-dashboard reads, bounded database pools, request-duration diagnostics, and content-shaped loading feedback.

## Architecture

The backend is a **modular monolith**. Modules are deployed together while preserving application, domain, infrastructure, and presentation boundaries.

```text
Presentation / Infrastructure
            ↓
        Application
            ↓
           Domain
```

```text
src/
├── main/                    # FastAPI composition root
├── modules/
│   ├── auth/                # Identity, sessions, account lifecycle
│   ├── journal/             # Entries, analyses, history, snapshots
│   ├── catalog/             # Themes, works, authors, passages
│   ├── ai_processing/       # Journal analysis and PDF ingestion
│   ├── recommendation/      # Personalized and exploratory works
│   ├── sharing/             # Shares and professional activities
│   ├── data_export/         # Portable JSON and ZIP exports
│   ├── internal_events/     # Transactional Outbox and publishers
│   ├── notification/        # Email event handling and delivery
│   └── operations/          # Failure diagnostics and reprocessing
└── shared/                  # Cross-cutting contracts and adapters

frontend/
├── src/                     # React pages, components, and API clients
└── tests/                   # Frontend behavior and contract tests
```

### Work ingestion flow

```text
Admin uploads a PDF
  └── S3 + PostgreSQL ingestion + transactional Outbox
        └── SNS → SQS
              └── ingestion worker
                    ├── extract and normalize text
                    ├── persist resumable chunks
                    ├── request structured AI suggestions
                    ├── validate literal source evidence
                    └── persist passages in Neo4j for human review
```

### Journal analysis flow

```text
Journal entry
  └── submit for analysis
        └── journal-analysis worker
              ├── structured interpretation
              ├── canonical theme validation
              ├── contextual passage selection
              └── persisted conclusion and explainable associations
```

### Transactional event flow

```text
Business state + Outbox event
  └── one PostgreSQL transaction
        └── Outbox dispatcher → SNS → SQS/Lambda → SES
```

## Technology stack

| Area | Technologies |
|---|---|
| API | Python, FastAPI, Pydantic, Uvicorn |
| Relational and vector data | PostgreSQL, SQLAlchemy, Alembic, asyncpg, pgvector |
| Knowledge graph | Neo4j |
| Authentication | JWT, Argon2, HttpOnly refresh cookie |
| AI | OpenAI Responses API, strict JSON Schema, HTTPX |
| Documents and storage | pypdf, Amazon S3 |
| Messaging | Transactional Outbox, Amazon SNS, Amazon SQS, RabbitMQ |
| Notifications | AWS Lambda, Amazon SES, SMTP |
| Web application | React 19, Vite, React Router, Lucide |
| Infrastructure | Docker, Docker Compose, Terraform |
| Tests | pytest, pytest-asyncio, Node test runner, oxlint |

## Verified snapshot

Verified on **2026-11-25** from `main`:

- 55 OpenAPI paths and 74 HTTP operations;
- 21 Alembic migrations with head `f13a4c600006`;
- 626 backend unit tests passing;
- 88 frontend tests passing;
- frontend lint and production build passing;
- local PostgreSQL, Neo4j, RabbitMQ, API, and worker definitions in Docker Compose;
- Terraform configuration for the SNS/SQS/DLQ messaging slice and the AWS demo stack.

Cloud-backed flows were exercised with S3, SNS, SQS, OpenAI, Neo4j, and SES. The public demonstration environment uses CloudFront, private S3 buckets, EC2/EBS, ECR, RDS PostgreSQL, Secrets Manager, and CloudWatch; delivery is still a reviewed manual operation rather than a CI/CD pipeline.

## Running locally

### Prerequisites

- Python 3.12 or newer;
- [uv](https://docs.astral.sh/uv/);
- Node.js and npm;
- Docker Desktop with Docker Compose;
- Git.

### Backend dependencies

```bash
uv sync --locked
```

Create local environment files from the provided examples. Never commit AWS credentials, provider keys, SMTP passwords, JWT secrets, or production connection strings.

### Infrastructure, API, and workers

```powershell
docker compose -f docker-compose.infra.yml -f docker-compose.api_workers.yml --profile ai up -d --build
```

Apply migrations when the database schema has not been updated:

```powershell
$env:ENV = "dev"
uv run alembic upgrade head
```

Main local endpoints:

- API: `http://localhost:8000`;
- Swagger UI: `http://localhost:8000/docs`;
- ReDoc: `http://localhost:8000/redoc`;
- Neo4j Browser: `http://localhost:7474`;
- RabbitMQ Management: `http://localhost:15672`.

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

The web application is normally available at `http://localhost:5173`.

### Stop the environment

```powershell
docker compose -f docker-compose.infra.yml -f docker-compose.api_workers.yml --profile ai stop
```

This preserves the local database volumes.

## Tests

```bash
uv run pytest tests/unit -q
```

```bash
cd frontend
npm test -- --run
npm run lint
npm run build
```

Integration tests require the corresponding PostgreSQL/Neo4j infrastructure and environment configuration. The academic evidence and execution matrix are available in [`docs/tcc/evidencias`](docs/tcc/evidencias/).

## Infrastructure as Code and deployment

[`infra/terraform`](infra/terraform/) contains the messaging slice for SNS/SQS/DLQs and an independent AWS demonstration stack. Existing messaging resources must be imported and compared with a reviewed plan before Terraform becomes their source of truth.

The demonstration stack provisions networking, RDS, EC2/EBS, ECR, S3, CloudFront, Secrets Manager, CloudWatch, IAM, and a budget. The application image and frontend assets are deployed through reviewed manual commands. A hardened production platform still needs, at minimum:

- CI/CD with automatic tests, migrations, health checks, and rollback controls;
- a managed or highly available Neo4j strategy and Multi-AZ database policy;
- custom DNS, formal backup/restore drills, tracing, alarms, and security testing;
- complete adoption of the pre-existing messaging and notification resources into reviewed state.

## Documentation

Start with the [documentation index](docs/README.md). It links the final TCC document, architecture diagrams, user stories, operational guides, traceability matrix, and test evidence.

Useful technical references:

- [real implementation status](reflecta_IMPLEMENTATION_STATUS.md);
- [project context](reflecta_PROJECT_CONTEXT.md);
- [development environment guide](docs/GUIA_AMBIENTE_DESENVOLVIMENTO.md);
- [backend operations](docs/BACKEND_OPERATIONS.md);
- [Terraform messaging guide](infra/terraform/README.md).

## Security and production boundaries

Reflecta processes sensitive personal text. Production use requires reviewed encryption, retention, auditability, secrets management, provider privacy policies, observability, backup/restore procedures, penetration testing, and incident response.

The repository demonstrates a functional academic MVP; it should not be presented as a clinically validated or production-hardened healthcare system.

## License

This public portfolio repository does not currently grant an open-source license. All rights are reserved unless explicitly stated otherwise.

## Academic context

Reflecta was developed by **Pedro Máximo Campos do Carmo** and **Augusto Noronha Leite** as a Software Engineering capstone project at PUC Minas. This repository is maintained by [Pedro Maximo Campos](https://github.com/pedromaximocampos) as a public portfolio version of the project.

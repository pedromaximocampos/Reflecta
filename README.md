# Reflecta

![Status](https://img.shields.io/badge/status-in%20development-orange)
![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![Architecture](https://img.shields.io/badge/architecture-modular%20monolith-4B5563)
![Tests](https://img.shields.io/badge/tests-287%20passing-brightgreen)

> **Work in progress:** Reflecta is actively being developed as a Software Engineering capstone project. The repository already contains working vertical slices, but it is not yet a production-ready application.

Reflecta is a private, text-based journaling platform designed to help people understand recurring themes in their reflections and connect them with curated philosophical, literary, and cultural knowledge.

The long-term product combines private journaling, structured AI-assisted interpretation, a curated knowledge graph, personalized recommendations, and controlled sharing with healthcare professionals. AI is intended to support reflection—not diagnose users or replace professional care.

## Why this project exists

Journaling can produce valuable personal insights, but isolated entries are often difficult to revisit and connect over time. Reflecta explores how software architecture, semantic processing, and curated knowledge can turn those entries into structured and explainable reflection paths while preserving privacy and user ownership.

This project is also a practical study of:

- modular monolith design;
- Clean Architecture and Domain-Driven Design;
- transactional consistency and the Outbox Pattern;
- asynchronous event processing on AWS;
- relational, vector, and graph persistence;
- authentication, authorization, ownership, and privacy boundaries;
- testable application design with explicit ports and adapters.

## Current implementation

### Authentication and account lifecycle

- sign-up, login, logout, and token refresh;
- password hashing with Argon2 and JWT-based authentication;
- email verification and password reset flows;
- `USER` and `ADMIN` roles with route guards;
- authenticated profile updates;
- soft account deletion by confirmation token;
- deleted-account recovery;
- session invalidation and transactional event creation.

### Journal

- authenticated journal entry creation;
- entry listing and retrieval with ownership enforcement;
- draft editing and logical deletion;
- PostgreSQL `journal_schema` with tables prepared for analyses, sentences, themes, passages, and embeddings;
- pgvector extension and vector columns prepared for the future semantic pipeline.

Journal entries are text-only in the current scope. Audio and image journaling are intentionally excluded from the MVP.

### Catalog and knowledge graph

- administrator-protected Theme CRUD;
- deterministic, unique, and stable slugs;
- work and author creation in Neo4j;
- PDF ingestion requests backed by PostgreSQL and Amazon S3;
- AI-suggested passage persistence and human review workflows;
- passage editing, approval, rejection, activation, and deactivation;
- Neo4j repositories and Unit of Work abstractions;
- constraints and transaction handling for graph persistence;
- separation between the Catalog module and consumers of catalog knowledge.

### AI processing

- PDF text extraction, Unicode normalization, and boundary-aware chunking;
- durable per-chunk processing state in PostgreSQL;
- Inbox Pattern for idempotent SQS event consumption;
- SQS visibility and processing-lease heartbeats;
- structured OpenAI Responses API output validated against active catalog themes;
- literal quote, page, offset, and theme validation before graph persistence;
- retryable chunk processing without repeating successfully completed chunks;
- journal analysis submission, worker execution, and structured result persistence.

### Events and notifications

- transactional Outbox persistence in PostgreSQL;
- event routing and retry-aware dispatching;
- Amazon SNS publishing;
- SNS-to-SQS delivery architecture;
- AWS Lambda batch consumer with partial batch failure responses;
- Amazon SES and SMTP notification adapters;
- email templates for verification, password reset, account deletion, and account recovery;
- local RabbitMQ infrastructure retained as a development path while the AWS flow evolves.

## Architecture

Reflecta is implemented as a **modular monolith**. Modules are deployed as one backend but maintain explicit business and dependency boundaries.

```text
Presentation / Infrastructure
            ↓
        Application
            ↓
           Domain
```

The domain does not depend on FastAPI, SQLAlchemy, Neo4j, AWS SDKs, or messaging implementations. Infrastructure implements ports defined by inner layers, while bootstrap modules compose concrete dependencies.

```text
src/
├── main/                    # FastAPI application entry point
├── modules/
│   ├── auth/                # Identity, sessions, roles, and account lifecycle
│   ├── journal/             # Private text entries and analysis data
│   ├── catalog/             # Curated themes, works, authors, and passages
│   ├── ai_processing/       # Journal interpretation and work ingestion
│   ├── internal_events/     # Outbox, routing, and publishers
│   └── notification/        # Event handlers and email delivery
└── shared/                  # Cross-cutting contracts and infrastructure
```

Recommendation and Sharing / Professional remain planned modules without complete implementations.

## Main processing flows

### Transactional event delivery

```text
Use case
  └── business state + Outbox event committed together in PostgreSQL
        └── Outbox dispatcher
              └── Amazon SNS
                    └── Amazon SQS
                          └── AWS Lambda
                                └── Amazon SES
```

### Work ingestion and passage curation

```text
Admin uploads a PDF
  └── Amazon S3 + PostgreSQL ingestion + Outbox event
        └── Amazon SNS → Amazon SQS
              └── AI Processing worker
                    ├── PDF extraction and normalized text
                    ├── resumable chunks and Inbox idempotency
                    ├── OpenAI structured passage suggestions
                    └── Neo4j passages pending human review
```

### Journal analysis

```text
Journal draft
  └── submit for analysis
        └── AI Processing worker
              ├── structured OpenAI analysis
              ├── validation against active catalog themes
              └── persisted analysis and entry state transition
```

Journal submission and structured analysis are implemented as an initial vertical slice. Sentence-level processing, embeddings, and contextual passage matching remain future increments.

## Technology stack

| Area | Technologies |
|---|---|
| API | Python, FastAPI, Pydantic, Uvicorn |
| Dependency management | uv |
| Relational persistence | PostgreSQL, SQLAlchemy, Alembic, asyncpg |
| Vector persistence | pgvector |
| Knowledge graph | Neo4j |
| Authentication | JWT, Argon2 |
| Async messaging | Transactional Outbox, Amazon SNS, Amazon SQS, RabbitMQ |
| AI | OpenAI Responses API, strict JSON Schema validation, HTTPX |
| Document processing | pypdf, normalized text, boundary-aware chunking |
| Object storage | Amazon S3 |
| Notifications | AWS Lambda, Amazon SES, SMTP |
| Infrastructure | Docker, Docker Compose |
| Testing | pytest, pytest-asyncio |

## API surface

The current API exposes 25 paths and 37 HTTP operations across three public modules:

- `/auth`: authentication, verification, password reset, profile, deletion, and recovery;
- `/journal/entries`: authenticated Journal CRUD plus analysis submission and retrieval;
- `/catalog/themes`: administrator-protected Theme CRUD;
- `/catalog/works`: work creation and PDF ingestion;
- `/catalog/passages`: passage listing, editing, review, and availability management.

After starting the API, the generated documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Running locally

### Prerequisites

- Python 3.12 or newer;
- [uv](https://docs.astral.sh/uv/);
- Docker Desktop with Docker Compose;
- Git.

### 1. Install the dependencies

```bash
uv sync --locked
```

The recommended interpreter for IDE configuration is:

```text
.venv/Scripts/python.exe   # Windows
.venv/bin/python           # Linux/macOS
```

### 2. Configure the environment

Create a local `.env.dev` file. It is intentionally excluded from version control because it contains credentials and environment-specific resource identifiers.

The required settings are declared in [`src/shared/config/settings.py`](src/shared/config/settings.py). They cover PostgreSQL, Neo4j, JWT, RabbitMQ, SMTP, SNS, and SQS.

Never commit real AWS credentials, SMTP passwords, JWT secrets, or production connection strings.

### 3. Start the local infrastructure

```bash
docker compose -f docker-compose.infra.yml up -d
```

Default local services:

- PostgreSQL development database: `localhost:5432`;
- PostgreSQL test database: `localhost:5433`;
- Neo4j Browser: `http://localhost:7474`;
- Neo4j Bolt: `localhost:7687`;
- RabbitMQ Management: `http://localhost:15672`.

### 4. Apply the migrations

PowerShell:

```powershell
$env:ENV = "dev"
uv run alembic upgrade head
```

Linux/macOS:

```bash
ENV=dev uv run alembic upgrade head
```

### 5. Start the API

```bash
uv run uvicorn src.main.server.fast_api.run:app --reload
```

The API will be available at `http://localhost:8000`.

### Optional: run the containerized API and workers

Start the infrastructure first, then run:

```bash
docker compose -f docker-compose.api_workers.yml up --build
```

AWS-backed workers require valid IAM permissions and configured SNS, SQS, Lambda, and SES resources.

To include the AI workers declared under the Compose profile:

```bash
docker compose -f docker-compose.api_workers.yml --profile ai up --build
```

## Tests

Run the complete suite with:

```bash
uv run pytest -q
```

Current verified result:

```text
287 passed
```

The suite covers domain rules, application use cases, authentication, account lifecycle, notification handlers, Catalog/Neo4j behavior, Journal persistence, S3 adapters, Inbox idempotency, SQS consumption, PDF chunking, OpenAI contracts, controllers, and validation.

The repository still needs broader automated integration, API, and end-to-end coverage.

## Development status and roadmap

### Implemented or available as a working vertical slice

- Auth and account lifecycle;
- administrator authorization for Catalog operations;
- Theme CRUD backed by Neo4j;
- work and author creation backed by Neo4j;
- PDF upload and ingestion state backed by S3 and PostgreSQL;
- resumable AI processing with durable chunks and Inbox idempotency;
- passage suggestion, explanation, review, and lifecycle management;
- Journal draft CRUD backed by PostgreSQL;
- initial structured Journal analysis pipeline;
- Outbox persistence and event dispatch infrastructure;
- email event handling and AWS/local notification adapters;
- Docker-based PostgreSQL, Neo4j, and RabbitMQ infrastructure.

### In progress or planned

- embeddings generation and similarity search;
- sentence-level Journal processing and contextual passage matching;
- work listing/editing and ingestion-status API endpoints;
- recommendation generation;
- controlled sharing with healthcare professionals;
- generalized consumer idempotency outside the AI ingestion Inbox;
- operational monitoring and failure recovery;
- frontend application;
- CI/CD and production deployment.

## Engineering considerations

Reflecta processes highly sensitive personal content. Production readiness requires additional work around encryption, retention, auditability, secrets management, observability, provider privacy policies, and security testing.

The project deliberately keeps private journal text in PostgreSQL. Neo4j stores curated knowledge and must not become a storage location for private journal entries.

## Documentation

The [`docs`](docs/) directory contains architecture diagrams, use cases, the data glossary, development setup guidance, and academic project material.

The project context and implementation status documents distinguish planned behavior from code that is already implemented. Documentation is not treated as evidence of implementation without matching code, migrations, or tests.

## Academic and portfolio context

Reflecta is being developed as a Software Engineering capstone project and as a portfolio demonstration of backend architecture and cloud integration. The repository shows the evolution of a real system, including architectural trade-offs, incomplete modules, technical debt, and incremental vertical delivery.

## License

This repository does not currently publish an open-source license. All rights are reserved unless stated otherwise.

---

Developed by [Pedro Maximo Campos](https://github.com/pedromaximocampos).

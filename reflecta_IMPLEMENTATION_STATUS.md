# Reflecta — verified implementation status

> Updated on 2026-11-25 after performance verification and preparation of the AWS demonstration release.
>
> This document records capabilities supported by code, migrations, tests, or documented executions. Product plans alone are not treated as implementation evidence.

## Verification snapshot

- Backend source synchronized from `Codigo/BACK` into the repository root.
- Frontend source synchronized from `Codigo/FRONT` into `frontend/`.
- 55 OpenAPI paths and 74 HTTP operations generated.
- 21 Alembic migration files; current head: `f13a4c600006`.
- 626 backend unit tests passing.
- 88 frontend tests passing.
- Frontend lint and production build passing.
- Academic documentation and evidence synchronized into `docs/tcc/`.
- One portfolio portability adjustment keeps an environment-path test independent of the physical repository directory name.

## Status legend

- `IMPLEMENTED`: working code and automated or documented verification exist.
- `PARTIAL`: a useful vertical slice exists, but production or broader verification work remains.
- `PLANNED`: no complete working slice has been verified.

## Executive status

| Area | Status | Verified scope |
|---|---|---|
| Backend/API | IMPLEMENTED | FastAPI exposes Auth, Journal, Catalog, AI Processing, Recommendation, Sharing, Data Export, and Operations routes. |
| Modular monolith | IMPLEMENTED | Modules have explicit application/domain/infrastructure/presentation areas and a shared composition root. |
| Authentication | IMPLEMENTED | Sign-up, login, refresh, logout, verification, reset, profile, avatar, deletion, recovery, and roles. |
| Journal | IMPLEMENTED | Dated entries, CRUD, ownership, calendar/window navigation, individual analysis, contextual analysis, and history. |
| AI Processing | PARTIAL | Structured journal analysis and resumable PDF ingestion work; provider/cloud E2E remains environment-dependent. |
| Catalog / Knowledge | IMPLEMENTED | Themes, works, authors, covers, ingestions, passages, review, lifecycle, and Neo4j relationships. |
| Recommendation | IMPLEMENTED | Personalized thematic works, exploratory works, and detail presentation. |
| Sharing / Professional | IMPLEMENTED | Expiring/revocable shares, selected journal snapshots, professional activities, and user completion flow. |
| Data Export | IMPLEMENTED | Authenticated, user-scoped JSON and ZIP exports. |
| Notifications | PARTIAL | SMTP/SES adapters, event handler, Lambda/SQS consumer, and activity email template exist; production IaC is incomplete. |
| Internal Events | PARTIAL | Transactional Outbox, SNS/SQS publishing, RabbitMQ development path, retry, and DLQ behavior exist. |
| Operations | IMPLEMENTED | Failure listing/details plus bounded administrative and ingestion reprocessing flows. |
| Frontend | IMPLEMENTED | React user and administrator areas cover the verified product flows. |
| Terraform | PARTIAL | Messaging plus the AWS demo network, RDS, EC2/EBS, ECR, S3, CloudFront, IAM, secrets, logs, and budget are versioned; some pre-existing resources remain outside this state. |
| CI/CD | PLANNED | No complete production delivery pipeline is currently verified. |

## Current modules

```text
src/modules/
├── auth
├── journal
├── catalog
├── ai_processing
├── recommendation
├── sharing
├── data_export
├── notification
├── internal_events
└── operations
```

The dominant dependency direction for recent flows is:

```text
Presentation / Infrastructure → Application → Domain
```

Some legacy areas still contain architectural debt and should not be described as perfectly isolated DDD modules.

## Persistence

### PostgreSQL and pgvector

PostgreSQL is the transactional source of truth for:

- users, sessions, account lifecycle, and Outbox events;
- private journal entries and analyses;
- contextual-analysis metadata and sharing;
- professional activities;
- work-ingestion state, durable chunks, Inbox events, and failures.

The schema supports vector columns, but vector similarity is not the primary passage-selection mechanism in the current MVP.

### Neo4j

Neo4j stores curated knowledge:

- `Theme`, `Work`, `Author`, and `Passage` nodes;
- `WRITTEN_BY`, `BELONGS_TO`, and `RELATES_TO` relationships;
- passage source, location, explanation, confidence, reflective value, and lifecycle status.

Private journal text is not stored in Neo4j.

### Amazon S3

S3 adapters support work PDFs, normalized ingestion artifacts, work covers, and user avatars. Local execution requires valid AWS credentials and configured bucket names.

## Main asynchronous flows

### Work ingestion

1. Catalog persists the ingestion and Outbox event.
2. The dispatcher publishes through SNS/SQS.
3. AI Processing claims the event through an Inbox lease.
4. The PDF is extracted into durable chunks.
5. Successfully completed chunks are not repeated on redelivery.
6. AI suggestions are validated against literal source evidence and active canonical themes.
7. Valid passages are stored in Neo4j as pending review.
8. Administrators approve, reject, edit allowed fields, or remove passages from the catalog.

### Journal analysis

1. The user submits a journal entry for analysis.
2. The worker selects an unprocessed entry and calls the configured provider.
3. Structured output is validated against active canonical themes.
4. Up to five reflective themes are ranked.
5. Approved catalog passages are selected and stored as an explainable snapshot.
6. The user can curate effective themes and request bounded reanalysis.

### Sharing and professional activities

1. The owner creates an expiring share for a contextual analysis.
2. Only explicitly selected journal snapshots are included.
3. A professional resolves the token without receiving owner credentials.
4. The professional can assign multiple activities or guided reflections in one batch.
5. The user receives the assignment, lists activities, opens details, and marks items complete.

## Known production gaps

- Delivery remains manual; CI/CD and automatic rollback are not implemented.
- PostgreSQL is managed by RDS, while the demonstration Neo4j Community node remains single-instance on encrypted EBS.
- CloudFront provides TLS and hosting, but custom DNS and a formal high-availability strategy remain future work.
- CloudWatch logs and per-request duration diagnostics exist; distributed tracing and actionable alarms remain incomplete.
- Backup/restore, retention, incident response, and security testing need formal verification.
- Pydantic deprecation warnings remain technical debt.
- Cloud/provider integration tests are intentionally environment-dependent.

## Evidence and navigation

- [Repository README](README.md)
- [Documentation index](docs/README.md)
- [Final TCC report](docs/tcc/TCC-Reflecta-FINAL.pdf)
- [Use-case traceability](docs/tcc/rastreabilidade-casos-de-uso.md)
- [Evidence matrix](docs/tcc/evidencias/matriz-evidencias.md)
- [Terraform messaging guide](infra/terraform/README.md)

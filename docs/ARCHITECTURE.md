# CODO Target Architecture

## Client
Flutter mobile app. Web responsive and PWA are separate delivery targets from the same product design system.

## Core path
UI -> CODO API -> legal orchestrator -> hybrid search -> version resolver -> verified corpus -> citation verifier -> answer renderer.

## Services
- identity-service
- legal-corpus-service
- legal-search-service
- legal-versioning-service
- procedure-service
- jurisprudence-service
- institution-service
- ai-orchestrator
- citation-verifier
- ingestion-service
- notification-service
- audit-service
- admin-service

## Non-negotiable behavior
1. Official text is distinct from CODO explanation.
2. Every answer exposes source, text, number, article, version, date and status when available.
3. A draft or bill is never rendered as applicable law.
4. Historical and repealed provisions remain traceable.
5. AI does not answer from model memory when verified retrieval is insufficient.
6. Administrative changes are audited.
7. User-sensitive data is separated from the legal corpus.

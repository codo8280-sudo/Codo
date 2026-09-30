# CODO - Increment 04 Summary

Date: 29 September 2026

## Objective

Turn the Increment 03 ingestion skeleton into a controlled first-corpus workflow in which a legal PDF can be acquired, hashed, extracted, drafted, reviewed, legally classified, quality-checked, published and indexed without allowing automatic publication or silent legal assumptions.

## Main changes

### 1. Extraction and review draft

Added `ExtractionService` and conservative `LegalTextParser` support for:

- PDF text extraction through `pypdf`;
- page trace markers in extraction artifacts;
- removal of page markers from legal text;
- `Article premier` and numeric articles;
- suffixes such as bis / ter / quater / quinquies;
- duplicate and numbering-gap diagnostics;
- generated CODO article identifiers;
- mandatory `verification_pending` draft status.

### 2. Workflow correction

Fixed the Increment 03 state mismatch: a job extracted to `to_analyze` can now be structured. The previous implementation only accepted `imported` even though extraction correctly advanced the workflow.

### 3. Provenance model

Migration `005_first_corpus_and_provenance.sql` adds:

- Presidency source registry entry;
- initial launch legal domains;
- `legal_version_sources` for explicit version-to-snapshot provenance;
- `source_registry_checks` for repeated institutional-source observations.

Acquisition now writes an `original` artifact and detects whether the source is new, changed or unchanged.

### 4. Legal decision gate

New endpoint:

`POST /v1/admin/ingestion/{jobId}/legal-decision`

A human validator must assign a final legal status to the document and articles during `legal_review`. `verification_pending` cannot be submitted as a final decision.

### 5. Quality gate

New endpoint:

`GET /v1/admin/ingestion/{jobId}/quality`

It checks original preservation, source verification, provenance/hash match, article structuring, legal statuses, metadata and control artifacts. The report returns `can_validate` and `can_publish`.

### 6. Publication and indexing

Publication now requires:

- verified source provenance;
- no `verification_pending` status;
- recorded human validation.

Lexical chunks are rebuilt in the same publication transaction so a newly published article is immediately searchable without a separate manual chunking step.

### 7. Public provenance

New endpoint:

`GET /v1/documents/{codoId}/provenance`

It exposes the snapshot URL, final URL, capture date, SHA-256, trust level and provenance role of a published version. Flutter's article screen can display this evidence.

### 8. First corpus bootstrap

Prepared:

- `backend/manifests/ci_constitution_2016_consolidated_2023.json`;
- `backend/scripts/bootstrap_first_corpus.py`;
- `docs/FIRST_CORPUS_BOOTSTRAP.md`.

The script intentionally stops after acquisition, extraction and draft generation. It cannot structure, validate or publish by itself.

## Official constitutional references prepared

The candidate manifest identifies the Presidency consolidated Constitution PDF and institutional verification references from the Constitutional Council. The build environment did not successfully download the Presidency PDF binary. CODO therefore did not substitute a secondary copy or manufacture a first corpus. The actual staging environment must acquire the official bytes and calculate its own hash.

## Tests and checks

- 20 Python tests: PASS.
- Python compile: PASS.
- FastAPI root / health: PASS.
- database guard without configuration: PASS.
- OpenAPI 3.1: PASS, 16 paths.
- manifest JSON: PASS.
- 54 Dart files: relative imports PASS.
- Flutter SDK: not available here.
- PostgreSQL server: not available here.

## Next increment

Increment 05 should run this pipeline against a staging database and actual official source network, then implement:

- PostgreSQL integration tests;
- first real source snapshot and extraction report;
- amendment/source linking for 2020 and 2023;
- admin OIDC/role authorization;
- legal validation UI backed by authenticated API actions;
- initial published Constitution corpus only after human legal review;
- observability and ingestion monitoring.

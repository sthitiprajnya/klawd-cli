# Rust Worker Contracts (Internal)

## 1) Provider Probe Worker
- Transport: HTTP (`POST /v1/probe/providers`) and gRPC (`providerprobe.v1.ProviderProbe/ProbeProviders`).
- Request:
  - `model_pool: string`
  - `providers: [{ api_key: string }]`
- Response:
  - `providers: [{ api_key: string, available: bool, latency_ms: int, reason: string|null }]`
- Semantics:
  - timeout budget: 1500ms per request (fail-open in Python)
  - retry: 1 immediate retry on transport errors only
  - deterministic errors: `INVALID_ARGUMENT`/HTTP 422 for schema violations.

## 2) Skill Ingest/Validation Worker
- Transport: HTTP (`POST /v1/skills/ingest`) and gRPC (`skillingest.v1.SkillIngest/Ingest`).
- Request:
  - `path: string`
  - `content: string`
  - `sha256: string`
- Response:
  - `accepted: bool`
  - `normalized_skill_id: string`
  - `errors: [string]`
- Semantics:
  - atomicity: write to temp file and rename into final location only after full validation.
  - timeout budget: 2000ms.

## 3) Event Normalization Worker
- Transport: HTTP (`POST /v1/events/normalize`) and gRPC (`eventnorm.v1.EventNorm/NormalizeBatch`).
- Request:
  - `events: [object]`
  - `schema_version: string`
- Response:
  - `events: [object]`
  - `dropped_count: int`
  - `errors: [{index: int, code: string}]`
- Semantics:
  - high-throughput batched normalization; deterministic error code mapping.
  - timeout budget: 1000ms.

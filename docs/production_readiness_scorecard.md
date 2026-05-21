# Production Readiness Scorecard (0–5)

This scorecard is based on the implementation gaps identified in the architecture review discussion.

## Category Scores

| Category | Score (0–5) | Why |
|---|---:|---|
| Safety | 3.5 | Good baseline controls (PRISM hooks, path restrictions, allowlist model), but no unified threat telemetry for live prompt filtering and no deterministic escalation path after repeated self-heal failures. |
| Reliability | 2.5 | System survives via restart policies, but restart thrashing risk, passive provider recovery, and no dead-letter queue reduce operational stability. |
| Learning Quality | 2.0 | Memory write path exists, but duplicate outcome risk and possible semantic dedup false positives can degrade long-term memory quality. |
| Self-modification Governance | 2.0 | Autonomous edits are possible with some checks, but provenance is incomplete (no canonical diff/model version/rollback pointer persisted). |
| Observability | 3.0 | Good traces/metrics foundation, but fragmented security signal logging and weak change lineage limit incident forensics. |
| Cost Control | 3.0 | Token tracking and router-level controls exist, but repeated self-heal loops and instability patterns can cause avoidable spend. |

**Overall weighted readiness: 2.7 / 5.0**

---

## Prioritized Fix-Next-10

Priority is ordered by risk reduction and implementation leverage.

1. **Add deterministic idempotency for `store_outcome`**
   - Introduce a stable key (e.g., `job_id + iteration + stage + artifact_hash`) and upsert semantics.
   - Goal: stop duplicate memory poisoning from retries.

2. **Implement dead-letter + human escalation for repeated LOGIC failures**
   - After N failed self-heal attempts, route to dead-letter queue and emit urgent operator notification.
   - Goal: prevent unbounded retry loops and silent task starvation.

3. **Harden `dedup.py` with a second-pass symbolic guard**
   - Keep embedding similarity as first pass; require AST/symbol/dependency signature confirmation before MERGE.
   - Goal: reduce false positive skill merges.

4. **Persist autonomous change provenance as first-class audit data**
   - Record unified diff, model/provider/version, prompt hash, reviewer verdict, and rollback pointer.
   - Goal: make every self-edit explainable and reversible.

5. **Unify PRISM + immunization telemetry schema**
   - Consolidate regex evidence and LLM threat confidence into one event stream keyed by `job_id`.
   - Goal: enable false-positive tuning and incident analytics.

6. **Introduce restart backoff/jitter and crash-loop circuit breaker**
   - Apply exponential backoff and maximum restart burst policy (systemd and container layer).
   - Goal: stop 10-second infinite thrash loops.

7. **Add active provider recovery probes to ThreadParker**
   - Probe degraded providers on cadence; reinstate only after a successful health trial.
   - Goal: avoid blind re-routing after passive TTL expiry.

8. **Make skill hot-reload atomic-safe**
   - Parse only after atomic rename into place (temp-write + fsync + rename) or debounce until stable file hash.
   - Goal: eliminate partial-read YAML parse failures.

9. **Add held-out evaluation dataset governance contract**
   - Require immutable dataset version IDs and contamination checks in `evaluate_candidate` caller contract.
   - Goal: protect prompt promotion integrity.

10. **Create control-plane SLOs for autonomous loop behavior**
   - Track queue depth, retry fan-out, degraded-provider rate, self-heal success, and crash-loop rate.
   - Goal: operational guardrails for 24/7 autonomous reliability.

---

## 14-Day Execution Plan (Optional)

- **Days 1–3:** Fixes #1, #2, #6 (highest safety/reliability impact).
- **Days 4–7:** Fixes #3, #4, #5 (governance and forensic quality).
- **Days 8–10:** Fixes #7, #8 (stability hardening).
- **Days 11–14:** Fixes #9, #10 and baseline SLO dashboard/alerts.

Expected result after this wave: **~3.6–3.9 / 5** readiness if implemented cleanly and regression-tested.

# NEM Forecast Observatory — Build Plan

**What we're building:** AEMO publishes a 5-minute-ahead price forecast (P5MIN) with no
uncertainty quantification. We post-process it into calibrated predictive distributions
using current probabilistic-EPF methods, score ourselves against AEMO continuously in
public, quantify the value in battery dollars, and expose a grounded LLM analyst over
the whole system.

**The claim we're building toward:** *"AEMO's P5MIN provides no uncertainty
quantification. I built calibrated predictive distributions on top of it, passing
coverage tests under drift via online conformal recalibration, and demonstrated
$X/MW/year in additional battery revenue versus point-forecast dispatch — significant at
p < 0.01 by Diebold–Mariano."*

---

## All phases

| Phase | When | Output |
|---|---|---|
| **0 — Setup** | 30 min | Repo, accounts, archive download running in background |
| **1 — Data foundation** | Day 1 (~10h) | Bitemporal store, ingestion, `features_asof`, leakage test in CI |
| **2 — Baseline & error decomposition** | Day 2 AM | P5MIN error reproduced and decomposed by regime — the finding |
| **3 — Distributional layer** | Day 2 PM | QRA + conformal + IDR ensemble, LightGBM quantile, online recalibration |
| **4 — Evaluation & economics** | Day 2 eve / Day 3 AM | CRPS, pinball, PIT, coverage tests, Diebold–Mariano, battery simulator |
| **5 — AI layer** | Day 3 AM/PM | Notice extraction + gold set + ablation, agent tools, as-of retrieval, eval harness |
| **6 — Ship** | Day 3 PM | Frontend, live scoring loop, deploy, README, write-up |

**Never cut, at any point:** bitemporal store · leakage test · walk-forward validation ·
proper scoring rules · Diebold–Mariano significance testing · live public scoreboard ·
dollar translation · LLM gold set.

**MVP scope decisions:** VIC1 only for modelling (ingest all regions). 12 months of
history. One horizon (30-min ahead). No unit-level `DISPATCHLOAD` in Phase 1 — it's 40M+
rows and we don't need it yet. Bid-stack reconstruction is a Phase 2 stretch goal.

---

# PHASE 1 — Data Foundation

**Objective:** a bitemporal store of NEM market data where lookahead leakage is
structurally impossible, backfilled 12 months, ingesting live.

**Definition of done:**
1. `docker compose up` works from clean checkout
2. 12 months backfilled across all Phase 1 reports, resumable, no duplicates
3. Celery Beat ingesting live and staying current
4. `features_asof(interval, asof_ts)` returns a provenance-tagged bundle
5. Leakage test over ≥1000 sampled pairs passing in CI and blocking merges
6. `nemobs verify` produces an honest coverage report

**Reports for Phase 1:**
`DISPATCHPRICE` (truth) · `P5MIN` (baseline) · `DISPATCHREGIONSUM` (demand) ·
`ROOFTOP_PV_ACTUAL` + `ROOFTOP_PV_FORECAST` · `DISPATCHCONSTRAINT` ·
`MARKETNOTICE` (Phase 5 input, ingest now)

---

## Domain facts you must encode correctly

Get any of these wrong and everything downstream is silently broken.

**NEM time is UTC+10 fixed, year-round, no daylight saving.** Not Melbourne local time.
Pick one representation, write it in `DECISIONS.md`, never deviate. Recommendation: store
everything as timezone-aware UTC, convert at the edges, and name every column so the
convention is unambiguous.

**Timestamps are interval-ENDING.** An interval labelled `14:05` covers 14:00–14:05.

**`INTERVENTION` flag on `DISPATCHPRICE`.** When AEMO intervenes in the market (e.g.
issues a direction), *two* price runs are published for the same interval — the
intervention case and the "what price would have been" case. If you ignore this you get
duplicate rows and wrong labels. Decide which you're using (normally `INTERVENTION = 0`
for the pricing run), document it, and assert uniqueness after filtering.

**Price bounds.** Market floor is −$1,000/MWh; the cap is indexed annually — look up the
current value rather than hardcoding from memory. Use these for range assertions and,
later, for censored modelling.

**`RUN_DATETIME` ≠ publication time.** For `P5MIN`, `RUN_DATETIME` is what the run was
*for*; the file appears on NEMWeb some seconds-to-minutes later. **Measure this lag
empirically** across a sample of files and apply a conservative buffer. When in doubt,
assume data was available *later* than you think — erring late is safe, erring early is
leakage.

---

## Phase 1 sessions

Six sessions. Review between each. Commit as you go.

---

### Session 1.0 — Setup and background download (30 min)

Do this first; the download runs while you build everything else.

> Create a new repo `nem-observatory`. Read `BUILD_PLAN.md` for context.
>
> Before any application code, I need the historical archive downloading in the
> background, because it's the long pole.
>
> 1. Verify the current AEMO MMSDM Data Archive URL structure by actually browsing
>    `http://nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/` — do not assume the
>    path from memory. Report the real directory pattern, file naming, and per-month size
>    for the reports listed in `BUILD_PLAN.md` Phase 1.
> 2. Write a standalone `scripts/bulk_download.py` — no framework, no DB, just: fetch the
>    last 12 months of monthly archives for those reports to `./data/raw/`, resumable,
>    skip files already present with matching size, exponential backoff, progress
>    logging to a file. Polite: sane user agent, modest concurrency (3–4), jittered.
> 3. Start it in a detached process (`nohup`/`tmux`) and show me how to check progress.
>
> This script is deliberately throwaway and separate from the real ingestion pipeline.
> Don't over-engineer it.

Commit: `chore: initialise repo` · `feat: bulk archive downloader`

---

### Session 1.1 — Reconnaissance (45 min)

> **No application code.** Establishing ground truth about the data.
>
> 1. Verify current APIs of `NEMOSIS` and `NEMSEER` (UNSW-CEEM) against live source —
>    these are niche packages and your recall may be stale. Report actual signatures, and
>    which package handles the forecast tables (`P5MIN`) vs dispatch tables.
> 2. For each Phase 1 report, take a real file from `./data/raw/` and print: raw first 30
>    lines showing the `C`/`I`/`D`/`F` row structure, then parsed columns, dtypes, row
>    counts, 3 sample rows per embedded table.
> 3. Determine where `published_datetime` comes from for each report — explicit column,
>    filename, or directory listing time. Show evidence. Flag ambiguity.
> 4. **Measure the `RUN_DATETIME` → actual-availability lag** for `P5MIN` empirically
>    across ~20 files using NEMWeb directory listing timestamps. Report the distribution
>    and recommend a conservative buffer.
> 5. Confirm the `INTERVENTION` flag behaviour on `DISPATCHPRICE` — find a real
>    intervention interval in the data and show me both rows.
>
> Deliverable: `docs/DATA_MODEL.md`. Then propose the bitemporal schema, table by table,
> and **stop for my review.** No migrations yet.

Commit: `docs: NEMWeb data model and publication time rules`

---

### Session 1.2 — Scaffold (1h)

> Read `BUILD_PLAN.md` and `docs/DATA_MODEL.md`. Skeleton only, no ingestion logic.
>
> - Structure: `src/nemobs/{config,ingest,storage,features,quality,cli}.py` packages
> - `pyproject.toml` with `uv`; Python 3.12
> - `docker-compose.yml`: Postgres 16 (plain — skip TimescaleDB for MVP unless trivial),
>   Redis, MinIO. Healthchecks on all three.
> - `config.py` — Pydantic Settings, `.env.example` committed, `.env` gitignored
> - `structlog` JSON logging, configured once
> - Alembic + initial migration for the agreed schema. Every table carries
>   `interval_datetime` and `published_datetime`. Composite index
>   `(region, interval_datetime, published_datetime)` on forecast tables.
> - `cli.py` — Typer with `backfill`, `poll-once`, `verify`, `status` stubbed
> - `ruff` + `mypy`, GitHub Actions running lint/types/pytest
> - `docs/DECISIONS.md` seeded with: time representation, why bitemporal, intervention
>   handling
>
> Acceptance: clean-checkout `docker compose up` healthy, `alembic upgrade head` succeeds,
> `nemobs --help` lists commands, CI green.

Commit: `chore: scaffold` · `feat: compose stack` · `feat: bitemporal schema` ·
`ci: lint types tests` · `docs: decisions log`

---

### Session 1.3 — Vertical slice: DISPATCHPRICE (2h)

> One report end to end, properly, before touching the rest.
>
> - `ingest/nemweb_client.py` — listing, download, backoff with jitter, content hashing
> - `storage/raw_store.py` — persist raw zip to MinIO keyed by content hash **before
>   parsing**. The DB must be rebuildable from object storage alone.
> - `ingest/parsers.py` — parse via the Session 1.1 verified API, raw `C`/`I`/`D`/`F`
>   fallback
> - `ingest/publication.py` — `published_datetime` derivation per documented rule,
>   including the measured lag buffer
> - `storage/repository.py` — idempotent upsert; re-running any window is a no-op
> - `ingest/tasks.py` — Celery task + Beat schedule; backfill and live poll share one
>   parsing path
> - `ingest_watermark` table for per-report state
> - Handle `INTERVENTION` per the documented decision; assert uniqueness after filtering
>
> Tests: parser against a committed fixture · publication-time derivation against files
> with independently known availability · idempotency (ingest twice, row count unchanged)
> · intervention handling
>
> Acceptance: `nemobs backfill --report DISPATCHPRICE --start 2026-07-01 --end
> 2026-07-08` loads cleanly with no gaps or dupes; running twice changes nothing.

Commit: `feat: nemweb client` · `feat: raw object store` · `feat: dispatchprice ingestion`
· `test: parser idempotency intervention`

---

### Session 1.4 — Remaining reports + quality (2h)

> Extend to `P5MIN`, `DISPATCHREGIONSUM`, `ROOFTOP_PV_ACTUAL`, `ROOFTOP_PV_FORECAST`,
> `DISPATCHCONSTRAINT`, `MARKETNOTICE`.
>
> Refactor ingestion into a **report registry** keyed by report name, so adding a report
> is config plus a parser. Do this now that you have two concrete cases — not before.
>
> **Critical:** for `P5MIN`, the same `(interval, region)` has many rows, one per forecast
> run. **This is correct — do not deduplicate.** Add a test asserting multiple runs
> persist for one target interval, and that the run count is plausible (~12 runs for an
> interval one hour ahead).
>
> `quality/checks.py`:
> - interval gap detection per report
> - duplicate `(interval, published, region, intervention)` detection
> - range assertions: price within floor/cap, demand plausible, PV non-negative
> - `nemobs verify --start X --end Y`, exit non-zero on failure
>
> Acceptance: one week of every report ingests cleanly; `verify` reports honestly;
> multi-run test passes.

Commit: `refactor: report registry` · one `feat:` per report · `feat: quality checks`

---

### Session 1.5 — features_asof, leakage test, backfill (2.5h + runtime)

The centrepiece. Everything downstream depends on this being right.

> 1. `features/asof.py`, one public function:
>    `features_asof(interval: datetime, asof_ts: datetime) -> FeatureBundle`
>    - `FeatureBundle` is a Pydantic model, not a DataFrame
>    - Every source filtered on `published_datetime <= asof_ts`
>    - For `P5MIN`: return the most recent run available at `asof_ts`, **plus the
>      revision delta** vs the prior run for that interval (the change between successive
>      publications is expected to be a strong feature — expose it now)
>    - Explicit nulls with a reason code when data genuinely wasn't available. **Never**
>      fill a gap from a later publication.
>    - **Provenance:** every field carries the `published_datetime` of its source row
> 2. `tests/test_leakage.py` — sample ≥1000 random `(interval, asof_ts)` pairs across the
>    backfill window, call `features_asof`, assert **no field's provenance timestamp
>    exceeds `asof_ts`**. Check provenance, not the query — a test that re-runs the same
>    filter proves nothing. Blocks merges in CI.
> 3. Enforce the boundary: nothing outside `features/` may import `repository` for
>    modelling reads. Add an import test.
> 4. Run the 12-month backfill from `./data/raw/`. Resumable, progress output.
> 5. `nemobs verify` over the full window → `docs/BACKFILL_REPORT.md` with row counts,
>    coverage, and gaps found — **including the ones you couldn't resolve.**
>
> Acceptance: all Phase 1 definition-of-done items pass, CI green, 12 months loaded.

Commit: `feat: features_asof with provenance` · `test: leakage prevention` ·
`ci: block on leakage test` · `chore: 12 month backfill` · `docs: backfill report`

---

## Phase 1 discipline

**Read every diff before committing.** If you can't explain a file in an interview it
shouldn't be in the repo. This is the difference between a project you built and a
project that appeared.

**`docs/DECISIONS.md`, two lines per non-obvious choice**, written when you make it. Why
bitemporal. Why provenance-based leakage testing. Why forecast runs aren't deduplicated.
Why that intervention rule. Why that lag buffer. This becomes your interview script.

**If a spec requirement turns out wrong once you see real data, change it and note why.**
Working around a bad assumption silently is how these projects rot.

---

## Before Phase 2

Sanity checks worth ten minutes:
- Plot VIC1 price for one week. Do you see the evening peak and midday negative prices?
- Count negative-price intervals as a share of the year. Does it look like the >20% of
  hours reported for VIC/SA?
- For one interval, pull all P5MIN runs targeting it and plot forecast vs. horizon. Does
  it converge toward the actual as the interval approaches?

That third plot is the entire thesis of the project in one image. Put it in the README.
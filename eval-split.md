# EVAL SPLIT AND GATE — the M3 bar, defined BEFORE any corpus build or adapter training

Work order: WO-C0 · Date: 2026-11-12 · Status: DEFINITION (no training, no eval was run to produce this file)

This file defines what "the adapter beats the prompt-only baseline" means. C1 (corpus), C2
(training), and T1 (training test lane) reference this file as the pass bar. Nothing may be
redefined after training starts except by a dated revision appended below.

---

## 1. THE REALITY (grounded in what is actually on disk)

- **129 tasks total** in `C:\Users\aaron\evo\state\gemma\eval\starter\tasks.jsonl` (1,984,455 B, 129 lines).
- **1 of 129 snapshots is locally available**: `starter\snapshots\httpx_3672.tgz` (task `httpx_3672`,
  full git repo at its base_commit). The other 128 snapshots are NOT on disk — they come only from
  the Kaggle dataset / notebook environment, which mounts all tasks.
- **Therefore: the FULL local split is small — exactly one runnable task — until the
  Kaggle-notebook lane is used.** Local Rog is CPU-only with no Docker daemon; the harness's
  `--sandbox subprocess` backend makes a 1-task smoke eval possible locally, but any multi-task
  measurement happens in the notebook environment (per GEMMA_PLAN.md COMPUTE: L4×4 for
  parity-critical evals, on the hardware that scores us).
- Consequence, stated plainly: **tonight's local run proves the PIPE, not the adapter.** No claim
  about adapter quality may be drawn from the local tier.

## 2. THE SPLIT DEFINITION — two tiers

Every id below was read directly from `tasks.jsonl` (provenance in §6). Sorting is plain
lexicographic ascending on `instance_id`. No id was chosen by hand.

### Tier LOCAL — the pipe-proof task (tonight)

- **Task id**: `httpx_3672` (the only task with a local snapshot).
- **Run**: the full harness two-phase pipeline (`swegemma eval --sandbox subprocess
  --task-ids httpx_3672`), run **twice**, once per arm where the model is reachable.
- **Pass bar**: resolution is binary 0 or 1 per run; **both runs must complete both phases**
  (Container A agent patch extraction, Container B pytest verification). A completed run with
  resolution 0 still counts as pipe-success; a crashed/timed-out phase counts as pipe-FAILURE.
- **This tier proves the PIPE, not the adapter.** Its only claim, if green, is: "our submission
  bundle runs end-to-end through the official harness."

### Tier NOTEBOOK — the Kaggle-notebook split (M2/M3)

Fixed rule, no cherry-picking: **DEV = first 12 ids in sorted order; GATE = last 6 ids in sorted
order.** Verified disjoint (0 shared ids).

**DEV-12 (adapter iteration — may be trained on, may be looked at):**
```
fastapi_11194   fastapi_11355   fastapi_12942   fastapi_13207
fastapi_13537   fastapi_13713   fastapi_13786   fastapi_13920
fastapi_14077   fastapi_14099   fastapi_14186   fastapi_14246
```

**GATE-6 (final held-out — NEVER trained on, NEVER inspected during M2):**
```
rich_4006   rich_4070   rich_4075   rich_4076   rich_4077   rich_4079
```

**Honest caveat on the fixed rule**: sorting is repo-confounded — DEV-12 is entirely
`fastapi/fastapi` and GATE-6 is entirely `Textualize/rich`. The rule buys determinism and
zero-selection-bias at the cost of no repo stratification. A stratified revision is allowed only
as a dated amendment appended to this file BEFORE training starts; after M2 begins, the GATE-6
ids are frozen.

**Seed**: `seed: 0` declared in `configs/sampling.yaml` for BOTH arms. If the harness ignores the
seed field, the 2-runs-per-arm design still checks variance empirically (§5).

**Prompt-only baseline config** (§3) runs on **all 18 ids** (DEV-12 for honest comparison during
iteration, GATE-6 for the gate). The gate itself reads **GATE-6 only**.

## 3. THE BASELINE CONTRACT

Prompt-only baseline = **the exact same `agent.yaml` tree with the adapters removed — nothing
else changes.** Concretely, one line: **the `adapter:` key (root `agent.yaml`) and
`adapters/main_lora/` (plus any sub-agent `adapter:` key, e.g. `sub_agents/code_analyzer.yaml`'s
`adapter: tool_lora`) are removed/commented out; the agent tree, tools, prompts, sampling config,
eval budgets, and seed stay byte-identical.** Same model checkpoint name
(`gemma-4-31b-it-qat-w4a16-ct`), same server, same budgets. If a run differs in anything other
than adapter presence, the run is invalid and must be rerun.

## 4. RESOLUTION — the unit of measurement

Quoted contract (HARNESS_README.md §4, "Resolution Criterion"): a task is `resolved = True` iff
pytest exits 0 **and** JUnit XML validates — `passed_tests > 0`, `failures == 0`, `errors == 0`,
every required test node (FAIL_TO_PASS / PASS_TO_PASS / extracted test functions) passed without
being skipped. `resolution_rate = resolved / total tasks in the split ∈ [0.0, 1.0]`.

## 5. THE GATE RULE (M3)

- Arms: **adapter** (full submission tree) vs **prompt-only baseline** (§3), both on **GATE-6**.
- Each arm runs **twice** (2 independent runs, same seed, same notebook environment).
- Per-arm score = mean `resolution_rate` over its 2 runs.
- **PASS: adapter mean > baseline mean in BOTH pairs — i.e. adapter wins run-1 AND run-2 against
  the corresponding baseline runs, strictly greater (no ties count as wins).**
- **NO WIN: any overlapping or tied pair** — including 1 win + 1 loss, 1 win + 1 tie, or 2 ties.
  If variance across runs overlaps, the honest verdict is **NO WIN**, and per GEMMA_PLAN.md M3 we
  ship the prompt-only agent (honesty > sunk cost).

## 6. WHAT THIS GATE CANNOT CLAIM

**One split of 12+6 tasks drawn from a 129-task benchmark is a local selection signal, NOT a
leaderboard prediction.** It does not predict the Kaggle hidden split, the competition ranking,
or generalization beyond `fastapi` + `rich` at these 18 commits. Any paper text, README, or
report that states or implies a leaderboard estimate from this gate is FALSE and must not be
written.

## 7. PROVENANCE

- `tasks.jsonl`: **129 rows** (verified by line count and by parse). First row keys (exact):
  `instance_id, repo, base_commit, patch, test_patch, problem_statement, hints_text, created_at`.
  First row: `instance_id='fastapi_15661'`, `repo='fastapi/fastapi'`,
  `base_commit='ee22a4b8ca46dcce26c8c183afc4992a888d8be2'`. Repo distribution:
  fastapi/fastapi 67 · Textualize/rich 48 · psf/requests 13 · encode/httpx 1.
- **No difficulty field exists in the schema** — difficulty spread is NOT derivable from
  tasks.jsonl alone. `created_at` spans 2023-07-29 → 2026-06-20.
- Snapshot inventory: `starter\snapshots\` contains exactly **1 file**, `httpx_3672.tgz`
  (1,576,322 B) — 1 of 129 tasks (ACQUIRE_REPORT.md, 2026-11-12).
- Split derivation: ids sorted lexicographically; first 12 / last 6 verified disjoint by script.
- Sizing note: WO-C0 depends on B0 (`eval\smoke-test.md`, actual wall-time per eval run) — that
  file does not exist yet as of 2026-11-12. The 12/6 sizes are therefore provisional: if B0
  numbers force a resize, **only N and M change; the rule (first-N-sorted dev, last-M-sorted
  gate, never trained on) and this file's structure do not.**

---

*Appended revisions (dated, oldest last): none.*

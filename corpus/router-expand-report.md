# ROUTER-SEEDS EXPANSION REPORT — router-seeds.jsonl 24 -> 152 rows

Built 2026-11-13 by `build_router_expand.py` (order W-B.1 step 3, FINISH_PLAN.md
lines 239-257). Expanded IN PLACE; the 24 original rows are re-emitted BYTE-VERBATIM
(verified: `lines[:24] == original file lines`, checked after the build against
`wb1/router-seeds.pre-expand.jsonl`, the pre-expansion backup). Only the sources
BUCKETS.md names for B1 (BUCKETS.md line 19) were used. HONESTY LAW: every count is
real from this run (source: `router_expand_summary.json`).

## 1. HEADLINE + ACCOUNTING

| Lane | Source | Scanned | Emitted | Skipped | Rejected |
|---|---|---|---|---|---|
| F fish trace | `evo/traces/fish-20261111-210512.jsonl` | 12 | 12 | 0 | 0 |
| T tasks bug-fix | `scullm/eval/starter/tasks.jsonl` | 129 | 100 | 29 | 0 |
| R rule: explain->analyzer | `scullm/submission/sub_agents/code_analyzer.yaml:7` | 8 | 8 | 0 | 0 |
| R rule: plan->planner | `scullm/submission/skills/scullm-planning/SKILL.md:8` | 8 | 8 | 0 | 0 |
| existing rows | `router-seeds.jsonl` (pre-expansion) | — | 24 kept | 0 | 0 |

**24 + 128 = 152 rows** (`router_expand_summary.json` fields `rows_before`,
`rows_after`). V6 reconciles exactly. `skips_router_expand.jsonl` holds all 29
rejected candidates: tasks.jsonl lines 101-129, each recorded with the cap reason
("this build takes tasks.jsonl lines 1-100 in file order (deterministic)").

## 2. WHAT EACH LANE TEACHES

- **Lane F (12 rows — router behavior evidence)**: one row per fish trace line. Each
  recorded walk tick shows which stage served: sparrow (formulate), crow (decide),
  execute (run one bounded command), check (verify goal facts). The stage-need wording
  is grounded in the walker flow law (`evo/GLOSSARY.md` line 49: "STATE -> SPARROW
  formulates -> CROW answers -> CODE executes ... -> verdict by code policy"); the
  system prompt carries the mechanical tick situation (task_id, turn, verbatim trace
  note) — the pass name NEVER appears in the row's user turn (mechanical leakage check
  in V2). Assistant label = the stage that actually served, e.g.
  `crow - answer the turn`, parse rule unchanged (split on the first " - ").
  Source provenance: trace line number on every row.
- **Lane T (100 rows — the named rule bug-fix->executor)**: tasks.jsonl lines 1-100 in
  file order (BUCKETS.md line 39 names tasks.jsonl as B1 "routing situations" source).
  System = a documented constant frame + a VERBATIM slice of the task's
  problem_statement (first <= 400 chars, cut after the last sentence ender inside the
  window when one exists, else hard cut — a byte-identical substring, never reworded;
  recorded system lengths 159-519 chars) + the task's verbatim `repo` field.
  Assistant = `executor - minimal verified source patch` (wording follows
  `submission/agent.yaml` line 7: "minimal, verified source patch"). User turn neutral.
  Zero exact-duplicate message rows among the 128 new rows (mechanical check post-build).
- **Lane R (16 rows — the named rules explain->analyzer, plan->planner)**: authored
  situation framings of the recorded contracts: the analyzer rows use exactly the three
  situation classes `code_analyzer.yaml` line 7 itself names ("a symbol, file path, or
  question about the repository ... Cannot edit files or run commands"); the planner
  rows restate the scullm planning skill's own law (`SKILL.md` line 8: "Write the plan
  as a .scullm text file BEFORE acting ... Walk only plans the checker passed").
  The route mapping itself is BUCKETS.md line 19's recorded rule
  ("bug-fix->executor, explain->analyzer, plan->planner"). Row `source` = the contract
  line each situation class comes from; the BUCKETS.md rule citation lives here in the
  report. No situation was invented that those lines do not name.

## 3. LABEL CENSUS (all 152 rows, assistant content split on the first " - ")

executor 100, walker-blue 7, analyzer 8, planner 8, planner-red 4, planner-blue 3,
rag 3, base 4, coder 2, walker-red 1, sparrow 3, crow 3, execute 3, check 3
(`router_expand_summary.json` field `label_census`).

**Namespace observation (recorded honestly, not papered over):** the file now spans
three label vocabularies — the moed heritage experts (`walker-red/blue`,
`planner-red/blue`, `coder`, `rag`, `base`; the original 24 rows), the SCULLM role
heads named by BUCKETS.md's B1 rule (`executor`, `analyzer`, `planner`), and the
walker stage names from the fish trace (`sparrow`, `crow`, `execute`, `check`). Two
honest caveats for the coordinator, both recorded here rather than resolved silently:
1. Whether the final router head collapses these vocabularies into one serving enum is
   a serving-time design decision (e.g. planner-red/planner-blue vs planner) — it is
   NOT decided here.
2. `crow` is both the trace's decide-stage name and the submission root agent's name
   (`agent.yaml` line 5: `name: crow`). The trace rows use it in the stage sense; the
   collision is the sources' own vocabulary, kept verbatim.

## 4. VALIDATION (house V-pattern, adapted for router rows)

- **V1 PARSE**: all 152 lines of the expanded file re-read and parsed: 0 failures; new
  rows re-validated in full. PASS.
- **V2 SCHEMA**: exact key order `[messages, source]`; 3 well-formed messages;
  assistant parses to "<expert> - <desc>" with the expert in the lane's allowed set;
  the row's expert token never appears in that row's user turn. 0 failures.
- **V3 NO TOKENIZER LITERALS**: every new row serialized and scanned for all 8
  literals; source probes (slice + repo) scanned pre-emit. 0 hits.
- **V5 PROVENANCE**: every source stat-checked (fish 12 lines, tasks.jsonl 129,
  code_analyzer.yaml 30, SKILL.md 118 — `router_expand_summary.json` field
  `source_lines`); every source_line within range. 0 failures.
- **V6 ACCOUNTING**: reconciles exactly (section 1).
- Byte-fidelity of the original 24 rows: VERIFIED after the write (section header).

## 5. PROVENANCE — sources stat'd READ-ONLY, all UNCHANGED after the build

| Path | Lines | Role |
|---|---|---|
| `C:/Users/aaron/evo/traces/fish-20261111-210512.jsonl` | 12 | lane F source (READ-ONLY; BUCKETS.md line 19 names it) |
| `C:/Users/aaron/scullm/eval/starter/tasks.jsonl` | 129 | lane T source (competition published TRAINING split; BUCKETS.md line 39) |
| `C:/Users/aaron/scullm/submission/sub_agents/code_analyzer.yaml` | 30 | lane R analyzer contract, line 7 |
| `C:/Users/aaron/scullm/submission/skills/scullm-planning/SKILL.md` | 118 | lane R planner law, line 8 |
| `C:/Users/aaron/evo/GLOSSARY.md` | 274 | stage-need wording source, line 49 (cited here, not a row source) |

All stat'd (size + mtime + sha256) before reading and re-stat'd after the build: all
UNCHANGED (`router_expand_summary.json` field `read_only_assertions_unchanged`).
Rule-mapping source: `scullm/submission/corpus/BUCKETS.md` line 19.

## 6. SCOPE NOTES (honest)

- BUCKETS.md line 19 also names "sea-seat variants, moed signature expansion" as
  expansion material: NOT taken — the order restricted this build to the fish trace +
  SWE routing rules. The existing 24 moed rows already cover the moed signatures.
- tasks.jsonl is the competition's published TRAINING split (BUCKETS.md section 4
  honesty note): these router rows are trained-and-sourced on that split only; no
  claim of transfer to the hidden scoring split is made anywhere.
- The 29 cap-skipped tasks lines remain convertible later by re-running the builder
  with a raised cap; they are recorded, never laundered.

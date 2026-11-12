# COMPLETION-AUDIT.md — corpus completion audit (order W-B.1 step 1)

Audited 2026-11-13 by worker W-B. Every count in the "measured" column is a REAL
`wc -l` re-run by this worker this session (not copied from the plan). Expected numbers
come from FINISH_PLAN.md section 1, lines 95-112 (the plan's own table, measured
2026-11-12). Gap statuses cite BUCKETS.md. Serving heads cite the corpus's own build
reports. HONESTY LAW: any mismatch would be flagged in the last column; every number
carries its source.

## 1. THE AUDIT TABLE

Command run this session (working dir `C:/Users/aaron/scullm/submission/corpus/`):
`wc -l <each file below>` — re-run again at audit close; both runs agreed.

| File | Measured (wc -l, this session) | Plan expected (FINISH_PLAN.md lines 95-112) | Match | BUCKETS.md gap status | Serving head |
|---|---|---|---|---|---|
| `corpus_decisions_gemma.jsonl` | 370 | 370 | YES | B2 — deepest bucket; normalization complete, 370 emitted (`bucket-build-report.md` s2, V1-V6 green, reconciles exactly) | **crow head** (TEV1 walker decisions; the D-row trainer's sole input, `training/t4/RUNBOOK.md` s.c) |
| `corpus_signals_gemma.jsonl` | 1,239 | 1,239 | YES | B6 — "strongest ready bucket"; normalization complete, 1,239 emitted (`bucket-build-report.md` s3) | **analyzer head** |
| `corpus_b7_swe.jsonl` | 695 | 695 | YES | B7 — source converted; 695 rows from the published training split (`b7-report.md`; BUCKETS.md line 25's "0 converted" predates that build) | **executor head** |
| `corpus_b4_chunks.jsonl` | 350 | 350 | YES | B4 — Chunk Law bucket converted; 350 rows, one bounded action per row (`b4-report.md`; BUCKETS.md line 22's "0 trained rows" predates that build) | **executor head** (walker-side chunk edits) |
| `corpus_freecad.jsonl` | 366 | 366 | YES | B11 — FreeCAD harvest, minted after BUCKETS.md's 9-bucket map (`freecad-report.md` line 5: "next free id after B9; B10 is taken") | **FreeCAD head** |
| `corpus_godot.jsonl` | 80 | 80 | YES | B12 — Godot head fleet, 6 sub-heads (`godot-report.md`) | **Godot head fleet** |
| `corpus_b8_toolnav.jsonl` | 60 | 60 | YES | B8 — "no source at all" per BUCKETS.md line 26; 60 rows minted synthetically from the tool spec (`b8-report.md`) | **executor / analyzer** (tool grounding) |
| `corpus_d_gemma.jsonl` | 94 | 94 | YES | superseded D slice — the earlier C1 build of the same decisions; **do not upload** (`training/t4/RUNBOOK.md` lines 93-94) | none (superseded; not a serving corpus) |
| `corpus_freecad_dataset.jsonl` | 69 | 69 | YES | B11-DATASET lane — dataset-verified CAD rows (`dataset-build-report.md`) | **FreeCAD head** (dataset lane) |
| `corpus_freecad_flows.jsonl` | 48 | 48 | YES | B11 flows lane — 48 SCULLM/OFL plan rows, 8 parametric families x 6 (`freecad-flows-report.md`) | **FreeCAD head** (flows lane) |
| `corpus_b11_bspline.jsonl` | 31 | 31 | YES | B11-DATASET bspline emitter — the 31 lifted BSpline rejects (`dataset-build-report.md` s99-113) | **FreeCAD head** (dataset bspline lane) |
| `router-seeds.jsonl` | 152 | 24 (pre-expansion; expansion ordered by W-B.1 step 3) | YES, with the ordered change noted | B1 — "thin" per BUCKETS.md line 19; expanded this session 24 -> 152 (`router-expand-report.md`; 24 original rows byte-verbatim + 128 new) | **router head** (root agent) |
| `corpus_b9_guardrails.jsonl` | 72 | (new file — W-B.1 step 2 deliverable) | n/a (new) | B9 — "0 purpose-built" per BUCKETS.md line 27; 72 purpose-built rows now exist (`b9-report.md`: 52 source-grounded + 20 authored) | **all heads** (anti-hallucination layer) |

Literal file sum of the 12 plan-listed files (pre-expansion B1 count of 24) was 3,426 —
matches FINISH_PLAN.md line 112. Current literal file sum over the 13 files above:
**3,626** (measured `wc -l` total, this session). The delta vs the plan table is exactly
the ordered W-B.1 work: router-seeds +128, corpus_b9_guardrails +72; no other file
changed.

**MISMATCHES: NONE.** All 12 plan-listed measured counts equal the plan's expected
numbers exactly.

## 2. THE D-ROW VERIFICATION (not just a line count)

`corpus_decisions_gemma.jsonl` was JSON-parsed line by line this session: **370/370 rows
carry `"type": "D"`** (type histogram `{"D": 370}`, zero other types; zero parse
failures). The plan's claim (FINISH_PLAN.md line 100: "all type D") is verified by
content, not inferred from the line count.

## 3. B3 AND B5 — OUT-OF-SCOPE FOR THE FIRST ADAPTER

- **B3 (SWE-format plans): OUT-OF-SCOPE for the first adapter** — BUCKETS.md line 21
  records 0 rows in SCULLM format (239 house-format P rows need re-templating, plus
  synthetic authoring); it serves the planner head, which does not exist in the first
  adapter (the crow head trains on D rows only, `training/t4/RUNBOOK.md` s.c).
- **B5 (replans): OUT-OF-SCOPE for the first adapter** — BUCKETS.md line 23 records it
  thin (66 house-format + 91 envelopes) and its raw material absent (0 `war2-*.log`
  tick logs found on disk, BUCKETS.md line 46); it serves planner/walker robustness,
  not the crow head's first training run.

Both remain post-first-adapter work per BUCKETS.md section 4's build order; neither
blocks the crow-head training set.

## 4. CRITICAL-PATH READ

The crow head's training set is the 370 D rows of `corpus_decisions_gemma.jsonl`
(FINISH_PLAN.md lines 114-118: the trainer consumes exactly those rows, measured twice
+ dry-run confirmed). That file is present, complete, content-verified (section 2), and
unchanged by this order. The B1 and B9 builds of W-B.1 serve the router and
anti-hallucination layers that come AFTER the first adapter ships; they did not touch
any crow-head input.

CROW-HEAD TRAINING SET: COMPLETE (370 D rows, corpus_decisions_gemma.jsonl) — no critical-path corpus work remains.

# BUCKET BUILD REPORT — B2 DECISIONS + B6 SIGNALS (Gemma normalization)

Built 2026-11-12 by `build_b2.py` and `build_b6.py`. Law executed:
`gemma-template.md` (RULE 0 N1/N2, rules a-d, RULE 5, V1-V6) + `BUCKETS.md` B2/B6.
BOUNDARY LAW: every source under `sunny\`, `ham_n_eggs\`, `evo\tasks|traces` was stat'd
(size+mtime+sha256) before reading and re-stat'd after — all UNCHANGED, READ-ONLY honored.
HONESTY LAW: every count is real from this run; no row invented; full skip lists written to
`skips_b2.jsonl` / `skips_b6.jsonl` (one JSON object per skipped row, with reason), never
laundered, never truncated.

## 1. THE HEADLINE + FLEET TOTAL

| Bucket | File | Emitted | Skipped (with reasons) | Rejected | Held-out |
|---|---|---|---|---|---|
| B2 DECISIONS | `corpus_decisions_gemma.jsonl` | **370** | 2,998 | 0 | 140 |
| B6 SIGNALS | `corpus_signals_gemma.jsonl` | **1,239** | 773 | 0 | 0 |

**FLEET TOTAL TODAY: 1,727 rows** = 94 (`corpus_d_gemma.jsonl`, the prior D-build)
+ 370 (B2) + 1,239 (B6) + 24 (`router-seeds.jsonl`, B1).

Honesty note on the fleet sum: the 94 D rows and B2's 94 sunny/fish rows are the SAME
decisions — B2 re-emits them under the `"bucket":"B2"` label (cross-check: **94/94 exact
matches modulo the bucket key**, zero mismatches). B2's net-new content over the D-build is
the **276 house-lane rows** (below). Counting unique decisions + signals + router rows, the
non-redundant corpus today is **1,633**; the 1,727 figure is the literal file sum.

## 2. B2 DECISIONS — 370 emitted, per-source accounting (V6)

V6 fields: scanned = emitted + rejected + skipped + deduped + held-out + out-of-scope
(`out_of_scope` is one added, documented field for rows that belong to other buckets).

| Source | scanned | emitted | rejected | skipped | deduped | held-out | out-of-scope |
|---|---|---|---|---|---|---|---|
| `evo/traces/fish-20261111-210512.jsonl` | 12 | 3 | 0 | 9 | 0 | 0 | 0 |
| `sunny/runs/decisions_corpus.jsonl` | 2,676 | 91 | 0 | 2,585 | 0 | 0 | 0 |
| `ham_n_eggs/war/train/corpus/loop-v16.jsonl` (house D lane) | 2,427 | 276 | 0 | 404 | 0 | 0 | 1,747 |
| `sunny/runs/decisions_holdout.jsonl` (eval-only) | 140 | 0 | 0 | 0 | 0 | 140 | 0 |
| **TOTAL** | **5,255** | **370** | **0** | **2,998** | **0** | **140** | **1,747** |

Reconciliation: 5,255 = 370 + 0 + 2,998 + 0 + 140 + 1,747 — **RECONCILES EXACTLY**.

Letter histogram (emitted): A=88, B=113, C=169. Outside A-D: **0** (RULE 5 gate held). No D
letters exist in the sources; that imbalance is recorded, not corrected.

### Derivation rules per lane

- **Fish trace (N1)** — 3 rows (t1/t2/t3, all chose A): `pass=="crow"` + `decided_by=="model"`
  + chosen letter; state = goal + ` | check: ` + `json.dumps(steps[0].check)` (LAW-LITERAL
  glue); options = the LAW-LITERAL letter protocol; SYSTEM constant (trace carries none).
  9 harness passes skipped with reasons.
- **Sunny (N2)** — 91 `starling_envelope` rows (all 4-option): `.strip()`ed state/question
  (the template's only permitted normalization), options + system verbatim,
  `answer = LETTERS[payload.answer]`. Skips: 1,007 `assess` (5 options each — RULE 5, never
  truncated), 210 `judge` (no option letters), 1,336 `encode` + 32 `coder_pair` (non-decision
  kinds — `encode` is B6's source, `coder_pair` is B4 material).
- **House D lane (ADAPTED TRANSFORM, coordinator direction)** — of 680 loop-v16 D rows, the
  **276 that carry a real source `id`** and parse EXACTLY as
  `[STATE: block / EPISODE: 1 line / QUESTION: 1 line / OPTIONS: / option lines /
  ANSWER LETTER:]` are emitted with the **EPISODE line relocated verbatim into row metadata
  key `"episode"` (out of the training input)** and the decision input re-rendered in the
  template's canonical STATE/QUESTION/OPTIONS form. State/question/options/answer are
  byte-identical slices located by their unambiguous label prefixes — nothing guessed,
  nothing deleted, nothing invented. The training input differs from the source render by
  that one relocated line, and the full episode text rides on every emitted row. Findings:
  - 404 rows skip-listed: **292** whose render deviates from the house shape (exact
    label-delimited parse fails), **112** that parse but carry **no task_id** (V2 requires a
    non-empty task_id; inventing one is forbidden — these are the D-contract rows the
    D-builder's rules genuinely cannot cover).
  - 20 of the 276 admitted rows carry self-documenting cross-chain ids (`cross/A+B`) — real
    ids, visible in `task_id`, admitted.
  - 0 exact duplicates among the converted rows (the house lane's duplicate mass sits in the
    no-id set). 1,747 non-D rows (P/S/W/T/T2) are out-of-scope — other buckets' lanes.
- **Holdout** — all 140 rows held out: `decisions_holdout.jsonl` is eval-only per BUCKETS.md
  ("eval only — never train on it"). Counted, never trained on.

## 3. B6 SIGNALS — 1,239 emitted, per-source accounting (V6)

| Source | scanned | emitted | rejected | skipped | deduped | out-of-scope |
|---|---|---|---|---|---|---|
| `sunny/runs/decisions_corpus.jsonl` (`encode` kind) | 2,676 | 1,014 | 0 | 322 | 0 | 1,340 |
| `ham_n_eggs/war/train/corpus/loop-v16.jsonl` (`T2` kind) | 2,427 | 225 | 0 | 451 | 0 | 1,751 |
| **TOTAL** | **5,103** | **1,239** | **0** | **773** | **0** | **3,091** |

Reconciliation: 5,103 = 1,239 + 0 + 773 + 0 + 3,091 — **RECONCILES EXACTLY**.

Row shape (both lanes): system = the grounding law in one line; user = the raw observation;
assistant = the grounded fact summary.

### Derivation rules per lane

- **T2 lane (verbatim admission)** — house T2 rows are ALREADY the target shape (same 3-turn
  system/user/assistant form, one system string across all 676). Admitted verbatim with the
  bucket tag; **225 distinct rows emitted**; the other 451 are exact duplicates of an earlier
  T2 row (the house walk repeats command→finding pairs) — each recorded in the skip list as
  `exact-duplicate of T2 row N` naming the first occurrence's source line.
- **Encode lane (ADAPTED TRANSFORM)** — the 1,336 encode rows carry `{"raw": <observation>,
  "target": {obs_id, status, error_type, exit_code, raw_chars, key_facts, excerpt}}`. The
  schema has no chat payload, so per the work order the transform is adapted honestly:
  - user = `raw` (stripped — the template's permitted normalization);
  - system = **"You read tool outputs and state what was learned. One short line."** — copied
    VERBATIM from the house T2 rows (the encode rows carry no system of their own; the
    closest proven constant is the house lane's own signals system);
  - assistant = ONE mechanical sentence over the record's own fields, e.g.
    `obs o-0005: status ok, error_type none, exit 0, 24 chars; facts: 1 entries; entries:
    build_output_nightly.log.` — every value verbatim from `target`, glue strings are
    LAW-LITERAL build constants; `obs_id` provenance preserved in the content. All 1,014
    summaries are exactly 1 sentence (enforced ≤3 by the adapted V4, mechanical counter).
  - Admitted by status: **ok 741, error 273** (error observations get grounded error
    summaries — legitimate analyzer signals).
  - Skips (322): **52 empty-raw rows** (nothing to ground a summary on; user content would be
    empty — flagged as **B9 material** per BUCKETS.md), **21 rows whose raw/target carries
    the Qwen chat-template literals** (verbatim `core/config.py` excerpts — RULE (a)/V3 ban
    them from stored rows), **249 exact duplicates** (`exact-duplicate of encode row N`).

Schema surprise, counted: the encode rows' `raw_chars` field disagrees with `len(raw)` on 102
rows. The recorded `raw_chars` is carried VERBATIM into summaries (it is the source record's
own assertion); no value was recomputed or silently corrected.

### Dedup accounting note

Per the coordinator's dedup law, every dedup drop is recorded as a NAMED skip entry
(`exact-duplicate of <lane> row <first source line>`) and counted under `skipped`; the V6
`deduped` field is therefore 0 in both builds because every dropped row carries its own skip
entry. The breakdown in §4 separates them.

## 4. SKIP BREAKDOWN (both buckets, aggregated from the skip files)

| Reason | Rows | Bucket |
|---|---|---|
| sunny `encode`/`coder_pair`: non-letter-decision kinds (template §1b) | 1,368 | B2 |
| sunny `assess`: option_count=5 exceeds the A-D protocol (RULE 5) | 1,007 | B2 |
| house D: render deviates from the house shape (exact parse fails) | 292 | B2 |
| sunny `judge`: outcome judgments, no option letters | 210 | B2 |
| house D: parses but has no task_id (id field absent — never invented) | 112 | B2 |
| fish trace: non-crow harness passes (sparrow/execute/check) | 9 | B2 |
| T2 exact-duplicate of an earlier T2 row | 451 | B6 |
| encode exact-duplicate of an earlier encode row | 249 | B6 |
| encode: empty raw — B9 material (BUCKETS.md) | 52 | B6 |
| encode: Qwen chat-template literals in raw/target (RULE a/V3) | 21 | B6 |
| **Total skipped** | **3,771** | |

The 1,007 assess rows were NOT laundered into 4 options; the true A–E space is preserved and
skip-listed. If the owner widens the protocol, re-running `build_b2.py` re-admits them
unchanged.

## 5. VALIDATION V1-V6 (both builds)

- **V1 PARSE**: `corpus_decisions_gemma.jsonl` — 370 lines re-read, 0 failures. PASS.
  `corpus_signals_gemma.jsonl` — 1,239 lines re-read, 0 failures. PASS.
- **V2 SCHEMA**: B2 — exact key order `bucket, type, task_id, state, question, options,
  answer, source, source_line[, episode][, joined_from], messages`; `type=="D"`; non-empty
  task_id; ≥2 non-empty options; 3 message objects, roles system/user/assistant, non-empty
  contents. B6 — exact key order `bucket, type, source, source_line, messages`; `type=="S"`;
  same message rules. 0 failures at emit and on re-read, both files.
- **V3 NO TOKENIZER LITERALS**: every emitted line serialized and scanned for all 8 literals.
  `corpus_decisions_gemma.jsonl`: 0 hits. `corpus_signals_gemma.jsonl`: 0 hits. (`/no_think`
  inside the trace SYSTEM string is ordinary instruction text — RULE (a), exempt.)
- **V4**: B2 letter closure — every assistant content is a single letter matching `^[A-G]$`,
  equals `answer`, index < len(options), inside A-D; every user content carries the
  `A) …` block and ends `ANSWER LETTER:`. B6 adapted (coordinator direction) — assistant
  content non-empty and ≤3 sentences: all 1,239 rows are exactly 1 sentence (dist:
  {1: 1239}); assistant lengths 21–278 chars; user lengths 1–4,000 chars.
- **V5 PROVENANCE**: every row's `source` stat-checked at build time and every `source_line`
  within the file's line count (B2: fish 12 lines, sunny 2,676, loop-v16 2,427, holdout 140;
  B6: sunny 2,676, loop-v16 2,427); trace rows' `joined_from` stat-checked.
- **V6 ACCOUNTING**: reconciles exactly in both builds (§2, §3).
- **END-OF-TURN CHECK: NOT MEASURED — Gemma tokenizer not staged (OQ3).**
- Rejections at emit time: **0** in both builds.

## 6. PROVENANCE — every source, stat-checked, READ-ONLY asserted

| Path | Bytes | Lines | sha256 (first 16) |
|---|---|---|---|
| `C:/Users/aaron/evo/traces/fish-20261111-210512.jsonl` | 2,950 | 12 | `f50fd4110f53898b…` |
| `C:/Users/aaron/sunny/runs/decisions_corpus.jsonl` | 2,782,170 | 2,676 | `ba6a7a066aa2f27b…` |
| `C:/Users/aaron/ham_n_eggs/war/train/corpus/loop-v16.jsonl` | 4,518,403 | 2,427 | `c9674600d597d434…` |
| `C:/Users/aaron/sunny/runs/decisions_holdout.jsonl` | 151,741 | 140 | `68abcde8bfbd6f47…` |

- All four sources were stat'd (size+mtime+sha256) before reading and re-stat'd after both
  builds: **all UNCHANGED**. Nothing outside `C:/Users/aaron/evo/` was written.
- Full skip lists: `skips_b2.jsonl` (2,998 entries), `skips_b6.jsonl` (773 entries) — one
  JSON object per skipped source row with reason and, where meaningful, kind /
  true_option_count / answer_index / duplicate_of_line.
- Machine-readable summaries: `b2_summary.json`, `b6_summary.json`.
- Builders: `build_b2.py`, `build_b6.py` (in this directory).

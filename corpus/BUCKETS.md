# BUCKETS.md — the training-data bucket map (Gemma E2B multi-head fine-tune)

Built 2026-11-12. Every count below is a REAL count from disk this session
(`wc -l` or JSON parse). Where a source is not built yet, the count is **0 —
TO AUTHOR / TO CONVERT**. HONESTY LAW honored throughout.

Two corrections to prior evidence, from disk:
- `decisions_corpus.jsonl` is **2,676 rows**, not the 2,242 previously claimed.
- `decisions_holdout.jsonl` is **140 rows**, not 114.
- `tasks.jsonl` lives at `C:\Users\aaron\evo\state\gemma\eval\starter\tasks.jsonl`
  (129 rows) — the path given in the brief (`state\gemma\starter\`) does not exist.

---

## 1. THE NINE BUCKETS

| # | Bucket | Serves head | Row schema (one line) | Source files | Real rows today | Gap |
|---|--------|-------------|----------------------|--------------|-----------------|-----|
| B1 | ROUTER | **router** (root agent, `router_lora`) | `{messages:[system(user situation)/user/assistant(head name)], source}` chat row | `router-seeds.jsonl` (24) + `fish-20261111-210512.jsonl` (12 trace rows, convertible) | **24 ready** (+12 traces) | Thin. ~150+ more rows TO AUTHOR: SWE routing rules (bug-fix→executor, explain→analyzer, plan→planner), sea-seat variants, moed signature expansion |
| B2 | DECISIONS | **TEV1-walker** (crow) | intent-context STATE/EPISODE/QUESTION/OPTIONS → single letter or gate label | `decisions_corpus.jsonl` kinds `assess`(1007) + `judge`(210) + `starling_envelope`(91); `loop-v16.jsonl` D rows (680, house lane) | **1,308** (sunny lane) + 680 (house lane) = **1,988** | Deepest bucket. Needs format normalization into `gemma-template.md` chat rows; `judge` kind has 125/210 rows with null labels to filter |
| B3 | PLANS | **planner** | intent (problem_statement/objective) → SCULLM script (fenced plan program) | house lane P rows (239) + 227 persisted plan-tree JSONs (68 red + 159 blue); SCULLM template TO AUTHOR | **239 house-format** (wrong template for SCULLM) + 227 raw trees | **0 rows in SCULLM format.** Re-template P rows, then synthetic rows from tasks.jsonl intents TO AUTHOR |
| B4 | CHUNK-EDITS | **executor** | plan node → ONE incremental edit (`edit_file` old→new or one command), Chunk Law | closest raw material: T rows (676, one command/tick — bash not file edits), `coder_pair` rows (32), tasks.jsonl gold patches (129) | **0** in trained format | **Zero rows today.** The Chunk Law's own bucket is empty. Convert patches → hunk-per-row trajectories + synthetic TO AUTHOR. Highest-value conversion job |
| B5 | REPLANS | **planner / walker** | failure observation → honest corrected plan (or replan decision) | house S rows (66); `starling_envelope` rows (91, "loop, replan, or accept?" envelopes); failure-bearing encode rows (399) | **66 house-format** (+91 envelope decisions) | Thin. Need failure traces from live walks (0 `war2-*.log` tick logs found on disk — raw logs absent; only the minted corpus remains) |
| B6 | SIGNALS | **analyzer** | observation → grounded fact summary (one line, Cartographer style) | `decisions_corpus.jsonl` `encode` kind (1336: 933 ok / 399 error / 4 empty); house T2 rows (676) | **1,336** (+676) | Strongest ready bucket. Normalize to chat format; the 403 error/empty rows double as B9 material |
| B7 | SWE-EDITS | **executor** | problem_statement → minimal patch trajectory (chunked hunks) | `tasks.jsonl` training split (129 rows, SWE-bench schema, **gold `patch`+`test_patch` included**); our own repos' real bugs TO AUTHOR | **129 source tasks** / **0 converted rows** | Source exists with gold patches — conversion is mechanical, not authoring. Own-repo bug harvesting not started |
| B8 | TOOL-NAV | **executor / analyzer** | symbol question → graph-tool call sequence → narrow read | none found. Competition's 9 sandbox tools exist in `swegemma` harness; no tool-use corpus minted | **0** | **No source at all.** Must be minted from the competition tool spec + live tool traces. Blocks executor/analyzer on tool grounding |
| B9 | GUARDRAILS | **all heads** (anti-hallucination) | situation where honest answer is "not in the vocabulary / not in the data" → replan / ask / abstain | error+empty `encode` rows (403); `judge` null-label rows (125); explicit abstain rows TO AUTHOR | **403 raw** (grounded refusals, repurposable) / **0 purpose-built** | The explicit "not in the vocabulary" rows don't exist yet. Author from the Chunk Law failure modes + hallucination audits |

---

## 2. THE SOURCE INVENTORY

| File | Path | Real rows | Feeds |
|------|------|-----------|-------|
| `decisions_corpus.jsonl` | `C:\Users\aaron\sunny\runs\` (READ-ONLY) | **2,676** (encode 1336, assess 1007, judge 210, starling_envelope 91, coder_pair 32) | B2, B6, B9, B4 (partly) |
| `decisions_holdout.jsonl` | `C:\Users\aaron\sunny\runs\` (READ-ONLY) | **140** (assess 109, judge 22, starling_envelope 9) | **eval only — never train on it** |
| `fish-20261111-210512.jsonl` | `C:\Users\aaron\evo\traces\` | **12** (chosen: pass 9 / A 3; passes sparrow+crow+execute+check 3 each; decided_by model 6 / code 6) | B1 (router behavior evidence, convertible) |
| `router-seeds.jsonl` | `C:\Users\aaron\evo\state\gemma\submission\corpus\` | **24** (heads: walker 7, planner 7, rag 4, base 4, coder 2) | B1 |
| `tasks.jsonl` | `C:\Users\aaron\evo\state\gemma\eval\starter\` (brief's path wrong) | **129** (SWE-bench schema: base_commit, created_at, hints_text, instance_id, patch, problem_statement, repo, test_patch) | B7, B3 (intents), B1 (routing situations) |
| `loop-v16.jsonl` | `C:\Users\aaron\ham_n_eggs\war\train\corpus\` (READ-ONLY) | **2,427** (P 239, D 680, S 66, W 90, T 676, T2 676) | B2 (D), B3 (P), B5 (S), B4 (T), B6 (T2) |
| `tev1-mermaid-v1.jsonl` | same dir (READ-ONLY) | **6,000** chat rows | B2/walker head corpus (already trained tev1m01) |
| `loop.jsonl` / `loop-v15.jsonl` | same dir (READ-ONLY) | **2,027 / 2,095** | lineage only, superseded by v16 |
| `v17.jsonl` | same dir (READ-ONLY) | **27,721** | comparison monolith, not per-bucket |
| `tev1-inputs-v1.jsonl` | same dir (READ-ONLY) | **0** (empty file) | intended B2 phraser lane, never populated |
| plan-tree JSONs | `...\corpus\trees\` (68 red) + `...\corpus\logs_blue\trees\` (159 blue) | **227** files | B3/B5 raw material |
| `war2-*.log` tick logs | NOT FOUND anywhere under ham_n_eggs | **0** | raw walk traces absent — B5 must mint from future live walks |

Row-type definitions (P/D/S/W/T/T2) verified against the `make_loop_data.py`
docstring (READ-ONLY, `C:\Users\aaron\ham_n_eggs\war\train\make_loop_data.py`)
and `C:\Users\aaron\evo\school\TEV1_METHOD.md` §3c.

---

## 3. THE GAPS, RANKED (by which head they block)

1. **B8 TOOL-NAV — 0 rows, no source.** Blocks executor + analyzer on the
   competition's 9 sandbox tools. Nothing to convert; must be minted from the
   harness tool spec and live traces.
2. **B4 CHUNK-EDITS — 0 trained rows.** The Chunk Law's own bucket is empty;
   blocks the executor head entirely. Raw material exists (676 T rows, 129 gold
   patches, 32 coder_pairs) — the conversion job is the biggest single unlock.
3. **B7 SWE-EDITS — 129 sources, 0 converted.** Blocks executor on the actual
   competition shape (problem_statement → patch trajectory). Gold patches are
   in hand; this is mechanical.
4. **B3 PLANS — 0 rows in SCULLM format** (239 in the old OFL builder-program
   template). Blocks the planner head until re-templated.
5. **B9 GUARDRAILS — 0 purpose-built rows** (403 repurposable error rows).
   Cross-cutting: an anti-hallucination head layer, cheap to author.
6. **B1 ROUTER — 24 ready, thin.** Enough for a first LoRA smoke-train, not
   enough for a production router. Blocks everything structurally (it is the
   root agent) but not numerically.
7. **B5 REPLANS — 66 + 91, thin and house-format.** Blocks planner robustness.
8. **B2 DECISIONS — 1,988 rows, needs format normalization only.** Not a data
   gap, a pipeline gap.
9. **B6 SIGNALS — 1,336 + 676, same: normalization only.**

## 4. THE BUILD ORDER

Per the head training order (router → TEV1 walker → roles):

1. **B1 ROUTER first** (expand 24 → ~150: SWE routing rules, sea-seat variants).
   Small authoring cost, unblocks the entry architecture — the router IS the
   root agent in the Self-Loop (`GLOSSARY.md`, "The Self-Loop").
2. **B2 DECISIONS second** — normalize the 1,988 existing rows into the
   `gemma-template.md` chat format. Zero new data; serves the TEV1/crow walker
   head immediately (with `tev1-mermaid-v1.jsonl`'s 6,000 as the house lane).
3. **B6 SIGNALS third** — normalize the 1,336 encode rows. Serves the analyzer
   and grounds every other head's observations.

Then the role-head conversion wave, in value order: **B7 → B4 → B3 → B5 → B9 → B8**
(SWE patches convert first because the source is richest and the intent chain —
Intent-Driven Code, `GLOSSARY.md` — is already in each problem_statement; B4
follows because the Chunk Law applies to every converted trajectory; B8 last
because it needs live tool traces that don't exist yet).

**The honesty note (competition data):** `tasks.jsonl` is the competition's
**published TRAINING split** — the harness README (`eval/starter/HARNESS_README.md`
line 636) explicitly says you may evaluate any submission locally "against the
published training tasks." The **scoring split is hidden**. Training on
training-split tasks is legitimate; **claiming transfer to scoring tasks is not**.
Every B7-derived result must be stated as "trained and evaluated on the
published training split," never as a predicted score.

## 5. PROVENANCE

All counts taken 2026-11-12 from disk by `wc -l` and Python JSON parse
(`PYTHONIOENCODING=utf-8`):

- `wc -l` batch: decisions_corpus 2676 · decisions_holdout 140 ·
  fish-20261111-210512 12 · router-seeds 24 · tasks.jsonl 129.
- Kind tallies (json parse): decisions_corpus {encode 1336, assess 1007,
  judge 210, starling_envelope 91, coder_pair 32} = 2,676 exact; holdout
  {assess 109, judge 22, starling_envelope 9} = 140 exact.
- router-seed head tally (json parse, last assistant message): walker 7,
  planner 7, rag 4, base 4, coder 2 = 24 exact.
- fish tally (json parse): pass sparrow/crow/execute/check 3 each = 12 exact.
- loop-v16 {P 239, D 680, S 66, W 90, T 676, T2 676} = 2,427 exact;
  tev1-mermaid-v1 6,000; loop 2,027; loop-v15 2,095; v17 27,721;
  tev1-inputs-v1 0 (0 bytes).
- Plan trees: `corpus/trees/` 68 red + `corpus/logs_blue/trees/` 159 blue = 227.
- `war2-*.log`: 0 files found (find over ham_n_eggs maxdepth 3).
- Read (READ-ONLY, untouched): `ham_n_eggs/war/train/make_loop_data.py` header,
  `sunny/runs/*.jsonl` headers/samples, competition `HARNESS_README.md` grep.

Writes confined to `C:\Users\aaron\evo\` (this file). BOUNDARY LAW honored.

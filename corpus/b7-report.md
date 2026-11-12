# B7 (SWE-EDITS) BUILD REPORT — corpus_b7_swe.jsonl

Built 2026-11-12 by `build_b7.py` from the competition's published TRAINING tasks.

## LICENSE / HONESTY NOTE (attached to this output by law)

`C:\Users\aaron\evo\state\gemma\eval\starter\tasks.jsonl` is the competition's
**published TRAINING split** (the harness README explicitly permits local
evaluation against published training tasks). Training on it is legitimate.
**The scoring split is hidden — claiming transfer to scoring tasks is NOT
claimable.** Every B7-derived result must be stated as "trained and evaluated
on the published training split," never as a predicted score.

## DERIVATION (synthetic-derivation rows, mechanical)

- Source field verified from a real row: the gold fix is `patch` (unified
  diff); `test_patch` holds the test changes and is NOT used as edit ground
  truth. Row schema: `instance_id, repo, base_commit, patch, test_patch,
  problem_statement, hints_text, created_at`.
- The gold `patch` of each task is **mechanically SLICED into unified-diff
  hunks**; EACH hunk becomes ONE row (Chunk Law: one incremental edit per
  row). Each sliced hunk = `--- <old>` + `+++ <new>` + `@@ ... @@` + body
  (file headers repeated so the hunk stands alone; git plumbing lines —
  `index`/`new file mode` — are dropped as metadata, not edit content).
  Nothing else is touched: hunks are byte-verbatim from the gold patch.
- Assistant content of every row = a real hunk of the task's real gold fix.
  Each row's `source` records the derivation: `tasks.jsonl:<instance_id>#h<k>`
  (task + hunk ordinal).
- User block: `REPO: <repo>` + `PROBLEM: <problem_statement truncated to
  first 2000 chars>` + the fixed intent tail, per the B7 row shape. 11 of 129
  problem_statements exceeded 2000 chars and were truncated by the shape's
  own rule; none were rewritten.

## COUNTS

| Metric | Value |
|---|---|
| Tasks scanned | **129** |
| Tasks admitted (unified patch present) | **129** |
| Tasks skipped (RULE 5: empty / non-unified patch) | **0** |
| Hunks extracted (file sections 278) | **695** |
| Hunks emitted as rows | **695** |
| Hunks skipped (V4 unified-diff parse failure) | **0** |
| Deduped (exact-duplicate messages) | **0** |
| Rows written | **695** |
| Unique source tasks in output | **129** |
| Tasks contributing >1 hunk | **71** (single-hunk tasks: 58) |
| Largest hunk contributors | fastapi_14609 (92 hunks), fastapi_14186 (51), rich_4070 (33) |
| Hunk size (assistant content, chars) | min 132 / median 519 / max 32,461 |

Accounting reconciles exactly: 129 scanned = 129 emitted-at-task-level + 0
skipped; 695 hunks = 695 rows + 0 hunk-skips + 0 deduped. No silent loss.

## SKIP LIST

**Empty — zero entries.** All 129 patches are well-formed unified diffs (0
empty patches, 0 non-unified patches, every hunk's `@@` header counts
reconcile with its body). If the owner later adds malformed tasks, RULE 5
re-runs and records them here with task id, line, and reason.

## V-CHECKS (all enforced by the builder, re-verified by an independent pass)

- **V1 PARSE** — written file re-read; **695/695 lines parse, 0 failures**.
- **V2 SCHEMA** — every row has exactly keys `messages, bucket, source,
  split`; `bucket=="B7"`, `split=="training-published"`; 3 messages with
  roles `system, user, assistant` in order; all contents non-empty.
  **695/695 pass.**
- **V3 NO TOKENIZER LITERALS** — serialized lines scanned for `<|im_start|>`,
  `<|im_end|>`, `<think>`, `</think>`, `<start_of_turn>`, `<end_of_turn>`,
  `<bos>`, `<eos>`: **0 hits**.
- **V4 DIFF PARSES (adapted)** — every emitted hunk starts with `--- `/`+++ `
  lines, contains exactly one `@@` hunk header, and its header line counts
  reconcile against the body (context+removed == old count, context+added ==
  new count; omitted counts mean 1). **695/695 pass, 0 skips.**
- **V5 PROVENANCE** — source path `tasks.jsonl` stat-checked at build time
  (1,984,455 bytes on disk); every row's `source` carries instance_id + hunk
  index; all 129 unique instance_ids in output match source rows. Source read
  **READ-ONLY** — no bytes outside `C:\Users\aaron\evo\` written.
- **V6 ACCOUNTING** — table above; sums reconcile with zero remainder.

## FILES

- Corpus: `C:\Users\aaron\evo\state\gemma\submission\corpus\corpus_b7_swe.jsonl`
  (695 lines, UTF-8, LF, one JSON object per line)
- Builder: `C:\Users\aaron\evo\state\gemma\submission\corpus\build_b7.py`
- Reproduce: `PYTHONIOENCODING=utf-8 python build_b7.py` (deterministic; prints
  the same counts and skip list)

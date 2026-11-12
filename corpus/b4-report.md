# B4 (CHUNK-EDITS, walker side) BUILD REPORT — corpus_b4_chunks.jsonl

Built 2026-11-12 by `build_b4.py`. Converts the sunny/house corpus's T-rows — the
walker-side raw material named for B4 in `BUCKETS.md` — into Chunk-Law-compliant
Gemma rows (one situation -> ONE bounded action per row). The sunny and
ham_n_eggs sources were READ-ONLY throughout; writes are confined to
`C:\Users\aaron\evo\`.

## DERIVATION

Source: `C:\Users\aaron\ham_n_eggs\war\train\corpus\loop-v16.jsonl`, rows
`type == "T"` (676 of 2,427 scanned lines; the other 1,751 rows — P/D/S/W/T2 —
are other buckets' lanes, counted as `out_of_scope`).

The T rows are ALREADY one-bounded-action chat rows, so the transform is the
B6 worker's T2-lane pattern carried over: admit the three turns verbatim and add
the bucket tags. Nothing is invented and nothing is paraphrased (RULE d):

- **system** = the walker's own one-line scaffold law, carried by all 676 rows,
  kept VERBATIM: *"You are the tool operator of a penetration-testing walker.
  Reply with ONE bash command and nothing else — no prose, no fences."* This is
  the one-edit-per-turn law of the Chunk Law at the command depth.
- **user** = the situation: `MISSION:` + `SITUATION (last observation,
  truncated 700):` (the state) + `GOAL: …` (the transition's trigger — the plan
  node being executed) + the `Command:` prompt tail. All 676 source rows match
  this structure; carried byte-for-byte.
- **assistant** = ONE bounded action — a single one-line bash command
  (observed lengths 11–200 chars; 0 multi-line, 0 fences in the source).
- Row keys, in order: `messages, bucket, sub_head, source` — `bucket:"B4"`,
  `sub_head:"chunk-edit"`, `source:"<file>:<line>"` per the B4 brief's row shape.

**Documented schema adaptation (the honesty note):** the B4 brief's row shape
describes the system slot as "the scaffold laws in one line (chunked writes, one
edit per turn, verify before proceed)". The T lane carries its OWN system string,
so per RULE 0-N2 ("it is real conditioning text — never substituted with the
trainer constant") and the B6 T2-lane precedent ("verbatim, it IS the law"), the
source system is kept verbatim and NOT replaced with a build constant. Substituting
B7's executor constant here would overwrite real conditioning text; the brief's
law-shape is satisfied by the source's own one-line law plus the
one-command-per-tick fact itself.

## COUNTS (V6 accounting — reconciles exactly)

| Metric | Value |
|---|---|
| Source lines scanned (whole file) | **2,427** |
| — of which T rows (this bucket's raw material) | **676** |
| — of which out_of_scope (P 239 / D 680 / S 66 / W 90 / T2 676) | **1,751** |
| Emitted rows | **350** |
| Rejected (V-check failures) | **0** |
| Skipped (non-dedup, RULE 5) | **0** |
| Deduped (exact-duplicate messages, counted) | **326** |
| Distinct message groups | **350** |

Reconciliation: 2,427 scanned = 350 emitted + 0 rejected + 0 skipped + 326
deduped + 0 held-out + 1,751 out_of_scope. **No silent loss.**

## DEDUP LAW (applied — the B6 discipline)

The template's dedup law collapses exact-duplicate `messages` rows to one row,
every collapsed occurrence recorded in the skip list. The 676 T rows contain
**350 distinct system/user/assistant groups**; 326 rows are exact duplicates of
an earlier row and were collapsed (the same file's T2 lane deduped 451 exact
duplicates in B6 — same discipline, applied here). Every dedup entry in
`skips_b4.jsonl` carries `duplicate_of_line` (the first source line of the
group) and `duplicate_count` (the occurrence index of the collapsed row, 2..22).
69 duplicate groups total; occurrence histogram: 2x:69 · 3x:32 · 4x:23 · 5x:20 ·
6x:20 · 7x:20 · 8x:19 · 9x:19 · 10x:18 · 11x:17 · 12x:14 · 13x:11 · 14x:10 ·
15x:8 · 16x:6 · 17x:6 · 18x:5 · 19x:5 · 20x:2 · 21x:1 · 22x:1. The largest
group (first seen at source line 910) has 22 identical occurrences.

## V-CHECK RESULTS (pasted validator output)

- **V1 PARSE**: `V1: PASS (350 lines, 0 failures)` — the written file re-read,
  every line `json.loads` cleanly, and every row re-passes V2/V3/V4/V5.
- **V2 SCHEMA**: PASS — every row has exactly the keys
  `[messages, bucket, sub_head, source]` in order, `bucket=="B4"`,
  `sub_head=="chunk-edit"`, and a 3-turn `system/user/assistant` `messages`
  array with non-empty string contents.
- **V3 NO TOKENIZER LITERALS**: PASS — 0 hits of `<|im_start|>`, `<|im_end|>`,
  `<think>`, `</think>`, `<start_of_turn>`, `<end_of_turn>`, `<bos>`, `<eos>`
  in any emitted line (source rows also carry 0; checked before emission).
- **V4 (ADAPTED — single bounded action)**: PASS — assistant content is
  non-empty, single-line, fence-free in all 350 rows (lengths 11–200 chars,
  median 64). B2's letter-closure rule does not apply to B4: rows end in an
  action, not a letter.
- **V5 PROVENANCE**: PASS — every row's `source` is
  `C:/Users/aaron/ham_n_eggs/war/train/corpus/loop-v16.jsonl:<line>` with the
  line within 1..2427; emitted lines span 676..2026 (the T-row region of the
  file).
- **V6 ACCOUNTING**: reconciles exactly (table above), totals also written to
  `b4_summary.json`.

## FILES

- `C:\Users\aaron\evo\state\gemma\submission\corpus\corpus_b4_chunks.jsonl` —
  350 rows, UTF-8, one JSON object per line, LF endings (249,714 bytes, no CR).
- `C:\Users\aaron\evo\state\gemma\submission\corpus\build_b4.py` — the builder.
- `C:\Users\aaron\evo\state\gemma\submission\corpus\skips_b4.jsonl` — 326 dedup
  entries (each with `duplicate_of_line` and `duplicate_count`).
- `C:\Users\aaron\evo\state\gemma\submission\corpus\b4_summary.json` — machine
  totals for this build.

## BOUNDARY / HONESTY ASSERTIONS

- `loop-v16.jsonl` was READ-ONLY: sha256 before and after the build is identical
  (`c9674600d597d4346e57c528bf50efb472a57cb993c100aa2788a06ba6fc68f0`).
- No sunny or ham_n_eggs file was modified. Every emitted row's content is
  verbatim source text; the only build-added fields are the
  `bucket`/`sub_head`/`source` tags.
- Note for the corpus report: these 350 rows are walker-side chunk-edit rows
  (one command per turn). The B4 bucket's file-edit side (B7's unified-diff
  hunks, 695 rows) is built separately; the two lanes share the executor head
  and the same Chunk Law.

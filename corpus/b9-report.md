# B9 GUARDRAILS BUILD REPORT — corpus_b9_guardrails.jsonl

Built 2026-11-13 by `build_b9.py` (order W-B.1 step 2, FINISH_PLAN.md lines 239-257).
Law executed: `gemma-template.md` rules a/d, the house V1-V6 pattern from `build_b6.py`
(V4 adapted), BUCKETS.md B9 ("situation where honest answer is 'not in the vocabulary /
not in the data' -> replan / ask / abstain"; "explicit abstain rows TO AUTHOR"), and the
Chunk Law failure modes (`C:/Users/aaron/evo/GLOSSARY.md` lines 51-61, owner ruling
2026-11-12). BOUNDARY LAW: reads `sunny\` and `evo\` READ-ONLY (stat'd before and after,
sha256 compared — all UNCHANGED); writes confined to `C:/Users/aaron/scullm/`.
HONESTY LAW: every count below is real from this run (source: `b9_summary.json`).

## 1. HEADLINE + ACCOUNTING

| Bucket | File | Emitted | Skipped | Rejected | Deduped | Out-of-scope |
|---|---|---|---|---|---|---|
| B9 GUARDRAILS | `corpus_b9_guardrails.jsonl` | **72** | 0 | 0 | 0 | 2,624 |

V6 accounting: scanned 2,696 = emitted 72 + skipped 0 + rejected 0 + deduped 0 +
out-of-scope 2,624 — **RECONCILES EXACTLY** (`b9_summary.json` field `reconciles: true`).
`skips_b9.jsonl` exists and is empty (0 entries): every candidate that entered a lane
passed validation, so there was nothing to record; the file is written for the record,
never laundered.

## 2. LANE E — the 52 empty-raw encode rows (source-grounded)

Source: `C:/Users/aaron/sunny/runs/decisions_corpus.jsonl` (READ-ONLY). The candidate
predicate is byte-identical to `build_b6.py`'s empty-raw skip predicate
(`not isinstance(raw, str) or not raw.strip()`) — the exact set that build's
`skips_b6.jsonl` flags as "B9 material". Cross-check is mechanical and passed:
**52/52 emitted rows match the 52 B9-flagged skip entries on (source, source_line)**
(`b9_summary.json` field `encode_lane_matches_b6_flags: true`). Recorded field values of
the 52 records (verbatim from the source records): 34 with status `error`, error_type
`other`, exit `n/a`, raw_chars 0, key_facts `["0 lines"]`; 14 with status `ok`,
error_type `none`, exit `0`, raw_chars 0, key_facts `["returned 0 chars"]`; 4 with status
`empty`, error_type `none`, exit `0`, raw_chars 0, key_facts `["raw_chars=0"]`.

Row shape: system = the guardrail system constant (below); user = a mechanical situation
sentence built ONLY from the record's own target fields (obs_id, status, error_type,
exit_code, raw_chars, key_facts) with LAW-LITERAL glue strings, e.g.
`obs o-0001 came back with status error, error_type other, exit code n/a, and 0 chars of
output text (0 lines).`; assistant = the grounded abstain, e.g.
`obs o-0001 is error with 0 chars of output: there is no content to read here. Report
that the output carried nothing; do not invent content; replan the step.` The abstain
verbs (report / do not invent / replan) are BUCKETS.md B9's own recorded behaviors
("replan / ask / abstain"). All 52 user contents are distinct (distinct obs_id).

## 3. LANE C — Chunk Law failure-mode abstain patterns (authored, law-grounded)

20 rows over 5 patterns. The failure modes are the Chunk Law's own list
(GLOSSARY.md lines 51-61); each pattern cites the law lines it is grounded in (V5
stat-checked), plus a second recorded source where the shipped harness itself restates
the law. Row `source_line` is an INT (house convention, as in the build_b2/build_b6
rows): the FIRST line of the cited range; the full range and the second source are
recorded in `b9_summary.json` (`chunk_lane_patterns`) and in the table below.
Situations are authored framings that name what the cited lines name — nothing beyond
them. assistant abstains are authored build constants (BUCKETS.md B9: "explicit abstain
rows TO AUTHOR"):

| Pattern | Rows | Grounded in (row source first) | Teaches |
|---|---|---|---|
| FM1 whole-file dump | 4 | GLOSSARY.md:53-54 + submission/prompts/system.md:6 | refuse whole-file writes; one bounded edit per turn |
| FM2 parallel edits | 4 | GLOSSARY.md:53-54 + submission/prompts/system.md:6 | one edit per turn, verify between edits |
| FM3 unverified "done" | 4 | GLOSSARY.md:60-61 + submission/prompts/system.md:5 | done = chunks completed + a real check passed |
| FM4 unbounded generation | 4 | GLOSSARY.md:58-59 + submission/prompts/system.md:14 | short verifiable spans, not one giant answer |
| FM5 unbounded plan | 4 | submission/skills/scullm-planning/SKILL.md:16 + GLOSSARY.md:56-57 | plans stay 5-12 nodes; grow by replanning, not front-loading |

System constant (authored; recorded here, not passed off as imported — motivated by
BUCKETS.md B9's own definition):
`"You are a grounded agent. If the answer is not in the provided material, or a tool
output is empty or failed, say so plainly and replan or ask. Never invent file contents,
command output, or facts."`
Type letter: `"G"` (guardrail). BUCKETS.md B9 records no type letter; this is a
documented build convention, first used in this build (`b9_summary.json` fields
`system_constant_provenance`, `type_letter_provenance`).

## 4. VALIDATION (V1-V6, house pattern from build_b6.py, V4 adapted)

- **V1 PARSE**: 72 lines re-read, re-parsed, and re-validated: 0 failures. PASS.
- **V2 SCHEMA**: exact key order `[bucket, type, source, source_line, messages]`;
  `bucket=="B9"`; `type=="G"`; 3 message objects with roles system/user/assistant and
  non-empty string contents; system content equals the registered constant. 0 failures
  at emit and on re-read.
- **V3 NO TOKENIZER LITERALS**: every emitted line serialized and scanned for all 8
  literals; source probes scanned pre-emit. 0 hits.
- **V4 ADAPTED (grounding proof)**: user and assistant content must EQUAL the lane's
  mechanically reconstructed expected strings (lane E: rebuild from the record's own
  fields; lane C: membership in the registered pattern constants), and the assistant
  must be 1-3 sentences (mechanical counter). Distribution: 1 sentence x4 (FM5), 2
  sentences x68. PASS.
- **V5 PROVENANCE**: every source stat-checked at build time; every source_line within
  the file's real line count (sunny 2,676; GLOSSARY.md, system.md, SKILL.md line counts
  taken from disk at run time — `b9_summary.json` field `source_lines`). 0 failures.
- **V6 ACCOUNTING**: reconciles exactly (section 1).
- **END-OF-TURN CHECK: NOT MEASURED — Gemma tokenizer not staged on this machine.**

## 5. PROVENANCE — sources stat'd READ-ONLY, all UNCHANGED after the build

| Path | Lines | Role |
|---|---|---|
| `C:/Users/aaron/sunny/runs/decisions_corpus.jsonl` | 2,676 | lane E source (READ-ONLY) |
| `C:/Users/aaron/evo/GLOSSARY.md` | 274 | Chunk Law lines 51-61 (READ-ONLY citation source) |
| `C:/Users/aaron/scullm/submission/prompts/system.md` | 14 | harness restatement of the chunk discipline, line 6 (READ-ONLY citation source) |
| `C:/Users/aaron/scullm/submission/skills/scullm-planning/SKILL.md` | 118 | bounded-plan law, line 16 (READ-ONLY citation source) |

(Line counts as recorded at build time — `b9_summary.json` field `source_lines`.)

All four stat'd (size + mtime + sha256) before reading and re-stat'd after the build:
all UNCHANGED (`b9_summary.json` field `read_only_assertions_unchanged`).

## 6. SCOPE NOTES (honest)

- The order scoped this build to the 52 flagged empty-raw rows + Chunk Law abstain
  patterns. BUCKETS.md B9 also mentions 403 raw error+empty encode rows and 125
  `judge` null-label rows as repurposable material: NOT taken here. The 273 error rows
  with non-empty raw were already admitted into B6 (`bucket-build-report.md` section 3:
  "error observations get grounded error summaries"); the rest is post-first-adapter
  material. Recorded, not silently dropped.
- Lane C rows are authored per BUCKETS.md B9's own instruction ("explicit abstain rows
  TO AUTHOR"); their situations cite the law lines that name each failure mode. No
  situation was invented that the cited lines do not name.
- This bucket serves ALL heads as an anti-hallucination layer; it is stretch-corpus for
  the post-first-adapter heads and does not touch the crow-head training set (the 370
  D rows of `corpus_decisions_gemma.jsonl`).

# B8 TOOL-NAV — build report (synthetic mint)

Built 1794490189 epoch by `build_b8.py`. Deliverables:
`corpus_b8_toolnav.jsonl` (60 rows) + this report.

## Honesty law

BUCKETS.md records B8 as **"0 — no source exists"**. Nothing on disk is a real
harness tool trace. Every row here is **HONEST MINTING**: derived from the
documented behavior of the 9-tool registry in
`C:\Users\aaron\evo\state\gemma\HARNESS_README.md` (§5.2 prompt rules and
environment caps, §6 the 9 tools with exact names/parameters, §6.1 free-vs-
counted budget semantics, §7.1 harness limits, §8.1/§8.2 patch mechanics and
protected files, §10 gotchas). Every row carries
`"source": "HARNESS_README §<sec> (synthetic-mint)"` — the synthetic-mint tag
is mandatory and present on all 60 rows. These rows teach documented
tool discipline; **they are not evidence of tool use**, and no transfer claim
is made from them.

## Counts (V6 accounting)

| metric | value |
|---|---|
| rows defined | 60 |
| rows emitted | 60 |
| rejected / deduped | 0 |
| written-file parse failures (V1) | 0 |
| V6 reconciles (defined == emitted + rejected) | True |

## Pattern breakdown

| pattern | rows |
|---|---|
| locate-first | 16 |
| budget-discipline | 14 |
| edit-discipline | 14 |
| gotcha-driven | 16 |

- **locate-first (16)** — the skill's own loop, one row per stage:
  `search_similar_code` (symbol query, prose rejection, truncation handling) →
  `get_code_neighbors` (callers/callees, edge_type filter, dotted-path
  resolution) → `get_code_subgraph` (shortlist, list/comma-string forms) →
  narrow `read_file` (line-range slice, truncated-read continuation), plus
  stop-locating discipline and the no-graph-data fallback.
- **budget-discipline (14)** — `get_status` (FREE) at phase boundaries; the
  `budget_warning` field (<= 10 remaining) → finalize behavior;
  `submit_patch` not counted and callable at zero; time-budget awareness;
  TimeoutExceeded recovery; batching compound commands; nudge mechanics (§5.3).
- **edit-discipline (14)** — read the exact region then minimal old/new
  anchors; uniqueness + allow_multiple; 3-tier matching verification; whole-
  file `write_file` rejection; payload-size truncation avoidance; typed
  arguments; workspace-relative paths; targeted verification runs.
- **gotcha-driven (16)** — scratch scripts in /tmp (git add -N sweep);
  cleanup before submit; never touch pytest.ini/conftest.py (§8.2 reset);
  protected test files; submit_patch LAST; diff preview before the
  irreversible submit; offline/no-network environment; new-file placement;
  git-excluded artifacts; targeted pytest; output shaping; CommandError
  recovery; the closing sequence.

## Tool coverage (rows teaching each §6 registry tool)

| tool | rows |
|---|---|
| `run_command` | 16 |
| `submit_patch` | 15 |
| `get_status` | 8 |
| `read_file` | 11 |
| `edit_file` | 24 |
| `write_file` | 6 |
| `get_code_neighbors` | 6 |
| `search_similar_code` | 8 |
| `get_code_subgraph` | 6 |

All 9 registry names are the exact §6 strings; every row mentions at least one
registry tool (enforced), and no non-registry tool name appears anywhere.

## Validation

- **V1 PARSE** — written file re-read; every line `json.loads` cleanly
  (0 failures).
- **V2 SCHEMA** — exactly keys `messages, bucket, sub_head, source`; 3 messages
  in roles system/user/assistant; one-line system law; non-empty contents;
  bucket `B8`; sub_head `tool-nav`; source matches
  `HARNESS_README §<sec> (synthetic-mint)`.
- **V3 NO TOKENIZER LITERALS** — superset ban list enforced per line: the 8
  template literals (`<|im_start|>`, `<|im_end|>`, `<think>`, `</think>`,
  `<start_of_turn>`, `<end_of_turn>`, `<bos>`, `<eos>`) plus the harness
  channel/tool-call markers (`<|tool_call`, `<|channel`, `<channel|>`).
- **TOOL-NAME CLOSURE** — every snake_case token in a serialized row must be a
  §6 registry name or explicitly allowlisted non-tool vocabulary (JSON response
  fields, error types, example symbols, spec vocabulary):
  agent_patch, allow_multiple, budget_warning, consecutive_nudges, count_tool_call, edge_type, end_line, error_type, eval_baseline, exit_code, is_truncated, max_output_tokens, max_tool_calls, network_mode, new_string, node_name, old_string, parse_header, patch_submitted, pytest_cache, read_response, remaining_tool_calls, start_line, test_parse, test_patch, time_seconds_remaining, tool_calls, tool_calls_remaining, tool_calls_used, total_lines.
  CamelCase identifiers (TimeoutExceeded, BadHeader) are outside the scan by
  design; the registry names are snake_case, so any snake_case hallucinated
  tool name would fail the build.
- **V5 PROVENANCE** — `HARNESS_README.md` stat-ed at build time
  (55940 bytes, READ-ONLY); every cited §id is checked against
  its actual header text in the file, so no row cites a section that does not
  exist.
- **V6 ACCOUNTING** — rows defined = emitted + rejected/deduped, exactly.

## Boundary law

Reads: `state/gemma/HARNESS_README.md` (READ-ONLY). Writes: `build_b8.py`,
`corpus_b8_toolnav.jsonl`, `b8-report.md` — all inside
`C:\Users\aaron\evo\`. Nothing outside `evo` was modified.

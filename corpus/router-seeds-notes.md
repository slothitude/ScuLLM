# router-seeds-notes.md — extraction table and coverage notes

Source: `C:\Users\aaron\ham_n_eggs\tools\moed.py` (READ-ONLY — copied, never edited; boundary law).
Cross-checked against `C:\Users\aaron\evo\school\MOE_HEADS_METHOD.md` §2.2 (routing flow, preserved description, moed.py:74-95).

Corpus: `router-seeds.jsonl` — 24 rows, Gemma chat MESSAGE form (system/user/assistant).
The trainer's tokenizer applies the chat template; no `<start_of_turn>` markers are embedded.

## Row form (consensus v4 — after three rounds of openrouter + nvapi lane reviews)

This is a **router-classification corpus**, not a chat corpus: the assistant target
teaches the Gemma router head to emit the routing decision for the conversation.
It is therefore intentional that the assistant content is a route label, not an
answer to the user turn. Label format: `"<resolved-expert> - <desc>"` —

- `<resolved-expert>` is one of `walker-red | walker-blue | planner-red | planner-blue | coder | rag | base`
  — exactly the namespace `EXPERT_IDS` uses (moed.py:64-71); parse rule is "split on
  the first ` - `". Seat is resolved in the label itself (no "seat auto-detected").
- `<desc>` is the moed.py route description, cleaned: NO parenthetical asides of any
  kind — no signature tags, no trigger-word restatements, no "(no adapter)", no
  "seat auto-detected", no placeholder/training-status comments — and lowercased
  uniformly (acronyms like OFL kept).
- System prompts carry the routing triggers verbatim from the moed.py signatures;
  user turns are strictly neutral prompt dressing — no routing-rule restatement, no
  meta-questions, no seat words — so the router learns system-prompt → route with
  zero label leakage in the user turn.
- Rows from one tuple that share a resolved expert share identical labels by design
  (distinct trigger prompts, same routing outcome): rows 07-10 all read
  `walker-blue - state-aware walking`, rows 11-12 `planner-red - red OFL planning`,
  rows 14-16 `planner-blue - blue planning`, rows 18-19 `coder - stdlib Python
  scripts`, rows 21-22 `base - world model`. The extraction table below maps each
  row to its matched signature.
- The blue-placeholder serving fact (planner-blue/walker-blue ride red lora ids
  until blue trains, moed.py:64-71, comment "placeholder: blue walker head not
  trained yet") and the R1b precedence provenance (comment 76-80) are recorded
  HERE, not in labels or source fields.
- `source` fields are clean `file:line` provenance strings; the full source file
  for verification is `C:\Users\aaron\ham_n_eggs\tools\moed.py` (read-only).

## Extraction table (rule → source line → rows → resolved expert)

| # | Rule | moed.py source | Resolved expert | Rows |
|---|------|----------------|-----------------|------|
| R1a | Rag preempt: any system prompt containing `search results` (case-insensitive) → rag | 81-82 | rag | 1 |
| R1b | Rag preempt beats persona signatures (comment: "personas must not outrank the material", moed.py:76-80) — prompt carries Omni-Flow persona AND SEARCH RESULTS | 81-82 | rag | 1 |
| R2 | No/empty system prompt → base | 83-84 | base | 1 |
| R3a | Walker seat detection, red outcome: `red` / `ham{` / `exploit` / `flag` in prompt → walker-red | 86-88 | walker-red | 1 |
| R3b | Walker seat detection, blue default: none of those words → walker-blue | 86-88 | walker-blue | 1 |
| R4 | No ROUTES signature matches → base ("unrecognized") | 95 | base | 1 |
| T1 | Walker identity: `TEV1` / `decision model walking` / `YOUR JUMP` (one row per signature; seat-neutral prompt text → walker-blue per 86-88) | 43 | walker-blue | 3 |
| T1p | Walker-identity precedence demo: TEV1 prompt that also carries `watch the boxes` / `rotate on confident` still routes walker, because walker is matched before planner/seat words ("blue objectives contain 'watch'/'rotate'"); seat-neutral text → walker-blue | 41-43 | walker-blue | 1 |
| T2 | `planner for a red or blue` / `capture both ham` → planner-red (one row per signature) | 45 | planner-red | 2 |
| T3 | `Omni-Flow plan generator` → planner-red | 46 | planner-red | 1 |
| T4 | `blue` / `watch the boxes` / `rotate on confident` → planner-blue (one row per signature) | 47 | planner-blue | 3 |
| T5 | `Mermaid diagram` → planner-red | 48 | planner-red | 1 |
| T6 | `write tiny python scripts` / `Write a minimal stdlib-only Python3 script` → coder (one row per signature) | 50 | coder | 2 |
| T7 | `SEARCH RESULTS` in the ROUTES table → rag | 52 | rag | 1 |
| T8 | `TASK: forward-dynamics` → base (world model) | 54 | base | 1 |
| T9 | `TASK: inverse-dynamics` → base (world model) | 55 | base | 1 |
| T10 | `TASK: masked-jump` → walker (trajectory prediction; seat-neutral → walker-blue per 86-88, 92-93) | 56 | walker-blue | 1 |
| T11 | `TASK: state-contrastive` → walker (state discrimination; seat-neutral → walker-blue per 86-88, 92-93) | 57 | walker-blue | 1 |

Total: 24 rows. All 11 ROUTES tuples (moed.py:40-58) and all 4 route()-level behaviors (moed.py:81-95) are covered; multi-signature tuples are expanded one row per distinct signature (each signature is an independently matched condition in the table walk at moed.py:89-94), which is why rule T1 → 3 rows, T2 → 2, T4 → 3, T6 → 2. Several rows share a resolved expert and therefore an identical label (T1's four rows, T4's three, T2's pair, T6's pair, T8/T9's pair): that is intentional — distinct trigger prompts, same routing outcome.

## Semantics preserved from the source (and encoded in the rows)

- Matching is case-insensitive throughout: `low = system_prompt.lower()` then `sig.lower() in low` (moed.py:85, 91). Signature text in the rows appears verbatim from the source.
- Evaluation order is load-bearing: rag preempt first (81), then empty-prompt (83), then seat detection (86-88), then the ROUTES table in tuple order (89-94), then fallback (95). Row 02 (R1b) and row 10 (T1p) exist specifically to teach the two stated precedence facts (comments at 76-80 and 41-43); the precedence lesson is encoded in the row OUTCOMES (row 02 routes rag, row 10 routes walker-blue), not restated in the user turn.
- Seat resolution applies to EVERY walker-family row, including `TASK: masked-jump` / `TASK: state-contrastive` (`if expert == "walker"` at moed.py:92-93). Rows 07-10, 23-24 carry seat-neutral prompt text, so they resolve walker-blue at serving time; the labels carry that resolved seat directly (`walker-blue - ...`).
- Blue heads are placeholders: `walker-blue` and `planner-blue` map to lora ids 0 / 1, i.e. the red heads serve until blue trains (moed.py:64-71, comment "placeholder: blue walker head not trained yet"). This fact lives in these notes; the training labels stay clean route decisions.
- EXPERT_IDS load order (context for the trainer, not a routing rule): 0=walker, 1=planner, 2=coder, 3=rag (moed.py:64-71; confirmed in MOE_HEADS_METHOD.md §2.2 point on EXPERT_IDS).

## Ambiguities flagged

1. `blue` as a bare signature (moed.py:47) is very broad — any prompt merely containing the word "blue" routes planner-blue if no earlier rule fires. Row 14 is sourced and correct, but the trigger is a single common word; a Gemma router trained on this will over-fire planner on incidental "blue" mentions. (Note: the harness's actual blue SYS prompts use the full vocabulary, so at serving time it is fine; for a general router this rule is the weakest of the set.)
2. T7 (`SEARCH RESULTS` in ROUTES, moed.py:52) is dead code in the chat path: route() preempts on the same token at moed.py:81 before the table is ever walked. Row 20 is kept for table coverage; it should not be read as a second, distinct rag rule.
3. R2 vs R4 produce the same outcome (base) from different branches — rows 03 and 06 look near-duplicate but encode different conditions (no system prompt at all vs an unmatched system prompt).
4. T2's first signature is literally "planner for a red or blue" yet the tuple's assigned expert is planner-red (moed.py:45). That red outcome IS the source's rule, not a default guess. Row 11's user turn is deliberately seat-neutral, so the row can look odd to a human reader (prompt mentions blue, label says red) — the oddity belongs to moed's own table, not to the row; the signature stays verbatim in the system prompt, where moed does its matching.
5. Row 02 (R1b) and row 13 (T3) both contain the phrase "Omni-Flow plan generator" in the system prompt but route differently (rag vs planner-red). That is the R1b precedence demo working as designed: route() checks the "search results" token FIRST (moed.py:81), and row 02's system prompt additionally carries a SEARCH RESULTS block, which is the deciding marker; row 13's does not. The mapping is conditioned on the extra material, so there is no conflicting signature — this is exactly the precedence fact the row exists to teach.

## Serving-path divergences reported, NOT covered by rows (boundary law: reported, not fixed)

- `/v1/completions` (`proxy_completions`, moed.py:165-186) routes on the raw prompt prefix with the same ROUTES table but WITHOUT the rag preempt, seat detection, empty-prompt rule, or fallback desc. Its walker rows return the literal expert name `"walker"`, which is not a key in `EXPERT_IDS` (moed.py:64-71) — so on that path a walker-signature completion gets no lora field and rides the bare base. The corpus is chat-shaped (router head trains on chat routing), so none of this is encoded as rows; recorded here as a source-project observation only.
- The no-think pin (`chat_template_kwargs {"enable_thinking": False}`, moed.py:149-152) and the lora-id injection (`body["lora"] = [{"id": N}]`, moed.py:139-148) are serving mechanics, not routing knowledge — intentionally not seed rows.

## What is NOT covered (the gap for the C1 corpus)

moed's table knows four situations: walking a decision tree, emitting an OFL/mermaid plan, stdlib-python code_task nodes, and search-grounded planning. It has NO rules for software-engineering situations — repo triage, bug reproduction, test-failure triage, PR review, dependency upgrades, refactors, CI-greening. The only code-adjacent rule is the coder pair ("write tiny python scripts" / "Write a minimal stdlib-only Python3 script", moed.py:50), which targets harness `code_task` nodes, not SWE work; the coder head therefore gets only two seed rows here. There are likewise no rules for tool-calling, multimodal input, safety/escalation, or memory-bearing conversations, and this corpus carries no negative/ambiguous examples (e.g. a walker-signature prompt asking for an essay) or multi-turn conversations. All of that space is uncovered by this corpus and is the C1 corpus's job to fill — it is deferred there on purpose, not overlooked here. No unsourced rows were invented to close these gaps (honesty law).

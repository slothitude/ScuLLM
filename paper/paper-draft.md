# Harness Discipline Before Weights

*Subtitle: Mechanical Verdict Laws for a Small Coding Agent, with a Staged Gemma 4 E2B LoRA Path*

Kaggle Gemma 4 Developer Agent Competition, main track

SlothitudeGames


## Abstract

Small-model coding agents are usually improved by changing weights first; on one agent we changed the harness first. Its contribution is a disciplined process and a staged plan: no Gemma result and no competition score are claimed or predicted. The protocol allowed one mechanical law per failing verdict — a code-side check, gate, or cap — version-bumped, suite-tested, and relaunched, with no training between changes; the documented exception is the planner check-authoring seat, whose bundled prompt-fix rounds all failed and became a mechanical veto. The agent produced eight consecutive scaffold-checked artifacts (attempts 16-22 plus the g03b run series) on the Qwen 3.5 harness — a local surrogate stack; the declared Gemma 4 E2B base has not been evaluated end to end. This is evidence of process discipline in our own scaffold, not of task success: the checks are ours, were not ablated, and were not run against held-out repository tasks. Each turn was logged with its decision owner, option probabilities, and judge ground truth, growing a labeled decision set from 38 to 1,014 rows beside a 140-row holdout never trained. A per-role LoRA trainer is written and dry-run verified on the Qwen 3.5 0.8B base (encode-and-mask check, exit 0, no training step run), with correct completion-only masking; no Gemma 4 E2B adapter has been trained or shipped. The shipping rule is stated before the adapter is trained: an adapter is submitted only if it beats the prompt-only baseline on a local split. We report one small plan-then-execute trace as system measurements only.

## Introduction

The competition frame is narrow, and we exploit the narrowness. A submission is declarative-only: no competitor Python reaches the harness, the host compiler interprets our YAML into its agent classes, every seat is served by one declared Gemma base, and per-role LoRA adapters may differ while the base stays fixed [4]. Grading is code-owned end to end: a task resolves only when the repository's test suite exits clean under the harness's hermetic pytest pass [4]. A harness that already routes verdicts through code is aligned with how the benchmark grades, so that is where we spent effort first — discipline preceding adapter training, since the traces that became the corpus were produced under those laws. One published approach distills a frontier teacher's trajectories into a small-model Gemma base [4]; ours distills the agent's own recorded decisions.

Our system is a plan-then-execute decision duo steering a coder seat under exactly such a loop. The planner formulates one lettered question about the current state; the executor answers exactly one letter, from a peaked letter distribution that doubles as a confidence signal; the full decision economics are in Table 1 (Measured Results) [2]. Between decisions the plan artifact is OFL, a line-based, byte-exact plan language (Architecture); we call the design contract it implements SCULLM (Related Works). The planned root is the coder seat carrying these laws; the duo is kept as the alternative tree under `variants/`, and the planned local comparison decides which root ships.

The lineage behind the thesis is the part we did not have to invent: the change log for the longest clean streak records harness-law versions and no training event [1], and the seat that resisted three prompt-fix rounds is the case for mechanical fixes over prompt tuning. The paper proceeds from the declarative architecture, through the training-free scaffold improvements and training method, to measured results, related works, and limitations with the staged submission path.

## Architecture

The planned entry is a declarative tree, not a program. The planned root is a single `LlmAgent` coder seat on `gemma-4-e2b-it-qat-w4a16-ct` — one of the four names on the harness's allowlist, under the harness's single-base rule [4, 5] — declaring the workspace tools plus the two free lifecycle tools, and an executor LoRA adapter in `adapters/` in PEFT directory form, which the host's serving layer discovers and right-sizes automatically [4, 5]. A read-only `code_analyzer` sub-agent is wrapped as an `AgentTool` with `skip_summarization: true`, keeping its bulk dumps out of the coder's context — the harness's documented isolation pattern for delegated code search [4, 5]. An optional plan-then-execute variant — a `SequentialAgent` chaining planner then executor inside a `LoopAgent`, bounded by the harness ceiling of 500 iterations — is kept under `variants/` for the local A/B [4, 5]. `eval_config.yaml` requests the harness-default budgets: 60 minutes, 100 tool calls, 500 turns [4, 5].

The host compiler embodies the same thesis our own engines run on: the model authors declarations, a deterministic engine interprets them, and code owns the verdicts. Competitors submit no Python entrypoint at all; the sandboxed compiler resolves every agent, tool, and generation parameter against closed registries [4, 5]. We exploit the budget asymmetry the harness grants: `submit_patch` and `get_status` are free, outside the tool-call budget, and the loop terminates the moment a turn ends with the patch submitted [4, 5]. That becomes our prompt law: verify first, clean scratch out of the workspace, and call `submit_patch` last.

The decision cascade beneath the planned coder is ordered cheap first, expensive last: a deterministic script or guard answers when it can, Monte-Carlo structure search when the script cannot, a few-shot letter decision when structure is ambiguous, a replan when everything above has failed. The plan-then-execute duo is that letter layer.

The plan artifact is OFL, our structured plan language: no shapes, no decoration, one quoting rule — what the model emits is what the parser reads, byte for byte. `loop N` visit budgets and edge guards such as `[obs~PATTERN]` and `[need NAME]` live IN the plan file itself — cycles are written, not guessed — and the reference parser preserves them across the canonical roundtrip `parse(emit(parse(f))) == parse(f)` [7]. Mermaid is a one-way view, never parsed back. Because the artifact the trainer sees is the artifact the interpreter walks, the adapter can never learn a format the harness will not read.

## The Training-Free Scaffold Improvements

The strongest claim this project makes is not a benchmark score; it is how improvement happened. The eight — attempt 16 (checker=PASS, 18/18), then the g03b run series (the progress log's g03b era, seeded from attempt 16's passing sandbox), then attempts 17 through 22 — are consecutive scaffold-checked artifacts on the Qwen 3.5 surrogate harness (not the declared base), each checker=PASS, the scaffold's own gates green [1]. The logs are specific about the endpoint: attempt 22 (sun-222018) is recorded verbatim as "ask_human 0/4, wall 1384s, checker=PASS — EIGHTH consecutive artifact-passing run; the failing check is verbatim the same impossible expectation" [1]. Two labels share that line: checker=PASS is the scaffold's gate verdict; the "failing check" is the planner-authored check with an impossible expectation — the one that survived all three prompt-fix rounds [1]. The evidence file inventories every change in that window and finds only harness law versions — among them w3.1, w3.3, pl1.11, pl1.14, the w3.5-w3.9 zone, cd1.6, ex1.0 — with no training event [1].

Every failing verdict gets one mechanical law, except the planner check-authoring seat; each change is version-bumped, suite-tested, and relaunched, with no training between changes. The representative laws: w3.3, a stale-check detector; pl1.11, the vacuous-replan cap, landed after a forced replan bypassed its bound; w3.9, truth-bearing judge rows that log the judge option set (later the enabler of an answerable training feed); w3.10, under which an empty-edits reply on a failed check is the coder asserting the code already satisfies the files, triggering a miscalibration-flagged replan — evidenced by 13 empty-edits calls in attempt 21; cd1.6, the coder brief opening with the literal ISSUE EXPECTED/GOT delta line; and ex1.0, a describe-only explainer that replaces diagnosis with pointers [1].

The honest negative result carries the argument. Planner check-authoring resisted all three prompt-fix rounds — pl1.10, then pl1.12 alongside the w3.3 stale-check detector, then pl1.13 plus pl1.14 — and the same impossible expectation survived each run; the recorded conclusion was that the next fix must be MECHANICAL, a check-grounding veto at plan acceptance. A mechanical veto was landed (pl1.15); its effect is unmeasured. Prompt tuning failed where a mechanical gate was needed; that asymmetry is the thesis.

We have no competition score; nothing here predicts one. In our trace verification is done only by a checker, a baseline git checkpoint is committed before any edit, and replans and ladders are bounded by caps.

## Training Method

The recipe is measured, and it is not yet a Gemma recipe. On the Qwen 3.5 0.8B lane the executor trainer is dry-run verified: LoRA r=8 with alpha 16 and dropout 0 applied to all linear projections, learning rate 5e-5 on a cosine schedule, one epoch, effective batch 8 (micro batch 2 times gradient accumulation 4), block packing, and completion-only masking — prompt tokens are labeled -100 so the only unmasked targets are the answer letter plus the `<|im_end|>` token [3]. A proven 4B decider lane sits alongside it (QLoRA, r=16, on Qwen 3.5 4B) [3]. The masking was verified mechanically on the same lane — three corpus-shaped rows encoded to 104/95/106 token ids with 102/93/104 prompt labels set to -100 [3]. The dry run is the trainer's --dry-run pass — encode, masking, loader checks, exit 0, no training step.

Training uses only agent trajectories: rows come from the agent's recorded traces — decision rows with judge ground truth and option probabilities — plus self-authored tasks [1, 3]. A correction we keep: distillation v1's dedup key collapsed the corpus and produced zero answerable rows; v2 carried turn and probabilities in the key and made the feed answerable [1]. The feed now holds 1,014 labeled decision rows, up from 38; the file-level corpus and holdout are reported in Measured Results [3].

Per-role adapters are the natural shape under this harness. We declare one base, gemma-4-e2b-it-qat-w4a16-ct; the harness guide allows different agents to carry different LoRA adapters, with max_lora_rank <= 128 and the whole unpacked submission under 3 GiB [4, 5]; the planned adapters would use r8-r16, and the evidence's size table puts a rank-16 adapter near 110-220 MB [4]. The planned seat split follows the interference law — one LoRA cannot hold two vocabularies: the executor carries the decider-letter vocabulary, the planner carries question formulation, and the coder's laws are distilled into prompts and skills rather than a third adapter.

The Gemma lane is staged, not yet run; no Gemma training number exists in the evidence pack. The 2026-11-12 GGUF q4_0 footprint benchmark measured 1.7 GB VRAM, 28 percent of our 6 GB card [6] — a different artifact, and not a measure of the declared w4a16 compressed-tensors checkpoint. Unsloth support for the gemma4 architecture is unverified for both sizes — the sources record native unsloth patching only for Qwen3_5 [3]. The decision rule is stated before the adapter is trained: the prompt-only tree ships, and the executor adapter replaces it only if it beats the prompt-only baseline on our local split.

## Measured Results

Every number here comes from our own plan-then-execute trace or our own 6 GB-card scaffold measurements; none is a benchmark claim.

**Table 1 — decision economics of the duo** (trace: 12 rows, three tasks one turn each; source [2]):

| pass | role | n | mean latency (ms) | decided_by |
|---|---|---|---|---|
| planner | formulates one lettered question | 3 | 12,158 | model |
| executor | answers one letter | 3 | 4,620 | model |
| execute | runs the decided step | 3 | 8,387 | code |
| check | code-side verdict | 3 | 0 (zero wall cost) | code |

The executor is the cheapest model call in the loop: on the example row it answers letter A from a peaked distribution with top logprob -0.29 — the decision split the planned cascade is built on [2].

**Table 2 — the plan-then-execute scaffold on the 6 GB card** (source [2]):

| fact | measured value |
|---|---|
| warm decision (LoRA adapter, CPU-loaded, qwen38 co-resident) | 0.70 s |
| big-prompt proof | 11,836-token prompt answered in 9.1 s |
| VRAM | 5,278/6,144 MiB |
| honest big-prompt cap | ~10,000 tokens |
| encoder throughput (walker-duo encoder, CPU-loaded, qwen38 co-resident) | 4.2-5.2 tok/s |

Short calls ran 0.62-0.71 s [2].

The calibration finding is the central lesson. On the v2b floor run (run n01), the untrained 4B escalated its call_coder probability 0.15 -> 0.82 while watching its own failures, and still could not use that evidence in-context [2]. Zero-shot confidence is not evidence-use in this single run; the w3.x harness laws are our candidate curriculum for it.

The routing gate follows: decisions below the confidence threshold would escalate to a stronger seat, since confidence must be earned through the laws, not asserted by the model. We have not measured this gate's accuracy per confidence band; it is planned to ship on the calibration lesson, not a measured curve.

The corpus economics are the payoff of logging the loop: decision rows grew from 38 to 1,014, shipping runs/decisions_corpus.jsonl (2,676 rows) beside runs/decisions_holdout.jsonl (140 rows, never trained) [3, 10].

End-to-end toy runs: B0 passed in 6 turns (1,963 tok, 92 s); B1 passed at 1,368 tok, 58 s [2].

The competition metric (resolution rate on held-out SWE tasks) is reported only from scored submissions, not extrapolated from anything in this section.

## Related Works and Citations

The scripted-adventure lineage predates agents. SCUMM (1987) let game designers script entire adventures without writing C, and Loom (1990) abandoned the verb interface for a closed four-note grammar interpreted by an engine. The same proposal/execution principle appeared in the author's own Scumm_L engine, recorded as "Godot is the authority. The LLM proposes state changes; Godot validates before applying." [9]. Prior engines kept authorship with humans or let the LLM only propose mutations inside human-authored structures; SCULLM — Script Creation Utility for LLMs, our backronym — is distinct in its model authorship: the small model writes, in the closed DSL, the executable program it walks.

OFL [7] is the structured plan language, and the SCULLM contract note [8] states the design contract — closed vocabulary, validator with bounded repairs, byte-identical compile, gates on declaration and interpreter — that Architecture implements.

On the competition side, our engineering constraints — the model registry, single-base rule, adapter serving, truncation note — come from the competition's harness guide, not the Rules tabs, and we cite them as harness-document facts [5]. Discussion thread #751596 records entrants' LoRAs failing to beat prompt-only baselines on this competition [4] — the failure mode our shipping gate is built against (Training Method, Limitations).

**Sources**

[1] evidence-walker-lineage.md — recorded lineage of attempts 16-22 and the g03b run series.
[2] evidence-latency.md — plan-then-execute trace and 6 GB-card measurements.
[3] evidence-corpus-training.md — corpus build and trainer dry-run record.
[4] evidence-competition-facts.md — competition rules, model registry, field intel.
[5] Kaggle Gemma 4 Developer Agent competition harness guide (HARNESS_README), dated 2026-10-13, pulled 2026-11-12 from kaggle.com/competitions/gemma-4-developer-agent — model registry, single-base rule, adapter serving, truncation note.
[6] Local E2B QAT benchmark log, 2026-11-12; 1.7 GB VRAM footprint on the GGUF q4_0 build (reviewers on request).
[7] OFL.md and ofl.py — the structured plan language and its reference parser.
[8] scullm-research.md — SCULLM contract research note.
[9] Scumm_L — the author's LLM-proposes, Godot-validates engine (MIT).
[10] corpus/BUCKETS.md, built 2026-11-12 — disk-measured counts (wc -l, decomposition receipts); supersedes the corpus counts in [3].

Items 1-4, 6, and 10 are internal records, available to reviewers on request.

## Limitations and Staged Path

Our measurements are taken on our own task suite and harness, not on SWE-bench; the scaffold improvements are evidence produced by our own checkers [1], a discipline result, not the competition metric. The Gemma E2B training lane is staged as described in Training Method. E4B (gemma-4-e4b-it-qat-w4a16-ct, the larger allowlisted variant) is untested on our lane; if E2B underperforms it stays available as an alternative base, under the same single-base rule.

A second caveat we state plainly: the scaffold lineage and the decision corpus were gathered on the Qwen 3.5 harness — the 0.8B two-pass harness and the 4B walker lane — a different model family from the declared base. The declared base has never been run end to end in our stack, and we hypothesize that the corpus transfers across model families.

Risk one: the field's LoRA failure mode (thread #751596, Related Works) [4]. Mitigation: the executor LoRA ships only if it beats the prompt-only baseline on our local holdout split (rows never trained on); otherwise the prompt-only tree ships.

Risk two: token truncation on big edits — a large thought block followed by a large edit payload can cut the tool-call tag before it closes [4, 5]. Mitigation: incremental edit_file payloads, one focused change per call, with a bounded thinking budget.

Risk three: protected-file tampering — the harness strips hunks touching protected test files and runner configuration, force-resetting those paths before Phase 2 verification [4]. Mitigation: our prompt law treats test files and the harness's own pytest.ini and conftest.py as untouchable, and keeps scratch scripts in /tmp, never /workspace.

Risk four: cadence — the main track allows one submission per day [4]. Mitigation: bank one scored submission every day from the first minimal passing skeleton; a day without one is a lost datapoint, and final selection draws on the banked runs.

Staged submission path. The planned order stages the prompt-only tree first on gemma-4-e2b-it-qat-w4a16-ct, with the plan-then-execute variant kept as the alternative tree and the executor LoRA second; no submission has been made and no competition result is claimed or predicted. On each submission day the tree with the better local split performance would go out, subject to the LoRA shipping rule stated before the adapter is trained.

Finally, the self-built law: competitive entries are made by the agent itself — trained on its own recorded trajectories — never by a borrowed frontier brain; every law and corpus row here was produced by the agent's own runs.

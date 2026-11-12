# SCULLM — Script Creation Utility for LLMs

**Harness discipline before weights.** On one small coding agent, we changed the harness
first — and wrote down, as executable law, exactly why.

SCULLM is our entry in the Kaggle *Gemma 4 Developer Agent* competition. It is a
declarative agent bundle — one coder seat, nine tools, a planning skill with mechanical
verdict gates — plus the measured, honest record of how it was built: every number in this
repository traces to a file, every metric carries its source, and anything not measured is
written `NOT MEASURED`, never guessed.

---

## The thesis in one paragraph

Small-model coding agents are usually improved by changing weights first. We inverted the
order: the agent's contribution is a disciplined *process* — one mechanical law per failing
verdict, version-bumped, suite-tested, and relaunched, with no training between changes —
and a *staged plan*: no Gemma result and no competition score are claimed or predicted.
What the process produced on the local surrogate stack is measurable (below); what it
will produce on the declared Gemma 4 E2B base is deliberately an open question, gated by
pre-registered exams rather than optimism.

## What is actually here

| Layer | Artifact | Receipt |
|---|---|---|
| Declarative bundle | `agent.yaml` — one `LlmAgent` coder seat on `gemma-4-e2b-it-qat-w4a16-ct`, single-base law, nine tools, budgets 60 min / 100 tool calls / 500 turns | `compile_submission: PASSED` (official wheels) |
| Planning skill | `skills/scullm-planning/` — write → check → walk plan language (OFL), byte-exact roundtrip `parse(emit(parse(f))) == parse(f)` | `scullm_check.py`, adversarially tested (17-case battery) |
| Delegated code search | `sub_agents/code_analyzer.yaml` — read-only `AgentTool`, `skip_summarization: true`, bulk dumps kept out of the coder's context | harness-documented isolation pattern |
| Trainer | `tools/train_crow_gemma.py` — LoRA r16 / alpha 16, seven projections, completion-only masking (unmasked = the letter + `<turn|>`), house recipe | dry-run verified: arch + masking OK; 2 trainer bugs found, fixed, independently audited (`tools/fix-audit/`) |
| Validator | `tools/validate_submission.py` — hygiene (extension allowlist, no corpus/), single-base law, official `validate_directory` + `compile_submission` | self-tested both ways: PASS on the clean bundle, FAIL on a poisoned copy |
| Corpus | `corpus/` — **3,626 rows across 13 buckets** | `corpus/COMPLETION-AUDIT.md` — every count re-verified by `wc -l`, D-rows by JSON parse |
| Training plan | `training/` — T4 runbook, preflight (GO pending owner session), upload manifest | fit wall: NOT MEASURED (first real sec/step lands at the owner's session) |
| The paper | `paper/paper-draft.md` + `paper/paper-draft.pdf` — 2,998 words, submitted on the paper track | dual-lane consensus review, 5 rounds; gate G1: AGREE-PASS |

## The corpus, honestly

The training set for the first adapter ("crow head") is **370 decision rows, all verified
`type: D`** — logged from real agent turns, each carrying its decision owner, option
probabilities, and judge ground truth. Around it sit the supporting buckets:

- **B6 signals** 1,239 · **B7 SWE-edits** 695 · **B4 chunk-edits** 350 · **B11 FreeCAD** 366
  · **B12 Godot** 80 · **B8 tool-nav** 60 · **B9 guardrails** 72 (built from source-flagged
  abstain patterns) · **B1 router seeds** 152 (expanded from recorded sources only)
- B3 and B5 are explicitly **out of scope** for the first adapter, with reasons written down.
- Every rejected candidate has a skip-list entry with a reason. Nothing was invented to
  fill a bucket. `corpus/BUCKETS.md` is the law; `COMPLETION-AUDIT.md` is the audit.

## The laws (the actual contribution)

1. **The Chunk Law** — one bounded action per turn. Every corpus row, every plan step,
   every tool call obeys it; the guardrail bucket (B9) exists because we catalogued its
   failure modes.
2. **Intent-Driven Code** — every artifact derives from a stated intent; plans are written
   before code, and the plan language is the contract.
3. **Honesty law** — verdict lines match evidence; unverified rows never ship; cutting
   beats fudging. `NOT MEASURED` is a first-class value in this repository.
4. **Dual-lane consensus** — every judgment call was reviewed by two independent model
   lanes with an arbiter on evidence; every gate closes only on AGREE-PASS.

## Architecture (30 seconds)

```
agent.yaml (declarative tree, no Python entrypoint — the host compiler resolves it)
└── coder seat  gemma-4-e2b-it-qat-w4a16-ct      ← single-base law
    ├── 9 workspace tools (+2 free lifecycle: submit_patch, get_status)
    ├── sub_agent: code_analyzer (read-only, summarization off)
    └── skills: scullm-planning (write→check→walk, mechanical verdicts)
                repo-navigation
adapter: (commented — ships prompt-only until the pre-registered gate says otherwise)
```

The competition harness compiles this bundle in its sandbox; we exploit its budget
asymmetry — `submit_patch` and `get_status` are free — so the prompt law becomes:
verify first, keep the workspace clean, submit the patch last.

## Training plan and the gates that guard it

The trainer is written, dry-run verified (arch support + masking verified; the measured
route is unsloth dequantize-and-train on a T4 — the 3060 OOMs by 768 MB, recorded
honestly in `tools/gemma_dryrun.txt`). Before any adapter ships:

- **DEV-12** (first 12 sorted task ids) is the development split — it may be iterated on.
- **GATE-6** (last 6 sorted task ids, all `rich`) is frozen and never trained on.
- **Ship rule, pre-registered before training**: the adapter replaces the prompt-only
  baseline only if it wins **strictly in both pairs** of a 2×2 A/B on GATE-6.
  **No win → prompt-only ships.** No re-running arms to hunt a win; no post-hoc splits.
- The banked baseline already has a public score on the competition leaderboard
  (submission `58262373`, score **0.03**, read live from the Kaggle API) — that is the
  number every later bank is compared against.

## Repository map

```
agent.yaml  eval_config.yaml  eval-split.md  adapter-budget.md   ← the shippable bundle
prompts/  skills/  sub_agents/  tools/                            ← bundle internals
corpus/                                                           ← 3,626-row audited corpus
provenance/                                                       ← config snapshots, budget tool
freecad-factory/                                                  ← FreeCAD task factory spec + examples
training/                                                         ← T4 runbook, preflight, notebook
paper/                                                            ← the submitted writeup
tools/fix-audit/                                                  ← independent audit of the trainer fixes
```

## Reproduction

1. Read `eval-split.md` — the pre-registered evaluation contract (DEV-12 / GATE-6, arms,
   verdict rule, no-leaderboard-extrapolation law).
2. Validate the bundle: `python tools/validate_submission.py <bundle-dir>` — last line
   `VALIDATE: PASS` (it self-tests: it fails a deliberately poisoned copy).
3. Training: `training/RUNBOOK.md` → `training/preflight-checklist.md` → the notebook,
   on a Kaggle T4×2 session. `training/SESSION-CARD.md` is the one-page cheat sheet.
4. Corpus: every builder script and its skip lists are in `corpus/`; every count in
   `BUCKETS.md` reconciles with `wc -l`.

## Honest limitations

- The declared Gemma 4 E2B base **has not been evaluated end to end** at writing time;
  the local evidence base is a Qwen 3.5 surrogate stack, and the paper says so plainly.
- The checks are ours: not ablated, not run against held-out repository tasks.
- The planner's check-authoring seat failed all prompt-fix rounds and became a mechanical
  veto — recorded, not buried.
- The Godot `fix` sub-bucket is thin (2 rows); widening is a recorded v2 lane.
- `GEMMA_PLAN.md`'s COMPUTE table is pending the first measured burn; every wall time in
  the training docs is `NOT MEASURED` until a real session produces it.

## License

Copyright (c) 2026 SlothitudeGames. All rights reserved. This repository is a competition
entry; any license grant applies only per the competition's winner-license terms. The
base-model weights belong to their publisher and are not redistributed here.

## Links

- Competition: the Kaggle *Gemma 4 Developer Agent* competition (paper track writeup + main track)
- Writeup: submitted on the competition's paper track (2,998 words, dual-lane reviewed)
- Sibling project (prior engine, lineage only): [Scumm_L](https://github.com/slothitude/Scumm_L)

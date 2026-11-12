# GODOT BUCKET — READY (B12, handed to SCULLM 2026-11-13)

## Status: READY for Godot-fleet training

The bucket is verified in its new home: `scullm\submission\corpus\corpus_godot.jsonl` — **80 rows, all sourced, zero tokenizer literals, message-shape valid** (re-verified in-place after migration, 2026-11-13).

## The rows (per sub_head — one Godot-fleet head each)

| sub_head | rows | trains | source |
|---|---|---|---|
| logic | 34 | the logic head (RefCounted classes, LOGIC SEPARATE law) | 2-4 shipped scripts per game |
| tests | 19 | the tests head (2×-clear discipline) | headless test batteries |
| spec | 10 | the spec head (intent → game spec → structure) | jam specs + project listings |
| scenes | 10 | the scenes head (node composition) | scene dirs per game |
| scullm-plan | 5 | the scullm-plan head (milestones as OFL flows) | authored plans, scullm_check exit-0 ×5 |
| fix | 2 | the fix head | git history (honest: only 2 repair commits exist — thin, documented) |

## Provenance
11 real shipped games: sonar, slime-line, gyro-squadron-45, star-visitor, cubefall, powder-run, slope-hound, letterloom, twisted-six, octogram-rpg, octogram-arcade. Fully owned (our own shipped games — no license questions). Builder: `build_godot.py` (deterministic — two runs byte-identical). Report: `godot-report.md` (per-lane accounting, the slime-line spec-syntax-error fallback, the honest fix-thinness).

## Ready-for-training notes
1. The rows are Gemma chat-format (messages/system-user-assistant) — the trainer's tokenizer applies the template; no embedded markers (verified).
2. The sub_head tag drives the Godot-fleet routing corpus: pair each row's sub_head with the router head's B1 seeds when the Godot heads train.
3. Thin buckets (fix=2) are honestly thin — widen from git history of the 4 unharvested Godot projects (godot_agents, godotcode-sandbox, godot-adk-graph-editor, sculmm-engine) + Godot docs/demos before training the fix head.
4. The scullm-plan rows (5) validate the milestone-plan shape: scene → input → logic-class → test-suite → gate-2×-green → diary. Mint more per milestone from DIARY entries (v2 lane).

## v2 lanes (not blocking READY)
Godot docs/demo projects · GMP work-order schemas · Telegram-feedback→spec pairs · the 4 unharvested Godot projects.

# B12 GODOT HEAD(S) — corpus build report

Generated 2026-11-12 10:36 UTC by `build_godot.py` (reproducible; deterministic sorted order).

## The fleet (sub_heads)

The Godot head is a fleet — one head per pipeline stage. Row counts:

| sub_head | rows | lane |
|---|---|---|
| spec | 10 | spec-structure |
| scenes | 10 | spec-structure |
| logic | 34 | milestone-code |
| tests | 19 | tests |
| fix | 2 | fix |
| scullm-plan | 5 | scullm-plan |
| **total** | **80** | |

## Games harvested (actual dirs discovered on disk, READ-ONLY)

| game dir | spec | rows |
|---|---|---|
| `C:/Users/aaron/sonar/` | `spec/jam_spec.json` | 9 |
| `C:/Users/aaron/slime-line/` | `spec/jam_spec.json` | 6 |
| `C:/Users/aaron/gyro-squadron-45/` | `spec/study_spec.json` | 8 |
| `C:/Users/aaron/star-visitor/` | `spec/study_spec.json` | 6 |
| `C:/Users/aaron/cubefall/` | `spec/study_spec.json` | 8 |
| `C:/Users/aaron/powder-run/` | `spec/study_spec.json` | 9 |
| `C:/Users/aaron/slope-hound/` | `spec/study_spec.json` | 8 |
| `C:/Users/aaron/letterloom/` | `spec/study_spec.json` | 7 |
| `C:/Users/aaron/twisted-six/` | `spec/study_spec.json` | 9 |
| `C:/Users/aaron/octogram-rpg/` | `spec.md` | 8 |

Other Godot projects found on disk but NOT harvested as spec games (verified `project.godot`, no usable spec file): `octogram`, `godot_agents`, `godotcode-sandbox`, `godot-adk-graph-editor`, `sculmm-engine`. `octogram-arcade` ships spec-less but its readable git history fed lane 4 (fix rows).

## Rows per lane

- **fix**: emitted 2; scanned 5; deduped 0; rejected {}; skipped {'slime-line:git-unreadable': 1, 'powder-run:no-git': 1, 'slope-hound:no-git': 1, 'letterloom:no-git': 1, 'twisted-six:no-git': 1, 'octogram-rpg:no-git': 1}
- **milestone-code**: emitted 34; scanned 137; deduped 0; rejected {}; skipped {'sonar:not-refcounted': 8, 'sonar:cap-4-per-game': 2, 'slime-line:not-refcounted': 17, 'gyro-squadron-45:not-refcounted': 14, 'star-visitor:not-refcounted': 13, 'cubefall:not-refcounted': 10, 'powder-run:cap-4-per-game': 5, 'slope-hound:not-refcounted': 2, 'slope-hound:cap-4-per-game': 4, 'letterloom:not-refcounted': 1, 'letterloom:cap-4-per-game': 3, 'twisted-six:not-refcounted': 1, 'twisted-six:cap-4-per-game': 3, 'octogram-rpg:not-refcounted': 3, 'octogram-rpg:cap-4-per-game': 17}
- **scullm-plan**: emitted 5; scanned 5; deduped 0; rejected {}; skipped {}
- **spec-structure**: emitted 20; scanned 10; deduped 0; rejected {}; skipped {}
- **tests**: emitted 19; scanned 33; deduped 0; rejected {}; skipped {'sonar:cap-2-per-game': 2, 'slime-line:cap-2-per-game': 2, 'gyro-squadron-45:cap-2-per-game': 2, 'star-visitor:cap-2-per-game': 2, 'cubefall:cap-2-per-game': 3, 'powder-run:cap-2-per-game': 1, 'slope-hound:cap-2-per-game': 1, 'twisted-six:cap-2-per-game': 1}

Balance note: the fleet trains one head per sub_head. `fix` is thin by fact — the shipped repos' histories hold only 2 repair-flavored commits (octogram-arcade); sonar/gyro/star-visitor/cubefall histories are clean milestone pushes. Per the coordinator rule the sampling was widened where the corpus is rich: logic got the per-game cap (up to 4 RefCounted classes each) and tests 2 batteries each.


## scullm-plan validation (scullm_check.py)

- `cubefall_M1.scullm` — exit 0 — PASS (kept)
- `sonar_M2.scullm` — exit 0 — PASS (kept)
- `gyro-squadron-45_M1.scullm` — exit 0 — PASS (kept)
- `powder-run_M1.scullm` — exit 0 — PASS (kept)
- `twisted-six_M1.scullm` — exit 0 — PASS (kept)

5/5 plans passed the checker; only exit-0 plans are rows. Plan artifacts: `godot_plans/*.scullm`.

## V-law results (over the written file)

- V1 PARSE: 80 lines read back; 0 json failures.
- V2 SCHEMA: 0 schema failures.
- V3 NO TOKENIZER LITERALS: 0 failures.
- V5 PROVENANCE: 0 sources failed to resolve to a read file with an in-range line.
- V6 ACCOUNTING: per-lane scanned = emitted + rejected + deduped + skipped, reconciled above (caps are counted skips; nothing silently dropped).

## License line

Our own shipped games + our own specs + our own git history — fully owned (slothitude / the game-making pipeline). No third-party engine docs, no asset-store content, no scraped material.

## v2 harvest list (next expansion, all READ-ONLY sources)

- Godot docs + official demo projects (MIT/CC-BY — check per-file before mixing).
- The GMP work-order schemas at `C:/Users/aaron/game-making-pipeline/` (READ-ONLY): milestone work-orders, wall/gate schemas, diary formats.
- Telegram-feedback -> spec pairs (player feedback turned into spec deltas) from the pipeline's feedback lanes.
- Spec-less Godot projects with extractable structure rows (`octogram-arcade`, `octogram`) and any new game the pipeline ships.

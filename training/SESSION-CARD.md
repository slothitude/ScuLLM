# SESSION CARD — Kaggle T4×2 training run #1 (CROW Gemma LoRA)

Owner cheat sheet for OWNER GATE 2 (FINISH_PLAN.md §4). Every number below is measured and cited;
the only unknowns are the ones this session exists to measure (fit wall, pip wall, quota, burn).

1. **Create the notebook.** kaggle.com → notebook → new; get
   `C:\Users\aaron\scullm\training\t4\t4_train_notebook.ipynb` in (import the file or paste the
   cells). It is 19 cells — 8 markdown + 11 code, labeled Cell 1–Cell 11 (notebook itself).
2. **Attach the two inputs** (RUNBOOK.md §a.1; notebook header cell): File → Add Input →
   Competitions → `gemma-4-developer-agent`, then File → Add Input → Models → the Google `gemma-4`
   model (the e2b QAT variant). Weights mount read-only under `/kaggle/input`.
3. **Accelerator.** Settings → Accelerator → **GPU T4 x2** — burns 1× quota (full 30 h/week pool);
   L4×4 burns 2× and is reserved for parity evals (RUNBOOK §a.2).
4. **Internet ON** (Settings) — the pip cell (Cell 2) needs it; training cells need no network once
   weights + files are mounted (RUNBOOK §a.3).
5. **Upload the 4 files** (Input panel → Upload, or wrap as a Kaggle Dataset and attach) —
   measured bytes, preflight-checklist.md UPLOAD MANIFEST (`stat -c '%n %s'`, 2026-11-13):
   - `submission/corpus/corpus_decisions_gemma.jsonl` — **518,215 B** (370 D rows = THE training corpus)
   - `submission/corpus/corpus_b7_swe.jsonl` — **1,816,066 B** (staging only, 0 D rows)
   - `submission/corpus/corpus_signals_gemma.jsonl` — **976,347 B** (staging only, 0 D rows)
   - `submission/tools/train_crow_gemma.py` — **33,024 B** (canonical B1+B2 fixes included)
   - 4-file total **3,343,652 B**. Do NOT upload `corpus_d_gemma.jsonl` (superseded, RUNBOOK §c).
6. **Quota reading now.** Read the Kaggle quota widget and type the value into Cell 1's
   `REMAINING_GPU_QUOTA` (cell 1 slot; preflight GATE 3; M0 exit criterion).
7. **Run the cells in order.** Quota burns every attached minute, idle included — no between-cell
   idling (RUNBOOK §g.1).

| Cell | It does | Run-green looks like (hard stops in bold) |
|---|---|---|
| 1 | session check: nvidia-smi + CUDA assert | torch sees **2 GPUs — else fix the accelerator and re-run** |
| 2 | pip: unsloth + trl/peft/bitsandbytes/accelerate | prints "pip installs ok in Ns" — record Ns |
| 3 | version gate | "QAT-path gate PASS" (transformers >= 5.15.1 + unsloth); **unsloth missing = hard stop** |
| 4 | corpus verify (copies to /kaggle/working, counts D rows) | "…370 D rows"; the `== 370` assert must pass |
| 5 | stage trainer + B1 patch to the staged copy | "trainer staged + compiles: …" — see step 8 |
| 6 | discover the mounted checkpoint, single-base assert | "BASE_DIR = …e2b…" — **non-e2b base = STOP** (agent.yaml line 6) |
| 7 | in-cloud dry run (base load + masking) | "unsloth lane ok" + "DRY-RUN PASS" + "in-cloud dry-run ok in Ns" — record Ns; **fallback lane = hard stop** |
| 8 | THE FIT — HOUSE recipe r16 a16 dropout 0.0, 7 projections, lr 2e-4, warmup 10, 2 epochs, micro 1 accum 8, seed 3407, max-len 512 (cell 8 cmd = RUNBOOK §d) | loss prints at steps 5/10 per epoch; "FIT WALL TIME …"; **exit 2 = base load failed, 3 = fit failed**; train_state must say `done` |
| 9 | post-run verification | "adapter_config: r=16 alpha=16 dropout=0.0 targets=7 projections  PASS"; adapter dir < 3 GiB, per-file bytes printed |
| 10 | zip + digest | "download: /kaggle/working/crow_lora.zip" + size + sha256; reprints FIT_WALL_S |
| 11 | final report | gpu peak GB; prints "NOW: Save Version, then STOP" |

8. **KNOWN-BENIGN Cell 5 warning — IGNORE this one line.** Cell 5 may print
   `WARNING: neither the B1 bug string nor the fix was found — inspect resolve_targets() manually.`
   It is expected: the uploaded trainer already carries the canonical B1 fix (line 340 of
   `train_crow_gemma.py`, verified 2026-11-13; receipt `submission/tools/gemma_dryrun.txt`
   "FIXES APPLIED"; preflight-checklist.md GATE 1), which matches neither of Cell 5's two search
   strings (the old bug `return list(target_arg)` nor the notebook's own one-liner). Cell 5's
   `py_compile` still runs and still prints "trainer staged + compiles:" — THAT line is the gate.
   If it does not print, stop and diagnose.
9. **Expected banners (not errors; measured 3060 dry-run, gemma_dryrun.txt run 1/4):** unsloth
   "Fast Gemma4 patching"; "Model already quantized with gemma. Disabling `load_in_4bit`…";
   "Switching to 16bit LoRA" — that dequantize IS the intended route (≈ 4.88–5.02 GB torch /
   5,349 MiB peak, dry-run stand-in — fits a 16 GB T4). NEVER pass `--no-4bit`, `--packing`,
   `--fallback-transformers`, or `--target-modules all-linear` (measured-broken lanes;
   preflight GO/NO-GO discipline).
10. **Record the 7 smoke-test fields** into `C:\Users\aaron\scullm\eval\smoke-test.md` verbatim
    from this session's printed output (eval/smoke-test.md slots; RUNBOOK §g.4): (1) pip time
    (Cell 2), (2) dry-run time (Cell 7), (3) fit wall time (Cell 8 / Cell 10), (4) final loss/step
    from `train_state_crow_gemma.json` (Cell 8), (5) adapter bytes (Cell 9), (6) Kaggle quota
    reading (Cell 1 slot), (7) observed burn (quota widget before vs after; if ≠ 1× for T4×2,
    GEMMA_PLAN.md COMPUTE gets corrected). Fit wall was NOT MEASURED before this session — the
    dry-run completed 0 optimizer steps (RUNBOOK §e).
11. **End the session — in this order** (RUNBOOK §g.2; Cell 11 reminder): **Save Version first**
    (log + zip captured), **then explicitly stop** (⋯ → Stop). Closing the tab does not free the
    GPU; verify no active session remains.
12. **Download + land.** Output panel → `crow_lora.zip` (size + sha256 from Cell 10). On Rog it
    goes to `submission/adapters/crow_lora/` (PEFT layout), then the C0 gate
    (`submission/eval-split.md`: adapter arm STRICTLY > baseline arm, both arms twice) before it
    counts as an adapter (RUNBOOK §f.4).

Sources: training/t4/RUNBOOK.md (§a–§g) · training/t4/preflight-checklist.md (GATE 1–5 + UPLOAD
MANIFEST) · training/t4/t4_train_notebook.ipynb (19 cells, code quoted above) ·
submission/tools/gemma_dryrun.txt (measured verdict + FIXES APPLIED) · eval/smoke-test.md (the 7
slots) · FINISH_PLAN.md §4 (gate 2). One session, one purpose, stopped when done.

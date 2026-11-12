# PREFLIGHT — go/no-go for the T4×2 cloud training run (CROW Gemma LoRA)

Staged 2026-11-12. Companion: `RUNBOOK.md` (the sequence) and `t4_train_notebook.ipynb`
(the runnable form). Every item cites its measured source; nothing here is a guess.

## GATE 1 — the local dry-run verdict (smart-training law)

- [x] **VERDICT LANDED** — `submission/tools/gemma_dryrun.txt` (2026-11-12, Lappy 3060,
      RTX 3060 Laptop 5.67 GiB usable, unsloth 2026.10.11 / torch 2.14.1+cu130 /
      transformers 5.15.1 / peft 0.21.2 / trl 1.15.0):
  - **FAIL as a 3060 fit gate** — the gemma-QAT base is untrainable there: transformers
    raises `QuantizationMethod.GEMMA do not support training` (measured, run 5) and the
    16-bit load OOMs (~5.0 GB + 768 MB headroom > 5.67 GB, measured run 1).
  - **VERIFIED as a config gate** — gemma4 arch support (unsloth "Fast Gemma4 patching"),
    GemmaTokenizer + `<|turn>` template, completion-only masking (unmasked = exactly the
    letter + `<turn|>` end token; prompt fully -100), and LoRA r16 prep
    (37,920,768 / 2,365,851,416 trainables = 1.603%).
  - **Working route measured:** unsloth dequantize-and-train — 16-bit bf16 load ≈ 4.88–5.02 GB
    / nvidia-smi peak 5,349 MiB → fits a T4's 16 GB with headroom. (Base used was the
    sha-verified DRY-RUN-ONLY stand-in `gemma-4-E2B-it-qat-mobile-transformers`; same arch/
    scale as the declared base, never to be shipped.)
- [x] **SUB-GATE CLOSED (2026-11-13): both canonical fixes landed in
      `submission/tools/train_crow_gemma.py`** — per `submission/tools/gemma_dryrun.txt`,
      section "FIXES APPLIED (2026-11-12, code pass on Rog CPU by ScareCrow:Nvidia;
      target: train_crow_gemma.py in this directory)". Quoted from that section:
  - **B1** — "FIXED in resolve_targets(). Old code `return list(target_arg)` char-split the
    comma string ... Now: `return [t.strip() for t in target_arg.split(",") if t.strip()]`.
    Single-name inputs preserved ('q_proj' -> ['q_proj']); whitespace and trailing commas
    tolerated. The HOUSE default --target-modules (comma string of the 7 projections) now
    resolves to the 7-name list as intended." (Fix verified present at line 340 of the
    trainer, 2026-11-13; the old `return list(target_arg)` is gone.)
  - **B2** — "FIXED in resolve_all_linear()/resolve_targets(). New _is_quant_wrapper()
    excludes quantization wrapper Linears by class identity over the whole MRO (fragments
    'quant' / 'clippable' -> catches QuantizedLinear, which SUBCLASSES nn.Linear, and
    Gemma4ClippableLinear)"; on a QAT-direct base with nothing wrappable left,
    "resolve_targets raises SystemExit with a clear 'unsupported ... needs a
    dequantized/16-bit base' message instead of feeding peft the cryptic 'Target module
    Gemma4ClippableLinear(...) is not supported'". (Fix verified present at lines 297/315
    of the trainer, 2026-11-13.)
  - Receipt verdict lines, verbatim: "ALL SELF-TESTS PASS" and "py_compile: OK  ($ python
    -m py_compile train_crow_gemma.py)".
  - The receipt's own honesty notes stay in force: the wrapper exclusion "is a class-MRO
    identity check, not a hard isinstance import"; and "The transformers
    QuantizationMethod.GEMMA training refusal (run 5) is upstream (transformers), untouched
    by both fixes" — which is exactly why the lane discipline below still binds.
  - Lane discipline (RUNBOOK §b/§d, unchanged): never `--fallback-transformers` on a QAT
    base — measured-broken, per the receipt's closing section: "the --fallback-transformers
    lanes still hit the transformers QuantizationMethod.GEMMA training refusal on a QAT
    base (upstream, by design) - only the unsloth lane or a one-time repacked bf16 base
    trains"; never `--target-modules all-linear` for this run — the HOUSE 7-name list +
    the B1 fix is the path, per the receipt: "The declared T4 lane (unsloth + HOUSE 7-name
    default targets) is unaffected: 7 explicit names, no all-linear resolution, patched
    peft wraps the QAT modules as it did in run 4."

## GATE 2 — corpus (measured on disk 2026-11-12; row scan + dry-run confirmation)

- [x] `corpus_decisions_gemma.jsonl` — 518,215 B, **370 rows, all type D → the training corpus**
- [x] `corpus_b7_swe.jsonl` — 1,816,066 B, 695 rows, **0 D rows** (dry-run measured
      `0 usable rows, 12 rejected`) — uploads as staging only
- [x] `corpus_signals_gemma.jsonl` — 976,347 B, 1,239 rows, all type S, **0 D rows** — staging only
- [x] Upload set = those three + `train_crow_gemma.py`; training consumes 370 of 2,304 rows
      (16.1%) — recorded, not hidden. (The old "3.16 MiB total" figure was the 3-corpus-file
      total; the measured 4-file total is 3,343,652 B — see the UPLOAD MANIFEST below.)
- [ ] In-session check (notebook cell 4): row counts + the `== 370` assert must pass after upload

## GATE 3 — budget vs quota (30 h/week pool, T4×2 burns 1×)

- [x] Lane check: T4×2 = 1× burn → full 30 h pool (GEMMA_PLAN.md COMPUTE, owner-confirmed
      2026-11-12; KAGGLE_EXPECTATIONS.md §2 flags these as planning assumptions to verify
      in-notebook, not competition-published rules)
- [ ] **Quota remaining: NOT MEASURED** — read the Kaggle notebook quota widget before launch
      (notebook cell 1 has the slot; M0 exit criterion, KAGGLE_EXPECTATIONS fix 2)
- [ ] **Fit burn: NOT MEASURED** — 0 optimizer steps ran on the dry-run; formula staged
      (370 rows × 2 epochs = 740 micro steps ≈ 94 optimizer steps) awaiting the first real
      sec/step. Do not schedule a session chain against invented minutes
- [ ] Session discipline acknowledged: Save Version → explicit Stop; idle minutes burn quota
      (RUNBOOK §g)

## GATE 4 — measured-numbers slot (M0 / smoke-test)

- [ ] `eval/smoke-test.md` — **STAGED 2026-11-13**: the file now exists at `eval/smoke-test.md`
      with `NOT-YET-RUN:` slots for pip time, dry-run time, fit wall time, final loss/step,
      adapter bytes, the quota reading, and observed burn (RUNBOOK §g.4). It gets filled ONLY
      from the owner session's real printed output — never estimated. Until then every wall
      figure in the runbook stays marked NOT MEASURED. (Path note: RUNBOOK line 19 and the
      notebook header still say `state/gemma/eval/smoke-test.md` — the pre-migration path; in
      this repo the file lives at `eval/smoke-test.md`. Read-only files: reported, not edited.)
- [x] VRAM side of the slot IS measured (see GATE 1) — the T4 fit is not expected to OOM

## GATE 5 — environment + single-base law

- [x] Base declared in `submission/agent.yaml` line 6: `gemma-4-e2b-it-qat-w4a16-ct` — the
      notebook discovers the mounted checkpoint and hard-stops on any non-e2b base
- [ ] In-session: competition + gemma-4 model inputs attached; `config.json` + safetensors
      found under `/kaggle/input` (notebook cell 6)
- [ ] In-session: transformers >= 5.15.1 and unsloth importable (notebook cell 3 — measured
      version floor; missing unsloth = the broken QAT-direct path, hard stop)
- [ ] In-session: cloud dry-run prints `DRY-RUN PASS` AND the log contains
      `unsloth lane ok` (notebook cell 7 — a fallback-lane run is a measured hard stop)
- [ ] Post-fit: adapter_config r=16/alpha=16/dropout=0/7 projections; adapter dir inside the
      rank-16 ≈ 110–220 MB envelope and the 3 GiB budget; train_state `done` (notebook cell 9)
- [ ] Post-download: adapter lands in `submission/adapters/crow_lora/`; **C0 gate**
      (`submission/eval-split.md`) must pass — adapter arm STRICTLY > baseline arm, twice —
      before the adapter counts as done

## GO / NO-GO

**GO pending owner session** (verdict flipped 2026-11-13; the 2026-11-12 NO-GO stood on the
open B1/B2 sub-gate, now closed — see GATE 1). Two owner actions remain, both inside the
session itself:

1. **The notebook session** — upload the manifest below and run `t4_train_notebook.ipynb` on
   GPU T4 x2 end to end. The dry-run validated everything it could reach (arch, masking,
   route, flags) but never ran an optimizer step, so this first session is itself the fit
   confirmation.
2. **The quota reading** — notebook cell 1 prints the slot: read the Kaggle notebook quota
   widget and replace `REMAINING_GPU_QUOTA` before launch (GATE 3; M0 exit criterion,
   KAGGLE_EXPECTATIONS fix 2).

Standing session discipline (RUNBOOK §b/§d, restated): never `--fallback-transformers` on a
QAT base (measured-broken — transformers refuses `QuantizationMethod.GEMMA` training); never
`--target-modules all-linear` for this run (the HOUSE 7-name list + the B1 fix is the path);
unsloth lane or nothing — notebook cells 3/7/8 hard-stop on any fall-through. Then work the
checklist top to bottom: every unchecked box above must be checked (in-session checks get
checked by the notebook's own asserts) before the fit cell runs.

## UPLOAD MANIFEST (staged 2026-11-13; measured, not estimated)

Owner action: upload all four files into the notebook (Input panel → Upload, or wrap as a
Kaggle Dataset and attach — RUNBOOK §c). Measured with this command, run in
`C:\Users\aaron\scullm` on 2026-11-13:

    $ stat -c '%n %s' submission/corpus/corpus_b7_swe.jsonl submission/corpus/corpus_decisions_gemma.jsonl submission/corpus/corpus_signals_gemma.jsonl submission/tools/train_crow_gemma.py

- [ ] `submission/corpus/corpus_b7_swe.jsonl` — **1,816,066 B** (staging only, 0 D rows)
- [ ] `submission/corpus/corpus_decisions_gemma.jsonl` — **518,215 B** (the training corpus,
      370 D rows)
- [ ] `submission/corpus/corpus_signals_gemma.jsonl` — **976,347 B** (staging only, 0 D rows)
- [ ] `submission/tools/train_crow_gemma.py` — **33,024 B** (canonical B1+B2 fixes included,
      per GATE 1)
- Measured 3-corpus-file total: **3,310,628 B (3.16 MiB)** — matches RUNBOOK §c's table
- **Measured 4-file upload total: 3,343,652 B (3.19 MiB)** — the plan's stale "3.16 MiB
  corpus set" covered the 3 corpus files only; the trainer adds 33,024 B
- After upload, notebook cell 4 re-verifies on Kaggle: row counts + the `== 370` assert
  (GATE 2's in-session check)

# RUNBOOK — the T4×2 cloud training run (CROW Gemma LoRA, work order C2)

Staged 2026-11-12; updated the same day when the 3060 dry-run verdict **LANDED** in
`submission/tools/gemma_dryrun.txt`. **The verdict is honest FAIL for a 3060 fit** — the QAT
base cannot be trained there at all (transformers refuses GEMMA-quantized training; the 16-bit
load OOMs 5.67 GB) — but it bought the config knowledge this run runs on: gemma4 arch + unsloth
patching + completion-only masking are VERIFIED, and the working route is **unsloth
dequantize-and-train** (16-bit load ≈ 4.9–5.0 GB measured → fits a T4's 16 GB with headroom).

**Remaining gates before an actual cloud RUN** (preflight-checklist.md is the list):
1. the two measured trainer bugs (B1 comma-split, B2 QAT-wrapper targets) — LANDED: their
   canonical fixes are in `train_crow_gemma.py` (B1 comma-split in `resolve_targets()`, B2
   QAT-wrapper exclusion via `_is_quant_wrapper()`; receipt: `submission/tools/gemma_dryrun.txt`
   section "FIXES APPLIED", self-tests ALL PASS, py_compile OK);
2. the owner's green light on the cloud burn (smart-training law: the 3060 validated the config
   as far as it physically can — VRAM fit-validation of this base can only happen on the T4).

Companion files: `t4_train_notebook.ipynb` (the runnable form) and `preflight-checklist.md`.
Everything below is quoted from real scripts and measured records. Fit wall-time stays
**NOT MEASURED** — the dry-run completed 0 optimizer steps; `eval/smoke-test.md`
does not exist yet.

---

## (a) Attach the notebook to the competition (base weights come free)

1. kaggle.com → notebook → **File → Add Input → Competitions → `gemma-4-developer-agent`**
   → also **Add Input → Models → the `gemma-4` Google model** (the e2b QAT variant).
2. **Settings → Accelerator → GPU T4 x2.** T4×2 burns quota **1×** — the full 30 h/week
   pool. L4×4 burns 2× and is reserved for parity evals (GEMMA_PLAN.md COMPUTE).
3. Internet: ON for the pip-install cell; the training cells need no network once weights +
   corpus are mounted/uploaded.
4. The base weights mount read-only under `/kaggle/input` — no download, no HF license gate
   in this environment. Mount shape per the official getting-started notebook (cell 4, quoted
   in `KAGGLE_EXPECTATIONS.md` §4):
   `MODEL_PATH = Path(f'/kaggle/input/models/google/gemma-4/other/{declared_model}/2')`
   — for us `declared_model = gemma-4-e2b-it-qat-w4a16-ct` (the single base declared in
   `submission/agent.yaml` line 6; single-base rule HARNESS_README §3.2). The notebook
   **discovers** the real path by globbing `/kaggle/input` and asserts on it — the mount
   string shifts with how the input is attached.
5. Single-base cross-check before the fit: the discovered checkpoint dir and `agent.yaml`'s
   `model:` line must both say `gemma-4-e2b-it-qat-w4a16-ct`. Mismatch → STOP.
6. **QAT caveat (measured):** the declared base is a QAT checkpoint like the dry-run stand-in.
   It stays QAT on disk; **unsloth dequantizes it to 16-bit bf16 at load** (measured banner:
   "Model already quantized with gemma. Disabling `load_in_4bit`… Switching to 16bit LoRA").
   That is the intended route — do not fight it.

## (b) Pip-install the stack — the dry-run verdict renamed the lanes

Before the verdict the trainer's docstring listed unsloth as a fast path with a load-bearing
fallback. The record flips that: **unsloth is THE lane; the fallbacks are measured-broken for
this checkpoint** (record runs 1/2/5):
- transformers 5.15.1 hard-refuses: `ValueError: The model you are trying to fine-tune is
  quantized with QuantizationMethod.GEMMA but that quantization method do not support
  training` — kills TRL/Trainer construction (measured).
- 4-bit request on the QAT base: unsloth overrides it itself (banner, measured); the plain
  fallback dies at load instead (`GemmaQuantizationConfig but you are passing a
  BitsAndBytesConfig`, measured).
- **unsloth 2026.10.11 patches Gemma4** ("Fast Gemma4 patching", measured) and dequantizes to
  16-bit bf16 ≈ 4.88–5.02 GB torch / 5,349 MiB nvidia-smi peak — measured on the E2B-scale
  stand-in (`gemma-4-E2B-it-qat-mobile-transformers`, sha-verified, dry-run-only; the same
  arch/family, NOT the declared artifact). On a T4 that is inside 16 GB with headroom.

Install cell (also notebook cell 2):
```bash
pip install -q unsloth                                            # THE lane
pip install -q trl peft bitsandbytes accelerate                   # imports stay happy; NOT load-bearing
```
Notebook cell 3 gates the version floor the dry-run measured: **transformers >= 5.15.1** and
unsloth importable — unsloth missing would route the run into the QAT-direct path, which is
broken by design, so the cell hard-stops. Notebook cells 7/8 additionally hard-stop if the
trainer log shows a fall-through (`unsloth lane ok` must appear in the log).

## (c) Upload the corpus (sizes and row counts measured on disk 2026-11-12)

Upload all three files from `C:\Users\aaron\scullm\submission\corpus\` (drag into the
Input panel, or wrap as a Kaggle Dataset and attach):

(path retargeted 2026-11-13 — project moved to C:\Users\aaron\scullm; the measured numbers themselves are unchanged)

| file | bytes (measured) | rows (measured) | row type | consumed by train_crow_gemma.py? |
|---|---|---|---|---|
| `corpus_b7_swe.jsonl` | 1,816,066 B (1.73 MiB) | 695 | none (`messages`-format SWE rows) | **NO** — rejected "not a D row" |
| `corpus_decisions_gemma.jsonl` | 518,215 B (506 KiB) | 370 | all `D` | **YES — the training corpus** |
| `corpus_signals_gemma.jsonl` | 976,347 B (953 KiB) | 1,239 | all `S` | **NO** — rejected "not a D row" |
| total | 3,310,628 B (3.16 MiB) | 2,304 | — | 370 usable (16.1%) |

**Honesty finding, measured twice:** the trainer is a D-row trainer — `row_to_sample` requires
`type == "D"`. The row-by-row scan found 0 D rows in b7/swe and 0 in signals; the dry-run
confirmed on a real b7 sample: `[data] 0 usable rows, 12 rejected (first: [(0, 'not a D row'), …])`.
The fit therefore trains on the **370 D rows of `corpus_decisions_gemma.jsonl`** (`--corpus`
takes one path; there is no multi-file mode). Do NOT concatenate the three files and call it
2,304 training rows — 1,934 would be rejects. If b7_swe is ever meant to train this head it
needs a joiner pass into D-rows first (record, CORPUS section).
(`corpus_d_gemma.jsonl`, 118,487 B / 94 rows, also exists on disk — the earlier C1 slice of the
same D rows, superseded by the 370-row B2 build; do not upload it.)

## (d) The run command (flags quoted from train_crow_gemma.py argparse) + the B1 patch

**B1 first (measured trainer bug):** `resolve_targets()` does `return list(target_arg)`,
char-splitting a comma string — the dry-run measured `Target modules {'g','v',',','a','_','p',
'j',…} not found in the base model` when the HOUSE list was passed. Our fit command passes
exactly that list, so the notebook applies the record's one-liner
(`str(target_arg).split(",")`) **to the staged copy in /kaggle/working only** (cell 5);
`submission/tools/train_crow_gemma.py` itself now carries the canonical fixes — B1 comma-split
in `resolve_targets()`, B2 QAT-wrapper exclusion via `_is_quant_wrapper()` (receipt:
`submission/tools/gemma_dryrun.txt` section "FIXES APPLIED"). **B2** (all-linear resolving QAT
`QuantizedLinear` wrappers → peft
ValueError) is why we do NOT use `--target-modules all-linear`: the HOUSE 7-name list + B1 fix
avoids the wrappers entirely (record's own recommendation).

Dry-run inside the cloud session first (minutes; validates the real base load + masking before
the fit burns quota — the trainer prints `DRY-RUN PASS:` on success):
```bash
python train_crow_gemma.py --dry-run \
  --base  "$BASE_DIR" \
  --corpus /kaggle/working/corpus_decisions_gemma.jsonl
```
Then the fit — every flag is a real argparse flag, set to the HOUSE defaults (TEV1_METHOD.md):
```bash
python train_crow_gemma.py \
  --base  "$BASE_DIR" \
  --corpus /kaggle/working/corpus_decisions_gemma.jsonl \
  --out   /kaggle/working/adapters/crow_lora \
  --state /kaggle/working/train_state_crow_gemma.json \
  --r 16 --alpha 16 --dropout 0.0 \
  --target-modules q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj \
  --lr 2e-4 --warmup 10 --epochs 2 \
  --micro 1 --accum 8 --seed 3407 --max-len 512
```
(`$BASE_DIR` = the discovered `/kaggle/input` checkpoint dir. `--out`/`--state` are explicit
because the script's relative defaults assume the submission tree. Defaults are already HOUSE —
flags spelled out so the command is self-documenting. No `--packing` (tiny single-letter
completions; the flag's help says keep off), no `--no-4bit` (unsloth's own banner overrides the
4-bit request for the QAT base — that switch to 16-bit IS the measured route), and never
`--fallback-transformers` (measured-broken on QAT). `save_strategy="no"` is fixed — no
intermediate checkpoints, only the final PEFT save. Expect `logging_steps=5` loss prints.)

Exit codes: `2` = base load failed, `3` = fit failed. `train_state.json` goes
`starting → training → done` (`TrainStateCB`); `failed` on either trap.

## (e) Expected wall-time math — **NOT MEASURED (the M0 slot)**

The dry-run completed **0 optimizer steps** — no sec/step exists anywhere yet, and
`eval/smoke-test.md` is unwritten. Until M0 records one number, this section is a formula:

- dataset: 370 usable D rows (measured) × 2 epochs × micro 1 = **740 micro forward/backward
  steps**; optimizer steps = 2 × ceil(370/8) = **94** (effective batch 8).
- **fit wall = 740 × (sec per micro-step) + load/save overhead.** `sec per micro-step`:
  **NOT MEASURED** → slot for the M0/T4-session number. Loss logs at steps 5/10 per epoch are
  the checkpoints to time against.
- overhead: pip install (~3–8 min class, NOT MEASURED on Kaggle), unsloth 16-bit base load from
  the mount (NOT MEASURED in wall-clock; VRAM measured — see below), PEFT save of a rank-16
  adapter (HARNESS_README §3.4 envelope ≈ 110–220 MB — one write).
- **VRAM (measured, dry-run stand-in):** 16-bit load ≈ 4.88–5.02 GB torch /
  5,349 MiB nvidia-smi peak; LoRA prep adds ~37.9M trainables (measured 1.603% of the base) —
  all comfortably inside one T4's 16 GB; on the 3060 (5.67 GB) the same load OOM'd, which is
  exactly why this run is a T4 run.
- The notebook times every stage and prints the real numbers; paste them into
  `eval/smoke-test.md` — those recorded numbers, not this section, drive quota planning.

## (f) Checkpoint download + post-run verification

1. `save_pretrained` writes `adapter_config.json` + `adapter_model.safetensors` (+ tokenizer
   files) to `--out`; the script warns itself if the two adapter files are missing.
2. Verify before download (notebook cell 9): config has `r: 16`, `lora_alpha: 16`,
   dropout 0.0, exactly the 7 projections; safetensors nonzero; dir total inside the rank-16
   envelope ≈ 110–220 MB (record the exact bytes); `train_state_crow_gemma.json` = `"done"`
   with real step/loss; all inside the 3 GiB unpacked submission budget INCLUDING adapters
   (HARNESS_README §2.4 — feed the number to `submission/adapter-budget.md`, WO-B10).
3. Download: zip the adapter dir to `/kaggle/working/crow_lora.zip`, print SHA-256 + size
   (notebook cell 10), fetch via the **Output** panel. Never download the base weights.
4. On Rog: copy into `submission/adapters/crow_lora/` (PEFT layout, harness-discovered), then
   the **C0 gate** (`submission/eval-split.md`): adapter arm STRICTLY > prompt-only baseline
   arm, both arms twice. The fit only produces the candidate; C0 makes it an adapter.

## (g) Kill/cleanup discipline (quota is a shared weekly pool)

1. **Every attached minute burns 1× quota, including idle.** No between-cell idling; interrupt
   and diagnose stuck cells.
2. Before stopping: **Save Version** (log + zip captured), **then explicitly Stop the session**
   (⋯ → Stop). Closing the tab does not free the GPU. Verify no active session remains.
3. Keep `/kaggle/working` lean: adapter zip, `fit_log.txt`, `train_state_crow_gemma.json`. The
   ~20 GiB working-output cap is planning guidance to verify in-notebook
   (KAGGLE_EXPECTATIONS §5.8).
4. Record into `eval/smoke-test.md` immediately after (M0 exit criterion, KAGGLE_EXPECTATIONS
   fix 2): fit wall time, dry-run time, pip time, final loss/step, adapter bytes, the Kaggle
   UI's remaining quota, and observed burn. If burn ≠ 1× for T4×2, edit GEMMA_PLAN.md's
   COMPUTE table to the measured values before the next session is scheduled.
5. One session, one purpose, stopped when done.

# AUDIT — twin trainer bug-fix (B1+B2), ScareCrow:OpenRouter, 2026-11-12

Work under review: `C:\Users\aaron\evo\state\gemma\submission\tools\train_crow_gemma.py`
(fixed file READ-ONLY for this audit) · claims in `gemma_dryrun.txt` "FIXES APPLIED"
· independent tests: `../fix_audit_test.py` (fresh assertions, loaded the REAL
file via importlib; Rog CPU, python 3.13.12, torch 2.11.0+cpu — no stub needed).
Judge gate: `judge.sh` in this dir → `python minion_harness.py judge .` — exit 0.

## 1. Triage of the builder's claims

| # | Builder claim (gemma_dryrun.txt) | Classification | Audit evidence |
|---|---|---|---|
| 1 | B1 fix line `return [t.strip() for t in target_arg.split(",") if t.strip()]` present in resolve_targets() | VERIFIED | read at train_crow_gemma.py:340; `inspect.getsource` on the imported real module confirms; my test asserts the OLD bug is gone (`result != list("q_proj,k_proj")`, no single-char names — the run-2 charsplit signature) |
| 2 | B1 "q_proj,k_proj" → exactly ["q_proj","k_proj"] | VERIFIED | my test: PASS (exact list) |
| 3 | B1 single names preserved | VERIFIED | my test: 'v_proj' → ['v_proj'] PASS |
| 4 | B1 whitespace + trailing commas tolerated | VERIFIED | my tests: " q_proj ,  k_proj " and ",q_proj,,k_proj,," both → ["q_proj","k_proj"] PASS |
| 5 | B1 HOUSE default --target-modules resolves to the 7 names | VERIFIED | my test pulls the default through the REAL `parse_args([])` → resolve_targets → equals `HOUSE["target_modules"]` PASS |
| 6 | B2 `_is_quant_wrapper` excludes QuantizedLinear / Gemma4ClippableLinear, keeps real nn.Linear | VERIFIED | fresh fake family mirroring the measured repr (Clippable wraps child 'linear': QuantizedLinear): real q_proj/up_proj kept, all wrappers dropped, suffix 'linear' absent (the run-3 tripwire) PASS |
| 7 | B2 excluded-wrapper count print | VERIFIED | enumeration of my model = exactly 10 wrapper Linears; print says "excluded 10 quantization wrapper module(s)" PASS |
| 8 | B2 wrapper-only base → SystemExit with "unsupported / dequantized" message | VERIFIED | my test raises SystemExit, message contains both strings PASS |
| 9 | B2 honesty note: MRO check ≈ isinstance-equivalent against the wrapper bases | VERIFIED with nuance | my test proves the fragment check sweeps the WHOLE MRO (innocent leaf class over a `_QuantizedBase` ancestor → True). That is BROADER than isinstance-to-the-real-classes — safe for exclusion, but it is the reach behind risk R1 below |
| 10 | Builder's self-test receipts (gemma_dryrun.txt) | CONSISTENT | no contradictions between their receipts and my independent results |

## 2. Independent test results

`fix_audit_test.py` — 24 PASS / 0 FAIL, exit 0 (full transcript above in the run
log; re-runnable: `PYTHONIOENCODING=utf-8 python fix_audit_test.py`).
Coverage beyond the builder's own tests: old-bug charsplit tripwire, order
preservation on the comma path, empty-fragment dropping, the CLI-default path
through real `parse_args`, nested wrapper children (a Clippable inside a
Clippable — 10 wrappers counted correctly), the pre-existing lm_head/visual/mtp
filter regression guard, and the false-positive probe below.

## 3. Regression risks

- **R1 (LOW)** — B2 fragment check false positives: any legitimate custom
  nn.Linear subclass with `quant` or `clippable` merely incidentally in its own
  OR ANY ANCESTOR class name is silently dropped from all-linear (demonstrated:
  `QuantFreeLinear` → excluded). Exposure here is low: this submission's
  checkpoint family (transformers 5.15.1 gemma4-QAT) names real linears bare
  `Linear`, and the recommended T4 lane uses the HOUSE 7-name default, which
  never enters all-linear resolution. Residual risk is only for future
  checkpoints with custom Linear subclass naming.
- **R2 (LOW/INFO, pre-existing)** — the head filter matches the fragment
  `visual`, not `vision`: a gemma-style `vision_tower...` full name is not
  excluded. Untouched by B1/B2 and largely moot (peft matches by suffix, so a
  full-name exclusion would not block a same-suffix wrap anyway). No action
  required for this fix; noted for a future pass if multimodal heads ever need
  hard exclusion.
- **R3 (LOW/INFO, not a regression)** — B1 has no None/empty guard: `None` →
  AttributeError, `""` → `[]` handed to peft. Identical to pre-fix behavior
  (`list(None)`/`list("")`), and unreachable from the CLI because argparse's
  default is the HOUSE comma string and there is no way to pass None.
- **R4 (INFO)** — comma path does not dedupe or validate names; duplicates /
  typos pass through to peft's own errors. Same as pre-fix (which was strictly
  worse). No action.
- Out of audit scope (cannot be verified from Rog CPU): the builder's GPU-lane
  claims (3060 VRAM numbers, unsloth/transformers behavior, T4 fit expectations).
  Those remain claims until the T4 fit run happens — the fix record itself says
  so honestly.

## 4. Verdict

Both claimed fixes exist in the real file, behave as described under fresh
independent tests, and no regression was introduced by them. All discovered
issues are pre-existing, informational, or LOW-risk-by-construction.

AUDIT: APPROVED

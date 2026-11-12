# TASK — AUDIT of the twin's trainer bug-fix (ScareCrow:OpenRouter)

Brief: independent pre-gate audit of the B1+B2 fixes in
`state/gemma/submission/tools/train_crow_gemma.py` before the cloud training
run is gated. Fixes claimed in `gemma_dryrun.txt` ("FIXES APPLIED"):

- B1: resolve_targets() comma-split with strip (old bug: `list(target_arg)`
  char-split "q_proj,k_proj" into 17 single-char module names ->
  peft NoMatchingPeftModuleError on run 2).
- B2: all-linear wrapper exclusion via class-MRO name check (fragments
  "quant"/"clippable" over type(mod).__mro__), excluding QuantizedLinear /
  Gemma4ClippableLinear while keeping real nn.Linear; wrapper-only base
  raises SystemExit with an "unsupported" message (old failure: peft
  "Target module Gemma4ClippableLinear(...) is not supported", run 3).

Deliverables (all inside this task dir + fix_audit_test.py alongside it):
1. fix_audit_test.py — FRESH assertions from the bug descriptions, loading
   the REAL file via importlib (torch 2.11.0+cpu present on Rog, so the
   torch-dependent B2 paths run locally; no stub needed).
2. judge.sh — the V-law gate: fixed file exists + py_compile + fresh tests
   green + AUDIT.md verdict line present. Exit 0 = green.
3. AUDIT.md — triage of the builder's claims, independent test results,
   regression risks with severity, final line AUDIT: APPROVED / CHANGES-REQUIRED.

Laws: BOUNDARY LAW (write only inside C:\Users\aaron\evo\), HONESTY LAW
(genuinely independent tests; a discovered defect is reported, not fixed).
The fixed file itself is READ-ONLY for this audit.

# The V-laws (every build passes these before done):
# V1  the build exists and parses/runs
# V2  the output schema/shape matches the brief exactly
# V3  no placeholders, no TODOs, no invented data
# V4  the brief's specific acceptance checks pass
# V5  every emitted artifact carries its source/provenance
# V6  the accounting reconciles (scanned = emitted + skipped, counts real)

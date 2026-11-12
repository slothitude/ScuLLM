# FreeCAD Task Factory — generation pipeline spec

Insight being industrialized: **FreeCAD ships all the components of the competition** —
real production Python code (`Mod/`), a test culture, a bug surface, and (via the swegemma
harness) a verifier. The factory turns `Mod/` functions into honest swegemma-schema tasks:
write passing tests on current code, inject ONE realistic bug, describe the damage as a bug
report, package the snapshot. Every claim is labeled **RUN** (executed on this machine,
2026-11-12; receipts in `RUN_LOG.md`) or **DESIGNED-NOT-RUN** (designed but not yet
executed, with the reason).

**ETHICS (non-negotiable):** these are synthetic bugs on our own snapshots — the germ
eating its own food. They are our training/eval material, generated from FreeCAD source we
did not write and mutations we injected ourselves. They must NEVER be claimed, sold,
submitted, or described as external SWE-bench tasks or as upstream FreeCAD bugs. The
synthetic namespace (`instance_id` = `freecad_9xxxx`, `repo` = `FreeCAD/FreeCAD` with a
factory-generated `base_commit` from our own git snapshot) makes provenance self-evident in
every row.

---

## Step 1 — Source selection

**Candidate pool (RUN-measured):** scanning `C:\Program Files\FreeCAD 1.1\Mod\` (READ-ONLY,
harvest only) for `*.py` files containing NO import of `FreeCAD`, `PySide`, `Part`, `Mesh`,
`Sketcher`, `Draft`, `TechDraw` yields **394 files**. After dropping data/example dumps
(e.g. `Fem/femexamples/meshes/*` — 30+ files of pure coordinate literals), the usable
pure-logic pool is roughly 100–150 files, including:

- `Mod/PartDesign/fcgear/involute.py` — gear involute math, stdlib-only (`from math import ...`),
  and it self-documents the property we need: *"this file doesn't depend on FreeCAD, a
  property very handy when testing in isolation"* (line 374).
- `Mod/BIM/Dice3DS/dom3ds.py` — 3DS binary format parsing (stdlib struct).
- `Mod/CAM/Path/Tool/assets/store/filestore.py` — file-store logic (stdlib).
- `Mod/AddonManager/Addon.py` — addon metadata dataclass logic.

**Selection rules for a target function:**
1. Module imports stdlib only (importable under plain `python3`, headless, offline).
2. Function is deterministic and side-effect-light (pure math / parse / transform preferred;
   file-IO allowed via pytest `tmp_path`).
3. Observable contract can be stated as math or round-trip invariants, not GUI pixels.
4. Function is small (< ~60 lines) but load-bearing (called elsewhere in `Mod/`).

## Step 2 — Test derivation (the hidden-test suite = the whole grade)

The verifier grades ONLY by running the tests in `test_patch` (task-schema.md §4), so tests
are the most important artifact. Base rule: **write tests on CURRENT (correct) code first —
this is the PASS_TO_PASS base.** Every test must pass on the correct code before any bug is
injected.

Test-writing heuristics (in preference order):
1. **Property / round-trip tests** — discriminate any mutation without magic numbers
   (e.g. *the involute point at parameter t sits at polar angle t − atan(t)*).
2. **Boundary tests** — the identity point (`genInvolutePolar(Rb, Rb) == 0`).
3. **Known closed-form values** — derived independently of the implementation's own formula.
4. **Error-class tests** — "must return a finite value", "must not raise" (catches crash-type
   bugs).

**RUN-gate A (correctness gate):** `pytest tests/... -q` on the correct workspace must exit
0. In the worked example this gate caught a real bug in MY OWN test: v1 of the round-trip
test assumed the involute parameter equals the polar angle; it failed on CORRECT code
(`t=0.2 → got 0.002604 = 0.2 − atan(0.2)`), proving the wrong assumption before shipping.
Tests were fixed to the true identity. This is the gate doing its job.

## Step 3 — Bug injection (ONE realistic mutation per task)

Operators, each with a canonical example diff on `Mod/PartDesign/fcgear/involute.py`:

**(a) Off-by-one / budget trim** — DESIGNED-NOT-RUN
```diff
--- a/Mod/PartDesign/fcgear/involute.py
+++ b/Mod/PartDesign/fcgear/involute.py
@@ -376,7 +376,7 @@
-    for i in range(6):
+    for i in range(3):
```
Newton solver loses its convergence budget → `RuntimeError: No convergence after 3
iterations.` on shallow roots.

**(b) Wrong default** — DESIGNED-NOT-RUN
```diff
--- a/Mod/PartDesign/fcgear/involute.py
+++ b/Mod/PartDesign/fcgear/involute.py
@@ -30,7 +30,7 @@
-def CreateExternalGear(
-    w, m, Z, phi, split=True, addCoeff=1.0, dedCoeff=1.25, filletCoeff=0.375, shiftCoeff=0.0
-):
+def CreateExternalGear(
+    w, m, Z, phi, split=True, addCoeff=1.25, dedCoeff=1.25, filletCoeff=0.375, shiftCoeff=0.0
+):
```
Gear teeth one quarter-module too tall; every generated gear silently malformed.

**(c) Dropped edge case** — DESIGNED-NOT-RUN
```diff
--- a/Mod/PartDesign/fcgear/involute.py
+++ b/Mod/PartDesign/fcgear/involute.py
@@ -246,8 +246,8 @@
     fe = 1  # fraction of involute length at end of approx
-    fs = 0.01  # fraction of length offset from base to avoid singularity
+    fs = 0.0  # fraction of length offset from base
```
The singularity guard the comment warns about is removed → division blow-up for
non-involute flanks.

**(d) Operand swap / sign flip** — RUN (as task `freecad_90002`)
```diff
--- a/Mod/PartDesign/fcgear/involute.py
+++ b/Mod/PartDesign/fcgear/involute.py
@@ -343,7 +343,7 @@
-    return (sqrt(R * R - Rb * Rb) / Rb) - acos(Rb / R)
+    return (sqrt(R * R - Rb * Rb) / Rb) - acos(R / Rb)
```
→ `ValueError: math domain error` for every R > Rb (the whole useful involute). [RUN:
3/3 tests fail on this variant]

**(e) Wrong operand in expression** (subclass of (d)) — RUN (as task `freecad_90001`)
```diff
--- a/Mod/PartDesign/fcgear/involute.py
+++ b/Mod/PartDesign/fcgear/involute.py
@@ -343,7 +343,7 @@
-    return (sqrt(R * R - Rb * Rb) / Rb) - acos(Rb / R)
+    return (sqrt(R * R - Rb * Rb) / R) - acos(Rb / R)
```
→ silent wrong (even negative) angles; 2/3 tests fail on this variant. [RUN]

**Injection rules:** exactly ONE mutation per task; must compile; must keep the module
importable; **RUN-gate B (discrimination gate):** the derived tests must FAIL on the buggy
variant (any failure counts — there is no stored FAIL_TO_PASS list, but an undetected bug
makes the task trivially "resolvable" by doing nothing, which fails honesty, not just
quality). Rejection rate expectation: some mutations slip past tests → discard the task,
don't weaken the tests.

## Step 4 — problem_statement derivation (from the BUG'S OBSERVABLE BEHAVIOR)

The statement is written as a user bug report about behavior, produced AFTER running the
buggy variant, quoting values actually captured from the RUN. Rules:
1. Never quote or paraphrase the fix, never mention identifiers-only-a-diff-would-know
   ("divide by Rb" is forbidden; "the returned angle is wrong / negative / raises" is
   required).
2. Include a runnable pure-python repro with real captured outputs (e.g. the `-0.0012794…`
   value in `freecad_90001` is a RUN-captured number, not invented).
3. State the invariant the reporter expects ("angle must be 0 at R=Rb, grow monotonically,
   agree with t − atan(t)").
4. Length target ≈ the real-data median (418 chars) to ~1.5k; richer than that is fine
   (real max is 10k).

## Step 5 — Snapshot packaging (Mod subtree → repo snapshot at base_commit)

1. Layout mirrors upstream paths so diffs read `-p1 a/Mod/PartDesign/fcgear/involute.py`.
2. Workspace = snapshot root = buggy code + (later, via test_patch) `tests/`.
3. Add a minimal `pyproject.toml` stub (`[tool.setuptools] packages = []; py-modules = []`)
   so the harness's "installs `/workspace` in editable mode" baseline step has something
   valid to install. [DESIGNED-NOT-RUN against the real harness; the stub itself is
   exercised locally]
4. `git init && git add -A && git commit` → the commit SHA is `base_commit` (real 40-hex
   SHAs in the worked examples: `5721f84f…`, `08f57c23…`). [RUN]
5. Gold `patch` = `git diff` of buggy→correct (applies cleanly by construction; verified
   with `git apply --check`). [RUN]
6. `test_patch` = new-file diff of `tests/test_*.py` (same `@@ -0,0 +1,N @@` form row 1 of
   the real data uses). [RUN]
7. `instance_id` = `freecad_9xxxx` synthetic namespace; `repo` = `FreeCAD/FreeCAD`;
   `hints_text` = `""`; `created_at` = generation timestamp.

## Step 6 — Verification (exactly what the harness will do)

Hidden tests = the derived tests from Step 2. Resolution = the harness's own criterion
(pytest exit 0 + JUnit `passed_tests > 0, failures == 0, errors == 0`, every test node
extracted from `test_patch` passed, none skipped; 300 s timeout). Factory-side pre-ship
loop, RUN on both worked examples:

1. `git apply --check gold_patch.diff` / `git apply --check test_patch.diff` on the
   snapshot → both OK. [RUN]
2. Apply both → `pytest tests/... -q --junitxml=…` → exit 0, `3 passed`, JUnit
   `failures="0" errors="0" skipped="0"`. [RUN]
3. Restore snapshot to baseline (`git checkout -- .`), delete applied tests → 0 dirty
   paths. [RUN]

(Local emulation note: the harness runs `PYTHONNOUSERSITE=1` with system-installed pytest;
on this Windows box pytest lives in the user site, so the local emulation drops that one
env var. Everything else matches the documented invocation.)

## Scaling estimate

Scripted end-to-end (selector → tests → mutation → gates → snapshot → emit), the only
non-mechanical steps are writing 2–4 tests and one bug report per task (~5–10 min of author
or LLM time); the gates are seconds of CPU. Expect **~15–25 tasks/hour** with an author in
the loop, **~40–60 tasks/hour** once test-writing is LLM-generated with the RUN gates
auto-rejecting bad rows. Pool: ~100–150 usable pure-python files × ~4–8 targetable
functions × 2–3 mutation variants ≈ **1,000–3,000 tasks** reachable from this one FreeCAD
install, all with real base_commits, real diffs, and run-verified gates.

## Worked artifacts (in this directory)

- `example-tasks.jsonl` — 2 full tasks in the exact schema.
- `examples/task_0001/` — `workspace-correct/`, `workspace-buggy/`, `gold_patch.diff`,
  `test_patch.diff`, `base_commit.txt`.
- `examples/task_0002/` — same layout.
- `snapshots/freecad_90001/`, `snapshots/freecad_90002/` — git snapshot repos at the buggy
  baseline (the `base_commit` SHAs are their HEADs).
- `RUN_LOG.md` — every command and its captured output.

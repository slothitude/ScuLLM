# RUN LOG — receipts for every executed claim (2026-11-12, Windows 11, Python 3.13.13, pytest 8.4.2, git 2.53.0)

Everything below was actually executed on this machine. Anything NOT in this file that the
spec or examples claim is DESIGNED-NOT-RUN.

## 1. Competition schema extraction — RUN

`C:\Users\aaron\evo\state\gemma\eval\starter\tasks.jsonl`: 129 lines.

- All 129 rows share one 8-key keyset, same order:
  `instance_id, repo, base_commit, patch, test_patch, problem_statement, hints_text, created_at`.
- `hints_text` empty in 129/129 rows. `instance_id` unique 129/129.
- patch length min/median/max: 176 / 1,159 / 308,489 chars. test_patch: 344 / 1,671 / 133,966.
  problem_statement: 42 / 418 / 10,095.
- repo distribution: fastapi/fastapi 67, Textualize/rich 48, psf/requests 13, encode/httpx 1.
- No FAIL_TO_PASS / PASS_TO_PASS anywhere (verified by full-file keyset scan).
- Verifier semantics quoted from `HARNESS_README.md` §8 (apply agent_patch → apply
  test_patch → hermetic pytest → exit 0 + JUnit gates). Verbatim command quoted in
  task-schema.md §4.

## 2. Source harvest — RUN

Scan of `C:\Program Files\FreeCAD 1.1\Mod\` (READ-ONLY; md5 verified the copy):
`Mod/PartDesign/fcgear/involute.py` md5 `a93991272173bc526f6cfb2f6b7f4852` — identical on
both sides. 478 lines. 394 `*.py` files in `Mod/` import no FreeCAD/Qt/Part/Mesh/... module.
`involute.py` line 374 (verbatim): "this file doesn't depend on FreeCAD, a property very
handy when testing in isolation, so let's keep it."

## 3. Derived tests on CORRECT code — RUN (Gate A)

```
$ python -m pytest tests/test_involute_involute_polar.py -v        # task_0001/workspace-correct
tests/test_involute_involute_polar.py::test_angle_is_zero_at_base_circle PASSED [ 33%]
tests/test_involute_involute_polar.py::test_known_angle_r10_r20 PASSED   [ 66%]
tests/test_involute_involute_polar.py::test_parametric_roundtrip PASSED  [100%]
============================== 3 passed in 0.08s ==============================

$ python -m pytest tests/test_involute_involute_polar.py -v        # task_0002/workspace-correct
tests/test_involute_involute_polar.py::test_returns_finite_angle_above_base_circle PASSED [ 33%]
tests/test_involute_involute_polar.py::test_known_angle_r10_r20 PASSED   [ 66%]
tests/test_involute_involute_polar.py::test_parametric_roundtrip PASSED  [100%]
============================== 3 passed in 0.02s ==============================
```

Gate A catch (the honest part): v1 of `test_parametric_roundtrip` asserted
`genInvolutePolar(Rb, R(t)) == t` and FAILED on the correct code:

```
t=0.2: R=10.198039 got=0.002604440 diff=-1.97e-01
t=0.7: R=12.206556 got=0.089274036 diff=-6.11e-01
t=1.4: R=17.204651 got=0.449453159 diff=-9.51e-01
```

The assumption was wrong (the function returns the swept polar angle t − atan(t), not the
involute parameter t). Tests were corrected to the true identity, then re-passed. Captured
buggy-variant values quoted in the problem_statement (e.g. `0.08927403580619446`,
`-0.0012794247116967583`) come from these RUNs.

## 4. Bug variants vs derived tests — RUN (Gate B)

```
$ cd task_0001/workspace-buggy && python -m pytest tests/test_involute_involute_polar.py -v
FAILED tests/test_involute_involute_polar.py::test_known_angle_r10_r20
FAILED tests/test_involute_involute_polar.py::test_parametric_roundtrip
========================= 2 failed, 1 passed in 0.11s ==========================
(obtained -0.0012794247116967583, expected 0.002604440150119236)

$ cd task_0002/workspace-buggy && python -m pytest tests/test_involute_involute_polar.py -v
E       ValueError: math domain error
Mod\PartDesign\fcgear\involute.py:346: ValueError
FAILED tests/test_involute_involute_polar.py::test_returns_finite_angle_above_base_circle
FAILED tests/test_involute_involute_polar.py::test_known_angle_r10_r20
FAILED tests/test_involute_involute_polar.py::test_parametric_roundtrip
============================== 3 failed in 0.12s ==============================
```

## 5. Snapshots — RUN

```
freecad_90001 base_commit = 5721f84fbbe26e05ae7a8cd5f32796dc930a322b
freecad_90002 base_commit = 08f57c231fbcb57708b9a98de23a2b04024e6d52
```
(`git init` + commit of the buggy workspace + pyproject stub; `core.autocrlf false`;
post-run `git status --porcelain` = 0 dirty paths.)

## 6. Patch apply + verify loop — RUN

```
=== freecad_90001 ===  git apply --check gold_patch.diff: OK   test_patch.diff: OK
3 passed in 0.04s      pytest exit_code = 0
junit: tests="3" ... errors="0" failures="0" skipped="0"
=== freecad_90002 ===  git apply --check gold_patch.diff: OK   test_patch.diff: OK
3 passed in 0.04s      pytest exit_code = 0
junit: tests="3" ... errors="0" failures="0" skipped="0"
```

Local-emulation deviation from the harness command (declared): the harness runs
`PYTHONNOUSERSITE=1` with system pytest; on this box pytest is in the user site
(`C:\Users\aaron\AppData\Roaming\Python\Python313\site-packages`), so that flag was dropped
locally. `PYTHONSAFEPATH=1` was kept.

## 7. Schema emission — RUN

`example-tasks.jsonl`: 2 rows, each parsed back with `json.loads`, key order asserted equal
to the competition keyset:

```
row 0: freecad_90001  base=5721f84fbbe2  patch=477B  test_patch=1975B  ps=1357ch  hints=''  created=2026-11-12T10:21:44Z
row 1: freecad_90002  base=08f57c231fbc  patch=478B  test_patch=1745B  ps=735ch  hints=''  created=2026-11-12T10:21:44Z
KEY ORDER == competition schema: OK
```

## DESIGNED-NOT-RUN (and why)

1. **swegemma harness end-to-end (`swegemma eval` in its two-container docker lifecycle)** —
   the docker sandbox lane is not available in this session; steps 6 above emulate the
   documented verify flow locally instead.
2. **Mutation examples (a)–(c) in factory-spec.md (off-by-one, wrong default, dropped edge
   case)** — documented operator examples; not injected/run in this session. The two
   injected mutations (operand swap, wrong operand) ARE run (§4).
3. **FreeCAD GUI/API behavior of involute.py inside FreeCAD** — unnecessary: the module is
   stdlib-only and was exercised directly.
4. **Editable-install of the snapshot pyproject stub by the real harness** — stub authored,
   not pip-installed here.

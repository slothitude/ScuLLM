# VALIDATE_REPORT.md — W-VALID rebuild of the WO-B7 bundle validator

Date: 2026-11-13 · Worker: Muse builder (SCULLM W-VALID) · Harness dir: `submission\tools\wvalid\`

**What this is:** `C:\Users\aaron\scullm\submission\tools\validate_submission.py` — a rebuild of
the missing WO-B7 validator (`work-plan.md` line 1116 records "B7: `VALIDATE: PASS`"; the script
itself was absent from BOTH trees — evo pre-migration and scullm post-migration — as measured and
reported by W-DIST-1 in `submission\dist\package-report.md` section 2). It is a **thin orchestrator,
not a new validator**: the official wheels (`adk_submission.validate_directory` +
`adk_submission.compile_submission`, installed from `eval\wheelhouse\` into an isolated
`--no-deps --target` dir, never user-site) are the judge. The script only front-runs the checks the
competition notebook itself establishes before the wheels run, so hygiene failures surface first.

## 1. Ground truth the script implements (every constant cites its source)

| Check | Source of the rule |
|---|---|
| Allowed extensions only `.yaml .yml .md .txt .py .json .safetensors` | `eval\proof\PIPE-PROOF.md` mechanical fix 5 (quoted verbatim in package-report section 1) |
| No `corpus/` directory | PIPE-PROOF fix 5 M2 action |
| No `.out` files | PIPE-PROOF fix 5 (names `provenance/compute-adapter-budget.out`) |
| Exactly one root config among `agent.yaml/agent.yml/root_agent.yaml/root_agent.yml`; no symlinks; total < 3 GiB; `!include` targets exist inside the bundle | Notebook `eval\kernels\gemma-4-developer-agent-baseline-harness.ipynb` cell 5 |
| Every declared tool name within the nine known (`run_command, read_file, edit_file, write_file, get_code_neighbors, search_similar_code, get_code_subgraph, get_status, submit_patch`) | `submission\README.md` "Tool budget" section |
| Exactly one unique base model, one of the four ALLOWED_MODELS; adapter key state reported | Notebook cell 5 + README "Single base model (section 3.2)"; adapter names read from the commented lines in `agent.yaml` / `sub_agents\code_analyzer.yaml` |
| `build_submission_limits()` -> `validate_directory(BUNDLE, limits)` | Notebook cell 7 code (the cell under the markdown heading "## 3. Official Harness Compilation Check") |
| `discover_declared_models` == {model}; `compile_submission` with the nine-tool registry; model registered as `LiteLlm(model="openai/<model>", api_base="http://127.0.0.1:9/v1", api_key="EMPTY")` | Notebook cell 7, replicated exactly as package-report section 3 records it for our nine-tool tree |
| Six notebook stubs verbatim + three compile-time-only graph-tool stubs | Notebook cell 7 stub signatures; package-report section 3 ("compile-time stubs only; on the eval runtime they are harness builtins"; `ToolNotFoundError: Tool 'get_code_neighbors' not found in registry` otherwise) |
| Wheels installed `pip install --no-deps --target` into `submission\dist\.tmp\wheels`, plus `aiohttp>=3.10` into the same target | package-report section 3 (user-site aiohttp 3.9.1 breaks the litellm import) |

**Deliberately NOT gated, with evidence:** the notebook cell-5 markdown-placeholder assertion
(`{problem_description}`/`{hints}` only in `.md`/`.txt`). The banked bundle's own documentation
prose legitimately contains braces, and the official judge passes this exact tree, so replicating
that assertion would fail honest documentation. Measured scan of the current bundle:
`adapter-budget.md`, `freecad-factory\task-schema.md`, and `tools\gemma_dryrun.txt` each carry
non-state-var brace groups; `prompts\system.md` is state-vars only. The script's docstring records
this exclusion.

## 2. Self-test 1 — the real pruned bundle: PASS (exit 0)

Command: `python C:/Users/aaron/scullm/submission/tools/validate_submission.py` (no argv; defaulted
to `submission\dist\bundle\`, 34 files — matching package-report section 5's 34 zip entries). Full
raw transcript, pasted verbatim (warnings included; also kept at
`submission\tools\wvalid\selftest1-pass.raw`):

```
C:\Users\aaron\AppData\Roaming\Python\Python313\site-packages\requests\__init__.py:113: RequestsDependencyWarning: urllib3 (2.8.0) or chardet (7.4.0.post2)/charset_normalizer (3.3.2) doesn't match a supported version!
  warnings.warn(
C:\Users\aaron\scullm\submission\dist\.tmp\wheels\google\adk\features\_feature_decorator.py:72: UserWarning: [EXPERIMENTAL] feature FeatureName.SKILL_TOOLSET is enabled.
  check_feature_enabled()
validator: C:\Users\aaron\scullm\submission\tools\validate_submission.py
python: 3.13.12
bundle: C:\Users\aaron\scullm\submission\dist\bundle
wheel target (isolated, never user-site): C:\Users\aaron\scullm\submission\dist\.tmp\wheels
[a] structural hygiene on C:\Users\aaron\scullm\submission\dist\bundle
[a] files=34 bytes=348687 (< 3221225472 3 GiB cap: True)
[a] root config: agent.yaml
[a] declared tool names (9): ['edit_file', 'get_code_neighbors', 'get_code_subgraph', 'get_status', 'read_file', 'run_command', 'search_similar_code', 'submit_patch', 'write_file']
[b] single-base model law
[b] declared model: 'gemma-4-e2b-it-qat-w4a16-ct' in 2 yaml file(s): agent.yaml -> gemma-4-e2b-it-qat-w4a16-ct; sub_agents/code_analyzer.yaml -> gemma-4-e2b-it-qat-w4a16-ct
[b] adapter state: agent.yaml: adapter key commented out (crow_lora)
[b] adapter state: sub_agents/code_analyzer.yaml: adapter key commented out (analyzer_lora)
[c] official validate_directory via the wheelhouse wheels
[wheels] reusing provisioned target C:\Users\aaron\scullm\submission\dist\.tmp\wheels (5 dist-infos; last provisioned by a prior run)
[c] adk_submission resolved: C:\Users\aaron\scullm\submission\dist\.tmp\wheels\adk_submission\__init__.py (inside target: True)
[c] swegemma resolved: C:\Users\aaron\scullm\submission\dist\.tmp\wheels\swegemma\__init__.py (inside target: True)
[c] google.adk resolved: C:\Users\aaron\scullm\submission\dist\.tmp\wheels\google\adk\__init__.py (inside target: True)
[c] validate_directory: PASSED
[d] official compile_submission with the nine-tool registry
[d] discover_declared_models: ['gemma-4-e2b-it-qat-w4a16-ct']
[d] compile_submission: PASSED (root_agent='crow', tools=9)
VALIDATE: PASS
EXIT=0
```

The `compile_submission: PASSED (root_agent='crow', tools=9)` line matches the independent receipt
in `submission\dist\package-report.md` section 3 byte for byte.

## 3. Self-test 2 — poisoned copy: FAIL with reason (exit 1)

Method: bundle copied to `submission\tools\wvalid\poison-test\bundle\` (a temp dir under scullm),
`leak.jsonl` planted in its root, validator re-run against it; the temp dir was deleted afterward.
Full raw transcript, pasted verbatim (also kept at
`submission\tools\wvalid\selftest2-fail.raw`; note the run fails at check (a) before the wheels
import, so no wheel warnings appear):

```
validator: C:\Users\aaron\scullm\submission\tools\validate_submission.py
python: 3.13.12
bundle: C:\Users\aaron\scullm\submission\tools\wvalid\poison-test\bundle
wheel target (isolated, never user-site): C:\Users\aaron\scullm\submission\dist\.tmp\wheels
[a] structural hygiene on C:\Users\aaron\scullm\submission\tools\wvalid\poison-test\bundle
VALIDATE: FAIL — check(a): forbidden extension '.jsonl' (PIPE-PROOF fix 5): leak.jsonl
EXIT=1
```

Last-line contract holds both ways: `VALIDATE: PASS` is the last line on success, the
`VALIDATE: FAIL — <reason>` line on failure, with exit codes 0 / 1.

## 4. Additional robustness probes (same session, both cleaned up afterward)

- **corpus/ poison variant**: `corpus/rows.jsonl` planted -> `VALIDATE: FAIL — check(a):
  forbidden extension '.jsonl' (PIPE-PROOF fix 5): corpus/rows.jsonl`, exit 1. Then with an
  otherwise-allowed `corpus/notes.md` -> `VALIDATE: FAIL — check(a): corpus/ directory present
  (PIPE-PROOF fix 5 M2 action): corpus/notes.md`, exit 1 — proving the corpus/ rule is extension-
  independent, as fix 5 requires.
- **Cold-start wheel provisioning**: with a fresh empty target, `ensure_wheels` ran the recorded
  recipe (`pip install --no-deps --target` of the five wheelhouse wheels, then `aiohttp>=3.10`
  into the same target) and the freshly provisioned target imported cleanly and passed
  `validate_directory` on the real bundle. This proves the script works from a cold machine, not
  only against W-DIST-1's pre-provisioned dir.

## 5. py_compile and hygiene

`python -m py_compile submission/tools/validate_submission.py` -> OK (ran twice). The
`__pycache__\validate_submission.cpython-313.pyc` it produced was deleted afterward; the
pre-existing `train_crow_gemma.cpython-313.pyc` in the same cache dir was left untouched. All
probe dirs (`poison-test\`, `provision-test\`) were deleted; the only files this task leaves in
`wvalid\` are this report's raw transcripts (`selftest1-pass.raw`, `selftest2-fail.raw`), the
task brief, and the state log.

## 6. Boundary + gates

- Writes confined to `C:\Users\aaron\scullm\submission\tools\` (the script, this report, the
  wvalid harness dir) plus one `__pycache__` entry, deleted. The shared wheel target
  `submission\dist\.tmp\wheels\` was reused as-is (its provisioning predates this task, per
  package-report section 3); nothing outside `scullm\` was read for writes or modified.
- No upload, no zip change, no bundle edit. The bundle at `submission\dist\bundle\` was only read.
- Owner-gate reminders unchanged from package-report: upload = OWNER GATE 4 (1/day channel).

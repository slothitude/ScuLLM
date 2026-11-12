# swegemma Competition Task Schema — extracted from real rows

Source of truth: `C:\Users\aaron\scullm\eval\starter\tasks.jsonl` (129 rows) plus
`HARNESS_README.md` (same directory) for verifier semantics. **Every quote below is verbatim
from the data.** All claims labeled RUN (measured by script on this machine, 2026-11-12) or
README (quoted from HARNESS_README.md).

(path retargeted 2026-11-13 — project moved to C:\Users\aaron\scullm; the measured numbers themselves are unchanged)

## 1. File shape

- 1 JSON object per line (JSONL), UTF-8. 129 lines. [RUN]
- **Every one of the 129 rows has exactly the same 8 keys, in the same order** (checked with
  `collections.Counter` over key tuples — a single keyset, 129 occurrences): [RUN]

```
instance_id, repo, base_commit, patch, test_patch, problem_statement, hints_text, created_at
```

- **There is NO `FAIL_TO_PASS` and NO `PASS_TO_PASS` field.** These SWE-bench names do not
  occur anywhere in the file (all 129 rows scanned). [RUN] Resolution is computed by the
  harness at verify time instead — see §4.

## 2. Field-by-field

### `instance_id` — string, unique row id
Format `{repo_dirname_lowercase}_{PR_number}`. Examples: `fastapi_15661`, `fastapi_15588`,
`fastapi_15589`. All 129 unique. [RUN]

### `repo` — string, GitHub `owner/name`
Distribution across the 129 starter rows: `fastapi/fastapi` ×67, `Textualize/rich` ×48,
`psf/requests` ×13, `encode/httpx` ×1. [RUN]

### `base_commit` — string, 40-char lowercase hex git SHA
The snapshot the agent starts from. Example: `ee22a4b8ca46dcce26c8c183afc4992a888d8be2`. [RUN]

### `patch` — string, unified diff — **the GOLD solution, never shown to the agent**
Standard git diff with `-p1` prefixes:

```diff
--- a/fastapi/sse.py
+++ b/fastapi/sse.py
@@ -33,10 +33,20 @@ class EventSourceResponse(StreamingResponse):
...
-def _check_id_no_null(v: str | None) -> str | None:
+def _check_single_line(v: str | None, field_name: str) -> str | None:
```

New files use the `@@ -0,0 +1,N @@` form (row 1 adds `scripts/prepare_release.py` this way).
Length stats over 129 rows: min 176 / median 1,159 / max 308,489 chars. [RUN]
The verifier does **not** apply `patch`; the agent's own `agent_patch` is what gets applied
(README §8 flow: apply agent_patch → apply task.test_patch → pytest).

### `test_patch` — string, unified diff — **the hidden tests, applied by the verifier**
Same diff format, touches only test files. Example (row 2, appended to an existing file):

```diff
--- a/tests/test_sse.py
+++ b/tests/test_sse.py
@@ -221,6 +221,15 @@ def test_server_sent_event_null_id_rejected():
+@pytest.mark.parametrize("field_name", ["event", "id"])
+def test_server_sent_event_single_line_fields_reject_newlines(
...
```

Row 1 creates a whole new file (`--- a/tests/test_prepare_release.py`, `@@ -0,0 +1,307 @@`) —
so a factory adding a brand-new test file is a pattern already present in the real data.
Length stats: min 344 / median 1,671 / max 133,966 chars. [RUN]

### `problem_statement` — string — **the agent's ONLY task description**
Verbatim GitHub PR text in the starter rows (emoji title, PR template, description,
checklists). Row 2 begins:

```
♻️ Validate Server Sent Event fields to avoid applications from sending broken data

## Pull Request
...
```

Length stats: min 42 / median 418 / max 10,095 chars. [RUN] Injected into the agent prompt as
`{problem_description}` (README §5.1/§5.2: "Problem Statement:
{task.problem_statement}").

### `hints_text` — string — agent-visible hints, optional
**Empty in 129/129 starter rows.** [RUN] README §5.2: the Hints section is "included if
`task.hints_text` is non-empty"; §5.1: `hints` is "only present if `task.hints_text` is
non-empty". Factory convention: emit `""`.

### `created_at` — string, ISO-8601 UTC with `Z`
Example: `2026-05-31T16:00:39Z`. [RUN]

## 3. Who sees what

| Field | Agent sees | Verifier uses |
|---|---|---|
| `instance_id` | no (prompt header uses `repo`) | row identity |
| `repo` | yes (prompt header: "repository {task.repo}") | — |
| `base_commit` | no (harness checks out the snapshot) | snapshot setup |
| `patch` (gold) | **never** | reference only; not applied |
| `test_patch` | **never** (agent test-file edits are stripped) | hidden tests |
| `problem_statement` | **yes** — the task itself | — |
| `hints_text` | yes, only if non-empty | — |
| `created_at` | no | — |

Agent test-file protection (README §8.3): modifications the agent makes to
`test_*.py`/`*_test.py`/`tests/**` or runner configs (`conftest.py`, `pytest.ini`,
`pyproject.toml`, ...) "are stripped and discarded before `task.test_patch` is applied".

## 4. Resolution criterion (what the verifier actually does)

README §8, verbatim order of Container B:

> 10. Apply agent_patch (4-pass resilient git apply / patch)
> 12. Apply task.test_patch
> 13. Run hermetic pytest on target test files
> 14. exit_code == 0 -> resolved = True (score = 1.0)

The exact pytest invocation (README §8.4):

```bash
cd /workspace && PYTHONSAFEPATH=1 PYTHONNOUSERSITE=1 python3 -s -m pytest <pytest_targets> \
  --junitxml=/tmp/_swegemma_junit_<id>.xml \
  -p no:anyio -o timeout=0 \
  -o python_classes="Test* *Test" -q
```

Resolution (README §8.5): `resolved = True` **iff** (1) pytest exits 0 **and** (2) the JUnit
XML "exists, has `passed_tests > 0`, `failures == 0`, `errors == 0`, and every required test
node (`FAIL_TO_PASS`, `PASS_TO_PASS`, or **test functions extracted from `test_patch`**)
explicitly passed without being skipped". The required-node set is therefore **derived from
`test_patch` at verify time** — no stored list. Score = Resolution Rate = resolved / total.
Verification timeout: 300 s (fixed).

## 5. Factory implications (summary)

1. Emit exactly 8 fields, in the order above, one JSON object per line. No extra fields.
2. The hidden-test suite is the whole grading surface → derived tests must (a) pass on
   correct code, (b) fail on the buggy base, (c) be inside `tests/` so agent tampering is
   stripped anyway.
3. `patch` is emitted as gold reference (diff buggy→correct); it is not the grading
   mechanism.
4. `hints_text` stays `""`; `created_at` is the generation timestamp.

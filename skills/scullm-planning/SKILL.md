---
name: scullm-planning
description: Write execution plans in the SCULLM line grammar and self-check them with scullm_check.py before acting; fix until the checker says PASS.
---

# SCULLM planning loop

Write the plan as a .scullm text file BEFORE acting. Then check it. Walk only plans the checker passed. The checker ships beside this file.

1. Write the plan to /tmp/plan.scullm.
2. Check it: `python3 scullm_check.py /tmp/plan.scullm` (run from this skill's directory).
3. FAIL (exit 1)? Read the first FAIL line. It names a line number. Fix that line only. Re-check.
4. PASS (exit 0)? Walk it: start at the first node defined, run what each node says, follow its edges.
5. A gate in the plan = a real check before the next step. If it fails, take the labeled failure edge, never skip ahead.

Keep plans small: 5-12 nodes. One decision per gate. `#` starts a comment. Blank lines are ignored.

## Grammar

```
plan "objective"                          # exactly one plan line per file
ID: KIND "one string" edge|attr ...       # node line
ID: jump ID                               # goto form: no string

ID    := [A-Za-z0-9_]+
KIND  := action | gate | code | done | replan | jump | flag | goal
edge  := LABEL [guard]... -> (ID | replan)
guard := "[" ( obs~ PATTERN | need NAME ) "]"
attr  := loop N
```

STRING is double-quoted with no raw newline. That is the only quoting rule.

Node kinds (one string each):

- `action "cmd"` - run a shell command.
- `gate "question?" edges...` - branch. A gate MUST have edges and every edge MUST have a label.
- `code "instruction"` - hand to the coder.
- `done "text"` - success end.
- `replan "reason"` - return to the planner with the reason.
- `jump ID` - 0-tick goto.
- `flag "name"` - record a milestone. It is terminal: add `next->ID` to keep walking.
- `goal "text" flags=a,b` - end goal; finishes only when every named flag was recorded by a flag node.

Edges and attributes:

- Gate edges carry labels: `yes->n2 no->n3`. First matching label whose guards hold fires.
- Unlabeled edge = FAIL. Non-gate node: at most one edge. No edge on a non-gate node = fall through to the next-defined node.
- Guards: `yes[obs~uid=]->n4` (regex vs last output, case-insensitive) and `yes[need user]->n5` (milestone `user` already recorded). Combine: `yes[obs~ham\{][need user]->n7`. All guards must hold.
- `loop 2` on a node: visit budget. Arrival N+1 replans. One loop per node.
- Edge targets must be defined nodes, or the keyword `replan`. A `jump` target must be a defined node.

Laws:

- The first node defined is the entry. Cycles are allowed.
- Exactly one plan line. One STRING per node. At least one done/goal reachable from the entry.
- State (ticks, outputs, flags) lives in the walker. Never write state in the file.

## Example - SWE fix (fixtures/valid.scullm, checker PASS)

```
# swe fix: locate -> reproduce -> minimal edit -> test -> submit
plan "fix Window.slice IndexError in src/window.py"

w0: action "grep -n 'def slice' src/window.py; read the slice body"
w1: action "run repro: python3 -c 'from window import Window; Window(3).slice(0,5)'"
w2: gate   "repro raises IndexError?"                 yes->w3  no->w5
w3: code   "edit slice: stop = min(stop, len(self.values))"
w4: gate   "repro passes now?"                        yes->w6  no->replan
w5: replan "wrong defect site: relocate and re-read"
w6: flag   "repro_clean"                              next->w7
w7: action "python3 -m pytest tests/test_window.py -x -q"
w8: gate   "tests pass?"                              yes->w10  no->w9
w9: code   "fix the failure surfaced by tests"        loop 2
w9b: gate  "fixed?"                                   yes->w7  no->replan
w10: gate  "milestone set?"                           yes[need repro_clean]->w11  no->replan
w11: goal  "patch verified, submit"                   flags=repro_clean
```

## Example - recovery: gate fails -> replan (checker PASS)

```
# recovery: primary fix fails the gate, fallback once, then replan
plan "make make test green: primary fix, fallback, replan"

r0: action "make test 2>&1 | tail -20"
r1: gate  "compile error?"                        yes->r2  no->r5
r2: code  "fix the compile error"                 loop 2
r3: gate  "builds now?"                           yes->r6  no->r4
r4: gate  "same error class as before?"           yes->r11 no->r2
r5: replan "not a compile problem: gather runtime logs"
r6: flag  "build_green"                           next->r7
r7: action "make test 2>&1 | tail -5"
r8: gate  "tests pass?"                           yes->r10 no->r9
r9: code  "apply the fallback fix"                loop 1
r9b: gate "tests pass now?"                       yes->r7  no->r11
r10: goal "tests green, report success"           flags=build_green
r11: replan "primary and fallback failed: widen scope"
```

## Verified

`python3 scullm_check.py fixtures/...` on the three fixtures:

```
$ python3 scullm_check.py fixtures/valid.scullm
PASS: 13 nodes, entry w0, 5 gate(s), 16 edge(s), end/goal reachable: w11    (exit 0)

$ python3 scullm_check.py fixtures/invalid_kind.scullm
FAIL: line 5: not a node/plan/comment line: 'a1: verify "run the tests" ...'
scullm_check: FAIL (1 error(s); first at line 5)                            (exit 1)

$ python3 scullm_check.py fixtures/broken_edge.scullm
FAIL: line 5: node b1: edge yes->b9 targets an undefined node
scullm_check: FAIL (1 error(s); first at line 5)                            (exit 1)
```

The checker's regexes and `parse_guard` are copied verbatim from the reference parser (omniflow/interp/ofl.py) per omniflow/lang/OFL.md. Every plan it accepts parses under the reference parser. It rejects a few things the reference silently ignores (a missing or extra plan line, a second STRING on a node, trailing garbage, an unlabeled gate edge, a done/goal that is unreachable from the entry) - those are the skill contract, so fix them too.

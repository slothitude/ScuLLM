#!/usr/bin/env python3
"""scullm_check.py — deterministic checker for SCULLM plan files (OFL grammar).

Grammar source of truth (READ-ONLY upstream, copied verbatim below):
  omniflow/lang/OFL.md          — the OFL spec (node kinds, edges, guards)
  omniflow/interp/ofl.py        — the reference parser (regexes + parse_guard)

This script VALIDATES ONLY. It never executes plan content. Pure stdlib.

Usage:
    python3 scullm_check.py plan.scullm      # file
    cat plan.scullm | python3 scullm_check.py  # stdin

Output: PASS/FAIL lines. Exit 0 = valid. Exit 1 = invalid; the first FAIL
line carries the first error with its line number. Exit 2 = usage/IO error.

Checks (per OFL.md grammar + parser contract):
  - exactly one plan-line: plan "objective"
  - node kinds: action gate code done replan jump flag goal
  - ID syntax [A-Za-z0-9_]+ ; exactly one STRING per node (jump: no STRING)
  - edge syntax LABEL[guard]* -> (ID | "replan"); guards obs~PATTERN / need NAME
  - loop N attribute (single INT visit budget)
  - gate needs >= 1 labeled edge; non-gate has at most one edge
  - no duplicate node ids; no dangling edge/jump targets
  - a last action/code/gate-chain node with no edge and no successor is an
    error (a `jump` node is exempt: it is a goto)
  - at least one done/goal node reachable from the entry (first node defined)
"""
import re
import sys

# ---- copied verbatim from the reference parser omniflow/interp/ofl.py ----
KINDS = {"action": "action", "gate": "gate", "code": "code",
         "done": "done", "replan": "replan", "flag": "flag", "goal": "goal"}
NODE_RE = re.compile(r'^([A-Za-z0-9_]+):\s*(action|gate|code|done|replan|flag|goal)\s+"((?:[^"\\]|\\.)*)"\s*(.*)$')
GOALF_RE = re.compile(r'\bflags=([A-Za-z0-9_,]+)')
JUMP_RE = re.compile(r'^([A-Za-z0-9_]+):\s*jump\s+([A-Za-z0-9_]+)\s*$')
EDGE_RE = re.compile(r'([A-Za-z0-9_][A-Za-z0-9_ ]*?(?:\[(?:\\.|[^\]])*\])*)->([A-Za-z0-9_]+|replan)')
LABEL_RE = re.compile(r'[A-Za-z0-9_]+')
BRACKET_RE = re.compile(r'\[((?:\\.|[^\]])*)\]')
NEED_RE = re.compile(r'^need\s+([A-Za-z0-9_]+)$')
LOOP_RE = re.compile(r'\bloop\s+(\d+)\b')
PLAN_RE = re.compile(r'^plan\s+"((?:[^"\\]|\\.)*)"')
ID_RE = re.compile(r'^[A-Za-z0-9_]+$')  # OFL.md: ID / LABEL / NAME := identifier


def parse_guard(label):
    """Split an edge label into (pure label, guards) — copied from ofl.py.

    "yes[obs~uid=][need user]" -> ("yes", [("obs", "uid="), ("need", "user")])
    Raises ValueError on a malformed bracket suffix.
    """
    m = LABEL_RE.match(label)
    if not m:
        raise ValueError(f"bad edge label: {label!r}")
    pure, guards, pos = m.group(0), [], m.end()
    while pos < len(label):
        bm = BRACKET_RE.match(label, pos)
        if not bm:
            raise ValueError(f"bad guard suffix in edge label: {label!r}")
        body = bm.group(1)
        if body.startswith("obs~"):
            pat = body[4:]
            if not pat:
                raise ValueError(f"empty obs pattern in edge label: {label!r}")
            guards.append(("obs", pat))
        else:
            nm = NEED_RE.match(body)
            if not nm:
                raise ValueError(
                    f"bad guard {body!r} in edge label: {label!r} "
                    f"(want obs~PATTERN or need NAME)")
            guards.append(("need", nm.group(1)))
        pos = bm.end()
    return pure, guards


def count_arrows_outside_brackets(rest):
    """Count `->` tokens outside [guard] brackets (a `->` inside an obs
    regex pattern does not count). More arrows than EDGE_RE matches means
    an unlabeled edge."""
    n, i, depth = 0, 0, 0
    while i < len(rest):
        c = rest[i]
        if c == "\\":
            i += 2
            continue
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
        elif depth == 0 and rest.startswith("->", i):
            n += 1
            i += 2
            continue
        i += 1
    return n


def strip_comment(raw):
    """Drop a trailing `#` comment, honoring `#` inside double-quoted STRINGs."""
    out, in_str, i = [], False, 0
    while i < len(raw):
        c = raw[i]
        if in_str:
            if c == "\\" and i + 1 < len(raw):
                out.append(raw[i:i + 2])
                i += 2
                continue
            if c == '"':
                in_str = False
            out.append(c)
            i += 1
            continue
        if c == "#":
            break
        if c == '"':
            in_str = True
        out.append(c)
        i += 1
    return "".join(out).rstrip()


def check(text):
    """Validate plan text. Returns (errors, info); errors = [(line, msg), ...]."""
    errors = []  # (line_number or 0, message)

    def err(ln, msg):
        errors.append((ln, msg))

    nodes, order, plan_lines = {}, [], []
    for ln, raw in enumerate(text.splitlines(), 1):
        line = strip_comment(raw).strip()
        if not line:
            continue
        pm = PLAN_RE.match(line)
        if pm:
            plan_lines.append(ln)
            continue
        jm = JUMP_RE.match(line)
        if jm:
            nid, dst = jm.groups()
            if nid in nodes:
                err(ln, f"duplicate node {nid} (first at line {nodes[nid]['line']})")
                continue
            nodes[nid] = {"line": ln, "kind": "jump", "jump": dst,
                          "branches": {}, "done": False, "terminal": False}
            order.append(nid)
            continue
        nm = NODE_RE.match(line)
        if not nm:
            err(ln, f"not a node/plan/comment line: {raw.strip()[:60]!r}")
            continue
        nid, kind, body, rest = nm.groups()
        if nid in nodes:
            err(ln, f"duplicate node {nid} (first at line {nodes[nid]['line']})")
            continue
        if '"' in rest:
            err(ln, "extra STRING or stray quote after the node STRING "
                    "(exactly one STRING per node)")
        # loop attr: strip BEFORE edge scanning (reference behavior)
        loops = list(LOOP_RE.finditer(rest))
        if len(loops) > 1:
            err(ln, "multiple loop attributes (want one `loop N`)")
        for m in reversed(loops):
            rest = rest[:m.start()] + rest[m.end():]
        # goal flags attr
        requires = []
        if kind == "goal":
            gm = GOALF_RE.search(rest)
            if gm:
                requires = [x for x in gm.group(1).split(",") if x]
                rest = rest[:gm.start()] + rest[gm.end():]
                for rname in requires:
                    if not ID_RE.match(rname):
                        err(ln, f"bad milestone name in flags=: {rname!r} "
                                f"(want [A-Za-z0-9_]+)")
        # edges
        branches, edge_spans = {}, []
        matches = list(EDGE_RE.finditer(rest))
        if count_arrows_outside_brackets(rest) > len(matches):
            err(ln, "unlabeled edge (write every edge as label->target)")
        if kind == "gate" and not matches:
            err(ln, f"gate {nid} has no edges (a gate must branch)")
        if kind != "gate" and len(matches) > 1:
            err(ln, f"{nid} has multiple edges - use a gate")
        for m in matches:
            lbl, dst = m.group(1), m.group(2)
            edge_spans.append(m.span())
            try:
                pure, _guards = parse_guard(lbl)
            except ValueError as e:
                err(ln, str(e))
                continue
            if kind == "gate":
                if pure in branches:
                    err(ln, f"gate {nid} repeats edge label {pure!r}")
                branches[pure] = dst
            else:
                branches = {"next": dst}
        # leftover garbage (also catches unlabeled edges like bare `->n3`)
        buf = list(rest)
        for a, b in edge_spans:
            buf[a:b] = " " * (b - a)
        leftover = "".join(buf).strip()
        if leftover:
            hint = " (gate edges need labels: yes->n2)" if "->" in leftover and kind == "gate" else \
                   (" (write one edge as next->n2)" if "->" in leftover else "")
            err(ln, f"trailing garbage on node line{hint}: {leftover[:60]!r}")

        done_flag = kind in ("done", "goal")
        terminal = kind in ("done", "goal", "replan", "flag")
        nodes[nid] = {"line": ln, "kind": kind, "jump": None,
                      "branches": branches, "done": done_flag,
                      "terminal": terminal, "requires": requires}
        order.append(nid)

    # plan-line count
    if not plan_lines:
        err(0, 'no plan line found (want exactly one: plan "objective")')
    for ln in plan_lines[1:]:
        err(ln, "extra plan line (exactly one plan line allowed)")
    if not nodes:
        err(0, "no nodes in plan")
        return errors, {"nodes": 0, "entry": None, "ends": [], "gates": 0, "edges": 0}

    # implicit next: non-gate non-terminal node with no edge falls through to
    # the next-defined node; the LAST such node has no successor -> error
    for i, nid in enumerate(order):
        n = nodes[nid]
        if n["kind"] == "gate" or n["terminal"] or n["branches"] or n["jump"]:
            continue
        if i + 1 < len(order):
            n["branches"] = {"next": order[i + 1]}
        else:
            err(n["line"], f"node {nid} is last but has no edge and no successor")

    # dangling targets (edges AND jump gotos die at parse time, not walk time)
    edges = 0
    for nid in order:
        n = nodes[nid]
        if n["jump"] is not None and n["jump"] not in nodes:
            err(n["line"], f"node {nid}: jump targets undefined node {n['jump']}")
        for lbl, dst in n["branches"].items():
            edges += 1
            if dst != "replan" and dst not in nodes:
                err(n["line"], f"node {nid}: edge {lbl}->{dst} targets an undefined node")

    # reachability: entry = first node defined; at least one done/goal reachable
    seen, stack = set(), [order[0]]
    while stack:
        nid = stack.pop()
        if nid in seen or nid not in nodes:
            continue
        seen.add(nid)
        n = nodes[nid]
        if n["jump"] is not None:
            stack.append(n["jump"])
        stack.extend(n["branches"].values())
    ends = [nid for nid in order if nodes[nid]["done"]]
    if not ends:
        err(0, "no done/goal node defined (the plan can never finish)")
    elif not any(nid in seen for nid in ends):
        err(nodes[order[0]]["line"],
            f"no done/goal node reachable from entry {order[0]!r}")

    info = {"nodes": len(order), "entry": order[0],
            "ends": [nid for nid in ends if nid in seen],
            "gates": sum(1 for nid in order if nodes[nid]["kind"] == "gate"),
            "edges": edges}
    return errors, info


def main():
    if len(sys.argv) > 2:
        print("usage: scullm_check.py [plan.scullm]  (no arg = stdin)",
              file=sys.stderr)
        sys.exit(2)
    if len(sys.argv) == 2:
        try:
            with open(sys.argv[1], encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            print(f"scullm_check: cannot read {sys.argv[1]}: {e}", file=sys.stderr)
            sys.exit(2)
    else:
        text = sys.stdin.read()

    errors, info = check(text)
    if errors:
        # errors are appended in scan order: positional errors first (ascending
        # line numbers), aggregate plan-level errors (no line number) after.
        for ln, msg in errors:
            print(f"FAIL: line {ln}: {msg}" if ln else f"FAIL: {msg}")
        print(f"scullm_check: FAIL ({len(errors)} error(s); "
              f"first at line {errors[0][0] or '?'})")
        sys.exit(1)
    print(f"PASS: {info['nodes']} nodes, entry {info['entry']}, "
          f"{info['gates']} gate(s), {info['edges']} edge(s), "
          f"end/goal reachable: {','.join(info['ends']) or 'none'}")
    sys.exit(0)


if __name__ == "__main__":
    main()

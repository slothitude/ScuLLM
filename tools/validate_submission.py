#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_submission.py — the WO-B7 bundle validator, rebuilt as a thin orchestrator.

Provenance (W-VALID, 2026-11-13): the original B7 script was missing from both the
evo and scullm trees (pre-migration gap; see submission/dist/package-report.md
section 2). This file rebuilds it as a THIN ORCHESTRATOR, not a new validator:
the official wheels (adk_submission.validate_directory + compile_submission,
installed from eval/wheelhouse into an isolated --target temp dir, never
user-site) are the judge. The local checks below only front-run what the
notebook's structural pre-check (eval/kernels/gemma-4-developer-agent-
baseline-harness.ipynb, cell 5) and PIPE-PROOF.md mechanical fix 5 already
establish, so hygiene failures surface before the wheels run.

Checks, in order:
  (a) structural hygiene — PIPE-PROOF.md fix 5: allowed extensions only
      .yaml .yml .md .txt .py .json .safetensors; no corpus/ directory;
      no .out files; plus the notebook cell-5 law (one root config, no
      symlinks, < 3 GiB total, YAML parses, !include targets exist,
      declared tools within the nine known).
  (b) single-base law — exactly one unique base model string across the
      tree, one of the four ALLOWED_MODELS; adapter key state reported.
  (c) official validate_directory — via the wheelhouse wheels.
  (d) official compile_submission — with the nine-tool registry (the six
      notebook stubs verbatim plus the three graph tools stubbed at
      compile time only; on the eval runtime they are harness builtins).

Usage:
    python validate_submission.py [BUNDLE_DIR]

    BUNDLE_DIR defaults to submission/dist/bundle/ when that exists, else
    the submission root. Exit 0 with last line "VALIDATE: PASS", exit 1
    with last line "VALIDATE: FAIL - <reason>".

NOT gated here, with evidence: the notebook cell-5 {state-var} substitution
assertion (only {problem_description}/{hints} allowed in md/txt) is not
replicated, because the banked bundle's own documentation prose legitimately
contains braces
(adapter-budget.md, freecad-factory/task-schema.md, tools/gemma_dryrun.txt)
and the official judge (validate_directory) passes this exact tree. See
submission/tools/VALIDATE_REPORT.md.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# --- constants (ground truth, with sources) ---------------------------------

# PIPE-PROOF.md mechanical fix 5: "allowed extensions are only
# .yaml .yml .md .txt .py .json .safetensors".
ALLOWED_SUFFIXES = {".yaml", ".yml", ".md", ".txt", ".py", ".json", ".safetensors"}

# Notebook cell 5 (gemma-4-developer-agent-baseline-harness.ipynb).
ROOT_CONFIGS = ("agent.yaml", "agent.yml", "root_agent.yaml", "root_agent.yml")
ALLOWED_MODELS = (
    "gemma-4-31b-it-qat-w4a16-ct",
    "gemma-4-12b-it-qat-w4a16-ct",
    "gemma-4-e4b-it-qat-w4a16-ct",
    "gemma-4-e2b-it-qat-w4a16-ct",
)
SIZE_CAP_BYTES = 3 * 2**30  # notebook cell 5 + swegemma MAX_SUBMISSION_SIZE_BYTES

# submission/README.md "Tool budget": the nine harness tools (seven
# budget-counting plus the two free lifecycle tools).
NINE_TOOLS = {
    "run_command",
    "read_file",
    "edit_file",
    "write_file",
    "get_code_neighbors",
    "search_similar_code",
    "get_code_subgraph",
    "get_status",
    "submit_patch",
}

# Notebook cell 7 HARNESS_WHEELS tuple.
WHEEL_PREFIXES = ("google_adk-", "google_genai-", "adk_submission-", "adk_eval_core-", "swegemma-")
PROVIDER_PREFIXES = ("openai/", "google/", "hosted_vllm/", "custom/")

HERE = Path(__file__).resolve().parent          # submission/tools
SCULLM = HERE.parent.parent                     # C:\\Users\\aaron\\scullm
DEFAULT_BUNDLE = HERE.parent / "dist" / "bundle"
DEFAULT_WHEELS_DIR = SCULLM / "eval" / "wheelhouse"
DEFAULT_TARGET = HERE.parent / "dist" / ".tmp" / "wheels"


def fail(reason: str) -> None:
    print(f"VALIDATE: FAIL — {reason}")
    sys.exit(1)


def norm_model(name: str) -> str:
    name = name.strip().lower()
    for prefix in PROVIDER_PREFIXES:
        name = name.removeprefix(prefix)
    return name


def parse_yaml(text: str, where: str):
    import yaml

    loader = getattr(parse_yaml, "_loader", None)
    if loader is None:
        loader = type(
            "_IncludeLoader", (yaml.SafeLoader,), {}
        )
        loader.add_constructor(
            "!include", lambda l, node: l.construct_scalar(node)
        )
        parse_yaml._loader = loader
    try:
        return yaml.load(text, Loader=loader)
    except Exception as exc:
        fail(f"check(a): YAML does not parse: {where}: {exc!r}")


# --- resolve the bundle ------------------------------------------------------

def resolve_bundle(argv: list[str]) -> Path:
    if len(argv) > 1:
        bundle = Path(argv[1]).resolve()
        if not bundle.is_dir():
            fail(f"bundle directory not found: {bundle}")
        return bundle
    if DEFAULT_BUNDLE.is_dir():
        return DEFAULT_BUNDLE.resolve()
    root = HERE.parent.resolve()
    print(f"[bundle] no bundle dir at {DEFAULT_BUNDLE}; falling back to submission root {root}")
    print("[bundle] NOTE: the raw root carries corpus/ and other fix-5 exclusions; "
          "validate the pruned bundle for the zip-time tree")
    return root


# --- check (a): structural hygiene -------------------------------------------

def check_hygiene(bundle: Path):
    print(f"[a] structural hygiene on {bundle}")
    all_paths = sorted(bundle.rglob("*"))
    if not any(p.is_file() for p in all_paths):
        fail("check(a): bundle contains no files")

    for p in all_paths:
        if p.is_symlink():
            fail(f"check(a): symlink rejected (notebook cell-5 law): {p}")

    files = [p for p in all_paths if p.is_file()]
    total = 0
    for p in files:
        rel = p.relative_to(bundle)
        if p.suffix.lower() not in ALLOWED_SUFFIXES:
            fail(f"check(a): forbidden extension {p.suffix!r} (PIPE-PROOF fix 5): {rel.as_posix()}")
        if "corpus" in rel.parts:
            fail("check(a): corpus/ directory present (PIPE-PROOF fix 5 M2 action): "
                 + rel.as_posix())
        if p.suffix.lower() == ".out":
            fail("check(a): .out file present (PIPE-PROOF fix 5 names "
                 "provenance/compute-adapter-budget.out): " + rel.as_posix())
        total += p.stat().st_size
    print(f"[a] files={len(files)} bytes={total} "
          f"(< {SIZE_CAP_BYTES} 3 GiB cap: {total < SIZE_CAP_BYTES})")
    if total >= SIZE_CAP_BYTES:
        fail(f"check(a): bundle exceeds 3 GiB: {total} bytes")

    roots = [name for name in ROOT_CONFIGS if (bundle / name).is_file()]
    if len(roots) != 1:
        fail(f"check(a): expected exactly 1 root config, found {roots} (notebook cell-5 law)")
    print(f"[a] root config: {roots[0]}")

    for cfg in (p for p in files if p.suffix.lower() in (".yaml", ".yml")):
        text = cfg.read_text(encoding="utf-8")
        data = parse_yaml(text, cfg.relative_to(bundle).as_posix()) or {}
        if not isinstance(data, dict):
            fail(f"check(a): YAML top level is not a mapping: {cfg.relative_to(bundle).as_posix()}")
        for inc in re.findall(r"!include\s+(\S+)", text):
            inc_path = (cfg.parent / inc).resolve()
            if bundle.resolve() not in inc_path.parents or not inc_path.is_file():
                fail(f"check(a): bad !include {inc!r} in {cfg.relative_to(bundle).as_posix()} "
                     "(missing or escapes the bundle)")

    declared_tools: set[str] = set()
    for cfg in (p for p in files if p.suffix.lower() in (".yaml", ".yml")):
        data = parse_yaml(cfg.read_text(encoding="utf-8"),
                          cfg.relative_to(bundle).as_posix()) or {}
        for entry in data.get("tools", []) or []:
            if isinstance(entry, str):
                declared_tools.add(entry)
            elif isinstance(entry, dict) and "agent_tool" in entry:
                continue  # analyzer wiring, not a sandbox function name
            else:
                fail(f"check(a): unrecognized tools entry in "
                     f"{cfg.relative_to(bundle).as_posix()}: {entry!r}")
    unknown_tools = declared_tools - NINE_TOOLS
    if unknown_tools:
        fail(f"check(a): declared tools outside the nine known: {sorted(unknown_tools)}")
    print(f"[a] declared tool names ({len(declared_tools)}): {sorted(declared_tools)}")


# --- check (b): single-base law ----------------------------------------------

def check_single_base(bundle: Path) -> str:
    print("[b] single-base model law")
    files = sorted(p for p in bundle.rglob("*") if p.is_file()
                   and p.suffix.lower() in (".yaml", ".yml"))
    declared_models: dict[str, list[str]] = {}
    adapter_state: list[str] = []
    for cfg in files:
        rel = cfg.relative_to(bundle).as_posix()
        text = cfg.read_text(encoding="utf-8")
        data = parse_yaml(text, rel) or {}
        model = data.get("model")
        if model is not None:
            declared_models.setdefault(norm_model(str(model)), []).append(rel)
        commented = re.findall(r"^\s*#\s*adapter\s*:\s*(\S+)", text, re.MULTILINE)
        if "adapter" in data:
            adapter_state.append(f"{rel}: adapter key PRESENT "
                                 f"(requires adapters/{data['adapter']}/ per section 3.4)")
        elif commented:
            adapter_state.append(f"{rel}: adapter key commented out ({', '.join(commented)})")
    if len(declared_models) != 1:
        fail(f"check(b): single-base law violated, unique declared models: "
             f"{ {k: v for k, v in declared_models.items()} }")
    model = next(iter(declared_models))
    if model not in ALLOWED_MODELS:
        fail(f"check(b): model {model!r} not in ALLOWED_MODELS {list(ALLOWED_MODELS)}")
    printers = "; ".join(f"{rel} -> {model}" for rel in declared_models[model])
    print(f"[b] declared model: {model!r} in {len(declared_models[model])} yaml file(s): {printers}")
    if adapter_state:
        for line in adapter_state:
            print(f"[b] adapter state: {line}")
    else:
        print("[b] adapter state: no adapter key in any yaml (active or commented)")
    return model


# --- wheels: provision the official judge ------------------------------------

def ensure_wheels(target: Path) -> None:
    present = sorted(d.name for d in target.iterdir()
                     if d.is_dir() and d.name.startswith(WHEEL_PREFIXES)) if target.is_dir() else []
    missing = [p for p in WHEEL_PREFIXES
               if not any(d.name.startswith(p) for d in target.iterdir())] if target.is_dir() else list(WHEEL_PREFIXES)
    if target.is_dir() and not missing:
        print(f"[wheels] reusing provisioned target {target} "
              f"({len(present)} dist-infos; last provisioned by a prior run)")
    else:
        if not DEFAULT_WHEELS_DIR.is_dir():
            fail(f"check(c): wheelhouse not found: {DEFAULT_WHEELS_DIR}")
        wheels = [str(w) for w in sorted(DEFAULT_WHEELS_DIR.glob("*.whl"))
                  if w.name.startswith(WHEEL_PREFIXES)]
        if len(wheels) != len(WHEEL_PREFIXES):
            fail(f"check(c): expected {len(WHEEL_PREFIXES)} harness wheels in "
                 f"{DEFAULT_WHEELS_DIR}, found {len(wheels)}: "
                 f"{[Path(w).name for w in wheels]}")
        target.mkdir(parents=True, exist_ok=True)
        print(f"[wheels] provisioning {target} with --no-deps --target (never user-site)")
        proc = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "--no-deps",
             "--target", str(target), *wheels],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            fail(f"check(c): pip install of harness wheels failed: {proc.stderr.strip()[-400:]}")

    # aiohttp>=3.10 into the SAME target: the user-site aiohttp 3.9.1 breaks the
    # litellm import (AttributeError: no attribute ConnectionTimeoutError) —
    # package-report.md section 3 records this exact remedy.
    aiohttp_dist = list(target.glob("aiohttp-*.dist-info")) if target.is_dir() else []
    ok_aiohttp = False
    if aiohttp_dist:
        m = re.search(r"aiohttp-(\d+)\.(\d+)", aiohttp_dist[0].name)
        ok_aiohttp = m and (int(m.group(1)), int(m.group(2))) >= (3, 10)
    if not ok_aiohttp:
        print("[wheels] installing aiohttp>=3.10 into the target (user-site aiohttp "
              "3.9.x breaks the litellm import; package-report.md section 3)")
        proc = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "--upgrade",
             "--target", str(target), "aiohttp>=3.10"],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            fail(f"check(c): pip install of aiohttp>=3.10 failed: {proc.stderr.strip()[-400:]}")


def check_official(bundle: Path, model: str) -> None:
    print("[c] official validate_directory via the wheelhouse wheels")
    ensure_wheels(DEFAULT_TARGET)
    sys.path.insert(0, str(DEFAULT_TARGET))

    try:
        import adk_submission  # noqa: F401
        import swegemma  # noqa: F401
        from adk_submission import ModelRegistry, compile_submission, validate_directory
        from adk_submission.discovery import discover_declared_models
        from google.adk.models.lite_llm import LiteLlm
        from swegemma.config import build_submission_limits
    except Exception as exc:
        fail(f"check(c): official wheels failed to import from {DEFAULT_TARGET}: {exc!r}")

    resolved = {
        "adk_submission": adk_submission.__file__,
        "swegemma": swegemma.__file__,
        "google.adk": sys.modules["google.adk"].__file__,
    }
    for name, path in resolved.items():
        inside = Path(path).resolve().is_relative_to(DEFAULT_TARGET.resolve())
        print(f"[c] {name} resolved: {path} (inside target: {inside})")
        if not inside:
            fail(f"check(c): {name} resolved OUTSIDE the isolated target ({path}); "
                 "refusing to judge on user-site copies")

    limits, constraints = build_submission_limits()
    try:
        validate_directory(bundle, limits)
    except Exception as exc:
        fail(f"check(c): validate_directory rejected the bundle: {exc!r}")
    print("[c] validate_directory: PASSED")

    print("[d] official compile_submission with the nine-tool registry")
    try:
        declared = discover_declared_models(bundle, normalize_fn=norm_model)
    except Exception as exc:
        fail(f"check(d): discover_declared_models failed: {exc!r}")
    if declared != {model}:
        fail(f"check(d): declared-model mismatch: wheels see {sorted(declared)}, "
             f"check(b) saw {model!r}")
    print(f"[d] discover_declared_models: {sorted(declared)}")

    # The six notebook stubs, verbatim from cell 7; on the eval runtime these are
    # harness builtins — these bodies exist only so compile_submission can bind
    # names to a registry (package-report.md section 3, "compile-time stubs only").
    def run_command(command: str) -> str: ...
    def read_file(filepath: str, start_line: int | None = None, end_line: int | None = None) -> str: ...
    def write_file(filepath: str, content: str) -> str: ...
    def edit_file(filepath: str, old_string: str, new_string: str, allow_multiple: bool = False) -> str: ...
    def submit_patch() -> str: ...
    def get_status() -> str: ...

    # The three graph tools, compile-time stubs (ToolNotFoundError otherwise;
    # on the eval runtime they are harness builtins — package-report.md section 3).
    def get_code_neighbors(*args, **kwargs) -> str: ...
    def search_similar_code(*args, **kwargs) -> str: ...
    def get_code_subgraph(*args, **kwargs) -> str: ...

    tools = {
        fn.__name__: fn
        for fn in (run_command, read_file, write_file, edit_file, submit_patch,
                   get_status, get_code_neighbors, search_similar_code, get_code_subgraph)
    }
    if set(tools) != NINE_TOOLS:
        fail(f"check(d): tool registry is not the nine-tool set: {sorted(tools)}")

    models = ModelRegistry()
    try:
        models.register(model, LiteLlm(model=f"openai/{model}",
                                       api_base="http://127.0.0.1:9/v1", api_key="EMPTY"))
    except Exception as exc:
        fail(f"check(d): model registration failed for {model!r}: {exc!r}")

    try:
        compiled_agent = compile_submission(bundle, tools, models, limits=limits,
                                            generation_constraints=constraints)
    except Exception as exc:
        fail(f"check(d): compile_submission rejected the bundle: {exc!r}")
    print(f"[d] compile_submission: PASSED (root_agent={compiled_agent.name!r}, "
          f"tools={len(tools)})")


def main() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    bundle = resolve_bundle(sys.argv)
    print(f"validator: {Path(__file__).resolve()}")
    print(f"python: {sys.version.split()[0]}")
    print(f"bundle: {bundle}")
    print(f"wheel target (isolated, never user-site): {DEFAULT_TARGET}")

    check_hygiene(bundle)
    model = check_single_base(bundle)
    check_official(bundle, model)

    print("VALIDATE: PASS")


if __name__ == "__main__":
    main()

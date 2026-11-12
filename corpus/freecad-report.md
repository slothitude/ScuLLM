# FREECAD HEAD HARVEST — B11 build report (corpus_freecad)

Built 2026-11-12T10:17:11+00:00 UTC by
`build_freecad.py`. Owner ruling: "we finetune a freecad head" — an engineering/CAD seat
in the SCULLM head fleet. Bucket **B11** (next free id after B9; B10 is taken by the
adapter byte-budget work order). HONESTY LAW: every number below is a real count from the
run on disk (`freecad_summary.json`); rows are mechanically derived from shipped code —
no invented APIs. BOUNDARY LAW: FreeCAD at `C:/Program Files/FreeCAD 1.1/` and the uv
cache were READ-ONLY (harvest = copy facts out); writes confined to `C:/Users/aaron/evo/`.

## 1. THE HEADLINE

**366 rows emitted** to `corpus_freecad.jsonl` — **300 lane-1 (api) + 66 lane-2 (bridge)**.
V1 re-read: **PASS (366 lines, 0 parse failures, 0 V3 tokenizer-literal hits)**. V2
schema/roles: enforced on every candidate, **0 rejects**. V5 provenance: every row's
`source` resolves to an existing file with the line in bounds; an independent post-check
re-sliced 20 random api rows against the real files (**0 mismatches**) and re-checked all
66 bridge rows against `server.py` (**0 mismatches**). V6 accounting: **30/30 modules
reconcile exactly** (candidates = emitted + rejected + deduped + skipped); every skip
carries a reason (4,709 skips recorded, none laundered — full list in
`freecad_summary.json`).

## 2. THE TWO ACTION SURFACES

The freecad head has two hands, and this corpus trains both:

1. **Raw python API** (lane `api`) — writing parametric FreeCAD python (`App.addObject`,
   `Part.makeBox`, Draft/Fem/CAM object factories), harvested from the 30 Python modules
   shipped in `C:/Program Files/FreeCAD 1.1/Mod/` (FreeCAD **1.1.3**, rev 20260725).
2. **The bridge** (lane `bridge`) — driving FreeCAD through the **freecad-mcp 0.1.30**
   (MIT) MCP server, the same 17 tools this machine's freecad-mcp serves:
   `create_document, create_object, edit_object, delete_object, execute_code,
   execute_code_async, execute_code_headless, get_async_status, get_view,
   get_object, get_objects, get_parts_list, get_rpc_status, insert_part_from_library,
   list_documents, reload_document, run_fem_analysis`. Tool names/args are copied
   verbatim from `server.py`'s AST (decorated `@tool` functions); the bridge tool count
   is **17**, and every tool is covered.

## 3. MODULE DIVERSITY (lane 1 — 300 rows, round-robin across 30 modules)

| Module | .py read | docstring candidates | rows | | Module | .py read | candidates | rows |
|---|---|---|---|---|---|---|---|---|
| Draft | 239 | 1,439 | **24** | | Material | 17 | 79 | 23 |
| Part | 42 | 97 | **24** | | Idf | 2 | 11 | 3 |
| Sketcher | 16 | 11 | 4 | | Show | 15 | 52 | 17 |
| Mesh | 5 | 3 | 2 | | BIM (Arch) | 199 | 810 | **23** |
| MeshPart | 3 | 3 | 2 | | Fem | 386 | 384 | **23** |
| Spreadsheet | 5 | 4 | 3 | | CAM | 358 | 1,436 | **23** |
| TechDraw | 31 | 49 | 23 | | AddonManager | 56 | 295 | 23 |
| PartDesign | 55 | 87 | 24 | | Test | 20 | 50 | 13 |
| Assembly | 23 | 26 | 13 | | Help/Start/Plot/Tux | 12 | 56 | 14 |
| OpenSCAD | 21 | 96 | 17 | | Surface/Points/Measure/Import/Inspection/RevEng/Robot/Web | 20 | 7 | 2 |

Cored engineering surfaces (Draft, Part, TechDraw, PartDesign, BIM, Fem, CAM, Material)
each land at 23–24 rows — the round-robin + per-module cap (32) + per-file cap (3) keep
Draft/CAM/Fem's 1,400-candidate giants from drowning the small modules. **Zero-row
modules are a real property of FreeCAD 1.1.3, not a harvester gap**: Surface, Points,
Inspection, ReverseEngineering, Robot and Web are C++-implemented workbenches whose
shipped Python is Init/InitGui stubs (their 1 docstring candidate each is trivial and
was skipped with its reason). Note: **there is no `Arch` directory in 1.1** — Arch was
folded into **BIM** (`ArchCurtainWall.py`, `ArchWall.py`, ...), which is where the
architecture corpus actually lives.

## 4. ROW DERIVATION (per lane, mechanical only)

- **Lane 1 (`api`)** — `args_derivation: "docstring-first-sentence+code-excerpt"` on all
  300. For each public top-level function/method/class with a docstring:
  user = `"Write FreeCAD python to <first docstring sentence, cleaned>"` (whitespace
  collapsed; signature-style docstrings like `makeX(a, b): does X` keep only the
  description part — mechanical regex, no prose authored); assistant = the definition's
  first 15 lines, verbatim and dedented. Skipped with reasons: per-file cap (2,573),
  trivial/overlong first sentence (746), private `_` names (234), module cap (1,081),
  500KB-over files never read (15), api quota overflow (60).
- **Lane 2 (`bridge`)** — system: "You are the FreeCAD head: drive FreeCAD through the
  bridge tools in small verified steps."; assistant is a JSON tool call
  `{"tool": ..., "args": {...}}`. **Honest derivation marking per row** (`args_derivation`):
  - `docstring-example-verbatim` (9 rows) — payload copied from the tool's own
    docstring Examples blocks (create_object's cylinder/cut/pipe/FEM examples etc.).
  - `docstring-factory-table` (5 rows) — the documented Draft/Part factory types with
    exactly their required properties (Part::Tube, Draft::Circle/Rectangle/Polygon/Wire).
  - `signature-required+...` (rest) — required params only, values from the signature
    defaults / documented ViewName enum; the 3 `code` arguments are **real shipped
    FreeCAD statements** lifted from lane-1 files, each provenance-stamped in the row
    (e.g. `...+lane1-code:FreeCAD1.1/Mod/Sketcher/SketcherTests/TestSketchValidateCoincidents.py:136`).
  - The **intent phrasing is derived** from each tool's own docstring first sentence —
    marked by the `signature-required+docstring-intent` / derivation field, per the
    honesty requirement. Numeric sample values (e.g. `Radius: 10`) are illustrative and
    never presented as API facts.

## 5. LICENSE NOTE (disclosed)

- **FreeCAD 1.1.3**: shipped under **LGPL2+** — stated verbatim in the install's own
  `C:/Program Files/FreeCAD 1.1/doc/LICENSE.html` ("LGPL2+ license, as stated below").
  Harvest = copying facts (docstrings + code excerpts) out of the installed source into
  an **internal** training corpus for the owner's own head; the install itself was never
  modified (read-only harvest). Use disclosed here as required.
- **freecad-mcp 0.1.30**: **MIT** (per its PyPI METADATA in the uv cache); same
  internal-use harvest, disclosed.

## 6. WHAT A V2 HARVEST WOULD ADD

1. **FreeCAD wiki tutorials** via the sunny.researcher lane (`GET /read?url=...`,
   `POST /crawl` on wiki.freecad.org / manual.freecad.org) — intent→script rows written
   as prose-plus-code, the shape lane 1 lacks (docstring-first-sentence prompts are
   terse). License: wiki text is CC-BY-SA — disclosed per page.
2. **The femexamples + CAM test corpora** (`Fem/femexamples/*.py`, `CAM/CAMTests/`) as
   multi-step build scripts: whole-file "build this model" tasks with verified setups.
3. **Bridge episode rows**: real tool-call *traces* through the live freecad-mcp on this
   machine (create → get_object → edit → run_fem_analysis), captured from actual
   sessions rather than schema-derived — turns lane 2 from schema teaching into
   trajectory teaching.
4. **Sketcher constraint solver examples** (Sketcher's Python surface is thin — 11
   candidates) and **Draft/TechDraw dimensioning recipes** from forum threads.
5. **Longer code excerpts** (15 lines truncates real functions; 30-40 lines with the
   Chunk Law applied) once B4's converter exists.

## 7. FILES AND PROVENANCE

- Script: `C:/Users/aaron/evo/state/gemma/submission/corpus/build_freecad.py`
- Corpus: `C:/Users/aaron/evo/state/gemma/submission/corpus/corpus_freecad.jsonl` (366 rows)
- Accounting: `C:/Users/aaron/evo/state/gemma/submission/corpus/freecad_summary.json`
- Read (READ-ONLY): `C:/Program Files/FreeCAD 1.1/Mod/` (1,518 .py read of 1,533 on
  disk; 15 over 500 KB never read per the harvest rule; 0 parse failures) and
  `C:/Users/aaron/AppData/Local/uv/cache/archive-v0/ru6EwflA4eOUO4_d/freecad_mcp/server.py`.
- V-laws executed: V1 parse (PASS, re-read), V2 schema/roles (5-key B11 shape, exact
  order), V3 no tokenizer literals (0 hits), V5 provenance (existence + line bounds +
  independent byte-match spot check), V6 accounting (30/30 modules reconcile; per-tool
  bridge accounting in the summary).

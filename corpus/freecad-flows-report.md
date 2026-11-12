# freecad-flows-report.md — B11-PLAN FreeCAD flow bucket

Built 2026-11-12. 48 SCULLM/OFL plan rows for the FreeCAD head (8 parametric families x 6). HONESTY LAW: every count below is a real count from this build run; every API symbol in the plans was grepped against the FreeCAD 1.1 `Mod/` tree (READ-ONLY).

## 1. ACCOUNTING (V6)

| family | emitted |
|---|---|
| primitive-pad | 6 |
| sketch-driven | 6 |
| revolution | 6 |
| boolean-assembly | 6 |
| fillet-chamfer | 6 |
| pattern-mirror | 6 |
| spreadsheet-params | 6 |
| techdraw-export | 6 |

authored 48 | emitted 48 | rejected 0 | total 48 (reconciles exactly). Build note: during authoring, two TechDraw drafts (dims, svg export) were re-written because their first drafts had no `action` node; the counts above are the FINAL authored set.

## 2. REPLAN-HEAVY PLANS (honest-failure flows)

The brief asked for 4; **8** were emitted (one per family — every family ends in an honest-failure flow: a gate fails, the retry loop gets `loop 2` fresh observations via a `jump` anchor, and the third arrival replans):

- row 6 (primitive-pad): bracket with a bolt bore — cut misses tolerance twice then replans"...
- row 12 (sketch-driven): slot plate — through pocket fails twice, sketch chain is redone"...
- row 18 (revolution): sealed tank revolve — profile rebuilt twice then replanned"...
- row 24 (boolean-assembly): lens mount — intersection comes back empty twice then replans"...
- row 30 (fillet-chamfer): handle bar — fillet radius too big twice, then replans down"...
- row 36 (pattern-mirror): hole grid — occurrences overlap twice then replans to two rows"...
- row 42 (spreadsheet-params): parametric bracket — a broken alias poisons recompute twice before replan"...
- row 48 (techdraw-export): section sheet — the front view renders empty twice before replan"...

## 3. VALIDATOR

`scullm_check.py` EXISTED at build time at `C:/Users/aaron/evo/state/gemma/submission/skills/scullm-planning/scullm_check.py` — it was IMPORTED and run via its `check()` on every one of the 48 authored plans. No own-validator fallback was needed. Every emitted plan: 0 errors, 5-9 nodes, kinds include action+gate+code, a verification gate naming `doc.recompute()` with a check, and a reachable done node (V4-adapted).

Sample validator output (row 1): errors=0, info={'nodes': 7, 'entry': 'n0', 'ends': ['n5'], 'gates': 1, 'edges': 6}


Per-row scullm_check verdict (all 48 PASS, 0 errors):

| row | family | nodes | gates | edges | entry | reachable done |
|---|---|---|---|---|---|---|
| 1 | primitive-pad | 7 | 1 | 6 | n0 | n5 |
| 2 | primitive-pad | 6 | 1 | 5 | n0 | n4 |
| 3 | primitive-pad | 6 | 1 | 5 | n0 | n4 |
| 4 | primitive-pad | 6 | 1 | 5 | n0 | n4 |
| 5 | primitive-pad | 8 | 2 | 8 | n0 | n6 |
| 6 | primitive-pad | 8 | 1 | 6 | n0 | n4 |
| 7 | sketch-driven | 7 | 1 | 6 | n0 | n5 |
| 8 | sketch-driven | 7 | 1 | 6 | n0 | n5 |
| 9 | sketch-driven | 7 | 1 | 6 | n0 | n5 |
| 10 | sketch-driven | 7 | 1 | 6 | n0 | n5 |
| 11 | sketch-driven | 7 | 1 | 6 | n0 | n5 |
| 12 | sketch-driven | 9 | 1 | 7 | n0 | n5 |
| 13 | revolution | 6 | 1 | 5 | n0 | n4 |
| 14 | revolution | 7 | 2 | 7 | n0 | n5 |
| 15 | revolution | 5 | 1 | 4 | n0 | n3 |
| 16 | revolution | 7 | 2 | 7 | n0 | n5 |
| 17 | revolution | 6 | 1 | 5 | n0 | n4 |
| 18 | revolution | 8 | 1 | 6 | n0 | n4 |
| 19 | boolean-assembly | 7 | 1 | 6 | n0 | n5 |
| 20 | boolean-assembly | 6 | 1 | 5 | n0 | n4 |
| 21 | boolean-assembly | 6 | 1 | 5 | n0 | n4 |
| 22 | boolean-assembly | 6 | 1 | 5 | n0 | n4 |
| 23 | boolean-assembly | 7 | 2 | 7 | n0 | n5 |
| 24 | boolean-assembly | 8 | 1 | 6 | n0 | n4 |
| 25 | fillet-chamfer | 5 | 1 | 4 | n0 | n3 |
| 26 | fillet-chamfer | 6 | 1 | 5 | n0 | n4 |
| 27 | fillet-chamfer | 7 | 1 | 6 | n0 | n5 |
| 28 | fillet-chamfer | 5 | 1 | 4 | n0 | n3 |
| 29 | fillet-chamfer | 5 | 1 | 4 | n0 | n3 |
| 30 | fillet-chamfer | 7 | 1 | 5 | n0 | n3 |
| 31 | pattern-mirror | 7 | 1 | 6 | n0 | n5 |
| 32 | pattern-mirror | 6 | 1 | 5 | n0 | n4 |
| 33 | pattern-mirror | 6 | 1 | 5 | n0 | n4 |
| 34 | pattern-mirror | 6 | 1 | 5 | n0 | n4 |
| 35 | pattern-mirror | 7 | 1 | 6 | n0 | n5 |
| 36 | pattern-mirror | 8 | 1 | 6 | n0 | n4 |
| 37 | spreadsheet-params | 6 | 1 | 5 | n0 | n4 |
| 38 | spreadsheet-params | 6 | 1 | 5 | n0 | n4 |
| 39 | spreadsheet-params | 6 | 1 | 5 | n0 | n4 |
| 40 | spreadsheet-params | 6 | 1 | 5 | n0 | n4 |
| 41 | spreadsheet-params | 6 | 1 | 5 | n0 | n4 |
| 42 | spreadsheet-params | 7 | 1 | 5 | n0 | n3 |
| 43 | techdraw-export | 6 | 1 | 5 | n0 | n4 |
| 44 | techdraw-export | 7 | 1 | 6 | n0 | n5 |
| 45 | techdraw-export | 7 | 2 | 7 | n0 | n5 |
| 46 | techdraw-export | 6 | 1 | 5 | n0 | n4 |
| 47 | techdraw-export | 6 | 1 | 5 | n0 | n4 |
| 48 | techdraw-export | 7 | 1 | 5 | n0 | n3 |

## 4. VALIDATION V1-V6 (adapted)

- **V1 PARSE**: file re-read — 48 lines, 0 parse failures.

- **V2 SCHEMA**: exact keys [messages, bucket, source], bucket B11-PLAN, 3 messages system/user/assistant, non-empty contents — 0 failures.

- **V3 NO TOKENIZER LITERALS**: all 8 literals scanned per emitted line — 0 hits.

- **V4 (adapted PLAN CLOSURE)**: per plan — scullm_check PASS (grammar + no dangling edges + at least one reachable done/goal), node count 5-9, action/gate/code present, verification gate (recompute + check), done node.

- **V5 PROVENANCE**: every row carries `source` = `FreeCAD1.1 grammar:OFL.md + api-family:<family>`. Ground truth paths stat-verified this run: OFL doc exists at `C:/Users/aaron/ham_n_eggs/omniflow/lang/OFL.md` (the brief's `evo\ham_n_eggs\...` path does NOT exist — corrected, READ-ONLY); FreeCAD 1.1 install at `C:/Program Files/FreeCAD 1.1` (READ-ONLY, `Mod/` walked read-only for grounding).

- **V6 ACCOUNTING**: authored = emitted + rejected = 48 = 48 + 0. Per-family counts in section 1 reconcile.

## 5. API GROUNDING CHECK (HONESTY LAW)

Every API symbol extracted from the 48 authored plans was grepped against `C:/Program Files/FreeCAD 1.1/Mod` (symbol table built read-only from Mod text files). Distinct symbols checked: **76** (26 type ids + 26 calls + 21 property assigns + 3 bonus). NOT-GROUNDED count: 0. Lib-binary-only symbols: ['TechDrawGui.exportPageAsSvg'].


### Type ids (addObject strings)

| `Part::Box` | Mod/ | 52 |
| `Part::Cut` | Mod/ | 22 |
| `Part::Cylinder` | Mod/ | 22 |
| `Part::Feature` | Mod/ | 162 |
| `Part::MultiCommon` | Mod/ | 4 |
| `Part::MultiFuse` | Mod/ | 17 |
| `Part::Sphere` | Mod/ | 13 |
| `PartDesign::AdditiveBox` | Mod/ | 17 |
| `PartDesign::AdditiveCylinder` | Mod/ | 5 |
| `PartDesign::Body` | Mod/ | 44 |
| `PartDesign::Chamfer` | Mod/ | 3 |
| `PartDesign::Fillet` | Mod/ | 4 |
| `PartDesign::Groove` | Mod/ | 2 |
| `PartDesign::LinearPattern` | Mod/ | 2 |
| `PartDesign::Mirrored` | Mod/ | 2 |
| `PartDesign::Pad` | Mod/ | 15 |
| `PartDesign::Plane` | Mod/ | 5 |
| `PartDesign::Pocket` | Mod/ | 4 |
| `PartDesign::PolarPattern` | Mod/ | 2 |
| `PartDesign::Revolution` | Mod/ | 5 |
| `Spreadsheet::Sheet` | Mod/ | 6 |
| `TechDraw::DrawPage` | Mod/ | 16 |
| `TechDraw::DrawProjGroup` | Mod/ | 3 |
| `TechDraw::DrawSVGTemplate` | Mod/ | 5 |
| `TechDraw::DrawViewDimension` | Mod/ | 3 |
| `TechDraw::DrawViewPart` | Mod/ | 7 |


### Calls (module-qualified where capitalized)

| `Anchor.recompute` | Mod/ (.method() form) | 374 |
| `Cavity.setExpression` | Mod/ (.method() form) | 30 |
| `FreeCAD.Vector` | Mod/ (.method() form) | 294 |
| `FreeCAD.newDocument` | Mod/ (.method() form) | 145 |
| `Group.addProjection` | Mod/ (.method() form) | 1 |
| `Group.recompute` | Mod/ (.method() form) | 374 |
| `Hub.setExpression` | Mod/ (.method() form) | 30 |
| `Pad.setExpression` | Mod/ (.method() form) | 30 |
| `Page.addView` | Mod/ (.method() form) | 17 |
| `PageA.addView` | Mod/ (.method() form) | 17 |
| `Part.makeBox` | Mod/ (.method() form) | 19 |
| `Part.makeCylinder` | Mod/ (.method() form) | 7 |
| `Plate.setExpression` | Mod/ (.method() form) | 30 |
| `Shape.isValid` | Mod/ (.method() form) | 48 |
| `TechDrawGui.exportPageAsSvg` | lib-binary:TechDrawGui.pyd | 1 |
| `Vents.setExpression` | Mod/ (.method() form) | 30 |
| `addGeometry` | Mod/ (.method() form) | 33 |
| `addObject` | Mod/ (.method() form) | 353 |
| `cut` | Mod/ (.method() form) | 44 |
| `isValid` | Mod/ (.method() form) | 48 |
| `makeFillet` | Mod/ (.method() form) | 3 |
| `recompute` | Mod/ (.method() form) | 374 |
| `removeSplitter` | Mod/ (.method() form) | 33 |
| `set` | Mod/ (.method() form) | 41 |
| `setAlias` | Mod/ (.method() form) | 2 |
| `setExpression` | Mod/ (.method() form) | 30 |


### Property assignments

| `Angle` | Mod/ | 200 |
| `Axis` | Mod/ | 135 |
| `Base` | Mod/ | 685 |
| `Direction` | Mod/ | 125 |
| `Length` | Mod/ | 419 |
| `MirrorPlane` | Mod/ | 2 |
| `Occurrences` | Mod/ | 4 |
| `Originals` | Mod/ | 4 |
| `Profile` | Mod/ | 88 |
| `Radius` | Mod/ | 162 |
| `References2D` | Mod/ | 2 |
| `Reversed` | Mod/ | 57 |
| `Shape` | Mod/ | 523 |
| `Shapes` | Mod/ | 92 |
| `Size` | Mod/ | 133 |
| `Source` | Mod/ | 92 |
| `Template` | Mod/ | 46 |
| `Tool` | Mod/ | 624 |
| `Type` | Mod/ | 581 |
| `UseAllEdges` | Mod/ | 3 |
| `XDirection` | Mod/ | 2 |


### Bonus property reads

| `Shape.Volume` | Mod/ (combined) | 35 |
| `BoundBox` | Mod/ | 103 |
| `FullyConstrained` | Mod/ | 1 |


## 6. BOUNDARY LAW

Written: only the two deliverables under `C:/Users/aaron/evo/state/gemma/submission/corpus/` plus this build script under `evo/state/gemma/paper/`. Read-only: FreeCAD 1.1 install, `ham_n_eggs` OFL.md, everything else.


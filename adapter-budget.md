# ADAPTER BYTE BUDGET — gemma-4-e2b-it-qat-w4a16-ct (WO-B10)

Computed 2026-11-12. Every number below is output of `provenance/compute-adapter-budget.py`
(pasted in section 5), run with `C:/Python313/python.exe` against the **official config obtained
from Hugging Face** — not estimated by feel. Base declared in `agent.yaml` /
`sub_agents/code_analyzer.yaml`: `gemma-4-e2b-it-qat-w4a16-ct`.

**Labels used**: MEASURED = bytes read off a real file on disk. OBTAINED = fetched from the
official HF config (HTTP 200). DERIVED = arithmetic from the above. ESTIMATE = scaled by assumption.

---

## 1. Per-candidate table (per head; bytes/head identical for every head role)

Formula: `LoRA params(module) = r x (in_features + out_features)`; PEFT stores
`lora_A=(r, in)` + `lora_B=(out, r)`. Save dtype **BF16 = 2 B/param** — MEASURED from the real
starter-kit adapter header ([S3], all four tensors are `dtype=BF16`). fp32 column shown for the
training-checkpoint variant only; the 3 GiB cap is judged on the submitted safetensors (BF16).

### E2B linear inventory (OBTAINED — official config [S1])

`35 layers (28 sliding_attention + 7 full_attention), hidden=1536, heads=8, head_dim=256,
global_head_dim=512, kv_heads=1, intermediate=6144`:

| layer type | q_proj | k_proj | v_proj | o_proj | gate/up | down |
|---|---|---|---|---|---|---|
| sliding (28x) | 1536->2048 | 1536->256 | 1536->256 | 2048->1536 | 1536->6144 | 6144->1536 |
| full (7x) | 1536->4096 | 1536->512 | 1536->512 | 4096->1536 | 1536->6144 | 6144->1536 |

Tensors per head: all-linear = 2x7x35 = **490**; q/v-only = 2x2x35 = **140**.
Upper-bound bias (stated, not hidden): E2B has `num_kv_shared_layers=20` (some layers share
k/v — reality has FEWER k/v modules than counted) and `use_double_wide_mlp=True`
(per-layer-input path assumed to add no LoRA-targeted linears). The table is therefore an
upper bound on true bytes.

### Bytes per head (DERIVED, BF16 as saved)

| targeting | rank | params/head | bytes/head | MiB | +10% MiB | fp32 MiB (training only) |
|---|---:|---:|---:|---:|---:|---:|
| all-linear | 8   | 9,719,808    | 19,439,616    | 18.54  | 20.39  | 37.08  |
| all-linear | 16  | 19,439,616   | 38,879,232    | 37.08  | 40.79  | 74.16  |
| all-linear | 64  | 77,758,464   | 155,516,928   | 148.31 | 163.14 | 296.62 |
| all-linear | 128 | 155,516,928  | 311,033,856   | 296.62 | 326.29 | 593.25 |
| q/v-only   | 8   | 1,634,304    | 3,268,608     | 3.12   | 3.43   | 6.23   |
| q/v-only   | 16  | 3,268,608    | 6,537,216     | 6.23   | 6.86   | 12.47  |
| q/v-only   | 64  | 13,074,432   | 26,148,864    | 24.94  | 27.43  | 49.88  |
| q/v-only   | 128 | 26,148,864   | 52,297,728    | 49.88  | 54.86  | 99.75  |

Each candidate head (`router_lora`, `crow_lora`, `analyzer_lora`, `planner_lora`) costs exactly
the same bytes — the base is shared, so N heads = N x the table value.

**Overhead is NOT 10% — it is MEASURED.** The work order said "~10% PEFT safetensors
overhead"; the real starter adapter shows 584 B overhead on 217,088 B of tensor data
(0.269%, ~144 B per tensor-header entry). A 490-tensor file adds ~70 KB (~0.2% at rank 16).
The +10% columns are kept anyway as the safety wrapper for all cap arithmetic below.

---

## 2. The 3 GiB budget math

Cap: **3,221,225,472 bytes** total unpacked size incl. `adapters/`
(HARNESS_README.md section 2.4, exact int). Base submission files measured on disk:
**117,376 B** (~115 KB: agent.yaml 2,261 + README.md 5,199 + eval-split.md 7,192 +
eval_config.yaml 287 + corpus/ 60,113 + tools/ 36,070 + prompts/ 2,747 + skills/ 1,834 +
sub_agents/ 1,673; provenance/ and this report excluded from the shipped number). It is noise
against 3 GiB.

| head set | targeting | rank | adapters B | total B (incl base, +10%) | % of cap | margin B | max heads that fit |
|---|---|---:|---:|---:|---:|---:|---:|
| MIN-3 (router+crow+analyzer) | all-linear | 8   | 64,150,734    | 64,268,110    | 2.00%  | 3,156,957,362 | 150 |
| MIN-3 (router+crow+analyzer) | all-linear | 16  | 128,301,468   | 128,418,844   | 3.99%  | 3,092,806,628 | 75  |
| MIN-3 (router+crow+analyzer) | all-linear | 64  | 513,205,863   | 513,323,239   | 15.94% | 2,707,902,233 | 18  |
| MIN-3 (router+crow+analyzer) | all-linear | 128 | 1,026,411,726 | 1,026,529,102 | 31.87% | 2,194,696,370 | 9   |
| MIN-3 (router+crow+analyzer) | q/v-only   | 8   | 10,786,407    | 10,903,783    | 0.34%  | 3,210,321,689 | 895 |
| MIN-3 (router+crow+analyzer) | q/v-only   | 16  | 21,572,814    | 21,690,190    | 0.67%  | 3,199,535,282 | 447 |
| MIN-3 (router+crow+analyzer) | q/v-only   | 64  | 86,291,253    | 86,408,629    | 2.68%  | 3,134,816,843 | 111 |
| MIN-3 (router+crow+analyzer) | q/v-only   | 128 | 172,582,503   | 172,699,879   | 5.36%  | 3,048,525,593 | 55  |
| FULL-4 (+planner)            | all-linear | 8   | 85,534,312    | 85,651,688    | 2.66%  | 3,135,573,784 | 150 |
| FULL-4 (+planner)            | all-linear | 16  | 171,068,624   | 171,186,000   | 5.31%  | 3,050,039,472 | 75  |
| FULL-4 (+planner)            | all-linear | 64  | 684,274,484   | 684,391,860   | 21.25% | 2,536,833,612 | 18  |
| FULL-4 (+planner)            | all-linear | 128 | 1,368,548,968 | 1,368,666,344 | 42.49% | 1,852,559,128 | 9   |
| FULL-4 (+planner)            | q/v-only   | 8   | 14,381,876    | 14,499,252    | 0.45%  | 3,206,726,220 | 895 |
| FULL-4 (+planner)            | q/v-only   | 16  | 28,763,752    | 28,881,128    | 0.90%  | 3,192,344,344 | 447 |
| FULL-4 (+planner)            | q/v-only   | 64  | 115,055,004   | 115,172,380   | 3.58%  | 3,106,053,092 | 111 |
| FULL-4 (+planner)            | q/v-only   | 128 | 230,110,004   | 230,227,380   | 7.15%  | 2,990,998,092 | 55  |

Every candidate in the table fits the cap with >=57% margin — at E2B scale **the zip is nowhere
near binding**. The Self-Loop minimum (router + crow + analyzer per GEMMA_PLAN) plus planner at
rank 16 all-linear uses 5.31% of the cap.

---

## 3. VRAM cross-check (serving is not the constraint)

- Per-GPU usable: 4x L4 = 96 GB total, `gpu_memory_utilization=0.90` -> ~86.4 GB usable
  (HARNESS_README.md section 3.1).
- Base weight footprint E2B W4A16: README table says ~2-3 GB total (~0.7 GB/GPU).
  Local corroboration (MEASURED, 2026-11-12): the official GGUF q4_0 (3.35 GB) ran
  full-offload on the 3060 at **1,727 MiB / 6,144 MiB VRAM with 8k ctx** (`e2b-bench.md`).
- LoRA serving buffers: harness auto-sizes `max_loras = max(1, len(adapter_map))` and
  `max_lora_rank = max(detected_ranks)` — with 4 adapters at rank 16 that is 4 LoRA buffers
  at rank 16 on a 2B model, a few hundred MB worst case. vLLM's own hard ceiling
  `max_lora_rank <= 128` (README section 3.1 rule 3) is respected by every rank in the table.
- Conclusion: serving 4 adapters on 86.4 GB usable leaves tens of GB of KV-cache headroom.
  **The 3 GiB zip cap is the only binding constraint, and we use 5.31% of it.**

---

## 4. CHOSEN

CHOSEN: FULL-4 (router_lora + crow_lora + analyzer_lora + planner_lora) at rank 16, all-linear
targeting, BF16 as saved = 171,186,000 bytes total incl. base files and +10% overhead =
5.31% of the 3 GiB cap; margin 3,050,039,472 bytes (94.69%). Rank 16 also matches the
GEMMA_PLAN crow recipe ("rank 8-16") and keeps `max_lora_rank=16` so the vLLM LoRA buffers
stay small.

Fallback ladder if a future head set pushes over budget (in order, each step roughly
halves-or-better the cost):
1. **fewer roles** — drop planner_lora, then analyzer_lora (Self-Loop minimum = router + crow);
2. **q/v-only targeting** — cuts each head ~5.9x (35 MB -> 6 MB at rank 16);
3. **lower rank** — rank 16 -> 8 halves again; ranks below 8 are NOT in the candidate table.

Recovery path upward also exists: rank 64 all-linear FULL-4 (21.25%) and rank 128 all-linear
FULL-4 (42.49%) both still fit with >=57% margin if quality demands it.

---

## 5. Provenance

### Sources

| id | what | where | label |
|---|---|---|---|
| S1 | E2B official config (text_config dims) | `https://huggingface.co/google/gemma-4-e2b-it-qat-w4a16-ct/resolve/main/config.json` (HTTP 200, 22,202 B, fetched 2026-11-12; canonical name redirects `e2b`->`E2B`) — snapshot: `submission/provenance/e2b-config-snapshot.json` | OBTAINED |
| S2 | 31B official config (validation only) | `https://huggingface.co/google/gemma-4-31b-it-qat-w4a16-ct/resolve/main/config.json` (HTTP 200, 18,711 B) — snapshot: `submission/provenance/31b-config-snapshot.json` | OBTAINED |
| S3 | Real PEFT starter adapter, measured byte-by-byte (header parsed) | `eval/starter/sample_submission_download/sample_submission/adapters/main_lora/adapter_model.safetensors` (217,672 B; r=4, q_proj+o_proj, `layers_to_transform:[0]`, base `google/gemma-4-31b-it-qat-w4a16-ct`) | MEASURED |
| S4 | 3 GiB cap = 3,221,225,472 B unpacked; L4x4/0.90/max_lora_rank<=128/max_loras=len(adapter_map); E2B ~2-3 GB W4A16 | `HARNESS_README.md` sections 2.4 and 3.1/3.4 | CITED |
| S5 | Base submission size 117,376 B | measured with `find`/`du -sb` on `submission/` 2026-11-12 (excl. `provenance/`, `adapter-budget.md`) | MEASURED |
| S6 | Local E2B VRAM corroboration 1,727 MiB @ 8k ctx | `e2b-bench.md` (llama-server native timings, 2026-11-12) | MEASURED |

### Measured vs derived, stated plainly

- MEASURED: sample-adapter tensor shapes/dtype/overhead (S3), file sizes (S5), local VRAM (S6).
- OBTAINED: both HF configs (S1, S2) — the E2B table dims are the official config's own numbers.
- DERIVED: all adapter byte math (r x (in+out) x 2 B), head-set totals, margins, head counts.
- ESTIMATE (bracketed, conservative-side): the k/v sharing and double-wide-MLP notes in
  section 1 — the table counts MORE modules than the config implies, so true bytes can only be
  lower than tabulated, never higher.
- Triple validation of the formula: (a) predicted 217,088 B == MEASURED 217,088 B for the S3
  sample; (b) the same formula on the 31B config reproduces every README section 3.4 range
  (r16: 206.2 MiB in "~110-220"; r32: 412.5 in "~220-450"; r64: 825.0 in "~450-900";
  r128: 1,650.0 MiB in "~0.9-1.8 GB"); (c) dims come from Google's own config, not memory.
  The work order's fallback authority (README table / 15.5 scaling) was NOT needed.

### The exact script (`submission/provenance/compute-adapter-budget.py`)

```python
#!/usr/bin/env python3
"""B10 ADAPTER BYTE BUDGET — gemma-4-e2b-it-qat-w4a16-ct (run with C:/Python313/python.exe).

Sources (all MEASURED / OBTAINED, cited in adapter-budget.md):
  [S1] e2b config  : submission/provenance/e2b-config-snapshot.json
       (fetched 2026-11-12 from https://huggingface.co/google/gemma-4-e2b-it-qat-w4a16-ct/resolve/main/config.json, HTTP 200)
  [S2] 31b config  : submission/provenance/31b-config-snapshot.json
       (fetched 2026-11-12 from https://huggingface.co/google/gemma-4-31b-it-qat-w4a16-ct/resolve/main/config.json, HTTP 200)
  [S3] measured PEFT sample adapter (starter kit, 31B, r=4, q+o, layer 0):
       eval/starter/sample_submission_download/sample_submission/adapters/main_lora/adapter_model.safetensors (217,672 B)
  [S4] submission base size: measured with find/du on 2026-11-12 = 117,376 B (see report)
LoRA math: params(module) = r * (in_features + out_features).  Lora_A=(r,in), Lora_B=(out,r).
"""
import json, struct, os, math

EVO = r"C:\Users\aaron\scullm"
E2B_CFG = os.path.join(EVO, r"submission\provenance\e2b-config-snapshot.json")
B31_CFG = os.path.join(EVO, r"submission\provenance\31b-config-snapshot.json")
SAMPLE  = os.path.join(EVO, r"eval\starter\sample_submission_download\sample_submission\adapters\main_lora\adapter_model.safetensors")
CAP     = 3_221_225_472          # 3 GiB, HARNESS_README.md section 2.4 (exact int from README)
BASE_SUBMISSION = 117_376        # measured unpacked submission/ minus provenance/ minus this report
OVERHEAD_SAFETY = 0.10           # work-order assumption; also report measured overhead
DT_SAVED  = 2                    # BF16 — measured in [S3] header
DT_TRAIN  = 4                    # fp32 — training-checkpoint variant, shown for completeness
RANKS = [8, 16, 64, 128]
HEADS = ["router_lora", "crow_lora", "analyzer_lora", "planner_lora"]

def text_cfg(path):
    c = json.load(open(path, encoding="utf-8"))
    return c.get("text_config", c)

def e2b_module_dims(t):
    """Per-layer (in,out) dicts from the official config. Sliding layers use head_dim;
    full-attention layers use global_head_dim (global kv heads fall back to kv heads)."""
    h   = t["hidden_size"]
    nh  = t["num_attention_heads"]
    hd  = t["head_dim"]
    ghd = t.get("global_head_dim") or hd
    kv  = t["num_key_value_heads"]
    gkv = t.get("num_global_key_value_heads") or kv
    i   = t["intermediate_size"]
    types = t["layer_types"]
    per_layer = []
    for lt in types:
        d   = hd if lt == "sliding_attention" else ghd
        nkv = kv if lt == "sliding_attention" else gkv
        q_out = nh * d
        k_out = nkv * d
        per_layer.append({
            "q_proj":  (h, q_out), "k_proj": (h, k_out), "v_proj": (h, k_out),
            "o_proj":  (q_out, h),
            "gate_proj": (h, i), "up_proj": (h, i), "down_proj": (i, h),
        })
    return per_layer

def set_bytes(per_layer, modules, rank, dtype_bytes):
    params = sum(rank * (a + b) for L in per_layer for m in modules for (a, b) in [L[m]])
    return params, params * dtype_bytes

# ---------- 1. VALIDATION against the measured sample adapter [S3] x [S2] ----------
t31 = text_cfg(B31_CFG)
h31, nh31, hd31 = t31["hidden_size"], t31["num_attention_heads"], t31["head_dim"]
q_out31 = nh31 * hd31   # layer 0 is sliding_attention (layer_types[0]) -> head_dim
pred_params = 4 * ((h31 + q_out31) + (q_out31 + h31))
with open(SAMPLE, "rb") as f:
    (hlen,) = struct.unpack("<Q", f.read(8))
    hdr = json.loads(f.read(hlen))
tens = {k: v for k, v in hdr.items() if k != "__metadata__"}
meas_bytes = sum(v["data_offsets"][1] - v["data_offsets"][0] for v in tens.values())
print("=" * 78)
print("STEP 1  CROSS-VALIDATION: predicted vs measured sample adapter [S2 x S3]")
print("=" * 78)
print(f"  31B layer-0 (sliding): hidden={h31} q_out={q_out31} (=heads{nh31}*head_dim{hd31})")
print(f"  predicted params r=4 q+o 1 layer = {pred_params}  -> bf16 bytes = {pred_params*2}")
print(f"  measured   tensor data bytes     = {meas_bytes}   file={os.path.getsize(SAMPLE)}  header={hlen}")
print(f"  MATCH: {pred_params*2 == meas_bytes}")
n_entries = len(tens)
per_entry = hlen / n_entries
print(f"  measured safetensors overhead: {os.path.getsize(SAMPLE)-meas_bytes} B = "
      f"{(os.path.getsize(SAMPLE)-meas_bytes)/meas_bytes*100:.3f}% of data  (~{per_entry:.0f} B/header-entry)")

# ---------- 2. E2B module inventory ----------
t = text_cfg(E2B_CFG)
PL = e2b_module_dims(t)
n_sl = sum(1 for x in t["layer_types"] if x == "sliding_attention")
n_fu = len(t["layer_types"]) - n_sl
ALL = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
QV  = ["q_proj", "v_proj"]
print()
print("=" * 78)
print("STEP 2  E2B LINEAR INVENTORY [S1]  (MEASURED config, not estimated)")
print("=" * 78)
print(f"  layers={len(PL)} (sliding={n_sl}, full_attention={n_fu})  hidden={t['hidden_size']}"
      f"  heads={t['num_attention_heads']}  head_dim={t['head_dim']}  global_head_dim={t['global_head_dim']}"
      f"  kv_heads={t['num_key_value_heads']}  intermediate={t['intermediate_size']}")
for lt, idx in (("sliding", 0), ("full", next(i for i, x in enumerate(t["layer_types"]) if x != "sliding_attention"))):
    d = PL[idx]
    print(f"  {lt:>7} layer {idx}: " + "  ".join(f"{m}:{a}->{b}" for m, (a, b) in d.items()))
n_mod_per_layer = len(ALL) * len(PL)
print(f"  all-linear tensors/head = 2*{len(ALL)}*{len(PL)} = {2*n_mod_per_layer}")
print(f"  q/v-only  tensors/head = 2*{len(QV)}*{len(PL)} = {2*len(QV)*len(PL)}")
print("  upper-bound notes: kv-shared layers (num_kv_shared_layers="
      f"{t['num_kv_shared_layers']}) counted as if every layer owns k/v; "
      "use_double_wide_mlp=True per-layer-input path assumed to add no LoRA-targeted linears.")

# ---------- 3. PER-HEAD TABLE ----------
print()
print("=" * 78)
print("STEP 3  PER-HEAD BYTES  ranks 8/16/64/128 x {all-linear, q/v-only}")
print("=" * 78)
rows = {}
print(f"{'target':>10} {'rank':>5} {'params/head':>13} {'bf16 B':>12} {'bf16 MiB':>10} "
      f"{'+10% MiB':>10} {'fp32 MiB':>10}")
for name, mods in (("all-linear", ALL), ("q/v-only", QV)):
    for r in RANKS:
        p, b = set_bytes(PL, mods, r, DT_SAVED)
        rows[(name, r)] = (p, b)
        print(f"{name:>10} {r:>5} {p:>13,} {b:>12,} {b/2**20:>10.2f} "
              f"{b*1.1/2**20:>10.2f} {p*DT_TRAIN/2**20:>10.2f}")

# ---------- 4. HEAD-SET BUDGET MATH ----------
print()
print("=" * 78)
print("STEP 4  HEAD SETS vs 3 GiB CAP = {:,} B   (base submission measured {} B)".format(CAP, BASE_SUBMISSION))
print("=" * 78)
sets = {"MIN-3 (router+crow+analyzer)": HEADS[:3], "FULL-4 (+planner)": HEADS}
print(f"{'set':>30} {'target':>10} {'rank':>5} {'adapters B':>14} {'+base B':>14} "
      f"{'%cap':>7} {'margin B':>15} {'max heads fit':>14}")
for sname, hs in sets.items():
    for name, mods in (("all-linear", ALL), ("q/v-only", QV)):
        for r in RANKS:
            _, b = rows[(name, r)]
            tot = len(hs) * math.ceil(b * (1 + OVERHEAD_SAFETY)) + BASE_SUBMISSION
            maxheads = (CAP - BASE_SUBMISSION) // math.ceil(b * (1 + OVERHEAD_SAFETY))
            print(f"{sname:>30} {name:>10} {r:>5} {len(hs)*math.ceil(b*1.1):>14,} {tot:>14,} "
                  f"{tot/CAP*100:>6.2f}% {CAP-tot:>15,} {maxheads:>14}")

# ---------- 5. CHOSEN ----------
r_ch, tgt_ch, n_ch = 16, "all-linear", 4
_, b = rows[(tgt_ch, r_ch)]
tot = n_ch * math.ceil(b * (1 + OVERHEAD_SAFETY)) + BASE_SUBMISSION
print()
print("=" * 78)
print("STEP 5  CHOSEN CHECK")
print("=" * 78)
print(f"  4 heads (router_lora, crow_lora, analyzer_lora, planner_lora) rank 16 all-linear")
print(f"  per-head bf16 = {b:,} B; with +10% = {math.ceil(b*1.1):,} B; x{n_ch} = {n_ch*math.ceil(b*1.1):,} B")
print(f"  + base submission {BASE_SUBMISSION:,} B -> total {tot:,} B = {tot/CAP*100:.2f}% of cap")
print(f"  margin = {CAP-tot:,} B ({(CAP-tot)/CAP*100:.2f}%)  [requirement: >=25%]")
ok = (CAP - tot) / CAP >= 0.25
print(f"  MARGIN OK: {ok}")
```

### Script output (verbatim, `submission/provenance/compute-adapter-budget.out`)

```text
==============================================================================
STEP 1  CROSS-VALIDATION: predicted vs measured sample adapter [S2 x S3]
==============================================================================
  31B layer-0 (sliding): hidden=5376 q_out=8192 (=heads32*head_dim256)
  predicted params r=4 q+o 1 layer = 108544  -> bf16 bytes = 217088
  measured   tensor data bytes     = 217088   file=217672  header=576
  MATCH: True
  measured safetensors overhead: 584 B = 0.269% of data  (~144 B/header-entry)
==============================================================================
STEP 2  E2B LINEAR INVENTORY [S1]  (MEASURED config, not estimated)
==============================================================================
  layers=35 (sliding=28, full_attention=7)  hidden=1536  heads=8  head_dim=256  global_head_dim=512  kv_heads=1  intermediate=6144
  sliding layer 0: q_proj:1536->2048  k_proj:1536->256  v_proj:1536->256  o_proj:2048->1536  gate_proj:1536->6144  up_proj:1536->6144  down_proj:6144->1536
     full layer 4: q_proj:1536->4096  k_proj:1536->512  v_proj:1536->512  o_proj:4096->1536  gate_proj:1536->6144  up_proj:1536->6144  down_proj:6144->1536
  all-linear tensors/head = 2*7*35 = 490
  q/v-only  tensors/head = 2*2*35 = 140
  upper-bound notes: kv-shared layers (num_kv_shared_layers=20) counted as if every layer owns k/v; use_double_wide_mlp=True per-layer-input path assumed to add no LoRA-targeted linears.
==============================================================================
STEP 3  PER-HEAD BYTES  ranks 8/16/64/128 x {all-linear, q/v-only}
==============================================================================
    target  rank   params/head       bf16 B   bf16 MiB   +10% MiB   fp32 MiB
all-linear     8     9,719,808   19,439,616      18.54      20.39      37.08
all-linear    16    19,439,616   38,879,232      37.08      40.79      74.16
all-linear    64    77,758,464  155,516,928     148.31     163.14     296.62
all-linear   128   155,516,928  311,033,856     296.62     326.29     593.25
  q/v-only     8     1,634,304    3,268,608       3.12       3.43       6.23
  q/v-only    16     3,268,608    6,537,216       6.23       6.86      12.47
  q/v-only    64    13,074,432   26,148,864      24.94      27.43      49.88
  q/v-only   128    26,148,864   52,297,728      49.88      54.86      99.75
==============================================================================
STEP 4  HEAD SETS vs 3 GiB CAP = 3,221,225,472 B   (base submission measured 117376 B)
==============================================================================
                           set     target  rank     adapters B        +base B    %cap        margin B  max heads fit
  MIN-3 (router+crow+analyzer) all-linear     8     64,150,734     64,268,110   2.00%   3,156,957,362            150
  MIN-3 (router+crow+analyzer) all-linear    16    128,301,468    128,418,844   3.99%   3,092,806,628             75
  MIN-3 (router+crow+analyzer) all-linear    64    513,205,863    513,323,239  15.94%   2,707,902,233             18
  MIN-3 (router+crow+analyzer) all-linear   128  1,026,411,726  1,026,529,102  31.87%   2,194,696,370              9
  MIN-3 (router+crow+analyzer)   q/v-only     8     10,786,407     10,903,783   0.34%   3,210,321,689            895
  MIN-3 (router+crow+analyzer)   q/v-only    16     21,572,814     21,690,190   0.67%   3,199,535,282            447
  MIN-3 (router+crow+analyzer)   q/v-only    64     86,291,253     86,408,629   2.68%   3,134,816,843            111
  MIN-3 (router+crow+analyzer)   q/v-only   128    172,582,503    172,699,879   5.36%   3,048,525,593             55
             FULL-4 (+planner) all-linear     8     85,534,312     85,651,688   2.66%   3,135,573,784            150
             FULL-4 (+planner) all-linear    16    171,068,624    171,186,000   5.31%   3,050,039,472             75
             FULL-4 (+planner) all-linear    64    684,274,484    684,391,860  21.25%   2,536,833,612             18
             FULL-4 (+planner) all-linear   128  1,368,548,968  1,368,666,344  42.49%   1,852,559,128              9
             FULL-4 (+planner)   q/v-only     8     14,381,876     14,499,252   0.45%   3,206,726,220            895
             FULL-4 (+planner)   q/v-only    16     28,763,752     28,881,128   0.90%   3,192,344,344            447
             FULL-4 (+planner)   q/v-only    64    115,055,004    115,172,380   3.58%   3,106,053,092            111
             FULL-4 (+planner)   q/v-only   128    230,110,004    230,227,380   7.15%   2,990,998,092             55
==============================================================================
STEP 5  CHOSEN CHECK
==============================================================================
  4 heads (router_lora, crow_lora, analyzer_lora, planner_lora) rank 16 all-linear
  per-head bf16 = 38,879,232 B; with +10% = 42,767,156 B; x4 = 171,068,624 B
  + base submission 117,376 B -> total 171,186,000 B = 5.31% of cap
  margin = 3,050,039,472 B (94.69%)  [requirement: >=25%]
  MARGIN OK: True
```

(path retargeted 2026-11-13 — project moved to C:\Users\aaron\scullm; the budget numbers themselves are unchanged)

### Reproduce

```
C:/Python313/python.exe C:/Users/aaron/scullm/submission/provenance/compute-adapter-budget.py
```

(path retargeted 2026-11-13 — project moved to C:\Users\aaron\scullm; the budget numbers themselves are unchanged)

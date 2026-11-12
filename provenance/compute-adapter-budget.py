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

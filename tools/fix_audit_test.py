#!/usr/bin/env python3
"""fix_audit_test.py -- INDEPENDENT audit tests for the B1+B2 fixes in
train_crow_gemma.py (written by ScareCrow:OpenRouter, 2026-11-12).

Provenance:
  - Fixed file under audit: C:\\Users\\aaron\\evo\\state\\gemma\\submission\\tools\\train_crow_gemma.py
    (loaded via importlib straight from disk -- no stub, no copy of the code).
  - Bug contract comes from gemma_dryrun.txt "FIXES APPLIED" + the measured
    dry-run failures it cites:
      run 2: NoMatchingPeftModuleError, target modules {'g','v',',','a','_','p','j',...}
             (resolve_targets() returned list(target_arg) -> 17 single chars).
      run 3: resolved all-linear list contained the suffix 'linear' and peft
             raised "Target module Gemma4ClippableLinear(...) is not supported"
             (QuantizedLinear subclasses nn.Linear; peft matches by suffix name).
  - Env: Rog CPU, python 3.13.12, torch 2.11.0 (real nn.Linear graph used for B2).
  - These assertions are written fresh from the bug descriptions; they are NOT
    the builder's self-test code (gemma_dryrun.txt "SELF-TEST RECEIPTS").

Run: PYTHONIOENCODING=utf-8 python fix_audit_test.py   (exit 0 = all green)
"""
import contextlib
import importlib.util
import io
import os
import sys
import traceback

FIXED_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "train_crow_gemma.py")

PASS_N = 0
FAIL_N = 0
OBS = []  # honest observations (not gate criteria)


def check(name, cond, detail=""):
    global PASS_N, FAIL_N
    if cond:
        PASS_N += 1
        print(f"  PASS  {name}")
    else:
        FAIL_N += 1
        print(f"  FAIL  {name} :: {detail}")
        OBS.append(f"FAIL {name} :: {detail}")


def note(msg):
    print(f"  OBS   {msg}")
    OBS.append(msg)


# ---------------------------------------------------------------- load REAL file
spec = importlib.util.spec_from_file_location("audit_tcg", FIXED_FILE)
tcg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tcg)

import torch.nn as nn  # torch 2.11.0+cpu on Rog (verified: pip show torch)

print(f"[audit] loaded REAL file: {FIXED_FILE}")
print(f"[audit] source identity: resolve_targets has comma-split comment: "
      f"{'split(\",\")' in repr(tcg.resolve_targets.__doc__ or '')}")
import inspect
b1_src = inspect.getsource(tcg.resolve_targets)
print(f"[audit] B1 line present in real source: "
      f"{'target_arg.split(\",\")' in b1_src}")


# ================================================================= B1: comma-split
# Bug contract: old code `return list(target_arg)` char-split the comma string.
# Fresh assertions below are framed on the MEASURED failure, not the builder's.

print("\n== B1: resolve_targets() comma handling ==")

# 1. The exact measured charsplit tripwire: result must NOT be the old
#    17-single-character list, and must be exactly the two module names.
house_two = "q_proj,k_proj"
old_bug_result = list(house_two)  # what the OLD code returned
got = tcg.resolve_targets(None, house_two)
check("B1 comma pair resolves to exactly ['q_proj','k_proj']",
      got == ["q_proj", "k_proj"], f"got {got!r}")
check("B1 old-bug tripwire: result != list(comma_string) (no charsplit)",
      got != old_bug_result, f"got {got!r}, old bug gave {old_bug_result!r}")
check("B1 no single-character names survive (the run-2 charsplit signature)",
      all(len(t) > 1 for t in got), f"got {got!r}")

# 2. Single name (no comma) passes through unchanged.
check("B1 single name 'v_proj' -> ['v_proj']",
      tcg.resolve_targets(None, "v_proj") == ["v_proj"],
      f"got {tcg.resolve_targets(None, 'v_proj')!r}")

# 3. Order preservation: comma path must keep the USER's order
#    (the all-linear path sorts; the comma path must not silently reorder).
check("B1 user order preserved ('k_proj,q_proj' stays reversed)",
      tcg.resolve_targets(None, "k_proj,q_proj") == ["k_proj", "q_proj"],
      f"got {tcg.resolve_targets(None, 'k_proj,q_proj')!r}")

# 4. Whitespace tolerance (strip) -- spaces around and between names.
check("B1 whitespace tolerated (' q_proj ,  k_proj ')",
      tcg.resolve_targets(None, " q_proj ,  k_proj ") == ["q_proj", "k_proj"],
      f"got {tcg.resolve_targets(None, ' q_proj ,  k_proj ')!r}")

# 5. Empty fragments from leading/trailing/double commas are dropped.
check("B1 empty fragments dropped (',q_proj,,k_proj,,')",
      tcg.resolve_targets(None, ",q_proj,,k_proj,,") == ["q_proj", "k_proj"],
      f"got {tcg.resolve_targets(None, ',q_proj,,k_proj,,')!r}")

# 6. THE CLI DEFAULT path: parse_args([]) default is the HOUSE 7-name comma
#    string; resolve_targets must turn it into exactly HOUSE's list.
a = tcg.parse_args([])
check("B1 argparse default is the HOUSE comma string",
      a.target_modules == ",".join(tcg.HOUSE["target_modules"]),
      f"got {a.target_modules!r}")
check("B1 HOUSE 7-name default resolves to exactly the 7 projections",
      tcg.resolve_targets(None, a.target_modules) == tcg.HOUSE["target_modules"],
      f"got {tcg.resolve_targets(None, a.target_modules)!r}")

# 7. Internal spaces are NOT re-split (only commas split) -- documents the
#    contract: a malformed name with a space survives as one token.
check("B1 commas are the only separator ('q proj,k_proj' keeps the space token)",
      tcg.resolve_targets(None, "q proj,k_proj") == ["q proj", "k_proj"],
      f"got {tcg.resolve_targets(None, 'q proj,k_proj')!r}")

# Honest edge probes (INFORMATIONAL, not gate criteria -- they characterize
# behaviour on inputs the CLI cannot produce via the argparse default):
try:
    got_none = tcg.resolve_targets(None, None)
    note(f"B1 None input -> returned {got_none!r} (no guard)")
except Exception as e:
    note(f"B1 None input -> raises {type(e).__name__} (no guard; NOT a "
         f"regression: the old list(None) behaved the same, and argparse "
         f"default makes None unreachable from the CLI)")
try:
    got_empty = tcg.resolve_targets(None, "")
    note(f"B1 empty string -> returned {got_empty!r} (empty target list "
         f"reaches peft downstream; pre-existing behaviour)")
except Exception as e:
    note(f"B1 empty string -> raises {type(e).__name__}")


# ================================================================= B2: wrapper exclusion
# Bug contract: QuantizedLinear SUBCLASSES nn.Linear and Gemma4ClippableLinear
# wraps one; the measured repr is
#   Gemma4ClippableLinear((linear): QuantizedLinear(in=768,out=768,bias=False,num_bits=8))
# peft matches by SUFFIX NAME, so the wrapper surfaced under the suffix
# 'linear' and peft could not wrap it.

print("\n== B2: all-linear wrapper exclusion ==")


class QuantizedLinear(nn.Linear):  # measured: subclasses nn.Linear
    pass


class Gemma4ClippableLinear(nn.Linear):  # measured repr: child module 'linear'
    def __init__(self, in_f, out_f):
        super().__init__(in_f, out_f)
        self.linear = QuantizedLinear(in_f, out_f)


class Inner(nn.Module):  # nests the run-3 killer suffix: attribute name 'linear'
    def __init__(self):
        super().__init__()
        self.linear = Gemma4ClippableLinear(8, 8)


class Block(nn.Module):
    def __init__(self):
        super().__init__()
        self.q_proj = nn.Linear(8, 8)             # REAL -> must be included
        self.up_proj = nn.Linear(8, 8)            # REAL -> must be included
        self.clip = Gemma4ClippableLinear(8, 8)   # wrapper -> excluded
        self.gate = QuantizedLinear(8, 8)         # wrapper -> excluded
        self.inner = Inner()                      # contains suffix-'linear' wrapper


class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.block0 = Block()
        self.block1 = Block()
        self.head = nn.Linear(8, 8)  # ordinary head, not lm_head


model = Model()
# Wrapper count: per Block = clip + gate + inner.linear = 3; two blocks -> 6.
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    got_all = tcg.resolve_all_linear(model)
printed = buf.getvalue()

check("B2 real nn.Linear targets kept, sorted",
      got_all == ["head", "q_proj", "up_proj"], f"got {got_all!r}")
check("B2 run-3 tripwire: suffix 'linear' NOT in all-linear targets",
      "linear" not in got_all, f"got {got_all!r}")
# Wrapper census (verified by enumeration): per Block = clip +
# clip.linear + gate + inner.linear (a Clippable w/ its own QuantizedLinear
# child) + inner.linear.linear = 5 -> two blocks = 10.
check("B2 exclusion count printed (exactly 10 wrappers across 2 blocks)",
      "excluded 10 quantization wrapper" in printed, f"printed={printed!r}")

# Plain nn.Linear is never a wrapper; the fragment check is name-based.
check("B2 _is_quant_wrapper(plain nn.Linear) is False",
      tcg._is_quant_wrapper(nn.Linear(8, 8)) is False)

# MRO sweep claim: a wrapper whose LEAF class name is innocent but whose
# ANCESTOR carries the quant fragment must still be caught.
class _QuantizedBase(nn.Linear):
    pass


class InnocentLeaf(_QuantizedBase):
    pass


check("B2 MRO sweep catches quant fragment in an ANCESTOR class name",
      tcg._is_quant_wrapper(InnocentLeaf(8, 8)) is True)
check("B2 leaf-name fragment ('quant' in the leaf itself) caught",
      tcg._is_quant_wrapper(QuantizedLinear(8, 8)) is True)
check("B2 clippable fragment caught (Gemma4ClippableLinear)",
      tcg._is_quant_wrapper(Gemma4ClippableLinear(8, 8)) is True)

# --- honest regression probe (FALSE POSITIVE risk, documented): a LEGITIMATE
# custom nn.Linear subclass whose class name merely CONTAINS 'quant' or
# 'clippable' is silently excluded from all-linear. This demonstrates the
# reach of the fragment check; for THIS submission (transformers 5.15.1 gemma4,
# real linears are bare nn.Linear) the practical exposure is low.
class QuantFreeLinear(nn.Linear):  # ironically named custom subclass
    pass


check("B2-risk documented: incidental 'quant' in a custom class name IS excluded",
      tcg._is_quant_wrapper(QuantFreeLinear(8, 8)) is True)
note("B2 RISK (low): fragment check ('quant'/'clippable' over the whole MRO) "
     "will also drop any legitimate custom nn.Linear subclass with 'quant' "
     "or 'clippable' incidentally in a class name. Standard checkpoints "
     "name real linears 'Linear', so exposure is checkpoint-specific.")

# --- wrapper-only base (QAT-direct): all-linear must refuse cleanly via
# SystemExit, not hand peft the cryptic "not supported".
class OnlyQAT(nn.Module):
    def __init__(self):
        super().__init__()
        self.clip = Gemma4ClippableLinear(8, 8)


qat_model = OnlyQAT()
try:
    with contextlib.redirect_stdout(io.StringIO()):
        tcg.resolve_targets(qat_model, "all-linear")
    check("B2 wrapper-only base raises SystemExit", False, "no exception raised")
except SystemExit as e:
    msg = str(e.code)
    check("B2 wrapper-only base raises SystemExit", True)
    check("B2 SystemExit message says 'unsupported'",
          "unsupported" in msg, f"msg={msg!r}")
    check("B2 SystemExit message points at dequantized/16-bit base",
          "dequantized" in msg, f"msg={msg!r}")
except Exception as e:  # anything else is a WRONG exception type
    check("B2 wrapper-only base raises SystemExit", False,
          f"raised {type(e).__name__}: {e}")

# --- mixed base: all-linear returns (does not raise) and the list is non-empty.
try:
    with contextlib.redirect_stdout(io.StringIO()):
        mixed = tcg.resolve_targets(model, "all-linear")
    check("B2 mixed base: all-linear resolves non-empty",
          isinstance(mixed, list) and len(mixed) > 0, f"got {mixed!r}")
except SystemExit as e:
    check("B2 mixed base: all-linear resolves non-empty", False,
          f"unexpected SystemExit: {e}")

# --- PRE-EXISTING head filter still intact after the B2 change (regression
# guard on the lm_head / visual / mtp exclusion that shipped before the fix).
class HeadModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.q_proj = nn.Linear(8, 8)
        self.lm_head = nn.Linear(8, 8)
        self.visual_fc1 = nn.Linear(8, 8)
        self.mtp_proj = nn.Linear(8, 8)


with contextlib.redirect_stdout(io.StringIO()):
    heads = tcg.resolve_all_linear(HeadModel())
check("B2 regression guard: lm_head/visual/mtp exclusion still works",
      heads == ["q_proj"], f"got {heads!r}")

# Honest observation on the PRE-EXISTING (not B2) head filter: it matches the
# fragment 'visual', not 'vision' -- so a gemma-style 'vision_tower...' name is
# NOT filtered by full-name. Largely moot: peft matches by suffix anyway, and
# this filter shipped before the B2 fix and was untouched by it.
class VisionNameModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.q_proj = nn.Linear(8, 8)
        self.vision_tower_fc = nn.Linear(8, 8)


with contextlib.redirect_stdout(io.StringIO()):
    vres = tcg.resolve_all_linear(VisionNameModel())
note(f"PRE-EXISTING head filter matches 'visual' not 'vision': a module named "
     f"'vision_tower_fc' resolves into all-linear ({vres!r}). Unchanged by "
     f"B1/B2; low impact (peft matches by suffix, so exclusion by full name "
     f"would not prevent a same-suffix wrap anyway).")

# --- nested child of a wrapper is ALSO excluded when reachable as a Linear
# (inner.linear IS a QuantizedLinear named '.linear' -> caught by suffix rule).
with contextlib.redirect_stdout(io.StringIO()):
    nested = tcg.resolve_all_linear(model)
check("B2 nested QuantizedLinear child excluded from suffix list",
      "linear" not in nested and "clip" not in nested, f"got {nested!r}")

# ---------------------------------------------------------------- accounting
print("\n== accounting ==")
print(f"[audit] PASS={PASS_N} FAIL={FAIL_N} OBS={len(OBS)}")
for o in OBS:
    print(f"[audit] obs: {o}")

if FAIL_N:
    print("[audit] RESULT: RED")
    sys.exit(1)
print("[audit] RESULT: GREEN (all independent assertions pass)")
sys.exit(0)

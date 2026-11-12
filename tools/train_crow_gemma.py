#!/usr/bin/env python3
"""Gemma LoRA trainer for the CROW decider (work order C2) - the Gemma variant
of the proven Qwen E1 trainer (evo/state/train_crow.py).

Same corpus contract, same completion-only masking:
  corpus_d.jsonl D-rows {"type":"D","options":[...],"answer":"A"|"B"|"C",
  "task_id":...} -> chat sample (system + user STATE/QUESTION/OPTIONS ->
  assistant letter); prompt tokens labelled -100, only the completion (+ the
  end-of-turn tokens the BASE TOKENIZER'S OWN chat template emits) trains.
  No Qwen tokens are hardcoded anywhere - the masking boundary comes from
  apply_chat_template() of the loaded base tokenizer.

Recipe = the HOUSE method that shipped TEV1 (evo/school/TEV1_METHOD.md):
  LoRA r16 alpha16 dropout0 on the 7 attention+MLP projections,
  lr 2e-4, warmup 10, 2 epochs, batch 1 x grad-accum 8 (effective 8),
  4-bit nf4 (double-quant, bf16 compute) base, adamw_8bit, seed 3407.
  All constants are argparse-configurable (defaults are the HOUSE values).

LANES (fallback is load-bearing):
  1. unsloth FastLanguageModel fast path (tried first, unless
     --fallback-transformers).
  2. TRL SFTTrainer + peft on plain transformers (same constants, same
     pre-tokenized completion-only dataset, same collator semantics).
  3. plain transformers Trainer + peft (the proven rescue pattern from
     train_crow.py) if TRL is absent.
  unsloth support for the gemma4 architecture is UNVERIFIED FOR BOTH SIZES
  (source: HARNESS_README.md tool_call_parser='gemma4' + training-lane-notes.md;
  no lane has ever loaded a gemma4 checkpoint here), so lane 2/3 may be the
  real lane. Lane 1 failures are caught and fall through honestly.

HARNESS CONSTRAINTS (state/gemma/HARNESS_README.md):
  - adapter rank cap: max_lora_rank <= 128 (this script refuses r > 128);
  - total unpacked submission < 3 GiB INCLUDING adapters/ (r16 on the 7
    projections of an E2B-scale base is far inside that; measured size is
    printed after save);
  - single-base rule: every agent in the submission declares one base model -
    train this adapter on the same base you declare in agent.yaml
    (gemm-4-e2b-it-qat-w4a16-ct family);
  - adapter layout: adapters/<name>/adapter_config.json +
    adapter_model.safetensors (PEFT save_pretrained output).

Run (CPU box = dry-run only; a real fit needs the Lappy GPU lease per
state/gemma/work-plan.md WO-T1, or a Kaggle GPU notebook with the base
weights attached at /kaggle/input):
  python train_crow_gemma.py --dry-run
  python train_crow_gemma.py --corpus <corpus_d.jsonl>
Env: GEMMA_BASE_PATH overrides the default base id; TMPDIR is redirected
(aaron-hostile unsloth compiled-cache trap, same cure as train_crow.py).
"""
import argparse
import json
import os
import sys
import traceback
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# submission/ root (this script lives in submission/tools/)
SUBMISSION_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir))
DEFAULT_CORPUS = os.path.join(SUBMISSION_DIR, "corpus", "corpus_d.jsonl")
# PEFT adapter output: submission/adapters/crow_lora/ (HARNESS_README.md 3.4
# layout - adapter_config.json + adapter_model.safetensors inside the dir).
DEFAULT_OUT = os.path.join(SUBMISSION_DIR, "adapters", "crow_lora")
# train_state.json deliberately lives OUTSIDE submission/ (worker scratch law,
# work-plan.md 3: submission carries only harness-allowed files).
DEFAULT_STATE = os.path.abspath(
    os.path.join(SUBMISSION_DIR, os.pardir, os.pardir, "train_state_crow_gemma.json"))

# ---------------------------------------------------------------------------
# BASE MODEL - MARKED CONSTANT, EDIT ME FOR A LOCAL/STAGED CHECKPOINT.
# 'google/gemma-4-E2B-it-qat-w4a16-ct' is the HF repo id of the declared
# competition base. LOCAL TRAINING NEEDS THE SAFETENSORS CHECKPOINT DOWNLOADED
# (gemma repos are license-gated: accept the license + HF_TOKEN) OR THE
# /kaggle/input DATASET ATTACHED on Kaggle - pass the mounted path with
# --base /kaggle/input/<dataset>/<checkpoint-dir> or export GEMMA_BASE_PATH.
# Nothing is staged locally right now (see tools/gemma_dryrun.txt, OQ3).
# ---------------------------------------------------------------------------
GEMMA_BASE_PATH = "google/gemma-4-E2B-it-qat-w4a16-ct"

MAX_LORA_RANK = 128  # harness cap (HARNESS_README.md 3.4: max_lora_rank <= 128)

LETTERS = "ABCDEFG"
SYSTEM = ("You are a decision maker. Given the state and the question, reply with "
          "EXACTLY one letter: the correct option.")

# HOUSE recipe constants (TEV1_METHOD.md 2a/2b - every default below cites it)
HOUSE = {
    "r": 16, "alpha": 16, "dropout": 0.0,
    "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj",
                       "gate_proj", "up_proj", "down_proj"],
    "lr": 2e-4, "warmup": 10, "epochs": 2,
    "micro": 1, "accum": 8,          # batch 1 x accum 8 = effective 8
    "seed": 3407,
    "four_bit": True,                # 4-bit nf4 (double-quant) base, bf16 compute
}

_TORCH = None


def torch():
    """Lazy torch import so --help and corpus checks work on a CPU-only box."""
    global _TORCH
    if _TORCH is None:
        import torch as _t
        _TORCH = _t
    return _TORCH


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


try:  # aaron-hostile unsloth compiled-cache trap (same cure as train_crow.py)
    _gtmp = os.path.expanduser("~/.cache/gemma-unsloth-tmp")
    os.makedirs(_gtmp, exist_ok=True)
    if os.access(_gtmp, os.W_OK):
        os.environ.setdefault("TMPDIR", _gtmp)
except OSError:
    pass
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


# --------------------------------------------------------------- corpus rows
def row_to_sample(row, idx):
    """D-row -> (messages, task_id) or (None, reason). Identical contract to
    train_crow.py row_to_sample."""
    if not isinstance(row, dict) or str(row.get("type", "")).upper() != "D":
        return None, "not a D row"
    opts = row.get("options")
    if not isinstance(opts, list) or len(opts) < 2:
        return None, "options must be a list of >=2"
    opts = [str(o) for o in opts]
    answer = str(row.get("answer", "")).strip().upper()
    if answer not in LETTERS or LETTERS.index(answer) >= len(opts):
        return None, f"bad answer {answer!r} for {len(opts)} options"
    if not (state := str(row.get("state", "")).strip()) and not row.get("question"):
        return None, "no state and no question"
    question = str(row.get("question", "")).strip() or "Pick the correct option."
    task_id = row.get("task_id", f"row{idx}")
    user = ("STATE: " + state + "\n"
            "QUESTION: " + question + "\n"
            "OPTIONS:\n" + "\n".join(f"{LETTERS[i]}) {o}" for i, o in enumerate(opts))
            + "\nANSWER LETTER:")
    msgs = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user},
        {"role": "assistant", "content": answer},
    ]
    return (msgs, str(task_id)), None


def read_corpus(path, cap=None):
    rows, rejects = [], []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for idx, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                rejects.append((idx, f"bad json: {exc}"))
                continue
            sample, why = row_to_sample(row, idx)
            if sample is None:
                rejects.append((idx, why))
            else:
                rows.append(sample)
            if cap and len(rows) >= cap:
                break
    return rows, rejects


def synthetic_rows(n=3):
    """Corpus-shaped fixtures used by --dry-run when no corpus_d.jsonl exists."""
    return [
        row_to_sample({"type": "D",
                       "state": "The system is online. Sensor A reads 42, sensor B reads 17.",
                       "question": "Which sensor is above threshold 30?",
                       "options": ["Sensor A", "Sensor B", "Both sensors"],
                       "answer": "A", "task_id": "dry-1"}, 0)[0],
        row_to_sample({"type": "D",
                       "state": "Queue depth 3, workers 3, all busy, ETA 4 min.",
                       "question": "Should the dispatcher admit the next job?",
                       "options": ["Admit", "Hold"],
                       "answer": "B", "task_id": "dry-2"}, 1)[0],
        row_to_sample({"type": "D",
                       "state": "Path A is 12 km with 2 lights; path B is 9 km with 6 lights.",
                       "question": "Which route arrives first in heavy traffic?",
                       "options": ["Route A", "Route B", "Either"],
                       "answer": "A", "task_id": "dry-3"}, 2)[0],
    ][:n]


# ------------------------------------------------------------- tokenization
# Masking boundary comes from the BASE TOKENIZER'S OWN chat template - no
# Qwen tokens (im_end / enable_thinking / <|...|>) are hardcoded anywhere.
def tok_attr(tok, name):
    v = getattr(tok, name, None)
    if v is None and hasattr(tok, "tokenizer"):  # VLM processor unwrapping
        v = getattr(tok.tokenizer, name, None)
    return v


def inner_tok(tok):
    it = getattr(tok, "tokenizer", tok)
    return it if it is not None else tok


def _template(tok, msgs, add_generation_prompt):
    return tok.apply_chat_template(msgs, tokenize=False,
                                   add_generation_prompt=add_generation_prompt)


def render_texts(tok, msgs):
    """(prompt_text, full_text) via the tokenizer's own template; if the
    template rejects a system role, fold system into the first user turn
    (generic fallback - still template-rendered, nothing token-specific)."""
    try:
        return _template(tok, msgs[:-1], True), _template(tok, msgs, False)
    except Exception as exc:
        print(f"[fmt] template rejected the message roles ({type(exc).__name__}); "
              f"folding system into the first user turn")
        sys_txt = "".join(m["content"] + "\n\n" for m in msgs[:-1]
                          if m.get("role") == "system").strip()
        rest = [m for m in msgs[:-1] if m.get("role") != "system"]
        if sys_txt and rest:
            rest[0] = dict(rest[0])
            rest[0]["content"] = sys_txt + "\n\n" + rest[0]["content"]
        elif sys_txt:
            rest = [{"role": "user", "content": sys_txt}]
        return _template(tok, rest, True), _template(tok, rest + [msgs[-1]], False)


def encode_sample(tok, msgs, max_len):
    """Completion-only labels via the template: preferred method renders the
    prompt (add_generation_prompt=True) and the full chat separately and
    takes full_ids[len(prompt_ids):] as the trainable completion; if the
    two tokenizations disagree at the boundary, falls back to the
    train_crow.py suffix method (prompt_ids + completion + eos)."""
    it = inner_tok(tok)
    prompt_text, full_text = render_texts(tok, msgs)
    prompt_ids = it(prompt_text, add_special_tokens=False)["input_ids"]
    full_ids = it(full_text, add_special_tokens=False)["input_ids"]
    method = "template-prefix"
    if full_ids[:len(prompt_ids)] == prompt_ids and len(full_ids) > len(prompt_ids):
        ids = full_ids
        labels = [-100] * len(prompt_ids) + full_ids[len(prompt_ids):]
    else:
        method = "suffix+eos"
        comp_ids = it(msgs[-1]["content"], add_special_tokens=False)["input_ids"]
        comp_ids = comp_ids + [tok_attr(tok, "eos_token_id")]
        ids = (prompt_ids + comp_ids)[:max_len]
        labels = ([-100] * len(prompt_ids) + comp_ids)[: len(ids)]
    assert all(isinstance(t, int) for t in ids), \
        "encoder returned non-token ids (processor bypass failed)"
    return {"input_ids": ids, "labels": labels, "_method": method}


def encode_corpus(tok, samples, max_len):
    out, dropped = [], 0
    for msgs, task_id in samples:
        ex = encode_sample(tok, msgs, max_len)
        if not any(l != -100 for l in ex["labels"]):
            dropped += 1  # truncation ate the whole completion; nothing to learn
            continue
        ex["task_id"] = task_id
        out.append(ex)
    return out, dropped


def pack_examples(examples, max_len):
    """Greedy block packing: concat samples up to max_len (each sample keeps
    its own per-token labels; padding is never packed)."""
    packed, cur_ids, cur_lab = [], [], []
    for ex in examples:
        if cur_ids and len(cur_ids) + len(ex["input_ids"]) > max_len:
            packed.append({"input_ids": cur_ids, "labels": cur_lab})
            cur_ids, cur_lab = [], []
        cur_ids = cur_ids + ex["input_ids"]
        cur_lab = cur_lab + ex["labels"]
    if cur_ids:
        packed.append({"input_ids": cur_ids, "labels": cur_lab})
    return packed


# ------------------------------------------------------------- model loading
# Class-name fragments identifying quantization wrapper Linears (dry-run B2:
# gemma-QAT QuantizedLinear SUBCLASSES nn.Linear and Gemma4ClippableLinear
# wraps one, so a bare isinstance match handed peft modules it cannot wrap ->
# "Target module Gemma4ClippableLinear(...) is not supported"). Checked over
# the whole MRO, which is isinstance-equivalent against any wrapper base
# without a version-fragile import of transformers-5.x-only classes.
_QUANT_WRAPPER_FRAGMENTS = ("quant", "clippable")


def _is_quant_wrapper(mod):
    """True for QAT/quantization wrapper Linears (QuantizedLinear,
    Gemma4ClippableLinear, ...): matched by class identity over the MRO."""
    return any(f in cls.__name__.lower()
               for cls in type(mod).__mro__
               for f in _QUANT_WRAPPER_FRAGMENTS)


def resolve_all_linear(model):
    """Suffix names of every REAL nn.Linear in the text tower (for
    --target-modules all-linear), excluding lm_head / vision / mtp heads AND
    quantization wrapper modules (gemma-QAT wrappers subclass nn.Linear but
    peft cannot wrap them directly - dry-run bug B2)."""
    names, n_wrappers = set(), 0
    T = torch()
    for name, mod in model.named_modules():
        if not isinstance(mod, T.nn.Linear):
            continue
        if _is_quant_wrapper(mod):
            n_wrappers += 1
            continue
        low = name.lower()
        if "lm_head" in low or "visual" in low or "mtp" in low:
            continue
        names.add(name.split(".")[-1])
    if n_wrappers:
        print(f"[lora] all-linear: excluded {n_wrappers} quantization wrapper "
              f"module(s) (QAT base; peft cannot wrap them directly)")
    return sorted(names)


def resolve_targets(model, target_arg):
    if target_arg == "all-linear":
        targets = resolve_all_linear(model)
        print(f"[lora] resolved all-linear -> {targets}")
        if not targets:
            raise SystemExit("[lora] --target-modules all-linear: no wrappable "
                             "nn.Linear left after excluding quantization "
                             "wrappers -> unsupported for this base "
                             "(needs a dequantized/16-bit base)")
        return targets
    # B1 fix: split on commas (the old list(target_arg) char-split
    # "q_proj,k_proj" into 17 single-character module names).
    return [t.strip() for t in target_arg.split(",") if t.strip()]


def load_model_unsloth(a, max_len):
    """Lane 1: unsloth fast path. Raises on any failure (caller falls through)."""
    from unsloth import FastLanguageModel  # must precede transformers/peft
    model, tok = FastLanguageModel.from_pretrained(
        a.base, max_seq_length=max_len, dtype=None,
        load_in_4bit=a.four_bit)  # unsloth 4-bit defaults to nf4
    targets = resolve_targets(model, a.target_modules)
    model = FastLanguageModel.get_peft_model(
        model, r=int(a.r), lora_alpha=int(a.alpha),
        lora_dropout=float(a.dropout), bias="none",
        target_modules=targets, use_gradient_checkpointing="unsloth",
        random_state=int(a.seed))
    print(f"[load] unsloth lane ok (4bit={a.four_bit}, max_len={max_len})")
    return model, tok


def load_model_fallback(a, max_len):
    """Lane 2/3 base+LoRA: plain transformers + peft. 4-bit = nf4
    double-quant, bf16 compute (HOUSE quantization)."""
    T = torch()
    from transformers import AutoConfig, AutoTokenizer
    import transformers as tfm
    tok = AutoTokenizer.from_pretrained(a.base)
    arch = None
    try:
        arch = AutoConfig.from_pretrained(a.base).architectures[0]
    except Exception:
        pass
    kwargs = dict(device_map="auto", trust_remote_code=True)
    if a.four_bit:
        from transformers import BitsAndBytesConfig
        kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=T.bfloat16)
        kwargs["torch_dtype"] = T.bfloat16
    else:
        kwargs["torch_dtype"] = T.bfloat16
    model = None
    for loader in ("AutoModelForCausalLM",
                   "AutoModelForImageTextToText", arch):
        if not loader:
            continue
        try:
            cls = getattr(tfm, loader)
            model = cls.from_pretrained(a.base, **kwargs)
            print(f"[load] fallback lane ok via {loader}")
            break
        except Exception as exc:
            print(f"[load] {loader} failed: {type(exc).__name__}: {exc}")
    if model is None:
        raise SystemExit("[load] all fallback loaders failed on " + a.base)
    model.gradient_checkpointing_enable()
    model.enable_input_require_grads()
    targets = resolve_targets(model, a.target_modules)
    from peft import LoraConfig, get_peft_model
    model = get_peft_model(model, LoraConfig(
        r=int(a.r), lora_alpha=int(a.alpha), lora_dropout=float(a.dropout),
        bias="none", task_type="CAUSAL_LM", target_modules=targets))
    return model, tok


def load_model(a, max_len):
    """Try lane 1 unless forced off; every lane-1 failure falls through to
    lane 2/3 honestly (unsloth gemma4 support is UNVERIFIED)."""
    if a.fallback_transformers:
        return load_model_fallback(a, max_len)
    try:
        return load_model_unsloth(a, max_len)
    except ImportError as exc:
        print(f"[load] unsloth not importable ({type(exc).__name__}: {exc}) "
              f"-> TRL/peft fallback lane")
    except Exception as exc:
        print(f"[load] unsloth lane FAILED ({type(exc).__name__}: {exc}) "
              f"-> TRL/peft fallback lane (gemma4 support in unsloth is "
              f"UNVERIFIED - the fallback is load-bearing)")
    return load_model_fallback(a, max_len)


# ------------------------------------------------------------------ training
class TrainStateCB:
    """Writes the state file {"status","step","loss","ts"} after each epoch,
    on train end, and at fit start (failure handled in main)."""

    def __init__(self, path):
        self.path = path
        self.last_loss = None

    def _write(self, status, step):
        try:
            with open(self.path, "w", encoding="utf-8") as fh:
                json.dump({"status": status, "step": step,
                           "loss": self.last_loss, "ts": now_iso()}, fh)
        except OSError as exc:
            print(f"[state] could not write {self.path}: {exc}")

    def on_log(self, args, state, control, logs=None, **kw):
        if logs and logs.get("loss") is not None:
            self.last_loss = round(float(logs["loss"]), 6)

    def on_epoch_end(self, args, state, control, **kw):
        self._write("training", state.global_step)
        print(f"[state] epoch end step={state.global_step} "
              f"loss={self.last_loss} -> {self.path}")

    def on_train_end(self, args, state, control, **kw):
        self._write("done", state.global_step)
        print(f"[state] train end step={state.global_step} -> {self.path}")


def _make_train_args(output_dir, a):
    """TrainingArguments (or TRL SFTConfig, a TrainingArguments subclass) with
    the HOUSE constants - identical for both lanes."""
    T = torch()
    try:
        import bitsandbytes  # noqa: F401
        optim = "adamw_8bit"
    except Exception:
        optim = "adamw_torch"
    kw = dict(output_dir=output_dir, num_train_epochs=float(a.epochs),
              per_device_train_batch_size=int(a.micro),
              gradient_accumulation_steps=int(a.accum),
              learning_rate=float(a.lr), warmup_steps=int(a.warmup),
              logging_steps=5, optim=optim, seed=int(a.seed),
              bf16=True, report_to="none", save_strategy="no",
              dataloader_drop_last=False,
              gradient_checkpointing=True)
    try:  # TRL >= SFTConfig era: SFTConfig subclasses TrainingArguments
        from trl import SFTConfig
        cfg = SFTConfig(max_seq_length=int(a.max_len), packing=False, **kw)
        print("[fit] args = TRL SFTConfig (packing=False, pre-tokenized data)")
    except Exception:
        from transformers import TrainingArguments
        cfg = TrainingArguments(**kw)
        print("[fit] args = transformers TrainingArguments")
    return cfg, optim, T


def build_trainer(model, tok, examples, a, out_dir, state_cb):
    """Lane 2 (TRL SFTTrainer) with lane 3 (plain transformers Trainer) as
    last resort. Identical constants, dataset and collator semantics - the
    completion-only labels are carried on the dataset either way and the
    explicit collator overrides any TRL label re-derivation."""
    data = pack_examples(examples, int(a.max_len)) if a.packing else examples
    print(f"[data] {len(examples)} samples -> {len(data)} "
          f"{'packed blocks' if a.packing else 'sequences'}; "
          f"micro={a.micro} accum={a.accum} (effective {a.micro * a.accum})")
    cfg, optim, T = _make_train_args(os.path.join(out_dir, "ckpt"), a)
    it = inner_tok(tok)
    it.padding_side = "right"

    class ListDataset(T.utils.data.Dataset):
        def __init__(self, rows):
            self.rows = rows

        def __len__(self):
            return len(self.rows)

        def __getitem__(self, i):
            return self.rows[i]

    class PadCollator:
        def __init__(self, pad_id):
            self.pad_id = pad_id

        def __call__(self, feats):
            maxlen = max(len(f["input_ids"]) for f in feats)
            batch = {"input_ids": [], "attention_mask": [], "labels": []}
            for f in feats:
                ids, lab = f["input_ids"], f["labels"]
                diff = maxlen - len(ids)
                batch["input_ids"].append(ids + [self.pad_id] * diff)
                batch["attention_mask"].append([1] * len(ids) + [0] * diff)
                batch["labels"].append(lab + [-100] * diff)
            return {k: T.tensor(v, dtype=T.long) for k, v in batch.items()}

    collator = PadCollator(tok_attr(tok, "pad_token_id"))
    rows = [{"input_ids": r["input_ids"], "labels": r["labels"]} for r in data]
    try:
        from trl import SFTTrainer
        trainer = SFTTrainer(model=model, args=cfg, processing_class=tok,
                             train_dataset=ListDataset(rows),
                             data_collator=collator, callbacks=[state_cb])
        print("[fit] lane = TRL SFTTrainer + peft (explicit collator: labels "
              "pass through untouched)")
    except Exception as exc:
        print(f"[fit] TRL SFTTrainer unavailable ({type(exc).__name__}: {exc}) "
              f"-> plain transformers Trainer (proven rescue lane)")
        from transformers import Trainer
        trainer = Trainer(model=model, processing_class=tok,
                          train_dataset=ListDataset(rows),
                          data_collator=collator, args=cfg,
                          callbacks=[state_cb])
    print(f"[fit] optimizer={optim}")
    return trainer


def write_state(path, status, step, loss):
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"status": status, "step": step, "loss": loss,
                       "ts": now_iso()}, fh)
    except OSError as exc:
        print(f"[state] could not write {path}: {exc}")


def gpu_report(tag):
    T = torch()
    if not T.cuda.is_available():
        print(f"[gpu] {tag}: cuda unavailable")
        return
    free, total = T.cuda.mem_get_info()
    print(f"[gpu] {tag}: allocated={T.cuda.memory_allocated()/2**30:.2f}GB "
          f"peak={T.cuda.max_memory_allocated()/2**30:.2f}GB "
          f"free={free/2**30:.2f}/{total/2**30:.2f}GB")


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        description="CROW Gemma LoRA trainer (HOUSE recipe, work order C2)")
    ap.add_argument("--base", default=os.environ.get("GEMMA_BASE_PATH",
                                                     GEMMA_BASE_PATH),
                    help="base model HF id or local checkpoint dir "
                         "(default: the marked GEMMA_BASE_PATH constant; "
                         "weights must be downloaded/attached)")
    ap.add_argument("--corpus", default=None,
                    help="corpus_d.jsonl (default: %s)" % DEFAULT_CORPUS)
    ap.add_argument("--out", default=DEFAULT_OUT,
                    help="PEFT adapter output dir (default: submission/adapters/crow_lora)")
    ap.add_argument("--state", default=DEFAULT_STATE,
                    help="train_state.json path (default: outside submission/)")
    # ---- HOUSE recipe constants, all configurable (defaults = HOUSE) ----
    ap.add_argument("--r", type=int, default=HOUSE["r"],
                    help="LoRA rank (HOUSE 16; harness cap 128)")
    ap.add_argument("--alpha", type=int, default=HOUSE["alpha"],
                    help="LoRA alpha (HOUSE 16)")
    ap.add_argument("--dropout", type=float, default=HOUSE["dropout"],
                    help="LoRA dropout (HOUSE 0)")
    ap.add_argument("--target-modules", default=",".join(HOUSE["target_modules"]),
                    help="comma list, or 'all-linear' "
                         "(HOUSE default: the 7 attention+MLP projections)")
    ap.add_argument("--lr", type=float, default=HOUSE["lr"],
                    help="learning rate (HOUSE 2e-4)")
    ap.add_argument("--warmup", type=int, default=HOUSE["warmup"],
                    help="warmup steps (HOUSE 10)")
    ap.add_argument("--epochs", type=float, default=HOUSE["epochs"],
                    help="epochs (HOUSE 2)")
    ap.add_argument("--micro", type=int, default=HOUSE["micro"],
                    help="per-device batch (HOUSE 1)")
    ap.add_argument("--accum", type=int, default=HOUSE["accum"],
                    help="grad accumulation (HOUSE 8; effective = micro*accum)")
    ap.add_argument("--seed", type=int, default=HOUSE["seed"],
                    help="seed (HOUSE 3407)")
    ap.add_argument("--max-len", type=int, default=512,
                    help="max seq len (D-row surface is short; decider "
                         "precedent 512; HOUSE chat lane used 2048)")
    ap.add_argument("--packing", action="store_true",
                    help="greedy block packing (off by default; single-letter "
                         "completions are tiny - keep off unless told)")
    ap.add_argument("--no-4bit", dest="four_bit", action="store_false",
                    help="load the base in bf16 instead of 4-bit nf4 "
                         "(HOUSE default: 4-bit nf4)")
    ap.add_argument("--dry-run", action="store_true",
                    help="load model + LoRA prep + tokenize 3 rows, then exit 0")
    ap.add_argument("--fallback-transformers", action="store_true",
                    help="skip the unsloth lane entirely (TRL/peft fallback)")
    args = ap.parse_args(argv)
    if args.r > MAX_LORA_RANK:
        raise SystemExit(f"[lora] r={args.r} exceeds the harness adapter rank "
                         f"cap {MAX_LORA_RANK} (HARNESS_README.md 3.4)")
    return args


def main(argv=None):
    a = parse_args(argv)
    print(f"[config] base={a.base}\n"
          f"[config] HOUSE recipe: r={a.r} alpha={a.alpha} dropout={a.dropout} "
          f"targets={a.target_modules} lr={a.lr} warmup={a.warmup} "
          f"epochs={a.epochs} micro={a.micro} accum={a.accum} "
          f"(effective {a.micro * a.accum}) 4bit_nf4={a.four_bit} "
          f"seed={a.seed} max_len={a.max_len} packing={a.packing}")

    if a.dry_run:
        corpus = a.corpus or (DEFAULT_CORPUS if os.path.exists(DEFAULT_CORPUS) else None)
        if corpus:
            samples, rejects = read_corpus(corpus, cap=3)
            print(f"[data] dry-run on first 3 real rows of {corpus} "
                  f"({len(rejects)} rejects in the first 3)")
            if not samples:
                raise SystemExit("[data] no valid rows in first 3 of " + corpus)
        else:
            samples = [(m, t) for m, t in synthetic_rows(3)]
            print("[data] dry-run on 3 synthetic corpus-shaped rows "
                  "(no corpus_d.jsonl yet - the C1 joiner owns that file)")
    else:
        corpus = a.corpus or DEFAULT_CORPUS
        if not os.path.exists(corpus):
            raise SystemExit("[data] corpus not found: " + corpus +
                             " - it is produced by the C1 joiner, not by this script")
        samples, rejects = read_corpus(corpus)
        print(f"[data] {len(samples)} usable rows, {len(rejects)} rejected "
              f"(first: {rejects[:3]})")
        if not samples:
            raise SystemExit("[data] corpus has no usable D rows")

    os.makedirs(a.out, exist_ok=True)
    state_path = a.state
    state_cb = TrainStateCB(state_path)

    try:
        model, tok = load_model(a, a.max_len)
    except SystemExit:
        raise
    except Exception as exc:
        write_state(state_path, "failed", 0, None)
        print(f"[load] FAILED: {type(exc).__name__}: {exc}")
        print("[load] is the base checkpoint staged? local training needs the "
              "safetensors downloaded (license-gated: HF_TOKEN) or the "
              "/kaggle/input dataset attached; pass --base <path>")
        traceback.print_exc()
        sys.exit(2)

    print(f"[tok] type={type(tok).__name__} eos={tok_attr(tok, 'eos_token')!r} "
          f"pad={tok_attr(tok, 'pad_token')!r}")
    encoded, dropped = encode_corpus(tok, samples, a.max_len)
    print(f"[fmt] {len(encoded)} encoded samples, {dropped} dropped "
          f"(completion truncated away)")

    if a.dry_run:
        it = inner_tok(tok)
        print("\n=== DRY RUN: completion-only masking check ===")
        for ex in encoded[:3]:
            unmasked = [t for t, l in zip(ex["input_ids"], ex["labels"]) if l != -100]
            print(f"  {ex.get('task_id')} [{ex['_method']}]: "
                  f"ids={len(ex['input_ids'])} "
                  f"masked={len(ex['labels']) - len(unmasked)} "
                  f"unmasked_decoded={it.decode(unmasked)!r}")
            print(f"    prompt tail: ...{it.decode(ex['input_ids'])[-110:]!r}")
        gpu_report("dry-run")
        n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
        n_all = sum(p.numel() for p in model.parameters())
        print(f"[lora] trainable={n_train:,} / {n_all:,} "
              f"({100 * n_train / max(n_all, 1):.3f}%)")
        print("DRY-RUN PASS: model + LoRA prep + tokenization verified; no fit run.")
        return

    n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[lora] trainable={n_train:,}")
    write_state(state_path, "starting", 0, None)
    try:
        trainer = build_trainer(model, tok, encoded, a, a.out, state_cb)
        print(f"[fit] starting: {len(encoded)} samples, HOUSE recipe per "
              f"config (GPU must already be granted)")
        trainer.train()
    except Exception as exc:
        write_state(state_path, "failed", 0, None)
        print(f"[fit] FAILED: {type(exc).__name__}: {exc}")
        traceback.print_exc()
        sys.exit(3)
    gpu_report("post-train")
    # PEFT save: adapter_config.json + adapter_model.safetensors inside a.out
    model.save_pretrained(a.out)
    tok.save_pretrained(a.out)
    files = {f: os.path.getsize(os.path.join(a.out, f))
             for f in sorted(os.listdir(a.out))}
    print(f"[save] PEFT adapter -> {a.out}")
    for f, sz in files.items():
        print(f"[save]   {f}  {sz:,} B")
    if "adapter_config.json" not in files or \
            not any(f.endswith(".safetensors") for f in files):
        print("[save] WARNING: expected adapter_config.json + "
              "adapter_model.safetensors (HARNESS_README.md 3.4 layout)")
    print("\n=== NEXT STEPS (do not run from here) ===")
    print(f"# eval the adapter against the C0 gate "
          f"(submission/eval-split.md): adapter arm STRICTLY > baseline arm, "
          f"both arms twice")
    print(f"# adapter dir is submission-relative: adapters/crow_lora; "
          f"submission total must stay < 3 GiB")
    print(f"# state file: {state_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Optional build-time SFT for a tiny English essay specialist.

Runtime remains ESP32-S3 only. Training happens on a PC/Mac and produces a
GPT-Neo checkpoint which is later converted to the CRDP v3 on-device format.

JSONL:
  {"prompt":"the importance of reading","response":"Reading is an important habit..."}

The loss is masked to response + EOS and uses the same User/Bot prefix as the
firmware.
"""

import argparse
import json
import math
from pathlib import Path

import torch
from torch.utils.data import DataLoader, TensorDataset

def encode_record(row, tok):
    prompt = str(row["prompt"]).strip()
    response = str(row["response"]).strip()
    if not prompt or not response:
        raise ValueError("prompt/response cannot be empty")
    prefix = f"User: Write a short English essay of about 120 words about {prompt}.\nBot:"
    a = tok(prefix, add_special_tokens=False).input_ids
    b = tok(" " + response, add_special_tokens=False).input_ids
    ids = a + b + [tok.eos_token_id]
    labels = [-100] * len(a) + b + [tok.eos_token_id]
    return ids, labels

def load_jsonl(path, tok, seq_len):
    ids_all, labels_all = [], []
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        try:
            ids, labels = encode_record(row, tok)
        except Exception as exc:
            raise ValueError(f"line {n}: {exc}") from exc
        ids_all.extend(ids)
        labels_all.extend(labels)
    blocks = len(ids_all) // seq_len
    if blocks == 0:
        raise ValueError("dataset is shorter than one sequence block")
    ids_all = ids_all[:blocks * seq_len]
    labels_all = labels_all[:blocks * seq_len]
    return (
        torch.tensor(ids_all, dtype=torch.long).view(blocks, seq_len),
        torch.tensor(labels_all, dtype=torch.long).view(blocks, seq_len),
    )

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out-dir", default="data/essay_model_8m")
    ap.add_argument("--base", default="TheREZOR/TinyTalk-2")
    ap.add_argument("--seq-len", type=int, default=256)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--warmup", type=int, default=100)
    args = ap.parse_args()

    from huggingface_hub import snapshot_download
    from transformers import GPTNeoForCausalLM, GPT2TokenizerFast

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print("[+] device:", device)

    snap = snapshot_download(
        repo_id=args.base,
        allow_patterns=["*.bin", "*.safetensors", "*.json", "merges.txt"],
    )
    tok = GPT2TokenizerFast.from_pretrained(snap)
    model = GPTNeoForCausalLM.from_pretrained(snap).to(device)

    x, y = load_jsonl(args.data, tok, args.seq_len)
    loader = DataLoader(TensorDataset(x, y),
                        batch_size=args.batch_size, shuffle=True)

    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    steps = len(loader) * args.epochs

    def lr_at(step):
        if step < args.warmup:
            return args.lr * step / max(args.warmup, 1)
        p = (step - args.warmup) / max(1, steps - args.warmup)
        return 1e-5 + 0.5 * (args.lr - 1e-5) * (1 + math.cos(math.pi * p))

    print(f"[+] params: {sum(p.numel() for p in model.parameters()) / 1e6:.2f}M")
    print(f"[+] training blocks: {len(x):,} steps: {steps:,}")

    step = 0
    for epoch in range(args.epochs):
        for xb, yb in loader:
            lr = lr_at(step)
            for group in opt.param_groups:
                group["lr"] = lr
            xb, yb = xb.to(device), yb.to(device)
            loss = model(xb, labels=yb).loss
            opt.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            step += 1
            if step % 50 == 0:
                print(f"    step {step}/{steps} loss={loss.item():.4f} lr={lr:.2e}")
        print(f"[+] epoch {epoch + 1}: loss={loss.item():.4f}")

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    model.cpu().save_pretrained(out, safe_serialization=False)
    tok.save_pretrained(out)
    print("[+] saved:", out)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Validate the English essay SFT JSONL format."""

import argparse
import json
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--min-response-chars", type=int, default=80)
    ap.add_argument("--max-response-chars", type=int, default=3000)
    args = ap.parse_args()

    errors = []
    records = 0
    for line_no, line in enumerate(Path(args.path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        records += 1
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_no}: invalid JSON: {exc}")
            continue
        if not isinstance(row, dict):
            errors.append(f"line {line_no}: record must be an object")
            continue
        prompt = str(row.get("prompt", "")).strip()
        response = str(row.get("response", "")).strip()
        if not prompt:
            errors.append(f"line {line_no}: missing prompt")
        if not response:
            errors.append(f"line {line_no}: missing response")
        if len(response) < args.min_response_chars:
            errors.append(f"line {line_no}: response too short")
        if len(response) > args.max_response_chars:
            errors.append(f"line {line_no}: response too long")

    print("records:", records)
    if errors:
        for item in errors[:50]:
            print("ERROR:", item)
        raise SystemExit(1)
    print("OK")

if __name__ == "__main__":
    main()

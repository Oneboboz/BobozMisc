# Build tools

These tools run on a PC/Mac only.

Direct model conversion:
```bash
python tools/convert_tinyessay_instruct.py --model 8M --min-count 3 --max-vocab 15500 --keep-bin
```

Optional essay fine-tune:
```bash
python tools/validate_essay_dataset.py data/essay_train.jsonl
python tools/finetune_essay.py --data data/essay_train.jsonl --out-dir data/essay_model_8m --epochs 3
python tools/convert_tinyessay_instruct.py --model-dir data/essay_model_8m --corpus tools/essay_prompts.txt --min-count 1 --max-vocab 15500 --max-pos 256 --keep-bin
```

The generated model arrays are intentionally ignored by Git. Runtime uses only the resulting ESP32-S3 firmware.

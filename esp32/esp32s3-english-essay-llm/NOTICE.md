# NOTICE

## ESP32-S3 inference engine

These files are vendored/adapted from:

https://github.com/therezor/cardputer-ai

- main/llm.h
- main/llm.cpp
- main/dot_q4_pie.S

The upstream source is MIT-licensed. The full upstream license text is kept at:

third_party/CARDPUTER_AI_LICENSE.txt

## Default model: TheREZOR/TinyTalk-2

https://huggingface.co/TheREZOR/TinyTalk-2

The model card identifies TinyTalk-2 as an 8M-parameter GPT-Neo model designed to run fully offline on ESP32-S3 and states a CC BY-NC-SA 4.0 license.

The model derives from:

- roneneldan/TinyStories-Instruct-8M
- allenai/soda
- roneneldan/TinyStoriesInstruct
- li2017dailydialog/daily_dialog
- allenai/sciq

The model card states that DailyDialog and SciQ-derived training material makes the released model non-commercial.

This repository does not commit model weights by default. The conversion script downloads the checkpoint and produces local generated artifacts.

## Tokenizer

The runtime uses GPT-2 byte-level BPE data derived from:

https://github.com/openai/gpt-2

GPT-2 source code is MIT-licensed.

## Original project files

The serial-only application glue, build files, validator, SFT helper and documentation added here are project files under the parent repository's license.

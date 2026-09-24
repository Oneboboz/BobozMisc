# 系统架构

```text
ESP32-S3
  │
  ├─ Audio / Mic
  │      ↓
  ├─ Conformer ASR
  │      ↓
  ├─ Tokenizer
  │      ↓
  ├─ Morphology + Dictionary
  │      ↓
  ├─ POS / Parser
  │      ↓
  ├─ Clause Parser
  │      ↓
  ├─ Translation Engine
  │      ↓
  └─ Display
```

## 模块职责

### ASR
只做 Audio → English Text。

### Dictionary
提供 word → definition，以及 word form → lemma。

### Morphology
例如 running → run、studies → study、went → go。

### Parser
识别主语、谓语、宾语、补语、定语、状语和从句边界。

### Translation
输入结构化句子，而不是简单的单词数组。

例如：

```text
Subject: I
Tense: present_perfect_progressive
Verb: work
Object: this project
Duration: three years
```

再根据中文表达习惯生成结果。

## 资源策略

- 高频词放 Flash。
- 大词典可放外部 Flash/SD。
- 规则表使用紧凑结构。
- 不规则词表使用排序数组或哈希。
- 中间 AST 尽量使用静态内存。
- 避免大量动态 String。
- ASR 模型使用 Flash/PSRAM。
- NLP 规则数据驱动。

## 测试

PC 端先测试：

`sentence → tokenizer → morphology → parser → translator`

ESP32 端再接：

`microphone → ASR → same NLP pipeline`

这样即使 ASR 尚未接入，也可以独立开发和测试翻译核心。

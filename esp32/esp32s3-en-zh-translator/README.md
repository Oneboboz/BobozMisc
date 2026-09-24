# ESP32-S3 英汉离线翻译器

> 项目状态：原型/开发准备阶段
> 目标平台：ESP32-S3

## 目标

把现有 ESP32-S3 英汉电子词典/语言分析工作，与 `lspr98/conformer-stt-s3` 的本地英语 ASR 路线整合，最终形成离线英汉翻译设备。

上游 ASR： https://github.com/lspr98/conformer-stt-s3

本仓库不直接复制未经确认许可证的第三方代码或模型，只保存集成规划、状态和开发任务。

## 总体架构

```text
英语语音
  ↓
麦克风 / Audio AFE
  ↓
ESP32-S3 Conformer ASR
  ↓
英文文本
  ↓
Tokenizer
  ↓
词形还原 / Dictionary
  ↓
POS / 句法分析
  ↓
从句识别
  ↓
英汉翻译
  ↓
中文显示
```

同时保留电子词典模式：英文单词 → 原形 → 词性 → 中文释义 → 词形/例句。

## 当前已有基础

- 已建立 ESP32-S3 本地英汉词典方向。
- 已生成 `dictionary_generated.cpp` 形式的词典数据。
- 已加入大量英语单词和中文释义。
- 已开始处理英语变形词。
- 已开始从“单词查询”向“句子翻译”扩展。
- 当前变形词识别仍需要继续修复。

## 关键原则

ASR、Dictionary、NLP、Translation、UI 必须分层，不能全部堆在 `main.cpp`。

ASR 只负责：

`Audio → English Text`

翻译核心则负责：

`English Text → Chinese`

## 后续阶段

### Phase 1：词形系统

处理 `-s/-es/-ed/-ing/-er/-est`、不规则动词、不规则复数、大小写、标点和 lemma 查询。

### Phase 2：句法

实现 tokenizer、POS、基本句型、助动词、情态动词、时态、介词短语和固定短语。

### Phase 3：从句

支持定语从句、宾语从句、主语/表语从句、原因/时间/条件/让步从句。

### Phase 4：翻译

从“逐词翻译”升级为结构化翻译，处理英语语序、中文语序、时态、固定搭配和从句重排。

### Phase 5：ASR

验证 `conformer-stt-s3` 在目标 ESP32-S3 板、麦克风、Flash/PSRAM 条件下的实际性能，再接入 NLP pipeline。

### Phase 6：产品化

加入显示界面、测试集、性能统计、功耗优化和长句稳定性。

## 最终目标

不是简单的“电子词典 + 逐词翻译”，而是在 ESP32-S3 资源限制下，实现一个能够理解常见英语语法结构、时态、短语和从句的离线英汉电子翻译器。


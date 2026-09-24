# ESP32-S3 English Essay LLM

一个**纯离线、单颗 ESP32-S3 本地运行**的英文作文实验项目。

目标是利用已经在 ESP32-S3 上验证过的 TinyTalk / TinyStories-Instruct GPT-Neo 8M 推理链，做一个专用的 **English Essay Mode**。运行时不需要 Wi-Fi、API、电脑或 SD 卡。

## 当前方案

默认模型使用 **TheREZOR/TinyTalk-2**，8M 级 GPT-Neo。上游项目已经在无 PSRAM 的 ESP32-S3 Cardputer 上用 Q4_0、int4 KV cache 和 ESP32-S3 PIE SIMD 跑通，报告约 5 tok/s。

本项目移除了 Cardputer 键盘、屏幕和 M5 组件，只保留推理内核和串口作文界面。

输入：

~~~text
essay> The importance of learning English
~~~

固件形成：

~~~text
User: Write a short English essay of about 120 words about The importance of learning English.
Bot:
~~~

随后直接在 ESP32-S3 上离线生成英文文本。

**重要：TinyTalk-2 不是英语考试作文专用模型。** 它是一个小型英文聊天/短文模型。本项目因此另外提供作文数据 SFT 工具，可在 PC/Mac 上把它继续微调成更偏作文的模型；微调、量化和转换完成后，运行时仍然只有 ESP32-S3。

## 技术路线

复用上游：

- GPT-Neo TinyTalk-2 / TinyStories-Instruct 8M
- Q4_0 权重
- ESP32-S3 PIE SIMD Q4×Q8
- int4 KV cache
- GPT-2 byte-level BPE
- 模型与 tokenizer 直接映射到 Flash

对应源码保留：

- `main/llm.h`
- `main/llm.cpp`
- `main/dot_q4_pie.S`

## 硬件

推荐至少：

- ESP32-S3
- 8 MB Flash
- 240 MHz

你之前的 **N16R8（16 MB Flash + 8 MB PSRAM）**在空间上更宽裕；本版本仍默认 72-token internal-RAM KV 工作窗口，以保持和上游 8M 路线一致。

如果是 **4 MB Flash** 的 S3 SuperMini，不能直接使用 8M 固件，应改成 3M 模型重新生成。

## 生成模型

### 直接使用 TinyTalk-2

PC/Mac：

~~~bash
python3 -m venv .venv
. .venv/bin/activate
pip install huggingface_hub tokenizers torch numpy transformers safetensors

python tools/convert_tinyessay_instruct.py \
  --model 8M \
  --min-count 3 \
  --max-vocab 15500 \
  --max-pos 256 \
  --keep-bin
~~~

生成：

~~~text
embed/model_neo_q4.bin
embed/tok_neo.bin
main/model_data.cpp
main/tok_data.cpp
~~~

这些生成物默认被 `.gitignore` 排除。

### 作文专门微调

JSONL 每行：

~~~json
{"prompt":"the importance of reading","response":"Reading is an important habit because ..."}
~~~

检查：

~~~bash
python tools/validate_essay_dataset.py data/essay_train.jsonl
~~~

训练：

~~~bash
python tools/finetune_essay.py \
  --data data/essay_train.jsonl \
  --out-dir data/essay_model_8m \
  --epochs 3
~~~

转换：

~~~bash
python tools/convert_tinyessay_instruct.py \
  --model-dir data/essay_model_8m \
  --corpus tools/essay_prompts.txt \
  --min-count 1 \
  --max-vocab 15500 \
  --max-pos 256 \
  --keep-bin
~~~

训练和转换发生在 PC/Mac；**ESP32-S3 只负责推理。**

## 编译

### PlatformIO

~~~bash
pio run
pio run -t upload
pio device monitor
~~~

### ESP-IDF

~~~bash
idf.py set-target esp32s3
idf.py build
idf.py flash
idf.py monitor
~~~

串口打开后：

~~~text
essay> The importance of learning English
~~~

## 串口命令

~~~text
/help
/temp 0.72
/top_p 0.90
/new
~~~

普通输入都会作为作文题目。

## 默认参数

- Model: TinyTalk-2 8M / GPT-Neo
- Quantization: Q4_0
- KV cache: int4
- KV working window: 72
- Position export: 256
- Temperature: 0.72
- Top-p: 0.90
- Target output: about 120 words
- Max generated tokens: 220

120 words 只是目标值，不是保证值。小模型可能提前停止、重复或跑题。

## 为什么没有直接选 28.9M TinyStories PLE？

ESP32-S3 已经有约 28.9M 参数的 TinyStories PLE 项目，但它主要做连续故事文本生成，不是 instruction-following 模型。

对于：

~~~text
Write an essay about ...
~~~

“能放进去”和“能理解任务”是两件事。

因此这里优先选择已有 User/Bot instruction/chat 训练，并已实机验证 ESP32-S3 推理链的 TinyTalk 系列。

## 许可证

本项目 glue code 依父仓库 MIT License。

`main/llm.h`、`main/llm.cpp`、`main/dot_q4_pie.S` 来自/改编自：

https://github.com/therezor/cardputer-ai

上游代码为 MIT，完整文本保存在 `third_party/CARDPUTER_AI_LICENSE.txt`。

默认 TinyTalk-2 模型为 **CC BY-NC-SA 4.0**，属于非商业用途路线；模型和训练数据归属见 `NOTICE.md`。

## 来源

- https://github.com/therezor/cardputer-ai
- https://huggingface.co/TheREZOR/TinyTalk-2
- https://huggingface.co/roneneldan/TinyStories-Instruct-8M
- https://github.com/openai/gpt-2

## 状态

**实验版。**

第一阶段：普通 ESP32-S3 完全离线地根据英文题目生成短文。

第二阶段：针对真实英语作文数据进行 SFT、量化评估、词表裁剪和 S3 实测。

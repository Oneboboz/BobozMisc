# BobozMisc

个人杂项工具库，用于集中保存小型脚本、补丁、配置、实验代码和临时工具。

这个仓库用于承载那些“值得保存，但没必要单独建立一个仓库”的内容。

## 目录

```text
.
├─ catgpt/       # CatGPT / AI 网关相关补丁与工具
├─ android/      # Android / APK 相关小工具
├─ esp32/        # ESP32 / Arduino / ESP-IDF
├─ windows/      # Windows / PowerShell / BAT
├─ termux/       # Termux 专用脚本
├─ scripts/      # 通用脚本
├─ patches/      # 通用源码补丁
├─ tools/        # 其他小工具
└─ archive/      # 已归档或实验性内容
```

## 已收录

### CatGPT

`catgpt/toolcalling-loop-fix-v2/`

用于修复 CatGPT 浏览器模式下 OpenAI-compatible Tool Calling 的重复调用循环。

主要针对：

- `assistant.tool_calls` 在 latest-turn 裁剪过程中丢失
- 已收到 `role=tool` 后仍重复调用相同工具
- `tool_choice=required` 导致二次工具调用
- `list_files → list_files → list_files` 这类循环

详细说明：

[catgpt/toolcalling-loop-fix-v2/README.md](catgpt/toolcalling-loop-fix-v2/README.md)

## 文件组织

多文件工具：

```text
category/
└─ project-name/
   ├─ README.md
   ├─ script.py
   └─ *.bat / *.ps1 / *.sh
```

单文件工具可以直接放在对应分类目录。

## 命名建议

默认使用小写 `kebab-case`：

```text
fastboot-helper.ps1
termux-network-test.sh
catgpt-toolcalling-fix
```

## 原则

这个仓库以“可直接拿来用”为目标。

实验性内容可以保留，但 README 应注明：

- 目标软件 / 硬件
- 测试环境
- 使用方法
- 已知限制
- 是否具有破坏性操作

第三方代码必须保留其原始许可证和来源要求。

## ESP32-S3 English Essay LLM

`esp32/esp32s3-english-essay-llm/`

纯离线 ESP32-S3 英语作文实验：复用 TinyTalk-2 / TinyStories-Instruct 8M 的 GPT-Neo Q4_0 + PIE SIMD 推理链，串口输入英文题目，直接在 S3 本地生成短文。包含模型转换、可选英语作文 SFT、数据集验证及 ESP-IDF / PlatformIO 工程。

## License

仓库提供 MIT License；但第三方项目、复制或修改的代码可能受其原始许可证约束，以对应目录中的许可证和上游项目说明为准。

# BobozMisc

个人杂项仓库，用于集中保存小型脚本、补丁、配置、实验代码和临时工具。

## 目录结构

```text
.
├─ catgpt/       # CatGPT / AI 网关相关补丁与工具
├─ android/      # Android / Termux 相关小工具
├─ esp32/        # ESP32 / MCU 实验与脚本
├─ windows/      # Windows / PowerShell / BAT
├─ termux/       # Termux 专用脚本
├─ scripts/      # 通用脚本
├─ patches/      # 通用源码补丁
└─ tools/        # 其他小工具
```

## 当前内容

### CatGPT

`catgpt/toolcalling-loop-fix-v2/`

用于修复 CatGPT 浏览器模式下 OpenAI-compatible Tool Calling 的重复调用循环。

主要针对：

- `assistant.tool_calls` 在 latest-turn 裁剪过程中丢失
- 已收到 `role=tool` 后仍重复调用相同工具
- `tool_choice=required` 导致二次工具调用
- `list_files → list_files → list_files` 这类循环

详细说明见：

[`catgpt/toolcalling-loop-fix-v2/README.md`](catgpt/toolcalling-loop-fix-v2/README.md)

## 文件命名建议

小脚本尽量使用清晰的项目目录：

```text
category/
└─ project-name/
   ├─ README.md
   ├─ script.py
   └─ *.bat / *.ps1 / *.sh
```

单文件工具可以直接放在对应分类目录。

## 原则

这个仓库以“可直接拿来用”为目标。能独立运行的小工具尽量附带 README 和使用方法；实验性内容可以保留，但要注明适用环境。

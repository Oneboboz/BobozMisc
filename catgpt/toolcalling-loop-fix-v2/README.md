# CatGPT Tool Calling Loop Fix V2

针对 [TheBadFella/CatGPT](https://github.com/TheBadFella/CatGPT) 浏览器模式下 OpenAI-compatible Tool Calling 重复调用问题。

## 修复内容

- 修复 latest-turn 裁剪时丢失 `assistant.tool_calls`。
- 已存在 `role=tool` 结果时，明确禁止重复相同工具。
- 不因 `tool_choice=required` 在工具结果回合机械触发第二次调用。
- 检测相同 `tool + arguments`，必要时转为最终自然语言回答。
- 自动备份原始 `src/api/openai_routes.py`。
- 自动执行 Python 语法检查。

## 安装

把 `patch_toolcalling.py` 放到 CatGPT 源码根目录：

```powershell
python .\patch_toolcalling.py
docker compose build --no-cache
docker compose up -d
docker compose ps
```

## 测试

用 Zoo Code 发送：

```
请使用一次 list_files 工具查看当前工作目录，然后告诉我结果。
```

预期：

```
tool_calls -> 执行工具 -> role=tool -> 最终回答
```

不应出现：

```
list_files -> list_files -> list_files -> ...
```

## 恢复

补丁会生成：

```
src/api/openai_routes.py.backup-YYYYMMDD-HHMMSS
```

用备份覆盖原文件即可恢复。

## 版本

这是针对 CatGPT 当前源码结构制作的补丁。上游源码发生较大变化后，需要重新核对目标函数。

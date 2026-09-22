from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime

TARGET = Path("src/api/openai_routes.py")
MARK = "CATGPT_TOOLCALL_LOOP_FIX_V3"


def fail(message):
    print("[ERROR] " + message)
    raise SystemExit(1)


if not TARGET.exists():
    fail("请把本脚本放到 CatGPT 源码项目根目录。")

src = TARGET.read_text(encoding="utf-8")
if MARK in src:
    print("[OK] V3 补丁已经应用。")
    raise SystemExit(0)

if "CATGPT_TOOLCALL_LOOP_FIX_V2" not in src:
    fail("检测不到 V2 补丁。请先应用 V2，再应用 V3。")

backup = TARGET.with_name(
    TARGET.name + ".backup-v3-" + datetime.now().strftime("%Y%m%d-%H%M%S")
)
shutil.copy2(TARGET, backup)
print("[OK] 已备份当前文件: " + str(backup))


def replace_once(text, old, new, label):
    if old not in text:
        fail("找不到 " + label + "，源码版本可能已改变。")
    return text.replace(old, new, 1)


# 1. V2 的核心误区：
#    有 tool result 时把“没有 tool_call”直接当最终答案。
#    V3 恢复 tool_choice=required 的正常语义，让模型继续寻找下一步工具。
old = '''    if not parse_error and not (
        tool_calls is None and _tool_choice_requires_call(tool_choice) and not has_tool_results
    ):
'''
new = '''    if not parse_error and not (
        tool_calls is None and _tool_choice_requires_call(tool_choice)
    ):
'''
src = replace_once(src, old, new, "V2 tool-call required 判断")


old = '''    # A follow-up containing tool results should normally produce the final answer,
    # even when the original request carried tool_choice=required. Do not force a
    # second JSON tool call merely because the client kept the original flag.
    if has_tool_results and parse_error is None and tool_calls is None:
        return None, response_text, None

'''
src = replace_once(src, old, "", "V2 tool-result bypass")


# 2. V2 遇到重复调用时会强制生成最终回答，这会把“创建文件”等后续动作截断。
#    V3 改为：重复调用 -> 进入 continuation retry -> 寻找下一步工具。
old = '''        repeated = _repeated_tool_calls(tool_calls, executed_keys)
        if repeated:
            log.warning(
                "Preventing repeated tool-call loop: %s",
                ", ".join(call.function.name for call in repeated),
            )
            try:
                final_result = await client.send_message(
                    _build_tool_result_followup_prompt(repeated),
                    model=model_id,
                    **reasoning_kwargs,
                )
                final_text = final_result.message
                if _decode_tool_payload(final_text) is not None:
                    final_result = await client.send_message(
                        "Use the already-present tool result and provide the final answer now. "
                        "Do not call tools and do not output JSON.",
                        model=model_id,
                        **reasoning_kwargs,
                    )
                    final_text = final_result.message
                return None, final_text, final_result
            except Exception as exc:
                raise HTTPException(
                    status_code=502,
                    detail=f"Could not recover repeated tool-call loop: {exc}",
                ) from exc
        return tool_calls, response_text, None
'''
new = '''        repeated = _repeated_tool_calls(tool_calls, executed_keys)
        if repeated:
            log.warning(
                "V3 detected repeated completed tool call: %s",
                ", ".join(call.function.name for call in repeated),
            )
            parse_error = ToolCallParseError(
                "The model repeated an already-executed tool call. It must continue with the next necessary tool action."
            )
            tool_calls = None
        else:
            return tool_calls, response_text, None
'''
src = replace_once(src, old, new, "V2 重复 tool call recovery")


# 3. retry 时分两种情况：
#    - 新回合：修复普通 tool-call JSON
#    - 已有 tool result：继续原任务，寻找 NEXT 工具，不能只复述 result
old = '''    retry_reason = parse_error or ToolCallParseError(
        "A tool call was required but none was returned"
    )
    log.warning("Tool response was not usable; retrying once: %s", retry_reason)
    try:
        retry_result = await client.send_message(
            _build_tool_call_retry_prompt(retry_reason),
            model=model_id,
            **reasoning_kwargs,
        )
'''
new = '''    if has_tool_results:
        retry_prompt = (
            "Continue the original user task from the current conversation. "
            "A previous tool call has already been executed and its result is available. "
            "Do NOT repeat that completed tool call. "
            "Determine the NEXT necessary action from the original user request. "
            "If another tool is required, return exactly one JSON fenced tool_calls object "
            "using the next appropriate tool and valid JSON arguments. "
            "Do not merely summarize or repeat the previous tool result."
        )
        log.warning(
            "Tool continuation was not usable; retrying once: %s",
            parse_error or "missing next tool call",
        )
    else:
        retry_reason = parse_error or ToolCallParseError(
            "A tool call was required but none was returned"
        )
        retry_prompt = _build_tool_call_retry_prompt(retry_reason)
        log.warning("Tool response was not usable; retrying once: %s", retry_reason)

    try:
        retry_result = await client.send_message(
            retry_prompt,
            model=model_id,
            **reasoning_kwargs,
        )
'''
src = replace_once(src, old, new, "tool-call retry prompt")


# 4. retry 后也禁止回到刚刚已经执行过的同一调用。
old = '''        tool_calls = _parse_tool_calls(response_text, tools)
    except ToolCallParseError as exc:
'''
new = '''        tool_calls = _parse_tool_calls(response_text, tools)
        repeated = _repeated_tool_calls(tool_calls, executed_keys)
        if repeated:
            raise HTTPException(
                status_code=502,
                detail=(
                    "Provider repeated an already-executed tool call after continuation retry: "
                    + ", ".join(call.function.name for call in repeated)
                ),
            )
    except ToolCallParseError as exc:
'''
src = replace_once(src, old, new, "retry 后重复调用检查")


# 5. 标记 V3，防止重复应用。
src = src.replace(
    "MARK = \"CATGPT_TOOLCALL_LOOP_FIX_V2\"",
    "MARK = \"CATGPT_TOOLCALL_LOOP_FIX_V3\"",
    1,
)

TARGET.write_text(src, encoding="utf-8")
subprocess.run([sys.executable, "-m", "py_compile", str(TARGET)], check=True)

print("[OK] Python 语法检查通过。")
print("[OK] Tool Calling V3 修复完成。")
print("[OK] 备份文件: " + str(backup))

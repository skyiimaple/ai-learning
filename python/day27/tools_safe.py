"""含高风险工具；执行层做确认与重试。"""

from __future__ import annotations

import json
import time
from pathlib import Path

RISKY = {"delete_file"}


def delete_file(path: str, *, confirm: bool = False) -> str:
    p = Path(path)
    if not confirm:
        return json.dumps({"status": "need_confirm", "path": str(p)})
    if not p.exists():
        return json.dumps({"error": "not found"})
    # 演示：只允许删 day27/tmp_playground 下文件
    playground = Path(__file__).with_name("tmp_playground").resolve()
    rp = p.resolve()
    if playground not in rp.parents and rp != playground:
        return json.dumps({"error": "path not allowed"})
    rp.unlink()
    return json.dumps({"deleted": str(rp)})


def run_tool_with_retry(name: str, arguments: dict, *, retries: int = 2) -> str:
    last = ""
    for i in range(retries + 1):
        if name == "delete_file":
            last = delete_file(
                str(arguments.get("path", "")),
                confirm=bool(arguments.get("confirm", False)),
            )
        else:
            # 复用 day26.run_tool
            from tools_bridge import run_tool

            last = run_tool(name, arguments)
        err = "error" in last or "need_confirm" in last
        if not err or "need_confirm" in last:
            return last
        time.sleep(0.3 * (i + 1))
    return last

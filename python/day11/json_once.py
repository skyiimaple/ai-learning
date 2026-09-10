import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from common.llm import chat_completions

SYSTEM = """你是数据抽取助手。
规则：
1. 只输出一个 JSON 对象，不要 Markdown，不要代码块，不要解释。
2. 字段必须且只能是：
   - summary: string  （一句话中文摘要）
   - students: array，每项为 {"name": string, "score": number}
   - pass_count: number  （分数>=60 的人数）
3. 文本里没出现的学生不要编造。
4. score 必须是数字，不要带引号。
"""

USER_TEXT = """
期末成绩：Alice 80 分，Bob 95，Carol 70，Frank 才 59。
请按规则抽取。
"""


def extract_json_text(raw: str) -> str:
    """模型有时仍会包 ```json，做一层兜底剥离。"""
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        return fence.group(1).strip()
    # 兜底：取第一个 { 到最后一个 }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


def main():
    data = chat_completions(
        [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": USER_TEXT},
        ],
        temperature=0,
    )
    raw = data["choices"][0]["message"]["content"]
    print("=== raw ===")
    print(raw)
    print("=== parsed ===")
    obj = json.loads(extract_json_text(raw))
    print(json.dumps(obj, ensure_ascii=False, indent=2))
    print("usage:", data.get("usage"))


if __name__ == "__main__":
    main()

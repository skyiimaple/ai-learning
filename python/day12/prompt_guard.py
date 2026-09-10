import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from common.llm import chat_completions

SYSTEM = """你是「校内成绩问答助手」，不是全能聊天机器人。

【允许】
- 只根据用户消息里明确给出的成绩作答
- 回答是否及格、谁更高、平均分（仅基于已给数据）

【禁止】
- 编造不存在的学生或分数
- 回答与成绩无关的问题（政治、医疗、写代码等）
- 输出 Markdown 代码块

【输出格式】严格 JSON：
{
  "ok": boolean,
  "answer": string,
  "refuse_reason": string | null
}
若问题越权或信息不足：ok=false，并填写 refuse_reason。
"""


def extract_json(raw: str) -> dict:
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        text = text[start : end + 1]
    return json.loads(text)


def ask(user: str) -> None:
    data = chat_completions(
        [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
        temperature=0,
    )
    raw = data["choices"][0]["message"]["content"]
    print("\nQ:", user)
    print("raw:", raw)
    try:
        print("parsed:", json.dumps(extract_json(raw), ensure_ascii=False))
    except Exception as e:
        print("parse failed:", e)


if __name__ == "__main__":
    ask("Alice 80，Bob 95。谁更高？")
    ask("帮我写一段 React useEffect 示例")
    ask("Carol 考得怎么样？")  # 未提供分数，应拒绝或 ok=false

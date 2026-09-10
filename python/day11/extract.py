import json
import re
import sys
from pathlib import Path

from pydantic import ValidationError, model_validator
from schemas import ScoreReport

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from common.llm import chat_completions

SYSTEM = """你是数据抽取助手。
规则：
1. 只输出一个 JSON 对象，不要 Markdown，不要代码块，不要解释。
2. 字段必须且只能是：
   - summary: string
   - students: array，每项 {"name": string, "score": number}
   - pass_count: number（score>=60 的人数，必须与 students 一致）
3. 不要编造文本中未出现的学生。
"""


def extract_json_text(raw: str) -> str:
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        return fence.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


class ScoreReportStrict(ScoreReport):
    @model_validator(mode="after")
    def check_pass_count(self):
        expected = sum(1 for s in self.students if s.score >= 60)
        if self.pass_count != expected:
            raise ValueError(
                f"pass_count={self.pass_count} 与实际及格人数 {expected} 不一致"
            )
        return self


def extract_score_report(text: str) -> ScoreReportStrict:
    data = chat_completions(
        [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": text},
        ],
        temperature=0,
    )
    raw = data["choices"][0]["message"]["content"]
    try:
        obj = json.loads(extract_json_text(raw))
        return ScoreReportStrict.model_validate(obj)
    except (json.JSONDecodeError, ValidationError, ValueError) as e:
        raise RuntimeError(f"结构化失败: {e}\n原始输出:\n{raw}") from e


if __name__ == "__main__":
    sample = "期末：Ada 91，Bob 55，Cara 88。请抽取。"
    report = extract_score_report(sample)
    print(report.model_dump_json(indent=2, ensure_ascii=False))

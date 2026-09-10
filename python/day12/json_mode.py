import json
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from common.llm import get_llm_config


def chat_json(messages: list[dict]) -> dict:
    cfg = get_llm_config()
    url = f"{cfg['base_url']}/v1/chat/completions"
    with httpx.Client(timeout=60.0) as client:
        r = client.post(
            url,
            headers={
                "Authorization": f"Bearer {cfg['api_key']}",
                "Content-Type": "application/json",
            },
            json={
                "model": cfg["model"],
                "messages": messages,
                "temperature": 0,
                "response_format": {"type": "json_object"},
            },
        )
        r.raise_for_status()
        return r.json()


if __name__ == "__main__":
    data = chat_json(
        [
            {
                "role": "system",
                "content": (
                    "抽取成绩为 JSON，字段：summary(string), "
                    "students([{name,score}]), pass_count(number)。只输出 JSON 对象。"
                ),
            },
            {
                "role": "user",
                "content": "Alice 80，Bob 95，Frank 59。",
            },
        ]
    )
    raw = data["choices"][0]["message"]["content"]
    print("raw:", raw)
    print("parsed:", json.dumps(json.loads(raw), ensure_ascii=False, indent=2))
    print("usage:", data.get("usage"))

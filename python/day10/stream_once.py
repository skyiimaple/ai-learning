import json
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from common.llm import get_llm_config


def stream_print(msg: str) -> None:
    cfg = get_llm_config()
    url = f"{cfg['base_url']}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {cfg['api_key']}",
        "Content-Type": "application/json",
    }
    data = {
        "model": cfg["model"],
        "messages": [{"role": "user", "content": msg}],
        "temperature": 0.7,
        "stream": True,
    }
    with httpx.Client(timeout=60.0) as client:
        with client.stream("POST", url, headers=headers, json=data) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                if line.startswith("data: "):
                    data = line[6:].strip()
                    if data == "[DONE]":
                        print()
                        break
                    chunk = json.loads(data)
                    delta = chunk["choices"][0]["delta"]
                    piece = delta.get("content") or ""
                    if piece:
                        print(piece, end="", flush=True)


if __name__ == "__main__":
    stream_print("用三句话介绍python,语速要感觉像在打字")

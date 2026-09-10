import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent  # python/
sys.path.insert(0, str(ROOT))
from common.llm import get_llm_config

llm_config = get_llm_config()


def chat_once(msg: str) -> str:
    url = f"{llm_config['base_url']}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {llm_config['api_key']}",
        "Content-Type": "application/json",
    }
    data = {
        "model": llm_config["model"],
        "messages": [{"role": "user", "content": msg}],
        "temperature": 0.7,
    }
    t0 = time.perf_counter()
    with httpx.Client(timeout=60.0) as client:
        r = client.post(url, headers=headers, json=data)
        r.raise_for_status()
        data = r.json()
    elapsed = time.perf_counter() - t0
    content = data["choices"][0]["message"]["content"]
    usage = data["usage"] or {}
    print(f"Time taken: {elapsed:.2f} seconds")
    print(f"Usage: {usage}")
    return content


if __name__ == "__main__":
    print(chat_once("用一句话介绍你自己"))

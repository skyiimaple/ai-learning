import os

import httpx
from dotenv import load_dotenv

load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com").rstrip("/")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")


def get_llm_config() -> dict:
    if not LLM_API_KEY:
        raise RuntimeError("缺少环境变量 LLM_API_KEY，请在 .env 里配置")
    return {
        "api_key": LLM_API_KEY,
        "base_url": LLM_BASE_URL,
        "model": LLM_MODEL,
    }


def chat_completions(
    messages: list[dict],
    temperature: float = 0.7,
    tools: list[dict] | None = None,
    tool_choice: str | dict | None = None,
) -> dict:
    """调用兼容 OpenAI 的 /v1/chat/completions，返回完整 JSON。"""
    cfg = get_llm_config()
    url = f"{cfg['base_url']}/v1/chat/completions"
    payload: dict = {
        "model": cfg["model"],
        "messages": messages,
        "temperature": temperature,
    }
    if tools is not None:
        payload["tools"] = tools
    if tool_choice is not None:
        payload["tool_choice"] = tool_choice

    with httpx.Client(timeout=60.0) as client:
        r = client.post(
            url,
            headers={
                "Authorization": f"Bearer {cfg['api_key']}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        r.raise_for_status()
        return r.json()


def chat_completions_stream(messages: list[dict], temperature: float = 0.7):
    """生成器：yield 文本片段 str。"""
    import json

    cfg = get_llm_config()
    url = f"{cfg['base_url']}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {cfg['api_key']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": cfg["model"],
        "messages": messages,
        "temperature": temperature,
        "stream": True,
    }
    with httpx.Client(timeout=60.0) as client:
        with client.stream("POST", url, headers=headers, json=payload) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line or not line.startswith("data: "):
                    continue
                data = line[6:].strip()
                if data == "[DONE]":
                    break
                chunk = json.loads(data)
                delta = chunk["choices"][0].get("delta") or {}
                piece = delta.get("content") or ""
                if piece:
                    yield piece

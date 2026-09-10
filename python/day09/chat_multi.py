import os

import httpx
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ["LLM_API_KEY"]
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com").rstrip("/")
MODEL = os.getenv("LLM_MODEL", "deepseek-chat")
SYSTEM = (
    "你是严格的成绩助手。只根据用户提供的分数作答；不知道就说不知道，不要编造学生。"
)


def complete(messages: list[dict]) -> str:
    with httpx.Client(timeout=60.0) as client:
        r = client.post(
            f"{BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json={"model": MODEL, "messages": messages, "temperature": 0.2},
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


def main():
    messages = [{"role": "system", "content": SYSTEM}]
    print("输入空行退出。")
    while True:
        user = input("you> ").strip()
        if not user:
            break
        messages.append({"role": "user", "content": user})
        reply = complete(messages)
        messages.append({"role": "assistant", "content": reply})
        print("bot>", reply)
        print(f"(messages 条数: {len(messages)})")


if __name__ == "__main__":
    main()

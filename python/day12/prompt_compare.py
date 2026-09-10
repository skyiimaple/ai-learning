import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from common.llm import chat_completions

COMPLAINT = "我上周买的耳机左耳没声，已经找过两次客服了，非常生气，要退货。"


def ask(messages: list[dict], label: str) -> None:
    data = chat_completions(messages, temperature=0)
    raw = data["choices"][0]["message"]["content"]
    print(f"\n===== {label} =====")
    print(raw)
    print("usage:", data.get("usage"))


def zero_shot() -> None:
    ask(
        [
            {
                "role": "system",
                "content": (
                    "把用户投诉整理成 JSON，字段："
                    "category, urgency(low|mid|high), summary, need_refund(boolean)。"
                    "只输出 JSON。"
                ),
            },
            {"role": "user", "content": COMPLAINT},
        ],
        "Zero-shot",
    )


def few_shot() -> None:
    ask(
        [
            {
                "role": "system",
                "content": (
                    "把用户投诉整理成 JSON，字段："
                    "category, urgency(low|mid|high), summary, need_refund(boolean)。"
                    "只输出 JSON。参考示例学习分类口径。"
                ),
            },
            {
                "role": "user",
                "content": "外卖迟到 40 分钟，餐冷了，要赔偿。",
            },
            {
                "role": "assistant",
                "content": json.dumps(
                    {
                        "category": "delivery_delay",
                        "urgency": "mid",
                        "summary": "外卖严重迟到导致餐品变冷，用户要求赔偿",
                        "need_refund": False,
                    },
                    ensure_ascii=False,
                ),
            },
            {
                "role": "user",
                "content": "支付了两次钱，订单却显示失败，请尽快退款。",
            },
            {
                "role": "assistant",
                "content": json.dumps(
                    {
                        "category": "payment",
                        "urgency": "high",
                        "summary": "重复扣款且订单失败，用户要求退款",
                        "need_refund": True,
                    },
                    ensure_ascii=False,
                ),
            },
            {"role": "user", "content": COMPLAINT},
        ],
        "Few-shot",
    )


if __name__ == "__main__":
    zero_shot()
    few_shot()

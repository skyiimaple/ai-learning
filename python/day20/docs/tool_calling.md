# Tool Calling 笔记

模型只提议调用（tool_calls），真正执行是你的代码。

要把带 tool_calls 的 assistant 消息和 role=tool 结果写回 messages。

Day13/14 在 Python 手写循环；Day19 用 AI SDK 的 maxSteps。
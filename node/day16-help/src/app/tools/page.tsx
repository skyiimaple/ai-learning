"use client";

import { useChat } from "ai/react";

export default function ToolsChatPage() {
  const { messages, input, setInput, handleSubmit, isLoading, error, stop } =
    useChat({
      api: "/api/chat-tools",
      maxSteps: 5,
    });

  return (
    <main style={{ maxWidth: 640, margin: "40px auto", padding: 16 }}>
      <p
        style={{
          letterSpacing: "0.12em",
          textTransform: "uppercase",
          fontSize: 12,
        }}
      >
        Day19 · AI SDK Tools
      </p>
      <h1 style={{ marginTop: 8 }}>成绩助手（服务端 Tool Calling）</h1>
      <p style={{ color: "#666" }}>
        同源 <code>/api/chat-tools</code>；工具在 Route Handler 的{" "}
        <code>execute</code> 里跑。
      </p>

      <div
        style={{
          border: "1px solid #e5e5e5",
          borderRadius: 8,
          padding: 12,
          minHeight: 280,
          marginBottom: 16,
        }}
      >
        {messages.length === 0 ? (
          <span style={{ color: "#999" }}>试试：Frank 考了多少分？</span>
        ) : (
          messages.map((m) => (
            <div key={m.id} style={{ marginBottom: 14 }}>
              <strong>{m.role === "user" ? "你" : "助手"}：</strong>
              {m.content ? (
                <div style={{ whiteSpace: "pre-wrap" }}>{m.content}</div>
              ) : null}
              {m.toolInvocations?.length ? (
                <ul style={{ fontSize: 12, marginTop: 6, paddingLeft: 18 }}>
                  {m.toolInvocations.map((t) => (
                    <li key={t.toolCallId} style={{ marginBottom: 6 }}>
                      <code>{t.toolName}</code>
                      {"state" in t ? ` · ${t.state}` : ""}
                      {"args" in t ? (
                        <pre style={{ margin: "4px 0" }}>
                          {JSON.stringify(t.args, null, 2)}
                        </pre>
                      ) : null}
                      {"result" in t ? (
                        <pre style={{ margin: 0 }}>
                          {JSON.stringify(t.result, null, 2)}
                        </pre>
                      ) : null}
                    </li>
                  ))}
                </ul>
              ) : null}
            </div>
          ))
        )}
      </div>

      {error ? (
        <p style={{ color: "#b91c1c" }}>错误：{error.message}</p>
      ) : null}

      <form onSubmit={handleSubmit}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          rows={3}
          placeholder="比较一下 Bob 和平均分，谁更高？"
          style={{ width: "100%", padding: 12 }}
          disabled={isLoading}
        />
        <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
          <button type="submit" disabled={isLoading || !input.trim()}>
            {isLoading ? "生成中…" : "发送"}
          </button>
          {isLoading ? (
            <button type="button" onClick={() => stop()}>
              停止
            </button>
          ) : null}
        </div>
      </form>
    </main>
  );
}

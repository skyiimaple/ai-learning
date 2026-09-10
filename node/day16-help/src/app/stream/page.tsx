"use client";

import { useChat } from "@ai-sdk/react";

export default function StreamChatPage() {
  const { messages, input, setInput, handleSubmit, isLoading, error, stop } =
    useChat({
      api: "/api/chat",
    });

  return (
    <main style={{ maxWidth: 640, margin: "40px auto", padding: 16 }}>
      <p style={{ letterSpacing: "0.12em", textTransform: "uppercase", fontSize: 12 }}>
        Day17 · AI SDK useChat
      </p>
      <h1 style={{ marginTop: 8 }}>流式多轮对话</h1>
      <p style={{ color: "#666" }}>
        浏览器只打同源 <code>/api/chat</code>；Key 在 Route Handler。
      </p>

      <div
        style={{
          border: "1px solid #e5e5e5",
          borderRadius: 8,
          padding: 12,
          minHeight: 240,
          whiteSpace: "pre-wrap",
          marginBottom: 16,
        }}
      >
        {messages.length === 0 ? (
          <span style={{ color: "#999" }}>发一条消息开始…</span>
        ) : (
          messages.map((m) => (
            <div key={m.id} style={{ marginBottom: 12 }}>
              <strong>{m.role === "user" ? "你" : "助手"}：</strong>
              <div>{m.content}</div>
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
          placeholder="例如：用两句话介绍 FastAPI"
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
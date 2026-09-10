"use client";

import { FormEvent, useState } from "react";

type ToolStep = {
  tool: string;
  arguments: Record<string, unknown>;
  result: unknown;
};

type AgentOut = {
  answer: string;
  steps: ToolStep[];
  model: string;
  stopped?: boolean;
};

// const AGENT_URL =
//   process.env.NEXT_PUBLIC_AGENT_URL ?? "http://127.0.0.1:8015/agent/chat";
const AGENT_URL = "/api/agent";
export default function AgentPage() {
  const [message, setMessage] = useState(
    "比较一下 Bob 和平均分，谁更高？差多少？",
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [data, setData] = useState<AgentOut | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const text = message.trim();
    if (!text) {
      setError("请先输入问题");
      return;
    }
    setLoading(true);
    setError("");
    setData(null);
    try {
      const resp = await fetch(AGENT_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, temperature: 0 }),
      });
      const json = await resp.json().catch(() => ({}));
      if (!resp.ok) {
        throw new Error(
          typeof json.detail === "string"
            ? json.detail
            : `HTTP ${resp.status}`,
        );
      }
      setData(json as AgentOut);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ maxWidth: 640, margin: "40px auto", padding: 16 }}>
      <p
        style={{
          letterSpacing: "0.12em",
          textTransform: "uppercase",
          fontSize: 12,
        }}
      >
        Day16 · Next.js × Score Agent
      </p>
      <h1 style={{ marginTop: 8 }}>问成绩（经 Day15 API）</h1>
      <p style={{ color: "#666" }}>
        浏览器 → Next 页面 → <code>{AGENT_URL}</code>
      </p>

      <form onSubmit={onSubmit}>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          rows={4}
          style={{ width: "100%", padding: 12 }}
        />
        <button type="submit" disabled={loading} style={{ marginTop: 8 }}>
          {loading ? "请求中…" : "发送"}
        </button>
      </form>

      {error ? (
        <p style={{ color: "#b91c1c", marginTop: 16 }}>错误：{error}</p>
      ) : null}

      {data ? (
        <section style={{ marginTop: 24 }}>
          <h2>回答</h2>
          <pre style={{ whiteSpace: "pre-wrap" }}>{data.answer}</pre>
          <p style={{ color: "#666", fontSize: 14 }}>model: {data.model}</p>

          <h2>工具轨迹</h2>
          {data.steps?.length ? (
            <ul style={{ paddingLeft: 18 }}>
              {data.steps.map((s, i) => (
                <li key={`${s.tool}-${i}`} style={{ marginBottom: 12 }}>
                  <strong>{s.tool}</strong>
                  <pre style={{ fontSize: 12 }}>
                    {JSON.stringify(
                      { arguments: s.arguments, result: s.result },
                      null,
                      2,
                    )}
                  </pre>
                </li>
              ))}
            </ul>
          ) : (
            <p>本次没有调用工具</p>
          )}
        </section>
      ) : null}
    </main>
  );
}

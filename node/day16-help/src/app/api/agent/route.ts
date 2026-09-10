export const runtime = "nodejs";
export const maxDuration = 60;

const UPSTREAM =
  process.env.AGENT_UPSTREAM_URL ?? "http://127.0.0.1:8015/agent/chat";

export async function POST(req: Request) {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return Response.json({ detail: "无效 JSON" }, { status: 400 });
  }

  const message =
    typeof body === "object" &&
    body !== null &&
    "message" in body &&
    typeof (body as { message: unknown }).message === "string"
      ? (body as { message: string }).message.trim()
      : "";

  if (!message) {
    return Response.json({ detail: "message 不能为空" }, { status: 400 });
  }

  const temperature =
    typeof body === "object" &&
    body !== null &&
    "temperature" in body &&
    typeof (body as { temperature: unknown }).temperature === "number"
      ? (body as { temperature: number }).temperature
      : 0;

  try {
    const upstream = await fetch(UPSTREAM, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, temperature }),
      // Node 18+ 可用；超时靠 maxDuration
      cache: "no-store",
    });

    const data = await upstream.json().catch(() => ({}));

    if (!upstream.ok) {
      const detail =
        typeof data === "object" &&
        data !== null &&
        "detail" in data &&
        typeof (data as { detail: unknown }).detail === "string"
          ? (data as { detail: string }).detail
          : `上游错误 HTTP ${upstream.status}`;
      return Response.json({ detail }, { status: upstream.status });
    }

    return Response.json(data);
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return Response.json(
      { detail: `无法连接 Agent 上游（请确认 Day15 在 8015）：${msg}` },
      { status: 502 },
    );
  }
}
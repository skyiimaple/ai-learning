import Link from "next/link";

export default function Home() {
  return (
    <main style={{ maxWidth: 640, margin: "40px auto", padding: 16 }}>
      <h1>ai-learning / node</h1>
      <ul>
        <li>
          <Link href="/agent">Day16/18 · Score Agent（经 /api/agent）</Link>
        </li>
        <li>
          <Link href="/stream">Day17 · AI SDK 流式 Chat</Link>
        </li>
        <li>
          <Link href="/tools">Day19 · AI SDK Tool Calling</Link>
        </li>
      </ul>
    </main>
  );
}
import { createOpenAI } from "@ai-sdk/openai";
import { streamText } from "ai";

export const runtime = "nodejs";
export const maxDuration = 60;

const provider = createOpenAI({
  apiKey: process.env.LLM_API_KEY,
  baseURL: `${(process.env.LLM_BASE_URL ?? "https://api.deepseek.com").replace(/\/$/, "")}/v1`,
});

export async function POST(req: Request) {
  if (!process.env.LLM_API_KEY) {
    return new Response(JSON.stringify({ error: "缺少 LLM_API_KEY" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }

  const body = await req.json();
  const messages = body.messages ?? [];

  const result = streamText({
    model: provider(process.env.LLM_MODEL ?? "deepseek-chat"),
    messages,
    temperature: 0.7,
  });

  return result.toDataStreamResponse();
}
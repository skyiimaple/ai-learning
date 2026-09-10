import { createOpenAI } from "@ai-sdk/openai";
import { streamText, tool } from "ai";
import { z } from "zod";

import { avgScore, getScore } from "@/lib/scores";

export const runtime = "nodejs";
export const maxDuration = 60;

const provider = createOpenAI({
  apiKey: process.env.LLM_API_KEY,
  baseURL: `${(process.env.LLM_BASE_URL ?? "https://api.deepseek.com").replace(/\/$/, "")}/v1`,
});

export async function POST(req: Request) {
  if (!process.env.LLM_API_KEY) {
    return Response.json({ error: "缺少 LLM_API_KEY" }, { status: 500 });
  }

  const { messages } = await req.json();

  const result = streamText({
    model: provider(process.env.LLM_MODEL ?? "deepseek-chat"),
    system:
      "你是成绩助手。查分用 get_score，算平均用 avg_score。禁止编造数字。用中文简短回答。",
    messages,
    temperature: 0,
    maxSteps: 5,
    tools: {
      get_score: tool({
        description: "按姓名查单个学生成绩。未知返回 not found。",
        parameters: z.object({
          name: z.string().describe("学生英文名，如 Frank"),
        }),
        execute: async ({ name }) => getScore(name),
      }),
      avg_score: tool({
        description: "计算成绩表全体学生的平均分。",
        parameters: z.object({}),
        execute: async () => avgScore(),
      }),
    },
  });

  return result.toDataStreamResponse();
}

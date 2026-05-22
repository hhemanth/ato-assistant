import { NextRequest } from "next/server";

const BACKEND = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function POST(req: NextRequest) {
  const body = await req.json();

  let res: Response;
  try {
    res = await fetch(`${BACKEND}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    return new Response("Service unavailable. Please try again.", { status: 503 });
  }

  if (!res.ok) {
    const message =
      res.status === 429
        ? "You're sending messages too quickly. Please wait a moment and try again."
        : "Something went wrong. Please try again.";
    return new Response(message, { status: res.status });
  }

  return new Response(res.body, {
    headers: { "Content-Type": "text/plain; charset=utf-8" },
  });
}

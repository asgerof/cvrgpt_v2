import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const url = new URL(req.url);
  const q = url.searchParams.get("q") ?? "";
  const limit = url.searchParams.get("limit") ?? "10";

  const upstream = `${process.env.CVRGPT_API_URL}/v1/search?q=${encodeURIComponent(q)}&limit=${limit}`;

  const res = await fetch(upstream, {
    headers: { "x-api-key": process.env.CVRGPT_API_KEY as string },
    cache: "no-store",
  });

  const body = await res.text();
  return new NextResponse(body, {
    status: res.status,
    headers: {
      "content-type": res.headers.get("content-type") || "application/json",
    },
  });
}

import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const body = await req.json();
  
  const upstream = `${process.env.CVRGPT_API_URL}/v1/chat`;

  const res = await fetch(upstream, {
    method: "POST",
    headers: { 
      "Content-Type": "application/json",
      "X-API-Key": process.env.CVRGPT_API_KEY as string 
    },
    body: JSON.stringify(body),
  });

  const responseBody = await res.text();
  return new NextResponse(responseBody, {
    status: res.status,
    headers: {
      "content-type": res.headers.get("content-type") || "application/json",
    },
  });
}

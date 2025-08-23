import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const url = new URL(req.url);
  const thread_id = url.searchParams.get("thread_id");
  
  if (!thread_id) {
    return new NextResponse("Missing thread_id parameter", { status: 400 });
  }

  const upstream = `${process.env.CVRGPT_API_URL}/chat/export?thread_id=${encodeURIComponent(thread_id)}`;

  const res = await fetch(upstream, {
    headers: { "X-API-Key": process.env.CVRGPT_API_KEY as string },
  });

  if (!res.ok) {
    return new NextResponse("Export failed", { status: res.status });
  }

  const blob = await res.blob();
  return new NextResponse(blob, {
    status: 200,
    headers: {
      "Content-Type": "text/csv",
      "Content-Disposition": "attachment; filename=export.csv",
    },
  });
}

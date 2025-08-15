import { NextRequest, NextResponse } from "next/server";

export async function GET(
  req: NextRequest,
  { params }: { params: { cvr: string } }
) {
  const cvr = params.cvr;
  const upstream = `${process.env.CVRGPT_API_URL}/v1/company/${cvr}`;

  const res = await fetch(upstream, {
    headers: {
      "x-api-key": process.env.CVRGPT_API_KEY as string,
      // Forward If-None-Match for ETag support
      ...(req.headers.get("if-none-match") && {
        "if-none-match": req.headers.get("if-none-match") as string
      })
    },
    cache: "no-store",
  });

  const body = await res.text();
  const response = new NextResponse(body, {
    status: res.status,
    headers: {
      "content-type": res.headers.get("content-type") || "application/json",
    },
  });

  // Forward caching headers
  if (res.headers.get("etag")) {
    response.headers.set("etag", res.headers.get("etag") as string);
  }
  if (res.headers.get("cache-control")) {
    response.headers.set("cache-control", res.headers.get("cache-control") as string);
  }

  return response;
}

import { NextRequest, NextResponse } from "next/server";

export async function GET(
  req: NextRequest,
  { params }: { params: { cvr: string } }
) {
  const cvr = params.cvr;
  const upstream = `${process.env.CVRGPT_API_URL}/v1/accounts/latest/${cvr}`;

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

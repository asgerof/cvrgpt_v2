import { NextRequest, NextResponse } from "next/server";

export async function GET(
  req: NextRequest,
  { params }: { params: { cvr: string } }
) {
  const cvr = params.cvr;
  const upstream = `${process.env.CVRGPT_API_URL}/v1/compare/${cvr}/export`;

  const res = await fetch(upstream, {
    headers: { "x-api-key": process.env.CVRGPT_API_KEY as string },
  });

  if (!res.ok) {
    return new NextResponse("Export failed", { status: res.status });
  }

  const blob = await res.blob();
  return new NextResponse(blob, {
    status: 200,
    headers: {
      "Content-Type": "text/csv",
      "Content-Disposition": "attachment; filename=compare.csv",
    },
  });
}

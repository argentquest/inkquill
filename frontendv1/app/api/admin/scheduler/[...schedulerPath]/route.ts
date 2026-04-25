import { NextRequest, NextResponse } from "next/server";

import { requireAdmin } from "@/lib/require-admin";

export const runtime = "nodejs";

const SCHEDULER_BASE_URL =
  process.env.SCHEDULER_BASE_URL ??
  process.env.NEXT_PUBLIC_SCHEDULER_BASE_URL ??
  "http://127.0.0.1:8001";

function buildSchedulerUrl(request: NextRequest, schedulerPath: string[]) {
  const upstream = new URL(`/scheduler/${schedulerPath.join("/")}`, SCHEDULER_BASE_URL);
  request.nextUrl.searchParams.forEach((value, key) => {
    upstream.searchParams.set(key, value);
  });
  return upstream;
}

async function proxySchedulerRequest(
  request: NextRequest,
  context: { params: Promise<{ schedulerPath: string[] }> },
) {
  const denied = await requireAdmin(request);
  if (denied) return denied;

  const { schedulerPath } = await context.params;
  const upstreamUrl = buildSchedulerUrl(request, schedulerPath);

  try {
    const body =
      request.method === "GET" || request.method === "HEAD"
        ? undefined
        : await request.text();

    const upstreamResponse = await fetch(upstreamUrl, {
      method: request.method,
      headers: {
        "Content-Type": request.headers.get("content-type") ?? "application/json",
      },
      body,
      cache: "no-store",
    });

    const text = await upstreamResponse.text();
    return new NextResponse(text, {
      status: upstreamResponse.status,
      headers: {
        "Content-Type": upstreamResponse.headers.get("content-type") ?? "application/json",
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        message:
          error instanceof Error
            ? error.message
            : "Could not reach the scheduler service.",
      },
      { status: 503 },
    );
  }
}

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ schedulerPath: string[] }> },
) {
  return proxySchedulerRequest(request, context);
}

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ schedulerPath: string[] }> },
) {
  return proxySchedulerRequest(request, context);
}

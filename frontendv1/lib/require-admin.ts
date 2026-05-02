import { NextRequest, NextResponse } from "next/server";

function resolveBackendOrigin() {
  // Server-side internal URL takes priority (set in Docker via BACKEND_INTERNAL_URL).
  const internalUrl = process.env.BACKEND_INTERNAL_URL?.trim();
  if (internalUrl) {
    return internalUrl;
  }

  const configuredBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (!configuredBaseUrl || configuredBaseUrl.startsWith("/")) {
    return "http://localhost:8000";
  }

  return configuredBaseUrl.replace(/\/api\/v1\/?$/, "");
}

const BACKEND_ORIGIN = resolveBackendOrigin();

interface MePayload {
  success: boolean;
  data?: { is_admin?: boolean };
}

/**
 * Verifies the incoming request carries a valid admin session by forwarding
 * its cookies to FastAPI's /users/me endpoint.
 *
 * Returns null when the caller is a confirmed admin.
 * Returns a 401 or 403 NextResponse when access should be denied.
 */
export async function requireAdmin(request: NextRequest): Promise<NextResponse | null> {
  const cookie = request.headers.get("cookie") ?? "";

  let payload: MePayload;
  try {
    const res = await fetch(`${BACKEND_ORIGIN}/api/v1/users/me`, {
      headers: { cookie },
      cache: "no-store",
    });
    if (res.status === 401) {
      return NextResponse.json({ message: "Authentication required." }, { status: 401 });
    }
    payload = (await res.json()) as MePayload;
  } catch {
    return NextResponse.json({ message: "Could not verify session." }, { status: 503 });
  }

  if (!payload.success || !payload.data?.is_admin) {
    return NextResponse.json({ message: "Admin access required." }, { status: 403 });
  }

  return null;
}

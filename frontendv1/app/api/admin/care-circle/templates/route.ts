import { NextRequest, NextResponse } from "next/server";

import { readAvailableThemes, readTemplateInventory } from "@/lib/care-circle-template-admin";
import { requireAdmin } from "@/lib/require-admin";

export const runtime = "nodejs";

export async function GET(request: NextRequest) {
  const denied = await requireAdmin(request);
  if (denied) return denied;

  try {
    const [providers, themes] = await Promise.all([readTemplateInventory(), readAvailableThemes()]);
    return NextResponse.json({ providers, themes });
  } catch (error) {
    return NextResponse.json(
      { message: error instanceof Error ? error.message : "Could not load template inventory." },
      { status: 500 },
    );
  }
}

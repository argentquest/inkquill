import { NextRequest, NextResponse } from "next/server";

import { readTemplateEditorDocument, saveTemplateEditorDocument } from "@/lib/care-circle-template-admin";
import { requireAdmin } from "@/lib/require-admin";

export const runtime = "nodejs";

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ providerKey: string }> },
) {
  const denied = await requireAdmin(request);
  if (denied) return denied;

  try {
    const { providerKey } = await context.params;
    const theme = request.nextUrl.searchParams.get("theme") || "classic";
    const document = await readTemplateEditorDocument(providerKey, theme);
    return NextResponse.json(document);
  } catch (error) {
    return NextResponse.json(
      { message: error instanceof Error ? error.message : "Could not load template document." },
      { status: 500 },
    );
  }
}

export async function PUT(
  request: NextRequest,
  context: { params: Promise<{ providerKey: string }> },
) {
  const denied = await requireAdmin(request);
  if (denied) return denied;

  try {
    const { providerKey } = await context.params;
    const body = (await request.json()) as {
      theme?: string;
      templateHtml?: string;
      providerThemeCss?: string;
    };

    const theme = body.theme || "classic";
    if (typeof body.templateHtml !== "string" || typeof body.providerThemeCss !== "string") {
      return NextResponse.json({ message: "Template HTML and provider theme CSS are required." }, { status: 400 });
    }

    await saveTemplateEditorDocument({
      providerKey,
      theme,
      templateHtml: body.templateHtml,
      providerThemeCss: body.providerThemeCss,
    });

    return NextResponse.json({ message: "Template saved successfully." });
  } catch (error) {
    return NextResponse.json(
      { message: error instanceof Error ? error.message : "Could not save template document." },
      { status: 500 },
    );
  }
}

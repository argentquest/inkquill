"use client";

import { Loader2 } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

import { PageHeader } from "@/components/shell/page-header";

function ImagePreviewContent() {
  const searchParams = useSearchParams();
  const imageUrl = searchParams.get("url") ?? "";
  const title = searchParams.get("title") ?? "AI Generated Image";
  const description = searchParams.get("description") ?? "";
  const backUrl = searchParams.get("context_url");
  const backText = searchParams.get("context_text") || "Back";

  if (!imageUrl) {
    return (
      <div className="mx-auto max-w-2xl space-y-6">
        <div className="rounded-[28px] border border-red-200 bg-red-50 p-6 text-sm text-red-700">
          No image URL was provided to the preview.
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-panel">
        <div className="mb-4 flex items-center gap-2 text-sm font-semibold text-ink-900">
          <span className="flex size-5 items-center justify-center rounded-full bg-amber-100 text-amber-600 text-xs">AI</span>
          AI Generated Image Preview
        </div>
        <div className="overflow-hidden rounded-2xl">
          <img
            alt={title}
            className="h-auto w-full object-contain"
            src={imageUrl}
          />
        </div>
        {title && (
          <h1 className="mt-4 text-xl font-bold text-ink-900">{title}</h1>
        )}
        {description && (
          <p className="mt-2 text-sm text-ink-600">{description}</p>
        )}
        {backUrl && (
          <div className="mt-6">
            <a
              className="inline-flex items-center gap-2 rounded-full border border-black/10 bg-white/80 px-4 py-2.5 text-sm font-medium text-ink-700 shadow-sm transition hover:bg-white"
              href={backUrl}
            >
              {backText}
            </a>
          </div>
        )}
      </div>
    </div>
  );
}

export default function PublicImagePreviewPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        description="Public preview of an AI-generated image."
        eyebrow="Image Preview"
        title="AI Image Preview"
      />
      <Suspense
        fallback={
          <div className="flex h-64 items-center justify-center">
            <Loader2 className="size-6 animate-spin text-ink-500" />
          </div>
        }
      >
        <ImagePreviewContent />
      </Suspense>
    </div>
  );
}
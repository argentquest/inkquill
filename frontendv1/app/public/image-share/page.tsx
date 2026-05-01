"use client";

import { Loader2 } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

import { PageHeader } from "@/components/shell/page-header";

function ImageShareContent() {
  const searchParams = useSearchParams();
  const imageUrl = searchParams.get("image_url") ?? "";
  const title = searchParams.get("title") ?? "AI Generated Image";
  const description = searchParams.get("description") ?? "";
  const imageType = searchParams.get("type") ?? "AI Art";
  const owner = searchParams.get("owner") ?? "Creator";
  const date = searchParams.get("date") ?? "";
  const shareUrl = searchParams.get("share_url") ?? "";

  async function handleShare() {
    if (navigator.share) {
      try {
        await navigator.share({ title, text: description, url: shareUrl || window.location.href });
      } catch {
        // user cancelled
      }
    } else if (navigator.clipboard) {
      await navigator.clipboard.writeText(shareUrl || window.location.href);
    }
  }

  if (!imageUrl) {
    return (
      <div className="rounded-[28px] border border-red-200 bg-red-50 p-6 text-sm text-red-700">
        No image URL was provided to the share page.
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-panel">
        <div className="mb-4 flex items-center gap-2 text-sm font-semibold text-ink-900">
          <span className="flex size-5 items-center justify-center rounded-full bg-amber-100 text-amber-600 text-xs">Share</span>
          AI Image Share
        </div>
        <div className="overflow-hidden rounded-2xl">
          <img
            alt={title}
            className="h-auto w-full object-contain"
            src={imageUrl}
          />
        </div>
        {title && <h1 className="mt-4 text-xl font-bold text-ink-900">{title}</h1>}
        {description && <p className="mt-2 text-sm text-ink-600">{description}</p>}
        <dl className="mt-4 grid grid-cols-2 gap-x-4 gap-y-2 text-xs text-ink-500">
          <div>
            <dt className="font-medium text-ink-700">Type</dt>
            <dd>{imageType}</dd>
          </div>
          <div>
            <dt className="font-medium text-ink-700">Created by</dt>
            <dd>{owner}</dd>
          </div>
          {date && (
            <div className="col-span-2">
              <dt className="font-medium text-ink-700">Date</dt>
              <dd>{date}</dd>
            </div>
          )}
        </dl>
        <div className="mt-6 flex gap-3">
          <button
            className="flex-1 rounded-full border border-black/10 bg-ink-900 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-ink-700"
            onClick={() => void handleShare()}
            type="button"
          >
            Share this image
          </button>
          <a
            className="flex items-center justify-center rounded-full border border-black/10 bg-white/80 px-4 py-2.5 text-sm font-medium text-ink-700 shadow-sm transition hover:bg-white"
            href={shareUrl || "/public/image"}
          >
            Back
          </a>
        </div>
      </div>
    </div>
  );
}

export default function PublicImageSharePage() {
  return (
    <div className="space-y-8">
      <PageHeader
        description="Share this AI-generated image with the world."
        eyebrow="Image Share"
        title="Share AI Image"
      />
      <Suspense
        fallback={
          <div className="flex h-64 items-center justify-center">
            <Loader2 className="size-6 animate-spin text-ink-500" />
          </div>
        }
      >
        <ImageShareContent />
      </Suspense>
    </div>
  );
}
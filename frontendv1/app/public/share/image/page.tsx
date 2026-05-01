"use client";

import { Download, ImageIcon, Loader2 } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

import { ErrorState } from "@/components/ui/error-state";

function ShareImageContent() {
  const searchParams = useSearchParams();
  const imageUrl = searchParams.get("url");
  const title = searchParams.get("title") || "Shared image";

  if (!imageUrl) {
    return (
      <ErrorState
        detail="No image URL was provided."
        title="Image preview unavailable."
      />
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6" data-testid="share-image">
      <header className="space-y-2">
        <h1 className="text-2xl font-bold text-ink-900">{title}</h1>
        <div className="flex items-center gap-3">
          <a
            className="inline-flex items-center gap-2 rounded-full border border-black/10 bg-white/80 px-5 py-3 text-sm font-semibold text-ink-900 transition hover:bg-white"
            download
            href={imageUrl}
          >
            <Download className="size-4" />
            Download
          </a>
        </div>
      </header>

      <div className="overflow-hidden rounded-[28px] border border-black/10 bg-white/80 shadow-panel">
        {imageUrl.match(/\.(jpg|jpeg|png|gif|webp)$/i) ? (
          <img
            alt={title}
            className="w-full object-contain"
            src={imageUrl}
          />
        ) : (
          <div className="flex h-64 items-center justify-center">
            <ImageIcon className="size-12 text-ink-300" />
          </div>
        )}
      </div>
    </div>
  );
}

export default function ShareImagePage() {
  return (
    <Suspense
      fallback={(
        <div className="flex h-64 items-center justify-center">
          <Loader2 className="size-6 animate-spin text-ink-500" />
        </div>
      )}
    >
      <ShareImageContent />
    </Suspense>
  );
}

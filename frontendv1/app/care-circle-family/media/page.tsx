"use client";

import { useMemo, useRef } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertCircle, ImageIcon, Loader2, Trash2, UploadCloud } from "lucide-react";

import { useToasts } from "@/components/providers/app-providers";
import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";
import { PageHeader } from "@/components/shell/page-header";
import {
  deleteCareCircleMedia,
  fetchCareCircleMediaLibrary,
  uploadCareCircleMedia,
  type CareCircleMediaItem,
} from "@/lib/api";

function formatBytes(bytes: number) {
  if (!Number.isFinite(bytes) || bytes <= 0) {
    return "0 B";
  }

  const units = ["B", "KB", "MB", "GB"];
  const exponent = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const value = bytes / 1024 ** exponent;
  return `${value >= 10 || exponent === 0 ? value.toFixed(0) : value.toFixed(1)} ${units[exponent]}`;
}

function formatUploadDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "Uploaded recently";
  }
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function MediaCard({
  item,
  onDelete,
  isDeleting,
}: {
  item: CareCircleMediaItem;
  onDelete: () => void;
  isDeleting: boolean;
}) {
  const cropKeys = useMemo(
    () => Object.keys(item.aspect_ratio_urls ?? {}),
    [item.aspect_ratio_urls],
  );

  return (
    <article className="overflow-hidden rounded-[28px] border border-black/10 bg-white/80 shadow-panel">
      <div className="aspect-[4/3] bg-paper">
        {item.file_type === "image" ? (
          <img
            alt={item.alt_text || item.original_filename}
            className="h-full w-full object-cover"
            src={item.thumbnail_url || item.url}
          />
        ) : (
          <div className="flex h-full items-center justify-center text-ink-400">
            <ImageIcon className="size-10" />
          </div>
        )}
      </div>

      <div className="space-y-4 p-5">
        <div className="space-y-1">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <h2 className="truncate text-sm font-semibold text-ink-900">{item.original_filename}</h2>
              <p className="mt-1 text-xs text-ink-500">{formatUploadDate(item.created_at)}</p>
            </div>
            <button
              aria-label={`Delete ${item.original_filename}`}
              className="rounded-full border border-red-200 p-2 text-red-600 transition hover:bg-red-50 disabled:opacity-50"
              disabled={isDeleting}
              onClick={onDelete}
              type="button"
            >
              {isDeleting ? <Loader2 className="size-4 animate-spin" /> : <Trash2 className="size-4" />}
            </button>
          </div>

          {item.caption ? <p className="text-sm leading-6 text-ink-700">{item.caption}</p> : null}
        </div>

        <div className="flex flex-wrap gap-2 text-xs text-ink-600">
          <span className="rounded-full bg-black/[0.04] px-2.5 py-1">{formatBytes(item.file_size)}</span>
          {item.width && item.height ? (
            <span className="rounded-full bg-black/[0.04] px-2.5 py-1">{item.width} x {item.height}</span>
          ) : null}
          <span className="rounded-full bg-black/[0.04] px-2.5 py-1">{item.file_type}</span>
        </div>

        {cropKeys.length ? (
          <div className="rounded-2xl bg-paper px-4 py-3">
            <p className="text-xs uppercase tracking-[0.22em] text-ink-500">Prompt-ready crops</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {cropKeys.map((key) => (
                <span className="rounded-full bg-white px-2.5 py-1 text-xs font-medium text-ink-700" key={key}>
                  {key}
                </span>
              ))}
            </div>
          </div>
        ) : null}
      </div>
    </article>
  );
}

export default function FamilyMediaLibraryPage() {
  const queryClient = useQueryClient();
  const inputRef = useRef<HTMLInputElement | null>(null);
  const { pushToast } = useToasts();

  const mediaQuery = useQuery({
    queryKey: ["care-circle-family-media"],
    queryFn: fetchCareCircleMediaLibrary,
  });

  const uploadMutation = useMutation({
    mutationFn: async (files: File[]) => Promise.all(files.map((file) => uploadCareCircleMedia(file))),
    onSuccess: (_, files) => {
      void queryClient.invalidateQueries({ queryKey: ["care-circle-family-media"] });
      const count = files.length;
      pushToast({
        title: count === 1 ? "Photo uploaded" : "Photos uploaded",
        tone: "success",
        detail: count === 1 ? "The image is now available for family prompt workflows." : `${count} images are now available for family prompt workflows.`,
      });
      if (inputRef.current) {
        inputRef.current.value = "";
      }
    },
    onError: (error) => {
      pushToast({
        title: "Upload failed",
        tone: "error",
        detail: error instanceof Error ? error.message : "Try another image.",
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteCareCircleMedia,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["care-circle-family-media"] });
      pushToast({
        title: "Photo removed",
        tone: "success",
        detail: "The media item has been removed from the family library.",
      });
    },
    onError: (error) => {
      pushToast({
        title: "Delete failed",
        tone: "error",
        detail: error instanceof Error ? error.message : "Try again.",
      });
    },
  });

  const mediaItems = mediaQuery.data ?? [];

  return (
    <div className="space-y-8">
      <PageHeader
        description="Upload and arrange the photographs that power personalized friend memory prompts such as Memory Lane Photo and Dog Photo."
        eyebrow="Media Library"
        title="Family Uploads & Pictures"
      />

      <section className="rounded-[28px] border border-black/10 bg-white/75 p-6 shadow-panel">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="max-w-2xl">
            <p className="text-xs uppercase tracking-[0.24em] text-ink-500">Prompt supply</p>
            <h2 className="mt-2 text-xl font-semibold text-ink-900">Upload family photos for Care Circle prompts</h2>
            <p className="mt-2 text-sm leading-6 text-ink-600">
              Every upload is stored in the shared media library and made available to future family-facing prompt workflows. Image uploads also receive prompt-ready crops automatically.
            </p>
          </div>

          <div className="flex shrink-0 flex-wrap gap-3">
            <input
              accept="image/*"
              className="hidden"
              data-testid="care-circle-media-input"
              multiple
              onChange={(event) => {
                const files = Array.from(event.target.files ?? []);
                if (files.length) {
                  uploadMutation.mutate(files);
                }
              }}
              ref={inputRef}
              type="file"
            />
            <Button
              aria-label="Upload photos"
              className="gap-2"
              disabled={uploadMutation.isPending}
              onClick={() => inputRef.current?.click()}
            >
              {uploadMutation.isPending ? <Loader2 className="size-4 animate-spin" /> : <UploadCloud className="size-4" />}
              {uploadMutation.isPending ? "Uploading..." : "Upload photos"}
            </Button>
          </div>
        </div>
      </section>

      {mediaQuery.isLoading ? (
        <div className="flex h-32 items-center justify-center">
          <Loader2 className="size-6 animate-spin text-ink-500" />
        </div>
      ) : mediaQuery.isError ? (
        <ErrorState
          detail={mediaQuery.error instanceof Error ? mediaQuery.error.message : "Try refreshing the page."}
          onRetry={() => void mediaQuery.refetch()}
          retryLabel="Reload library"
          title="Media library unavailable"
        />
      ) : mediaItems.length === 0 ? (
        <section className="flex flex-col items-center justify-center rounded-[28px] border-2 border-dashed border-black/10 bg-white/50 p-16 text-center shadow-sm">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-paper text-ink-500 shadow-sm">
            <ImageIcon className="size-8" />
          </div>
          <h3 className="mt-4 text-base font-bold text-ink-900">No media uploaded yet</h3>
          <p className="mt-2 max-w-sm text-sm text-ink-500">
            Upload photographs here so Care Circle can reuse them in family memory prompts and personalized newsletter experiences.
          </p>
        </section>
      ) : (
        <section className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.24em] text-ink-500">Library contents</p>
              <p className="mt-1 text-sm text-ink-600">{mediaItems.length} item{mediaItems.length === 1 ? "" : "s"} ready for family workflows.</p>
            </div>
            <div className="flex items-center gap-2 rounded-full bg-paper px-3 py-2 text-xs text-ink-600">
              <AlertCircle className="size-4" />
              Images remain scoped to your authenticated account.
            </div>
          </div>

          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3" data-testid="care-circle-media-grid">
            {mediaItems.map((item) => (
              <MediaCard
                isDeleting={deleteMutation.isPending && deleteMutation.variables === item.storage_path}
                item={item}
                key={item.storage_path}
                onDelete={() => deleteMutation.mutate(item.storage_path)}
              />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

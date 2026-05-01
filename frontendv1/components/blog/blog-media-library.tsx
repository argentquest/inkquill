"use client";

import { useRef } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, ImageIcon, Loader2, Trash2, UploadCloud } from "lucide-react";
import Link from "next/link";

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

function MediaTile({ item, onDelete }: { item: CareCircleMediaItem; onDelete: () => void }) {
  const src = item.url ?? item.thumbnail_url;
  return (
    <div className="group relative rounded-2xl border border-black/10 bg-white/80 overflow-hidden shadow-sm" data-testid="media-tile">
      <div className="aspect-square bg-paper flex items-center justify-center">
        {src ? (
          <img alt={item.alt_text ?? item.original_filename} className="h-full w-full object-cover" src={src} />
        ) : (
          <ImageIcon className="size-8 text-ink-400" />
        )}
      </div>
      <div className="p-3">
        <p className="truncate text-xs font-medium text-ink-800">{item.original_filename}</p>
        <p className="mt-0.5 text-xs text-ink-400">{item.file_type}</p>
      </div>
      <button
        className="absolute right-2 top-2 rounded-full bg-white/80 p-1.5 text-ink-400 opacity-0 shadow-sm transition group-hover:opacity-100 hover:bg-red-50 hover:text-red-600"
        data-testid="delete-media-button"
        onClick={onDelete}
        type="button"
      >
        <Trash2 className="size-4" />
      </button>
    </div>
  );
}

interface BlogMediaLibraryProps {
  basePath: string;
}

export function BlogMediaLibrary({ basePath }: BlogMediaLibraryProps) {
  const queryClient = useQueryClient();
  const { pushToast } = useToasts();
  const fileRef = useRef<HTMLInputElement>(null);

  const { data: items = [], isLoading, isError, error, refetch } = useQuery({
    queryKey: ["blog-media"],
    queryFn: fetchCareCircleMediaLibrary,
  });

  const { mutate: doUpload, isPending: isUploading } = useMutation({
    mutationFn: (file: File) => uploadCareCircleMedia(file),
    onSuccess: () => {
      pushToast({ title: "File uploaded.", tone: "success" });
      void queryClient.invalidateQueries({ queryKey: ["blog-media"] });
    },
    onError: (err) => pushToast({ title: "Upload failed", detail: err instanceof Error ? err.message : "Try another file.", tone: "error" }),
  });

  const { mutate: doDelete } = useMutation({
    mutationFn: (storagePath: string) => deleteCareCircleMedia(storagePath),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["blog-media"] }),
    onError: () => pushToast({ title: "Delete failed", detail: "Try again.", tone: "error" }),
  });

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) doUpload(file);
    if (fileRef.current) fileRef.current.value = "";
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        <Link className="flex items-center gap-1.5 text-sm text-ink-500 hover:text-ink-900" href={basePath}>
          <ArrowLeft className="size-4" />
          Back to blog
        </Link>
      </div>

      <div className="flex items-start justify-between gap-4">
        <PageHeader
          description="Upload and manage images and files for your blog posts."
          eyebrow="Blog"
          title="Media Library"
        />
        <div className="mt-1 shrink-0">
          <input accept="image/*" className="sr-only" onChange={handleFileChange} ref={fileRef} type="file" />
          <Button
            className="gap-2"
            data-testid="upload-media-button"
            disabled={isUploading}
            onClick={() => fileRef.current?.click()}
            type="button"
          >
            {isUploading ? <Loader2 className="size-4 animate-spin" /> : <UploadCloud className="size-4" />}
            Upload
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex h-32 items-center justify-center">
          <Loader2 className="size-6 animate-spin text-ink-500" />
        </div>
      ) : isError ? (
        <ErrorState
          detail={error instanceof Error ? error.message : "Try refreshing."}
          onRetry={() => void refetch()}
          retryLabel="Reload library"
          title="Media library unavailable."
        />
      ) : items.length === 0 ? (
        <div
          className="flex flex-col items-center justify-center rounded-[28px] border-2 border-dashed border-black/10 bg-white/50 p-16 text-center shadow-sm"
          data-testid="media-empty-state"
        >
          <ImageIcon className="size-8 text-ink-400" />
          <p className="mt-3 text-sm font-medium text-ink-700">No media uploaded yet</p>
          <p className="mt-1 text-sm text-ink-500">Upload images to use in your blog posts.</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5" data-testid="media-grid">
          {items.map((item) => (
            <MediaTile
              item={item}
              key={item.id}
              onDelete={() => doDelete(item.storage_path)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

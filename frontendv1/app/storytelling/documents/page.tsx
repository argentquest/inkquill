"use client";

import { useRef, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Loader2, Trash2, UploadCloud, Download } from "lucide-react";

import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ErrorState } from "@/components/ui/error-state";
import { fetchDocuments, fetchUserWorlds, uploadDocument, deleteDocument } from "@/lib/api";

function statusBadgeClass(status: string) {
  switch (status.toUpperCase()) {
    case "PROCESSED":
      return "bg-green-100 text-green-800 border-green-200";
    case "PENDING":
      return "bg-amber-100 text-amber-800 border-amber-200";
    case "FAILED":
      return "bg-red-100 text-red-800 border-red-200";
    default:
      return "bg-ink-100 text-ink-700 border-ink-200";
  }
}

export default function DocumentsPage() {
  const queryClient = useQueryClient();
  const fileRef = useRef<HTMLInputElement>(null);
  const [selectedWorldId, setSelectedWorldId] = useState<string>("");

  const { data: documents, isLoading: docsLoading, error: docsError, refetch: refetchDocs } = useQuery({
    queryKey: ["documents"],
    queryFn: fetchDocuments,
  });

  const { data: worlds, isLoading: worldsLoading } = useQuery({
    queryKey: ["worlds"],
    queryFn: fetchUserWorlds,
  });

  const uploadMutation = useMutation({
    mutationFn: async ({ file, worldId }: { file: File; worldId: number }) => {
      return uploadDocument(file, worldId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      if (fileRef.current) fileRef.current.value = "";
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (documentId: number) => deleteDocument(documentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });

  function handleUpload(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const file = fileRef.current?.files?.[0];
    const worldId = Number(selectedWorldId);
    if (!file || !worldId) return;
    uploadMutation.mutate({ file, worldId });
  }

  if (docsLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Loader2 className="size-6 animate-spin text-ink-500" />
      </div>
    );
  }

  if (docsError) {
    return (
      <ErrorState
        detail={docsError instanceof Error ? docsError.message : "Try refreshing the page."}
        onRetry={() => void refetchDocs()}
        retryLabel="Reload documents"
        title="Documents could not be loaded."
      />
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Storytelling"
        title="Documents"
        description="Upload and manage reference documents for your worlds."
      />

      <section className="mx-auto max-w-3xl space-y-6 rounded-2xl border border-black/10 bg-white/70 p-6 shadow-panel">
        <h2 className="text-lg font-semibold text-ink-900">Upload document</h2>
        <form onSubmit={handleUpload} className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="world">World *</Label>
              <select
                id="world"
                className="flex h-10 w-full rounded-lg border border-black/10 bg-white px-3 py-2 text-sm outline-none transition focus:border-ink-500 focus:ring-1 focus:ring-ink-500"
                value={selectedWorldId}
                onChange={(e) => setSelectedWorldId(e.target.value)}
                required
              >
                <option value="" disabled>
                  {worldsLoading ? "Loading worlds..." : "Select a world"}
                </option>
                {worlds?.map((w) => (
                  <option key={w.id} value={w.id}>
                    {w.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="file">File *</Label>
              <Input
                id="file"
                name="file"
                type="file"
                ref={fileRef}
                accept=".pdf,.txt,.docx"
                required
              />
            </div>
          </div>

          {uploadMutation.isError && (
            <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {uploadMutation.error instanceof Error ? uploadMutation.error.message : "Upload failed."}
            </div>
          )}

          <div className="flex justify-end">
            <Button type="submit" disabled={uploadMutation.isPending || !selectedWorldId} className="gap-2">
              {uploadMutation.isPending && <Loader2 className="size-4 animate-spin" />}
              <UploadCloud className="size-4" />
              Upload
            </Button>
          </div>
        </form>
      </section>

      <section className="space-y-4">
        <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-ink-600">Your documents</h2>
        {!documents || documents.length === 0 ? (
          <p className="text-ink-500">No documents yet. Upload one above to get started.</p>
        ) : (
          <div className="grid gap-4">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="flex flex-col gap-3 rounded-2xl border border-black/10 bg-white/70 p-4 shadow-panel sm:flex-row sm:items-center sm:justify-between"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-ink-900">{doc.filename}</span>
                    <span className={`rounded-full border px-2 py-0.5 text-xs font-medium ${statusBadgeClass(doc.status)}`}>
                      {doc.status}
                    </span>
                  </div>
                  <p className="text-xs text-ink-500">
                    Uploaded {new Date(doc.uploaded_at).toLocaleString()}
                    {doc.error_message ? ` · Error: ${doc.error_message}` : ""}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Button asChild variant="outline" size="sm" className="gap-2">
                    <a href={`/api/v1/documents/download/${doc.id}`} download>
                      <Download className="size-4" />
                      Download
                    </a>
                  </Button>
                  <Button
                    variant="destructive"
                    size="sm"
                    className="gap-2"
                    onClick={() => {
                      if (confirm(`Delete "${doc.filename}"? This cannot be undone.`)) {
                        deleteMutation.mutate(doc.id);
                      }
                    }}
                    disabled={deleteMutation.isPending}
                  >
                    <Trash2 className="size-4" />
                    Delete
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

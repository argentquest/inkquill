"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, Loader2, MapPin } from "lucide-react";

import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";
import { fetchLocationHierarchy } from "@/lib/api";

export default function WorldHierarchyPage() {
  const params = useParams<{ worldId: string }>();
  const worldId = Number(params.worldId);

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["location-hierarchy", worldId],
    queryFn: () => fetchLocationHierarchy(worldId),
    enabled: !isNaN(worldId),
  });

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Loader2 className="size-6 animate-spin text-ink-500" />
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorState
        detail={error instanceof Error ? error.message : "Try refreshing."}
        onRetry={() => void refetch()}
        retryLabel="Reload hierarchy"
        title="Hierarchy could not be loaded."
      />
    );
  }

  const nodes = data ?? [];

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-3">
        <Button asChild variant="ghost" size="sm">
          <Link href={`/storytelling/worlds/${worldId}`}>
            <ArrowLeft className="mr-1 size-4" />
            World
          </Link>
        </Button>
      </div>

      <PageHeader eyebrow="World" title="Location Hierarchy" description="Parent-child relationships across your world." />

      {nodes.length === 0 ? (
        <p className="text-sm text-ink-500">No locations with parent relationships yet.</p>
      ) : (
        <div className="space-y-6">
          {nodes.map((node) => (
            <div key={node.parent.id ?? "root"} className="rounded-2xl border border-black/10 bg-white/70 p-5 shadow-panel">
              <div className="flex items-center gap-2">
                <MapPin className="size-4 text-ink-500" />
                <span className="font-semibold text-ink-900">
                  {node.parent.name}
                </span>
                {node.parent.scale && (
                  <span className="rounded-full bg-ink-100 px-2 py-0.5 text-xs font-medium text-ink-600">
                    {node.parent.scale}
                  </span>
                )}
              </div>
              {node.children.length > 0 && (
                <ul className="mt-3 space-y-2 border-l-2 border-black/10 pl-4">
                  {node.children.map((child) => (
                    <li key={child.id} className="flex items-center gap-2 text-sm text-ink-700">
                      <span className="h-1.5 w-1.5 rounded-full bg-ink-400" />
                      {child.name}
                      {child.scale && (
                        <span className="rounded-full bg-ink-100 px-2 py-0.5 text-xs font-medium text-ink-600">
                          {child.scale}
                        </span>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

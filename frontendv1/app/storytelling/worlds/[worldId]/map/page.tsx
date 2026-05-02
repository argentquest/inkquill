"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, Loader2, MapPin } from "lucide-react";

import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";
import { fetchLocationsForWorld } from "@/lib/api";

export default function WorldMapPage() {
  const params = useParams<{ worldId: string }>();
  const worldId = Number(params.worldId);

  const { data: locations, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["locations", worldId],
    queryFn: () => fetchLocationsForWorld(worldId),
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
        retryLabel="Reload map"
        title="Map could not be loaded."
      />
    );
  }

  const pinned = (locations ?? []).filter((l) => l.map_x != null && l.map_y != null);

  const xs = pinned.map((l) => l.map_x ?? 0);
  const ys = pinned.map((l) => l.map_y ?? 0);
  const minX = xs.length ? Math.min(...xs) : 0;
  const maxX = xs.length ? Math.max(...xs) : 100;
  const minY = ys.length ? Math.min(...ys) : 0;
  const maxY = ys.length ? Math.max(...ys) : 100;
  const rangeX = maxX - minX || 1;
  const rangeY = maxY - minY || 1;

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

      <PageHeader eyebrow="World" title="Map" description="Visual layout of your locations." />

      {pinned.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-black/15 bg-white/60 p-12 text-center">
          <MapPin className="mx-auto size-8 text-ink-400" />
          <p className="mt-3 text-sm text-ink-500">No locations have map coordinates yet.</p>
          <p className="text-xs text-ink-400">Set map_x and map_y on locations to see them here.</p>
        </div>
      ) : (
        <div className="relative h-[28rem] overflow-hidden rounded-2xl border border-black/10 bg-[#f0ece4] shadow-panel">
          {pinned.map((loc) => {
            const left = ((loc.map_x! - minX) / rangeX) * 90 + 5;
            const top = ((loc.map_y! - minY) / rangeY) * 90 + 5;
            return (
              <div
                key={loc.id}
                className="absolute -translate-x-1/2 -translate-y-1/2"
                style={{ left: `${left}%`, top: `${top}%` }}
              >
                <div className="flex flex-col items-center gap-1">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full border border-black/10 bg-white shadow-sm">
                    <MapPin className="size-4 text-ink-700" />
                  </div>
                  <span className="rounded-md bg-white/90 px-2 py-0.5 text-xs font-medium text-ink-800 shadow-sm">
                    {loc.name}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

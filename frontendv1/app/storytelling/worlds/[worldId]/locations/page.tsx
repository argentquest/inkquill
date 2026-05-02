"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Loader2, PlusCircle, MapPin, Trash2, Pencil } from "lucide-react";

import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";
import {
  fetchLocationsForWorld,
  deleteLocation,
  type LocationEntry,
} from "@/lib/api";

function LocationCard({ location }: { location: LocationEntry }) {
  const router = useRouter();
  const queryClient = useQueryClient();

  const deleteMutation = useMutation({
    mutationFn: () => deleteLocation(location.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["locations", location.world_id] });
    },
  });

  return (
    <article className="rounded-[20px] border border-black/10 bg-white/80 p-5 shadow-panel">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <Link href={`/storytelling/locations/${location.id}`}>
            <h2 className="truncate text-sm font-semibold text-ink-900 hover:underline">{location.name}</h2>
          </Link>
          <div className="mt-1 flex flex-wrap gap-2">
            {location.scale ? (
              <span className="rounded-full bg-paper px-2 py-0.5 text-xs text-ink-500">{location.scale}</span>
            ) : null}
            {location.importance_rating ? (
              <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700">
                Rating {location.importance_rating}
              </span>
            ) : null}
          </div>
          {location.description ? (
            <p className="mt-2 line-clamp-2 text-xs leading-5 text-ink-500">{location.description}</p>
          ) : null}
        </div>
      </div>
      <div className="mt-4 flex items-center gap-2">
        <Button asChild variant="ghost" size="sm">
          <Link href={`/storytelling/locations/${location.id}`}>
            <Pencil className="mr-1 size-3.5" />
            Edit
          </Link>
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className="text-red-600 hover:text-red-700"
          onClick={() => {
            if (confirm(`Delete location "${location.name}"? This cannot be undone.`)) {
              deleteMutation.mutate();
            }
          }}
          disabled={deleteMutation.isPending}
        >
          <Trash2 className="mr-1 size-3.5" />
          Delete
        </Button>
      </div>
    </article>
  );
}

export default function LocationsListPage() {
  const params = useParams<{ worldId: string }>();
  const worldId = Number(params.worldId);

  const { data: locations, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["locations", worldId],
    queryFn: () => fetchLocationsForWorld(worldId),
    enabled: !isNaN(worldId),
  });

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

      <PageHeader
        description="The places and spaces that make up this world."
        eyebrow="Locations"
        title="Locations"
        action={
          <Button asChild className="gap-2">
            <Link href={`/storytelling/worlds/${worldId}/locations/new`}>
              <PlusCircle className="size-4" />
              New location
            </Link>
          </Button>
        }
      />

      {isLoading ? (
        <div className="flex h-32 items-center justify-center">
          <Loader2 className="size-6 animate-spin text-ink-500" />
        </div>
      ) : isError ? (
        <ErrorState
          detail={error instanceof Error ? error.message : "Try refreshing the page."}
          onRetry={() => void refetch()}
          retryLabel="Reload locations"
          title="Locations could not be loaded."
        />
      ) : !locations?.length ? (
        <section className="flex flex-col items-center justify-center rounded-[28px] border-2 border-dashed border-black/10 bg-white/50 p-16 text-center shadow-sm">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-paper text-ink-500 shadow-sm">
            <MapPin className="size-8" />
          </div>
          <h3 className="mt-4 text-base font-bold text-ink-900">No locations yet</h3>
          <p className="mt-2 max-w-sm text-sm text-ink-500">
            Add your first location to start mapping this world.
          </p>
          <Button asChild className="mt-6 gap-2">
            <Link href={`/storytelling/worlds/${worldId}/locations/new`}>
              <PlusCircle className="size-4" />
              Create a location
            </Link>
          </Button>
        </section>
      ) : (
        <section className="space-y-4">
          <p className="text-sm text-ink-600">
            {locations.length} {locations.length === 1 ? "location" : "locations"}
          </p>
          <div className="grid gap-4 md:grid-cols-2">
            {locations.map((l) => (
              <LocationCard key={l.id} location={l} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

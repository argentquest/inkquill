"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Loader2, Save, Trash2 } from "lucide-react";

import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { ErrorState } from "@/components/ui/error-state";
import { fetchLocation, updateLocation, deleteLocation, type LocationCreatePayload, type LocationScale } from "@/lib/api";

const SCALES: LocationScale[] = ["REGION", "CITY", "BUILDING", "ROOM", "AREA", "OBJECT", "POINT", "OTHER"];

export default function LocationDetailPage() {
  const params = useParams<{ locationId: string }>();
  const locationId = Number(params.locationId);
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: location, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["location", locationId],
    queryFn: () => fetchLocation(locationId),
    enabled: !isNaN(locationId),
  });

  const updateMutation = useMutation({
    mutationFn: (payload: Partial<LocationCreatePayload>) => updateLocation(locationId, payload),
    onSuccess: (data) => {
      queryClient.setQueryData(["location", locationId], data);
      queryClient.invalidateQueries({ queryKey: ["locations", data.world_id] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteLocation(locationId),
    onSuccess: () => {
      if (location) {
        router.push(`/storytelling/worlds/${location.world_id}/locations`);
      }
    },
  });

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const scale = fd.get("scale") as LocationScale | "";
    const payload: Partial<LocationCreatePayload> = {
      name: String(fd.get("name")),
      description: String(fd.get("description") || ""),
      atmosphere: String(fd.get("atmosphere") || ""),
      significance: String(fd.get("significance") || ""),
      geography: String(fd.get("geography") || ""),
      cultural_context: String(fd.get("cultural_context") || ""),
      importance_rating: fd.get("importance_rating") ? Number(fd.get("importance_rating")) : undefined,
      connected_elements: String(fd.get("connected_elements") || ""),
      scale: scale || undefined,
    };
    updateMutation.mutate(payload);
  }

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Loader2 className="size-6 animate-spin text-ink-500" />
      </div>
    );
  }

  if (isError || !location) {
    return (
      <ErrorState
        detail={error instanceof Error ? error.message : "Try refreshing the page."}
        onRetry={() => void refetch()}
        retryLabel="Reload location"
        title="Location could not be loaded."
      />
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-3">
        <Button asChild variant="ghost" size="sm">
          <Link href={`/storytelling/worlds/${location.world_id}/locations`}>
            <ArrowLeft className="mr-1 size-4" />
            Locations
          </Link>
        </Button>
      </div>

      <PageHeader
        description={location.description || "Location details"}
        eyebrow="Location"
        title={location.name}
        action={
          <Button
            variant="destructive"
            size="sm"
            className="gap-2"
            onClick={() => {
              if (confirm(`Delete location "${location.name}"? This cannot be undone.`)) {
                deleteMutation.mutate();
              }
            }}
            disabled={deleteMutation.isPending}
          >
            <Trash2 className="size-4" />
            Delete
          </Button>
        }
      />

      <form onSubmit={handleSubmit} className="mx-auto max-w-2xl space-y-6">
        {(updateMutation.isError || deleteMutation.isError) && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {(updateMutation.error ?? deleteMutation.error) instanceof Error
              ? ((updateMutation.error ?? deleteMutation.error) as Error).message
              : "An error occurred."}
          </div>
        )}

        <div className="space-y-2">
          <Label htmlFor="name">Name *</Label>
          <Input id="name" name="name" required defaultValue={location.name} />
        </div>

        <div className="space-y-2">
          <Label htmlFor="scale">Scale</Label>
          <select
            id="scale"
            name="scale"
            defaultValue={location.scale ?? ""}
            className="flex h-10 w-full rounded-md border border-black/10 bg-white px-3 py-2 text-sm outline-none focus:border-black/30 focus:ring-1 focus:ring-black/20"
          >
            <option value="">Select scale...</option>
            {SCALES.map((s) => (
              <option key={s} value={s}>
                {s.replace("_", " ").toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase())}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="description">Description</Label>
          <Textarea id="description" name="description" rows={4} defaultValue={location.description ?? ""} placeholder="General description of the location..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="atmosphere">Atmosphere</Label>
          <Input id="atmosphere" name="atmosphere" defaultValue={location.atmosphere ?? ""} placeholder="Eerie, peaceful, bustling..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="significance">Significance</Label>
          <Textarea id="significance" name="significance" rows={3} defaultValue={location.significance ?? ""} placeholder="Why this location matters..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="geography">Geography</Label>
          <Textarea id="geography" name="geography" rows={3} defaultValue={location.geography ?? ""} placeholder="Terrain, climate, natural features..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="cultural_context">Cultural Context</Label>
          <Textarea id="cultural_context" name="cultural_context" rows={3} defaultValue={location.cultural_context ?? ""} placeholder="Social, political, or cultural aspects..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="connected_elements">Connected Elements</Label>
          <Textarea id="connected_elements" name="connected_elements" rows={3} defaultValue={location.connected_elements ?? ""} placeholder="Characters, locations, or lore items associated..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="importance_rating">Importance Rating (1-5)</Label>
          <Input id="importance_rating" name="importance_rating" type="number" min={1} max={5} defaultValue={location.importance_rating ?? ""} placeholder="5 = central location" />
        </div>

        <div className="flex items-center justify-end gap-3 pt-2">
          <Button asChild variant="outline">
            <Link href={`/storytelling/worlds/${location.world_id}/locations`}>Cancel</Link>
          </Button>
          <Button type="submit" disabled={updateMutation.isPending} className="gap-2">
            {updateMutation.isPending && <Loader2 className="size-4 animate-spin" />}
            <Save className="size-4" />
            Save changes
          </Button>
        </div>
      </form>
    </div>
  );
}

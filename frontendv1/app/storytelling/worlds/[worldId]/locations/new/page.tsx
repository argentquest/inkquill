"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { ArrowLeft, Loader2, Save } from "lucide-react";

import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { ErrorState } from "@/components/ui/error-state";
import { createLocationForWorld, type LocationCreatePayload, type LocationScale } from "@/lib/api";

const SCALES: LocationScale[] = ["REGION", "CITY", "BUILDING", "ROOM", "AREA", "OBJECT", "POINT", "OTHER"];

export default function NewLocationPage() {
  const params = useParams<{ worldId: string }>();
  const worldId = Number(params.worldId);
  const router = useRouter();

  const mutation = useMutation({
    mutationFn: (payload: LocationCreatePayload) => createLocationForWorld(worldId, payload),
    onSuccess: (data) => {
      router.push(`/storytelling/locations/${data.id}`);
    },
  });

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const scale = fd.get("scale") as LocationScale | "";
    const payload: LocationCreatePayload = {
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
    mutation.mutate(payload);
  }

  if (isNaN(worldId)) {
    return (
      <ErrorState
        detail="The world ID in the URL is not valid."
        title="Invalid world"
      />
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-3">
        <Button asChild variant="ghost" size="sm">
          <Link href={`/storytelling/worlds/${worldId}/locations`}>
            <ArrowLeft className="mr-1 size-4" />
            Locations
          </Link>
        </Button>
      </div>

      <PageHeader description="Add a new location to this world." eyebrow="New" title="Create Location" />

      <form onSubmit={handleSubmit} className="mx-auto max-w-2xl space-y-6">
        {mutation.isError && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {mutation.error instanceof Error ? mutation.error.message : "Failed to create location."}
          </div>
        )}

        <div className="space-y-2">
          <Label htmlFor="name">Name *</Label>
          <Input id="name" name="name" required placeholder="Location name" />
        </div>

        <div className="space-y-2">
          <Label htmlFor="scale">Scale</Label>
          <select
            id="scale"
            name="scale"
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
          <Textarea id="description" name="description" rows={4} placeholder="General description of the location..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="atmosphere">Atmosphere</Label>
          <Input id="atmosphere" name="atmosphere" placeholder="Eerie, peaceful, bustling..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="significance">Significance</Label>
          <Textarea id="significance" name="significance" rows={3} placeholder="Why this location matters..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="geography">Geography</Label>
          <Textarea id="geography" name="geography" rows={3} placeholder="Terrain, climate, natural features..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="cultural_context">Cultural Context</Label>
          <Textarea id="cultural_context" name="cultural_context" rows={3} placeholder="Social, political, or cultural aspects..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="connected_elements">Connected Elements</Label>
          <Textarea id="connected_elements" name="connected_elements" rows={3} placeholder="Characters, locations, or lore items associated..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="importance_rating">Importance Rating (1-5)</Label>
          <Input id="importance_rating" name="importance_rating" type="number" min={1} max={5} placeholder="5 = central location" />
        </div>

        <div className="flex items-center justify-end gap-3 pt-2">
          <Button asChild variant="outline">
            <Link href={`/storytelling/worlds/${worldId}/locations`}>Cancel</Link>
          </Button>
          <Button type="submit" disabled={mutation.isPending} className="gap-2">
            {mutation.isPending && <Loader2 className="size-4 animate-spin" />}
            <Save className="size-4" />
            Create location
          </Button>
        </div>
      </form>
    </div>
  );
}

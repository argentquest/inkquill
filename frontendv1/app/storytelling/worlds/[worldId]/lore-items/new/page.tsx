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
import { createLoreItemForWorld, type LoreItemCreatePayload, type LoreItemCategory } from "@/lib/api";

const CATEGORIES: LoreItemCategory[] = [
  "MAGIC_SYSTEM",
  "HISTORICAL_EVENT",
  "ARTIFACT",
  "DEITY",
  "CREATURE",
  "FACTION_ORGANIZATION",
  "CULTURE_CUSTOM",
  "TECHNOLOGY",
  "PHILOSOPHY_BELIEF",
  "OTHER_LORE",
];

const CATEGORY_LABELS: Record<LoreItemCategory, string> = {
  MAGIC_SYSTEM: "Magic System",
  HISTORICAL_EVENT: "Historical Event",
  ARTIFACT: "Artifact",
  DEITY: "Deity",
  CREATURE: "Creature",
  FACTION_ORGANIZATION: "Faction / Organization",
  CULTURE_CUSTOM: "Culture / Custom",
  TECHNOLOGY: "Technology",
  PHILOSOPHY_BELIEF: "Philosophy / Belief",
  OTHER_LORE: "Other",
};

export default function NewLoreItemPage() {
  const params = useParams<{ worldId: string }>();
  const worldId = Number(params.worldId);
  const router = useRouter();

  const mutation = useMutation({
    mutationFn: (payload: LoreItemCreatePayload) => createLoreItemForWorld(worldId, payload),
    onSuccess: (data) => {
      router.push(`/storytelling/lore-items/${data.id}`);
    },
  });

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const payload: LoreItemCreatePayload = {
      title: String(fd.get("title")),
      category: String(fd.get("category")) as LoreItemCategory,
      description: String(fd.get("description") || ""),
      importance_rating: fd.get("importance_rating") ? Number(fd.get("importance_rating")) : undefined,
      related_elements: String(fd.get("related_elements") || ""),
      placement_note: String(fd.get("placement_note") || ""),
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
          <Link href={`/storytelling/worlds/${worldId}/lore-items`}>
            <ArrowLeft className="mr-1 size-4" />
            Lore items
          </Link>
        </Button>
      </div>

      <PageHeader description="Add a new piece of lore to this world." eyebrow="New" title="Create Lore Item" />

      <form onSubmit={handleSubmit} className="mx-auto max-w-2xl space-y-6">
        {mutation.isError && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {mutation.error instanceof Error ? mutation.error.message : "Failed to create lore item."}
          </div>
        )}

        <div className="space-y-2">
          <Label htmlFor="title">Title *</Label>
          <Input id="title" name="title" required placeholder="Lore item title" />
        </div>

        <div className="space-y-2">
          <Label htmlFor="category">Category *</Label>
          <select
            id="category"
            name="category"
            required
            className="flex h-10 w-full rounded-md border border-black/10 bg-white px-3 py-2 text-sm outline-none focus:border-black/30 focus:ring-1 focus:ring-black/20"
          >
            <option value="">Select category...</option>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {CATEGORY_LABELS[c]}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="description">Description</Label>
          <Textarea id="description" name="description" rows={4} placeholder="Detailed description of this lore item..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="related_elements">Related Elements</Label>
          <Textarea id="related_elements" name="related_elements" rows={3} placeholder="Characters, locations, or other lore items this connects to..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="placement_note">Placement Note</Label>
          <Input id="placement_note" name="placement_note" placeholder="Where or how this lore item is found in the world..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="importance_rating">Importance Rating (1-5)</Label>
          <Input id="importance_rating" name="importance_rating" type="number" min={1} max={5} placeholder="5 = central concept" />
        </div>

        <div className="flex items-center justify-end gap-3 pt-2">
          <Button asChild variant="outline">
            <Link href={`/storytelling/worlds/${worldId}/lore-items`}>Cancel</Link>
          </Button>
          <Button type="submit" disabled={mutation.isPending} className="gap-2">
            {mutation.isPending && <Loader2 className="size-4 animate-spin" />}
            <Save className="size-4" />
            Create lore item
          </Button>
        </div>
      </form>
    </div>
  );
}

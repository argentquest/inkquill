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
import { fetchLoreItem, updateLoreItem, deleteLoreItem, type LoreItemCreatePayload, type LoreItemCategory } from "@/lib/api";

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

export default function LoreItemDetailPage() {
  const params = useParams<{ loreItemId: string }>();
  const loreItemId = Number(params.loreItemId);
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: item, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["lore-item", loreItemId],
    queryFn: () => fetchLoreItem(loreItemId),
    enabled: !isNaN(loreItemId),
  });

  const updateMutation = useMutation({
    mutationFn: (payload: Partial<LoreItemCreatePayload>) => updateLoreItem(loreItemId, payload),
    onSuccess: (data) => {
      queryClient.setQueryData(["lore-item", loreItemId], data);
      queryClient.invalidateQueries({ queryKey: ["lore-items", data.world_id] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteLoreItem(loreItemId),
    onSuccess: () => {
      if (item) {
        router.push(`/storytelling/worlds/${item.world_id}/lore-items`);
      }
    },
  });

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const payload: Partial<LoreItemCreatePayload> = {
      title: String(fd.get("title")),
      category: String(fd.get("category")) as LoreItemCategory,
      description: String(fd.get("description") || ""),
      importance_rating: fd.get("importance_rating") ? Number(fd.get("importance_rating")) : undefined,
      related_elements: String(fd.get("related_elements") || ""),
      placement_note: String(fd.get("placement_note") || ""),
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

  if (isError || !item) {
    return (
      <ErrorState
        detail={error instanceof Error ? error.message : "Try refreshing the page."}
        onRetry={() => void refetch()}
        retryLabel="Reload lore item"
        title="Lore item could not be loaded."
      />
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-3">
        <Button asChild variant="ghost" size="sm">
          <Link href={`/storytelling/worlds/${item.world_id}/lore-items`}>
            <ArrowLeft className="mr-1 size-4" />
            Lore items
          </Link>
        </Button>
      </div>

      <PageHeader
        description={item.description || "Lore item details"}
        eyebrow={CATEGORY_LABELS[item.category] ?? item.category}
        title={item.title}
        action={
          <Button
            variant="destructive"
            size="sm"
            className="gap-2"
            onClick={() => {
              if (confirm(`Delete lore item "${item.title}"? This cannot be undone.`)) {
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
          <Label htmlFor="title">Title *</Label>
          <Input id="title" name="title" required defaultValue={item.title} />
        </div>

        <div className="space-y-2">
          <Label htmlFor="category">Category *</Label>
          <select
            id="category"
            name="category"
            required
            defaultValue={item.category}
            className="flex h-10 w-full rounded-md border border-black/10 bg-white px-3 py-2 text-sm outline-none focus:border-black/30 focus:ring-1 focus:ring-black/20"
          >
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {CATEGORY_LABELS[c]}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="description">Description</Label>
          <Textarea id="description" name="description" rows={4} defaultValue={item.description ?? ""} placeholder="Detailed description of this lore item..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="related_elements">Related Elements</Label>
          <Textarea id="related_elements" name="related_elements" rows={3} defaultValue={item.related_elements ?? ""} placeholder="Characters, locations, or other lore items this connects to..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="placement_note">Placement Note</Label>
          <Input id="placement_note" name="placement_note" defaultValue={item.placement_note ?? ""} placeholder="Where or how this lore item is found in the world..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="importance_rating">Importance Rating (1-5)</Label>
          <Input id="importance_rating" name="importance_rating" type="number" min={1} max={5} defaultValue={item.importance_rating ?? ""} placeholder="5 = central concept" />
        </div>

        <div className="flex items-center justify-end gap-3 pt-2">
          <Button asChild variant="outline">
            <Link href={`/storytelling/worlds/${item.world_id}/lore-items`}>Cancel</Link>
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

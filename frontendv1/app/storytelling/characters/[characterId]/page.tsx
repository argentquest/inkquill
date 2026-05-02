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
import { fetchCharacter, updateCharacter, deleteCharacter, type CharacterCreatePayload } from "@/lib/api";

export default function CharacterDetailPage() {
  const params = useParams<{ characterId: string }>();
  const characterId = Number(params.characterId);
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: character, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["character", characterId],
    queryFn: () => fetchCharacter(characterId),
    enabled: !isNaN(characterId),
  });

  const updateMutation = useMutation({
    mutationFn: (payload: Partial<CharacterCreatePayload>) => updateCharacter(characterId, payload),
    onSuccess: (data) => {
      queryClient.setQueryData(["character", characterId], data);
      queryClient.invalidateQueries({ queryKey: ["characters", data.world_id] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteCharacter(characterId),
    onSuccess: () => {
      if (character) {
        router.push(`/storytelling/worlds/${character.world_id}/characters`);
      }
    },
  });

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const payload: Partial<CharacterCreatePayload> = {
      name: String(fd.get("name")),
      species: String(fd.get("species") || ""),
      gender: String(fd.get("gender") || ""),
      description: String(fd.get("description") || ""),
      personality_traits: String(fd.get("personality_traits") || ""),
      backstory: String(fd.get("backstory") || ""),
      importance_rating: fd.get("importance_rating") ? Number(fd.get("importance_rating")) : undefined,
      relationships: String(fd.get("relationships") || ""),
      profession: String(fd.get("profession") || ""),
      age_category: String(fd.get("age_category") || ""),
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

  if (isError || !character) {
    return (
      <ErrorState
        detail={error instanceof Error ? error.message : "Try refreshing the page."}
        onRetry={() => void refetch()}
        retryLabel="Reload character"
        title="Character could not be loaded."
      />
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-3">
        <Button asChild variant="ghost" size="sm">
          <Link href={`/storytelling/worlds/${character.world_id}/characters`}>
            <ArrowLeft className="mr-1 size-4" />
            Characters
          </Link>
        </Button>
      </div>

      <PageHeader
        description={character.description || "Character details"}
        eyebrow="Character"
        title={character.name}
        action={
          <Button
            variant="destructive"
            size="sm"
            className="gap-2"
            onClick={() => {
              if (confirm(`Delete character "${character.name}"? This cannot be undone.`)) {
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
          <Input id="name" name="name" required defaultValue={character.name} />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="species">Species</Label>
            <Input id="species" name="species" defaultValue={character.species ?? ""} placeholder="Human, Elf, Dragon..." />
          </div>
          <div className="space-y-2">
            <Label htmlFor="gender">Gender</Label>
            <Input id="gender" name="gender" defaultValue={character.gender ?? ""} placeholder="Male, Female, Non-binary..." />
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="profession">Profession</Label>
            <Input id="profession" name="profession" defaultValue={character.profession ?? ""} placeholder="Knight, Merchant, Wizard..." />
          </div>
          <div className="space-y-2">
            <Label htmlFor="age_category">Age Category</Label>
            <Input id="age_category" name="age_category" defaultValue={character.age_category ?? ""} placeholder="Young Adult, Elder..." />
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="description">Description</Label>
          <Textarea id="description" name="description" rows={4} defaultValue={character.description ?? ""} placeholder="General appearance and overview..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="personality_traits">Personality Traits</Label>
          <Textarea id="personality_traits" name="personality_traits" rows={3} defaultValue={character.personality_traits ?? ""} placeholder="Comma-separated or free text..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="backstory">Backstory</Label>
          <Textarea id="backstory" name="backstory" rows={4} defaultValue={character.backstory ?? ""} placeholder="Character history and origins..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="relationships">Relationships</Label>
          <Textarea id="relationships" name="relationships" rows={3} defaultValue={character.relationships ?? ""} placeholder="Key relationships with other characters..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="importance_rating">Importance Rating (1-5)</Label>
          <Input id="importance_rating" name="importance_rating" type="number" min={1} max={5} defaultValue={character.importance_rating ?? ""} placeholder="5 = main protagonist" />
        </div>

        <div className="flex items-center justify-end gap-3 pt-2">
          <Button asChild variant="outline">
            <Link href={`/storytelling/worlds/${character.world_id}/characters`}>Cancel</Link>
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

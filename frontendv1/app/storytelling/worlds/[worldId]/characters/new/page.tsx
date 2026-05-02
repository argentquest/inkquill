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
import { createCharacterForWorld, type CharacterCreatePayload } from "@/lib/api";

export default function NewCharacterPage() {
  const params = useParams<{ worldId: string }>();
  const worldId = Number(params.worldId);
  const router = useRouter();

  const mutation = useMutation({
    mutationFn: (payload: CharacterCreatePayload) => createCharacterForWorld(worldId, payload),
    onSuccess: (data) => {
      router.push(`/storytelling/characters/${data.id}`);
    },
  });

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const payload: CharacterCreatePayload = {
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
          <Link href={`/storytelling/worlds/${worldId}/characters`}>
            <ArrowLeft className="mr-1 size-4" />
            Characters
          </Link>
        </Button>
      </div>

      <PageHeader description="Add a new character to this world." eyebrow="New" title="Create Character" />

      <form onSubmit={handleSubmit} className="mx-auto max-w-2xl space-y-6">
        {mutation.isError && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {mutation.error instanceof Error ? mutation.error.message : "Failed to create character."}
          </div>
        )}

        <div className="space-y-2">
          <Label htmlFor="name">Name *</Label>
          <Input id="name" name="name" required placeholder="Character name" />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="species">Species</Label>
            <Input id="species" name="species" placeholder="Human, Elf, Dragon..." />
          </div>
          <div className="space-y-2">
            <Label htmlFor="gender">Gender</Label>
            <Input id="gender" name="gender" placeholder="Male, Female, Non-binary..." />
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="profession">Profession</Label>
            <Input id="profession" name="profession" placeholder="Knight, Merchant, Wizard..." />
          </div>
          <div className="space-y-2">
            <Label htmlFor="age_category">Age Category</Label>
            <Input id="age_category" name="age_category" placeholder="Young Adult, Elder..." />
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="description">Description</Label>
          <Textarea id="description" name="description" rows={4} placeholder="General appearance and overview..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="personality_traits">Personality Traits</Label>
          <Textarea id="personality_traits" name="personality_traits" rows={3} placeholder="Comma-separated or free text..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="backstory">Backstory</Label>
          <Textarea id="backstory" name="backstory" rows={4} placeholder="Character history and origins..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="relationships">Relationships</Label>
          <Textarea id="relationships" name="relationships" rows={3} placeholder="Key relationships with other characters..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="importance_rating">Importance Rating (1-5)</Label>
          <Input id="importance_rating" name="importance_rating" type="number" min={1} max={5} placeholder="5 = main protagonist" />
        </div>

        <div className="flex items-center justify-end gap-3 pt-2">
          <Button asChild variant="outline">
            <Link href={`/storytelling/worlds/${worldId}/characters`}>Cancel</Link>
          </Button>
          <Button type="submit" disabled={mutation.isPending} className="gap-2">
            {mutation.isPending && <Loader2 className="size-4 animate-spin" />}
            <Save className="size-4" />
            Create character
          </Button>
        </div>
      </form>
    </div>
  );
}

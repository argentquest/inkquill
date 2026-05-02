"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Loader2, PlusCircle, Users, Trash2, Pencil } from "lucide-react";

import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";
import {
  fetchCharactersForWorld,
  deleteCharacter,
  type CharacterEntry,
} from "@/lib/api";

function CharacterCard({ character }: { character: CharacterEntry }) {
  const router = useRouter();
  const queryClient = useQueryClient();

  const deleteMutation = useMutation({
    mutationFn: () => deleteCharacter(character.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["characters", character.world_id] });
    },
  });

  return (
    <article className="rounded-[20px] border border-black/10 bg-white/80 p-5 shadow-panel">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <Link href={`/storytelling/characters/${character.id}`}>
            <h2 className="truncate text-sm font-semibold text-ink-900 hover:underline">{character.name}</h2>
          </Link>
          <div className="mt-1 flex flex-wrap gap-2">
            {character.species ? (
              <span className="rounded-full bg-paper px-2 py-0.5 text-xs text-ink-500">{character.species}</span>
            ) : null}
            {character.gender ? (
              <span className="rounded-full bg-paper px-2 py-0.5 text-xs text-ink-500">{character.gender}</span>
            ) : null}
            {character.importance_rating ? (
              <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700">
                Rating {character.importance_rating}
              </span>
            ) : null}
          </div>
          {character.description ? (
            <p className="mt-2 line-clamp-2 text-xs leading-5 text-ink-500">{character.description}</p>
          ) : null}
        </div>
      </div>
      <div className="mt-4 flex items-center gap-2">
        <Button asChild variant="ghost" size="sm">
          <Link href={`/storytelling/characters/${character.id}`}>
            <Pencil className="mr-1 size-3.5" />
            Edit
          </Link>
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className="text-red-600 hover:text-red-700"
          onClick={() => {
            if (confirm(`Delete character "${character.name}"? This cannot be undone.`)) {
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

export default function CharactersListPage() {
  const params = useParams<{ worldId: string }>();
  const worldId = Number(params.worldId);

  const { data: characters, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["characters", worldId],
    queryFn: () => fetchCharactersForWorld(worldId),
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
        description="The people and creatures who inhabit this world."
        eyebrow="Characters"
        title="Characters"
        action={
          <Button asChild className="gap-2">
            <Link href={`/storytelling/worlds/${worldId}/characters/new`}>
              <PlusCircle className="size-4" />
              New character
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
          retryLabel="Reload characters"
          title="Characters could not be loaded."
        />
      ) : !characters?.length ? (
        <section className="flex flex-col items-center justify-center rounded-[28px] border-2 border-dashed border-black/10 bg-white/50 p-16 text-center shadow-sm">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-paper text-ink-500 shadow-sm">
            <Users className="size-8" />
          </div>
          <h3 className="mt-4 text-base font-bold text-ink-900">No characters yet</h3>
          <p className="mt-2 max-w-sm text-sm text-ink-500">
            Add your first character to start populating this world.
          </p>
          <Button asChild className="mt-6 gap-2">
            <Link href={`/storytelling/worlds/${worldId}/characters/new`}>
              <PlusCircle className="size-4" />
              Create a character
            </Link>
          </Button>
        </section>
      ) : (
        <section className="space-y-4">
          <p className="text-sm text-ink-600">
            {characters.length} {characters.length === 1 ? "character" : "characters"}
          </p>
          <div className="grid gap-4 md:grid-cols-2">
            {characters.map((c) => (
              <CharacterCard key={c.id} character={c} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

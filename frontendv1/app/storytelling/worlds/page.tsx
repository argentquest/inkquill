"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Globe, Loader2, PlusCircle } from "lucide-react";

import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";
import { fetchUserWorlds, type WorldEntry } from "@/lib/api";

function WorldCard({ world }: { world: WorldEntry }) {
  return (
    <Link href={`/storytelling/worlds/${world.id}`}>
      <article className="rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-panel transition hover:border-black/20 hover:shadow-lg">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0 flex-1">
            <h2 className="truncate text-base font-semibold text-ink-900">{world.name}</h2>
            {world.short_description ? (
              <p className="mt-1 line-clamp-2 text-sm leading-6 text-ink-600">{world.short_description}</p>
            ) : null}
            {world.is_free_chat_enabled ? (
              <div className="mt-3">
                <span className="rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-medium text-emerald-700">
                  Public chat enabled
                </span>
              </div>
            ) : null}
          </div>
          <div className="flex shrink-0 items-center justify-center rounded-full bg-paper p-3 text-ink-400">
            <Globe className="size-5" />
          </div>
        </div>
      </article>
    </Link>
  );
}

export default function WorldsPage() {
  const { data: worlds, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["storytelling-worlds"],
    queryFn: fetchUserWorlds,
  });

  return (
    <div className="space-y-8">
      <PageHeader
        description="Worlds are the settings and rule systems your stories live inside. Each story must belong to a world."
        eyebrow="Worlds"
        title="Your Worlds"
      />

      {isLoading ? (
        <div className="flex h-32 items-center justify-center">
          <Loader2 className="size-6 animate-spin text-ink-500" />
        </div>
      ) : isError ? (
        <ErrorState
          detail={error instanceof Error ? error.message : "Try refreshing the page."}
          onRetry={() => void refetch()}
          retryLabel="Reload worlds"
          title="Worlds could not be loaded."
        />
      ) : !worlds?.length ? (
        <section
          className="flex flex-col items-center justify-center rounded-[28px] border-2 border-dashed border-black/10 bg-white/50 p-16 text-center shadow-sm"
          data-testid="worlds-empty-state"
        >
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-paper text-ink-500 shadow-sm">
            <Globe className="size-8" />
          </div>
          <h3 className="mt-4 text-base font-bold text-ink-900">No worlds yet</h3>
          <p className="mt-2 max-w-sm text-sm text-ink-500">
            Build your first world to define the setting, rules, and lore that stories in your collection will share.
          </p>
          <Button className="mt-6 gap-2" disabled>
            <PlusCircle className="size-4" />
            Create a world
          </Button>
        </section>
      ) : (
        <section className="space-y-4" data-testid="worlds-list">
          <p className="text-sm text-ink-600">
            {worlds.length} {worlds.length === 1 ? "world" : "worlds"}
          </p>
          <div className="grid gap-4 md:grid-cols-2">
            {worlds.map((world) => (
              <WorldCard key={world.id} world={world} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

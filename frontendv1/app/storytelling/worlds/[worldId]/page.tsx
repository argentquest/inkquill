"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, Globe, Loader2, Users, MapPin, BookOpen, Plus, MessageSquare, GitBranch, Map } from "lucide-react";

import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";
import { fetchWorld } from "@/lib/api";

function StatCard({
  href,
  icon: Icon,
  label,
  count,
}: {
  href: string;
  icon: React.ElementType;
  label: string;
  count: number | undefined;
}) {
  return (
    <Link
      href={href}
      className="flex items-center gap-4 rounded-[20px] border border-black/10 bg-white/80 p-5 shadow-panel transition hover:border-black/20 hover:shadow-lg"
    >
      <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-paper text-ink-500">
        <Icon className="size-6" />
      </div>
      <div>
        <p className="text-sm font-medium text-ink-500">{label}</p>
        <p className="text-2xl font-bold text-ink-900">{count ?? 0}</p>
      </div>
    </Link>
  );
}

export default function WorldDetailPage() {
  const params = useParams<{ worldId: string }>();
  const worldId = Number(params.worldId);

  const { data: world, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["world", worldId],
    queryFn: () => fetchWorld(worldId),
    enabled: !isNaN(worldId),
  });

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Loader2 className="size-6 animate-spin text-ink-500" />
      </div>
    );
  }

  if (isError || !world) {
    return (
      <ErrorState
        detail={error instanceof Error ? error.message : "Try refreshing the page."}
        onRetry={() => void refetch()}
        retryLabel="Reload world"
        title="World could not be loaded."
      />
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-3">
        <Button asChild variant="ghost" size="sm">
          <Link href="/storytelling/worlds">
            <ArrowLeft className="mr-1 size-4" />
            Worlds
          </Link>
        </Button>
      </div>

      <PageHeader
        description={world.short_description ?? world.description ?? "Manage the characters, locations, and lore that define this world."}
        eyebrow="World"
        title={world.name}
      />

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard
          href={`/storytelling/worlds/${worldId}/characters`}
          icon={Users}
          label="Characters"
          count={0}
        />
        <StatCard
          href={`/storytelling/worlds/${worldId}/locations`}
          icon={MapPin}
          label="Locations"
          count={0}
        />
        <StatCard
          href={`/storytelling/worlds/${worldId}/lore-items`}
          icon={BookOpen}
          label="Lore Items"
          count={0}
        />
      </section>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-[20px] border border-dashed border-black/15 bg-white/60 p-6 text-center">
          <Users className="mx-auto size-8 text-ink-400" />
          <h3 className="mt-3 text-sm font-semibold text-ink-900">Characters</h3>
          <p className="mt-1 text-xs text-ink-500">Protagonists, NPCs, and everyone in between.</p>
          <Button asChild className="mt-4 gap-2" size="sm">
            <Link href={`/storytelling/worlds/${worldId}/characters`}>
              <Plus className="size-4" />
              View characters
            </Link>
          </Button>
        </div>

        <div className="rounded-[20px] border border-dashed border-black/15 bg-white/60 p-6 text-center">
          <MapPin className="mx-auto size-8 text-ink-400" />
          <h3 className="mt-3 text-sm font-semibold text-ink-900">Locations</h3>
          <p className="mt-1 text-xs text-ink-500">Regions, cities, buildings, and rooms.</p>
          <Button asChild className="mt-4 gap-2" size="sm">
            <Link href={`/storytelling/worlds/${worldId}/locations`}>
              <Plus className="size-4" />
              View locations
            </Link>
          </Button>
        </div>

        <div className="rounded-[20px] border border-dashed border-black/15 bg-white/60 p-6 text-center">
          <BookOpen className="mx-auto size-8 text-ink-400" />
          <h3 className="mt-3 text-sm font-semibold text-ink-900">Lore Items</h3>
          <p className="mt-1 text-xs text-ink-500">Magic systems, artifacts, factions, and history.</p>
          <Button asChild className="mt-4 gap-2" size="sm">
            <Link href={`/storytelling/worlds/${worldId}/lore-items`}>
              <Plus className="size-4" />
              View lore
            </Link>
          </Button>
        </div>

        <div className="rounded-[20px] border border-dashed border-black/15 bg-white/60 p-6 text-center">
          <MessageSquare className="mx-auto size-8 text-ink-400" />
          <h3 className="mt-3 text-sm font-semibold text-ink-900">Chat</h3>
          <p className="mt-1 text-xs text-ink-500">Discuss your world with AI.</p>
          <Button asChild className="mt-4 gap-2" size="sm">
            <Link href={`/storytelling/worlds/${worldId}/chat`}>
              <Plus className="size-4" />
              Open chat
            </Link>
          </Button>
        </div>

        <div className="rounded-[20px] border border-dashed border-black/15 bg-white/60 p-6 text-center">
          <GitBranch className="mx-auto size-8 text-ink-400" />
          <h3 className="mt-3 text-sm font-semibold text-ink-900">Hierarchy</h3>
          <p className="mt-1 text-xs text-ink-500">Explore location parent-child relationships.</p>
          <Button asChild className="mt-4 gap-2" size="sm">
            <Link href={`/storytelling/worlds/${worldId}/hierarchy`}>
              <Plus className="size-4" />
              View hierarchy
            </Link>
          </Button>
        </div>

        <div className="rounded-[20px] border border-dashed border-black/15 bg-white/60 p-6 text-center">
          <Map className="mx-auto size-8 text-ink-400" />
          <h3 className="mt-3 text-sm font-semibold text-ink-900">Map</h3>
          <p className="mt-1 text-xs text-ink-500">Visualise locations in 2-D space.</p>
          <Button asChild className="mt-4 gap-2" size="sm">
            <Link href={`/storytelling/worlds/${worldId}/map`}>
              <Plus className="size-4" />
              Open map
            </Link>
          </Button>
        </div>
      </section>
    </div>
  );
}

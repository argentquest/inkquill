import { OwnerScopeBadge } from "@/components/platform/owner-scope-badge";
import { RealtimeStatusIndicator } from "@/components/platform/realtime-status-indicator";
import type { PlatformCurrentContext } from "@/lib/types";

export function AppRouteLanding({ context }: { context: PlatformCurrentContext }) {
  return (
    <section className="rounded-[28px] border border-black/10 bg-white/65 p-5 shadow-panel">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h2 className="font-display text-3xl text-ink-900">{context.title}</h2>
          <p className="mt-3 max-w-3xl text-sm leading-7 text-ink-700">{context.description}</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <OwnerScopeBadge ownerScope={context.owner_scope} />
          <RealtimeStatusIndicator />
        </div>
      </div>
    </section>
  );
}

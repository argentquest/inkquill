import type { OwnerScope } from "@/lib/types";

const labels: Record<OwnerScope, string> = {
  none: "Platform",
  user: "User scope",
  family: "Family scope",
  patient: "Patient scope"
};

export function OwnerScopeBadge({ ownerScope }: { ownerScope: OwnerScope }) {
  return <div className="rounded-full border border-black/10 bg-white/75 px-3 py-2 text-xs uppercase tracking-[0.24em] text-ink-700">{labels[ownerScope]}</div>;
}

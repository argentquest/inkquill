import { SessionUser } from "@/lib/types";

export function AccountSummaryPanel({ user }: { user: SessionUser | null }) {
  return (
    <article className="rounded-[28px] border border-black/10 bg-white/75 p-6 shadow-panel">
      <p className="text-xs uppercase tracking-[0.28em] text-ink-600">Account summary</p>
      <h2 className="mt-3 font-display text-3xl text-ink-900">
        {user ? user.display_name ?? user.username : "Anonymous session"}
      </h2>
      <div className="mt-5 grid gap-3 text-sm text-ink-700">
        <p>Username: {user?.username ?? "No authenticated user"}</p>
        <p>Email: {user?.email ?? "Unavailable"}</p>
        <p>Admin: {user?.is_admin ? "Yes" : "No"}</p>
        <p>Status: {user?.is_active ? "Active" : user ? "Inactive" : "Anonymous"}</p>
      </div>
    </article>
  );
}

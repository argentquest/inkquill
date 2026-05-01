"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, Loader2, ShieldCheck, XCircle } from "lucide-react";
import { useLayoutEffect } from "react";

import { useSession } from "@/components/providers/app-providers";
import { PageHeader } from "@/components/shell/page-header";
import { LoadingState } from "@/components/ui/loading-state";
import { fetchAdminUsers, toggleUserActive, type AdminUser } from "@/lib/api";

function UserRow({ user }: { user: AdminUser }) {
  const queryClient = useQueryClient();
  const { mutate: toggle, isPending } = useMutation({
    mutationFn: () => toggleUserActive(user.id),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["admin-users"] }),
  });

  return (
    <tr className="border-b border-black/5 hover:bg-black/[0.02]" data-testid="admin-user-row">
      <td className="py-3 pr-4 text-sm font-medium text-ink-900">{user.username}</td>
      <td className="py-3 pr-4 text-sm text-ink-600">{user.email ?? "—"}</td>
      <td className="py-3 pr-4 text-sm text-ink-600">{user.display_name ?? "—"}</td>
      <td className="py-3 pr-4">
        {user.is_admin ? (
          <span className="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-700">
            <ShieldCheck className="size-3" /> Admin
          </span>
        ) : null}
      </td>
      <td className="py-3 pr-4">
        <span
          className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
            user.is_active
              ? "bg-emerald-50 text-emerald-700"
              : "bg-red-50 text-red-600"
          }`}
          data-testid="user-status-badge"
        >
          {user.is_active ? (
            <><CheckCircle2 className="size-3" /> Active</>
          ) : (
            <><XCircle className="size-3" /> Inactive</>
          )}
        </span>
      </td>
      <td className="py-3">
        <button
          className="rounded-[16px] border border-black/10 bg-white px-3 py-1.5 text-xs font-medium text-ink-700 transition hover:border-black/20 hover:bg-ink-50 disabled:opacity-40"
          data-testid="toggle-active-button"
          disabled={isPending}
          onClick={() => toggle()}
          type="button"
        >
          {isPending ? <Loader2 className="size-3 animate-spin" /> : user.is_active ? "Deactivate" : "Activate"}
        </button>
      </td>
    </tr>
  );
}

export default function AdminUsersPage() {
  const session = useSession();
  const isAdmin = session.user?.is_admin === true;

  useLayoutEffect(() => {
    if (session.status === "anonymous" || session.status === "error") {
      window.location.replace("/auth/login?next=/admin/users");
    } else if (session.status === "authenticated" && !isAdmin) {
      window.location.replace("/access-denied?surface=admin");
    }
  }, [session.status, isAdmin]);

  const { data: users = [], isLoading, isError } = useQuery({
    queryKey: ["admin-users"],
    queryFn: fetchAdminUsers,
    enabled: isAdmin,
  });

  if (session.status === "loading" || (session.status === "authenticated" && !isAdmin)) {
    return <LoadingState label="Checking access" />;
  }

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Admin › Users"
        title="User Management"
        description="All registered users. Toggle active status to suspend or reinstate access."
      />

      <div className="rounded-[24px] border border-black/10 bg-white/70 p-6 shadow-panel">
        {isLoading ? (
          <div className="flex items-center gap-2 text-sm text-ink-500">
            <Loader2 className="size-4 animate-spin" /> Loading users…
          </div>
        ) : isError ? (
          <p className="text-sm text-red-600" data-testid="users-error">Failed to load users.</p>
        ) : users.length === 0 ? (
          <p className="text-sm text-ink-500" data-testid="users-empty">No users found.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full" data-testid="admin-users-table">
              <thead>
                <tr className="border-b border-black/10 text-left">
                  <th className="pb-3 pr-4 text-xs uppercase tracking-[0.2em] text-ink-500">Username</th>
                  <th className="pb-3 pr-4 text-xs uppercase tracking-[0.2em] text-ink-500">Email</th>
                  <th className="pb-3 pr-4 text-xs uppercase tracking-[0.2em] text-ink-500">Display name</th>
                  <th className="pb-3 pr-4 text-xs uppercase tracking-[0.2em] text-ink-500">Role</th>
                  <th className="pb-3 pr-4 text-xs uppercase tracking-[0.2em] text-ink-500">Status</th>
                  <th className="pb-3 text-xs uppercase tracking-[0.2em] text-ink-500">Action</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => <UserRow key={u.id} user={u} />)}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

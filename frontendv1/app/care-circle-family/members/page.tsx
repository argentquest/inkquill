"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { UserRound, Check, X, Trash2 } from "lucide-react";

import { useToasts } from "@/components/providers/app-providers";
import { Button } from "@/components/ui/button";
import {
  fetchJoinRequests,
  fetchFamilyMembers,
  approveJoinRequest,
  rejectJoinRequest,
  removeFamilyMember,
  type FamilyJoinRequest,
  type FamilyMember,
} from "@/lib/api";

function RequestCard({ request, onApprove, onReject, isPending }: {
  request: FamilyJoinRequest;
  onApprove: () => void;
  onReject: () => void;
  isPending: boolean;
}) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-2xl border border-black/10 bg-white/80 px-5 py-4">
      <div className="flex items-center gap-3 min-w-0">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-amber-100 text-amber-700">
          <UserRound className="h-4 w-4" />
        </div>
        <div className="min-w-0">
          <p className="truncate text-sm font-medium text-ink-900">{request.display_name ?? request.username}</p>
          <p className="truncate text-xs text-ink-500">@{request.username}{request.email ? ` · ${request.email}` : ""}</p>
        </div>
      </div>
      <div className="flex shrink-0 gap-2">
        <button
          className="flex items-center gap-1.5 rounded-xl bg-green-600 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-green-700 disabled:opacity-50"
          disabled={isPending}
          onClick={onApprove}
        >
          <Check className="h-3.5 w-3.5" />
          Approve
        </button>
        <button
          className="flex items-center gap-1.5 rounded-xl border border-black/10 px-3 py-1.5 text-xs font-medium text-ink-700 transition hover:bg-black/5 disabled:opacity-50"
          disabled={isPending}
          onClick={onReject}
        >
          <X className="h-3.5 w-3.5" />
          Decline
        </button>
      </div>
    </div>
  );
}

function MemberCard({ member, onRemove, isPending }: {
  member: FamilyMember;
  onRemove: () => void;
  isPending: boolean;
}) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-2xl border border-black/10 bg-white/80 px-5 py-4">
      <div className="flex items-center gap-3 min-w-0">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-ink-100 text-ink-600">
          <UserRound className="h-4 w-4" />
        </div>
        <div className="min-w-0">
          <p className="truncate text-sm font-medium text-ink-900">{member.display_name ?? member.username}</p>
          <p className="truncate text-xs text-ink-500">@{member.username}{member.email ? ` · ${member.email}` : ""}</p>
        </div>
      </div>
      <button
        className="flex shrink-0 items-center gap-1.5 rounded-xl border border-black/10 px-3 py-1.5 text-xs font-medium text-red-600 transition hover:bg-red-50 disabled:opacity-50"
        disabled={isPending}
        onClick={onRemove}
      >
        <Trash2 className="h-3.5 w-3.5" />
        Remove
      </button>
    </div>
  );
}

export default function MembersPage() {
  const queryClient = useQueryClient();
  const { pushToast } = useToasts();

  const { data: requests = [], isLoading: requestsLoading } = useQuery({
    queryKey: ["family-join-requests"],
    queryFn: fetchJoinRequests,
  });

  const { data: members = [], isLoading: membersLoading } = useQuery({
    queryKey: ["family-members"],
    queryFn: fetchFamilyMembers,
  });

  const approveMutation = useMutation({
    mutationFn: approveJoinRequest,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["family-join-requests"] });
      void queryClient.invalidateQueries({ queryKey: ["family-members"] });
      pushToast({ title: "Member approved", tone: "success", detail: "They can now access your family circle." });
    },
    onError: (err) => pushToast({ title: "Could not approve", tone: "error", detail: err instanceof Error ? err.message : "Try again." }),
  });

  const rejectMutation = useMutation({
    mutationFn: rejectJoinRequest,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["family-join-requests"] });
      pushToast({ title: "Request declined", tone: "success", detail: "The request has been rejected." });
    },
    onError: (err) => pushToast({ title: "Could not decline", tone: "error", detail: err instanceof Error ? err.message : "Try again." }),
  });

  const removeMutation = useMutation({
    mutationFn: removeFamilyMember,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["family-members"] });
      pushToast({ title: "Member removed", tone: "success", detail: "They no longer have access to your family circle." });
    },
    onError: (err) => pushToast({ title: "Could not remove member", tone: "error", detail: err instanceof Error ? err.message : "Try again." }),
  });

  const isMutating = approveMutation.isPending || rejectMutation.isPending || removeMutation.isPending;

  return (
    <div className="mx-auto max-w-2xl space-y-10 py-8 px-4">
      <div>
        <p className="text-xs uppercase tracking-[0.32em] text-ink-600">Family circle</p>
        <h1 className="mt-2 font-display text-3xl text-ink-900">Members</h1>
        <p className="mt-3 text-sm leading-7 text-ink-700">
          Approve or decline join requests, and manage who has access to your family circle.
        </p>
      </div>

      <section>
        <h2 className="text-xs uppercase tracking-[0.24em] text-ink-600 mb-4">
          Pending requests {requests.length > 0 ? <span className="ml-1 inline-flex items-center justify-center rounded-full bg-amber-100 px-2 py-0.5 text-amber-700">{requests.length}</span> : null}
        </h2>
        {requestsLoading ? (
          <p className="text-sm text-ink-500">Loading...</p>
        ) : requests.length === 0 ? (
          <p className="rounded-2xl border border-dashed border-black/10 px-5 py-6 text-center text-sm text-ink-500">No pending requests.</p>
        ) : (
          <div className="space-y-3">
            {requests.map((r) => (
              <RequestCard
                key={r.id}
                request={r}
                isPending={isMutating}
                onApprove={() => approveMutation.mutate(r.id)}
                onReject={() => rejectMutation.mutate(r.id)}
              />
            ))}
          </div>
        )}
      </section>

      <section>
        <h2 className="text-xs uppercase tracking-[0.24em] text-ink-600 mb-4">Active members</h2>
        {membersLoading ? (
          <p className="text-sm text-ink-500">Loading...</p>
        ) : members.length === 0 ? (
          <p className="rounded-2xl border border-dashed border-black/10 px-5 py-6 text-center text-sm text-ink-500">
            No members yet. Share your join code so others can request access.
          </p>
        ) : (
          <div className="space-y-3">
            {members.map((m) => (
              <MemberCard
                key={m.id}
                member={m}
                isPending={isMutating}
                onRemove={() => removeMutation.mutate(m.id)}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

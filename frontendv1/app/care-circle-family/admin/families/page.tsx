"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Users, Trash2, Ban, CheckCircle } from "lucide-react";

import { useToasts } from "@/components/providers/app-providers";
import {
  adminFetchFamilies,
  adminDisableFamily,
  adminDeleteFamily,
  type AdminFamily,
} from "@/lib/api";

function FamilyRow({ family, onDisable, onDelete, isMutating }: {
  family: AdminFamily;
  onDisable: () => void;
  onDelete: () => void;
  isMutating: boolean;
}) {
  const [confirmDelete, setConfirmDelete] = useState(false);

  return (
    <div className={`rounded-2xl border px-5 py-4 ${family.is_disabled ? "border-red-200 bg-red-50/50" : "border-black/10 bg-white/80"}`}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <p className="font-medium text-ink-900 truncate">{family.name}</p>
            {family.is_disabled && (
              <span className="shrink-0 rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700">Disabled</span>
            )}
          </div>
          <p className="mt-0.5 text-xs text-ink-500 font-mono tracking-wider">{family.join_code}</p>
          <div className="mt-2 flex flex-wrap gap-3 text-xs text-ink-600">
            <span>Owner: <strong>{family.owner_display_name ?? family.owner_username ?? "Unknown"}</strong></span>
            <span className="flex items-center gap-1"><Users className="h-3 w-3" />{family.member_count} member{family.member_count !== 1 ? "s" : ""}</span>
            <span>{family.patient_count} patient{family.patient_count !== 1 ? "s" : ""}</span>
            {family.pending_requests > 0 && (
              <span className="text-amber-600">{family.pending_requests} pending request{family.pending_requests !== 1 ? "s" : ""}</span>
            )}
          </div>
        </div>
        <div className="flex shrink-0 gap-2">
          <button
            className="flex items-center gap-1.5 rounded-xl border border-black/10 px-3 py-1.5 text-xs font-medium text-ink-700 transition hover:bg-black/5 disabled:opacity-50"
            disabled={isMutating}
            onClick={onDisable}
            title={family.is_disabled ? "Enable family" : "Disable family"}
          >
            {family.is_disabled ? <CheckCircle className="h-3.5 w-3.5 text-green-600" /> : <Ban className="h-3.5 w-3.5" />}
            {family.is_disabled ? "Enable" : "Disable"}
          </button>
          {confirmDelete ? (
            <div className="flex gap-1.5">
              <button
                className="rounded-xl bg-red-600 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-red-700 disabled:opacity-50"
                disabled={isMutating}
                onClick={onDelete}
              >
                Confirm delete
              </button>
              <button
                className="rounded-xl border border-black/10 px-3 py-1.5 text-xs font-medium text-ink-700 transition hover:bg-black/5"
                onClick={() => setConfirmDelete(false)}
              >
                Cancel
              </button>
            </div>
          ) : (
            <button
              className="flex items-center gap-1.5 rounded-xl border border-red-200 px-3 py-1.5 text-xs font-medium text-red-600 transition hover:bg-red-50 disabled:opacity-50"
              disabled={isMutating}
              onClick={() => setConfirmDelete(true)}
            >
              <Trash2 className="h-3.5 w-3.5" />
              Delete
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default function AdminFamiliesPage() {
  const queryClient = useQueryClient();
  const { pushToast } = useToasts();

  const { data: families = [], isLoading } = useQuery({
    queryKey: ["admin-families"],
    queryFn: adminFetchFamilies,
  });

  const disableMutation = useMutation({
    mutationFn: ({ id, disabled }: { id: number; disabled: boolean }) => adminDisableFamily(id, disabled),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["admin-families"] });
      pushToast({ title: "Family updated", tone: "success", detail: "The family status has been changed." });
    },
    onError: (err) => pushToast({ title: "Error", tone: "error", detail: err instanceof Error ? err.message : "Try again." }),
  });

  const deleteMutation = useMutation({
    mutationFn: adminDeleteFamily,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["admin-families"] });
      pushToast({ title: "Family deleted", tone: "success", detail: "The family and all its data have been removed." });
    },
    onError: (err) => pushToast({ title: "Error", tone: "error", detail: err instanceof Error ? err.message : "Try again." }),
  });

  const isMutating = disableMutation.isPending || deleteMutation.isPending;

  return (
    <div className="mx-auto max-w-3xl space-y-8 py-8 px-4">
      <div>
        <p className="text-xs uppercase tracking-[0.32em] text-ink-600">Admin</p>
        <h1 className="mt-2 font-display text-3xl text-ink-900">All families</h1>
        <p className="mt-3 text-sm leading-7 text-ink-700">
          View, disable, or delete any family. Disabling prevents the family from being joined but keeps all data intact.
        </p>
      </div>

      {isLoading ? (
        <p className="text-sm text-ink-500">Loading families...</p>
      ) : families.length === 0 ? (
        <p className="rounded-2xl border border-dashed border-black/10 px-5 py-6 text-center text-sm text-ink-500">No families yet.</p>
      ) : (
        <div className="space-y-3">
          <p className="text-xs text-ink-500">{families.length} famil{families.length !== 1 ? "ies" : "y"}</p>
          {families.map((family) => (
            <FamilyRow
              key={family.id}
              family={family}
              isMutating={isMutating}
              onDisable={() => disableMutation.mutate({ id: family.id, disabled: !family.is_disabled })}
              onDelete={() => deleteMutation.mutate(family.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

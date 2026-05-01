"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, Loader2, Megaphone, Trash2, XCircle } from "lucide-react";
import { useLayoutEffect } from "react";

import { useSession } from "@/components/providers/app-providers";
import { PageHeader } from "@/components/shell/page-header";
import { LoadingState } from "@/components/ui/loading-state";
import { deleteCTA, fetchAdminCTAs, toggleCTAActive, type AdminCTA } from "@/lib/api";

function CTARow({ cta }: { cta: AdminCTA }) {
  const queryClient = useQueryClient();

  const { mutate: toggle, isPending: toggling } = useMutation({
    mutationFn: () => toggleCTAActive(cta.id),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["admin-ctas"] }),
  });

  const { mutate: remove, isPending: removing } = useMutation({
    mutationFn: () => deleteCTA(cta.id),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["admin-ctas"] }),
  });

  return (
    <div
      className="flex items-start justify-between gap-4 rounded-[20px] border border-black/8 bg-white px-5 py-4"
      data-testid="cta-row"
    >
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2 flex-wrap">
          <p className="font-medium text-ink-900 text-sm">{cta.title}</p>
          <span className="rounded-full bg-ink-900/6 px-2 py-0.5 text-xs text-ink-600">{cta.position}</span>
          <span className="rounded-full bg-ink-900/6 px-2 py-0.5 text-xs text-ink-600">{cta.style}</span>
          <span
            className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
              cta.is_active ? "bg-emerald-50 text-emerald-700" : "bg-red-50 text-red-600"
            }`}
            data-testid="cta-status-badge"
          >
            {cta.is_active ? <><CheckCircle2 className="size-3" /> Active</> : <><XCircle className="size-3" /> Inactive</>}
          </span>
        </div>
        {cta.subtitle ? <p className="mt-1 text-xs text-ink-500">{cta.subtitle}</p> : null}
        {cta.primary_button_text ? (
          <p className="mt-1 text-xs text-ink-400">
            CTA: {cta.primary_button_text}
            {cta.primary_button_url ? ` → ${cta.primary_button_url}` : ""}
          </p>
        ) : null}
      </div>
      <div className="flex shrink-0 items-center gap-2">
        <button
          className="rounded-[16px] border border-black/10 bg-white px-3 py-1.5 text-xs font-medium text-ink-700 transition hover:border-black/20 hover:bg-ink-50 disabled:opacity-40"
          data-testid="toggle-cta-button"
          disabled={toggling}
          onClick={() => toggle()}
          type="button"
        >
          {toggling ? <Loader2 className="size-3 animate-spin" /> : cta.is_active ? "Deactivate" : "Activate"}
        </button>
        <button
          className="rounded-[16px] border border-red-200 bg-red-50 px-3 py-1.5 text-xs font-medium text-red-600 transition hover:bg-red-100 disabled:opacity-40"
          data-testid="delete-cta-button"
          disabled={removing}
          onClick={() => remove()}
          type="button"
        >
          {removing ? <Loader2 className="size-3 animate-spin" /> : <Trash2 className="size-3" />}
        </button>
      </div>
    </div>
  );
}

export default function AdminCTAPage() {
  const session = useSession();
  const isAdmin = session.user?.is_admin === true;

  useLayoutEffect(() => {
    if (session.status === "anonymous" || session.status === "error") {
      window.location.replace("/auth/login?next=/admin/cta");
    } else if (session.status === "authenticated" && !isAdmin) {
      window.location.replace("/access-denied?surface=admin");
    }
  }, [session.status, isAdmin]);

  const { data: ctas = [], isLoading, isError } = useQuery({
    queryKey: ["admin-ctas"],
    queryFn: fetchAdminCTAs,
    enabled: isAdmin,
  });

  if (session.status === "loading" || (session.status === "authenticated" && !isAdmin)) {
    return <LoadingState label="Checking access" />;
  }

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Admin › CTA"
        title="CTA Content"
        description="Call-to-action blocks rendered across the platform. Toggle active status or remove entries."
      />

      <div className="rounded-[24px] border border-black/10 bg-white/70 p-6 shadow-panel">
        {isLoading ? (
          <div className="flex items-center gap-2 text-sm text-ink-500">
            <Loader2 className="size-4 animate-spin" /> Loading CTA entries…
          </div>
        ) : isError ? (
          <p className="text-sm text-red-600" data-testid="cta-error">Failed to load CTA content.</p>
        ) : ctas.length === 0 ? (
          <div className="flex flex-col items-center gap-2 py-8 text-ink-400" data-testid="cta-empty">
            <Megaphone className="size-8 opacity-40" />
            <p className="text-sm">No CTA entries found.</p>
          </div>
        ) : (
          <div className="space-y-3" data-testid="cta-list">
            {ctas.map((cta) => <CTARow cta={cta} key={cta.id} />)}
          </div>
        )}
      </div>
    </div>
  );
}

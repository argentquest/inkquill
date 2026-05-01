"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, CheckCircle2, Loader2, Wrench } from "lucide-react";
import { useLayoutEffect, useState } from "react";

import { useSession } from "@/components/providers/app-providers";
import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { LoadingState } from "@/components/ui/loading-state";
import { disableMaintenanceMode, enableMaintenanceMode, fetchMaintenanceStatusAdmin } from "@/lib/api";

export default function AdminMaintenancePage() {
  const session = useSession();
  const isAdmin = session.user?.is_admin === true;

  useLayoutEffect(() => {
    if (session.status === "anonymous" || session.status === "error") {
      window.location.replace("/auth/login?next=/admin/maintenance");
    } else if (session.status === "authenticated" && !isAdmin) {
      window.location.replace("/access-denied?surface=admin");
    }
  }, [session.status, isAdmin]);

  const queryClient = useQueryClient();

  const { data: status, isLoading } = useQuery({
    queryKey: ["maintenance-status"],
    queryFn: fetchMaintenanceStatusAdmin,
    enabled: isAdmin,
    refetchInterval: 15000,
  });

  const [customMessage, setCustomMessage] = useState("");
  const [duration, setDuration] = useState("5");

  const { mutate: enable, isPending: enabling } = useMutation({
    mutationFn: () => enableMaintenanceMode(customMessage || undefined, Number(duration)),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["maintenance-status"] }),
  });

  const { mutate: disable, isPending: disabling } = useMutation({
    mutationFn: disableMaintenanceMode,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["maintenance-status"] }),
  });

  if (session.status === "loading" || (session.status === "authenticated" && !isAdmin)) {
    return <LoadingState label="Checking access" />;
  }

  const isEnabled = status?.enabled === true;

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Admin › Maintenance"
        title="Maintenance Mode"
        description="Enable maintenance mode to show a notice to all non-admin users while you perform platform updates."
      />

      <div className="rounded-[24px] border border-black/10 bg-white/70 p-6 shadow-panel">
        <div className="flex items-center gap-3 mb-6">
          <div
            className={`flex h-10 w-10 items-center justify-center rounded-full ${
              isEnabled ? "bg-amber-100 text-amber-700" : "bg-emerald-50 text-emerald-700"
            }`}
            data-testid="maintenance-status-icon"
          >
            {isEnabled ? <AlertTriangle className="size-5" /> : <CheckCircle2 className="size-5" />}
          </div>
          <div>
            <p className="font-semibold text-ink-900" data-testid="maintenance-status-label">
              {isLoading ? "Checking…" : isEnabled ? "Maintenance mode is ON" : "Site is live"}
            </p>
            {status?.message ? (
              <p className="text-sm text-ink-600">{status.message}</p>
            ) : null}
          </div>
        </div>

        {!isEnabled ? (
          <div className="space-y-4">
            <div className="flex flex-col gap-1">
              <label className="text-xs uppercase tracking-[0.2em] text-ink-600" htmlFor="maint-message">
                Message (optional)
              </label>
              <input
                className="rounded-[16px] border border-black/10 bg-[#fcfaf6] px-4 py-2.5 text-sm text-ink-900 outline-none focus:border-amber-600"
                data-testid="maintenance-message-input"
                id="maint-message"
                onChange={(e) => setCustomMessage(e.target.value)}
                placeholder="The application is getting an update and will be back shortly."
                type="text"
                value={customMessage}
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-xs uppercase tracking-[0.2em] text-ink-600" htmlFor="maint-duration">
                Duration (minutes)
              </label>
              <input
                className="w-32 rounded-[16px] border border-black/10 bg-[#fcfaf6] px-4 py-2.5 text-sm text-ink-900 outline-none focus:border-amber-600"
                data-testid="maintenance-duration-input"
                id="maint-duration"
                min={1}
                onChange={(e) => setDuration(e.target.value)}
                type="number"
                value={duration}
              />
            </div>
            <Button
              className="gap-2"
              data-testid="enable-maintenance-button"
              disabled={enabling}
              onClick={() => enable()}
              type="button"
            >
              {enabling ? <Loader2 className="size-4 animate-spin" /> : <Wrench className="size-4" />}
              Enable maintenance mode
            </Button>
          </div>
        ) : (
          <Button
            className="gap-2"
            data-testid="disable-maintenance-button"
            disabled={disabling}
            onClick={() => disable()}
            type="button"
          >
            {disabling ? <Loader2 className="size-4 animate-spin" /> : <CheckCircle2 className="size-4" />}
            Disable maintenance mode
          </Button>
        )}
      </div>
    </div>
  );
}

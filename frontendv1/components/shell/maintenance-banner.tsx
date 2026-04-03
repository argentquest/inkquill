"use client";

import { AlertTriangle } from "lucide-react";

import { useMaintenance } from "@/components/providers/app-providers";

export function MaintenanceBanner() {
  const { enabled, end_time, loading, message } = useMaintenance();

  if (loading || !enabled) {
    return null;
  }

  return (
    <div className="border-b border-ember/25 bg-[#fff1e8]">
      <div className="mx-auto flex max-w-7xl items-start gap-3 px-4 py-3 text-sm text-[#7a3d21] md:px-6">
        <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
        <div>
          <p className="font-semibold uppercase tracking-[0.2em]">Maintenance Mode</p>
          <p className="mt-1 leading-6">
            {message ?? "Scheduled maintenance is active."}
            {end_time ? ` Expected end: ${new Date(end_time).toLocaleString()}.` : ""}
          </p>
        </div>
      </div>
    </div>
  );
}

"use client";

import { useMaintenance } from "@/components/providers/app-providers";

export function MaintenanceGate({ children }: { children: React.ReactNode }) {
  const { enabled, message } = useMaintenance();

  if (!enabled) {
    return <>{children}</>;
  }

  return (
    <div className="relative">
      <div aria-hidden className="pointer-events-none opacity-35 blur-[1px]">
        {children}
      </div>
      <div className="absolute inset-0 flex items-center justify-center p-6">
        <div className="max-w-xl rounded-[28px] border border-ember/25 bg-paper/95 p-8 text-center shadow-panel">
          <p className="text-xs uppercase tracking-[0.28em] text-ember">App Access Paused</p>
          <h2 className="mt-3 font-display text-3xl text-ink-900">Maintenance is active</h2>
          <p className="mt-4 text-sm leading-7 text-ink-700">
            {message ??
              "Authenticated workspaces remain visible for context, but actions should pause until maintenance ends."}
          </p>
        </div>
      </div>
    </div>
  );
}

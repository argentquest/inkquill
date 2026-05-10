"use client";

import { AppShell } from "@/components/shell/app-shell";

export function AppShellResolver({ children }: { children: React.ReactNode }) {
  return (
    <AppShell>
      {children}
    </AppShell>
  );
}

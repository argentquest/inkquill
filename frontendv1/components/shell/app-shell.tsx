import { Footer } from "@/components/shell/footer";
import { MaintenanceGate } from "@/components/shell/maintenance-gate";
import { TopNav } from "@/components/shell/top-nav";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,rgba(220,229,226,0.85),transparent_34%),linear-gradient(180deg,#f7f4ef_0%,#efe7db_100%)]">
      <TopNav />
      <main className="mx-auto max-w-7xl px-4 py-8 md:px-6">
        <MaintenanceGate>{children}</MaintenanceGate>
        <Footer />
      </main>
    </div>
  );
}

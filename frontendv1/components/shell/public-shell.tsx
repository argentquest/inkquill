import { Footer } from "@/components/shell/footer";
import { TopNav } from "@/components/shell/top-nav";

export function PublicShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_right,rgba(216,108,61,0.14),transparent_28%),linear-gradient(180deg,#f6f1e8_0%,#f1e8d8_100%)]">
      <TopNav />
      <main className="mx-auto max-w-7xl px-4 py-8 md:px-6">
        {children}
        <Footer />
      </main>
    </div>
  );
}

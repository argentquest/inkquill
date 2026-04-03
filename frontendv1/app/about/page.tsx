import { PublicShell } from "@/components/shell/public-shell";
import { PageHeader } from "@/components/shell/page-header";

export default function AboutPage() {
  return (
    <PublicShell>
      <div className="space-y-8">
        <PageHeader
          description="The React rebuild is being structured as a creative-product platform first, with shared route patterns, strong shell behavior, and backend-led contracts."
          eyebrow="About"
          title="Ink & Quill is rebuilding the product around a cleaner React foundation."
        />
        <section className="rounded-[28px] border border-black/10 bg-white/80 p-8 shadow-panel">
          <p className="max-w-3xl text-base leading-8 text-ink-700">
            This route exists to prove the shared public framework can support editorial and support content without pulling in app-only chrome or backend-specific view templates.
          </p>
        </section>
      </div>
    </PublicShell>
  );
}

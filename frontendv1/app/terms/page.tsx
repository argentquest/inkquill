import { PublicShell } from "@/components/shell/public-shell";
import { PageHeader } from "@/components/shell/page-header";

export default function TermsPage() {
  return (
    <PublicShell>
      <div className="space-y-8">
        <PageHeader
          description="This route completes the core public information set introduced in Sprint 3."
          eyebrow="Terms"
          title="Terms pages no longer need to wait for the final admin sweep."
        />
        <section className="rounded-[28px] border border-black/10 bg-white/80 p-8 shadow-panel">
          <p className="max-w-3xl text-base leading-8 text-ink-700">
            The current content is intentionally light. The important part is that the route exists, carries the public shell correctly, and gives the React rebuild a stable legal-content home.
          </p>
        </section>
      </div>
    </PublicShell>
  );
}

import { cn } from "@/lib/utils";

export function SettingsFormSection({
  children,
  className,
  description,
  eyebrow = "Settings",
  title
}: {
  children: React.ReactNode;
  className?: string;
  description: string;
  eyebrow?: string;
  title: string;
}) {
  return (
    <section className={cn("rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-panel", className)}>
      <p className="text-xs uppercase tracking-[0.26em] text-ink-600">{eyebrow}</p>
      <h2 className="mt-3 font-display text-3xl text-ink-900">{title}</h2>
      <p className="mt-3 max-w-3xl text-sm leading-7 text-ink-700">{description}</p>
      <div className="mt-6">{children}</div>
    </section>
  );
}

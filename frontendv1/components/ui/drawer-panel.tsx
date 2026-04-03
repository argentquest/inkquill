import { cn } from "@/lib/utils";

export function DrawerPanel({
  children,
  className,
  title,
  description
}: {
  children: React.ReactNode;
  className?: string;
  title: string;
  description?: string;
}) {
  return (
    <aside
      className={cn(
        "rounded-[28px] border border-black/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.84),rgba(246,241,232,0.9))] p-6 shadow-panel",
        className
      )}
    >
      <p className="text-xs uppercase tracking-[0.26em] text-ink-600">Drawer Pattern</p>
      <h2 className="mt-3 font-display text-3xl text-ink-900">{title}</h2>
      {description ? <p className="mt-3 text-sm leading-7 text-ink-700">{description}</p> : null}
      <div className="mt-6">{children}</div>
    </aside>
  );
}

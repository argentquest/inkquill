export function EmptyState({
  eyebrow,
  title,
  description,
  action
}: {
  eyebrow: string;
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="rounded-[28px] border border-dashed border-black/15 bg-white/65 p-8 text-center shadow-panel">
      <p className="text-xs uppercase tracking-[0.28em] text-ink-600">{eyebrow}</p>
      <h2 className="mt-3 font-display text-3xl text-ink-900">{title}</h2>
      <p className="mx-auto mt-3 max-w-2xl text-sm leading-7 text-ink-700">{description}</p>
      {action ? <div className="mt-6 flex justify-center">{action}</div> : null}
    </div>
  );
}

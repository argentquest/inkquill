export function StatCard({
  label,
  value,
  detail
}: {
  label: string;
  value: string | number;
  detail?: string;
}) {
  return (
    <article className="rounded-[26px] border border-black/10 bg-white/78 p-5 shadow-panel">
      <p className="text-xs uppercase tracking-[0.24em] text-ink-600">{label}</p>
      <h2 className="mt-3 font-display text-4xl text-ink-900">{value}</h2>
      {detail ? <p className="mt-3 text-sm leading-7 text-ink-700">{detail}</p> : null}
    </article>
  );
}

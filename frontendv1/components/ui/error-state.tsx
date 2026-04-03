export function ErrorState({
  title,
  detail,
  retryLabel,
  onRetry
}: {
  title: string;
  detail?: string;
  retryLabel?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="rounded-[28px] border border-ember/30 bg-white/85 p-8 shadow-panel">
      <p className="text-xs uppercase tracking-[0.3em] text-ember">Error</p>
      <h2 className="mt-3 font-display text-3xl text-ink-900">{title}</h2>
      {detail ? <p className="mt-3 max-w-2xl text-sm leading-7 text-ink-700">{detail}</p> : null}
      {onRetry ? (
        <button
          className="mt-6 rounded-full bg-ink-900 px-5 py-3 text-sm font-semibold text-paper transition hover:bg-ink-700"
          onClick={onRetry}
          type="button"
        >
          {retryLabel ?? "Retry"}
        </button>
      ) : null}
    </div>
  );
}

export function PatientAccessStateBadge({
  state
}: {
  state: "active" | "inactive" | "archived";
}) {
  const styles = {
    active: "bg-[#d7f1df] text-[#1d5f33]",
    inactive: "bg-[#f4e7bf] text-[#7c5a10]",
    archived: "bg-[#eaded9] text-[#7c4d3b]"
  };

  return (
    <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] ${styles[state]}`}>
      {state}
    </span>
  );
}

import { cn } from "@/lib/utils";

export interface DataTableColumn<T> {
  key: string;
  header: string;
  className?: string;
  render: (_row: T) => React.ReactNode;
}

export function DataTable<T>({
  columns,
  emptyMessage,
  rows,
  tableLabel
}: {
  columns: DataTableColumn<T>[];
  emptyMessage: string;
  rows: T[];
  tableLabel: string;
}) {
  return (
    <div className="overflow-hidden rounded-[28px] border border-black/10 bg-white/80 shadow-panel">
      <div className="overflow-x-auto">
        <table aria-label={tableLabel} className="min-w-full border-collapse text-left">
          <thead className="bg-black/[0.03]">
            <tr>
              {columns.map((column) => (
                <th
                  className={cn("px-5 py-4 text-xs uppercase tracking-[0.24em] text-ink-600", column.className)}
                  key={column.key}
                  scope="col"
                >
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr>
                <td className="px-5 py-10 text-sm text-ink-700" colSpan={columns.length}>
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              rows.map((row, index) => (
                <tr className="border-t border-black/6" key={index}>
                  {columns.map((column) => (
                    <td className={cn("px-5 py-4 align-top text-sm text-ink-800", column.className)} key={column.key}>
                      {column.render(row)}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

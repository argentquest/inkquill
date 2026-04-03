import { AlertTriangle } from "lucide-react";

import { Button } from "@/components/ui/button";

export function ConfirmationModal({
  body,
  cancelLabel = "Cancel",
  confirmLabel = "Confirm",
  onCancel,
  onConfirm,
  open,
  title
}: {
  body: string;
  cancelLabel?: string;
  confirmLabel?: string;
  onCancel: () => void;
  onConfirm: () => void;
  open: boolean;
  title: string;
}) {
  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/35 px-4">
      <div className="w-full max-w-lg rounded-[32px] border border-black/10 bg-paper p-7 shadow-panel">
        <div className="flex items-start gap-4">
          <div className="rounded-full bg-ember/12 p-3 text-ember">
            <AlertTriangle className="h-5 w-5" />
          </div>
          <div className="flex-1">
            <p className="text-xs uppercase tracking-[0.28em] text-ink-600">Confirmation</p>
            <h2 className="mt-2 font-display text-3xl text-ink-900">{title}</h2>
            <p className="mt-3 text-sm leading-7 text-ink-700">{body}</p>
          </div>
        </div>
        <div className="mt-7 flex flex-wrap justify-end gap-3">
          <Button onClick={onCancel} variant="secondary">
            {cancelLabel}
          </Button>
          <Button onClick={onConfirm}>{confirmLabel}</Button>
        </div>
      </div>
    </div>
  );
}

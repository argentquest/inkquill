"use client";

import { X } from "lucide-react";

import { useToasts } from "@/components/providers/app-providers";
import { cn } from "@/lib/utils";

const toneClasses = {
  info: "border-forest/20 bg-mist text-forest",
  success: "border-forest/20 bg-[#e6f2ec] text-forest",
  warning: "border-ember/20 bg-[#fff0e8] text-[#7a3d21]",
  error: "border-[#c65353]/20 bg-[#faeaea] text-[#7c2020]"
};

export function ToastCenter() {
  const { dismissToast, toasts } = useToasts();

  return (
    <div className="pointer-events-none fixed right-4 top-4 z-50 flex w-full max-w-sm flex-col gap-3">
      {toasts.map((toast) => (
        <article
          className={cn(
            "pointer-events-auto rounded-[22px] border p-4 shadow-panel backdrop-blur",
            toneClasses[toast.tone ?? "info"]
          )}
          key={toast.id}
        >
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="font-semibold">{toast.title}</p>
              {toast.detail ? <p className="mt-1 text-sm leading-6 opacity-80">{toast.detail}</p> : null}
            </div>
            <button
              aria-label="Dismiss notification"
              className="rounded-full p-1 transition hover:bg-black/5"
              onClick={() => dismissToast(toast.id)}
              type="button"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </article>
      ))}
    </div>
  );
}

"use client";

import { AlertCircle } from "lucide-react";

export function InlineValidationMessage({ message }: { message?: string }) {
  if (!message) {
    return null;
  }

  return (
    <p className="mt-2 flex items-center gap-2 text-sm text-[#8a2e2e]">
      <AlertCircle className="h-4 w-4" />
      <span>{message}</span>
    </p>
  );
}

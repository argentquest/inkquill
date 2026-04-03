"use client";

import { ErrorState } from "@/components/ui/error-state";

export default function Error({
  error,
  reset
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main className="mx-auto max-w-7xl px-4 py-8 md:px-6">
      <ErrorState
        detail={error.message}
        onRetry={reset}
        retryLabel="Try again"
        title="The shell hit an unexpected error."
      />
    </main>
  );
}

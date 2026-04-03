"use client";

import { useCookieConsent } from "@/components/providers/app-providers";

export function CookieConsentBanner() {
  const { accept, accepted } = useCookieConsent();

  if (accepted) {
    return null;
  }

  return (
    <aside className="fixed bottom-4 left-4 right-4 z-50 mx-auto flex max-w-3xl flex-col gap-4 rounded-[28px] border border-black/10 bg-paper p-5 shadow-panel md:flex-row md:items-center md:justify-between">
      <div>
        <p className="text-xs uppercase tracking-[0.28em] text-ink-600">Cookie Consent</p>
        <p className="mt-2 text-sm leading-7 text-ink-700">
          Sprint 1 persists theme and consent preferences locally so the shell behaves consistently across visits.
        </p>
      </div>
      <button
        className="rounded-full bg-ink-900 px-5 py-3 text-sm font-semibold text-paper transition hover:bg-ink-700"
        onClick={accept}
        type="button"
      >
        Accept
      </button>
    </aside>
  );
}

"use client";

import { useEffect, useMemo, useState } from "react";

export function RealtimeStatusIndicator() {
  const [online, setOnline] = useState(true);

  useEffect(() => {
    const sync = () => setOnline(window.navigator.onLine);
    sync();
    window.addEventListener("online", sync);
    window.addEventListener("offline", sync);

    return () => {
      window.removeEventListener("online", sync);
      window.removeEventListener("offline", sync);
    };
  }, []);

  const state = useMemo(
    () => ({
      label: online ? "Realtime ready" : "Realtime offline",
      tone: online ? "text-emerald-900 bg-emerald-900/10 border-emerald-900/20" : "text-amber-900 bg-amber-900/10 border-amber-900/20"
    }),
    [online]
  );

  return <div className={`rounded-full border px-3 py-2 text-xs uppercase tracking-[0.24em] ${state.tone}`}>{state.label}</div>;
}

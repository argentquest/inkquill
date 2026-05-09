"use client";

import { Volume2 } from "lucide-react";
import { ProvBadge } from "@/components/care-circle-family/prov-badge";

export function VoiceMessageCard({
  message,
}: {
  message?: { url: string; duration?: string; from?: string } | null;
}) {
  if (!message) return null;

  return (
    <div className="relative overflow-hidden rounded-[24px] bg-gradient-to-br from-ember via-[#c45a2e] to-ink-900 p-5 text-white shadow-panel">
      <ProvBadge kind="family">Voice</ProvBadge>
      <div className="mt-3 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white/15">
          <Volume2 className="h-5 w-5 text-white" />
        </div>
        <div>
          <p className="text-sm font-semibold">
            {message.from ? `From ${message.from}` : "Voice message"}
          </p>
          {message.duration && (
            <p className="text-xs text-white/70">{message.duration}</p>
          )}
        </div>
      </div>
    </div>
  );
}

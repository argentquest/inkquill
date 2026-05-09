"use client";

import Image from "next/image";
import { ProvBadge } from "@/components/care-circle-family/prov-badge";

export interface TodayMetric {
  label: string;
  value: string;
}

export function TodayHero({
  leadPhoto,
  headline,
  lede,
  metrics,
  caption,
}: {
  leadPhoto?: { url: string; alt?: string } | null;
  headline?: string;
  lede?: string;
  metrics?: TodayMetric[];
  caption?: string;
}) {
  if (!leadPhoto && !headline && !lede) return null;

  return (
    <section className="overflow-hidden rounded-[28px] border border-black/10 bg-white/80 shadow-panel">
      <div className="grid gap-0 lg:grid-cols-2">
        {/* Photo side */}
        {leadPhoto && (
          <div className="relative aspect-[4/3] lg:aspect-auto">
            <Image
              src={leadPhoto.url}
              alt={leadPhoto.alt ?? "Today"}
              fill
              className="object-cover"
              sizes="(max-width: 1024px) 100vw, 50vw"
            />
            <div className="absolute left-4 top-4">
              <ProvBadge kind="family">Family photo</ProvBadge>
            </div>
            {caption && (
              <p className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-4 pt-12 text-sm italic text-white/90">
                {caption}
              </p>
            )}
          </div>
        )}

        {/* Text side */}
        <div className="flex flex-col justify-center p-6 lg:p-8">
          <span className="text-xs font-semibold uppercase tracking-[0.28em] text-forest">
            Today&#39;s Edition
          </span>
          {headline && (
            <h2 className="mt-3 font-display text-2xl font-semibold leading-tight text-ink-900 md:text-3xl">
              {headline}
            </h2>
          )}
          {lede && (
            <p className="mt-3 text-base leading-7 text-ink-700">{lede}</p>
          )}

          {/* Metrics rule */}
          {metrics && metrics.length > 0 && (
            <div className="mt-6 flex items-center gap-4 border-t border-ink-900/10 pt-4">
              {metrics.map((m, i) => (
                <div key={i} className="flex flex-col">
                  <span className="font-display text-xl font-semibold text-ink-900">
                    {m.value}
                  </span>
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-ink-400">
                    {m.label}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

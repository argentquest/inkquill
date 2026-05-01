"use client";

import { useQuery } from "@tanstack/react-query";
import { Activity, AlertTriangle, CheckCircle2, Clock, Loader2 } from "lucide-react";

import { PageHeader } from "@/components/shell/page-header";
import { ErrorState } from "@/components/ui/error-state";
import { fetchCareCircleActivityEvents } from "@/lib/api";

const toneStyles = {
  success: "bg-emerald-100 text-emerald-700",
  info: "bg-sky-100 text-sky-700",
  warning: "bg-amber-100 text-amber-700",
  error: "bg-red-100 text-red-700",
};

function EventIcon({ tone }: { tone: keyof typeof toneStyles }) {
  if (tone === "success") return <CheckCircle2 className="size-5" />;
  if (tone === "warning") return <AlertTriangle className="size-5" />;
  if (tone === "error") return <AlertTriangle className="size-5" />;
  return <Activity className="size-5" />;
}

function formatEventTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "Recently";
  }
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export default function FamilyEventFeedPage() {
  const { data: events, isError, isLoading } = useQuery({
    queryKey: ["care-circle-family-events"],
    queryFn: fetchCareCircleActivityEvents,
  });

  return (
    <div className="space-y-8">
      <PageHeader
        description="Monitor family access, friend profile updates, provider generation, and fallback activity for this care circle."
        eyebrow="Activity Feed"
        title="Family Event Stream"
      />

      {isLoading ? (
        <div className="flex h-32 items-center justify-center">
          <Loader2 className="size-6 animate-spin text-ink-500" />
        </div>
      ) : isError ? (
        <ErrorState title="Activity could not be loaded." detail="Try refreshing the page or checking the backend logs." />
      ) : !events?.length ? (
        <section className="rounded-[28px] border border-black/10 bg-white/70 p-8 text-center shadow-panel">
          <Clock className="mx-auto size-8 text-ink-400" />
          <h2 className="mt-4 text-base font-semibold text-ink-900">No activity yet</h2>
          <p className="mt-2 text-sm leading-6 text-ink-600">New friend profiles, provider runs, and family access changes will appear here.</p>
        </section>
      ) : (
        <section className="rounded-[28px] border border-black/10 bg-white/70 p-6 shadow-panel">
          <ul className="space-y-6" data-testid="care-circle-activity-feed">
            {events.map((event) => (
              <li className="flex gap-4" key={event.id}>
                <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full ${toneStyles[event.tone] ?? toneStyles.info}`}>
                  <EventIcon tone={event.tone} />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="text-sm font-semibold text-ink-900">{event.title}</p>
                    {event.patient_name ? (
                      <span className="rounded-full bg-black/[0.04] px-2 py-0.5 text-xs font-medium text-ink-600">{event.patient_name}</span>
                    ) : null}
                  </div>
                  <p className="mt-1 text-sm leading-6 text-ink-600">{event.description}</p>
                  <p className="mt-1 text-xs text-ink-400">{formatEventTime(event.occurred_at)}</p>
                </div>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

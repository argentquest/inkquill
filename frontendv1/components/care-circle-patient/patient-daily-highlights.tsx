"use client";

import { useEffect, useState } from "react";
import { ThumbsDown, ThumbsUp } from "lucide-react";

import { saveCareCirclePatientProviderFeedback, type CareCirclePatientRecord } from "@/lib/api";

const kindLabels: Record<string, string> = {
  family: "Family",
  memory: "Memory",
  activity: "Activity",
  comfort: "Comfort"
};

type FeedbackValue = "like" | "dislike";

function getSessionFeedbackStorageKey(patientId: string) {
  return `care-circle-patient-feedback-session:${patientId}`;
}

export function PatientDailyHighlights({ patient }: { patient: CareCirclePatientRecord }) {
  const highlights = patient.highlights ?? [];
  const [feedback, setFeedback] = useState<Record<string, FeedbackValue>>({});
  const [pendingProviderKeys, setPendingProviderKeys] = useState<Record<string, boolean>>({});
  const [saveError, setSaveError] = useState<string | null>(null);

  useEffect(() => {
    const apiFeedback = Object.fromEntries(
      highlights
        .filter((highlight) => highlight.feedback === "like" || highlight.feedback === "dislike")
        .map((highlight) => [highlight.providerKey, highlight.feedback as FeedbackValue])
    );

    try {
      const stored = window.sessionStorage.getItem(getSessionFeedbackStorageKey(patient.id));
      const sessionFeedback = stored ? (JSON.parse(stored) as Record<string, FeedbackValue>) : {};
      setFeedback({ ...apiFeedback, ...sessionFeedback });
    } catch {
      setFeedback(apiFeedback);
    }
    setSaveError(null);
  }, [highlights, patient.id]);

  useEffect(() => {
    try {
      window.sessionStorage.setItem(
        getSessionFeedbackStorageKey(patient.id),
        JSON.stringify(feedback),
      );
    } catch {
      // Ignore storage issues and keep the in-memory state.
    }
  }, [feedback, patient.id]);

  async function setProviderFeedback(providerKey: string, value: FeedbackValue) {
    const previousValue = feedback[providerKey];
    const nextValue = previousValue === value ? null : value;

    setFeedback((current) => {
      const next = { ...current };
      if (nextValue) {
        next[providerKey] = nextValue;
      } else {
        delete next[providerKey];
      }
      return next;
    });
    setPendingProviderKeys((current) => ({ ...current, [providerKey]: true }));
    setSaveError(null);

    try {
      await saveCareCirclePatientProviderFeedback(patient.id, providerKey, nextValue);
    } catch (error) {
      setFeedback((current) => {
        const next = { ...current };
        if (previousValue) {
          next[providerKey] = previousValue;
        } else {
          delete next[providerKey];
        }
        return next;
      });
      setSaveError(error instanceof Error ? error.message : "Could not save your feedback.");
    } finally {
      setPendingProviderKeys((current) => {
        const next = { ...current };
        delete next[providerKey];
        return next;
      });
    }
  }

  return (
    <section className="space-y-4">
      {saveError ? (
        <div className="rounded-2xl border border-ember/30 bg-white/90 px-4 py-3 text-sm text-ember">
          {saveError}
        </div>
      ) : null}
      {highlights.map((highlight) => {
        const hasRenderedHtml = Boolean(highlight.renderedHtml);
        const providerFeedback = feedback[highlight.providerKey];
        const isSaving = pendingProviderKeys[highlight.providerKey] === true;

        return (
          <article key={`${highlight.providerKey}-${highlight.displayOrder}`} className="rounded-[32px] border border-black/10 bg-white/88 p-6 shadow-panel md:p-8">
            {!hasRenderedHtml ? (
              <>
                <p className="text-xs uppercase tracking-[0.24em] text-ink-600">{kindLabels[highlight.kind] ?? highlight.kind}</p>
                <h2 className="mt-3 font-display text-3xl text-ink-900 md:text-4xl">{highlight.title}</h2>
              </>
            ) : null}
            {highlight.renderedHtml ? (
              <div
                className={`care-circle-rendered-html text-lg leading-8 text-ink-700 md:text-xl ${hasRenderedHtml ? "" : "mt-4"}`}
                dangerouslySetInnerHTML={{ __html: highlight.renderedHtml }}
              />
            ) : (
              <p className="mt-4 text-lg leading-8 text-ink-700 md:text-xl">{highlight.body}</p>
            )}
            <div className="mt-6 flex items-center gap-3 border-t border-black/10 pt-4">
              <span className="text-xs uppercase tracking-[0.24em] text-ink-500">Was this helpful?</span>
              <button
                aria-label={`Like ${highlight.title}`}
                aria-pressed={providerFeedback === "like"}
                className={[
                  "inline-flex items-center gap-2 rounded-full border px-4 py-2 text-sm font-semibold transition",
                  providerFeedback === "like"
                    ? "border-forest bg-forest text-white"
                    : "border-black/10 bg-white text-ink-900 hover:border-black/20 hover:bg-[#f8f5f0]"
                ].join(" ")}
                disabled={isSaving}
                onClick={() => void setProviderFeedback(highlight.providerKey, "like")}
                title="Like this provider"
                type="button"
              >
                <ThumbsUp className="h-4 w-4" />
                Like
              </button>
              <button
                aria-label={`Dislike ${highlight.title}`}
                aria-pressed={providerFeedback === "dislike"}
                className={[
                  "inline-flex items-center gap-2 rounded-full border px-4 py-2 text-sm font-semibold transition",
                  providerFeedback === "dislike"
                    ? "border-ember bg-ember text-white"
                    : "border-black/10 bg-white text-ink-900 hover:border-black/20 hover:bg-[#f8f5f0]"
                ].join(" ")}
                disabled={isSaving}
                onClick={() => void setProviderFeedback(highlight.providerKey, "dislike")}
                title="Dislike this provider"
                type="button"
              >
                <ThumbsDown className="h-4 w-4" />
                Dislike
              </button>
              {isSaving ? <span className="text-sm text-ink-500">Saving…</span> : null}
            </div>
          </article>
        );
      })}
    </section>
  );
}

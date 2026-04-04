"use client";

import { useEffect, useState } from "react";

import { PageHeader } from "@/components/shell/page-header";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { SettingsFormSection } from "@/components/ui/settings-form-section";
import { fetchInterviewQuestions, fetchInterviewStatus, fetchUserInsights } from "@/lib/api";
import type { InterviewQuestionsPayload, InterviewStatusPayload, UserInsightsPayload } from "@/lib/types";

export function OnboardingDashboardRoute() {
  const [questions, setQuestions] = useState<InterviewQuestionsPayload | null>(null);
  const [status, setStatus] = useState<InterviewStatusPayload | null>(null);
  const [insights, setInsights] = useState<UserInsightsPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [questionsPayload, statusPayload, insightsPayload] = await Promise.all([
          fetchInterviewQuestions("new_user_onboarding"),
          fetchInterviewStatus("new_user_onboarding"),
          fetchUserInsights()
        ]);
        if (mounted) {
          setQuestions(questionsPayload);
          setStatus(statusPayload);
          setInsights(insightsPayload);
        }
      } catch (loadError) {
        if (mounted) {
          setError(loadError instanceof Error ? loadError.message : "Unable to load onboarding data.");
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    void load();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Onboarding"
        title="Set the direction for your writing workspace."
        description="This surface previews the shared onboarding interview and its pending-completion state before deeper storytelling flows depend on personalized insights."
      />
      {loading ? <LoadingState label="Loading onboarding" /> : null}
      {!loading && error ? <ErrorState title="Onboarding data could not be loaded." detail={error} /> : null}
      {!loading && !error && questions && status && insights ? (
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)]">
          <SettingsFormSection
            description={questions.interview_description}
            eyebrow="Interview preview"
            title={questions.interview_title}
          >
            <ol className="space-y-4">
              {questions.questions.map((question) => (
                <li className="rounded-[22px] border border-black/10 bg-black/[0.02] px-4 py-4 text-sm text-ink-800" key={question.id}>
                  <p className="text-xs uppercase tracking-[0.24em] text-ink-600">Question {question.order}</p>
                  <p className="mt-2 font-semibold text-ink-900">{question.question}</p>
                  {question.subtitle ? <p className="mt-2 text-ink-700">{question.subtitle}</p> : null}
                </li>
              ))}
            </ol>
          </SettingsFormSection>
          <SettingsFormSection
            description="The shared platform should surface whether the onboarding interview is complete before app-specific flows rely on the resulting insights."
            eyebrow="Insights"
            title={status.completed ? "Onboarding completed" : "Onboarding still pending"}
          >
            <p className="text-sm leading-7 text-ink-700">
              {insights.has_completed_onboarding ? "Personalized insights are available." : "No personalized insights yet."}
            </p>
          </SettingsFormSection>
        </div>
      ) : null}
    </div>
  );
}

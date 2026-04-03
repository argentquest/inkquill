"use client";

import { useQuery } from "@tanstack/react-query";

import { PageHeader } from "@/components/shell/page-header";
import { DrawerPanel } from "@/components/ui/drawer-panel";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { StatCard } from "@/components/ui/stat-card";
import { fetchInterviewQuestions, fetchInterviewStatus, fetchUserInsights } from "@/lib/api";

const INTERVIEW_ID = "new_user_onboarding";

export default function OnboardingPage() {
  const questionsQuery = useQuery({
    queryKey: ["interview-questions", INTERVIEW_ID],
    queryFn: () => fetchInterviewQuestions(INTERVIEW_ID)
  });
  const statusQuery = useQuery({
    queryKey: ["interview-status", INTERVIEW_ID],
    queryFn: () => fetchInterviewStatus(INTERVIEW_ID)
  });
  const insightsQuery = useQuery({
    queryKey: ["user-insights"],
    queryFn: fetchUserInsights
  });

  if (questionsQuery.isLoading || statusQuery.isLoading || insightsQuery.isLoading) {
    return <LoadingState label="Loading onboarding route" />;
  }

  if (questionsQuery.isError || statusQuery.isError || insightsQuery.isError || !questionsQuery.data || !statusQuery.data || !insightsQuery.data) {
    const firstError = questionsQuery.error ?? statusQuery.error ?? insightsQuery.error;
    return (
      <ErrorState
        detail={firstError instanceof Error ? firstError.message : undefined}
        onRetry={() => {
          void questionsQuery.refetch();
          void statusQuery.refetch();
          void insightsQuery.refetch();
        }}
        retryLabel="Reload onboarding"
        title="Onboarding context could not be loaded."
      />
    );
  }

  const insights = insightsQuery.data.insights;
  const questionPreview = questionsQuery.data.questions.slice(0, 3);

  return (
    <div className="space-y-8">
      <PageHeader
        description="Sprint 3 keeps onboarding deliberately light: a real route, real interview contracts, and enough structure to support later guided flows without dragging the rebuild into full world-building mode."
        eyebrow="Onboarding"
        title={statusQuery.data.completed ? "Your onboarding context is already in place." : "Set the direction for your writing workspace."}
      />

      <section className="grid gap-5 md:grid-cols-3">
        <StatCard label="Interview route" value={questionsQuery.data.interview_id} />
        <StatCard label="Questions" value={String(questionsQuery.data.questions.length)} />
        <StatCard label="Status" value={statusQuery.data.completed ? "Completed" : "Pending"} />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="space-y-6">
          <section className="rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-panel">
            <p className="text-xs uppercase tracking-[0.26em] text-ink-600">Question Preview</p>
            <h2 className="mt-3 font-display text-3xl text-ink-900">{questionsQuery.data.interview_title}</h2>
            <p className="mt-3 text-sm leading-7 text-ink-700">{questionsQuery.data.interview_description}</p>
            <div className="mt-6 space-y-4">
              {questionPreview.map((question) => (
                <article className="rounded-[22px] border border-black/10 bg-paper/70 p-4" key={question.id}>
                  <p className="text-xs uppercase tracking-[0.22em] text-ink-600">Question {question.order}</p>
                  <h3 className="mt-2 text-lg text-ink-900">{question.question}</h3>
                  {question.subtitle ? <p className="mt-2 text-sm text-ink-700">{question.subtitle}</p> : null}
                </article>
              ))}
            </div>
          </section>

          {!insightsQuery.data.has_completed_onboarding ? (
            <EmptyState
              description="The onboarding API is reachable, but the user has not completed the interview yet. This route establishes the shell, status checks, and preview surface before deeper guided UX arrives."
              eyebrow="Pending"
              title="No personalized insights yet."
            />
          ) : null}
        </div>

        <DrawerPanel
          description="Once the interview has been completed, this panel carries the main personalization signals without pushing the route into a full wizard rebuild."
          title="Personalization signals"
        >
          {insights ? (
            <div className="space-y-4 text-sm leading-7 text-ink-800">
              <p><span className="font-semibold">Writing stage:</span> {insights.writing_stage ?? "Not set"}</p>
              <p><span className="font-semibold">Navigation choice:</span> {insights.navigation_choice ?? "Not set"}</p>
              <p><span className="font-semibold">Genres:</span> {insights.preferred_genres?.join(", ") || "Not set"}</p>
              <p><span className="font-semibold">Help needed:</span> {insights.help_needed?.join(", ") || "Not set"}</p>
            </div>
          ) : (
            <p className="text-sm leading-7 text-ink-700">Insights will appear here after the onboarding interview is completed.</p>
          )}
        </DrawerPanel>
      </section>
    </div>
  );
}

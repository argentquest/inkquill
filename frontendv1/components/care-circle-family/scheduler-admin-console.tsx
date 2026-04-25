"use client";

import { useLayoutEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  CalendarClock,
  Clock3,
  ExternalLink,
  PauseCircle,
  PlayCircle,
  RefreshCw,
  ShieldCheck,
} from "lucide-react";

import { useSession, useToasts } from "@/components/providers/app-providers";
import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { StatCard } from "@/components/ui/stat-card";

interface SchedulerHealthResponse {
  status: string;
  scheduler_running: boolean;
  registered_tasks: number;
  scheduled_jobs: number;
}

interface SchedulerTaskStatus {
  key: string;
  name: string;
  cron: string;
  next_run: string | null;
  is_running: boolean;
}

interface SchedulerStatusResponse {
  tasks: SchedulerTaskStatus[];
}

interface SchedulerJobInfo {
  id: string;
  name: string;
  next_run: string | null;
  trigger: string;
}

interface SchedulerJobListResponse {
  jobs: SchedulerJobInfo[];
}

interface SchedulerJobResult {
  success: boolean;
  message: string;
  task_key: string;
}

async function schedulerFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/admin/scheduler/${path}`, {
    credentials: "include",
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    let message = `Request failed: ${response.status} ${response.statusText}`;
    try {
      const payload = (await response.json()) as { detail?: string; message?: string };
      message = payload.detail ?? payload.message ?? message;
    } catch {
      // Ignore JSON parsing issues so we can preserve the fallback message.
    }
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

/**
 * Validate a cron expression with a basic check.
 * A valid cron expression has at least 5 space-separated fields.
 */
function isValidCronExpression(cron: string): boolean {
  const parts = cron.trim().split(/\s+/);
  return parts.length >= 5 && parts.every((part) => /^[\d\-\*,\/]+$/.test(part));
}

const SCHEDULER_REFRESH_INTERVAL_MS = 30_000;

function formatDateTime(value: string | null) {
  if (!value) {
    return "Not scheduled";
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(parsed);
}

export function SchedulerAdminConsole() {
  const session = useSession();
  const { pushToast } = useToasts();
  const queryClient = useQueryClient();
  const [cronInputs, setCronInputs] = useState<Record<string, string>>({});

  const isAdmin = session.user?.is_admin === true;

  useLayoutEffect(() => {
    if (session.status === "anonymous" || session.status === "error") {
      window.location.replace("/auth/login?next=/care-circle-family/admin/scheduler");
    } else if (session.status === "authenticated" && !isAdmin) {
      window.location.replace("/access-denied?surface=care-circle-family");
    }
  }, [isAdmin, session.status]);

  const healthQuery = useQuery({
    queryKey: ["scheduler-admin", "health"],
    queryFn: () => schedulerFetch<SchedulerHealthResponse>("health"),
    enabled: session.status === "authenticated" && isAdmin,
    refetchInterval: SCHEDULER_REFRESH_INTERVAL_MS,
  });

  const statusQuery = useQuery({
    queryKey: ["scheduler-admin", "status"],
    queryFn: () => schedulerFetch<SchedulerStatusResponse>("status"),
    enabled: session.status === "authenticated" && isAdmin,
    refetchInterval: SCHEDULER_REFRESH_INTERVAL_MS,
  });

  const jobsQuery = useQuery({
    queryKey: ["scheduler-admin", "jobs"],
    queryFn: () => schedulerFetch<SchedulerJobListResponse>("jobs"),
    enabled: session.status === "authenticated" && isAdmin,
    refetchInterval: SCHEDULER_REFRESH_INTERVAL_MS,
  });

  const refreshAll = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ["scheduler-admin", "health"] }),
      queryClient.invalidateQueries({ queryKey: ["scheduler-admin", "status"] }),
      queryClient.invalidateQueries({ queryKey: ["scheduler-admin", "jobs"] }),
    ]);
  };

  const operationMutation = useMutation({
    mutationFn: async ({
      taskKey,
      action,
      cron,
    }: {
      taskKey: string;
      action: "run" | "pause" | "resume" | "reschedule";
      cron?: string;
    }) => {
      const body = action === "reschedule" ? JSON.stringify({ cron }) : undefined;
      return schedulerFetch<SchedulerJobResult>(`jobs/${taskKey}/${action}`, {
        method: "POST",
        body,
      });
    },
    onSuccess: async (result, variables) => {
      pushToast({
        title: "Scheduler updated",
        tone: "success",
        detail: result.message ?? `Task ${variables.taskKey} updated successfully.`,
      });
      await refreshAll();
    },
    onError: (error, variables) => {
      pushToast({
        title: "Scheduler action failed",
        tone: "error",
        detail:
          error instanceof Error
            ? error.message
            : `Could not complete ${variables.action} for ${variables.taskKey}.`,
      });
    },
  });

  if (session.status === "loading" || (session.status === "authenticated" && !isAdmin)) {
    return <LoadingState label="Checking admin access" />;
  }

  if (healthQuery.isLoading || statusQuery.isLoading || jobsQuery.isLoading) {
    return <LoadingState label="Loading scheduler console" />;
  }

  const error =
    healthQuery.error instanceof Error
      ? healthQuery.error
      : statusQuery.error instanceof Error
        ? statusQuery.error
        : jobsQuery.error instanceof Error
          ? jobsQuery.error
          : null;

  if (error) {
    return (
      <ErrorState
        title="Scheduler console is unavailable"
        detail={error.message}
        retryLabel="Try again"
        onRetry={() => {
          void refreshAll();
        }}
      />
    );
  }

  const health = healthQuery.data;
  const tasks = statusQuery.data?.tasks ?? [];
  const jobs = jobsQuery.data?.jobs ?? [];

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Administration"
        title="Scheduler Console"
        description="Monitor Care Circle background jobs from the same admin shell your team already uses. Inspect task health, manually run jobs, and update cron schedules without leaving the main application."
        action={
          <div className="flex items-center gap-2 rounded-full border border-amber-200 bg-amber-50 px-4 py-2 text-sm font-semibold text-amber-800">
            <ShieldCheck className="h-4 w-4" />
            Admin only
          </div>
        }
      />

      <div className="grid gap-4 md:grid-cols-3">
        <StatCard
          label="Service"
          value={health?.scheduler_running ? "Running" : "Offline"}
          detail={health?.status === "healthy" ? "Scheduler heartbeat looks healthy." : "The scheduler API reported an unhealthy state."}
        />
        <StatCard
          label="Registered Tasks"
          value={health?.registered_tasks ?? 0}
          detail="Tasks discovered from the scheduler registry at startup."
        />
        <StatCard
          label="Scheduled Jobs"
          value={health?.scheduled_jobs ?? 0}
          detail="Jobs currently loaded in APScheduler and persisted in PostgreSQL."
        />
      </div>

      <section className="rounded-[28px] border border-black/10 bg-white/75 p-6 shadow-panel">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-ink-600">Live Controls</p>
            <h2 className="mt-2 font-display text-3xl text-ink-900">Task schedule</h2>
            <p className="mt-2 max-w-3xl text-sm leading-7 text-ink-700">
              Each card reflects the registered task key, its default cron, and whether APScheduler currently has an active job loaded.
            </p>
          </div>
          <Button
            variant="secondary"
            className="gap-2"
            onClick={() => {
              void refreshAll();
            }}
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
        </div>

        {tasks.length === 0 ? (
          <div className="mt-6">
            <EmptyState
              eyebrow="No tasks"
              title="The scheduler registry is empty"
              description="No schedulable tasks were returned by the service. Check startup logs to confirm the task modules were imported."
            />
          </div>
        ) : (
          <div className="mt-6 grid gap-4 xl:grid-cols-2">
            {tasks.map((task) => {
              const isBusy =
                operationMutation.isPending && operationMutation.variables?.taskKey === task.key;
              const cronValue = cronInputs[task.key] ?? task.cron;

              return (
                <article
                  key={task.key}
                  className="rounded-[24px] border border-black/10 bg-paper/65 p-5 shadow-sm"
                >
                  <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                    <div>
                      <div className="flex items-center gap-2 text-xs uppercase tracking-[0.26em] text-ink-500">
                        <CalendarClock className="h-3.5 w-3.5" />
                        {task.key}
                      </div>
                      <h3 className="mt-2 text-xl font-semibold text-ink-900">{task.name}</h3>
                      <div className="mt-3 flex flex-wrap gap-2 text-sm text-ink-700">
                        <span className="rounded-full border border-black/10 bg-white/85 px-3 py-1">
                          Cron: <span className="font-mono">{task.cron}</span>
                        </span>
                        <span className="rounded-full border border-black/10 bg-white/85 px-3 py-1">
                          {task.is_running ? "Scheduled" : "Paused or missing"}
                        </span>
                      </div>
                    </div>
                    <div className="rounded-2xl border border-black/10 bg-white/80 px-4 py-3 text-sm text-ink-700">
                      <div className="flex items-center gap-2 font-semibold text-ink-900">
                        <Clock3 className="h-4 w-4 text-ember" />
                        Next run
                      </div>
                      <p className="mt-2 leading-6">{formatDateTime(task.next_run)}</p>
                    </div>
                  </div>

                  <div className="mt-5 flex flex-wrap gap-2">
                    <Button
                      className="gap-2"
                      disabled={isBusy}
                      onClick={() => {
                        operationMutation.mutate({ taskKey: task.key, action: "run" });
                      }}
                    >
                      <PlayCircle className="h-4 w-4" />
                      Run now
                    </Button>
                    <Button
                      variant="secondary"
                      className="gap-2"
                      disabled={isBusy || !task.is_running}
                      onClick={() => {
                        operationMutation.mutate({ taskKey: task.key, action: "pause" });
                      }}
                    >
                      <PauseCircle className="h-4 w-4" />
                      Pause
                    </Button>
                    <Button
                      variant="secondary"
                      className="gap-2"
                      disabled={isBusy || task.is_running}
                      onClick={() => {
                        operationMutation.mutate({ taskKey: task.key, action: "resume" });
                      }}
                    >
                      <PlayCircle className="h-4 w-4" />
                      Resume
                    </Button>
                  </div>

                  <div className="mt-5 rounded-[22px] border border-black/10 bg-white/85 p-4">
                    <div className="flex items-center justify-between">
                      <label className="text-xs font-semibold uppercase tracking-[0.24em] text-ink-600" htmlFor={`cron-${task.key}`}>
                        Custom cron
                      </label>
                      <a
                        href="https://crontab.guru"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-xs text-ink-500 transition hover:text-ink-700"
                        title="Cron expression helper"
                      >
                        <ExternalLink className="h-3 w-3" />
                        crontab.guru
                      </a>
                    </div>
                    <p className="mt-1 text-xs text-ink-500">
                      Format: <span className="font-mono">minute hour day month weekday</span> (e.g. <span className="font-mono">0 8 * * *</span> for 8:00 AM daily)
                    </p>
                    <div className="mt-3 flex flex-col gap-3 md:flex-row">
                      <input
                        id={`cron-${task.key}`}
                        value={cronValue}
                        onChange={(event) => {
                          setCronInputs((current) => ({
                            ...current,
                            [task.key]: event.target.value,
                          }));
                        }}
                        className="w-full rounded-full border border-black/10 bg-paper px-4 py-3 font-mono text-sm text-ink-900 outline-none transition focus:border-forest/50 focus:ring-2 focus:ring-forest/15"
                      />
                      <Button
                        variant="secondary"
                        disabled={isBusy || !isValidCronExpression(cronValue) || cronValue === task.cron}
                        onClick={() => {
                          operationMutation.mutate({
                            taskKey: task.key,
                            action: "reschedule",
                            cron: cronValue.trim(),
                          });
                        }}
                      >
                        Save cron
                      </Button>
                    </div>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>

      <section className="rounded-[28px] border border-black/10 bg-white/75 p-6 shadow-panel">
        <p className="text-xs uppercase tracking-[0.28em] text-ink-600">APScheduler</p>
        <h2 className="mt-2 font-display text-3xl text-ink-900">Loaded jobs</h2>
        <p className="mt-2 max-w-3xl text-sm leading-7 text-ink-700">
          These are the concrete jobs currently loaded by the scheduler, including trigger text returned by APScheduler.
        </p>

        {jobs.length === 0 ? (
          <div className="mt-6">
            <EmptyState
              eyebrow="No jobs"
              title="No APScheduler jobs are loaded"
              description="If tasks are registered but no jobs appear here, confirm the scheduler service completed startup and that the job store is reachable."
            />
          </div>
        ) : (
          <div className="mt-6 overflow-hidden rounded-[24px] border border-black/10">
            <table className="min-w-full divide-y divide-black/10 text-left text-sm">
              <thead className="bg-ink-900/5 text-ink-700">
                <tr>
                  <th className="px-4 py-3 font-semibold">Job</th>
                  <th className="px-4 py-3 font-semibold">Name</th>
                  <th className="px-4 py-3 font-semibold">Next run</th>
                  <th className="px-4 py-3 font-semibold">Trigger</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-black/10 bg-white/80">
                {jobs.map((job) => (
                  <tr key={job.id}>
                    <td className="px-4 py-3 font-mono text-xs text-ink-700">{job.id}</td>
                    <td className="px-4 py-3 text-ink-900">{job.name}</td>
                    <td className="px-4 py-3 text-ink-700">{formatDateTime(job.next_run)}</td>
                    <td className="px-4 py-3 font-mono text-xs text-ink-600">{job.trigger}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

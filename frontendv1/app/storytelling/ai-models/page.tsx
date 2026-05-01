"use client";

import { useQuery } from "@tanstack/react-query";
import { Brain, Loader2 } from "lucide-react";

import { PageHeader } from "@/components/shell/page-header";
import { ErrorState } from "@/components/ui/error-state";
import { fetchLLMModels, type LLMModelEntry } from "@/lib/api";

function usdPmToDisplay(usdPm: number): string {
  if (usdPm === 0) return "Free";
  if (usdPm < 0.01) return `$${(usdPm * 1000).toFixed(2)}/Mtoken`;
  return `$${usdPm.toFixed(4)}/Mtoken`;
}

function ModelCard({ model }: { model: LLMModelEntry }) {
  return (
    <article
      className={`rounded-2xl border p-5 shadow-sm ${model.is_active ? "border-black/10 bg-white/80" : "border-black/5 bg-white/40 opacity-60"}`}
      data-testid="model-card"
    >
      <div className="flex items-start gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-paper text-ink-400">
          <Brain className="size-5" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-sm font-semibold text-ink-900">{model.display_name}</h3>
            <span className="rounded-full bg-black/[0.05] px-2 py-0.5 text-xs font-medium text-ink-600">
              {model.provider}
            </span>
            {!model.is_active ? (
              <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs text-amber-700">Inactive</span>
            ) : null}
          </div>
          <p className="mt-1 text-xs text-ink-500 font-mono">{model.model_name}</p>
          {model.description ? (
            <p className="mt-2 text-sm text-ink-600">{model.description}</p>
          ) : null}
          <div className="mt-3 flex flex-wrap gap-4 text-xs text-ink-500">
            <span>
              <span className="font-medium text-ink-700">Type:</span> {model.model_type}
            </span>
            <span>
              <span className="font-medium text-ink-700">Max tokens:</span>{" "}
              {model.max_tokens.toLocaleString()}
            </span>
            <span>
              <span className="font-medium text-ink-700">Input:</span>{" "}
              {usdPmToDisplay(model.user_price_input_usd_pm)}
            </span>
            <span>
              <span className="font-medium text-ink-700">Output:</span>{" "}
              {usdPmToDisplay(model.user_price_output_usd_pm)}
            </span>
          </div>
        </div>
      </div>
    </article>
  );
}

export default function AIModelsPage() {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["llm-models"],
    queryFn: fetchLLMModels,
  });

  const models = data?.models ?? [];
  const activeModels = models.filter((m) => m.is_active);
  const inactiveModels = models.filter((m) => !m.is_active);

  return (
    <div className="space-y-8">
      <PageHeader
        description="AI models available for story generation, scene writing, and world building."
        eyebrow="Storytelling"
        title="AI Models"
      />

      {isLoading ? (
        <div className="flex h-32 items-center justify-center">
          <Loader2 className="size-6 animate-spin text-ink-500" />
        </div>
      ) : isError ? (
        <ErrorState
          detail={error instanceof Error ? error.message : "Try refreshing the page."}
          onRetry={() => void refetch()}
          retryLabel="Reload models"
          title="AI models could not be loaded."
        />
      ) : models.length === 0 ? (
        <div
          className="flex flex-col items-center justify-center rounded-[28px] border-2 border-dashed border-black/10 bg-white/50 p-12 text-center shadow-sm"
          data-testid="models-empty-state"
        >
          <Brain className="size-8 text-ink-400" />
          <p className="mt-3 text-sm font-medium text-ink-700">No AI models configured</p>
          <p className="mt-1 text-sm text-ink-500">Contact your administrator to add AI model configurations.</p>
        </div>
      ) : (
        <div className="space-y-10">
          {data ? (
            <div className="flex flex-wrap gap-6 text-sm text-ink-600" data-testid="models-summary">
              <span><span className="font-semibold text-ink-900">{data.total_count}</span> total</span>
              <span><span className="font-semibold text-ink-900">{data.active_count}</span> active</span>
              {data.providers.length > 0 ? (
                <span>Providers: {data.providers.join(", ")}</span>
              ) : null}
            </div>
          ) : null}

          {activeModels.length > 0 ? (
            <section className="space-y-4">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-500">Active models</h2>
              <div className="space-y-3" data-testid="active-models-list">
                {activeModels.map((m) => (
                  <ModelCard key={m.id} model={m} />
                ))}
              </div>
            </section>
          ) : null}

          {inactiveModels.length > 0 ? (
            <section className="space-y-4">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-500">Inactive models</h2>
              <div className="space-y-3" data-testid="inactive-models-list">
                {inactiveModels.map((m) => (
                  <ModelCard key={m.id} model={m} />
                ))}
              </div>
            </section>
          ) : null}
        </div>
      )}
    </div>
  );
}

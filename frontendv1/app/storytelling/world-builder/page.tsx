"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Loader2, Sparkles, Wand2, ArrowRight, CheckCircle } from "lucide-react";

import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ErrorState } from "@/components/ui/error-state";
import {
  fetchWorldBuilderQuestions,
  generateWorldBuilderWorld,
  createWorldFromBuilder,
} from "@/lib/api";

type Step = "questions" | "generating" | "review" | "creating" | "done";

export default function WorldBuilderPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("questions");
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [generated, setGenerated] = useState<{
    short_description: string;
    description: string;
    visual_prompt: string;
    answer_summary: Array<Record<string, string>>;
  } | null>(null);
  const [worldName, setWorldName] = useState("");
  const [createdWorldId, setCreatedWorldId] = useState<number | null>(null);

  const { data: questions, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["world-builder-questions"],
    queryFn: fetchWorldBuilderQuestions,
  });

  const generateMutation = useMutation({
    mutationFn: () => generateWorldBuilderWorld(answers),
    onSuccess: (data) => {
      setGenerated(data);
      setStep("review");
    },
    onError: () => {
      setStep("questions");
    },
  });

  const createMutation = useMutation({
    mutationFn: () => createWorldFromBuilder({ name: worldName, answers }),
    onSuccess: (data) => {
      setCreatedWorldId(data.id);
      setStep("done");
    },
  });

  function toggleAnswer(questionId: number, answerId: number) {
    setAnswers((prev) => ({ ...prev, [questionId]: answerId }));
  }

  function allAnswered() {
    if (!questions) return false;
    return questions.every((q) => answers[q.id] !== undefined);
  }

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Loader2 className="size-6 animate-spin text-ink-500" />
      </div>
    );
  }

  if (isError || !questions) {
    return (
      <ErrorState
        detail={error instanceof Error ? error.message : "Try refreshing."}
        onRetry={() => void refetch()}
        retryLabel="Reload questions"
        title="World builder could not be loaded."
      />
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="World Builder"
        title="Build a World"
        description="Answer a few questions and let AI generate your world."
      />

      {step === "questions" && (
        <div className="mx-auto max-w-2xl space-y-8">
          {questions.map((q, idx) => (
            <div key={q.id} className="space-y-3">
              <div className="flex items-start gap-3">
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-ink-900 text-xs font-semibold text-white">
                  {idx + 1}
                </span>
                <div>
                  <h3 className="font-medium text-ink-900">{q.full_question}</h3>
                </div>
              </div>
              <div className="grid gap-2 pl-9 sm:grid-cols-2">
                {q.answers.map((a: any) => (
                  <button
                    key={a.id}
                    onClick={() => toggleAnswer(q.id, a.id)}
                    className={`rounded-xl border px-4 py-3 text-left text-sm transition ${
                      answers[q.id] === a.id
                        ? "border-ink-500 bg-ink-900 text-white shadow-panel"
                        : "border-black/10 bg-white/70 text-ink-700 hover:bg-white"
                    }`}
                  >
                    {a.text}
                  </button>
                ))}
              </div>
            </div>
          ))}

          <div className="flex justify-end pt-4">
            <Button
              className="gap-2"
              disabled={!allAnswered() || generateMutation.isPending}
              onClick={() => {
                setStep("generating");
                generateMutation.mutate();
              }}
            >
              {generateMutation.isPending && <Loader2 className="size-4 animate-spin" />}
              <Wand2 className="size-4" />
              Generate world
            </Button>
          </div>
        </div>
      )}

      {step === "generating" && (
        <div className="flex h-64 flex-col items-center justify-center gap-4">
          <Loader2 className="size-8 animate-spin text-ink-500" />
          <p className="text-sm text-ink-600">Crafting your world with AI…</p>
        </div>
      )}

      {step === "review" && generated && (
        <div className="mx-auto max-w-2xl space-y-6">
          <div className="space-y-2 rounded-2xl border border-black/10 bg-white/70 p-6 shadow-panel">
            <h3 className="text-lg font-semibold text-ink-900">Generated world</h3>
            <p className="text-sm font-medium text-ink-700">Short description</p>
            <p className="text-sm text-ink-600">{generated.short_description}</p>
            <p className="text-sm font-medium text-ink-700">Long description</p>
            <p className="text-sm leading-relaxed text-ink-600">{generated.description}</p>
            <p className="text-sm font-medium text-ink-700">Visual prompt</p>
            <p className="text-sm italic text-ink-500">{generated.visual_prompt}</p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="world-name">World name *</Label>
            <Input
              id="world-name"
              placeholder="Enter a name for your world…"
              value={worldName}
              onChange={(e) => setWorldName(e.target.value)}
            />
          </div>

          {createMutation.isError && (
            <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {createMutation.error instanceof Error ? createMutation.error.message : "Failed to create world."}
            </div>
          )}

          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={() => setStep("questions")}>
              Back to answers
            </Button>
            <Button
              className="gap-2"
              disabled={!worldName.trim() || createMutation.isPending}
              onClick={() => createMutation.mutate()}
            >
              {createMutation.isPending && <Loader2 className="size-4 animate-spin" />}
              <Sparkles className="size-4" />
              Create world
            </Button>
          </div>
        </div>
      )}

      {step === "done" && createdWorldId && (
        <div className="mx-auto max-w-md space-y-6 text-center">
          <CheckCircle className="mx-auto size-12 text-green-600" />
          <h3 className="text-xl font-semibold text-ink-900">World created!</h3>
          <p className="text-sm text-ink-600">Your new world is ready to explore.</p>
          <Button className="gap-2" onClick={() => router.push(`/storytelling/worlds/${createdWorldId}`)}>
            <ArrowRight className="size-4" />
            Go to world
          </Button>
        </div>
      )}
    </div>
  );
}

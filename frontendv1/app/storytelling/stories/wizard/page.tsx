"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { ArrowLeft, ArrowRight, Loader2, Sparkles, Wand2 } from "lucide-react";
import Link from "next/link";

import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { TextField } from "@/components/ui/text-field";
import { createStory } from "@/lib/api";

export default function StoryWizardPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [title, setTitle] = useState("");
  const [concept, setConcept] = useState("");
  const [genre, setGenre] = useState("");
  const [tone, setTone] = useState("");
  const [conflict, setConflict] = useState("");
  const [error, setError] = useState("");

  const createMutation = useMutation({
    mutationFn: () =>
      createStory({
        title: title.trim(),
        short_description: concept.trim() || null,
        story_genre: genre.trim() || null,
        story_tone: tone.trim() || null,
        primary_conflict_type: conflict.trim() || null,
        story_type: "advanced",
      }),
    onSuccess: (data) => {
      router.push(`/storytelling/stories/${data.id}`);
    },
    onError: (err: Error) => setError(err.message),
  });

  const canProceed =
    step === 1 ? concept.trim().length > 0 : step === 2 ? genre.trim().length > 0 : title.trim().length > 0;

  const handleNext = () => {
    setError("");
    if (step < 3) setStep(step + 1);
    else createMutation.mutate();
  };

  const handleBack = () => {
    if (step > 1) setStep(step - 1);
  };

  return (
    <div className="space-y-8">
      <PageHeader
        description="Answer a few questions and we'll set up your story world."
        eyebrow="Story Wizard"
        title="Guided Story Creation"
        action={
          <Link href="/storytelling/stories">
            <Button className="gap-2" variant="secondary">
              <ArrowLeft className="size-4" />
              Back
            </Button>
          </Link>
        }
      />

      <div className="mx-auto max-w-2xl space-y-6 rounded-[28px] border border-black/10 bg-white/80 p-8 shadow-panel">
        {/* Stepper */}
        <div className="flex items-center gap-2">
          {[1, 2, 3].map((s) => (
            <div key={s} className="flex items-center gap-2">
              <div
                className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold ${
                  s === step ? "bg-forest text-white" : s < step ? "bg-forest/20 text-forest" : "bg-black/5 text-ink-400"
                }`}
              >
                {s < step ? "✓" : s}
              </div>
              {s < 3 && <div className={`h-0.5 w-8 ${s < step ? "bg-forest/40" : "bg-black/5"}`} />}
            </div>
          ))}
        </div>

        {error ? (
          <div className="rounded-[20px] border border-[#c65353]/30 bg-ember/10 px-4 py-3 text-sm text-ember">
            {error}
          </div>
        ) : null}

        {step === 1 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-forest">
              <Sparkles className="size-5" />
              <h2 className="text-base font-semibold">What is your story about?</h2>
            </div>
            <p className="text-sm text-ink-600">
              Describe the core idea, main character, or premise in a sentence or two.
            </p>
            <textarea
              className="min-h-[140px] w-full rounded-[20px] border border-black/10 bg-white/85 px-4 py-3 text-sm text-ink-900 outline-none transition placeholder:text-ink-500 focus:border-ink-400 focus:ring-2 focus:ring-ink-200"
              placeholder="A reluctant blacksmith discovers she is the last heir to a fallen kingdom..."
              value={concept}
              onChange={(e) => setConcept(e.target.value)}
            />
          </div>
        )}

        {step === 2 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-forest">
              <Wand2 className="size-5" />
              <h2 className="text-base font-semibold">Set the mood</h2>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <TextField
                label="Genre"
                placeholder="e.g. Fantasy Adventure"
                value={genre}
                onChange={(e) => setGenre(e.target.value)}
              />
              <TextField
                label="Tone"
                placeholder="e.g. Dark, Hopeful"
                value={tone}
                onChange={(e) => setTone(e.target.value)}
              />
            </div>
            <TextField
              label="Primary Conflict"
              placeholder="e.g. Character vs. Self"
              value={conflict}
              onChange={(e) => setConflict(e.target.value)}
            />
          </div>
        )}

        {step === 3 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-forest">
              <Sparkles className="size-5" />
              <h2 className="text-base font-semibold">Give it a title</h2>
            </div>
            <TextField
              label="Story Title"
              placeholder="Enter your story title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
            <div className="rounded-[16px] bg-paper p-4 text-sm text-ink-700">
              <p className="font-semibold">Preview</p>
              <p className="mt-1">{title || "Untitled Story"}</p>
              {genre ? <p className="mt-1 text-xs text-ink-500">{genre} · {tone || "No tone set"}</p> : null}
            </div>
          </div>
        )}

        <div className="flex items-center justify-between pt-2">
          <Button variant="secondary" onClick={handleBack} disabled={step === 1}>
            Back
          </Button>
          <Button onClick={handleNext} disabled={!canProceed || createMutation.isPending}>
            {createMutation.isPending ? (
              <Loader2 className="size-4 animate-spin" />
            ) : step === 3 ? (
              "Create story"
            ) : (
              <>
                Next <ArrowRight className="size-4" />
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}

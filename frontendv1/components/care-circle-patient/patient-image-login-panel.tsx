"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { fetchCareCirclePatientAuthCatalog, loginCareCirclePatient } from "@/lib/api";

const accentByKey: Record<string, string> = {
  sun: "#e09f3e",
  dog: "#5c946e",
  flower: "#cf6f91",
  cake: "#d27d46",
  bird: "#4a84b8",
  car: "#7f658c",
  tree: "#56835a",
  house: "#9c6b52",
  moon: "#6b78b8",
  star: "#b78c35",
  boat: "#3e7f9f",
  hat: "#91674f"
};

export function PatientImageLoginPanel() {
  const router = useRouter();
  const [selectedKeys, setSelectedKeys] = useState<string[]>([]);
  const [error, setError] = useState("");
  const { data: catalog, isLoading, isError, error: queryError } = useQuery({
    queryKey: ["care-circle-patient-auth-catalog"],
    queryFn: fetchCareCirclePatientAuthCatalog,
  });

  const loginMutation = useMutation({
    mutationFn: () => loginCareCirclePatient(selectedKeys),
    onSuccess: (patient) => {
      router.push(`/care-circle-patient/home?patient=${patient.id}`);
    },
    onError: (mutationError) => {
      setError(mutationError instanceof Error ? mutationError.message : "Patient sign-in failed.");
      setSelectedKeys([]);
    }
  });

  const toggleKey = (key: string) => {
    setSelectedKeys((current) => {
      if (current.includes(key)) {
        return current.filter((value) => value !== key);
      }
      if (current.length >= 3) {
        return current;
      }
      return [...current, key];
    });
    setError("");
  };

  if (isLoading) {
    return <LoadingState label="Loading sign-in pictures" />;
  }

  if (isError || !catalog) {
    return <ErrorState detail={queryError instanceof Error ? queryError.message : "Could not load the patient sign-in catalog."} title="Sign-in unavailable" />;
  }

  return (
    <section className="rounded-[32px] border border-black/10 bg-white/82 p-6 shadow-panel md:p-8">
      <div className="max-w-2xl">
        <p className="text-xs uppercase tracking-[0.32em] text-ink-600">Patient sign-in</p>
        <h2 className="mt-3 font-display text-3xl text-ink-900 md:text-4xl">Choose the 3 pictures that belong to you.</h2>
        <p className="mt-4 text-base leading-8 text-ink-700">
          This direct-entry flow is imported from the DailyNewsletter picture sign-in pattern and adapted for the care-circle
          patient surface.
        </p>
      </div>

      <p className="mt-6 text-sm font-semibold text-ink-700">
        {selectedKeys.length === 0 ? "No pictures selected yet." : `${selectedKeys.length} of 3 selected`}
      </p>
      {error ? <p className="mt-3 text-sm font-semibold text-[#a63c27]">{error}</p> : null}

      <div className="mt-6 grid grid-cols-2 gap-3 md:grid-cols-4">
        {catalog.map((item) => {
          const selected = selectedKeys.includes(item.key);
          return (
            <button
              key={item.key}
              aria-label={item.label}
              aria-pressed={selected}
              className="grid min-h-28 place-items-center rounded-[24px] border bg-[#fffdf9] p-4 text-center transition hover:border-black/20"
              onClick={() => toggleKey(item.key)}
              style={{
                borderColor: selected ? accentByKey[item.key] ?? "#231913" : "rgba(35, 25, 19, 0.12)",
                borderWidth: selected ? 3 : 1
              }}
              type="button"
            >
              <span className="text-4xl">{item.emoji}</span>
              <span className="mt-2 text-sm font-semibold text-ink-900">{item.label}</span>
            </button>
          );
        })}
      </div>

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <Button disabled={selectedKeys.length !== 3 || loginMutation.isPending} onClick={() => loginMutation.mutate()}>
          {loginMutation.isPending ? "Checking..." : "Continue"}
        </Button>
        <Button
          disabled={selectedKeys.length === 0}
          onClick={() => {
            setSelectedKeys([]);
            setError("");
          }}
          variant="secondary"
        >
          Clear selection
        </Button>
      </div>
    </section>
  );
}

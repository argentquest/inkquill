"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createCareCirclePatient } from "@/lib/api";
import { LoadingState } from "@/components/ui/loading-state";

export default function NewPatientPage() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: createCareCirclePatient,
    onSuccess: (newPatient) => {
      queryClient.invalidateQueries({ queryKey: ["care-circle-family-patients"] });
      // Redirect to edit page with edit=1 as requested
      router.push(`/care-circle-family/patients/${newPatient.id}?edit=1`);
    },
    onError: (error) => {
      console.error("Failed to create patient:", error);
      alert("Failed to create new friend. Please try again.");
    },
  });

  useEffect(() => {
    // Auto-create a minimal patient record and redirect to edit
    const defaultPatient = {
      displayName: "New Friend",
      familyName: "New Family",
      stage: "moderate" as const,
      accessState: "active" as const,
      timezone: "America/Chicago",
      deliveryTime: "09:00",
      preferences: [],
    };

    createMutation.mutate(defaultPatient);
  }, [createMutation]);

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <LoadingState label="Creating new friend profile and generating login icons..." />
    </div>
  );
}

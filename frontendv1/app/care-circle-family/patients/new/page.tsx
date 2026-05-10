"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createCareCirclePatient } from "@/lib/api";
import { LoadingState } from "@/components/ui/loading-state";

export default function NewPatientPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const didCreate = useRef(false);

  const createMutation = useMutation({
    mutationFn: createCareCirclePatient,
    onSuccess: (newPatient) => {
      queryClient.invalidateQueries({ queryKey: ["care-circle-family-patients"] });
      router.push(`/care-circle-family/patients/${newPatient.id}?edit=1`);
    },
    onError: (error) => {
      console.error("Failed to create patient:", error);
      alert("Failed to create new friend. Please try again.");
    },
  });

  useEffect(() => {
    if (didCreate.current) return;
    didCreate.current = true;

    createMutation.mutate({
      displayName: "New Friend",
      familyName: "New Family",
      stage: "moderate",
      careMode: "memory_care",
      accessState: "active",
      timezone: "America/Chicago",
      deliveryTime: "09:00",
      preferences: [],
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <LoadingState label="Creating new friend profile and generating login icons..." />
    </div>
  );
}

"use client";

import { useQuery } from "@tanstack/react-query";

import { PatientDailyHighlights } from "@/components/care-circle-patient/patient-daily-highlights";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { fetchCareCirclePatientSession } from "@/lib/api";

export function PatientSessionClient({ patientId }: { patientId: string }) {
  const { data: patient, isLoading, isError, error } = useQuery({
    queryKey: ["care-circle-patient-session", patientId],
    queryFn: () => fetchCareCirclePatientSession(patientId),
  });

  if (isLoading) {
    return <LoadingState label="Preparing your day" />;
  }

  if (isError || !patient) {
    return <ErrorState detail={error instanceof Error ? error.message : "Could not load the friend session."} title="Daily session unavailable" />;
  }

  return <PatientDailyHighlights patient={patient} />;
}

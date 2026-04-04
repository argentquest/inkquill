"use client";

import { useQuery } from "@tanstack/react-query";

import { FamilyPatientCard } from "@/components/care-circle-family/family-patient-card";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { fetchCareCirclePatients } from "@/lib/api";

export function FamilyPatientsClient() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["care-circle-family-patients"],
    queryFn: fetchCareCirclePatients,
  });

  if (isLoading) {
    return <LoadingState label="Loading patient profiles" />;
  }

  if (isError) {
    return <ErrorState detail={error instanceof Error ? error.message : "Could not load patient profiles."} title="Patient profiles unavailable" />;
  }

  return (
    <section className="grid gap-6">
      {data?.map((patient) => <FamilyPatientCard key={patient.id} patient={patient} />)}
    </section>
  );
}

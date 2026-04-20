"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

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
    <div className="space-y-8">
      {/* New Patient Button */}
      <div className="flex justify-end">
        <Link
          href="/care-circle-family/patients/new"
          className="inline-flex items-center gap-2 rounded-full bg-black px-6 py-3 text-sm font-semibold text-white hover:bg-gray-800 transition-colors"
        >
          + New Patient
        </Link>
      </div>

      <section className="grid gap-6">
        {data?.map((patient) => (
          <FamilyPatientCard key={patient.id} patient={patient} />
        ))}
      </section>

      {data?.length === 0 && (
        <div className="text-center py-16 border border-dashed border-gray-300 rounded-3xl">
          <p className="text-gray-500">No patients yet.</p>
          <p className="text-sm text-gray-400 mt-2">
            Click "New Patient" to create your first care circle profile.
          </p>
        </div>
      )}
    </div>
  );
}

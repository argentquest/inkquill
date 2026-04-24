"use client";

import { useMutation, useQueries, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { Loader2, ArrowLeft } from "lucide-react";
import Link from "next/link";

import {
  fetchCareCirclePatientProviderConfigs,
  fetchCareCirclePatients,
  fetchCareCircleProviders,
  updateCareCirclePatientProviderConfig,
} from "@/lib/api";
import { useSession } from "@/components/providers/app-providers";
import { PageHeader } from "@/components/shell/page-header";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";

export default function ProviderDetailPage() {
  const params = useParams();
  const providerKey = params?.providerKey as string;
  const queryClient = useQueryClient();
  const session = useSession();
  const isOwner = session.user?.is_family_owner === true;

  const { data: providers, isLoading, isError } = useQuery({
    queryKey: ["care-circle", "providers"],
    queryFn: fetchCareCircleProviders
  });
  const {
    data: patients,
    isLoading: isLoadingPatients,
    isError: isPatientsError,
    error: patientsError,
  } = useQuery({
    queryKey: ["care-circle-family-patients"],
    queryFn: fetchCareCirclePatients,
  });

  const providerConfigQueries = useQueries({
    queries: (patients ?? []).map((patient) => ({
      queryKey: ["care-circle-family-patient-provider-configs", patient.id],
      queryFn: () => fetchCareCirclePatientProviderConfigs(patient.id),
      enabled: Boolean(patient.id),
    })),
  });

  const updateMutation = useMutation({
    mutationFn: (input: { patientId: string; isEnabled: boolean }) =>
      updateCareCirclePatientProviderConfig(input.patientId, providerKey, {
        is_enabled: input.isEnabled,
        custom_parameters: {},
      }),
    onSuccess: (_result, input) => {
      queryClient.invalidateQueries({
        queryKey: ["care-circle-family-patient-provider-configs", input.patientId],
      });
    },
  });

  const provider = providers?.find((p) => p.providerKey === providerKey);
  const isLoadingConfigs = providerConfigQueries.some((query) => query.isLoading);
  const configErrorQuery = providerConfigQueries.find((query) => query.isError);

  if (isLoading) {
    return (
      <div className="flex h-32 items-center justify-center">
        <Loader2 className="size-6 animate-spin text-ink-500" />
      </div>
    );
  }

  if (isLoadingPatients) {
    return <LoadingState label="Loading provider diagnostics" />;
  }

  if (isError || !provider) {
    return (
      <div className="space-y-6">
        <Link 
          className="inline-flex items-center gap-2 text-sm font-semibold text-ink-500 hover:text-ink-900" 
          href="/care-circle-family/providers"
        >
          <ArrowLeft className="size-4" />
          Back to Providers
        </Link>
        <div className="rounded-[28px] border border-red-200 bg-red-50 p-6 shadow-panel">
          <p className="text-sm font-semibold text-red-800">
            {isError ? "Failed to load provider data." : "Provider not found."}
          </p>
        </div>
      </div>
    );
  }

  if (isPatientsError) {
    return (
      <ErrorState
        detail={patientsError instanceof Error ? patientsError.message : "Could not load family friends."}
        title="Provider diagnostics unavailable"
      />
    );
  }

  if (configErrorQuery?.error) {
    return (
      <ErrorState
        detail={configErrorQuery.error instanceof Error ? configErrorQuery.error.message : "Could not load provider mappings."}
        title="Provider diagnostics unavailable"
      />
    );
  }

  const canReachPatientHome = provider.enabled && provider.patientVisible;

  return (
    <div className="space-y-8">
      <Link 
        className="inline-flex items-center gap-2 text-sm font-semibold text-ink-500 hover:text-ink-900" 
        href="/care-circle-family/providers"
      >
        <ArrowLeft className="size-4" />
        Back to Providers
      </Link>
      
      <PageHeader
        description={`Manage operational parameters and visibility testing for the ${provider.label} provider output.`}
        eyebrow="Provider Details"
        title={`${provider.icon || "📰"} ${provider.label}`}
      />

      <div className="flex flex-wrap gap-3">
        <Link
          className="inline-flex items-center rounded-full border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-ink-900 transition hover:border-black/20"
          href={`/care-circle-family/admin/template-studio?provider=${provider.providerKey}&theme=classic`}
        >
          Open template studio
        </Link>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <section className="rounded-[28px] border border-black/10 bg-white/70 p-6 shadow-panel text-sm">
          <h3 className="text-base font-bold text-ink-900">Provider Specifications</h3>
          <ul className="mt-4 space-y-4 text-ink-700">
            <li className="flex justify-between border-b pb-2">
              <span className="font-semibold text-ink-900">Technical Key</span>
              <span className="font-mono text-xs">{provider.providerKey}</span>
            </li>
            <li className="flex justify-between border-b pb-2">
              <span className="font-semibold text-ink-900">Module Category</span>
              <span className="capitalize">{provider.category}</span>
            </li>
            <li className="flex justify-between border-b pb-2">
              <span className="font-semibold text-ink-900">System Visibility</span>
              <span>{provider.enabled ? "Active" : "Disabled"}</span>
            </li>
            <li className="flex justify-between border-b pb-2">
              <span className="font-semibold text-ink-900">Friend Visibility</span>
              <span>{provider.patientVisible ? "Safe for Direct Display" : "Family Access Only"}</span>
            </li>
            <li className="flex justify-between pb-2">
              <span className="font-semibold text-ink-900">Friend Home Eligibility</span>
              <span>{canReachPatientHome ? "Eligible for friend session assembly" : "Blocked before friend assembly"}</span>
            </li>
          </ul>
        </section>

        <section className="rounded-[28px] border border-black/10 bg-white/70 p-6 shadow-panel text-sm">
          <h3 className="text-base font-bold text-ink-900">Live diagnostics</h3>
          <div className="mt-4 space-y-3 text-ink-700">
            <p>
              {provider.enabled
                ? "This provider is globally enabled in the catalog."
                : "This provider is globally disabled, so no friend can receive it until the catalog setting is turned back on."}
            </p>
            <p>
              {provider.patientVisible
                ? "It is currently marked friend-visible."
                : "It is currently family-only and will not appear in the friend-facing daily session."}
            </p>
            <p>
              Friend-level toggles below decide which family members may receive this provider when session assembly runs.
            </p>
          </div>
        </section>
      </div>

      <section className="rounded-[28px] border border-black/10 bg-white/70 p-6 shadow-panel">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-bold text-ink-900">Friend mapping</h3>
            <p className="mt-2 text-sm text-ink-700">
              Control which friends in this family can receive <span className="font-semibold">{provider.label}</span>.
            </p>
          </div>
          <Link
            className="inline-flex items-center rounded-full border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-ink-900 transition hover:border-black/20"
            href="/care-circle-family/patients"
          >
            Open patients
          </Link>
        </div>

        {isLoadingConfigs ? (
          <div className="mt-6">
            <LoadingState label="Loading friend mappings" />
          </div>
        ) : (
          <div className="mt-6 grid gap-4">
            {patients?.map((patient, index) => {
              const configRows = providerConfigQueries[index]?.data ?? [];
              const explicitConfig = configRows.find((config) => config.provider_key === provider.providerKey);
              const isEnabledForPatient = explicitConfig ? explicitConfig.is_enabled : provider.enabled;
              const isSavingThisPatient =
                updateMutation.isPending && updateMutation.variables?.patientId === patient.id;

              return (
                <article
                  key={patient.id}
                  className="flex flex-wrap items-center justify-between gap-4 rounded-[24px] border border-black/10 bg-[#fcfaf6] p-5"
                >
                  <div>
                    <p className="text-xs uppercase tracking-[0.2em] text-ink-600">{patient.familyName}</p>
                    <h4 className="mt-1 font-semibold text-ink-900">{patient.displayName}</h4>
                    <p className="mt-2 text-sm text-ink-700">
                      {patient.stage} stage · {patient.accessState} · delivery {patient.deliveryTime ?? "Flexible"}
                    </p>
                  </div>

                  <div className="flex flex-wrap items-center gap-3">
                    <span className="rounded-full border border-black/10 px-3 py-2 text-xs text-ink-700">
                      {provider.patientVisible ? "Friend-safe" : "Family-only"}
                    </span>
                    {isOwner ? (
                      <button
                        className={`inline-flex min-w-28 justify-center rounded-full px-4 py-2 text-sm font-semibold transition ${
                          isEnabledForPatient
                            ? "bg-emerald-100 text-emerald-900 hover:bg-emerald-200"
                            : "bg-slate-200 text-slate-800 hover:bg-slate-300"
                        } disabled:cursor-not-allowed disabled:opacity-60`}
                        disabled={updateMutation.isPending}
                        onClick={() =>
                          updateMutation.mutate({
                            patientId: patient.id,
                            isEnabled: !isEnabledForPatient,
                          })
                        }
                        type="button"
                      >
                        {isSavingThisPatient ? "Saving..." : isEnabledForPatient ? "Enabled" : "Disabled"}
                      </button>
                    ) : (
                      <span className={`inline-flex min-w-28 justify-center rounded-full px-4 py-2 text-sm font-semibold ${
                        isEnabledForPatient ? "bg-emerald-100 text-emerald-900" : "bg-slate-200 text-slate-800"
                      }`}>
                        {isEnabledForPatient ? "Enabled" : "Disabled"}
                      </span>
                    )}
                    <Link
                      className="inline-flex items-center rounded-full border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-ink-900 transition hover:border-black/20"
                      href={`/care-circle-family/patients/${patient.id}`}
                    >
                      Open friend
                    </Link>
                  </div>
                </article>
              );
            })}
          </div>
        )}

        {updateMutation.isError ? (
          <p className="mt-4 text-sm text-[#a0382b]">
            {updateMutation.error instanceof Error ? updateMutation.error.message : "Could not save friend mapping."}
          </p>
        ) : null}
      </section>
    </div>
  );
}

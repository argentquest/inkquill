"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { PatientAccessStateBadge } from "@/components/care-circle-family/patient-access-state-badge";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import {
  fetchCareCirclePatient,
  fetchCareCirclePatientProviderConfigs,
  fetchCareCircleProviders,
  type CareCirclePatientUpdateInput,
  updateCareCirclePatient,
  updateCareCirclePatientProviderConfig,
} from "@/lib/api";

function parseCsvList(value: string) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

export function FamilyPatientDetailClient({ patientId }: { patientId: string }) {
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();
  const { data: patient, isLoading, isError, error } = useQuery({
    queryKey: ["care-circle-family-patient", patientId],
    queryFn: () => fetchCareCirclePatient(patientId),
  });
  const {
    data: providerCatalog,
    isLoading: isLoadingProviderCatalog,
    isError: isProviderCatalogError,
    error: providerCatalogError,
  } = useQuery({
    queryKey: ["care-circle-providers"],
    queryFn: fetchCareCircleProviders,
  });
  const {
    data: providerConfigs,
    isLoading: isLoadingProviderConfigs,
    isError: isProviderConfigError,
    error: providerConfigError,
  } = useQuery({
    queryKey: ["care-circle-family-patient-provider-configs", patientId],
    queryFn: () => fetchCareCirclePatientProviderConfigs(patientId),
  });
  const [isEditing, setIsEditing] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [providerSaveError, setProviderSaveError] = useState<string | null>(null);
  const [pendingProviderKey, setPendingProviderKey] = useState<string | null>(null);
  const [formState, setFormState] = useState<CareCirclePatientUpdateInput>({
    familyName: "",
    joinCode: "",
    displayName: "",
    stage: "moderate",
    accessState: "active",
    timezone: "America/Chicago",
    deliveryTime: "",
    days: [],
    familyMembers: [],
    preferences: [],
    authImageKeys: [],
  });

  useEffect(() => {
    if (!patient) {
      return;
    }

    setFormState({
      familyName: patient.familyName,
      joinCode: patient.joinCode,
      displayName: patient.displayName,
      stage: patient.stage,
      accessState: patient.accessState,
      timezone: patient.timezone,
      deliveryTime: patient.deliveryTime ?? "",
      days: patient.days,
      familyMembers: patient.familyMembers,
      preferences: patient.preferences,
      authImageKeys: patient.authImageKeys,
    });
  }, [patient]);

  useEffect(() => {
    if (searchParams.get("edit") === "1") {
      setIsEditing(true);
      setSaveError(null);
    }
  }, [searchParams]);

  const updateMutation = useMutation({
    mutationFn: (input: CareCirclePatientUpdateInput) => updateCareCirclePatient(patientId, input),
    onSuccess: (updatedPatient) => {
      queryClient.setQueryData(["care-circle-family-patient", patientId], updatedPatient);
      queryClient.invalidateQueries({ queryKey: ["care-circle-family-patients"] });
      setSaveError(null);
      setIsEditing(false);
    },
    onError: (mutationError) => {
      setSaveError(mutationError instanceof Error ? mutationError.message : "Could not save patient settings.");
    },
  });

  const providerConfigMutation = useMutation({
    mutationFn: (input: { providerKey: string; isEnabled: boolean }) =>
      updateCareCirclePatientProviderConfig(patientId, input.providerKey, {
        is_enabled: input.isEnabled,
        custom_parameters: {},
      }),
    onMutate: (input) => {
      setProviderSaveError(null);
      setPendingProviderKey(input.providerKey);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["care-circle-family-patient-provider-configs", patientId] });
      setPendingProviderKey(null);
    },
    onError: (mutationError) => {
      setPendingProviderKey(null);
      setProviderSaveError(
        mutationError instanceof Error ? mutationError.message : "Could not update provider access."
      );
    },
  });

  if (isLoading) {
    return <LoadingState label="Loading patient profile" />;
  }

  if (isError || !patient) {
    return <ErrorState detail={error instanceof Error ? error.message : "Could not load the patient profile."} title="Patient profile unavailable" />;
  }

  const providerStateByKey = new Map(
    (providerConfigs ?? []).map((config) => [config.provider_key, config.is_enabled])
  );

  return (
    <div className="space-y-8">
      <section className="rounded-[28px] border border-black/10 bg-white/82 p-6 shadow-panel">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-ink-600">Family configuration</p>
            <h2 className="mt-2 font-display text-3xl text-ink-900">Managed patient settings</h2>
          </div>
          <button
            className="inline-flex rounded-full border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-ink-900 transition hover:border-black/20 disabled:cursor-not-allowed disabled:opacity-60"
            onClick={() => {
              setIsEditing((current) => !current);
              setSaveError(null);
            }}
            type="button"
          >
            {isEditing ? "Close editor" : "Edit family configuration"}
          </button>
        </div>

        {isEditing ? (
          <form
            className="mt-6 grid gap-5 md:grid-cols-2"
            onSubmit={(event) => {
              event.preventDefault();
              setSaveError(null);
              updateMutation.mutate(formState);
            }}
          >
            <label className="block text-sm text-ink-800">
              <span className="text-xs uppercase tracking-[0.24em] text-ink-600">Family name</span>
              <input
                className="mt-2 w-full rounded-2xl border border-black/10 bg-[#fcfaf6] px-4 py-3 text-base text-ink-900 outline-none transition focus:border-black/30"
                onChange={(event) => setFormState((current) => ({ ...current, familyName: event.target.value }))}
                value={formState.familyName}
              />
            </label>
            <label className="block text-sm text-ink-800">
              <span className="text-xs uppercase tracking-[0.24em] text-ink-600">Join code</span>
              <input
                className="mt-2 w-full rounded-2xl border border-black/10 bg-[#fcfaf6] px-4 py-3 font-mono text-base uppercase tracking-[0.18em] text-ink-900 outline-none transition focus:border-black/30"
                onChange={(event) => setFormState((current) => ({ ...current, joinCode: event.target.value.toUpperCase() }))}
                value={formState.joinCode}
              />
            </label>
            <label className="block text-sm text-ink-800">
              <span className="text-xs uppercase tracking-[0.24em] text-ink-600">Patient name</span>
              <input
                className="mt-2 w-full rounded-2xl border border-black/10 bg-[#fcfaf6] px-4 py-3 text-base text-ink-900 outline-none transition focus:border-black/30"
                onChange={(event) => setFormState((current) => ({ ...current, displayName: event.target.value }))}
                value={formState.displayName}
              />
            </label>
            <label className="block text-sm text-ink-800">
              <span className="text-xs uppercase tracking-[0.24em] text-ink-600">Stage</span>
              <select
                className="mt-2 w-full rounded-2xl border border-black/10 bg-[#fcfaf6] px-4 py-3 text-base text-ink-900 outline-none transition focus:border-black/30"
                onChange={(event) => setFormState((current) => ({ ...current, stage: event.target.value }))}
                value={formState.stage}
              >
                <option value="mild">Mild</option>
                <option value="moderate">Moderate</option>
                <option value="severe">Severe</option>
              </select>
            </label>
            <label className="block text-sm text-ink-800">
              <span className="text-xs uppercase tracking-[0.24em] text-ink-600">Access state</span>
              <select
                className="mt-2 w-full rounded-2xl border border-black/10 bg-[#fcfaf6] px-4 py-3 text-base text-ink-900 outline-none transition focus:border-black/30"
                onChange={(event) => setFormState((current) => ({ ...current, accessState: event.target.value }))}
                value={formState.accessState}
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="archived">Archived</option>
              </select>
            </label>
            <label className="block text-sm text-ink-800">
              <span className="text-xs uppercase tracking-[0.24em] text-ink-600">Timezone</span>
              <input
                className="mt-2 w-full rounded-2xl border border-black/10 bg-[#fcfaf6] px-4 py-3 text-base text-ink-900 outline-none transition focus:border-black/30"
                onChange={(event) => setFormState((current) => ({ ...current, timezone: event.target.value }))}
                value={formState.timezone}
              />
            </label>
            <label className="block text-sm text-ink-800">
              <span className="text-xs uppercase tracking-[0.24em] text-ink-600">Delivery time</span>
              <input
                className="mt-2 w-full rounded-2xl border border-black/10 bg-[#fcfaf6] px-4 py-3 text-base text-ink-900 outline-none transition focus:border-black/30"
                onChange={(event) => setFormState((current) => ({ ...current, deliveryTime: event.target.value }))}
                placeholder="08:30"
                value={formState.deliveryTime ?? ""}
              />
            </label>
            <label className="block text-sm text-ink-800 md:col-span-2">
              <span className="text-xs uppercase tracking-[0.24em] text-ink-600">Delivery days</span>
              <input
                className="mt-2 w-full rounded-2xl border border-black/10 bg-[#fcfaf6] px-4 py-3 text-base text-ink-900 outline-none transition focus:border-black/30"
                onChange={(event) => setFormState((current) => ({ ...current, days: parseCsvList(event.target.value) }))}
                placeholder="Mon, Wed, Fri"
                value={formState.days.join(", ")}
              />
            </label>
            <label className="block text-sm text-ink-800 md:col-span-2">
              <span className="text-xs uppercase tracking-[0.24em] text-ink-600">Family members</span>
              <input
                className="mt-2 w-full rounded-2xl border border-black/10 bg-[#fcfaf6] px-4 py-3 text-base text-ink-900 outline-none transition focus:border-black/30"
                onChange={(event) => setFormState((current) => ({ ...current, familyMembers: parseCsvList(event.target.value) }))}
                placeholder="Nina, Paul, Maggie"
                value={formState.familyMembers.join(", ")}
              />
            </label>
            <label className="block text-sm text-ink-800 md:col-span-2">
              <span className="text-xs uppercase tracking-[0.24em] text-ink-600">Preference tags</span>
              <input
                className="mt-2 w-full rounded-2xl border border-black/10 bg-[#fcfaf6] px-4 py-3 text-base text-ink-900 outline-none transition focus:border-black/30"
                onChange={(event) => setFormState((current) => ({ ...current, preferences: parseCsvList(event.target.value) }))}
                placeholder="gardening, jazz, family photos"
                value={formState.preferences.join(", ")}
              />
            </label>
            <label className="block text-sm text-ink-800 md:col-span-2">
              <span className="text-xs uppercase tracking-[0.24em] text-ink-600">Auth image keys</span>
              <input
                className="mt-2 w-full rounded-2xl border border-black/10 bg-[#fcfaf6] px-4 py-3 text-base text-ink-900 outline-none transition focus:border-black/30"
                onChange={(event) => setFormState((current) => ({ ...current, authImageKeys: parseCsvList(event.target.value) }))}
                placeholder="sun, dog, house"
                value={formState.authImageKeys.join(", ")}
              />
              <p className="mt-2 text-xs text-ink-600">Exactly three unique image keys are required for patient sign-in.</p>
            </label>
            {saveError ? <p className="md:col-span-2 text-sm text-[#a0382b]">{saveError}</p> : null}
            <div className="md:col-span-2 flex flex-wrap gap-3">
              <button
                className="inline-flex rounded-full bg-ink-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-ink-800 disabled:cursor-not-allowed disabled:opacity-60"
                disabled={updateMutation.isPending}
                type="submit"
              >
                {updateMutation.isPending ? "Saving..." : "Save family configuration"}
              </button>
              <button
                className="inline-flex rounded-full border border-black/10 bg-white px-5 py-3 text-sm font-semibold text-ink-900 transition hover:border-black/20"
                onClick={() => {
                  setIsEditing(false);
                  setSaveError(null);
                  setFormState({
                    familyName: patient.familyName,
                    joinCode: patient.joinCode,
                    displayName: patient.displayName,
                    stage: patient.stage,
                    accessState: patient.accessState,
                    timezone: patient.timezone,
                    deliveryTime: patient.deliveryTime ?? "",
                    days: patient.days,
                    familyMembers: patient.familyMembers,
                    preferences: patient.preferences,
                    authImageKeys: patient.authImageKeys,
                  });
                }}
                type="button"
              >
                Cancel
              </button>
            </div>
          </form>
        ) : null}
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.2fr,0.8fr]">
        <article className="rounded-[28px] border border-black/10 bg-white/82 p-6 shadow-panel">
          <div className="flex items-center justify-between gap-4">
            <h2 className="font-display text-3xl text-ink-900">Profile summary</h2>
            <PatientAccessStateBadge state={patient.accessState as "active" | "inactive" | "archived"} />
          </div>
          <dl className="mt-6 grid gap-5 md:grid-cols-2">
            <div>
              <dt className="text-xs uppercase tracking-[0.24em] text-ink-600">Family</dt>
              <dd className="mt-2 text-base text-ink-900">{patient.familyName}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-[0.24em] text-ink-600">Join code</dt>
              <dd className="mt-2 font-mono text-base uppercase tracking-[0.18em] text-ink-900">{patient.joinCode}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-[0.24em] text-ink-600">Stage</dt>
              <dd className="mt-2 text-base capitalize text-ink-900">{patient.stage}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-[0.24em] text-ink-600">Delivery</dt>
              <dd className="mt-2 text-base text-ink-900">
                {patient.deliveryTime ?? "Flexible"} · {patient.days.join(", ")}
              </dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-[0.24em] text-ink-600">Timezone</dt>
              <dd className="mt-2 text-base text-ink-900">{patient.timezone}</dd>
            </div>
          </dl>
        </article>

        <article className="rounded-[28px] border border-black/10 bg-white/82 p-6 shadow-panel">
          <h2 className="font-display text-3xl text-ink-900">Image sign-in</h2>
          <p className="mt-4 text-sm leading-7 text-ink-700">
            Exactly three familiar images are assigned for direct patient access.
          </p>
          <div className="mt-5 flex flex-wrap gap-2">
            {patient.authImageKeys.map((key) => (
              <span key={key} className="rounded-full border border-black/10 bg-[#fcfaf6] px-3 py-2 text-sm font-semibold capitalize text-ink-900">
                {key}
              </span>
            ))}
          </div>
          <Link className="mt-6 inline-flex rounded-full border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-ink-900 transition hover:border-black/20" href="/care-circle-patient/login">
            Preview patient sign-in
          </Link>
        </article>
      </section>

      <section className="rounded-[28px] border border-black/10 bg-white/82 p-6 shadow-panel">
        <h2 className="font-display text-3xl text-ink-900">Patient preferences</h2>
        <div className="mt-5 flex flex-wrap gap-2">
          {patient.preferences.map((preference) => (
            <span key={preference} className="rounded-full border border-black/10 bg-[#fcfaf6] px-3 py-2 text-sm text-ink-700">
              {preference}
            </span>
          ))}
        </div>
        <p className="mt-6 text-sm leading-7 text-ink-700">Family circle: {patient.familyMembers.join(", ")}.</p>
      </section>

      <section className="rounded-[28px] border border-black/10 bg-white/82 p-6 shadow-panel">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="font-display text-3xl text-ink-900">Provider selection</h2>
            <p className="mt-2 text-sm leading-7 text-ink-700">
              Enable or disable specific providers for this patient. Disabled providers are skipped during session assembly.
            </p>
          </div>
          <Link
            className="inline-flex rounded-full border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-ink-900 transition hover:border-black/20"
            href="/care-circle-family/providers"
          >
            Open provider catalog
          </Link>
        </div>

        {isLoadingProviderCatalog || isLoadingProviderConfigs ? (
          <div className="mt-6">
            <LoadingState label="Loading provider options" />
          </div>
        ) : isProviderCatalogError || isProviderConfigError ? (
          <div className="mt-6">
            <ErrorState
              detail={
                providerCatalogError instanceof Error
                  ? providerCatalogError.message
                  : providerConfigError instanceof Error
                    ? providerConfigError.message
                    : "Could not load provider settings."
              }
              title="Provider settings unavailable"
            />
          </div>
        ) : (
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {providerCatalog?.map((provider) => {
              const isEnabled = providerStateByKey.get(provider.providerKey) ?? provider.enabled;
              const isPending = pendingProviderKey === provider.providerKey && providerConfigMutation.isPending;

              return (
                <article
                  key={provider.providerKey}
                  className="rounded-[24px] border border-black/10 bg-[#fcfaf6] p-5"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{provider.icon || "📰"}</span>
                        <div>
                          <h3 className="font-semibold text-ink-900">{provider.label}</h3>
                          <p className="text-xs uppercase tracking-[0.2em] text-ink-600">{provider.category}</p>
                        </div>
                      </div>
                      <div className="mt-3 flex flex-wrap gap-2 text-xs">
                        <span className="rounded-full border border-black/10 px-2 py-1 text-ink-700">
                          {provider.patientVisible ? "Patient-safe" : "Family-only"}
                        </span>
                        <span className="rounded-full border border-black/10 px-2 py-1 text-ink-700">
                          Global {provider.enabled ? "on" : "off"}
                        </span>
                      </div>
                    </div>

                    <button
                      className={`inline-flex min-w-24 justify-center rounded-full px-4 py-2 text-sm font-semibold transition ${
                        isEnabled
                          ? "bg-emerald-100 text-emerald-900 hover:bg-emerald-200"
                          : "bg-slate-200 text-slate-800 hover:bg-slate-300"
                      } disabled:cursor-not-allowed disabled:opacity-60`}
                      disabled={providerConfigMutation.isPending}
                      onClick={() =>
                        providerConfigMutation.mutate({
                          providerKey: provider.providerKey,
                          isEnabled: !isEnabled,
                        })
                      }
                      type="button"
                    >
                      {isPending ? "Saving..." : isEnabled ? "Enabled" : "Disabled"}
                    </button>
                  </div>
                </article>
              );
            })}
          </div>
        )}

        {providerSaveError ? <p className="mt-4 text-sm text-[#a0382b]">{providerSaveError}</p> : null}
      </section>
    </div>
  );
}

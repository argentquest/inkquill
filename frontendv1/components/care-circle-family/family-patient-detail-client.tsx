"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { useSession } from "@/components/providers/app-providers";
import { PatientAccessStateBadge } from "@/components/care-circle-family/patient-access-state-badge";
import { ProviderOrderingPanel } from "@/components/care-circle-family/provider-ordering-panel";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import {
  EMPTY_PREFERENCES,
  fetchCareCirclePatient,
  fetchCareCirclePatientAuthCatalog,
  fetchCareCirclePatientProviderConfigs,
  fetchRegeneratePatientNewsletterStatus,
  fetchCareCircleProviders,
  fetchIsoCodes,
  fetchPatientNewsletterPreview,
  regeneratePatientNewsletter,
  sendPatientNewsletter,
  type CareCircleAuthCatalogItem,
  type CareCirclePatientPreferences,
  type CareCirclePatientUpdateInput,
  type IsoCodeEntry,
  updateCareCirclePatient,
} from "@/lib/api";

// ---------------------------------------------------------------------------
// Shared form primitives
// ---------------------------------------------------------------------------

const INPUT_CLS =
  "mt-2 w-full rounded-2xl border border-black/10 bg-[#fcfaf6] px-4 py-3 text-base text-ink-900 outline-none transition focus:border-black/30";
const LABEL_CLS = "block text-sm text-ink-800";
const EYEBROW_CLS = "text-xs uppercase tracking-[0.24em] text-ink-600";
const EMPTY_PATIENT_FORM: CareCirclePatientUpdateInput = {
  familyName: "",
  joinCode: "",
  displayName: "",
  stage: "moderate",
  accessState: "active",
  timezone: "America/Chicago",
  preferredLanguage: "en",
  country: "US",
  postalCode: null,
  deliveryTime: "",
  days: [],
  authImageKeys: [],
  email: null,
  phoneNumber: null,
  preferences: { ...EMPTY_PREFERENCES },
};

function FormField({
  label,
  children,
  span2,
}: {
  label: string;
  children: React.ReactNode;
  span2?: boolean;
}) {
  return (
    <label className={`${LABEL_CLS}${span2 ? " md:col-span-2" : ""}`}>
      <span className={EYEBROW_CLS}>{label}</span>
      {children}
    </label>
  );
}

function TagInput({
  label,
  values,
  onChange,
  placeholder,
  hint,
  span2 = true,
}: {
  label: string;
  values: string[];
  onChange: (_next: string[]) => void;
  placeholder?: string;
  hint?: string;
  span2?: boolean;
}) {
  const [draft, setDraft] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  function commit() {
    const trimmed = draft.trim();
    if (trimmed && !values.includes(trimmed)) {
      onChange([...values, trimmed]);
    }
    setDraft("");
  }

  return (
    <div className={`block text-sm text-ink-800${span2 ? " md:col-span-2" : ""}`}>
      <span className={EYEBROW_CLS}>{label}</span>
      <div
        className="mt-2 flex min-h-[48px] cursor-text flex-wrap gap-2 rounded-2xl border border-black/10 bg-[#fcfaf6] px-4 py-3 transition focus-within:border-black/30"
        onClick={() => inputRef.current?.focus()}
      >
        {values.map((value, i) => (
          <span
            key={i}
            className="inline-flex items-center gap-1.5 rounded-full bg-ink-900/8 px-3 py-1 text-sm font-medium text-ink-900"
          >
            {value}
            <button
              aria-label={`Remove ${value}`}
              className="flex h-4 w-4 items-center justify-center rounded-full text-ink-600 hover:bg-ink-900/10 hover:text-ink-900"
              onClick={(e) => { e.stopPropagation(); onChange(values.filter((_, j) => j !== i)); }}
              type="button"
            >
              ×
            </button>
          </span>
        ))}
        <input
          ref={inputRef}
          className="min-w-[120px] flex-1 bg-transparent text-base text-ink-900 outline-none placeholder:text-ink-400"
          onBlur={commit}
          onChange={(e) => setDraft(e.target.value.replace(",", ""))}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === ",") { e.preventDefault(); commit(); }
            else if (e.key === "Backspace" && draft === "" && values.length > 0) onChange(values.slice(0, -1));
          }}
          placeholder={values.length === 0 ? placeholder : undefined}
          value={draft}
        />
      </div>
      {hint ? <p className="mt-2 text-xs text-ink-600">{hint}</p> : null}
    </div>
  );
}

function AuthImagePicker({
  catalog,
  values,
  onChange,
}: {
  catalog: CareCircleAuthCatalogItem[];
  values: string[];
  onChange: (_next: string[]) => void;
}) {
  function toggle(key: string) {
    if (values.includes(key)) onChange(values.filter((k) => k !== key));
    else if (values.length < 3) onChange([...values, key]);
  }

  return (
    <div className="md:col-span-2">
      <span className={EYEBROW_CLS}>Auth image keys</span>
      <div className="mt-2 flex flex-wrap gap-2">
        {catalog.map((item) => {
          const selected = values.includes(item.key);
          const disabled = !selected && values.length >= 3;
          return (
            <button
              key={item.key}
              aria-pressed={selected}
              className={[
                "inline-flex items-center gap-2 rounded-full border px-4 py-2 text-sm font-medium transition",
                selected
                  ? "border-ink-900 bg-ink-900 text-white"
                  : disabled
                    ? "cursor-not-allowed border-black/10 bg-[#fcfaf6] text-ink-400"
                    : "border-black/10 bg-[#fcfaf6] text-ink-900 hover:border-black/30",
              ].join(" ")}
              disabled={disabled}
              onClick={() => toggle(item.key)}
              type="button"
            >
              <span>{item.emoji}</span>
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>
      <p className="mt-2 text-xs text-ink-600">
        {values.length}/3 selected — exactly three images are required for friend sign-in.
      </p>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Section divider used inside the form
// ---------------------------------------------------------------------------

function FormSection({ title }: { title: string }) {
  return (
    <div className="md:col-span-2 border-t border-black/8 pt-4 mt-1">
      <p className="text-xs uppercase tracking-[0.24em] text-ink-500">{title}</p>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function setPrefs(
  current: CareCirclePatientUpdateInput,
  patch: Partial<CareCirclePatientPreferences>,
): CareCirclePatientUpdateInput {
  return { ...current, preferences: { ...current.preferences, ...patch } };
}

function patientToForm(patient: {
  familyName: string;
  joinCode: string;
  displayName: string;
  stage: string;
  accessState: string;
  timezone: string;
  preferredLanguage: string;
  country: string;
  postalCode: string | null;
  deliveryTime: string | null;
  days: string[];
  authImageKeys: string[];
  email: string | null;
  phoneNumber: string | null;
  preferences: CareCirclePatientPreferences;
}): CareCirclePatientUpdateInput {
  return {
    familyName: patient.familyName,
    joinCode: patient.joinCode,
    displayName: patient.displayName,
    stage: patient.stage,
    accessState: patient.accessState,
    timezone: patient.timezone,
    preferredLanguage: patient.preferredLanguage,
    country: patient.country,
    postalCode: patient.postalCode,
    deliveryTime: patient.deliveryTime ?? "",
    days: patient.days,
    authImageKeys: patient.authImageKeys,
    email: patient.email,
    phoneNumber: patient.phoneNumber,
    preferences: { ...EMPTY_PREFERENCES, ...patient.preferences },
  };
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export function FamilyPatientDetailClient({ patientId }: { patientId: string }) {
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();
  const session = useSession();
  const isOwner = session.user?.is_family_owner === true;

  const { data: patient, isLoading, isError, error } = useQuery({
    queryKey: ["care-circle-family-patient", patientId],
    queryFn: () => fetchCareCirclePatient(patientId),
  });
  const { data: providerCatalog, isLoading: isLoadingProviderCatalog, isError: isProviderCatalogError, error: providerCatalogError } = useQuery({
    queryKey: ["care-circle-providers"],
    queryFn: fetchCareCircleProviders,
  });
  const { data: providerConfigs, isLoading: isLoadingProviderConfigs, isError: isProviderConfigError, error: providerConfigError } = useQuery({
    queryKey: ["care-circle-family-patient-provider-configs", patientId],
    queryFn: () => fetchCareCirclePatientProviderConfigs(patientId),
  });
  const { data: authCatalog = [] } = useQuery({
    queryKey: ["care-circle-patient-auth-catalog"],
    queryFn: fetchCareCirclePatientAuthCatalog,
  });
  const { data: isoCodes } = useQuery({
    queryKey: ["care-circle-iso-codes"],
    queryFn: fetchIsoCodes,
  });

  const [isEditing, setIsEditing] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [formState, setFormState] = useState<CareCirclePatientUpdateInput>(EMPTY_PATIENT_FORM);

  useEffect(() => {
    if (patient) setFormState(patientToForm(patient));
  }, [patient]);

  useEffect(() => {
    setFormState(EMPTY_PATIENT_FORM);
    setSaveError(null);
  }, [patientId]);

  useEffect(() => {
    if (searchParams.get("edit") === "1" && isOwner) { setIsEditing(true); setSaveError(null); }
  }, [searchParams, isOwner]);

  const [sendResult, setSendResult] = useState<{ ok: boolean; message: string } | null>(null);
  const [regenerationJobId, setRegenerationJobId] = useState<string | null>(null);
  const [regenerationMessage, setRegenerationMessage] = useState<string | null>(null);

  const todayStr = new Date().toISOString().slice(0, 10);
  const [previewDate, setPreviewDate] = useState(todayStr);

  const { data: newsletterPreview, isLoading: isLoadingPreview } = useQuery({
    queryKey: ["care-circle-newsletter-preview", patientId, previewDate],
    queryFn: () => fetchPatientNewsletterPreview(patientId, previewDate),
  });

  const { data: regenerationStatus } = useQuery({
    queryKey: ["care-circle-newsletter-regeneration", patientId, regenerationJobId],
    queryFn: () => fetchRegeneratePatientNewsletterStatus(patientId, regenerationJobId ?? ""),
    enabled: Boolean(regenerationJobId),
    refetchInterval: (query) => {
      const state = query.state.data?.state;
      return state === "COMPLETED" || state === "FAILED" ? false : 3000;
    },
  });

  useEffect(() => {
    if (!regenerationStatus) {
      return;
    }

    if (regenerationStatus.state === "COMPLETED") {
      setRegenerationMessage(regenerationStatus.result_message || "Newsletter regeneration finished.");
      setRegenerationJobId(null);
      queryClient.invalidateQueries({ queryKey: ["care-circle-newsletter-preview", patientId, previewDate] });
      return;
    }

    if (regenerationStatus.state === "FAILED") {
      setRegenerationMessage(regenerationStatus.result_message || "Newsletter regeneration failed.");
      setRegenerationJobId(null);
      return;
    }

    setRegenerationMessage(regenerationStatus.status_message || "Newsletter regeneration in progress...");
  }, [patientId, previewDate, queryClient, regenerationStatus]);

  function shiftPreviewDate(days: number) {
    const d = new Date(previewDate + "T12:00:00");
    d.setDate(d.getDate() + days);
    const next = d.toISOString().slice(0, 10);
    if (next <= todayStr) setPreviewDate(next);
  }

  const regenerateMutation = useMutation({
    mutationFn: () => regeneratePatientNewsletter(patientId),
    onSuccess: (result) => {
      setRegenerationJobId(result.job_id);
      setRegenerationMessage(result.message);
    },
    onError: (err) => {
      setRegenerationJobId(null);
      setRegenerationMessage(err instanceof Error ? err.message : "Failed to start regeneration.");
    },
  });

  const sendNewsletterMutation = useMutation({
    mutationFn: () => sendPatientNewsletter(patientId),
    onSuccess: (result) => {
      const parts = [];
      if (result.email_sent) parts.push("email sent");
      if (result.sms_sent) parts.push("SMS sent");
      setSendResult({ ok: true, message: parts.length > 0 ? parts.join(", ") : "dispatched (no delivery address on file)" });
    },
    onError: (err) => {
      setSendResult({ ok: false, message: err instanceof Error ? err.message : "Failed to send newsletter." });
    },
  });

  const updateMutation = useMutation({
    mutationFn: (input: CareCirclePatientUpdateInput) => updateCareCirclePatient(patientId, input),
    onSuccess: (updatedPatient) => {
      queryClient.setQueryData(["care-circle-family-patient", patientId], updatedPatient);
      queryClient.invalidateQueries({ queryKey: ["care-circle-family-patients"] });
      setSaveError(null);
      setIsEditing(false);
    },
    onError: (err) => setSaveError(err instanceof Error ? err.message : "Could not save friend settings."),
  });

  if (isLoading) return <LoadingState label="Loading friend profile" />;
  if (isError || !patient) {
    return <ErrorState detail={error instanceof Error ? error.message : "Could not load the friend profile."} title="Friend profile unavailable" />;
  }

  const prefs = formState.preferences;

  return (
    <div className="space-y-8">

      {/* ── Edit form ──────────────────────────────────────────────── */}
      <section className="rounded-[28px] border border-black/10 bg-white/82 p-6 shadow-panel">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className={EYEBROW_CLS}>Family configuration</p>
            <h2 className="mt-2 font-display text-3xl text-ink-900">Managed friend settings</h2>
          </div>
          {isOwner && (
            <button
              className="inline-flex rounded-full border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-ink-900 transition hover:border-black/20"
              onClick={() => { setIsEditing((v) => !v); setSaveError(null); }}
              type="button"
            >
              {isEditing ? "Close editor" : "Edit friend profile"}
            </button>
          )}
        </div>

        {isEditing ? (
          <form
            className="mt-6 grid gap-5 md:grid-cols-2"
            onSubmit={(e) => { e.preventDefault(); setSaveError(null); updateMutation.mutate(formState); }}
          >
            {/* — Family & access ——————————————————————————————— */}
            <FormSection title="Family & access" />

            <FormField label="Family name">
              <input className={INPUT_CLS} onChange={(e) => setFormState((c) => ({ ...c, familyName: e.target.value }))} value={formState.familyName} />
            </FormField>
            <FormField label="Join code">
              <input className={`${INPUT_CLS} font-mono uppercase tracking-[0.18em]`} onChange={(e) => setFormState((c) => ({ ...c, joinCode: e.target.value.toUpperCase() }))} value={formState.joinCode} />
            </FormField>
            <FormField label="Friend display name">
              <input className={INPUT_CLS} onChange={(e) => setFormState((c) => ({ ...c, displayName: e.target.value }))} value={formState.displayName} />
            </FormField>
            <FormField label="Newsletter name">
              <input
                className={INPUT_CLS}
                onChange={(e) => setFormState((c) => setPrefs(c, { recipientName: e.target.value || null }))}
                placeholder="Name used in newsletters (defaults to display name)"
                value={prefs.recipientName ?? ""}
              />
            </FormField>
            <FormField label="Stage">
              <select className={INPUT_CLS} onChange={(e) => setFormState((c) => ({ ...c, stage: e.target.value }))} value={formState.stage}>
                <option value="mild">Mild</option>
                <option value="moderate">Moderate</option>
                <option value="severe">Severe</option>
              </select>
            </FormField>
            <FormField label="Access state">
              <select className={INPUT_CLS} onChange={(e) => setFormState((c) => ({ ...c, accessState: e.target.value }))} value={formState.accessState}>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="archived">Archived</option>
              </select>
            </FormField>
            <FormField label="Email address">
              <input className={INPUT_CLS} onChange={(e) => setFormState((c) => ({ ...c, email: e.target.value || null }))} placeholder="friend@example.com" type="email" value={formState.email ?? ""} />
            </FormField>
            <FormField label="Phone number">
              <input className={INPUT_CLS} onChange={(e) => setFormState((c) => ({ ...c, phoneNumber: e.target.value || null }))} placeholder="+1 555 000 0000" type="tel" value={formState.phoneNumber ?? ""} />
            </FormField>

            {/* — Delivery ——————————————————————————————————————— */}
            <FormSection title="Delivery schedule" />

            <FormField label="Timezone">
              <input className={INPUT_CLS} onChange={(e) => setFormState((c) => ({ ...c, timezone: e.target.value }))} value={formState.timezone} />
            </FormField>
            <FormField label="Language">
              <select
                className={INPUT_CLS}
                onChange={(e) => setFormState((c) => ({ ...c, preferredLanguage: e.target.value }))}
                value={formState.preferredLanguage}
              >
                <option value="">Select language</option>
                {(isoCodes?.languages ?? []).map((lang: IsoCodeEntry) => (
                  <option key={lang.code} value={lang.code}>
                    {lang.name} ({lang.code})
                  </option>
                ))}
              </select>
            </FormField>
            <FormField label="Country">
              <select
                className={INPUT_CLS}
                onChange={(e) => setFormState((c) => ({ ...c, country: e.target.value }))}
                value={formState.country}
              >
                <option value="">Select country</option>
                {(isoCodes?.countries ?? []).map((country: IsoCodeEntry) => (
                  <option key={country.code} value={country.code}>
                    {country.name} ({country.code})
                  </option>
                ))}
              </select>
            </FormField>
            <FormField label="Postal code / ZIP">
              <input
                className={INPUT_CLS}
                onChange={(e) => setFormState((c) => ({ ...c, postalCode: e.target.value || null }))}
                placeholder="Used to resolve latitude and longitude"
                value={formState.postalCode ?? ""}
              />
            </FormField>
            <FormField label="Delivery time">
              <input className={INPUT_CLS} onChange={(e) => setFormState((c) => ({ ...c, deliveryTime: e.target.value }))} placeholder="08:30" value={formState.deliveryTime ?? ""} />
            </FormField>
            <TagInput
              label="Delivery days"
              onChange={(next) => setFormState((c) => ({ ...c, days: next }))}
              placeholder="Mon, Wed, Fri…"
              values={formState.days}
            />

            {/* — Image sign-in ————————————————————————————————— */}
            <FormSection title="Image sign-in" />
            <AuthImagePicker
              catalog={authCatalog}
              onChange={(next) => setFormState((c) => ({ ...c, authImageKeys: next }))}
              values={formState.authImageKeys}
            />

            {/* — Identity & background ————————————————————————— */}
            <FormSection title="Identity & background" />

            <FormField label="Preferred pronoun">
              <select
                className={INPUT_CLS}
                onChange={(e) => setFormState((c) => setPrefs(c, { preferredPronoun: e.target.value || null }))}
                value={prefs.preferredPronoun ?? ""}
              >
                <option value="">Not specified</option>
                <option value="she/her">She / Her</option>
                <option value="he/him">He / Him</option>
                <option value="they/them">They / Them</option>
              </select>
            </FormField>
            <FormField label="Era of youth">
              <input
                className={INPUT_CLS}
                onChange={(e) => setFormState((c) => setPrefs(c, { eraOfYouth: e.target.value || null }))}
                placeholder="e.g. 1950s"
                value={prefs.eraOfYouth ?? ""}
              />
            </FormField>
            <FormField label="Hometown">
              <input
                className={INPUT_CLS}
                onChange={(e) => setFormState((c) => setPrefs(c, { hometown: e.target.value || null }))}
                placeholder="City or town they grew up in"
                value={prefs.hometown ?? ""}
              />
            </FormField>
            <FormField label="Nationality / background">
              <input
                className={INPUT_CLS}
                onChange={(e) => setFormState((c) => setPrefs(c, { nationalityOrBackground: e.target.value || null }))}
                placeholder="e.g. Irish-American"
                value={prefs.nationalityOrBackground ?? ""}
              />
            </FormField>

            {/* — Location & health ————————————————————————————— */}
            <FormSection title="Location & health" />

            <FormField label="City for weather">
              <input
                className={INPUT_CLS}
                onChange={(e) => setFormState((c) => setPrefs(c, { cityForWeather: e.target.value || null }))}
                placeholder="City used for the weather provider"
                value={prefs.cityForWeather ?? ""}
              />
            </FormField>
            <FormField label="Mobility level">
              <select
                className={INPUT_CLS}
                onChange={(e) => setFormState((c) => setPrefs(c, { mobilityLevel: e.target.value || null }))}
                value={prefs.mobilityLevel ?? ""}
              >
                <option value="">Not specified</option>
                <option value="full">Full mobility</option>
                <option value="limited">Limited mobility</option>
                <option value="wheelchair">Wheelchair user</option>
                <option value="bedbound">Bedbound</option>
              </select>
            </FormField>

            {/* — People ————————————————————————————————————————— */}
            <FormSection title="People & relationships" />

            <TagInput
              label="Family members"
              onChange={(next) => setFormState((c) => setPrefs(c, { familyMembers: next }))}
              placeholder="Nina, Paul, Maggie…"
              values={prefs.familyMembers}
            />
            <TagInput
              label="Life roles"
              onChange={(next) => setFormState((c) => setPrefs(c, { lifeRoles: next }))}
              placeholder="mother, teacher, nurse…"
              values={prefs.lifeRoles}
            />
            <TagInput
              label="Pets"
              onChange={(next) => setFormState((c) => setPrefs(c, { pets: next }))}
              placeholder="Biscuit the dog, Mittens the cat…"
              values={prefs.pets}
            />

            {/* — Interests ————————————————————————————————————— */}
            <FormSection title="Interests & preferences" />

            <TagInput
              label="Hobbies"
              onChange={(next) => setFormState((c) => setPrefs(c, { hobbies: next }))}
              placeholder="gardening, knitting, crosswords…"
              values={prefs.hobbies}
            />
            <TagInput
              label="Favourite activities"
              onChange={(next) => setFormState((c) => setPrefs(c, { favoriteActivities: next }))}
              placeholder="walking, baking, reading…"
              values={prefs.favoriteActivities}
            />
            <TagInput
              label="Favourite foods"
              onChange={(next) => setFormState((c) => setPrefs(c, { favouriteFoods: next }))}
              placeholder="tea and biscuits, apple pie…"
              values={prefs.favouriteFoods}
            />
            <TagInput
              label="Favourite singers / musicians"
              onChange={(next) => setFormState((c) => setPrefs(c, { favoriteSingers: next }))}
              placeholder="Frank Sinatra, Doris Day…"
              values={prefs.favoriteSingers}
            />
            <TagInput
              label="Favourite TV shows"
              onChange={(next) => setFormState((c) => setPrefs(c, { favouriteTvShows: next }))}
              placeholder="Lawrence Welk, Ed Sullivan…"
              values={prefs.favouriteTvShows}
            />

            {/* — Actions ——————————————————————————————————————— */}
            {saveError ? <p className="md:col-span-2 text-sm text-[#a0382b]">{saveError}</p> : null}
            <div className="md:col-span-2 flex flex-wrap gap-3 pt-2">
              <button
                className="inline-flex rounded-full bg-ink-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-ink-800 disabled:cursor-not-allowed disabled:opacity-60"
                disabled={updateMutation.isPending}
                type="submit"
              >
                {updateMutation.isPending ? "Saving…" : "Save friend profile"}
              </button>
              <button
                className="inline-flex rounded-full border border-black/10 bg-white px-5 py-3 text-sm font-semibold text-ink-900 transition hover:border-black/20"
                onClick={() => { setIsEditing(false); setSaveError(null); setFormState(patientToForm(patient)); }}
                type="button"
              >
                Cancel
              </button>
            </div>
          </form>
        ) : null}
      </section>

      {/* ── Send newsletter ────────────────────────────────────────── */}
      <section className="rounded-[28px] border border-black/10 bg-white/82 p-6 shadow-panel">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className={EYEBROW_CLS}>Manual dispatch</p>
            <h2 className="mt-2 font-display text-3xl text-ink-900">Send newsletter now</h2>
            <p className="mt-2 text-sm leading-7 text-ink-700">
              Assembles and sends today&apos;s newsletter for this friend immediately. Requires an email or phone number on the profile.
            </p>
          </div>
          <div className="flex flex-col items-end gap-2">
            <button
              className="inline-flex rounded-full bg-ink-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-ink-800 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={sendNewsletterMutation.isPending}
              onClick={() => { setSendResult(null); sendNewsletterMutation.mutate(); }}
              type="button"
            >
              {sendNewsletterMutation.isPending ? "Sending…" : "Send newsletter"}
            </button>
            {sendResult ? (
              <p className={`text-sm ${sendResult.ok ? "text-green-700" : "text-[#a0382b]"}`}>
                {sendResult.ok ? "✓ " : "✗ "}{sendResult.message}
              </p>
            ) : null}
          </div>
        </div>
      </section>

      {/* ── Newsletter preview ─────────────────────────────────────── */}
      <section className="rounded-[28px] border border-black/10 bg-white/82 p-6 shadow-panel">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className={EYEBROW_CLS}>Newsletter preview</p>
            <h2 className="mt-2 font-display text-3xl text-ink-900">Daily newsletter</h2>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => shiftPreviewDate(-1)}
              className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-black/10 bg-white text-ink-900 transition hover:border-black/20 hover:bg-[#f8f5f0]"
              title="Previous day"
              type="button"
            >
              ←
            </button>
            <span className="min-w-[120px] text-center text-sm font-semibold text-ink-900">
              {previewDate === todayStr ? "Today" : previewDate}
            </span>
            <button
              onClick={() => shiftPreviewDate(1)}
              disabled={previewDate >= todayStr}
              className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-black/10 bg-white text-ink-900 transition hover:border-black/20 hover:bg-[#f8f5f0] disabled:cursor-not-allowed disabled:opacity-40"
              title="Next day"
              type="button"
            >
              →
            </button>
            {previewDate === todayStr && (
              <div className="flex flex-col items-end gap-1">
                <button
                  onClick={() => {
                    setRegenerationMessage(null);
                    regenerateMutation.mutate();
                  }}
                  disabled={regenerateMutation.isPending || Boolean(regenerationJobId)}
                  className="inline-flex items-center rounded-full border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-ink-900 transition hover:border-black/20 hover:bg-[#f8f5f0] disabled:cursor-not-allowed disabled:opacity-60"
                  title="Re-run all providers with fresh data"
                  type="button"
                >
                  {regenerateMutation.isPending || regenerationJobId ? "Regenerating…" : "↺ Regenerate"}
                </button>
                <span className="text-xs text-ink-500">
                  {regenerationJobId
                    ? regenerationStatus?.status_message || "Regeneration is running in the background…"
                    : regenerateMutation.isPending
                      ? "Starting regeneration…"
                      : "Fetches fresh data from all providers"}
                </span>
                {regenerationMessage ? (
                  <span className={`text-xs ${regenerationStatus?.state === "FAILED" ? "text-[#a0382b]" : "text-ink-500"}`}>
                    {regenerationMessage}
                  </span>
                ) : null}
              </div>
            )}
          </div>
        </div>

        <div className="mt-6">
          {isLoadingPreview ? (
            <LoadingState label="Loading newsletter…" />
          ) : newsletterPreview?.has_content ? (
            <iframe
              srcDoc={`<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>*{box-sizing:border-box;margin:0;padding:0}html,body{width:100%;background:#fff}</style></head><body>${newsletterPreview.html}</body></html>`}
              className="w-full rounded-2xl border border-black/10"
              style={{ height: "800px" }}
              title={`Newsletter for ${previewDate}`}
              sandbox="allow-same-origin"
            />
          ) : (
            <p className="text-sm text-ink-600 italic">No newsletter content cached for this date.</p>
          )}
        </div>
      </section>

      {/* ── Profile summary ────────────────────────────────────────── */}
      <section className="grid gap-6 lg:grid-cols-[1.2fr,0.8fr]">
        <article className="rounded-[28px] border border-black/10 bg-white/82 p-6 shadow-panel">
          <div className="flex items-center justify-between gap-4">
            <h2 className="font-display text-3xl text-ink-900">Profile summary</h2>
            <PatientAccessStateBadge state={patient.accessState as "active" | "inactive" | "archived"} />
          </div>
          <dl className="mt-6 grid gap-5 md:grid-cols-2">
            <div>
              <dt className={EYEBROW_CLS}>Family</dt>
              <dd className="mt-2 text-base text-ink-900">{patient.familyName}</dd>
            </div>
            <div>
              <dt className={EYEBROW_CLS}>Join code</dt>
              <dd className="mt-2 font-mono text-base uppercase tracking-[0.18em] text-ink-900">{patient.joinCode}</dd>
            </div>
            <div>
              <dt className={EYEBROW_CLS}>Stage</dt>
              <dd className="mt-2 text-base capitalize text-ink-900">{patient.stage}</dd>
            </div>
            <div>
              <dt className={EYEBROW_CLS}>Delivery</dt>
              <dd className="mt-2 text-base text-ink-900">
                {patient.deliveryTime ?? "Flexible"}{patient.days.length > 0 ? ` · ${patient.days.join(", ")}` : ""}
              </dd>
            </div>
            <div>
              <dt className={EYEBROW_CLS}>Timezone</dt>
              <dd className="mt-2 text-base text-ink-900">{patient.timezone}</dd>
            </div>
            <div>
              <dt className={EYEBROW_CLS}>Language</dt>
              <dd className="mt-2 text-base text-ink-900">{patient.preferredLanguage}</dd>
            </div>
            <div>
              <dt className={EYEBROW_CLS}>Country</dt>
              <dd className="mt-2 text-base text-ink-900">{patient.country}</dd>
            </div>
            {patient.postalCode ? (
              <div>
                <dt className={EYEBROW_CLS}>Postal code / ZIP</dt>
                <dd className="mt-2 text-base text-ink-900">{patient.postalCode}</dd>
              </div>
            ) : null}
            {patient.latitude !== null && patient.longitude !== null ? (
              <div className="md:col-span-2">
                <dt className={EYEBROW_CLS}>Resolved coordinates</dt>
                <dd className="mt-2 text-base text-ink-900">
                  {patient.latitude.toFixed(5)}, {patient.longitude.toFixed(5)}
                </dd>
              </div>
            ) : null}
            {patient.email ? (
              <div>
                <dt className={EYEBROW_CLS}>Email</dt>
                <dd className="mt-2 text-base text-ink-900">{patient.email}</dd>
              </div>
            ) : null}
            {patient.phoneNumber ? (
              <div>
                <dt className={EYEBROW_CLS}>Phone</dt>
                <dd className="mt-2 text-base text-ink-900">{patient.phoneNumber}</dd>
              </div>
            ) : null}
          </dl>
        </article>

        <article className="rounded-[28px] border border-black/10 bg-white/82 p-6 shadow-panel">
          <h2 className="font-display text-3xl text-ink-900">Image sign-in</h2>
          <p className="mt-4 text-sm leading-7 text-ink-700">
            Three familiar images assigned for direct friend access.
          </p>
          <div className="mt-5 flex flex-wrap gap-2">
            {patient.authImageKeys.map((key) => (
              <span key={key} className="rounded-full border border-black/10 bg-[#fcfaf6] px-3 py-2 text-sm font-semibold capitalize text-ink-900">
                {key}
              </span>
            ))}
          </div>
          <Link className="mt-6 inline-flex rounded-full border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-ink-900 transition hover:border-black/20" href="/care-circle-patient/login">
            Preview friend sign-in
          </Link>
        </article>
      </section>

      {/* ── Preferences summary ────────────────────────────────────── */}
      <section className="rounded-[28px] border border-black/10 bg-white/82 p-6 shadow-panel">
        <h2 className="font-display text-3xl text-ink-900">Friend preferences</h2>
        <dl className="mt-5 grid gap-5 md:grid-cols-2">
          {patient.preferences.hometown ? (
            <div>
              <dt className={EYEBROW_CLS}>Hometown</dt>
              <dd className="mt-2 text-base text-ink-900">{patient.preferences.hometown}</dd>
            </div>
          ) : null}
          {patient.preferences.eraOfYouth ? (
            <div>
              <dt className={EYEBROW_CLS}>Era of youth</dt>
              <dd className="mt-2 text-base text-ink-900">{patient.preferences.eraOfYouth}</dd>
            </div>
          ) : null}
          {patient.preferences.nationalityOrBackground ? (
            <div>
              <dt className={EYEBROW_CLS}>Background</dt>
              <dd className="mt-2 text-base text-ink-900">{patient.preferences.nationalityOrBackground}</dd>
            </div>
          ) : null}
          {patient.preferences.cityForWeather ? (
            <div>
              <dt className={EYEBROW_CLS}>Weather city</dt>
              <dd className="mt-2 text-base text-ink-900">{patient.preferences.cityForWeather}</dd>
            </div>
          ) : null}
          {patient.preferences.mobilityLevel ? (
            <div>
              <dt className={EYEBROW_CLS}>Mobility</dt>
              <dd className="mt-2 text-base capitalize text-ink-900">{patient.preferences.mobilityLevel.replace(/_/g, " ")}</dd>
            </div>
          ) : null}
          {patient.preferences.preferredPronoun ? (
            <div>
              <dt className={EYEBROW_CLS}>Pronoun</dt>
              <dd className="mt-2 text-base text-ink-900">{patient.preferences.preferredPronoun}</dd>
            </div>
          ) : null}
        </dl>

        {[
          { label: "Family members", items: patient.preferences.familyMembers },
          { label: "Life roles", items: patient.preferences.lifeRoles },
          { label: "Pets", items: patient.preferences.pets },
          { label: "Hobbies", items: patient.preferences.hobbies },
          { label: "Favourite activities", items: patient.preferences.favoriteActivities },
          { label: "Favourite foods", items: patient.preferences.favouriteFoods },
          { label: "Favourite singers", items: patient.preferences.favoriteSingers },
          { label: "Favourite TV shows", items: patient.preferences.favouriteTvShows },
        ].filter(({ items }) => items.length > 0).map(({ label, items }) => (
          <div key={label} className="mt-5">
            <p className={EYEBROW_CLS}>{label}</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {items.map((item) => (
                <span key={item} className="rounded-full border border-black/10 bg-[#fcfaf6] px-3 py-2 text-sm text-ink-700">
                  {item}
                </span>
              ))}
            </div>
          </div>
        ))}
      </section>

      {/* ── Provider ordering ──────────────────────────────────────── */}
      <section className="rounded-[28px] border border-black/10 bg-white/82 p-6 shadow-panel">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="font-display text-3xl text-ink-900">Provider selection & order</h2>
            <p className="mt-2 text-sm leading-7 text-ink-700">
              Toggle providers on or off, then drag or use the arrows to set the order they appear in the newsletter.
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
          <div className="mt-6"><LoadingState label="Loading provider options" /></div>
        ) : isProviderCatalogError || isProviderConfigError ? (
          <div className="mt-6">
            <ErrorState
              detail={
                providerCatalogError instanceof Error ? providerCatalogError.message
                  : providerConfigError instanceof Error ? providerConfigError.message
                  : "Could not load provider settings."
              }
              title="Provider settings unavailable"
            />
          </div>
        ) : (
          <ProviderOrderingPanel
            patientId={patientId}
            providerCatalog={providerCatalog ?? []}
            providerConfigs={providerConfigs ?? []}
            readOnly={!isOwner}
          />
        )}
      </section>
    </div>
  );
}

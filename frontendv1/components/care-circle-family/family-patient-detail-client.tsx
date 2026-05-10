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
  fetchTagTaxonomy,
  regeneratePatientNewsletter,
  sendPatientNewsletter,
  type CareCircleAuthCatalogItem,
  type CareCirclePatientPreferences,
  type CareCirclePatientUpdateInput,
  type IsoCodeEntry,
  type TagCategory,
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
  careMode: "memory_care",
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

type TabId = "overview" | "edit" | "preferences" | "providers" | "newsletter";

const TABS: { id: TabId; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "edit", label: "Edit Profile" },
  { id: "preferences", label: "Preferences" },
  { id: "providers", label: "Providers" },
  { id: "newsletter", label: "Newsletter" },
];

type EditSubTabId = "family" | "schedule" | "identity" | "people" | "signin";

const EDIT_SUB_TABS: { id: EditSubTabId; label: string }[] = [
  { id: "family", label: "Family & Access" },
  { id: "schedule", label: "Schedule & Location" },
  { id: "identity", label: "Identity & Background" },
  { id: "people", label: "People & Interests" },
  { id: "signin", label: "Image Sign-in" },
];

function EditSubTabBar({
  active,
  onChange,
}: {
  active: EditSubTabId;
  onChange: (id: EditSubTabId) => void;
}) {
  return (
    <nav
      aria-label="Edit profile sections"
      className="flex flex-wrap gap-1 rounded-2xl border border-black/10 bg-white/70 p-1.5 shadow-sm"
    >
      {EDIT_SUB_TABS.map((tab) => (
        <button
          key={tab.id}
          aria-selected={active === tab.id}
          className={[
            "rounded-xl px-4 py-2 text-sm font-medium transition",
            active === tab.id
              ? "bg-ink-900 text-white shadow-sm"
              : "text-ink-700 hover:bg-black/[0.05] hover:text-ink-900",
          ].join(" ")}
          onClick={() => onChange(tab.id)}
          role="tab"
          type="button"
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
}

function FormField({
  label,
  hint,
  children,
  span2,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
  span2?: boolean;
}) {
  return (
    <label className={`${LABEL_CLS}${span2 ? " md:col-span-2" : ""}`}>
      <span className={EYEBROW_CLS}>{label}</span>
      {hint && <p className="mt-1 text-xs text-ink-500 leading-snug">{hint}</p>}
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
  suggestions,
}: {
  label: string;
  values: string[];
  onChange: (_next: string[]) => void;
  placeholder?: string;
  hint?: string;
  span2?: boolean;
  suggestions?: TagCategory[];
}) {
  const [draft, setDraft] = useState("");
  const [activeCat, setActiveCat] = useState<string | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const inputRef = useRef<HTMLInputElement>(null);

  // Pick first category on mount or when suggestions load
  useEffect(() => {
    if (suggestions && suggestions.length > 0 && activeCat === null) {
      setActiveCat(suggestions[0].category);
    }
  }, [suggestions, activeCat]);

  function commit() {
    const trimmed = draft.trim();
    if (trimmed && !values.includes(trimmed)) {
      onChange([...values, trimmed]);
    }
    setDraft("");
  }

  function addSuggestion(tag: string) {
    if (!values.includes(tag)) {
      onChange([...values, tag]);
    }
  }

  const valuesSet = new Set(values.map((v) => v.toLowerCase()));

  // Suggestions for the active category, filtered by draft text and not already added
  const activeSuggestions = (() => {
    if (!suggestions || !showSuggestions) return [];
    const cat = suggestions.find((c) => c.category === activeCat);
    if (!cat) return [];
    const filter = draft.trim().toLowerCase();
    return cat.tags.filter(
      (t) => !valuesSet.has(t.toLowerCase()) && (filter === "" || t.toLowerCase().includes(filter))
    );
  })();

  const hasSuggestions = suggestions && suggestions.length > 0;

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

      {hasSuggestions && (
        <div className="mt-2">
          <button
            className="text-xs font-medium text-ink-500 hover:text-ink-800 transition"
            onClick={() => setShowSuggestions((v) => !v)}
            type="button"
          >
            {showSuggestions ? "▾ Hide suggestions" : "▸ Show suggestions"}
          </button>

          {showSuggestions && (
            <div className="mt-2 rounded-2xl border border-black/8 bg-white/60 p-3">
              {/* Category pills */}
              <div className="flex flex-wrap gap-1.5 overflow-x-auto pb-1">
                {suggestions!.map((cat) => (
                  <button
                    key={cat.category}
                    className={[
                      "rounded-full px-3 py-1 text-xs font-semibold transition whitespace-nowrap",
                      activeCat === cat.category
                        ? "bg-ink-900 text-white"
                        : "border border-ink-200 bg-white text-ink-600 hover:bg-ink-50",
                    ].join(" ")}
                    onClick={() => setActiveCat(cat.category)}
                    type="button"
                  >
                    {cat.category}
                  </button>
                ))}
              </div>

              {/* Tag grid */}
              {activeSuggestions.length > 0 ? (
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {activeSuggestions.slice(0, 30).map((tag) => (
                    <button
                      key={tag}
                      className="rounded-full border border-ink-200 bg-[#f7f4ef] px-3 py-1 text-sm text-ink-700 transition hover:border-ink-400 hover:bg-ink-100"
                      onClick={() => addSuggestion(tag)}
                      type="button"
                    >
                      + {tag}
                    </button>
                  ))}
                </div>
              ) : (
                <p className="mt-2 text-xs text-ink-400 italic">
                  {valuesSet.size > 0 && activeSuggestions.length === 0
                    ? "All suggestions in this category added."
                    : "No matches."}
                </p>
              )}
            </div>
          )}
        </div>
      )}

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

function FormSection({ title }: { title: string }) {
  return (
    <div className="md:col-span-2 border-t border-black/8 pt-4 mt-1">
      <p className="text-xs uppercase tracking-[0.24em] text-ink-500">{title}</p>
    </div>
  );
}

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
  careMode: string;
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
    careMode: patient.careMode ?? "memory_care",
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
// Tab bar
// ---------------------------------------------------------------------------

function TabBar({
  active,
  onChange,
  ownerOnly,
}: {
  active: TabId;
  onChange: (id: TabId) => void;
  ownerOnly: boolean;
}) {
  const visibleTabs = TABS.filter((t) => ownerOnly || !["edit", "newsletter"].includes(t.id));

  return (
    <nav
      aria-label="Patient profile sections"
      className="flex flex-wrap gap-1 rounded-2xl border border-black/10 bg-white/70 p-1.5 shadow-sm"
      data-testid="patient-tab-bar"
    >
      {visibleTabs.map((tab) => (
        <button
          key={tab.id}
          aria-selected={active === tab.id}
          className={[
            "rounded-xl px-4 py-2 text-sm font-medium transition",
            active === tab.id
              ? "bg-ink-900 text-white shadow-sm"
              : "text-ink-700 hover:bg-black/[0.05] hover:text-ink-900",
          ].join(" ")}
          onClick={() => onChange(tab.id)}
          role="tab"
          type="button"
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export function FamilyPatientDetailClient({ patientId }: { patientId: string }) {
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();
  const session = useSession();
  const isOwner = session.user?.is_family_owner === true;

  const [activeTab, setActiveTab] = useState<TabId>("overview");
  const [activeEditTab, setActiveEditTab] = useState<EditSubTabId>("family");
  const [saveError, setSaveError] = useState<string | null>(null);
  const [formState, setFormState] = useState<CareCirclePatientUpdateInput>(EMPTY_PATIENT_FORM);

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
  const { data: taxonomy } = useQuery({
    queryKey: ["tag-taxonomy"],
    queryFn: () => fetchTagTaxonomy(),
    staleTime: 10 * 60 * 1000,
  });

  const todayStr = new Date().toISOString().slice(0, 10);
  const [previewDate, setPreviewDate] = useState(todayStr);
  const [sendResult, setSendResult] = useState<{ ok: boolean; message: string } | null>(null);
  const [regenerationJobId, setRegenerationJobId] = useState<string | null>(null);
  const [regenerationMessage, setRegenerationMessage] = useState<string | null>(null);

  const { data: newsletterPreview, isLoading: isLoadingPreview } = useQuery({
    queryKey: ["care-circle-newsletter-preview", patientId, previewDate],
    queryFn: () => fetchPatientNewsletterPreview(patientId, previewDate),
    enabled: activeTab === "newsletter",
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
    if (patient) setFormState(patientToForm(patient));
  }, [patient]);

  useEffect(() => {
    setFormState(EMPTY_PATIENT_FORM);
    setSaveError(null);
    setActiveTab("overview");
    setActiveEditTab("family");
  }, [patientId]);

  useEffect(() => {
    if (searchParams.get("edit") === "1" && isOwner) {
      setActiveTab("edit");
    }
  }, [searchParams, isOwner]);

  useEffect(() => {
    if (!regenerationStatus) return;
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
      setActiveTab("overview");
    },
    onError: (err) => setSaveError(err instanceof Error ? err.message : "Could not save friend settings."),
  });

  if (isLoading) return <LoadingState label="Loading friend profile" />;
  if (isError || !patient) {
    return <ErrorState detail={error instanceof Error ? error.message : "Could not load the friend profile."} title="Friend profile unavailable" />;
  }

  const prefs = formState.preferences;

  return (
    <div className="space-y-6">
      <TabBar active={activeTab} onChange={setActiveTab} ownerOnly={isOwner} />

      {/* ── Overview tab ─────────────────────────────────────────────── */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          <section className="grid gap-6 lg:grid-cols-[1.2fr,0.8fr]">
            <article className="rounded-[28px] border border-black/10 bg-white/82 p-6 shadow-panel">
              <div className="flex items-center justify-between gap-4">
                <h2 className="font-display text-3xl text-ink-900">Profile summary</h2>
                <PatientAccessStateBadge state={patient.accessState as "active" | "inactive" | "archived"} />
              </div>
              <dl className="mt-6 grid gap-5 md:grid-cols-2">
                <div><dt className={EYEBROW_CLS}>Family</dt><dd className="mt-2 text-base text-ink-900">{patient.familyName}</dd></div>
                <div><dt className={EYEBROW_CLS}>Join code</dt><dd className="mt-2 font-mono text-base uppercase tracking-[0.18em] text-ink-900">{patient.joinCode}</dd></div>
                <div><dt className={EYEBROW_CLS}>Care mode</dt><dd className="mt-2 text-base capitalize text-ink-900">{patient.careMode === "general" ? "General" : "Memory Care"}</dd></div>
                {patient.careMode !== "general" && <div><dt className={EYEBROW_CLS}>Cognitive stage</dt><dd className="mt-2 text-base capitalize text-ink-900">{patient.stage}</dd></div>}
                <div>
                  <dt className={EYEBROW_CLS}>Delivery</dt>
                  <dd className="mt-2 text-base text-ink-900">
                    {patient.deliveryTime ?? "Flexible"}{patient.days.length > 0 ? ` · ${patient.days.join(", ")}` : ""}
                  </dd>
                </div>
                <div><dt className={EYEBROW_CLS}>Timezone</dt><dd className="mt-2 text-base text-ink-900">{patient.timezone}</dd></div>
                <div><dt className={EYEBROW_CLS}>Language</dt><dd className="mt-2 text-base text-ink-900">{patient.preferredLanguage}</dd></div>
                <div><dt className={EYEBROW_CLS}>Country</dt><dd className="mt-2 text-base text-ink-900">{patient.country}</dd></div>
                {patient.postalCode ? (
                  <div><dt className={EYEBROW_CLS}>Postal code / ZIP</dt><dd className="mt-2 text-base text-ink-900">{patient.postalCode}</dd></div>
                ) : null}
                {typeof patient.latitude === "number" && typeof patient.longitude === "number" ? (
                  <div className="md:col-span-2">
                    <dt className={EYEBROW_CLS}>Resolved coordinates</dt>
                    <dd className="mt-2 text-base text-ink-900">{patient.latitude.toFixed(5)}, {patient.longitude.toFixed(5)}</dd>
                  </div>
                ) : null}
                {patient.email ? <div><dt className={EYEBROW_CLS}>Email</dt><dd className="mt-2 text-base text-ink-900">{patient.email}</dd></div> : null}
                {patient.phoneNumber ? <div><dt className={EYEBROW_CLS}>Phone</dt><dd className="mt-2 text-base text-ink-900">{patient.phoneNumber}</dd></div> : null}
              </dl>
              {isOwner && (
                <button
                  className="mt-6 inline-flex rounded-full border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-ink-900 transition hover:border-black/20"
                  onClick={() => setActiveTab("edit")}
                  type="button"
                >
                  Edit profile
                </button>
              )}
            </article>

            <div className="space-y-6">
              <article className="rounded-[28px] border border-black/10 bg-white/82 p-6 shadow-panel">
                <h2 className="font-display text-3xl text-ink-900">Image sign-in</h2>
                <p className="mt-4 text-sm leading-7 text-ink-700">Three familiar images assigned for direct friend access.</p>
                <div className="mt-5 flex flex-wrap gap-2">
                  {patient.authImageKeys.map((key) => (
                    <span key={key} className="rounded-full border border-black/10 bg-[#fcfaf6] px-3 py-2 text-sm font-semibold capitalize text-ink-900">{key}</span>
                  ))}
                </div>
                <Link className="mt-6 inline-flex rounded-full border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-ink-900 transition hover:border-black/20" href="/care-circle-patient/login">
                  Preview friend sign-in
                </Link>
              </article>

              <article className="rounded-[28px] border border-black/10 bg-white/82 p-6 shadow-panel">
                <h2 className="font-display text-3xl text-ink-900">Friend preferences</h2>
                <dl className="mt-5 grid gap-4">
                  {patient.preferences.hometown ? <div><dt className={EYEBROW_CLS}>Hometown</dt><dd className="mt-1 text-base text-ink-900">{patient.preferences.hometown}</dd></div> : null}
                  {patient.preferences.eraOfYouth ? <div><dt className={EYEBROW_CLS}>Era of youth</dt><dd className="mt-1 text-base text-ink-900">{patient.preferences.eraOfYouth}</dd></div> : null}
                  {patient.preferences.nationalityOrBackground ? <div><dt className={EYEBROW_CLS}>Background</dt><dd className="mt-1 text-base text-ink-900">{patient.preferences.nationalityOrBackground}</dd></div> : null}
                  {patient.preferences.cityForWeather ? <div><dt className={EYEBROW_CLS}>Weather city</dt><dd className="mt-1 text-base text-ink-900">{patient.preferences.cityForWeather}</dd></div> : null}
                  {patient.preferences.mobilityLevel ? <div><dt className={EYEBROW_CLS}>Mobility</dt><dd className="mt-1 text-base capitalize text-ink-900">{patient.preferences.mobilityLevel.replace(/_/g, " ")}</dd></div> : null}
                  {patient.preferences.preferredPronoun ? <div><dt className={EYEBROW_CLS}>Pronoun</dt><dd className="mt-1 text-base text-ink-900">{patient.preferences.preferredPronoun}</dd></div> : null}
                </dl>
                {[
                  { label: "Hobbies", items: patient.preferences.hobbies },
                  { label: "Favourite activities", items: patient.preferences.favoriteActivities },
                  { label: "Favourite foods", items: patient.preferences.favouriteFoods },
                  { label: "Favourite singers", items: patient.preferences.favoriteSingers },
                  { label: "Favourite TV shows", items: patient.preferences.favouriteTvShows },
                ].filter(({ items }) => items.length > 0).map(({ label, items }) => (
                  <div key={label} className="mt-4">
                    <p className={EYEBROW_CLS}>{label}</p>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {items.map((item) => (
                        <span key={item} className="rounded-full border border-black/10 bg-[#fcfaf6] px-3 py-2 text-sm text-ink-700">{item}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </article>
            </div>
          </section>

          {patient.preferences.familyMembers.length > 0 && (
            <article className="rounded-[28px] border border-black/10 bg-white/82 p-6 shadow-panel">
              <h2 className="font-display text-3xl text-ink-900">Family members</h2>
              <div className="mt-5 flex flex-wrap gap-2">
                {patient.preferences.familyMembers.map((member) => (
                  <span key={member} className="rounded-full border border-black/10 bg-[#fcfaf6] px-4 py-2 text-sm font-semibold text-ink-900">{member}</span>
                ))}
              </div>
            </article>
          )}
        </div>
      )}

      {/* ── Edit Profile tab ─────────────────────────────────────────── */}
      {activeTab === "edit" && isOwner && (
        <section className="rounded-[28px] border border-black/10 bg-white/82 p-6 shadow-panel">
          <h2 className="font-display text-3xl text-ink-900">Edit friend profile</h2>
          <form
            className="mt-6 space-y-6"
            onSubmit={(e) => { e.preventDefault(); setSaveError(null); updateMutation.mutate(formState); }}
          >
            <EditSubTabBar active={activeEditTab} onChange={setActiveEditTab} />

            {activeEditTab === "family" && (
              <div className="grid gap-5 md:grid-cols-2">
                <FormSection title="Family & access" />
                <FormField label="Family name"><input className={INPUT_CLS} onChange={(e) => setFormState((c) => ({ ...c, familyName: e.target.value }))} value={formState.familyName} /></FormField>
                <FormField label="Join code"><input className={`${INPUT_CLS} font-mono uppercase tracking-[0.18em]`} onChange={(e) => setFormState((c) => ({ ...c, joinCode: e.target.value.toUpperCase() }))} value={formState.joinCode} /></FormField>
                <FormField label="Friend display name"><input className={INPUT_CLS} onChange={(e) => setFormState((c) => ({ ...c, displayName: e.target.value }))} value={formState.displayName} /></FormField>
                <FormField label="Newsletter name">
                  <input className={INPUT_CLS} onChange={(e) => setFormState((c) => setPrefs(c, { recipientName: e.target.value || null }))} placeholder="Name used in newsletters (defaults to display name)" value={prefs.recipientName ?? ""} />
                </FormField>
                <FormField
                  label="Care mode"
                  hint="Memory Care tailors every newsletter for someone living with cognitive decline — simpler language, shorter sentences, and a calm tone. General is for anyone who would enjoy a personalised daily newsletter without those restrictions."
                >
                  <select className={INPUT_CLS} onChange={(e) => setFormState((c) => ({ ...c, careMode: e.target.value }))} value={formState.careMode}>
                    <option value="memory_care">Memory Care</option>
                    <option value="general">General</option>
                  </select>
                </FormField>
                {formState.careMode === "memory_care" && (
                  <FormField
                    label="Cognitive stage"
                    hint="Sets how simple the AI-generated content will be. Early = longest, most natural writing. Severe = very short sentences, one idea at a time."
                  >
                    <select className={INPUT_CLS} onChange={(e) => setFormState((c) => ({ ...c, stage: e.target.value }))} value={formState.stage}>
                      <option value="early">Early — natural length, gentle language</option>
                      <option value="mild">Mild — shorter sentences, clear words</option>
                      <option value="moderate">Moderate — very simple, one idea per sentence</option>
                      <option value="severe">Severe — minimal words, one idea only</option>
                    </select>
                  </FormField>
                )}
                <FormField label="Access state">
                  <select className={INPUT_CLS} onChange={(e) => setFormState((c) => ({ ...c, accessState: e.target.value }))} value={formState.accessState}>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="archived">Archived</option>
                  </select>
                </FormField>
                <FormField label="Email address"><input className={INPUT_CLS} onChange={(e) => setFormState((c) => ({ ...c, email: e.target.value || null }))} placeholder="friend@example.com" type="email" value={formState.email ?? ""} /></FormField>
                <FormField label="Phone number"><input className={INPUT_CLS} onChange={(e) => setFormState((c) => ({ ...c, phoneNumber: e.target.value || null }))} placeholder="+1 555 000 0000" type="tel" value={formState.phoneNumber ?? ""} /></FormField>
              </div>
            )}

            {activeEditTab === "schedule" && (
              <div className="grid gap-5 md:grid-cols-2">
                <FormSection title="Delivery schedule" />
                <FormField label="Timezone"><input className={INPUT_CLS} onChange={(e) => setFormState((c) => ({ ...c, timezone: e.target.value }))} value={formState.timezone} /></FormField>
                <FormField label="Language">
                  <select className={INPUT_CLS} onChange={(e) => setFormState((c) => ({ ...c, preferredLanguage: e.target.value }))} value={formState.preferredLanguage}>
                    <option value="">Select language</option>
                    {(isoCodes?.languages ?? []).map((lang: IsoCodeEntry) => <option key={lang.code} value={lang.code}>{lang.name} ({lang.code})</option>)}
                  </select>
                </FormField>
                <FormField label="Country">
                  <select className={INPUT_CLS} onChange={(e) => setFormState((c) => ({ ...c, country: e.target.value }))} value={formState.country}>
                    <option value="">Select country</option>
                    {(isoCodes?.countries ?? []).map((country: IsoCodeEntry) => <option key={country.code} value={country.code}>{country.name} ({country.code})</option>)}
                  </select>
                </FormField>
                <FormField label="Postal code / ZIP"><input className={INPUT_CLS} onChange={(e) => setFormState((c) => ({ ...c, postalCode: e.target.value || null }))} placeholder="Used to resolve latitude and longitude" value={formState.postalCode ?? ""} /></FormField>
                <FormField label="Delivery time"><input className={INPUT_CLS} onChange={(e) => setFormState((c) => ({ ...c, deliveryTime: e.target.value }))} placeholder="08:30" value={formState.deliveryTime ?? ""} /></FormField>
                <TagInput label="Delivery days" onChange={(next) => setFormState((c) => ({ ...c, days: next }))} placeholder="Mon, Wed, Fri…" values={formState.days} />

                <FormSection title="Location & health" />
                <FormField label="City for weather"><input className={INPUT_CLS} onChange={(e) => setFormState((c) => setPrefs(c, { cityForWeather: e.target.value || null }))} placeholder="City used for the weather provider" value={prefs.cityForWeather ?? ""} /></FormField>
                <FormField label="Mobility level">
                  <select className={INPUT_CLS} onChange={(e) => setFormState((c) => setPrefs(c, { mobilityLevel: e.target.value || null }))} value={prefs.mobilityLevel ?? ""}>
                    <option value="">Not specified</option>
                    <option value="full">Full mobility</option>
                    <option value="limited">Limited mobility</option>
                    <option value="wheelchair">Wheelchair user</option>
                    <option value="bedbound">Bedbound</option>
                  </select>
                </FormField>
              </div>
            )}

            {activeEditTab === "identity" && (
              <div className="grid gap-5 md:grid-cols-2">
                <FormSection title="Identity & background" />
                <FormField label="Preferred pronoun">
                  <select className={INPUT_CLS} onChange={(e) => setFormState((c) => setPrefs(c, { preferredPronoun: e.target.value || null }))} value={prefs.preferredPronoun ?? ""}>
                    <option value="">Not specified</option>
                    <option value="she/her">She / Her</option>
                    <option value="he/him">He / Him</option>
                    <option value="they/them">They / Them</option>
                  </select>
                </FormField>
                <FormField label="Era of youth"><input className={INPUT_CLS} onChange={(e) => setFormState((c) => setPrefs(c, { eraOfYouth: e.target.value || null }))} placeholder="e.g. 1950s" value={prefs.eraOfYouth ?? ""} /></FormField>
                <FormField label="Hometown"><input className={INPUT_CLS} onChange={(e) => setFormState((c) => setPrefs(c, { hometown: e.target.value || null }))} placeholder="City or town they grew up in" value={prefs.hometown ?? ""} /></FormField>
                <FormField label="Nationality / background"><input className={INPUT_CLS} onChange={(e) => setFormState((c) => setPrefs(c, { nationalityOrBackground: e.target.value || null }))} placeholder="e.g. Irish-American" value={prefs.nationalityOrBackground ?? ""} /></FormField>
              </div>
            )}

            {activeEditTab === "people" && (
              <div className="grid gap-5 md:grid-cols-2">
                <FormSection title="People & relationships" />
                <TagInput label="Family members" onChange={(next) => setFormState((c) => setPrefs(c, { familyMembers: next }))} placeholder="Nina, Paul, Maggie…" values={prefs.familyMembers} />
                <TagInput label="Life roles" onChange={(next) => setFormState((c) => setPrefs(c, { lifeRoles: next }))} placeholder="mother, teacher, nurse…" values={prefs.lifeRoles} suggestions={taxonomy?.lifeRoles} />
                <TagInput label="Pets" onChange={(next) => setFormState((c) => setPrefs(c, { pets: next }))} placeholder="Biscuit the dog, Mittens the cat…" values={prefs.pets} suggestions={taxonomy?.pets} />

                <FormSection title="Interests & preferences" />
                <TagInput label="Hobbies" onChange={(next) => setFormState((c) => setPrefs(c, { hobbies: next }))} placeholder="gardening, knitting, crosswords…" values={prefs.hobbies} suggestions={taxonomy?.hobbies} />
                <TagInput label="Favourite activities" onChange={(next) => setFormState((c) => setPrefs(c, { favoriteActivities: next }))} placeholder="walking, baking, reading…" values={prefs.favoriteActivities} suggestions={taxonomy?.favoriteActivities} />
                <TagInput label="Favourite foods" onChange={(next) => setFormState((c) => setPrefs(c, { favouriteFoods: next }))} placeholder="tea and biscuits, apple pie…" values={prefs.favouriteFoods} suggestions={taxonomy?.favouriteFoods} />
                <TagInput label="Favourite singers / musicians" onChange={(next) => setFormState((c) => setPrefs(c, { favoriteSingers: next }))} placeholder="Frank Sinatra, Doris Day…" values={prefs.favoriteSingers} suggestions={taxonomy?.favoriteSingers} />
                <TagInput label="Favourite TV shows" onChange={(next) => setFormState((c) => setPrefs(c, { favouriteTvShows: next }))} placeholder="Lawrence Welk, Ed Sullivan…" values={prefs.favouriteTvShows} suggestions={taxonomy?.favouriteTvShows} />
              </div>
            )}

            {activeEditTab === "signin" && (
              <div className="grid gap-5 md:grid-cols-2">
                <FormSection title="Image sign-in" />
                <AuthImagePicker catalog={authCatalog} onChange={(next) => setFormState((c) => ({ ...c, authImageKeys: next }))} values={formState.authImageKeys} />
              </div>
            )}

            {saveError ? <p className="text-sm text-[#a0382b]">{saveError}</p> : null}
            <div className="flex flex-wrap gap-3 pt-2">
              <button className="inline-flex rounded-full bg-ink-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-ink-800 disabled:cursor-not-allowed disabled:opacity-60" disabled={updateMutation.isPending} type="submit">
                {updateMutation.isPending ? "Saving…" : "Save friend profile"}
              </button>
              <button className="inline-flex rounded-full border border-black/10 bg-white px-5 py-3 text-sm font-semibold text-ink-900 transition hover:border-black/20" onClick={() => { setSaveError(null); setFormState(patientToForm(patient)); setActiveTab("overview"); setActiveEditTab("family"); }} type="button">
                Cancel
              </button>
            </div>
          </form>
        </section>
      )}

      {/* ── Preferences tab ──────────────────────────────────────────── */}
      {activeTab === "preferences" && (
        <section className="rounded-[28px] border border-black/10 bg-white/82 p-6 shadow-panel">
          <h2 className="font-display text-3xl text-ink-900">Friend preferences</h2>
          <dl className="mt-5 grid gap-5 md:grid-cols-2">
            {patient.preferences.hometown ? <div><dt className={EYEBROW_CLS}>Hometown</dt><dd className="mt-2 text-base text-ink-900">{patient.preferences.hometown}</dd></div> : null}
            {patient.preferences.eraOfYouth ? <div><dt className={EYEBROW_CLS}>Era of youth</dt><dd className="mt-2 text-base text-ink-900">{patient.preferences.eraOfYouth}</dd></div> : null}
            {patient.preferences.nationalityOrBackground ? <div><dt className={EYEBROW_CLS}>Background</dt><dd className="mt-2 text-base text-ink-900">{patient.preferences.nationalityOrBackground}</dd></div> : null}
            {patient.preferences.cityForWeather ? <div><dt className={EYEBROW_CLS}>Weather city</dt><dd className="mt-2 text-base text-ink-900">{patient.preferences.cityForWeather}</dd></div> : null}
            {patient.preferences.mobilityLevel ? <div><dt className={EYEBROW_CLS}>Mobility</dt><dd className="mt-2 text-base capitalize text-ink-900">{patient.preferences.mobilityLevel.replace(/_/g, " ")}</dd></div> : null}
            {patient.preferences.preferredPronoun ? <div><dt className={EYEBROW_CLS}>Pronoun</dt><dd className="mt-2 text-base text-ink-900">{patient.preferences.preferredPronoun}</dd></div> : null}
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
                  <span key={item} className="rounded-full border border-black/10 bg-[#fcfaf6] px-3 py-2 text-sm text-ink-700">{item}</span>
                ))}
              </div>
            </div>
          ))}
        </section>
      )}

      {/* ── Providers tab ────────────────────────────────────────────── */}
      {activeTab === "providers" && (
        <section className="rounded-[28px] border border-black/10 bg-white/82 p-6 shadow-panel">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="font-display text-3xl text-ink-900">Provider selection & order</h2>
              <p className="mt-2 text-sm leading-7 text-ink-700">Toggle providers on or off, then drag or use the arrows to set the order they appear in the newsletter.</p>
            </div>
            <Link className="inline-flex rounded-full border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-ink-900 transition hover:border-black/20" href="/care-circle-family/providers">
              Open provider catalog
            </Link>
          </div>
          {isLoadingProviderCatalog || isLoadingProviderConfigs ? (
            <div className="mt-6"><LoadingState label="Loading provider options" /></div>
          ) : isProviderCatalogError || isProviderConfigError ? (
            <div className="mt-6">
              <ErrorState detail={providerCatalogError instanceof Error ? providerCatalogError.message : providerConfigError instanceof Error ? providerConfigError.message : "Could not load provider settings."} title="Provider settings unavailable" />
            </div>
          ) : (
            <ProviderOrderingPanel patientId={patientId} providerCatalog={providerCatalog ?? []} providerConfigs={providerConfigs ?? []} readOnly={!isOwner} />
          )}
        </section>
      )}

      {/* ── Newsletter tab ───────────────────────────────────────────── */}
      {activeTab === "newsletter" && isOwner && (
        <div className="space-y-6">
          <section className="rounded-[28px] border border-black/10 bg-white/82 p-6 shadow-panel">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className={EYEBROW_CLS}>Manual dispatch</p>
                <h2 className="mt-2 font-display text-3xl text-ink-900">Send newsletter now</h2>
                <p className="mt-2 text-sm leading-7 text-ink-700">Assembles and sends today&apos;s newsletter for this friend immediately. Requires an email or phone number on the profile.</p>
              </div>
              <div className="flex flex-col items-end gap-2">
                <button className="inline-flex rounded-full bg-ink-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-ink-800 disabled:cursor-not-allowed disabled:opacity-60" disabled={sendNewsletterMutation.isPending} onClick={() => { setSendResult(null); sendNewsletterMutation.mutate(); }} type="button">
                  {sendNewsletterMutation.isPending ? "Sending…" : "Send newsletter"}
                </button>
                {sendResult ? (
                  <p className={`text-sm ${sendResult.ok ? "text-green-700" : "text-[#a0382b]"}`}>{sendResult.ok ? "✓ " : "✗ "}{sendResult.message}</p>
                ) : null}
              </div>
            </div>
          </section>

          <div className="relative left-1/2 w-screen -translate-x-1/2 px-4 md:px-6">
            <section className="rounded-[28px] border border-black/10 bg-white/82 p-6 shadow-panel md:p-8">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <p className={EYEBROW_CLS}>Newsletter preview</p>
                  <h2 className="mt-2 font-display text-3xl text-ink-900">Daily newsletter</h2>
                </div>
                <div className="flex flex-wrap items-center gap-3">
                  <button onClick={() => shiftPreviewDate(-1)} className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-black/10 bg-white text-ink-900 transition hover:border-black/20" title="Previous day" type="button">←</button>
                  <span className="min-w-[120px] text-center text-sm font-semibold text-ink-900">{previewDate === todayStr ? "Today" : previewDate}</span>
                  <button onClick={() => shiftPreviewDate(1)} disabled={previewDate >= todayStr} className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-black/10 bg-white text-ink-900 transition hover:border-black/20 disabled:cursor-not-allowed disabled:opacity-40" title="Next day" type="button">→</button>
                  {previewDate === todayStr && (
                    <div className="flex flex-col items-end gap-1">
                      <button onClick={() => { setRegenerationMessage(null); regenerateMutation.mutate(); }} disabled={regenerateMutation.isPending || Boolean(regenerationJobId)} className="inline-flex items-center rounded-full border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-ink-900 transition hover:border-black/20 disabled:cursor-not-allowed disabled:opacity-60" type="button">
                        {regenerateMutation.isPending || regenerationJobId ? "Regenerating…" : "↺ Regenerate"}
                      </button>
                      <span className="text-xs text-ink-500">
                        {regenerationJobId ? regenerationStatus?.status_message || "Regeneration is running in the background…" : regenerateMutation.isPending ? "Starting regeneration…" : "Fetches fresh data from all providers"}
                      </span>
                      {regenerationMessage ? <span className={`text-xs ${regenerationStatus?.state === "FAILED" ? "text-[#a0382b]" : "text-ink-500"}`}>{regenerationMessage}</span> : null}
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
                    className="w-full rounded-2xl border border-black/10 bg-white"
                    style={{ height: "900px" }}
                    title={`Newsletter for ${previewDate}`}
                    sandbox="allow-same-origin"
                  />
                ) : (
                  <p className="text-sm italic text-ink-600">No newsletter content cached for this date.</p>
                )}
              </div>
            </section>
          </div>
        </div>
      )}
    </div>
  );
}

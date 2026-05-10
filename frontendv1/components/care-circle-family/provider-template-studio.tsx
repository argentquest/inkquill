"use client";

import "grapesjs/dist/css/grapes.min.css";

import { useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Loader2, Lock, Save } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";

import { useSession, useToasts } from "@/components/providers/app-providers";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";

interface TemplateInventoryProvider {
  name: string;
  label: string;
  icon?: string | null;
  order: number;
  enabled: boolean;
}

interface TemplateInventoryPayload {
  providers: TemplateInventoryProvider[];
  themes: string[];
}

interface TemplateEditorDocument {
  providerKey: string;
  label: string;
  theme: string;
  templateHtml: string;
  providerThemeCss: string;
  sharedThemeCss: string;
  availableThemes: string[];
}

async function fetchTemplateInventory(): Promise<TemplateInventoryPayload> {
  const response = await fetch("/api/admin/care-circle/templates", { cache: "no-store" });
  const payload = (await response.json()) as TemplateInventoryPayload | { message?: string };
  if (!response.ok) {
    throw new Error("message" in payload && payload.message ? payload.message : "Could not load template inventory.");
  }
  return payload as TemplateInventoryPayload;
}

async function fetchTemplateDocument(providerKey: string, theme: string): Promise<TemplateEditorDocument> {
  const response = await fetch(`/api/admin/care-circle/templates/${providerKey}?theme=${encodeURIComponent(theme)}`, {
    cache: "no-store",
  });
  const payload = (await response.json()) as TemplateEditorDocument | { message?: string };
  if (!response.ok) {
    throw new Error("message" in payload && payload.message ? payload.message : "Could not load template document.");
  }
  return payload as TemplateEditorDocument;
}

async function saveTemplateDocument(input: {
  providerKey: string;
  theme: string;
  templateHtml: string;
  providerThemeCss: string;
}) {
  const response = await fetch(`/api/admin/care-circle/templates/${input.providerKey}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });
  const payload = (await response.json()) as { message?: string };
  if (!response.ok) {
    throw new Error(payload.message ?? "Could not save template.");
  }
  return payload;
}

export function ProviderTemplateStudio() {
  const session = useSession();
  const { pushToast } = useToasts();
  const searchParams = useSearchParams();
  const router = useRouter();
  const editorRef = useRef<{
    getHtml: () => string;
    getCss: () => string;
    setComponents: (_input: string) => void;
    setStyle: (_input: string) => void;
    destroy: () => void;
  } | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const initializedRef = useRef(false);
  const [selectedProviderKey, setSelectedProviderKey] = useState(searchParams.get("provider") ?? "");
  const [selectedTheme, setSelectedTheme] = useState(searchParams.get("theme") ?? "classic");
  const [editorReady, setEditorReady] = useState(false);

  const inventoryQuery = useQuery({
    queryKey: ["care-circle-template-inventory"],
    queryFn: fetchTemplateInventory,
  });

  const providers = useMemo(() => inventoryQuery.data?.providers ?? [], [inventoryQuery.data?.providers]);
  const themes = useMemo(() => inventoryQuery.data?.themes ?? [], [inventoryQuery.data?.themes]);

  useEffect(() => {
    if (!selectedProviderKey && providers.length > 0) {
      setSelectedProviderKey(providers[0].name);
    }
  }, [providers, selectedProviderKey]);

  useEffect(() => {
    if (themes.length > 0 && !themes.includes(selectedTheme)) {
      setSelectedTheme(themes[0]);
    }
  }, [selectedTheme, themes]);

  const documentQuery = useQuery({
    queryKey: ["care-circle-template-document", selectedProviderKey, selectedTheme],
    queryFn: () => fetchTemplateDocument(selectedProviderKey, selectedTheme),
    enabled: Boolean(selectedProviderKey && selectedTheme),
  });

  const saveMutation = useMutation({
    mutationFn: saveTemplateDocument,
    onSuccess: (_input) => {
      pushToast({
        title: "Template saved",
        tone: "success",
        detail: "Provider HTML and theme overrides were written to disk.",
      });
      void documentQuery.refetch();
    },
    onError: (error, _input) => {
      pushToast({
        title: "Save failed",
        tone: "error",
        detail: error instanceof Error ? error.message : "The template could not be saved.",
      });
    },
  });

  useEffect(() => {
    if (initializedRef.current) {
      return;
    }
    if (!containerRef.current) {
      return;
    }

    initializedRef.current = true;

    void (async () => {
      const grapesjs = (await import("grapesjs")).default;
      const grapesPresetNewsletter = (await import("grapesjs-preset-newsletter")).default;

      const editor = grapesjs.init({
        container: containerRef.current!,
        fromElement: false,
        height: "880px",
        storageManager: false,
        noticeOnUnload: false,
        plugins: [grapesPresetNewsletter as never],
      });

      editorRef.current = editor as typeof editorRef.current;
      setEditorReady(true);
    })();

    return () => {
      editorRef.current?.destroy();
      editorRef.current = null;
      initializedRef.current = false;
      setEditorReady(false);
    };
  }, []);

  useEffect(() => {
    if (!editorReady || !editorRef.current || !documentQuery.data) {
      return;
    }

    editorRef.current.setComponents(documentQuery.data.templateHtml);
    editorRef.current.setStyle(documentQuery.data.providerThemeCss);
  }, [documentQuery.data, editorReady]);

  useEffect(() => {
    const params = new URLSearchParams(searchParams.toString());
    if (selectedProviderKey) {
      params.set("provider", selectedProviderKey);
    }
    if (selectedTheme) {
      params.set("theme", selectedTheme);
    }
    router.replace(`?${params.toString()}`);
  }, [router, searchParams, selectedProviderKey, selectedTheme]);

  const selectedProvider = useMemo(
    () => providers.find((provider) => provider.name === selectedProviderKey) ?? null,
    [providers, selectedProviderKey],
  );

  if (session.status === "loading" || inventoryQuery.isLoading) {
    return <LoadingState label="Loading template studio" />;
  }

  if (session.status !== "authenticated" || !session.user?.is_admin) {
    return (
      <div className="rounded-[28px] border border-black/10 bg-white/75 p-8 shadow-panel">
        <div className="flex items-center gap-3 text-ink-900">
          <Lock className="size-5" />
          <h2 className="text-lg font-semibold">Admin access required</h2>
        </div>
        <p className="mt-3 max-w-2xl text-sm text-ink-700">
          GrapesJS template editing is restricted to admin users because it writes directly to the provider template and
          theme files used by Care Circle rendering.
        </p>
      </div>
    );
  }

  if (inventoryQuery.error) {
    return (
      <ErrorState
        title="Template studio unavailable"
        detail={inventoryQuery.error instanceof Error ? inventoryQuery.error.message : "Could not load the studio."}
      />
    );
  }

  return (
    <div className="space-y-6">
      <section className="grid gap-4 rounded-[28px] border border-black/10 bg-white/75 p-6 shadow-panel md:grid-cols-[1fr_220px_auto]">
        <label className="space-y-2 text-sm">
          <span className="font-semibold text-ink-900">Provider</span>
          <select
            className="w-full rounded-2xl border border-black/10 bg-[#fcfaf6] px-4 py-3 text-ink-900"
            value={selectedProviderKey}
            onChange={(event) => setSelectedProviderKey(event.target.value)}
          >
            {providers.map((provider, index) => (
              <option key={`${provider.name}-${index}`} value={provider.name}>
                {provider.icon ? `${provider.icon} ` : ""}
                {provider.label}
              </option>
            ))}
          </select>
        </label>

        <label className="space-y-2 text-sm">
          <span className="font-semibold text-ink-900">Theme</span>
          <select
            className="w-full rounded-2xl border border-black/10 bg-[#fcfaf6] px-4 py-3 text-ink-900"
            value={selectedTheme}
            onChange={(event) => setSelectedTheme(event.target.value)}
          >
            {themes.map((theme) => (
              <option key={theme} value={theme}>
                {theme}
              </option>
            ))}
          </select>
        </label>

        <div className="flex items-end">
          <button
            type="button"
            className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-ink-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-ink-700 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={!editorRef.current || !selectedProviderKey || saveMutation.isPending}
            onClick={() => {
              const editor = editorRef.current;
              if (!editor || !selectedProviderKey) {
                return;
              }

              saveMutation.mutate({
                providerKey: selectedProviderKey,
                theme: selectedTheme,
                templateHtml: editor.getHtml(),
                providerThemeCss: editor.getCss(),
              });
            }}
          >
            {saveMutation.isPending ? <Loader2 className="size-4 animate-spin" /> : <Save className="size-4" />}
            Save template
          </button>
        </div>
      </section>

      <section className="rounded-[28px] border border-black/10 bg-white/75 p-6 shadow-panel">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-ink-900">
              {selectedProvider?.icon ? `${selectedProvider.icon} ` : ""}
              {selectedProvider?.label ?? "Provider template"}
            </h2>
            <p className="mt-2 max-w-3xl text-sm text-ink-700">
              This studio edits the provider’s `templates/default.html` and the selected provider-local theme override
              CSS. Shared theme CSS remains read-only and is still injected during backend render.
            </p>
          </div>
          {documentQuery.data ? (
            <div className="rounded-2xl border border-black/10 bg-[#fcfaf6] px-4 py-3 text-xs text-ink-700">
              <p>Shared theme loaded: {documentQuery.data.theme}</p>
              <p>Shared CSS size: {documentQuery.data.sharedThemeCss.length} bytes</p>
            </div>
          ) : null}
        </div>

        {documentQuery.isLoading ? (
          <div className="mt-6">
            <LoadingState label="Loading provider template" />
          </div>
        ) : documentQuery.error ? (
          <div className="mt-6">
            <ErrorState
              title="Template document unavailable"
              detail={documentQuery.error instanceof Error ? documentQuery.error.message : "Could not load the template."}
            />
          </div>
        ) : (
          <div className="mt-6 overflow-hidden rounded-[24px] border border-black/10">
            <div ref={containerRef} />
          </div>
        )}
      </section>
    </div>
  );
}
